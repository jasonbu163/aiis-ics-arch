// typed 配置只从显式配置源读取；连接错误不包含原始字符串。
using Microsoft.Extensions.Options;
using MySql.Data.MySqlClient;
using AIIS.Backend.Common.Time;
namespace AIIS.Backend.Configuration;

public sealed class DatabaseOptions
{
    public string ConnectionString { get; set; } = "";
    public int CommandTimeoutSeconds { get; set; } = 5;
    public int ConnectionTimeoutSeconds { get; set; } = 5;
    public static bool Valid(DatabaseOptions options)
    {
        try
        {
            var cs = new MySqlConnectionStringBuilder(options.ConnectionString);
            return !string.IsNullOrWhiteSpace(cs.Server) && !string.IsNullOrWhiteSpace(cs.Database) && !string.IsNullOrWhiteSpace(cs.UserID) && !string.IsNullOrWhiteSpace(cs.Password) && options.CommandTimeoutSeconds == 5 && options.ConnectionTimeoutSeconds == 5;
        }
        catch { return false; }
    }
    public string EffectiveConnectionString()
    {
        var cs = new MySqlConnectionStringBuilder(ConnectionString) { ConnectionTimeout = (uint)ConnectionTimeoutSeconds, DefaultCommandTimeout = (uint)CommandTimeoutSeconds };
        return cs.ConnectionString;
    }
}
public sealed class LoggingOptions { public string Directory { get; set; } = "logs"; }
public sealed class PlanModuleOptions { public bool Enabled { get; set; } = true; }
public static class BackendConfiguration
{
    public static void AddBackendOptions(this IServiceCollection services, IConfiguration config)
    {
        services.AddOptions<DatabaseOptions>().Bind(config.GetSection("Database")).Validate(DatabaseOptions.Valid, "database_configuration_invalid").ValidateOnStart();
        services.AddOptions<LoggingOptions>().Bind(config.GetSection("LoggingOptions")).Validate(x => !string.IsNullOrWhiteSpace(x.Directory), "log_directory_invalid").ValidateOnStart();
        services.AddOptions<PlanModuleOptions>().Bind(config.GetSection("Modules:Plan"));
        if (config["BusinessTimeZone"] != BusinessTime.Zone) throw new InvalidOperationException("business_timezone_invalid");
        var urls = (config["Urls"] ?? "http://127.0.0.1:18108").Split(';');
        if (urls.Any(x => !Uri.TryCreate(x, UriKind.Absolute, out var uri) || uri.Scheme != "http" || uri.Host != "127.0.0.1")) throw new InvalidOperationException("loopback_binding_required");
    }
}
