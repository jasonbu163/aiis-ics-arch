// 已入队但尚未领取的请求超时后不会成为一次 S7 I/O。
using System.Diagnostics;
using System.Text.Json;
using FieldFlow.Domain;
using FieldFlow.Infrastructure.S7;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace FieldFlow.Tests;

[TestClass]
[DoNotParallelize]
public sealed class QueueTests
{
    [TestMethod]
    [Timeout(12000)]
    public async Task QueueDeadlineCoversWaitingBehindInFlightRead()
    {
        var root = Directory.CreateTempSubdirectory("ff003-queue-");
        using var stop = new CancellationTokenSource();
        var report = Path.Combine(root.FullName, "report.json");
        Task? fixture = null;
        PlcOwner? owner = null;
        try
        {
            fixture = FixtureHost.RunAsync(["--report=" + report, "--read-delay-ms=1200"], stop.Token);
            var point = new Point("value", 1, 16, 0, true);
            var plc = new Plc("s7_a", "127.0.0.1", 34102, 0, 1, 3000, 5000, 16, 200, 3000,
                new Dictionary<string, Point> { [point.Id] = point });
            owner = new PlcOwner(plc);
            var first = owner.ExecuteAsync((session, token) => session.ReadAsync(point, 5000, token), CancellationToken.None);
            var limit = Stopwatch.StartNew();
            while (ReadCount(report) < 1 && limit.Elapsed < TimeSpan.FromSeconds(4))
                await Task.Delay(20);
            Assert.AreEqual(1, ReadCount(report));
            var waiting = Stopwatch.StartNew();
            var second = owner.ExecuteAsync((session, token) => session.ReadAsync(point, 5000, token), CancellationToken.None);
            await Assert.ThrowsExactlyAsync<OperationCanceledException>(async () => await second);
            Assert.IsLessThan(1000, waiting.ElapsedMilliseconds);
            _ = await first;
            await Task.Delay(100);
            Assert.AreEqual(1, ReadCount(report));
        }
        finally
        {
            if (owner is not null) await owner.DisposeAsync();
            stop.Cancel();
            if (fixture is not null)
            {
                try { await fixture; }
                catch (OperationCanceledException) { }
            }
            root.Delete(true);
        }
    }

    private static int ReadCount(string path)
    {
        try
        {
            using var document = JsonDocument.Parse(File.ReadAllText(path));
            return document.RootElement.GetProperty("reads").GetInt32();
        }
        catch (Exception error) when (error is IOException or JsonException or KeyNotFoundException)
        {
            return 0;
        }
    }
}
