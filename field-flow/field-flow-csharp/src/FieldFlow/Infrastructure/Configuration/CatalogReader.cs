// 解析一个 PLC JSON，并冻结已校验的设备与点位。
using System.Net;
using System.Net.Sockets;
using FieldFlow.Domain;

namespace FieldFlow.Infrastructure.Configuration;

internal sealed record Catalog(string Id, string Host, int Port, int Rack, int Slot,
    IReadOnlyDictionary<string, Point> Points);

internal static class CatalogReader
{
    public static Catalog Read(byte[] bytes)
    {
        var root = StrictData.Map(StrictData.Json(bytes),
            ["format", "schema_version", "id", "protocol", "source", "connection"],
            "name", "display_name", "description", "metadata", "dbs", "tables");
        if (StrictData.String(root["format"]) != "ff.plc" || StrictData.Integer(root["schema_version"], 1, 1) != 1)
            throw new ConfigException("config_version");
        var id = StrictData.Id(root["id"]);
        var protocol = StrictData.String(root["protocol"]);
        if (protocol == "modbus_tcp") throw new ConfigException("unsupported_protocol");
        if (protocol != "s7") throw new ConfigException("unsupported_protocol");
        if (!root.ContainsKey("dbs") || root.ContainsKey("tables")) throw new ConfigException("config_fields");
        StrictData.OptionalText(root, "name", 128);
        StrictData.OptionalText(root, "display_name", 256);
        StrictData.OptionalText(root, "description", 1024);
        if (root.TryGetValue("metadata", out var metadata))
        {
            var info = StrictData.Map(metadata, [], "brand", "model", "firmware");
            foreach (var value in info.Values) _ = StrictData.String(value, 128);
        }
        if (root["source"] is not Dictionary<string, object?> rawSource ||
            !rawSource.TryGetValue("kind", out var sourceKind))
            throw new ConfigException("config_fields");
        if (StrictData.String(sourceKind) != "manual") throw new ConfigException("unsupported_source");
        var source = StrictData.Map(rawSource, ["kind"], "note");
        StrictData.OptionalText(source, "note", 512);
        var connection = StrictData.Map(root["connection"], ["host", "port", "rack", "slot"],
            "local_tsap", "remote_tsap");
        var host = StrictData.String(connection["host"], 15);
        if (!IPAddress.TryParse(host, out var address) || address.AddressFamily != AddressFamily.InterNetwork ||
            address.ToString() != host || address.GetAddressBytes()[0] is 0 or >= 224)
            throw new ConfigException("config_host");
        var port = StrictData.Integer(connection["port"], 1, 65535);
        var rack = StrictData.Integer(connection["rack"], 0, 7);
        var slot = StrictData.Integer(connection["slot"], 0, 31);
        if (connection.TryGetValue("local_tsap", out var local) && StrictData.Integer(local, 1, 65535) != 256 ||
            connection.TryGetValue("remote_tsap", out var remote) &&
            StrictData.Integer(remote, 1, 65535) != 256 + rack * 32 + slot)
            throw new ConfigException("unsupported_connection");

        var points = new Dictionary<string, Point>(StringComparer.Ordinal);
        var blockNumbers = new HashSet<int>();
        var blocks = StrictData.List(root["dbs"], 1, 64);
        var occupied = new HashSet<(int Db, int Byte)>();
        foreach (var item in blocks)
        {
            var db = StrictData.Map(item, ["number", "size_bytes", "points"], "enabled");
            var number = StrictData.Integer(db["number"], 1, 65535);
            var size = StrictData.Integer(db["size_bytes"], 2, 65536);
            if (!blockNumbers.Add(number)) throw new ConfigException("config_duplicate_db");
            var dbEnabled = StrictData.Enabled(db);
            foreach (var pointValue in StrictData.List(db["points"], 1, 4096))
            {
                var pt = StrictData.Map(pointValue, ["id", "data_type", "byte_offset"],
                    "enabled", "name", "display_name", "source_name", "source_path", "source_native_type");
                var pointId = StrictData.Id(pt["id"]);
                if (StrictData.String(pt["data_type"]) != "int16") throw new ConfigException("unsupported_type");
                var offset = StrictData.Integer(pt["byte_offset"], 0, 65534);
                if (offset + 2 > size || !occupied.Add((number, offset)) || !occupied.Add((number, offset + 1)))
                    throw new ConfigException("config_point_overlap");
                StrictData.OptionalText(pt, "name", 128);
                StrictData.OptionalText(pt, "display_name", 256);
                StrictData.OptionalText(pt, "source_name", 256);
                StrictData.OptionalText(pt, "source_path", 1024);
                StrictData.OptionalText(pt, "source_native_type", 32);
                if (!points.TryAdd(pointId, new Point(pointId, number, size, offset, dbEnabled && StrictData.Enabled(pt))))
                    throw new ConfigException("config_duplicate_point");
                if (points.Count > 4096) throw new ConfigException("config_point_limit");
            }
        }
        return new Catalog(id, host, port, rack, slot, points);
    }
}
