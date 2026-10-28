/** 上海业务时间视图：墙上时间控件与IPC毫秒边界，不使用宿主本机时区。 */
export const BUSINESS_TIME_ZONE = 'Asia/Shanghai'
export const TIME_PROFILE = 'asia-shanghai-rfc3339-ms-v1'
const display = new Intl.DateTimeFormat('en-GB', { timeZone: BUSINESS_TIME_ZONE, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23' })
export function formatBusinessTime(value?: string | null): string {
  if (!value || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.test(value) || !Number.isFinite(Date.parse(value))) return '—'
  const parts = Object.fromEntries(display.formatToParts(new Date(value)).map(p => [p.type, p.value]))
  return `${parts.year}-${parts.month}-${parts.day} ${parts.hour}:${parts.minute}:${parts.second}`
}
export function wallTime(value?: string | null): string {
  const formatted = formatBusinessTime(value)
  return formatted === '—' ? '' : formatted.replace(' ', 'T')
}
export function historyBoundary(wall: string | null, end: boolean): string {
  if (!wall) return ''
  const value = wall.replace(' ', 'T')
  if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/.test(value)) return ''
  const iso = `${value}.${end ? '999' : '000'}+08:00`
  return wallTime(iso) === value ? iso : ''
}
