// 完整输出：Decimal 固定 scale 字符串，日历时间由共享上海工具转换。
using System.Globalization;
using AIIS.Backend.app.Plan.Persistence;
using AIIS.Backend.Common.Time;
namespace AIIS.Backend.app.Plan.Contracts;

public sealed record PlanOut(
    int Id, string CoilNo, string Grade, string Spec, string Weight, string Thickness, string Width,
    string MaterialStatus, string Density, string EntryLength, string Uncoiler1Tension, string ExitTension,
    string Process1Tension, string EntryLoopTension, string ExitLoopTension, string EntryUnitTension,
    string EntryLoopUnitTension, string ProcessUnitTension, string ExitLoopUnitTension, string ExitUnitTension,
    string Status, int Priority, string? Remark, string CreatedAt, string UpdatedAt)
{
    private static string D(decimal value, int scale) => value.ToString("F" + scale, CultureInfo.InvariantCulture);
    public static PlanOut From(PlanEntity e) => new(e.Id, e.CoilNo, e.Grade, e.Spec, D(e.Weight, 4), D(e.Thickness, 3), D(e.Width, 2), e.MaterialStatus,
        D(e.Density, 2), D(e.EntryLength, 2), D(e.Uncoiler1Tension, 2), D(e.ExitTension, 2), D(e.Process1Tension, 2), D(e.EntryLoopTension, 2), D(e.ExitLoopTension, 2),
        D(e.EntryUnitTension, 4), D(e.EntryLoopUnitTension, 4), D(e.ProcessUnitTension, 4), D(e.ExitLoopUnitTension, 4), D(e.ExitUnitTension, 4), e.Status, e.Priority, e.Remark, BusinessTime.Format(e.CreatedAt), BusinessTime.Format(e.UpdatedAt));
}
public sealed record PlanPageOut(IReadOnlyList<PlanOut> Items, int Total, int Page, int PageSize, int TotalPages);
