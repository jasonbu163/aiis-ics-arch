// 重启恢复必须保留 unknown 并阻挡同一物理目标的新命令。
using FieldFlow.Domain;
using FieldFlow.Infrastructure.State;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace FieldFlow.Tests;

[TestClass]
public sealed class StateTests
{
    [TestMethod]
    public async Task InFlightRecoversAsUnknownAndBlocksOverlappingWrite()
    {
        var root = Directory.CreateTempSubdirectory("ff003-state-");
        var path = Path.Combine(root.FullName, "state");
        var point = new Point("value", 1, 16, 0, true);
        var plc = new Plc("s7_a", "127.0.0.1", 34102, 0, 1, 1000, 1000, 4, 500, 1000,
            new Dictionary<string, Point> { [point.Id] = point });
        var now = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
        var first = new Command("feed", "id1", 42, now, now + 30000, "flow", "business",
            plc.Id, point.Id, plc, point, now + 10000, 500, 10000, "http://127.0.0.1:34880/demo01/command");
        try
        {
            StateStore.Initialize(path, "execute", "test");
            using (var state = StateStore.Open(path, "execute", "test"))
            {
                Assert.AreEqual("pending", await state.AdmitAsync(first));
                Assert.AreEqual("identity_conflict", await state.AdmitAsync(first with { InputMaxAgeMs = 5000 }));
                Assert.IsTrue(await state.DispatchAsync(first));
            }
            using (var reopened = StateStore.Open(path, "execute", "test"))
            {
                Assert.AreEqual("unknown", await reopened.AdmitAsync(first));
                Assert.AreEqual("unknown_blocked", await reopened.AdmitAsync(first with { CommandId = "id2" }));
            }
            var inspection = System.Text.Json.JsonSerializer.SerializeToElement(StateStore.Inspect(path));
            var unresolved = inspection.GetProperty("unresolved");
            Assert.AreEqual(1, unresolved.GetArrayLength());
            Assert.AreEqual("id1", unresolved[0].GetProperty("command_id").GetString());
        }
        finally { root.Delete(true); }
    }

    [TestMethod]
    public void MismatchedStateDoesNotChangeDatabaseOrKeepLock()
    {
        var root = Directory.CreateTempSubdirectory("ff003-state-id-");
        var path = Path.Combine(root.FullName, "state");
        try
        {
            StateStore.Initialize(path, "execute", "test");
            var database = Path.Combine(path, "state.sqlite3");
            var before = System.Security.Cryptography.SHA256.HashData(File.ReadAllBytes(database));
            Assert.ThrowsExactly<ConfigException>(() => StateStore.Open(path, "dry_run", "test"));
            CollectionAssert.AreEqual(before, System.Security.Cryptography.SHA256.HashData(File.ReadAllBytes(database)));
            using var reopened = StateStore.Open(path, "execute", "test");
        }
        finally { root.Delete(true); }
    }
}
