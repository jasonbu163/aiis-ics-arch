// 业务命令保留原始来源时效和已解析的物理目标。
namespace FieldFlow.Domain;

public sealed record Command(
    string SourceId, string CommandId, short Value, long IssuedAtMs, long ExpiresAtMs,
    string FlowId, string BusinessName, string DeviceId, string PointId, Plc Plc, Point Point,
    long DeadlineMs, int IntervalMs, int InputMaxAgeMs, string GetUrl);

public sealed class ClockGuard
{
    private readonly TimeProvider clock;
    private readonly long wall;
    private readonly long monotonic;
    private bool invalid;
    public bool IsInvalid => invalid;

    public ClockGuard(TimeProvider? clock = null)
    {
        this.clock = clock ?? TimeProvider.System;
        wall = this.clock.GetUtcNow().ToUnixTimeMilliseconds();
        monotonic = this.clock.GetTimestamp();
    }

    public bool Valid(Command command)
    {
        var elapsed = (long)clock.GetElapsedTime(monotonic, clock.GetTimestamp()).TotalMilliseconds;
        var now = clock.GetUtcNow().ToUnixTimeMilliseconds();
        if (Math.Abs(now - wall - elapsed) > 1000) invalid = true;
        return !invalid && now < command.DeadlineMs;
    }
}

public static class ProjectTime
{
    private static readonly TimeSpan Offset = TimeSpan.FromHours(8);
    public static string Now() => DateTimeOffset.UtcNow.ToOffset(Offset).ToString("O");
}
