// 用独立 HTTP/S7 夹具验证一次业务轮次、重复命令与不确定恢复。
using System.Text.Json;
using FieldFlow.App;
using FieldFlow.Domain;
using FieldFlow.Infrastructure.Configuration;
using FieldFlow.Infrastructure.Http;
using FieldFlow.Infrastructure.Logging;
using FieldFlow.Infrastructure.S7;
using FieldFlow.Infrastructure.State;
using FieldFlow.Services;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace FieldFlow.Tests;

[TestClass]
[DoNotParallelize]
public sealed class LoopbackTests
{
    [TestMethod]
    [Timeout(15000)]
    public async Task ExecuteDeduplicatesAndReadbackRetainsAdjacentBytes()
    {
        var result = await ExerciseAsync("normal", true);
        Assert.AreEqual(10, result.Gets);
        Assert.AreEqual(1, result.Writes);
        Assert.AreEqual(1, result.Reads);
        Assert.AreEqual(1, result.Sessions);
        Assert.AreEqual("002AA5A5", result.Prefix);
        Assert.AreEqual(1, result.Confirmed);
    }

    [TestMethod]
    [Timeout(15000)]
    public async Task DefaultDryRunReadsWithoutWriting()
    {
        var result = await ExerciseAsync("normal", false);
        Assert.AreEqual(0, result.Writes);
        Assert.AreEqual(1, result.Reads);
        Assert.AreEqual(1, result.Simulated);
    }

    [TestMethod]
    [Timeout(15000)]
    public async Task AppliedWriteWithoutAckStaysUnknownAcrossRestart()
    {
        var result = await ExerciseAsync("drop_ack", true);
        Assert.AreEqual(1, result.Writes);
        Assert.AreEqual(1, result.Unknown);
        Assert.AreEqual(0, result.Confirmed);
    }

    [TestMethod]
    [Timeout(15000)]
    public async Task MismatchedAckCannotConfirm()
    {
        var result = await ExerciseAsync("bad_ref", true);
        Assert.AreEqual(1, result.Writes);
        Assert.AreEqual(1, result.Unknown);
        Assert.AreEqual(0, result.Confirmed);
    }

    [TestMethod]
    [Timeout(15000)]
    public async Task ShortAckCannotConfirm()
    {
        var result = await ExerciseAsync("short_ack", true);
        Assert.AreEqual(1, result.Writes);
        Assert.AreEqual(1, result.Unknown);
        Assert.AreEqual(0, result.Confirmed);
    }

    [TestMethod]
    [Timeout(15000)]
    public async Task SlowHttpDoesNotBlockAnotherFlow()
    {
        var root = Directory.CreateTempSubdirectory("ff003-flow-");
        var report = Path.Combine(root.FullName, "fixture.json");
        var statePath = Path.Combine(root.FullName, "state");
        using var stop = new CancellationTokenSource();
        var fixture = FixtureHost.RunAsync(["--report=" + report], stop.Token);
        StateStore? state = null;
        PlcOwner? owner = null;
        CommandFeed? feed = null;
        AuditLog? audit = null;
        try
        {
            var config = ConfigLoader.Load(Path.Combine(AppContext.BaseDirectory, "config", "demo01.yaml"));
            var original = config.Flows[0];
            var plc = config.Plcs[original.DeviceId];
            var slow = original with { Id = "slow", GetUrl = new Uri("http://127.0.0.1:34880/slow") };
            var fast = original with { Id = "fast", PointId = "ready", GetUrl = new Uri("http://127.0.0.1:34880/fast") };
            StateStore.Initialize(statePath, "execute", config.InstanceId);
            state = StateStore.Open(statePath, "execute", config.InstanceId);
            owner = new PlcOwner(plc);
            feed = new CommandFeed(config.Http);
            audit = new AuditLog(statePath, config.InstanceId);
            var gate = new SendGate();
            var execution = new ExecutionService(state, owner, gate, audit, true);
            var slowTask = Demo01.OnceAsync(slow, plc, feed, execution, new ClockGuard(), CancellationToken.None);
            await Task.Delay(100);
            var fastResult = await Demo01.OnceAsync(fast, plc, feed, execution, new ClockGuard(), CancellationToken.None);
            Assert.AreEqual("confirmed", fastResult);
            using (var snapshot = JsonDocument.Parse(File.ReadAllText(report)))
            {
                Assert.AreEqual(1, snapshot.RootElement.GetProperty("writes").GetInt32());
                Assert.AreEqual(1, snapshot.RootElement.GetProperty("slow_in_flight").GetInt32());
            }
            Assert.AreEqual("confirmed", await slowTask);
        }
        finally
        {
            if (owner is not null) await owner.DisposeAsync();
            state?.Dispose();
            feed?.Dispose();
            audit?.Dispose();
            stop.Cancel();
            try { await fixture; }
            catch (OperationCanceledException) { }
            root.Delete(true);
        }
    }

    [TestMethod]
    [Timeout(15000)]
    public async Task StopBeforeReadyRecordsCanceledWithoutWrite()
    {
        var root = Directory.CreateTempSubdirectory("ff003-stop-");
        var report = Path.Combine(root.FullName, "fixture.json");
        var statePath = Path.Combine(root.FullName, "state");
        using var fixtureStop = new CancellationTokenSource();
        using var flowStop = new CancellationTokenSource();
        var fixture = FixtureHost.RunAsync(["--report=" + report, "--connect-delay-ms=4000"], fixtureStop.Token);
        StateStore? state = null;
        PlcOwner? owner = null;
        CommandFeed? feed = null;
        AuditLog? audit = null;
        try
        {
            var config = ConfigLoader.Load(Path.Combine(AppContext.BaseDirectory, "config", "demo01.yaml"));
            var flow = config.Flows[0];
            var plc = config.Plcs[flow.DeviceId];
            StateStore.Initialize(statePath, "execute", config.InstanceId);
            state = StateStore.Open(statePath, "execute", config.InstanceId);
            owner = new PlcOwner(plc);
            feed = new CommandFeed(config.Http);
            audit = new AuditLog(statePath, config.InstanceId);
            var gate = new SendGate();
            var execution = new ExecutionService(state, owner, gate, audit, true);
            var once = Demo01.OnceAsync(flow, plc, feed, execution, new ClockGuard(), flowStop.Token);
            var limit = System.Diagnostics.Stopwatch.StartNew();
            while (CountState(statePath, "pending") == 0 && limit.Elapsed < TimeSpan.FromSeconds(3))
                await Task.Delay(20);
            Assert.AreEqual(1, CountState(statePath, "pending"));
            gate.Close();
            flowStop.Cancel();
            Assert.AreEqual("canceled", await once);
            Assert.AreEqual(1, CountState(statePath, "canceled"));
            using var snapshot = JsonDocument.Parse(File.ReadAllText(report));
            Assert.AreEqual(0, snapshot.RootElement.GetProperty("writes").GetInt32());
        }
        finally
        {
            if (owner is not null) await owner.DisposeAsync();
            state?.Dispose();
            feed?.Dispose();
            audit?.Dispose();
            fixtureStop.Cancel();
            try { await fixture; }
            catch (OperationCanceledException) { }
            root.Delete(true);
        }
    }

    private static async Task<Result> ExerciseAsync(string mode, bool execute)
    {
        var root = Directory.CreateTempSubdirectory("ff003-loop-");
        var report = Path.Combine(root.FullName, "fixture.json");
        var statePath = Path.Combine(root.FullName, "state");
        using var stop = new CancellationTokenSource();
        Task? fixture = null;
        StateStore? state = null;
        PlcOwner? owner = null;
        CommandFeed? feed = null;
        AuditLog? audit = null;
        try
        {
            fixture = FixtureHost.RunAsync(["--report=" + report, "--mode=" + mode], stop.Token);
            var config = ConfigLoader.Load(Path.Combine(AppContext.BaseDirectory, "config", "demo01.yaml"));
            var flow = config.Flows[0];
            var plc = config.Plcs[flow.DeviceId];
            StateStore.Initialize(statePath, execute ? "execute" : "dry_run", config.InstanceId);
            state = StateStore.Open(statePath, execute ? "execute" : "dry_run", config.InstanceId);
            owner = new PlcOwner(plc);
            feed = new CommandFeed(config.Http);
            audit = new AuditLog(statePath, config.InstanceId);
            var gate = new SendGate();
            var execution = new ExecutionService(state, owner, gate, audit, execute);
            var clock = new ClockGuard();
            if (mode == "normal")
            {
                for (var i = 0; i < 10; i++)
                    _ = await Demo01.OnceAsync(flow, plc, feed, execution, clock, CancellationToken.None);
                if (execute)
                {
                    var read = await owner.ExecuteAsync((client, token) =>
                        client.ReadAsync(plc.Points[flow.PointId], plc.IoTimeoutMs, token), CancellationToken.None);
                    Assert.AreEqual((short)42, read);
                }
            }
            else
            {
                try
                {
                    _ = await Demo01.OnceAsync(flow, plc, feed, execution, clock, CancellationToken.None);
                    Assert.Fail("The unconfirmed write must not return success.");
                }
                catch (IOException) { }
                await owner.DisposeAsync();
                owner = null;
                state.Dispose();
                state = StateStore.Open(statePath, "execute", config.InstanceId);
                owner = new PlcOwner(plc);
                execution = new ExecutionService(state, owner, gate, audit, true);
                Assert.AreEqual("existing_unknown",
                    await Demo01.OnceAsync(flow, plc, feed, execution, clock, CancellationToken.None));
            }
            await owner.DisposeAsync();
            owner = null;
            state.Dispose();
            state = null;
            using var stateJson = JsonDocument.Parse(JsonSerializer.Serialize(StateStore.Inspect(statePath)));
            using var fixtureJson = JsonDocument.Parse(File.ReadAllText(report));
            var counts = stateJson.RootElement.GetProperty("counts");
            var data = fixtureJson.RootElement;
            return new Result(data.GetProperty("gets").GetInt32(), data.GetProperty("reads").GetInt32(),
                data.GetProperty("writes").GetInt32(), data.GetProperty("sessions").GetInt32(),
                data.GetProperty("db1").GetString()![..8],
                Count(counts, "confirmed"), Count(counts, "simulated"), Count(counts, "unknown"));
        }
        finally
        {
            if (owner is not null) await owner.DisposeAsync();
            state?.Dispose();
            feed?.Dispose();
            audit?.Dispose();
            stop.Cancel();
            if (fixture is not null)
            {
                try { await fixture; }
                catch (OperationCanceledException) { }
            }
            root.Delete(true);
        }
    }

    private static int Count(JsonElement counts, string name) =>
        counts.TryGetProperty(name, out var value) ? value.GetInt32() : 0;

    private static int CountState(string path, string name)
    {
        using var state = JsonDocument.Parse(JsonSerializer.Serialize(StateStore.Inspect(path)));
        return Count(state.RootElement.GetProperty("counts"), name);
    }

    private sealed record Result(int Gets, int Reads, int Writes, int Sessions, string Prefix,
        int Confirmed, int Simulated, int Unknown);
}
