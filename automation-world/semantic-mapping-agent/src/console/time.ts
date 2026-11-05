/** 上海业务时间显示工具；仅格式化明确携带时区的日历值，不改底层精度。 */
export const BUSINESS_TIME_ZONE = "Asia/Shanghai";
const formatter = new Intl.DateTimeFormat("en-CA", {
  timeZone: BUSINESS_TIME_ZONE, year: "numeric", month: "2-digit", day: "2-digit",
  hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23",
});
export function formatBusinessTime(value: string | null | undefined, missing = "—"): string {
  if (!value || !/^\d{4}-\d\d-\d\dT.*(?:Z|[+-]\d\d:\d\d)$/i.test(value)) return missing;
  const instant = new Date(value);
  if (!Number.isFinite(instant.getTime())) return missing;
  const parts = Object.fromEntries(formatter.formatToParts(instant).map(part => [part.type, part.value]));
  return `${parts.year}-${parts.month}-${parts.day} ${parts.hour}:${parts.minute}:${parts.second}`;
}
