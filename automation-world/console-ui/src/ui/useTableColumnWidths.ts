/** 公共列宽工具：按应用、表和稳定字段标识记忆 Element Plus 表格的本机列宽。 */
import { ref } from 'vue'

const maximumWidth = 4096

export function useTableColumnWidths(appId: string, tableId: string, minimums: Readonly<Record<string, number>>) {
  const key = `aiis.table-widths.v1:${appId}:${tableId}`
  const widths = ref<Partial<Record<string, number>>>({})
  const tableVersion = ref(0)

  try {
    const saved: unknown = JSON.parse(localStorage.getItem(key) ?? 'null')
    if (saved && typeof saved === 'object' && !Array.isArray(saved)) {
      for (const [field, min] of Object.entries(minimums)) {
        const value = (saved as Record<string, unknown>)[field]
        if (typeof value === 'number' && Number.isFinite(value) && value >= min && value <= maximumWidth) {
          widths.value[field] = value
        }
      }
    }
  } catch { /* 本机偏好不可用时，使用表格自身的默认宽度。 */ }

  function resize(width: number, _oldWidth: number, column: { property?: string; width?: number | string; realWidth?: number | null }) {
    const field = column.property
    if (!field || !Object.prototype.hasOwnProperty.call(minimums, field) || !Number.isFinite(width)) return
    const clamped = Math.max(minimums[field], Math.min(maximumWidth, Math.round(width)))
    widths.value[field] = clamped
    column.width = column.realWidth = clamped
    try { localStorage.setItem(key, JSON.stringify(widths.value)) } catch { /* 保留当前界面宽度。 */ }
  }

  function reset() {
    widths.value = {}
    try { localStorage.removeItem(key) } catch { /* 当前界面仍可恢复默认。 */ }
    // Element Plus 会在列实例内部保留拖拽结果，重建表格可清除它。
    tableVersion.value++
  }

  return { widths, tableVersion, resize, reset }
}
