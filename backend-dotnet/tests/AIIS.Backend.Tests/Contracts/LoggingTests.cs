// 实际日志解析、10MiB 轮转与五文件保留；输出写入专属临时根，不改变项目依赖。
using System.Text;
using System.Text.Json;
using AIIS.Backend.Infrastructure.Logging;
using Serilog;
using Microsoft.VisualStudio.TestTools.UnitTesting;
namespace AIIS.Backend.Tests.Contracts;

[TestClass]
public sealed class LoggingTests
{
    [TestMethod]
    public void JsonLinesRotateRetainAndFlush()
    {
        string directory = Path.Combine("/private/tmp", "arch-be008-log-check-" + Guid.NewGuid().ToString("N"));
        var previous = Console.Out;
        var capture = new JsonLineCounter();
        try
        {
            Console.SetOut(capture);
            using (var logger = BackendLogging.Configure(new LoggerConfiguration(), directory).CreateLogger())
                for (int i=0;i<64;i++) logger.Information("{event} {requestId} {payload}", "rotation_probe", "log-probe", new string('x',1024*1024));
        }
        finally { Console.SetOut(previous); }
        Assert.AreEqual(64,capture.Count);
        var files=Directory.GetFiles(directory,"*.jsonl");Assert.AreEqual(5,files.Length);
        foreach(string file in files)
        {
            Assert.IsTrue(new FileInfo(file).Length < BackendLogging.FileLimit + 2*1024*1024);
            foreach(string line in File.ReadLines(file))using(JsonDocument.Parse(line)){}
        }
        TestContext.WriteLine("rotation_directory="+directory+"; stdout64 valid JSON; retained5 files; dispose flushed");
    }
    public TestContext TestContext { get; set; } = null!;
    private sealed class JsonLineCounter : TextWriter
    {
        public override Encoding Encoding => Encoding.UTF8;
        private readonly StringBuilder line=new();
        public int Count { get; private set; }
        public override void Write(char value)
        {
            if(value=='\n') {using var doc=JsonDocument.Parse(line.ToString());line.Clear();Count++;}
            else line.Append(value);
        }
    }
}
