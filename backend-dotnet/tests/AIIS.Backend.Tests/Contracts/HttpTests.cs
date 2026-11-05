// 真实路由宿主的无库输入失败、模块开关与 OpenAPI 测试。
using System.Net;
using System.Text;
using System.Text.Json;
using AIIS.Backend.Common.Modules;
using AIIS.Backend.Tests.Domain;
using AIIS.Backend.Tests.Fixtures;
using Microsoft.VisualStudio.TestTools.UnitTesting;
namespace AIIS.Backend.Tests.Contracts;

[TestClass]
public sealed class HttpTests
{
    [TestMethod]
    public async Task EnabledRoutesAndStrictFailuresDoNotNeedDatabase()
    {
        await using var factory = new ApiFactory(); using var client = factory.CreateClient();
        Assert.AreEqual(HttpStatusCode.OK, (await client.GetAsync("/health")).StatusCode);
        using var spec = JsonDocument.Parse(await client.GetStringAsync("/openapi/v1.json"));
        var paths = spec.RootElement.GetProperty("paths");
        Assert.AreEqual(2, paths.EnumerateObject().Count(x => x.Name.StartsWith("/api/v1/plans")));
        Assert.IsTrue(paths.GetProperty("/api/v1/plans").TryGetProperty("post", out _));
        Assert.IsFalse(spec.RootElement.GetRawText().Contains("Bearer", StringComparison.OrdinalIgnoreCase));
        var createSchema = spec.RootElement.GetProperty("components").GetProperty("schemas").EnumerateObject().Single(x=>x.Name.EndsWith("CreatePlanIn",StringComparison.Ordinal)).Value;
        Assert.AreEqual(6,createSchema.GetProperty("required").GetArrayLength());
        Assert.AreEqual(2,createSchema.GetProperty("properties").GetProperty("weight").GetProperty("anyOf").GetArrayLength());
        Assert.AreEqual(6,paths.GetProperty("/api/v1/plans").GetProperty("get").GetProperty("parameters").GetArrayLength());
        foreach (string json in new[] { "{}", "[]", InputTests.Minimal.Replace("\"G\"", "null"), InputTests.Minimal.Replace("}", ",\"weight\":2}"), InputTests.Minimal.Replace("\"1.2300\"", "0.00001") })
        {
            using var response = await client.PostAsync("/api/v1/plans", new StringContent(json, Encoding.UTF8, "application/json"));
            Assert.AreEqual(422, (int)response.StatusCode, await response.Content.ReadAsStringAsync());
            using var body = JsonDocument.Parse(await response.Content.ReadAsStringAsync());
            Assert.AreEqual("plan_invalid_request", body.RootElement.GetProperty("errorCode").GetString());
            Assert.AreEqual(JsonValueKind.Null, body.RootElement.GetProperty("data").ValueKind);
            Assert.IsTrue(response.Headers.Contains("X-Request-Id"));
        }
        foreach (string path in new[] { "/api/v1/plans/0", "/api/v1/plans/-1", "/api/v1/plans/1.2", "/api/v1/plans/2147483648", "/api/v1/plans?page=0", "/api/v1/plans?pageSize=101", "/api/v1/plans?page=2147483647&pageSize=100", "/api/v1/plans?page=1e0" })
            Assert.AreEqual(422, (int)(await client.GetAsync(path)).StatusCode, path);
        Assert.AreEqual(405, (int)(await client.DeleteAsync("/api/v1/plans/1")).StatusCode);
        Assert.AreEqual(404, (int)(await client.GetAsync("/unknown")).StatusCode);
        Assert.AreNotEqual(200, (int)(await client.GetAsync("/api/v1/plans/xlsx/template")).StatusCode);
    }
    [TestMethod]
    public async Task UnsupportedMediaHasUnifiedEnvelopeWithoutChangingRouting()
    {
        await using var factory = new ApiFactory(); using var client = factory.CreateClient();
        foreach (string? mediaType in new string?[] { "text/plain", "application/octet-stream", "application/x-www-form-urlencoded", "application/merge-patch+json", null })
        {
            using var content = new ByteArrayContent(Encoding.UTF8.GetBytes(InputTests.Minimal));
            if (mediaType is not null) content.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue(mediaType);
            long started = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
            using var response = await client.PostAsync("/api/v1/plans", content);
            string text = await response.Content.ReadAsStringAsync();
            Assert.AreEqual(415, (int)response.StatusCode, mediaType);
            Assert.IsTrue(text.Length > 0, "415 must contain the unified error envelope: " + mediaType);
            Assert.AreEqual("application/json", response.Content.Headers.ContentType?.MediaType);
            using var body = JsonDocument.Parse(text);
            var error = body.RootElement;
            Assert.AreEqual(415, error.GetProperty("code").GetInt32());
            Assert.AreEqual("plan_invalid_request", error.GetProperty("message").GetString());
            Assert.AreEqual("plan_invalid_request", error.GetProperty("errorCode").GetString());
            Assert.AreEqual(JsonValueKind.Null, error.GetProperty("data").ValueKind);
            Assert.IsTrue(error.GetProperty("timestamp").GetInt64() >= started);
            Assert.IsTrue(error.GetProperty("timestamp").GetInt64() <= DateTimeOffset.UtcNow.ToUnixTimeMilliseconds());
            Assert.IsTrue(response.Headers.TryGetValues("X-Request-Id", out var ids) && ids.Single().Length > 0);
        }
        // 基础404/405不得被转换为业务错误；合法JSON仍走原422绑定失败路径。
        using var unknown = await client.PostAsync("/unknown", new StringContent(InputTests.Minimal, Encoding.UTF8, "text/plain"));
        Assert.AreEqual(404, (int)unknown.StatusCode);
        using var unsupported = await client.SendAsync(new HttpRequestMessage(HttpMethod.Delete, "/api/v1/plans/1") { Content = new StringContent(InputTests.Minimal, Encoding.UTF8, "text/plain") });
        Assert.AreEqual(405, (int)unsupported.StatusCode);
        using var invalidJson = await client.PostAsync("/api/v1/plans", new StringContent("{}", Encoding.UTF8, "application/json"));
        Assert.AreEqual(422, (int)invalidJson.StatusCode);
        using var invalid = JsonDocument.Parse(await invalidJson.Content.ReadAsStringAsync());
        Assert.AreEqual("plan_invalid_request", invalid.RootElement.GetProperty("errorCode").GetString());
    }
    [TestMethod]
    public async Task DisabledModuleHasNoRoutesOrOpenApi()
    {
        // 模块采用需要进程重启；FastEndpoints 同进程多宿主复用注册缓存，故验证真实新进程。
        using (var probe = new System.Net.Sockets.TcpListener(IPAddress.Loopback, 18108)) { probe.Start(); probe.Stop(); }
        string apiRoot = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "../../../../../"));
        string dotnet = Path.GetFullPath(Path.Combine(System.Runtime.InteropServices.RuntimeEnvironment.GetRuntimeDirectory(), "../../../dotnet"));
        string logs = Path.Combine("/private/tmp", "arch-be008-disabled-" + Guid.NewGuid().ToString("N"));
        var info = new System.Diagnostics.ProcessStartInfo(dotnet) { WorkingDirectory = apiRoot, RedirectStandardOutput = true, RedirectStandardError = true };
        info.ArgumentList.Add(Path.Combine(apiRoot, "bin/Debug/net10.0/AIIS.Backend.Api.dll"));
        info.Environment["Database__ConnectionString"] = "Server=127.0.0.1;Port=13388;Database=arch_be008_plan;User ID=arch_be008_app;Password=test-only-placeholder";
        info.Environment["Modules__Plan__Enabled"] = "false"; info.Environment["LoggingOptions__Directory"] = logs;
        info.Environment["DOTNET_GENERATE_ASPNET_CERTIFICATE"] = "false";
        using var process = System.Diagnostics.Process.Start(info)!;
        var stdout = process.StandardOutput.ReadToEndAsync(); var stderr = process.StandardError.ReadToEndAsync();
        try
        {
            using var client = new HttpClient { BaseAddress = new Uri("http://127.0.0.1:18108") };
            for (int i=0;;i++)
            {
                try { Assert.AreEqual(200,(int)(await client.GetAsync("/health")).StatusCode); break; }
                catch (HttpRequestException) when (i < 50 && !process.HasExited) { await Task.Delay(100); }
            }
            Assert.AreEqual(404, (int)(await client.GetAsync("/api/v1/plans")).StatusCode);
            Assert.AreEqual(404, (int)(await client.PostAsync("/api/v1/plans", new StringContent("{}", Encoding.UTF8, "application/json"))).StatusCode);
            Assert.AreEqual(404, (int)(await client.GetAsync("/api/v1/plans/1")).StatusCode);
            Assert.IsFalse((await client.GetStringAsync("/openapi/v1.json")).Contains("/api/v1/plans", StringComparison.Ordinal));
        }
        finally
        {
            if (!process.HasExited) { using var stop = System.Diagnostics.Process.Start("/bin/kill", "-TERM " + process.Id); await stop!.WaitForExitAsync(); await process.WaitForExitAsync(); }
            await stdout; await stderr;
        }
    }
    [TestMethod]
    public void ModuleMetadataRejectsInvalidComposition()
    {
        var one = new ModuleDefinition("one", true, [], ["GET /one"], [], typeof(object), typeof(object));
        Assert.Throws<InvalidOperationException>(() => ModuleRegistry.Validate([one, one]));
        Assert.Throws<InvalidOperationException>(() => ModuleRegistry.Validate([one with { Dependencies = ["missing"] }]));
        Assert.Throws<InvalidOperationException>(() => ModuleRegistry.Validate([one, one with { Id = "two" }]));
    }
    [TestMethod]
    public void MissingConnectionFailsWithoutSecretLeak()
    {
        using var factory = new ApiFactory(connection: "");
        var error = Assert.Throws<Microsoft.Extensions.Options.OptionsValidationException>(() => factory.CreateClient());
        Assert.IsTrue(error.Message.Contains("database_configuration_invalid", StringComparison.Ordinal));
        Assert.IsFalse(error.Message.Contains("Password", StringComparison.OrdinalIgnoreCase));
    }
}
