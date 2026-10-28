/** 本机表格列宽偏好：应用/表/稳定字段隔离，损坏或过期字段回默认，不写业务配置。 */
export interface WidthColumn { id: string; width: number; min: number }
export interface WidthStorage { getItem(key: string): string | null; setItem(key: string, value: string): void; removeItem(key: string): void }
export function widthKey(app: string, table: string): string { return `aiis.table-widths.v1:${app}:${table}` }
export function loadWidths(storage: WidthStorage | undefined, key: string, columns: readonly WidthColumn[]): Record<string, number> {
  const defaults = Object.fromEntries(columns.map(c => [c.id, c.width]))
  try {
    const parsed: unknown = JSON.parse(storage?.getItem(key) ?? 'null')
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return defaults
    for (const c of columns) {
      const width = (parsed as Record<string, unknown>)[c.id]
      if (typeof width === 'number' && Number.isFinite(width) && width >= c.min && width <= 4096) defaults[c.id] = width
    }
  } catch { /* Browser storage can be unavailable; retain usable defaults. */ }
  return defaults
}
export function saveWidth(storage: WidthStorage | undefined, key: string, columns: readonly WidthColumn[], widths: Record<string, number>, id: string, value: number): Record<string, number> {
  const column = columns.find(c => c.id === id)
  if (!column || !Number.isFinite(value)) return widths
  const next = { ...widths, [id]: Math.max(column.min, Math.min(4096, Math.round(value))) }
  try { storage?.setItem(key, JSON.stringify(next)) } catch { /* Current view remains usable. */ }
  return next
}
export function resetWidths(storage: WidthStorage | undefined, key: string, columns: readonly WidthColumn[]): Record<string, number> {
  try { storage?.removeItem(key) } catch { /* Current view still resets. */ }
  return Object.fromEntries(columns.map(c => [c.id, c.width]))
}
