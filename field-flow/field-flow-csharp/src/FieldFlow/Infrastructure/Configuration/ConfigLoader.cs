// 在产生运行副作用前完成 YAML、点表、身份和容量的整体预检。
using System.Security.Cryptography;
using System.Text;
using FieldFlow.Domain;

namespace FieldFlow.Infrastructure.Configuration;

public static class ConfigLoader
{
    private static readonly UTF8Encoding Utf8 = new(false, true);

    public static RuntimeConfig Load(string path)
    {
        try { return LoadCore(path); }
        catch (ConfigException) { throw; }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or
            System.Text.Json.JsonException or YamlDotNet.Core.YamlException or DecoderFallbackException or
            ArgumentException or OverflowException)
        {
            throw new ConfigException("config_invalid");
        }
    }

    private static RuntimeConfig LoadCore(string path)
    {
        var mainPath = Path.GetFullPath(path);
        RejectAncestors(mainPath);
        var main = ReadLimited(mainPath, 65536);
        var root = StrictData.Map(StrictData.Yaml(Utf8.GetString(main)),
            ["schema_version", "instance_id", "plc_files", "plc_runtime", "flows", "http", "shutdown_timeout_ms"]);
        _ = StrictData.Integer(root["schema_version"], 2, 2);
        var instance = StrictData.Id(root["instance_id"]);
        var directory = Path.GetDirectoryName(mainPath) ?? throw new ConfigException("config_path");
        var files = StrictData.List(root["plc_files"], 1, 4);
        var paths = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        var catalogs = new Dictionary<string, Catalog>(StringComparer.Ordinal);
        var hashes = new Dictionary<string, string>(StringComparer.Ordinal);
        var endpoints = new HashSet<string>(StringComparer.Ordinal);
        var total = 0;
        foreach (var item in files)
        {
            var relative = StrictData.String(item, 255);
            var segments = relative.Split('/');
            if (relative.StartsWith('/') || relative.Contains('\\') || relative.Contains(':') ||
                relative.Contains('*') || relative.Contains('?') || relative.Contains('~') ||
                relative.Contains('$') || segments.Any(UnsafeWindowsSegment))
                throw new ConfigException("config_path");
            var current = directory;
            foreach (var segment in segments)
            {
                current = Path.Combine(current, segment);
                RejectReparse(current);
            }
            var full = Path.GetFullPath(current);
            var within = Path.GetRelativePath(directory, full);
            if (Path.IsPathRooted(within) || within.Split(Path.DirectorySeparatorChar).Any(s => s == ".."))
                throw new ConfigException("config_path");
            if (!paths.Add(full)) throw new ConfigException("config_duplicate_file");
            var raw = ReadLimited(full, 1024 * 1024);
            total += raw.Length;
            if (total > 4 * 1024 * 1024) throw new ConfigException("config_size");
            var catalog = CatalogReader.Read(raw);
            if (!catalogs.TryAdd(catalog.Id, catalog)) throw new ConfigException("config_duplicate_device");
            if (!endpoints.Add(catalog.Host + ":" + catalog.Port)) throw new ConfigException("config_duplicate_endpoint");
            hashes.Add(relative, Convert.ToHexStringLower(SHA256.HashData(raw)));
        }
        var budgets = StrictData.List(root["plc_runtime"], 1, 4);
        var plcs = new Dictionary<string, Plc>(StringComparer.Ordinal);
        foreach (var item in budgets)
        {
            var budget = StrictData.Map(item,
                ["device_id", "connect_timeout_ms", "io_timeout_ms", "queue_capacity", "queue_wait_ms", "ready_wait_ms"]);
            var id = StrictData.Id(budget["device_id"]);
            if (!catalogs.TryGetValue(id, out var catalog)) throw new ConfigException("config_device");
            var plc = new Plc(id, catalog.Host, catalog.Port, catalog.Rack, catalog.Slot,
                StrictData.Integer(budget["connect_timeout_ms"], 500, 3000),
                StrictData.Integer(budget["io_timeout_ms"], 500, 5000),
                StrictData.Integer(budget["queue_capacity"], 1, 16),
                StrictData.Integer(budget["queue_wait_ms"], 100, 5000),
                StrictData.Integer(budget["ready_wait_ms"], 100, 5000), catalog.Points);
            if (!plcs.TryAdd(id, plc)) throw new ConfigException("config_duplicate_device");
        }
        if (plcs.Count != catalogs.Count) throw new ConfigException("config_device");

        var http = StrictData.Map(root["http"],
            ["connect_timeout_ms", "total_timeout_ms", "pool_wait_ms", "max_connections", "max_body_bytes"]);
        var options = new HttpOptions(StrictData.Integer(http["connect_timeout_ms"], 100, 1500),
            StrictData.Integer(http["total_timeout_ms"], 100, 5000),
            StrictData.Integer(http["pool_wait_ms"], 100, 1500),
            StrictData.Integer(http["max_connections"], 1, 8),
            StrictData.Integer(http["max_body_bytes"], 1, 4096));
        if (options.ConnectTimeoutMs > options.TotalTimeoutMs || options.PoolWaitMs > options.TotalTimeoutMs)
            throw new ConfigException("config_http_timeout");

        var flows = new List<Flow>();
        var flowIds = new HashSet<string>(StringComparer.Ordinal);
        var targets = new HashSet<(string Device, int Db, int Offset)>();
        foreach (var item in StrictData.List(root["flows"], 1, 8))
        {
            if (item is not Dictionary<string, object?> rawFlow || !rawFlow.TryGetValue("kind", out var kind))
                throw new ConfigException("config_fields");
            if (StrictData.String(kind) != "demo01") throw new ConfigException("config_flow_kind_unsupported");
            var flow = StrictData.Map(item,
                ["id", "kind", "business_name", "interval_ms", "device_ids", "source_id", "get_url", "input_max_age_ms", "target"]);
            var id = StrictData.Id(flow["id"]);
            if (!flowIds.Add(id)) throw new ConfigException("config_duplicate_flow");
            var deviceIds = StrictData.List(flow["device_ids"], 1, 4).Select(StrictData.Id).ToList();
            if (deviceIds.Distinct(StringComparer.Ordinal).Count() != deviceIds.Count ||
                deviceIds.Any(device => !plcs.ContainsKey(device))) throw new ConfigException("config_device");
            var target = StrictData.Map(flow["target"], ["device_id", "point_id"]);
            var deviceId = StrictData.Id(target["device_id"]);
            var pointId = StrictData.Id(target["point_id"]);
            if (!deviceIds.Contains(deviceId) || !plcs.TryGetValue(deviceId, out var device) ||
                !device.Points.TryGetValue(pointId, out var point) || !point.Enabled)
                throw new ConfigException("config_target");
            if (!targets.Add((deviceId, point.Db, point.Offset))) throw new ConfigException("config_write_conflict");
            var rawUrl = StrictData.String(flow["get_url"], 2048);
            if (!Uri.TryCreate(rawUrl, UriKind.Absolute, out var url) ||
                url.Scheme is not ("http" or "https") || string.IsNullOrEmpty(url.Host) ||
                !string.IsNullOrEmpty(url.UserInfo) || !string.IsNullOrEmpty(url.Fragment))
                throw new ConfigException("config_url");
            flows.Add(new Flow(id, StrictData.Id(flow["business_name"]),
                StrictData.Integer(flow["interval_ms"], 100, 10000), StrictData.Id(flow["source_id"]),
                url, StrictData.Integer(flow["input_max_age_ms"], 1, 60000), deviceId, pointId));
        }
        var shutdown = StrictData.Integer(root["shutdown_timeout_ms"], 5000, 20000);
        if (shutdown < Math.Max(options.TotalTimeoutMs, plcs.Values.Max(p => Math.Max(p.ConnectTimeoutMs, p.IoTimeoutMs))) + 5500)
            throw new ConfigException("config_shutdown_timeout");
        return new RuntimeConfig(instance, plcs, flows, options, shutdown, hashes);
    }

    private static byte[] ReadLimited(string path, int maximum)
    {
        using var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read);
        if (stream.Length > maximum) throw new ConfigException("config_size");
        var bytes = new byte[checked((int)stream.Length)];
        stream.ReadExactly(bytes);
        if (bytes.Length >= 3 && bytes[0] == 0xef && bytes[1] == 0xbb && bytes[2] == 0xbf)
            throw new ConfigException("config_bom");
        _ = Utf8.GetString(bytes);
        return bytes;
    }

    private static void RejectReparse(string path)
    {
        if ((File.GetAttributes(path) & FileAttributes.ReparsePoint) != 0)
            throw new ConfigException("config_path");
    }

    private static void RejectAncestors(string fullPath)
    {
        var root = Path.GetPathRoot(fullPath) ?? throw new ConfigException("config_path");
        var current = root;
        foreach (var segment in fullPath[root.Length..].Split(Path.DirectorySeparatorChar,
                     StringSplitOptions.RemoveEmptyEntries))
        {
            current = Path.Combine(current, segment);
            RejectReparse(current);
        }
    }

    private static bool UnsafeWindowsSegment(string segment)
    {
        if (segment is "" or "." or ".." || segment.EndsWith('.') || segment.EndsWith(' '))
            return true;
        var basename = segment.Split('.')[0];
        if (basename.Equals("CON", StringComparison.OrdinalIgnoreCase) ||
            basename.Equals("PRN", StringComparison.OrdinalIgnoreCase) ||
            basename.Equals("AUX", StringComparison.OrdinalIgnoreCase) ||
            basename.Equals("NUL", StringComparison.OrdinalIgnoreCase))
            return true;
        return basename.Length == 4 &&
            (basename.StartsWith("COM", StringComparison.OrdinalIgnoreCase) ||
             basename.StartsWith("LPT", StringComparison.OrdinalIgnoreCase)) &&
            basename[3] is >= '1' and <= '9';
    }
}
