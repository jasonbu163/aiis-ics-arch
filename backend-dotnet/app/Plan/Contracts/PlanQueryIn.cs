// 查询参数按精确整数和已检查的 offset 绑定；未知键忽略。
using System.Globalization;
using AIIS.Backend.Common.Errors;
using Microsoft.AspNetCore.Http;
namespace AIIS.Backend.app.Plan.Contracts;

public sealed record PlanQueryIn(int Page, int PageSize, int Offset, string? CoilNo, string? Grade, string? MaterialStatus, string? Status)
{
    public static int Positive(string? text, string field, int fallback)
    {
        if (text is null) return fallback;
        if (text.Length == 0 || text.Any(c => c is < '0' or > '9') || !int.TryParse(text, NumberStyles.None, CultureInfo.InvariantCulture, out int result) || result < 1) throw PlanException.Invalid(field, "positive_integer");
        return result;
    }
    public static PlanQueryIn Parse(IQueryCollection query)
    {
        string? Get(string key)
        {
            if (!query.TryGetValue(key, out var values)) return null;
            if (values.Count != 1) throw PlanException.Invalid(key, "single_value");
            return values[0];
        }
        int page = Positive(Get("page"), "page", 1), size = Positive(Get("pageSize"), "pageSize", 20);
        long offset = ((long)page - 1) * size;
        if (size > 100 || offset > int.MaxValue) throw PlanException.Invalid("pageSize", "pagination_range");
        return new(page, size, (int)offset, Get("coilNo"), Get("grade"), Get("materialStatus"), Get("status"));
    }
}
