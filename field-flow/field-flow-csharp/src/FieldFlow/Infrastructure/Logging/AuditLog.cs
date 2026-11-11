// 输出受限 JSONL 事件并轮转持久文件。
using System.Text;
using System.Text.Json;
using FieldFlow.Domain;

namespace FieldFlow.Infrastructure.Logging;

internal sealed class AuditException(Exception inner) : IOException("audit_failed", inner);

internal sealed class AuditLog(string directory, string instance) : IDisposable
{
    private readonly object sync = new();
    private readonly string path = Path.Combine(directory, "runtime.jsonl");
    private const int MaxBytes = 5 * 1024 * 1024;

    public Task WriteAsync(string eventName, string? flow = null, string? result = null,
        string? commandId = null, string? sessionId = null, string? requestId = null,
        long? durationMs = null, string? errorKey = null,
        IReadOnlyDictionary<string, string>? catalogHashes = null) =>
        Task.Run(() => Write(eventName, flow, result, commandId, sessionId, requestId, durationMs, errorKey, catalogHashes));

    private void Write(string eventName, string? flow, string? result, string? commandId,
        string? sessionId, string? requestId, long? durationMs, string? errorKey,
        IReadOnlyDictionary<string, string>? catalogHashes)
    {
        var text = JsonSerializer.Serialize(new
        {
            timestamp = ProjectTime.Now(), @event = eventName,
            implementation = "csharp", instance, flow, result, command_id = commandId,
            session_id = sessionId, request_id = requestId, duration_ms = durationMs, error_key = errorKey,
            catalog_hashes = catalogHashes
        });
        var bytes = Encoding.UTF8.GetBytes(text + "\n");
        if (bytes.Length > 4096) throw new IOException("audit_size");
        try
        {
            lock (sync)
            {
                if (File.Exists(path) && new FileInfo(path).Length + bytes.Length > MaxBytes)
                {
                    for (var i = 4; i >= 1; i--)
                    {
                        var destination = path + "." + i;
                        var source = i == 1 ? path : path + "." + (i - 1);
                        if (File.Exists(source)) File.Move(source, destination, true);
                    }
                }
                using var output = new FileStream(path, FileMode.Append, FileAccess.Write, FileShare.Read);
                output.Write(bytes);
                output.Flush(true);
                Console.WriteLine(text);
            }
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            throw new AuditException(error);
        }
    }

    public void Dispose() { }
}
