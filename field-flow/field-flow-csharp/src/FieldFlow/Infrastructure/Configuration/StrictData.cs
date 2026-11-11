// 将 YAML / JSON 转换为未经隐式类型转换的有界对象。
using System.Globalization;
using System.Text.Json;
using System.Text.RegularExpressions;
using FieldFlow.Domain;
using YamlDotNet.Core;
using YamlDotNet.Core.Events;
using YamlDotNet.RepresentationModel;

namespace FieldFlow.Infrastructure.Configuration;

internal static partial class StrictData
{
    [GeneratedRegex(@"^-?(?:0|[1-9][0-9]*)$", RegexOptions.CultureInvariant)]
    private static partial Regex IntegerPattern();

    public static object? Json(byte[] bytes)
    {
        using var doc = JsonDocument.Parse(bytes, new JsonDocumentOptions
        {
            MaxDepth = 16,
            AllowTrailingCommas = false,
            CommentHandling = JsonCommentHandling.Disallow
        });
        return FromJson(doc.RootElement, 0);
    }

    private static object? FromJson(JsonElement element, int depth)
    {
        if (depth > 16) throw new ConfigException("config_depth");
        switch (element.ValueKind)
        {
            case JsonValueKind.Object:
                var map = new Dictionary<string, object?>(StringComparer.Ordinal);
                foreach (var property in element.EnumerateObject())
                    if (!map.TryAdd(property.Name, FromJson(property.Value, depth + 1)))
                        throw new ConfigException("config_duplicate_key");
                return map;
            case JsonValueKind.Array:
                return element.EnumerateArray().Select(item => FromJson(item, depth + 1)).ToList();
            case JsonValueKind.String: return element.GetString();
            case JsonValueKind.True: return true;
            case JsonValueKind.False: return false;
            case JsonValueKind.Null: return null;
            case JsonValueKind.Number:
                var raw = element.GetRawText();
                if (!IntegerPattern().IsMatch(raw) ||
                    !long.TryParse(raw, NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture, out var value))
                    throw new ConfigException("config_integer");
                return value;
            default: throw new ConfigException("config_type");
        }
    }

    public static object? Yaml(string text)
    {
        var parser = new Parser(new StringReader(text));
        while (parser.MoveNext())
        {
            if (parser.Current is AnchorAlias ||
                parser.Current is NodeEvent node && !node.Anchor.IsEmpty)
                throw new ConfigException("config_yaml_anchor");
            if (parser.Current is NodeEvent tagged && !tagged.Tag.IsEmpty)
                throw new ConfigException("config_yaml_tag");
        }
        var stream = new YamlStream();
        stream.Load(new StringReader(text));
        if (stream.Documents.Count != 1) throw new ConfigException("config_yaml_document");
        return FromYaml(stream.Documents[0].RootNode, 0);
    }

    private static object? FromYaml(YamlNode node, int depth)
    {
        if (depth > 16) throw new ConfigException("config_depth");
        switch (node)
        {
            case YamlMappingNode mapping:
                var map = new Dictionary<string, object?>(StringComparer.Ordinal);
                foreach (var pair in mapping.Children)
                {
                    if (pair.Key is not YamlScalarNode key || key.Value is null || key.Value == "<<")
                        throw new ConfigException("config_yaml_key");
                    if (!map.TryAdd(key.Value, FromYaml(pair.Value, depth + 1)))
                        throw new ConfigException("config_duplicate_key");
                }
                return map;
            case YamlSequenceNode sequence:
                return sequence.Children.Select(item => FromYaml(item, depth + 1)).ToList();
            case YamlScalarNode scalar:
                var value = scalar.Value ?? "";
                if (scalar.Style != ScalarStyle.Plain) return value;
                if (value is "null" or "Null" or "NULL" or "~" or "") return null;
                if (value == "true") return true;
                if (value == "false") return false;
                if (IntegerPattern().IsMatch(value))
                {
                    if (!long.TryParse(value, NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture, out var number))
                        throw new ConfigException("config_integer");
                    return number;
                }
                return value;
            default: throw new ConfigException("config_yaml_node");
        }
    }

    public static Dictionary<string, object?> Map(object? value, string[] required, params string[] optional)
    {
        if (value is not Dictionary<string, object?> map) throw new ConfigException("config_object");
        var allowed = required.Concat(optional).ToHashSet(StringComparer.Ordinal);
        if (map.Keys.Any(k => !allowed.Contains(k)) || required.Any(k => !map.ContainsKey(k)) ||
            map.Values.Any(v => v is null))
            throw new ConfigException("config_fields");
        return map;
    }

    public static List<object?> List(object? value, int min, int max)
    {
        if (value is not List<object?> list || list.Count < min || list.Count > max)
            throw new ConfigException("config_list");
        return list;
    }

    public static string String(object? value, int maxBytes = 64)
    {
        if (value is not string text || text.Length == 0 || System.Text.Encoding.UTF8.GetByteCount(text) > maxBytes)
            throw new ConfigException("config_string");
        return text;
    }

    public static string Id(object? value)
    {
        var id = String(value);
        if (id.Any(ch => !(char.IsAsciiLetterOrDigit(ch) || ch is '_' or '-')))
            throw new ConfigException("config_id");
        return id;
    }

    public static int Integer(object? value, int min, int max)
    {
        if (value is not long n || n < min || n > max) throw new ConfigException("config_integer");
        return (int)n;
    }

    public static bool Enabled(Dictionary<string, object?> value)
    {
        if (!value.TryGetValue("enabled", out var enabled)) return true;
        return enabled is bool b ? b : throw new ConfigException("config_bool");
    }

    public static void OptionalText(Dictionary<string, object?> value, string key, int max)
    {
        if (value.TryGetValue(key, out var text)) _ = String(text, max);
    }
}
