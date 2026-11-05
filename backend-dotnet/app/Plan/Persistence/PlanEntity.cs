// 唯一 plans 实体：25 个显式列，无导航或数据库默认。
namespace AIIS.Backend.app.Plan.Persistence;

public sealed class PlanEntity
{
    public string CoilNo { get; set; } = "";
    public string Grade { get; set; } = "";
    public string Spec { get; set; } = "";
    public decimal Weight { get; set; }
    public decimal Thickness { get; set; }
    public decimal Width { get; set; }
    public string MaterialStatus { get; set; } = "";
    public decimal Density { get; set; }
    public decimal EntryLength { get; set; }
    public decimal Uncoiler1Tension { get; set; }
    public decimal ExitTension { get; set; }
    public decimal Process1Tension { get; set; }
    public decimal EntryLoopTension { get; set; }
    public decimal ExitLoopTension { get; set; }
    public decimal EntryUnitTension { get; set; }
    public decimal EntryLoopUnitTension { get; set; }
    public decimal ProcessUnitTension { get; set; }
    public decimal ExitLoopUnitTension { get; set; }
    public decimal ExitUnitTension { get; set; }
    public int Priority { get; set; } = 0;
    public string? Remark { get; set; }
    public int Id { get; set; }
    public string Status { get; set; } = "";
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
}
