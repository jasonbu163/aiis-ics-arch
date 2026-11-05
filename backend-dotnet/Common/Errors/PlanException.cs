// 共享稳定错误键与业务异常；不携带请求正文、SQL 或连接秘密。
namespace AIIS.Backend.Common.Errors;

public sealed class PlanException(int status, string errorCode, IReadOnlyList<FieldError>? errors = null) : Exception(errorCode)
{
    public int Status { get; } = status;
    public string ErrorCode { get; } = errorCode;
    public IReadOnlyList<FieldError>? Errors { get; } = errors;
    public static PlanException Invalid(string field, string rule) => new(422, "plan_invalid_request", [new(field, rule)]);
}
public sealed record FieldError(string Field, string Rule);
