// 计划创建 DTO；所有客户端省略默认由此明确提供，持久实体与 DTO 分离。
using System.Text.Json.Serialization;
namespace AIIS.Backend.app.Plan.Contracts;

public sealed class CreatePlanIn
{
    [JsonRequired]
    public string CoilNo { get; set; } = "";
    [JsonRequired]
    public string Grade { get; set; } = "";
    [JsonRequired]
    public string Spec { get; set; } = "";
    [JsonRequired]
    [JsonNumberHandling(JsonNumberHandling.AllowReadingFromString)]
    public decimal Weight { get; set; }
    [JsonRequired]
    [JsonNumberHandling(JsonNumberHandling.AllowReadingFromString)]
    public decimal Thickness { get; set; }
    [JsonRequired]
    [JsonNumberHandling(JsonNumberHandling.AllowReadingFromString)]
    public decimal Width { get; set; }
    public string MaterialStatus { get; set; } = "special";
    [JsonNumberHandling(JsonNumberHandling.AllowReadingFromString)]
    public decimal Density { get; set; }
    [JsonNumberHandling(JsonNumberHandling.AllowReadingFromString)]
    public decimal EntryLength { get; set; }
    [JsonNumberHandling(JsonNumberHandling.AllowReadingFromString)]
    public decimal Uncoiler1Tension { get; set; }
    [JsonNumberHandling(JsonNumberHandling.AllowReadingFromString)]
    public decimal ExitTension { get; set; }
    [JsonNumberHandling(JsonNumberHandling.AllowReadingFromString)]
    public decimal Process1Tension { get; set; }
    [JsonNumberHandling(JsonNumberHandling.AllowReadingFromString)]
    public decimal EntryLoopTension { get; set; }
    [JsonNumberHandling(JsonNumberHandling.AllowReadingFromString)]
    public decimal ExitLoopTension { get; set; }
    [JsonNumberHandling(JsonNumberHandling.AllowReadingFromString)]
    public decimal EntryUnitTension { get; set; }
    [JsonNumberHandling(JsonNumberHandling.AllowReadingFromString)]
    public decimal EntryLoopUnitTension { get; set; }
    [JsonNumberHandling(JsonNumberHandling.AllowReadingFromString)]
    public decimal ProcessUnitTension { get; set; }
    [JsonNumberHandling(JsonNumberHandling.AllowReadingFromString)]
    public decimal ExitLoopUnitTension { get; set; }
    [JsonNumberHandling(JsonNumberHandling.AllowReadingFromString)]
    public decimal ExitUnitTension { get; set; }
    public int Priority { get; set; } = 5;
    public string? Remark { get; set; }
}
