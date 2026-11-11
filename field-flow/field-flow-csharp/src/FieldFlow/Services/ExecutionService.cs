// 持久意图、一次性派发凭证和不确定结果位于业务流之外。
using System.Diagnostics;
using FieldFlow.Domain;
using FieldFlow.Infrastructure.Logging;
using FieldFlow.Infrastructure.S7;
using FieldFlow.Infrastructure.State;

namespace FieldFlow.Services;

internal sealed class FlowBlockedException(string reason) : Exception(reason);

internal sealed class ExecutionService(StateStore state, PlcOwner owner, SendGate gate, AuditLog audit, bool execute)
{
    public async Task<string> ApplyAsync(Command command, ClockGuard clock, CancellationToken stop)
    {
        if (!clock.Valid(command) || gate.IsClosed) return clock.IsInvalid ? "clock_invalid" : "expired";
        string status;
        try { status = await state.AdmitAsync(command); }
        catch { gate.Close(); throw; }
        if (status is "identity_conflict" or "unknown_blocked") throw new FlowBlockedException(status);
        if (status != "pending") return "existing_" + status;

        using var deadline = CancellationTokenSource.CreateLinkedTokenSource(stop);
        var remaining = command.DeadlineMs - DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
        if (remaining <= 0) deadline.Cancel();
        else deadline.CancelAfter(TimeSpan.FromMilliseconds(remaining));
        try
        {
            return await owner.ExecuteAsync(async (session, ownerStop) =>
            {
                if (!clock.Valid(command) || gate.IsClosed || ownerStop.IsCancellationRequested)
                {
                    await SafeTransition(command, "pending", "expired", "before_dispatch");
                    return "expired";
                }
                var requestId = Guid.NewGuid().ToString("N");
                var watch = Stopwatch.StartNew();
                try
                {
                    await audit.WriteAsync("plc_dispatch", command.FlowId, "preparing",
                        command.CommandId, session.SessionId, requestId);
                }
                catch { gate.Close(); throw; }
                if (!clock.Valid(command) || gate.IsClosed || ownerStop.IsCancellationRequested)
                {
                    await SafeTransition(command, "pending", "canceled", "before_dispatch");
                    return "canceled";
                }
                if (!execute)
                {
                    _ = await session.ReadAsync(command.Point, command.Plc.IoTimeoutMs, ownerStop);
                    await SafeTransition(command, "pending", "simulated", "dry_run");
                    await SafeAudit("plc_read", command, session.SessionId, requestId, watch.ElapsedMilliseconds, "simulated");
                    return "simulated";
                }
                bool dispatched;
                try { dispatched = await state.DispatchAsync(command); }
                catch { gate.Close(); throw; }
                if (!dispatched) throw new FlowBlockedException("unknown_blocked");
                if (!clock.Valid(command) || gate.IsClosed || ownerStop.IsCancellationRequested)
                {
                    await SafeTransition(command, "in_flight", "canceled", "before_send");
                    return "canceled";
                }
                Task write;
                try
                {
                    write = gate.Start(() =>
                    {
                        if (!clock.Valid(command) || ownerStop.IsCancellationRequested)
                            throw new OperationCanceledException("before_send_expired");
                        return session.WriteAsync(command.Point, command.Value, command.Plc.IoTimeoutMs, ownerStop);
                    });
                }
                catch (OperationCanceledException)
                {
                    await SafeTransition(command, "in_flight", "canceled", "stop_before_send");
                    return "canceled";
                }
                try { await write; }
                catch
                {
                    await SafeTransition(command, "in_flight", "unknown", "write_result_unknown");
                    await SafeAudit("plc_write", command, session.SessionId, requestId,
                        watch.ElapsedMilliseconds, "unknown", "s7_write_unknown");
                    throw;
                }
                await SafeTransition(command, "in_flight", "confirmed", "s7_ack");
                await SafeAudit("plc_write", command, session.SessionId, requestId, watch.ElapsedMilliseconds, "confirmed");
                return "confirmed";
            }, deadline.Token);
        }
        catch (OperationCanceledException) when (stop.IsCancellationRequested || gate.IsClosed || !clock.Valid(command))
        {
            var outcome = stop.IsCancellationRequested || gate.IsClosed ? "canceled" : "expired";
            bool canceled;
            try { canceled = await state.CancelPendingAsync(command, outcome, "not_started"); }
            catch { gate.Close(); throw; }
            if (canceled) return outcome;
            throw;
        }
    }

    private async Task SafeTransition(Command command, string from, string to, string reason)
    {
        try { await state.TransitionAsync(command, from, to, reason); }
        catch { gate.Close(); throw; }
    }

    private async Task SafeAudit(string kind, Command command, string session, string request,
        long durationMs, string result, string? error = null)
    {
        try { await audit.WriteAsync(kind, command.FlowId, result, command.CommandId, session, request, durationMs, error); }
        catch { gate.Close(); throw; }
    }
}
