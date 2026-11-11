// 来源命令只接受完整字段、正确类型和未过期的原始时间。
using System.Text;
using System.Text.Json;
using FieldFlow.Domain;
using FieldFlow.Infrastructure.Http;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace FieldFlow.Tests;

[TestClass]
public sealed class InputTests
{
    [TestMethod]
    public void ClockJumpLatchesUntilNewRuntime()
    {
        var time = new ControlledTime();
        var guard = new ClockGuard(time);
        var point = new Point("value", 1, 16, 0, true);
        var plc = new Plc("s7", "127.0.0.1", 34102, 0, 1, 1000, 1000, 1, 500, 500,
            new Dictionary<string, Point> { [point.Id] = point });
        var now = time.GetUtcNow().ToUnixTimeMilliseconds();
        var command = new Command("feed", "one", 1, now, now + 30000, "flow", "business",
            plc.Id, point.Id, plc, point, now + 10000, 500, 10000, "http://127.0.0.1:34880/");
        Assert.IsTrue(guard.Valid(command));
        time.WallOffsetMs = 2000;
        Assert.IsFalse(guard.Valid(command));
        Assert.IsTrue(guard.IsInvalid);
        time.WallOffsetMs = 0;
        Assert.IsFalse(guard.Valid(command));
    }

    [TestMethod]
    public void StrictCommandAcceptsValidAndRejectsDuplicateOrExpired()
    {
        var point = new Point("value", 1, 16, 0, true);
        var plc = new Plc("s7_a", "127.0.0.1", 34102, 0, 1, 3000, 5000, 16, 2000, 3000,
            new Dictionary<string, Point> { [point.Id] = point });
        var flow = new Flow("demo01", "example", 500, "demo01-feed",
            new Uri("http://127.0.0.1:34880/demo01/command"), 10000, plc.Id, point.Id);
        var now = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
        var body = JsonSerializer.Serialize(new
        {
            schema_version = 1, source_id = "demo01-feed", ready = true, command_id = "one",
            value = 42, issued_at_ms = now, expires_at_ms = now + 30000
        });
        var parsed = CommandFeed.Parse(Encoding.UTF8.GetBytes(body), flow, plc, point);
        Assert.IsNotNull(parsed);
        Assert.AreEqual((short)42, parsed.Value);
        var duplicate = body.Insert(1, "\"value\":1,");
        Assert.ThrowsExactly<IOException>(() => CommandFeed.Parse(Encoding.UTF8.GetBytes(duplicate), flow, plc, point));
        var expired = body.Replace(now.ToString(), (now - 60000).ToString(), StringComparison.Ordinal)
            .Replace((now + 30000).ToString(), (now - 30000).ToString(), StringComparison.Ordinal);
        Assert.ThrowsExactly<IOException>(() => CommandFeed.Parse(Encoding.UTF8.GetBytes(expired), flow, plc, point));
    }

    private sealed class ControlledTime : TimeProvider
    {
        private readonly DateTimeOffset initial = DateTimeOffset.UtcNow;
        public int WallOffsetMs { get; set; }
        public override DateTimeOffset GetUtcNow() => initial.AddMilliseconds(WallOffsetMs);
        public override long GetTimestamp() => 0;
        public override long TimestampFrequency => 1000;
    }
}
