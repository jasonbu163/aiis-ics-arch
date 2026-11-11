// 一条 TCP 会话以真实响应完成为边界，异常时关闭 socket。
using System.Buffers.Binary;
using System.Net.Sockets;
using FieldFlow.Domain;

namespace FieldFlow.Infrastructure.S7;

internal sealed class S7Session : IAsyncDisposable
{
    private readonly TcpClient client;
    private readonly NetworkStream stream;
    private ushort nextReference = 1;
    public string SessionId { get; } = Guid.NewGuid().ToString("N");
    public bool CanCall => nextReference < ushort.MaxValue;

    private S7Session(TcpClient client)
    {
        this.client = client;
        stream = client.GetStream();
    }

    public static async Task<S7Session> ConnectAsync(Plc plc, CancellationToken stop)
    {
        using var deadline = CancellationTokenSource.CreateLinkedTokenSource(stop);
        deadline.CancelAfter(plc.ConnectTimeoutMs);
        var tcp = new TcpClient(AddressFamily.InterNetwork) { NoDelay = true };
        try
        {
            await tcp.ConnectAsync(plc.Host, plc.Port, deadline.Token);
            var session = new S7Session(tcp);
            await session.stream.WriteAsync(S7Frames.Connect(plc), deadline.Token);
            S7Frames.ValidateConnect(await session.ReadFrameAsync(deadline.Token), plc);
            await session.stream.WriteAsync(S7Frames.Setup, deadline.Token);
            S7Frames.ValidateSetup(await session.ReadFrameAsync(deadline.Token));
            return session;
        }
        catch
        {
            tcp.Dispose();
            throw;
        }
    }

    public async Task<short> ReadAsync(Point point, int timeoutMs, CancellationToken stop)
    {
        return await CallAsync(point, null, timeoutMs, stop);
    }

    public async Task WriteAsync(Point point, short value, int timeoutMs, CancellationToken stop)
    {
        _ = await CallAsync(point, value, timeoutMs, stop);
    }

    private async Task<short> CallAsync(Point point, short? value, int timeoutMs, CancellationToken stop)
    {
        if (nextReference == ushort.MaxValue) throw new IOException("s7_reference_exhausted");
        var reference = nextReference++;
        using var deadline = CancellationTokenSource.CreateLinkedTokenSource(stop);
        deadline.CancelAfter(timeoutMs);
        try
        {
            await stream.WriteAsync(S7Frames.Request(point.Db, point.Offset, reference, value), deadline.Token);
            return S7Frames.ValidateResponse(await ReadFrameAsync(deadline.Token), reference, value.HasValue);
        }
        catch
        {
            client.Dispose();
            throw;
        }
    }

    private async Task<byte[]> ReadFrameAsync(CancellationToken cancellation)
    {
        var header = new byte[4];
        await stream.ReadExactlyAsync(header, cancellation);
        var size = BinaryPrimitives.ReadUInt16BigEndian(header.AsSpan(2));
        if (header[0] != 3 || header[1] != 0 || size is < 7 or > 512)
            throw new IOException("s7_frame_length");
        var frame = new byte[size];
        header.CopyTo(frame, 0);
        await stream.ReadExactlyAsync(frame.AsMemory(4), cancellation);
        return frame;
    }

    public ValueTask DisposeAsync()
    {
        stream.Dispose();
        client.Dispose();
        return ValueTask.CompletedTask;
    }
}
