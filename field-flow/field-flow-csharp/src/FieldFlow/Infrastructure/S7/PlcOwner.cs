// 一台 PLC 对应一个长期会话和有界队列，队列内仅执行一项实际 I/O。
using System.Threading.Channels;
using FieldFlow.Domain;

namespace FieldFlow.Infrastructure.S7;

internal sealed class PlcOwner : IAsyncDisposable
{
    private sealed class Job(Func<S7Session, CancellationToken, Task<object?>> run)
    {
        private int state;
        public Func<S7Session, CancellationToken, Task<object?>> Run { get; } = run;
        public TaskCompletionSource<object?> Completion { get; } =
            new(TaskCreationOptions.RunContinuationsAsynchronously);
        public bool TryClaim() => Interlocked.CompareExchange(ref state, 1, 0) == 0;
        public void CancelWaiting()
        {
            if (Interlocked.CompareExchange(ref state, 2, 0) == 0)
                Completion.TrySetException(new OperationCanceledException("queue_wait_timeout"));
        }
    }

    private readonly Plc plc;
    private readonly Channel<Job> queue;
    private readonly CancellationTokenSource stop = new();
    private readonly Task task;
    private TaskCompletionSource<bool> ready = NewReady();
    private S7Session? session;

    public PlcOwner(Plc plc)
    {
        this.plc = plc;
        queue = Channel.CreateBounded<Job>(new BoundedChannelOptions(plc.QueueCapacity)
        {
            SingleReader = true,
            FullMode = BoundedChannelFullMode.Wait
        });
        task = RunAsync();
    }

    public async Task<T> ExecuteAsync<T>(Func<S7Session, CancellationToken, Task<T>> action, CancellationToken cancellation)
    {
        using var readyDeadline = CancellationTokenSource.CreateLinkedTokenSource(cancellation, stop.Token);
        readyDeadline.CancelAfter(plc.ReadyWaitMs);
        await Volatile.Read(ref ready).Task.WaitAsync(readyDeadline.Token);
        var job = new Job(async (client, token) => await action(client, token));
        using var queueDeadline = CancellationTokenSource.CreateLinkedTokenSource(cancellation, stop.Token);
        queueDeadline.CancelAfter(plc.QueueWaitMs);
        using var registration = queueDeadline.Token.Register(job.CancelWaiting);
        await queue.Writer.WriteAsync(job, queueDeadline.Token);
        return (T)(await job.Completion.Task)!;
    }

    private async Task RunAsync()
    {
        var failures = 0;
        try
        {
            while (!stop.IsCancellationRequested)
            {
                if (session is null)
                {
                    try
                    {
                        session = await S7Session.ConnectAsync(plc, stop.Token);
                        failures = 0;
                        Volatile.Read(ref ready).TrySetResult(true);
                    }
                    catch (Exception error) when (error is IOException or System.Net.Sockets.SocketException or OperationCanceledException)
                    {
                        if (stop.IsCancellationRequested) break;
                        failures++;
                        var delay = failures >= 5 ? 10000 : Math.Min(2000, 250 * (1 << Math.Min(failures - 1, 3)));
                        if (failures >= 5) failures = 0;
                        await Task.Delay(delay, stop.Token);
                        continue;
                    }
                }
                var job = await queue.Reader.ReadAsync(stop.Token);
                if (!job.TryClaim()) continue;
                try
                {
                    stop.Token.ThrowIfCancellationRequested();
                    if (!session.CanCall)
                    {
                        await RetireAsync();
                        session = await S7Session.ConnectAsync(plc, stop.Token);
                        Volatile.Read(ref ready).TrySetResult(true);
                    }
                    job.Completion.TrySetResult(await job.Run(session, stop.Token));
                }
                catch (Exception error)
                {
                    job.Completion.TrySetException(error);
                    await RetireAsync();
                }
            }
        }
        catch (OperationCanceledException) when (stop.IsCancellationRequested) { }
        finally
        {
            queue.Writer.TryComplete();
            while (queue.Reader.TryRead(out var job))
                job.Completion.TrySetException(new OperationCanceledException("owner_stopped"));
            await RetireAsync();
        }
    }

    private async ValueTask RetireAsync()
    {
        if (session is null) return;
        var old = session;
        session = null;
        Interlocked.Exchange(ref ready, NewReady());
        await old.DisposeAsync();
    }

    private static TaskCompletionSource<bool> NewReady() =>
        new(TaskCreationOptions.RunContinuationsAsynchronously);

    public async ValueTask DisposeAsync()
    {
        stop.Cancel();
        queue.Writer.TryComplete();
        await task;
        stop.Dispose();
    }
}
