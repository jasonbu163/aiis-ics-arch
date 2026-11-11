// 配置测试覆盖原始点表和 Windows 路径歧义的启动前拒绝。
using FieldFlow.Domain;
using FieldFlow.Infrastructure.Configuration;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace FieldFlow.Tests;

[TestClass]
public sealed class ConfigurationTests
{
    [TestMethod]
    public void AcceptedS7CatalogLoadsWithoutTranslation()
    {
        var config = ConfigLoader.Load(Path.Combine(AppContext.BaseDirectory, "config", "demo01.yaml"));
        Assert.AreEqual("ff-csharp-demo01", config.InstanceId);
        Assert.AreEqual("s7_a", config.Flows[0].DeviceId);
        Assert.AreEqual(0, config.Plcs["s7_a"].Points["value"].Offset);
        Assert.AreEqual("fcda187b9a72bd75720409a4a9b84c1feb0b4bb8c01f98af027e945fcad9535d",
            config.CatalogHashes["plcs/s7-a.json"]);
    }

    [TestMethod]
    [DataRow("plcs/.. /s7-a.json")]
    [DataRow("plcs/NUL.txt")]
    [DataRow("../s7-a.json")]
    [DataRow("'plcs/s7-a.json '")]
    public void WindowsAmbiguousPathFailsBeforeReading(string invalid)
    {
        var root = Directory.CreateTempSubdirectory("ff003-config-");
        try
        {
            var text = File.ReadAllText(Path.Combine(AppContext.BaseDirectory, "config", "demo01.yaml"));
            var path = Path.Combine(root.FullName, "demo.yaml");
            File.WriteAllText(path, text.Replace("plcs/s7-a.json", invalid, StringComparison.Ordinal));
            var error = Assert.ThrowsExactly<ConfigException>(() => ConfigLoader.Load(path));
            Assert.AreEqual("config_path", error.Key);
            Assert.AreEqual(1, Directory.GetFileSystemEntries(root.FullName).Length);
        }
        finally { root.Delete(true); }
    }

    [TestMethod]
    public void DuplicateJsonKeyFailsClosed()
    {
        var root = Directory.CreateTempSubdirectory("ff003-duplicate-");
        try
        {
            Directory.CreateDirectory(Path.Combine(root.FullName, "plcs"));
            var config = File.ReadAllText(Path.Combine(AppContext.BaseDirectory, "config", "demo01.yaml"));
            File.WriteAllText(Path.Combine(root.FullName, "demo.yaml"), config);
            var catalog = File.ReadAllText(Path.Combine(AppContext.BaseDirectory, "config", "plcs", "s7-a.json"));
            File.WriteAllText(Path.Combine(root.FullName, "plcs", "s7-a.json"),
                catalog.Replace("\"format\": \"ff.plc\",", "\"format\": \"ff.plc\", \"format\": \"ff.plc\",", StringComparison.Ordinal));
            Assert.ThrowsExactly<ConfigException>(() => ConfigLoader.Load(Path.Combine(root.FullName, "demo.yaml")));
            Assert.IsFalse(File.Exists(Path.Combine(root.FullName, "state.sqlite3")));
        }
        finally { root.Delete(true); }
    }

    [TestMethod]
    public void SymlinkInMainConfigPathFailsBeforeReading()
    {
        var root = Directory.CreateTempSubdirectory("ff003-link-");
        try
        {
            var actual = Path.Combine(root.FullName, "actual");
            Directory.CreateDirectory(actual);
            var link = Path.Combine(root.FullName, "alias");
            try { Directory.CreateSymbolicLink(link, actual); }
            catch (Exception error) when (error is UnauthorizedAccessException or IOException)
            {
                Assert.Inconclusive("The test host cannot create a directory symlink.");
                return;
            }
            File.WriteAllText(Path.Combine(actual, "demo.yaml"), "schema_version: 2");
            var errorResult = Assert.ThrowsExactly<ConfigException>(() => ConfigLoader.Load(Path.Combine(link, "demo.yaml")));
            Assert.AreEqual("config_path", errorResult.Key);
        }
        finally { root.Delete(true); }
    }
}
