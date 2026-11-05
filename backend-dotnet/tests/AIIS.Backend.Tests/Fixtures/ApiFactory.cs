// 测试专用 HTTP 宿主：固定源码根和显式测试配置，无生产测试钩子。
using AIIS.Backend.Configuration;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
namespace AIIS.Backend.Tests.Fixtures;

public sealed class ApiFactory(bool enabled = true, string? connection = null, string? logDirectory = null) : WebApplicationFactory<Program>
{
    public string Logs { get; } = logDirectory ?? Path.Combine("/private/tmp", "arch-be008-test-logs-" + Guid.NewGuid().ToString("N"));
    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.UseContentRoot(Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "../../../../../")));
        builder.ConfigureAppConfiguration((_, config) => config.AddInMemoryCollection(new Dictionary<string, string?>
        {
            ["Database:ConnectionString"] = connection ?? "Server=127.0.0.1;Port=13388;Database=arch_be008_plan;User ID=arch_be008_app;Password=test-only-placeholder",
            ["Modules:Plan:Enabled"] = enabled.ToString(), ["BusinessTimeZone"] = "Asia/Shanghai",
            ["LoggingOptions:Directory"] = Logs, ["Urls"] = "http://127.0.0.1:18108"
        }));
    }
}
