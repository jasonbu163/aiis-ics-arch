// B 专属 MySQL 集成测试：真实 HTTP/EF/Driver/独立 SELECT，不用 InMemory/SQLite。
using System.Net;
using Microsoft.EntityFrameworkCore;
using AIIS.Backend.Infrastructure.Persistence;
using AIIS.Backend.app.Plan.Services;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using AIIS.Backend.Common.Errors;
using AIIS.Backend.Tests.Domain;
using AIIS.Backend.Tests.Fixtures;
using MySql.Data.MySqlClient;
using Microsoft.VisualStudio.TestTools.UnitTesting;
namespace AIIS.Backend.Tests.Persistence;

[TestClass, TestCategory("MySQL")]
public sealed class MySqlTests
{
    public TestContext TestContext { get; set; } = null!;
    private static async Task<JsonElement> Body(HttpResponseMessage response, int status = 200)
    {
        string text = await response.Content.ReadAsStringAsync(); Assert.AreEqual(status, (int)response.StatusCode, text);
        return JsonDocument.Parse(text).RootElement.Clone();
    }
    private static async Task<HttpResponseMessage> Post(HttpClient client, JsonObject input) => await client.PostAsync("/api/v1/plans", new StringContent(input.ToJsonString(), Encoding.UTF8, "application/json"));
    private static JsonObject Input(string coil) { var input = JsonNode.Parse(InputTests.Minimal)!.AsObject(); input["coilNo"] = coil; return input; }

    [TestMethod]
    public async Task RealMySqlPlanSlice()
    {
        var fixture = new MySqlFixture();
        Assert.AreEqual(0L, Convert.ToInt64(await fixture.Scalar("SELECT COUNT(*) FROM plans")), "fresh instance required");
        var columns = await fixture.Rows("SELECT column_name,column_type,is_nullable,IF(column_default IS NULL,'NULL',column_default),extra FROM information_schema.columns WHERE table_schema='arch_be008_plan' AND table_name='plans' ORDER BY ordinal_position");
        Assert.AreEqual(25, columns.Count); Assert.AreEqual(1, columns.Count(x => x[2] == "YES")); Assert.AreEqual("remark", columns.Single(x => x[2] == "YES")[0]);
        Assert.IsTrue(columns.All(x => x[3] == "NULL")); Assert.AreEqual("auto_increment", columns[0][4]);
        string[] expectedTypes = ["int","varchar(50)","varchar(20)","varchar(50)","decimal(12,4)","decimal(10,3)","decimal(10,2)","varchar(20)","decimal(10,2)","decimal(10,2)","decimal(10,2)","decimal(10,2)","decimal(10,2)","decimal(10,2)","decimal(10,2)","decimal(12,4)","decimal(12,4)","decimal(12,4)","decimal(12,4)","decimal(12,4)","varchar(20)","smallint","varchar(500)","datetime","datetime"];
        CollectionAssert.AreEqual(expectedTypes, columns.Select(x => x[1]).ToArray());
        var tables = await fixture.Rows("SHOW TABLES"); Assert.AreEqual(1, tables.Count); Assert.AreEqual("plans", tables[0][0]);
        var indexes = await fixture.Rows("SELECT index_name,non_unique,column_name FROM information_schema.statistics WHERE table_schema='arch_be008_plan' AND table_name='plans' ORDER BY index_name");
        CollectionAssert.AreEquivalent(new[] {"PRIMARY", "ix_plans_coil_no", "ix_plans_id", "ix_plans_priority", "ix_plans_status"}, indexes.Select(x => x[0]).ToArray());
        Assert.AreEqual("0", indexes.Single(x => x[0] == "ix_plans_coil_no")[1]);
        await using (var appDb = await fixture.Connect(true))
        {
            await using var denied = new MySqlCommand("DELETE FROM plans WHERE id=-1", appDb);
            var error = await Assert.ThrowsAsync<MySqlException>(() => denied.ExecuteNonQueryAsync()); Assert.AreEqual(1142, error.Number);
        }
        await using (var db = new PlanDbContext(new DbContextOptionsBuilder<PlanDbContext>().UseMySQL(fixture.AppConnection).Options))
        {
            Assert.IsFalse(await db.Plans.FromSqlInterpolated($"SELECT * FROM plans WHERE LOWER(TRIM(coil_no)) = LOWER(TRIM({"unused"}))").AnyAsync());
            var clock = await db.Database.SqlQuery<DatabaseClock>($"SELECT CURRENT_TIMESTAMP AS `LocalTime`, TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP, CURRENT_TIMESTAMP) AS `OffsetSeconds`, @@session.time_zone AS `SessionZone`, @@global.time_zone AS `ServerZone`").SingleAsync();
            Assert.AreEqual(28800L,clock.OffsetSeconds);
        }
        TestContext.WriteLine("AC12/16: plans25 columns/types/null/defaults/four indexes, one business table, application DELETE denied.");
        await using var factory = new ApiFactory(connection: fixture.AppConnection, logDirectory: Path.Combine(fixture.Root, "http-logs"));
        using var client = factory.CreateClient();
        var empty = (await Body(await client.GetAsync("/api/v1/plans"))).GetProperty("data"); Assert.AreEqual(0, empty.GetProperty("total").GetInt32()); Assert.AreEqual(0, empty.GetProperty("totalPages").GetInt32());
        var minimal = (await Body(await Post(client, Input("  Dev-AbC  ")))).GetProperty("data");
        Assert.AreEqual(25, minimal.EnumerateObject().Count()); Assert.AreEqual("special", minimal.GetProperty("materialStatus").GetString()); Assert.AreEqual("planned", minimal.GetProperty("status").GetString()); Assert.AreEqual(5, minimal.GetProperty("priority").GetInt32());
        Assert.AreEqual("0.0000", minimal.GetProperty("entryUnitTension").GetString()); Assert.AreEqual(JsonValueKind.Null, minimal.GetProperty("remark").ValueKind);
        int id = minimal.GetProperty("id").GetInt32();
        var detail = (await Body(await client.GetAsync("/api/v1/plans/" + id))).GetProperty("data"); Assert.AreEqual(minimal.GetRawText(), detail.GetRawText());
        Assert.AreEqual("  Dev-AbC  ", detail.GetProperty("coilNo").GetString());
        Assert.AreEqual(detail.GetProperty("createdAt").GetString(), detail.GetProperty("updatedAt").GetString()); Assert.IsTrue(detail.GetProperty("createdAt").GetString()!.EndsWith("+08:00", StringComparison.Ordinal));
        Assert.AreEqual(1L, Convert.ToInt64(await fixture.Scalar("SELECT COUNT(*) FROM plans WHERE id=@id AND created_at=updated_at", ("@id", id))));
        Assert.AreEqual("1.2300", (await fixture.Rows("SELECT CAST(weight AS CHAR) FROM plans WHERE id=" + id))[0][0]);
        foreach (string coil in new[] { "dev-abc", " DEV-ABC " }) Assert.AreEqual("plan_coil_already_exists", (await Body(await Post(client, Input(coil)), 409)).GetProperty("errorCode").GetString());
        foreach (string coil in new[] { " \t\u001c", "A\tB", "A\u007f" }) await Body(await Post(client, Input(coil)), 422);
        Assert.AreEqual(1L, Convert.ToInt64(await fixture.Scalar("SELECT COUNT(*) FROM plans")));
        TestContext.WriteLine("AC05/07/13/14: minimal defaults25, complete GET equality, raw coil retained, ASCII canonical409, invalid coil422, one row/times equal.");
        var full = Input("完整-😀"); full["grade"] = string.Concat(Enumerable.Repeat("😀",20)); full["materialStatus"] = "custom"; full["priority"] = 10; full["remark"] = "  remark preserved  "; full["weight"] = "99999999.9999000000"; full["thickness"] = "9999999.999"; full["width"] = "99999999.99";
        foreach (string field in new[] {"density","entryLength","uncoiler1Tension","exitTension","process1Tension","entryLoopTension","exitLoopTension"}) full[field]="99999999.99";
        foreach (string field in new[] {"entryUnitTension","entryLoopUnitTension","processUnitTension","exitLoopUnitTension","exitUnitTension"}) full[field]="99999999.9999";
        var all = (await Body(await Post(client, full))).GetProperty("data");
        Assert.AreEqual("99999999.9999", all.GetProperty("weight").GetString()); Assert.AreEqual("9999999.999", all.GetProperty("thickness").GetString()); Assert.AreEqual("99999999.99", all.GetProperty("width").GetString());
        foreach (var property in full) if (property.Key != "weight") Assert.AreEqual(property.Value!.ToString(), all.GetProperty(property.Key).ToString(), property.Key);
        Assert.AreEqual(all.GetRawText(), (await Body(await client.GetAsync("/api/v1/plans/" + all.GetProperty("id").GetInt32()))).GetProperty("data").GetRawText());
        foreach (var field in new[] {"weight","thickness","width","density","entryUnitTension"})
        {
            var invalid = Input("REJECT-"+field); invalid[field]="0.00001"; await Body(await Post(client, invalid),422);
            invalid[field]="100000000"; await Body(await Post(client, invalid),422);
        }
        var concurrency = await Task.WhenAll(Post(client,Input("SAME-RAW")),Post(client,Input("SAME-RAW")));
        CollectionAssert.AreEquivalent(new[]{200,409},concurrency.Select(x=>(int)x.StatusCode).ToArray());
        Assert.AreEqual(1L,Convert.ToInt64(await fixture.Scalar("SELECT COUNT(*) FROM plans WHERE coil_no='SAME-RAW'")));
        await using (var conn=await fixture.Connect(true))
        {
            string names=string.Join(",",columns.Where(x=>x[0]!="id").Select(x=>"`"+x[0]+"`"));
            await using var command=new MySqlCommand("INSERT INTO plans ("+names+") SELECT "+names+" FROM plans WHERE id=@id",conn);command.Parameters.AddWithValue("@id",id);
            var error=await Assert.ThrowsAsync<MySqlException>(()=>command.ExecuteNonQueryAsync());Assert.AreEqual(1062,error.Number);Assert.IsTrue(DatabaseErrors.IsCoilConflict(error));
        }
        // 不加生产 failpoint/锁：真实并发相同字面竞争，必须观察命名1062与同requestId确认回滚。
        bool uniqueRollback = false;
        for (int attempt=0;attempt<4 && !uniqueRollback;attempt++)
        {
            string coil="UNIQUE-RACE-"+attempt;
            var race=await Task.WhenAll(Enumerable.Range(0,16).Select(_=>Post(client,Input(coil))));
            Assert.AreEqual(1,race.Count(x=>(int)x.StatusCode==200));Assert.AreEqual(15,race.Count(x=>(int)x.StatusCode==409));
            Assert.AreEqual(1L,Convert.ToInt64(await fixture.Scalar("SELECT COUNT(*) FROM plans WHERE coil_no=@coil",("@coil",coil))));
            var events=Directory.GetFiles(Path.Combine(fixture.Root,"http-logs"),"*.jsonl").SelectMany(File.ReadLines).Select(line=>JsonDocument.Parse(line).RootElement.Clone()).ToArray();
            var uniqueIds=events.Where(x=>x.TryGetProperty("event",out var key)&&key.GetString()=="plan_unique_conflict").Select(x=>x.GetProperty("requestId").GetString()).ToHashSet();
            uniqueRollback=events.Any(x=>x.TryGetProperty("event",out var key)&&key.GetString()=="plan_transaction_rolled_back"&&uniqueIds.Contains(x.GetProperty("requestId").GetString()));
        }
        Assert.IsTrue(uniqueRollback,"actual Service named1062 and confirmed rollback must be observed");
        TestContext.WriteLine("AC08/14: actual Service named1062 event and successful rollback share requestId; competing same-literal requests leave exactly one row.");
        Assert.AreEqual(minimal.GetRawText(),(await Body(await client.GetAsync("/api/v1/plans/"+id))).GetProperty("data").GetRawText());
        await Body(await client.GetAsync("/api/v1/plans/2147483647"),404);
        TestContext.WriteLine("AC06/08/09/14: all nonzero/max fields round-trip; invalid Decimal no writes; concurrent same literal200+409/one row; actual named1062 classified, original unchanged.");
        for(int n=0;n<5;n++)await Body(await Post(client,Input("PAGE-"+n)));
        await fixture.Scalar("UPDATE plans SET created_at='2026-10-28 08:00:00',updated_at='2026-10-28 08:00:00' WHERE coil_no LIKE 'PAGE-%'");
        var list=(await Body(await client.GetAsync("/api/v1/plans?coilNo=PAGE-&pageSize=2"))).GetProperty("data");Assert.AreEqual(5,list.GetProperty("total").GetInt32());Assert.AreEqual(3,list.GetProperty("totalPages").GetInt32());
        var listIds=list.GetProperty("items").EnumerateArray().Select(x=>x.GetProperty("id").GetInt32()).ToArray();Assert.IsTrue(listIds[0]>listIds[1]);
        var page2=(await Body(await client.GetAsync("/api/v1/plans?coilNo=PAGE-&pageSize=2&page=2"))).GetProperty("data");Assert.IsTrue(listIds[1]>page2.GetProperty("items")[0].GetProperty("id").GetInt32());
        var beyond=(await Body(await client.GetAsync("/api/v1/plans?coilNo=PAGE-&page=999"))).GetProperty("data");Assert.AreEqual(0,beyond.GetProperty("items").GetArrayLength());Assert.AreEqual(5,beyond.GetProperty("total").GetInt32());
        foreach(string filter in new[]{"grade=G","materialStatus=special","status=planned","coilNo=PAGE-"}) Assert.IsTrue((await Body(await client.GetAsync("/api/v1/plans?"+filter))).GetProperty("data").GetProperty("total").GetInt32()>0);
        foreach(string filter in new[]{"grade=absent","materialStatus=absent","status=absent"}) Assert.AreEqual(0,(await Body(await client.GetAsync("/api/v1/plans?"+filter))).GetProperty("data").GetProperty("total").GetInt32());
        string attack=Uri.EscapeDataString("' OR 1=1; DROP TABLE plans; --");Assert.AreEqual(0,(await Body(await client.GetAsync("/api/v1/plans?coilNo="+attack))).GetProperty("data").GetProperty("total").GetInt32());
        Assert.AreEqual(5,(await Body(await client.GetAsync("/api/v1/plans?coilNo=PAGE-_%"))).GetProperty("data").GetProperty("total").GetInt32());
        Assert.AreEqual((await Body(await client.GetAsync("/api/v1/plans"))).GetProperty("data").GetRawText(),(await Body(await client.GetAsync("/api/v1/plans?priority=1&sort=bad&unknown=x"))).GetProperty("data").GetRawText());
        TestContext.WriteLine("AC10/11: pagination count/pages/beyond/tie id DESC, four filters/empty, parameterized SQL attack, %/_ wildcard, ignored priority/sort verified.");
        int count=Convert.ToInt32(await fixture.Scalar("SELECT COUNT(*) FROM plans"));
        await using(var restarted=new ApiFactory(connection:fixture.AppConnection,logDirectory:Path.Combine(fixture.Root,"restarted-http-logs")))
        {using var c=restarted.CreateClient();await Body(await c.GetAsync("/api/v1/plans/"+id));}
        Assert.AreEqual(count,Convert.ToInt32(await fixture.Scalar("SELECT COUNT(*) FROM plans")));
        Assert.AreEqual(1,(await fixture.Rows("SHOW TABLES")).Count);
        TestContext.WriteLine("AC15/16: new HTTP host reads persisted row; startup/restart leave count/schema unchanged.");
        await DatabaseDisconnectAndRecovery();
    }

    private async Task DatabaseDisconnectAndRecovery()
    {
        var fixture=new MySqlFixture();await using var factory=new ApiFactory(connection:fixture.AppConnection,logDirectory:Path.Combine(fixture.Root,"outage-logs"));using var client=factory.CreateClient();
        int count=Convert.ToInt32(await fixture.Scalar("SELECT COUNT(*) FROM plans"));
        try
        {
            fixture.Stop();
            var error=await Body(await Post(client,Input("DURING-OUTAGE")),503);Assert.AreEqual("plan_database_unavailable",error.GetProperty("errorCode").GetString());
            Assert.IsFalse(error.GetRawText().Contains("Password",StringComparison.OrdinalIgnoreCase));
        }
        finally {fixture.Start();}
        for(int i=0;;i++)
        {
            try {await fixture.Scalar("SELECT 1");break;}
            catch when(i<45){await Task.Delay(1000);}
        }
        Assert.AreEqual(count,Convert.ToInt32(await fixture.Scalar("SELECT COUNT(*) FROM plans")));
        await Body(await Post(client,Input("AFTER-RECOVERY")));await Body(await client.GetAsync("/api/v1/plans?coilNo=AFTER-RECOVERY"));
        Assert.AreEqual(1L,Convert.ToInt64(await fixture.Scalar("SELECT COUNT(*) FROM plans WHERE coil_no='AFTER-RECOVERY'")));
        TestContext.WriteLine("AC15: owned stop -> create503/no row/no leak -> owned start -> real create/list/SELECT success.");
    }
}
