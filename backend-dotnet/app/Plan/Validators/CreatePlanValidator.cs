// FluentValidation 负责 DTO 的业务/存储范围；JSON 形状由严格 binder 验证。
using AIIS.Backend.app.Plan.Contracts;
using AIIS.Backend.app.Plan.Domain;
using FluentValidation;
namespace AIIS.Backend.app.Plan.Validators;

public sealed class CreatePlanValidator : AbstractValidator<CreatePlanIn>
{
    public CreatePlanValidator()
    {
        RuleFor(x => x.CoilNo).Must(x => PlanRules.ScalarLength(x) is >= 1 and <= 50).WithErrorCode("string_length");
        RuleFor(x => x.CoilNo).Must(PlanRules.ValidCoil).WithErrorCode("plan_invalid_coil_no");
        RuleFor(x => x.Grade).Must(x => PlanRules.ScalarLength(x) is >= 1 and <= 20).WithErrorCode("string_length");
        RuleFor(x => x.Spec).Must(x => PlanRules.ScalarLength(x) is >= 1 and <= 50).WithErrorCode("string_length");
        RuleFor(x => x.MaterialStatus).Must(x => PlanRules.ScalarLength(x) is >= 0 and <= 20).WithErrorCode("string_length");
        RuleFor(x => x.Remark).Must(x => x is null || PlanRules.ScalarLength(x) is >= 0 and <= 500).WithErrorCode("string_length");
        RuleFor(x => x.Weight).InclusiveBetween(0, 99999999.9999m).WithErrorCode("decimal_range");
        RuleFor(x => x.Thickness).InclusiveBetween(0, 9999999.999m).WithErrorCode("decimal_range");
        RuleFor(x => x.Width).ExclusiveBetween(0, 100000000m).WithErrorCode("decimal_range");
        RuleFor(x => x.Priority).InclusiveBetween(1, 10).WithErrorCode("integer_range");
        RuleFor(x => x).Must(x => new[] { x.Density, x.EntryLength, x.Uncoiler1Tension, x.ExitTension, x.Process1Tension, x.EntryLoopTension, x.ExitLoopTension, x.EntryUnitTension, x.EntryLoopUnitTension, x.ProcessUnitTension, x.ExitLoopUnitTension, x.ExitUnitTension }.All(v => v >= 0)).WithErrorCode("decimal_range");
    }
}
