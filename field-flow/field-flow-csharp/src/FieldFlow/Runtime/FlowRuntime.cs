// 独立调度各流，并按同一停止期限监督全部自有资源。
using System.Diagnostics;
using FieldFlow.App;
using FieldFlow.Domain;
using FieldFlow.Infrastructure.Http;
using FieldFlow.Infrastructure.Logging;
using FieldFlow.Infrastructure.S7;
using FieldFlow.Infrastructure.State;
using FieldFlow.Services;

namespace FieldFlow.Runtime;

internal static class FlowRuntime
{
    public static async Task<int> RunAsync(RuntimeConfig config, string directory, bool execute)
    {
        using var stop = new CancellationTokenSource();
        var gate = new SendGate();
        var faults = new RuntimeFaults();
        var stopping = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        var stopLock = new object();
        long stoppedAt = 0;
        void RequestStop()
        {
            lock (stopLock)
            {
                if (stoppedAt != 0) return;
                stoppedAt = Stopwatch.GetTimestamp();
                gate.Close();
                stop.Cancel();
                stopping.TrySetResult(true);
            }
        }
        TimeSpan Remaining()
        {
            lock (stopLock)
            {
                var elapsed = stoppedAt == 0 ? 0 : Stopwatch.GetElapsedTime(stoppedAt).TotalMilliseconds;
                return TimeSpan.FromMilliseconds(Math.Max(0, config.ShutdownTimeoutMs - elapsed));
            }
        }

        StateStore? state = null;
        AuditLog? audit = null;
        CommandFeed? feed = null;
        var owners = new Dictionary<string, PlcOwner>(StringComparer.Ordinal);
        Task startup = Task.CompletedTask;
        Task flows = Task.CompletedTask;
        var exit = 0;
        ConsoleCancelEventHandler handler = (_, e) => { e.Cancel = true; RequestStop(); };
        Console.CancelKeyPress += handler;
        try
        {
            state = StateStore.Open(directory, execute ? "execute" : "dry_run", config.InstanceId);
            audit = new AuditLog(directory, config.InstanceId);
            feed = new CommandFeed(config.Http);
            startup = audit.WriteAsync("runtime_started", catalogHashes: config.CatalogHashes);
            await startup.WaitAsync(stop.Token);
            foreach (var plc in config.Plcs.Values) owners.Add(plc.Id, new PlcOwner(plc));
            flows = Task.WhenAll(config.Flows.Select(async flow =>
            {
                try
                {
                    await RunFlowAsync(flow, config.Plcs[flow.DeviceId], owners[flow.DeviceId],
                        state, feed, audit, gate, faults, execute, stop.Token);
                }
                catch
                {
                    RequestStop();
                    throw;
                }
            }));
            await Task.WhenAny(flows, stopping.Task);
            if (flows.IsCompleted)
            {
                try { await flows; }
                catch (OperationCanceledException) when (stop.IsCancellationRequested) { }
                catch { exit = 1; }
            }
        }
        catch (OperationCanceledException) when (stop.IsCancellationRequested) { }
        catch
        {
            exit = 1;
            throw;
        }
        finally
        {
            RequestStop();
            var ownerTasks = owners.Values.Select(async owner => await owner.DisposeAsync());
            var joined = Task.WhenAll(ownerTasks.Append(startup).Append(flows));
            var allJoined = true;
            try { await joined.WaitAsync(Remaining()); }
            catch (TimeoutException)
            {
                Console.Error.WriteLine("{\"error_key\":\"shutdown_incomplete\",\"resource\":\"tasks_or_owners\"}");
                allJoined = false;
                exit = 1;
            }
            catch (OperationCanceledException) when (stop.IsCancellationRequested) { }
            catch
            {
                if (!joined.IsCompleted) allJoined = false;
                exit = 1;
            }
            if (allJoined)
            {
                feed?.Dispose();
                if (state is not null && !state.TryClose(Remaining()))
                {
                    Console.Error.WriteLine("{\"error_key\":\"shutdown_incomplete\",\"resource\":\"state_writer\"}");
                    exit = 1;
                }
                else if (audit is not null)
                {
                    try { await audit.WriteAsync("resources_released").WaitAsync(Remaining()); }
                    catch { exit = 1; }
                    audit.Dispose();
                }
            }
            Console.CancelKeyPress -= handler;
        }
        if (faults.HasFault) exit = 1;
        return exit;
    }

    private static async Task RunFlowAsync(Flow flow, Plc plc, PlcOwner owner, StateStore state,
        CommandFeed feed, AuditLog audit, SendGate gate, RuntimeFaults faults, bool execute, CancellationToken stop)
    {
        var clock = new ClockGuard();
        var execution = new ExecutionService(state, owner, gate, audit, execute);
        while (!stop.IsCancellationRequested)
        {
            var iteration = Stopwatch.StartNew();
            try
            {
                var result = await Demo01.OnceAsync(flow, plc, feed, execution, clock, stop);
                if (result == "clock_invalid") faults.Mark();
                if (result is not ("idle" or "pending") && !result.StartsWith("existing_", StringComparison.Ordinal))
                    await audit.WriteAsync("flow_iteration", flow.Id, result, durationMs: iteration.ElapsedMilliseconds,
                        errorKey: result == "clock_invalid" ? result : null);
            }
            catch (FlowBlockedException error)
            {
                faults.Mark();
                await audit.WriteAsync("flow_blocked", flow.Id, "blocked",
                    durationMs: iteration.ElapsedMilliseconds, errorKey: error.Message);
                await Task.Delay(Timeout.InfiniteTimeSpan, stop);
                return;
            }
            catch (AuditException)
            {
                gate.Close();
                throw;
            }
            catch (OperationCanceledException) when (stop.IsCancellationRequested) { return; }
            catch (Exception error) when (error is IOException or HttpRequestException or
                System.Net.Sockets.SocketException or OperationCanceledException)
            {
                faults.Mark();
                var key = error switch
                {
                    OperationCanceledException => "operation_timeout",
                    HttpRequestException => "http_error",
                    System.Net.Sockets.SocketException => "socket_error",
                    _ => "io_error"
                };
                await audit.WriteAsync("flow_error", flow.Id, "recovering",
                    durationMs: iteration.ElapsedMilliseconds, errorKey: key);
            }
            await Task.Delay(flow.IntervalMs, stop);
        }
    }

    private sealed class RuntimeFaults
    {
        private int value;
        public bool HasFault => Volatile.Read(ref value) != 0;
        public void Mark() => Interlocked.Exchange(ref value, 1);
    }
}
