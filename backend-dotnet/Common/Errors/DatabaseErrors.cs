// 只对命名唯一键的 1062 判冲突；其他数据库失败保留明确分类。
using MySql.Data.MySqlClient;
using System.Text.RegularExpressions;
namespace AIIS.Backend.Common.Errors;

public static partial class DatabaseErrors
{
    [GeneratedRegex(@"for key '(?:plans\.)?ix_plans_coil_no'", RegexOptions.CultureInvariant)]
    private static partial Regex CoilIndex();
    public static MySqlException? Find(Exception ex)
    {
        for (Exception? current = ex; current is not null; current = current.InnerException)
            if (current is MySqlException mysql) return mysql;
        return null;
    }
    public static bool IsCoilConflict(Exception ex) => Find(ex) is { Number: 1062 } mysql && CoilIndex().IsMatch(mysql.Message);
    public static PlanException Translate(Exception ex, bool commitAttempted = false)
    {
        if (commitAttempted) return new(503, "plan_write_outcome_unknown");
        if (IsCoilConflict(ex)) return new(409, "plan_coil_already_exists");
        if (Find(ex) is { } mysql && (mysql.IsTransient || mysql.Number is 0 or 1040 or 1042 or 1045 or 1049 or 1129 or 1130 or 2002 or 2003 or 2006 or 2013 or 2055) || ex is TimeoutException or OperationCanceledException) return new(503, "plan_database_unavailable");
        return new(500, "plan_internal_error");
    }
}
