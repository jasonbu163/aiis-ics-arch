// 真实 MySQL 测试仅消费显式 run-root，并核对任务标签/loopback/固定库与版本。
using System.Diagnostics;
using System.Text.Json;
using MySql.Data.MySqlClient;
using Microsoft.VisualStudio.TestTools.UnitTesting;
namespace AIIS.Backend.Tests.Fixtures;

public sealed class MySqlFixture
{
    public string Root { get; }
    public string RunId { get; }
    public string AppConnection { get; }
    public string AdminConnection { get; }
    public MySqlFixture()
    {
        Root = Environment.GetEnvironmentVariable("BE008_RUN_ROOT") ?? throw new InvalidOperationException("explicit_run_root_required");
        if (Path.GetDirectoryName(Root) != "/private/tmp" || !Path.GetFileName(Root).StartsWith("arch-be008-run-", StringComparison.Ordinal) || Directory.ResolveLinkTarget(Root, false) is not null) throw new InvalidOperationException("unsafe_run_root");
        using var manifest = JsonDocument.Parse(File.ReadAllText(Path.Combine(Root, "manifest.json")));
        var m = manifest.RootElement;
        Assert.AreEqual("ARCH-BE-008", m.GetProperty("task").GetString());
        Assert.AreEqual("arch_be008_plan", m.GetProperty("database").GetString());
        Assert.AreEqual("127.0.0.1", m.GetProperty("host").GetString()); Assert.AreEqual(13388, m.GetProperty("port").GetInt32());
        RunId = m.GetProperty("runId").GetString()!;
        VerifyResources();
        AppConnection = Read("app-connection", "arch_be008_app");
        AdminConnection = Read("fixture-connection", "arch_be008_fixture");
    }
    private string Read(string file, string user)
    {
        string value = File.ReadAllText(Path.Combine(Root, file)); var cs = new MySqlConnectionStringBuilder(value);
        if (cs.Server != "127.0.0.1" || cs.Port != 13388 || cs.Database != "arch_be008_plan" || cs.UserID != user) throw new InvalidOperationException("test_connection_target_mismatch");
        return value;
    }
    private static string Docker(params string[] arguments)
    {
        var info = new ProcessStartInfo("docker") { RedirectStandardOutput = true, RedirectStandardError = true };
        foreach (var arg in arguments) info.ArgumentList.Add(arg);
        using var process = Process.Start(info)!;
        string output = process.StandardOutput.ReadToEnd(); process.StandardError.ReadToEnd(); process.WaitForExit();
        if (process.ExitCode != 0) throw new InvalidOperationException("owned_docker_command_failed");
        return output;
    }
    public void VerifyResources()
    {
        foreach (var (kind, name) in new[] { ("container", "aiis-arch-be008-mysql"), ("network", "aiis-arch-be008-net"), ("volume", "aiis-arch-be008-mysql-data") })
        {
            string format = kind == "container" ? "{{index .Config.Labels \"task\"}}|{{index .Config.Labels \"runId\"}}" : "{{index .Labels \"task\"}}|{{index .Labels \"runId\"}}";
            Assert.AreEqual("ARCH-BE-008|" + RunId, Docker(kind, "inspect", "--format", format, name).Trim());
        }
        using var bindings = JsonDocument.Parse(Docker("container", "inspect", "--format", "{{json .HostConfig.PortBindings}}", "aiis-arch-be008-mysql"));
        var port = bindings.RootElement.GetProperty("3306/tcp")[0]; Assert.AreEqual("127.0.0.1",port.GetProperty("HostIp").GetString()); Assert.AreEqual("13388",port.GetProperty("HostPort").GetString());
    }
    public void Stop() { VerifyResources(); Docker("stop", "aiis-arch-be008-mysql"); }
    public void Start() { VerifyResources(); Docker("start", "aiis-arch-be008-mysql"); }
    public async Task<MySqlConnection> Connect(bool app = false)
    {
        var connection = new MySqlConnection(app ? AppConnection : AdminConnection);
        await connection.OpenAsync();
        if (!connection.ServerVersion.StartsWith("8.4.6", StringComparison.Ordinal)) { await connection.DisposeAsync(); throw new InvalidOperationException("mysql_version_mismatch"); }
        return connection;
    }
    public async Task<object?> Scalar(string sql, params (string Name, object Value)[] parameters)
    {
        await using var connection = await Connect(); await using var command = new MySqlCommand(sql, connection);
        foreach (var p in parameters) command.Parameters.AddWithValue(p.Name, p.Value);
        return await command.ExecuteScalarAsync();
    }
    public async Task<List<string[]>> Rows(string sql)
    {
        await using var connection = await Connect(); await using var command = new MySqlCommand(sql, connection); await using var reader = await command.ExecuteReaderAsync();
        var rows = new List<string[]>();
        while (await reader.ReadAsync()) rows.Add(Enumerable.Range(0, reader.FieldCount).Select(i => reader.IsDBNull(i) ? "NULL" : Convert.ToString(reader.GetValue(i), System.Globalization.CultureInfo.InvariantCulture)!).ToArray());
        return rows;
    }
}
