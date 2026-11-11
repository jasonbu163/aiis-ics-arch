// 仅显式命令可访问配置、状态目录或启动运行时。
using System.Reflection;
using System.Text.Json;
using FieldFlow.Domain;
using FieldFlow.Infrastructure.Configuration;
using FieldFlow.Infrastructure.State;
using FieldFlow.Runtime;
using Microsoft.Data.Sqlite;

namespace FieldFlow.Cli;

internal static class Commands
{
    public static async Task<int> RunAsync(string[] raw)
    {
        var language = "zh-CN";
        try
        {
            var args = raw.ToList();
            var index = args.IndexOf("--lang");
            if (index >= 0)
            {
                if (index + 1 >= args.Count || args.Count(arg => arg == "--lang") != 1)
                    throw new ConfigException("arguments");
                var requestedLanguage = args[index + 1];
                if (requestedLanguage is not ("zh-CN" or "en-US")) throw new ConfigException("language");
                language = requestedLanguage;
                args.RemoveRange(index, 2);
            }
            if (args.Count == 0 || args.Count == 1 && args[0] == "--help")
            {
                Console.WriteLine(JsonSerializer.Serialize(new { help = Text(language, "help") }));
                return 0;
            }
            if (args.Count >= 2 && args[0] == "config" && args[1] == "validate")
            {
                var options = Options(args.Skip(2), ["--config"], []);
                var config = ConfigLoader.Load(options["--config"]!);
                Console.WriteLine(JsonSerializer.Serialize(new
                {
                    format_valid = true, runtime_compatible = true, files = config.CatalogHashes
                }));
                return 0;
            }
            if (args.Count >= 2 && args[0] == "state" && args[1] == "init")
            {
                var options = Options(args.Skip(2), ["--mode", "--state-dir", "--instance-id"], ["--synthetic"]);
                _ = StrictData.Id(options["--instance-id"]);
                StateStore.Initialize(options["--state-dir"]!, options["--mode"]!, options["--instance-id"]!);
                Console.WriteLine(JsonSerializer.Serialize(new { result = "initialized" }));
                return 0;
            }
            if (args.Count >= 2 && args[0] == "state" && args[1] == "inspect")
            {
                var options = Options(args.Skip(2), ["--state-dir"], []);
                Console.WriteLine(JsonSerializer.Serialize(StateStore.Inspect(options["--state-dir"]!)));
                return 0;
            }
            if (args[0] == "run")
            {
                var options = Options(args.Skip(1), ["--config", "--state-dir"], [], ["--execute"]);
                var config = ConfigLoader.Load(options["--config"]!);
                return await FlowRuntime.RunAsync(config, options["--state-dir"]!, options.ContainsKey("--execute"));
            }
            throw new ConfigException("arguments");
        }
        catch (ConfigException error)
        {
            Error(language, error.Key);
            return 2;
        }
        catch (Exception error) when (error is SqliteException or ArgumentException)
        {
            Error(language, "state_invalid");
            return 2;
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            Error(language, "operation_failed");
            return 1;
        }
    }

    private static Dictionary<string, string?> Options(IEnumerable<string> source,
        string[] values, string[] requiredFlags, string[]? optionalFlags = null)
    {
        var args = source.ToArray();
        var flags = requiredFlags.Concat(optionalFlags ?? []).ToHashSet(StringComparer.Ordinal);
        var result = new Dictionary<string, string?>(StringComparer.Ordinal);
        for (var i = 0; i < args.Length; i++)
        {
            var key = args[i];
            if (flags.Contains(key))
            {
                if (!result.TryAdd(key, null)) throw new ConfigException("arguments");
            }
            else if (values.Contains(key) && i + 1 < args.Length && !args[i + 1].StartsWith("--", StringComparison.Ordinal))
            {
                if (!result.TryAdd(key, args[++i])) throw new ConfigException("arguments");
            }
            else throw new ConfigException("arguments");
        }
        if (values.Concat(requiredFlags).Any(key => !result.ContainsKey(key)))
            throw new ConfigException("arguments");
        return result;
    }

    private static string Text(string language, string key)
    {
        using var stream = Assembly.GetExecutingAssembly()
            .GetManifestResourceStream("FieldFlow.Locale." + language + ".json")
            ?? throw new InvalidOperationException("locale_missing");
        using var document = JsonDocument.Parse(stream);
        return document.RootElement.GetProperty(key).GetString()!;
    }

    private static void Error(string language, string key) =>
        Console.Error.WriteLine(JsonSerializer.Serialize(new { error_key = key, message = Text(language, "error") }));
}
