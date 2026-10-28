/** DS统一上海日历时间显示；按显式偏移转换一次，单调计数不转换为日期。 */
export const BUSINESS_TIME_ZONE = 'Asia/Shanghai';
const calendar = new Intl.DateTimeFormat('en-GB', {
    timeZone: BUSINESS_TIME_ZONE,
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23',
});

export function formatShanghaiTime(value: unknown): string | null {
    if (typeof value !== 'string' || !/(?:Z|[+-]\d{2}:\d{2})$/.test(value)) return null;
    const date = new Date(value);
    if (!Number.isFinite(date.getTime())) return null;
    const parts = Object.fromEntries(calendar.formatToParts(date).map(part => [part.type, part.value]));
    return `${parts.year}-${parts.month}-${parts.day} ${parts.hour}:${parts.minute}:${parts.second}`;
}
