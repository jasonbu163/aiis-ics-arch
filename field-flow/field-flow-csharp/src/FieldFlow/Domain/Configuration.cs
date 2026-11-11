// 配置对象由启动前校验生成，运行期间不重新读取点表。
namespace FieldFlow.Domain;

public sealed record Point(string Id, int Db, int Size, int Offset, bool Enabled);
public sealed record Plc(
    string Id, string Host, int Port, int Rack, int Slot,
    int ConnectTimeoutMs, int IoTimeoutMs, int QueueCapacity, int QueueWaitMs,
    int ReadyWaitMs, IReadOnlyDictionary<string, Point> Points);
public sealed record Flow(
    string Id, string BusinessName, int IntervalMs, string SourceId,
    Uri GetUrl, int InputMaxAgeMs, string DeviceId, string PointId);
public sealed record HttpOptions(
    int ConnectTimeoutMs, int TotalTimeoutMs, int PoolWaitMs,
    int MaxConnections, int MaxBodyBytes);
public sealed record RuntimeConfig(
    string InstanceId, IReadOnlyDictionary<string, Plc> Plcs,
    IReadOnlyList<Flow> Flows, HttpOptions Http, int ShutdownTimeoutMs,
    IReadOnlyDictionary<string, string> CatalogHashes);

public sealed class ConfigException(string key) : Exception(key)
{
    public string Key { get; } = key;
}
