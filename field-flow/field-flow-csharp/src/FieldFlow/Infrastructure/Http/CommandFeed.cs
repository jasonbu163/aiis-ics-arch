// 严格解析来源命令，保持来源时间和响应体的单次总期限。
using System.Net;
using System.Net.Http.Headers;
using System.Text.Json;
using System.Text.RegularExpressions;
using FieldFlow.Domain;

namespace FieldFlow.Infrastructure.Http;

internal sealed partial class CommandFeed : IDisposable
{
    private static readonly string[] Fields =
        ["schema_version", "source_id", "ready", "command_id", "value", "issued_at_ms", "expires_at_ms"];
    private readonly HttpOptions options;
    private readonly HttpClient http;
    private readonly SemaphoreSlim pool;

    [GeneratedRegex(@"^-?(?:0|[1-9][0-9]*)$", RegexOptions.CultureInvariant)]
    private static partial Regex IntegerPattern();

    public CommandFeed(HttpOptions options)
    {
        this.options = options;
        http = new HttpClient(new SocketsHttpHandler
        {
            AllowAutoRedirect = false,
            UseProxy = false,
            ConnectTimeout = TimeSpan.FromMilliseconds(options.ConnectTimeoutMs),
            MaxConnectionsPerServer = options.MaxConnections
        }) { Timeout = Timeout.InfiniteTimeSpan };
        pool = new SemaphoreSlim(options.MaxConnections);
    }

    public async Task<Command?> GetAsync(Flow flow, Plc plc, Point point, CancellationToken stop)
    {
        using var total = CancellationTokenSource.CreateLinkedTokenSource(stop);
        total.CancelAfter(options.TotalTimeoutMs);
        using var poolDeadline = CancellationTokenSource.CreateLinkedTokenSource(total.Token);
        poolDeadline.CancelAfter(options.PoolWaitMs);
        await pool.WaitAsync(poolDeadline.Token);
        try
        {
            using var response = await http.GetAsync(flow.GetUrl, HttpCompletionOption.ResponseHeadersRead, total.Token);
            if (response.StatusCode != HttpStatusCode.OK ||
                response.Content.Headers.ContentType?.MediaType != "application/json")
                throw new IOException("http_response");
            var charset = response.Content.Headers.ContentType?.CharSet;
            if (charset is not null && !charset.Trim('"').Equals("utf-8", StringComparison.OrdinalIgnoreCase))
                throw new IOException("http_charset");
            await using var input = await response.Content.ReadAsStreamAsync(total.Token);
            using var body = new MemoryStream();
            var buffer = new byte[1024];
            int count;
            while ((count = await input.ReadAsync(buffer, total.Token)) != 0)
            {
                if (body.Length + count > options.MaxBodyBytes) throw new IOException("http_body_size");
                body.Write(buffer, 0, count);
            }
            return Parse(body.ToArray(), flow, plc, point);
        }
        finally { pool.Release(); }
    }

    internal static Command? Parse(byte[] body, Flow flow, Plc plc, Point point)
    {
        try
        {
            using var document = JsonDocument.Parse(body, new JsonDocumentOptions { MaxDepth = 8 });
            if (document.RootElement.ValueKind != JsonValueKind.Object) throw new IOException("input_shape");
            var fields = new Dictionary<string, JsonElement>(StringComparer.Ordinal);
            foreach (var property in document.RootElement.EnumerateObject())
                if (!fields.TryAdd(property.Name, property.Value)) throw new IOException("input_duplicate");
            if (fields.Count != Fields.Length || Fields.Any(field => !fields.ContainsKey(field)))
                throw new IOException("input_shape");
            if (Number(fields["schema_version"]) != 1 ||
                fields["source_id"].ValueKind != JsonValueKind.String ||
                fields["source_id"].GetString() != flow.SourceId)
                throw new IOException("input_source");
            var ready = fields["ready"];
            if (ready.ValueKind is not (JsonValueKind.True or JsonValueKind.False)) throw new IOException("input_ready");
            if (!ready.GetBoolean())
            {
                if (new[] { "command_id", "value", "issued_at_ms", "expires_at_ms" }
                    .Any(field => fields[field].ValueKind != JsonValueKind.Null))
                    throw new IOException("input_idle");
                return null;
            }
            if (fields["command_id"].ValueKind != JsonValueKind.String) throw new IOException("input_id");
            var id = fields["command_id"].GetString() ?? "";
            if (id.Length is < 1 or > 64 || id.Any(ch => !(char.IsAsciiLetterOrDigit(ch) || ch is '_' or '-')))
                throw new IOException("input_id");
            var value = Number(fields["value"]);
            var issued = Number(fields["issued_at_ms"]);
            var expires = Number(fields["expires_at_ms"]);
            var now = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
            if (value is < short.MinValue or > short.MaxValue || issued <= 0 || expires <= issued ||
                expires - issued > 60000 || issued > now + 1000 || now >= expires ||
                now - issued > flow.InputMaxAgeMs)
                throw new IOException("input_expired");
            var deadline = Math.Min(expires, checked(issued + flow.InputMaxAgeMs));
            return new Command(flow.SourceId, id, (short)value, issued, expires, flow.Id, flow.BusinessName,
                flow.DeviceId, flow.PointId, plc, point, deadline, flow.IntervalMs,
                flow.InputMaxAgeMs, flow.GetUrl.AbsoluteUri);
        }
        catch (Exception error) when (error is JsonException or OverflowException or InvalidOperationException)
        {
            throw new IOException("input_invalid", error);
        }
    }

    private static long Number(JsonElement element)
    {
        if (element.ValueKind != JsonValueKind.Number || !IntegerPattern().IsMatch(element.GetRawText()) ||
            !element.TryGetInt64(out var value)) throw new IOException("input_number");
        return value;
    }

    public void Dispose()
    {
        http.Dispose();
        pool.Dispose();
    }
}
