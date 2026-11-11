// 一个业务轮次只读取命令并提交 typed 意图。
using FieldFlow.Domain;
using FieldFlow.Infrastructure.Http;
using FieldFlow.Services;

namespace FieldFlow.App;

internal static class Demo01
{
    public static async Task<string> OnceAsync(Flow flow, Plc plc, CommandFeed feed,
        ExecutionService execution, ClockGuard clock, CancellationToken stop)
    {
        var command = await feed.GetAsync(flow, plc, plc.Points[flow.PointId], stop);
        return command is null ? "idle" : await execution.ApplyAsync(command, clock, stop);
    }
}
