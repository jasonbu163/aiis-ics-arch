// 本地测试夹具：独立解析最小 S7 帧并提供固定 HTTP 命令。
using System.Buffers.Binary;
using System.Collections.Concurrent;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Text.Json;

await FixtureHost.RunAsync(args, CancellationToken.None, true);

public static class FixtureHost
{
    public static async Task RunAsync(string[] args, CancellationToken external, bool handleConsole = false)
    {
        var options = args.Select(arg => arg.Split('=', 2)).ToDictionary(
            item => item[0], item => item.Length == 2 ? item[1] : "", StringComparer.Ordinal);
        var mode = options.GetValueOrDefault("--mode", "normal");
        var reportPath = options.GetValueOrDefault("--report", "");
        var readDelayMs = int.Parse(options.GetValueOrDefault("--read-delay-ms", "0"));
        var connectDelayMs = int.Parse(options.GetValueOrDefault("--connect-delay-ms", "0"));
        if (mode is not ("normal" or "drop_ack" or "bad_ref" or "short_ack") ||
            readDelayMs is < 0 or > 5000 || connectDelayMs is < 0 or > 5000 || string.IsNullOrEmpty(reportPath))
            throw new ArgumentException("fixture_arguments");

        using var stop = CancellationTokenSource.CreateLinkedTokenSource(external);
        ConsoleCancelEventHandler? handler = null;
        if (handleConsole)
        {
            handler = (_, e) => { e.Cancel = true; stop.Cancel(); };
            Console.CancelKeyPress += handler;
        }
        var s7 = new TcpListener(IPAddress.Loopback, 34102);
        var http = new TcpListener(IPAddress.Loopback, 34880);
        try { s7.Start(); http.Start(); }
        catch
        {
            s7.Stop();
            http.Stop();
            if (handler is not null) Console.CancelKeyPress -= handler;
            throw;
        }
        var shared = new FixtureState(reportPath, mode, readDelayMs);
        var clients = new ConcurrentBag<Task>();
        try
        {
            shared.Report();
            Console.WriteLine("{\"ready\":true}");
            var servers = new[] { AcceptS7(), AcceptHttp() };
            await Task.WhenAll(servers);
        }
        catch (OperationCanceledException) when (stop.IsCancellationRequested) { }
        finally
        {
            s7.Stop();
            http.Stop();
            await Task.WhenAll(clients.ToArray());
            shared.Report();
            if (handler is not null) Console.CancelKeyPress -= handler;
        }

        async Task AcceptS7()
        {
            while (!stop.IsCancellationRequested)
            {
                var client = await s7.AcceptTcpClientAsync(stop.Token);
                clients.Add(HandleS7(client));
            }
        }

        async Task HandleS7(TcpClient client)
        {
            using (client)
            {
                try
                {
                    shared.Connected();
                    var stream = client.GetStream();
                    var connect = await ReadFrame(stream, stop.Token);
                    if (connect.Length != 22 || connect[5] != 0xe0) throw new IOException("connect");
                    if (connectDelayMs > 0) await Task.Delay(connectDelayMs, stop.Token);
                    var confirmation = Convert.FromHexString("0300001611D00001000100C0010AC1020100C2020101");
                    await stream.WriteAsync(confirmation, stop.Token);
                    var setup = await ReadFrame(stream, stop.Token);
                    if (setup.Length != 25 || setup[17] != 0xf0) throw new IOException("setup");
                    await stream.WriteAsync(Convert.FromHexString("0300001B02F080320300000000000800000000F0000001000100F0"), stop.Token);
                    while (!stop.IsCancellationRequested)
                    {
                        var frame = await ReadFrame(stream, stop.Token);
                        var write = frame.Length == 37 && frame[17] == 5;
                        if (!write && (frame.Length != 31 || frame[17] != 4)) throw new IOException("request");
                        if (frame[18] != 1 || frame[27] != 0x84 || frame[23] != 0 || frame[24] != 2)
                            throw new IOException("request_item");
                        var reference = BinaryPrimitives.ReadUInt16BigEndian(frame.AsSpan(11));
                        var db = BinaryPrimitives.ReadUInt16BigEndian(frame.AsSpan(25));
                        var bits = (frame[28] << 16) | (frame[29] << 8) | frame[30];
                        if (bits % 8 != 0) throw new IOException("offset");
                        var offset = bits / 8;
                        if (write)
                        {
                            var value = BinaryPrimitives.ReadInt16BigEndian(frame.AsSpan(35));
                            shared.Write(db, offset, value);
                            if (mode == "drop_ack") return;
                            var ack = Convert.FromHexString("0300001602F0803203000000000002000100000501FF");
                            BinaryPrimitives.WriteUInt16BigEndian(ack.AsSpan(11), mode == "bad_ref" ? (ushort)(reference + 1) : reference);
                            await stream.WriteAsync(mode == "short_ack" ? ack.AsMemory(0, 17) : ack, stop.Token);
                            if (mode == "short_ack") return;
                        }
                        else
                        {
                            var value = shared.Read(db, offset);
                            if (readDelayMs > 0) await Task.Delay(readDelayMs, stop.Token);
                            var ack = Convert.FromHexString("0300001B02F0803203000000000002000600000401FF0400100000");
                            BinaryPrimitives.WriteUInt16BigEndian(ack.AsSpan(11), reference);
                            BinaryPrimitives.WriteInt16BigEndian(ack.AsSpan(25), value);
                            await stream.WriteAsync(ack, stop.Token);
                        }
                    }
                }
                catch (Exception error) when (error is IOException or SocketException or OperationCanceledException or ObjectDisposedException) { }
            }
        }

        async Task AcceptHttp()
        {
            while (!stop.IsCancellationRequested)
            {
                var client = await http.AcceptTcpClientAsync(stop.Token);
                clients.Add(HandleHttp(client));
            }
        }

        async Task HandleHttp(TcpClient client)
        {
            using (client)
            {
                try
                {
                    var stream = client.GetStream();
                    var request = new MemoryStream();
                    var buffer = new byte[1024];
                    while (request.Length < 4096)
                    {
                        var count = await stream.ReadAsync(buffer, stop.Token);
                        if (count == 0) return;
                        request.Write(buffer, 0, count);
                        if (Encoding.ASCII.GetString(request.ToArray()).Contains("\r\n\r\n")) break;
                    }
                    var first = Encoding.ASCII.GetString(request.ToArray()).Split("\r\n")[0];
                    var route = first.Split(' ').ElementAtOrDefault(1) ?? "";
                    if (route.Contains("slow", StringComparison.Ordinal))
                    {
                        shared.SlowStarted();
                        try { await Task.Delay(1200, stop.Token); }
                        finally { shared.SlowEnded(); }
                    }
                    var body = shared.Get(route.Contains("fast", StringComparison.Ordinal) ? "fixture-fast" : "fixture-command");
                    var bytes = Encoding.UTF8.GetBytes(body);
                    var headers = Encoding.ASCII.GetBytes("HTTP/1.1 200 OK\r\nContent-Type: application/json; charset=utf-8\r\nContent-Length: " + bytes.Length + "\r\nConnection: close\r\n\r\n");
                    await stream.WriteAsync(headers, stop.Token);
                    await stream.WriteAsync(bytes, stop.Token);
                }
                catch (Exception error) when (error is IOException or SocketException or OperationCanceledException or ObjectDisposedException) { }
            }
        }

        static async Task<byte[]> ReadFrame(NetworkStream stream, CancellationToken stop)
        {
            var header = new byte[4];
            await stream.ReadExactlyAsync(header, stop);
            var length = BinaryPrimitives.ReadUInt16BigEndian(header.AsSpan(2));
            if (header[0] != 3 || header[1] != 0 || length is < 7 or > 512) throw new IOException("frame_length");
            var frame = new byte[length];
            header.CopyTo(frame, 0);
            await stream.ReadExactlyAsync(frame.AsMemory(4), stop);
            return frame;
        }
    }
}

internal sealed class FixtureState(string reportPath, string mode, int readDelayMs)
{
    private readonly object sync = new();
    private readonly byte[] db1 = Enumerable.Repeat((byte)0xa5, 16).ToArray();
    private readonly byte[] db2 = Enumerable.Repeat((byte)0xa5, 16).ToArray();
    private readonly long issued = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
    private int gets;
    private int reads;
    private int writes;
    private int sessions;
    private int slowInFlight;

    public void Connected() { lock (sync) { sessions++; ReportLocked(); } }
    public void SlowStarted() { lock (sync) { slowInFlight++; ReportLocked(); } }
    public void SlowEnded() { lock (sync) { slowInFlight--; ReportLocked(); } }

    public short Read(int db, int offset)
    {
        lock (sync)
        {
            var bytes = Block(db, offset);
            reads++;
            var value = BinaryPrimitives.ReadInt16BigEndian(bytes.AsSpan(offset, 2));
            ReportLocked();
            return value;
        }
    }

    public void Write(int db, int offset, short value)
    {
        lock (sync)
        {
            var bytes = Block(db, offset);
            BinaryPrimitives.WriteInt16BigEndian(bytes.AsSpan(offset, 2), value);
            writes++;
            ReportLocked();
        }
    }

    public string Get(string id)
    {
        lock (sync)
        {
            gets++;
            ReportLocked();
            return JsonSerializer.Serialize(new
            {
                schema_version = 1, source_id = "demo01-feed", ready = true,
                command_id = id, value = 42, issued_at_ms = issued, expires_at_ms = issued + 30000
            });
        }
    }

    public void Report() { lock (sync) ReportLocked(); }

    private byte[] Block(int db, int offset)
    {
        if (offset < 0 || offset + 2 > 16) throw new IOException("block_range");
        return db switch { 1 => db1, 2 => db2, _ => throw new IOException("block") };
    }

    private void ReportLocked()
    {
        File.WriteAllText(reportPath, JsonSerializer.Serialize(new
        {
            mode, readDelayMs, gets, reads, writes, sessions, slow_in_flight = slowInFlight,
            db1 = Convert.ToHexString(db1), db2 = Convert.ToHexString(db2)
        }));
    }
}
