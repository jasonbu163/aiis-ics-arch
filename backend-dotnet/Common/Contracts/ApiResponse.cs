// 成功与错误信封；timestamp 只表示响应生成的 Unix 毫秒。
using AIIS.Backend.Common.Errors;
namespace AIIS.Backend.Common.Contracts;

public sealed record ApiResponse<T>(int Code, string Message, T Data, long Timestamp)
{
    public static ApiResponse<T> Success(T data) => new(200, "success", data, DateTimeOffset.UtcNow.ToUnixTimeMilliseconds());
}
public sealed record ApiError(int Code, string Message, object? Data, string ErrorCode, long Timestamp, IReadOnlyList<FieldError>? Errors)
{
    public static ApiError From(PlanException error) => new(error.Status, error.ErrorCode, null, error.ErrorCode, DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(), error.Errors);
}
