// 无时区 MySQL DATETIME 明确解释为上海日历；输出固定秒精度和 offset。
using System.Globalization;
namespace AIIS.Backend.Common.Time;

public static class BusinessTime
{
    public const string Zone = "Asia/Shanghai";
    public static string Format(DateTime value) => new DateTimeOffset(DateTime.SpecifyKind(value, DateTimeKind.Unspecified), TimeZoneInfo.FindSystemTimeZoneById(Zone).GetUtcOffset(value)).ToString("yyyy-MM-dd'T'HH:mm:sszzz", CultureInfo.InvariantCulture);
}
