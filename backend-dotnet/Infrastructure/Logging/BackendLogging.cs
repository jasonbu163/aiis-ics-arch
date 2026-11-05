// 紧凑 JSON Lines stdout + 10MiB/5 文件滚动；不输出异常正文或 SQL 参数。
using Serilog;
using Serilog.Events;
using Serilog.Formatting.Compact;
namespace AIIS.Backend.Infrastructure.Logging;

public static class BackendLogging
{
    public const long FileLimit = 10 * 1024 * 1024;
    public const int RetainedFiles = 5;
    public static LoggerConfiguration Configure(LoggerConfiguration logger, string directory) => logger.MinimumLevel.Information()
        .MinimumLevel.Override("Microsoft", LogEventLevel.Fatal).MinimumLevel.Override("System", LogEventLevel.Fatal)
        .Enrich.FromLogContext().WriteTo.Console(new CompactJsonFormatter())
        .WriteTo.File(new CompactJsonFormatter(), Path.Combine(directory, "backend-.jsonl"), rollingInterval: RollingInterval.Day, fileSizeLimitBytes: FileLimit, rollOnFileSizeLimit: true, retainedFileCountLimit: RetainedFiles, shared: true);
}
