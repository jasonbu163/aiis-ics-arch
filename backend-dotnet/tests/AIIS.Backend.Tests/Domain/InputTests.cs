// 纯规则/序列化测试，覆盖精度、Unicode、缺失与显式 null。
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using AIIS.Backend.app.Plan.Contracts;
using AIIS.Backend.app.Plan.Domain;
using AIIS.Backend.Common.Errors;
using AIIS.Backend.Common.Serialization;
using AIIS.Backend.Common.Time;
using Microsoft.VisualStudio.TestTools.UnitTesting;
namespace AIIS.Backend.Tests.Domain;

[TestClass]
public sealed class InputTests
{
    public const string Minimal = "{\"coilNo\":\"DEV-001\",\"grade\":\"G\",\"spec\":\"S\",\"weight\":\"1.2300\",\"thickness\":0.123,\"width\":1}";
    public static CreatePlanIn Parse(string json) => CreatePlanJson.Parse(Encoding.UTF8.GetBytes(json));
    [TestMethod]
    public void DefaultsAndAllRequiredAndNull()
    {
        var input = Parse(Minimal);
        Assert.AreEqual("special", input.MaterialStatus); Assert.AreEqual(5, input.Priority); Assert.IsNull(input.Remark);
        foreach (string key in new[] { "coilNo", "grade", "spec", "weight", "thickness", "width" })
        {
            var json = JsonNode.Parse(Minimal)!.AsObject(); json.Remove(key);
            Assert.Throws<PlanException>(() => Parse(json.ToJsonString()), key);
        }
        foreach (var property in typeof(CreatePlanIn).GetProperties().Where(p => p.Name != "Remark"))
        {
            var json = JsonNode.Parse(Minimal)!.AsObject(); json[JsonNamingPolicy.CamelCase.ConvertName(property.Name)] = null;
            Assert.Throws<PlanException>(() => Parse(json.ToJsonString()), property.Name);
        }
        Assert.IsNull(Parse(Minimal.Replace("}", ",\"remark\":null}")).Remark);
    }
    [TestMethod]
    public void StrictShapeAndPriority()
    {
        foreach (string extra in new[] { "\"coilNo\":\"DUP\"", "\"coil_no\":\"X\"", "\"id\":1", "\"createdAt\":\"x\"", "\"priority\":true", "\"priority\":\"5\"", "\"priority\":5.0", "\"priority\":1e0", "\"grade\":{}" })
            Assert.Throws<PlanException>(() => Parse(Minimal.Replace("}", "," + extra + "}")), extra);
        foreach (string bad in new[] { "[]", "null", "{}", Minimal + "{}", Minimal.Replace("\"G\"", "\"\\uD800\""), Minimal.Replace("\"G\"", "\"\\uDC00\"") })
            Assert.Throws<PlanException>(() => Parse(bad), bad);
        Assert.Throws<PlanException>(() => CreatePlanJson.Parse([123, 34, 255, 34, 58, 49, 125]));
    }
    [TestMethod]
    public void ExactDecimalGrammarAndBounds()
    {
        foreach (string text in new[] { " +001.2300e+1 ", "\t12.3000\r\n", "12.", ".30", "1e2", "00001.2300000000000000000000000000000000000" })
            Assert.IsTrue(ExactDecimal.TryParse(text, 12, 4, out _), text);
        foreach (string text in new[] { "", "+", ".", "1 2", "1,234", "NaN", "Infinity", "１", "1.000000000000000000000000000000000000001", "99999999.99991", "100000000", "1e999999999", "1e-999999999", "1e+", "(1)", "$1", "\u00a01\u00a0" })
            Assert.IsFalse(ExactDecimal.TryParse(text, 12, 4, out _), text);
        Assert.IsTrue(ExactDecimal.TryParse("99999999.999900000", 12, 4, out decimal max)); Assert.AreEqual(99999999.9999m, max);
        foreach (string value in new[] { "true", "\"\"", "\"NaN\"", "1e100", "0.00001", "-1" })
            Assert.Throws<PlanException>(() => Parse(Minimal.Replace("\"1.2300\"", value)), value);
        Assert.AreEqual(100m, Parse(Minimal.Replace("\"1.2300\"", "1e2")).Weight);
    }
    [TestMethod]
    public void PythonStripAndUnicodeScalars()
    {
        Assert.IsFalse(PlanRules.ValidCoil(" \t\u001c\u0085\u3000"));
        Assert.IsTrue(PlanRules.ValidCoil("\t X \r")); Assert.IsFalse(PlanRules.ValidCoil("X\tY")); Assert.IsFalse(PlanRules.ValidCoil("X\u007f"));
        Assert.IsTrue(PlanRules.ValidCoil("卷-😀"));
        var twenty = string.Concat(Enumerable.Repeat("😀", 20));
        Assert.AreEqual(20, PlanRules.ScalarLength(twenty));
        Assert.AreEqual(twenty, Parse(Minimal.Replace("\"G\"", JsonSerializer.Serialize(twenty))).Grade);
        Assert.Throws<PlanException>(() => Parse(Minimal.Replace("\"G\"", JsonSerializer.Serialize(twenty + "😀"))));
        Assert.AreEqual(" ", Parse(Minimal.Replace("\"G\"", "\" \"")).Grade);
    }
    [TestMethod]
    public void BusinessTimeDoesNotUseProcessTimeZone()
    {
        var value = new DateTime(2026, 10, 28, 0, 0, 1, DateTimeKind.Unspecified);
        Assert.AreEqual("2026-10-28T00:00:01+08:00", BusinessTime.Format(value));
        Assert.AreEqual("2026-10-28T00:00:01+08:00", BusinessTime.Format(DateTime.SpecifyKind(value, DateTimeKind.Utc)));
    }
}
