/** 文件路径: /frontend-js/src/utils/tableColumnWidths.js
 * 功能描述: 按应用、表和稳定字段保存可拖拽的本机列宽偏好。 */
import { reactive, ref } from 'vue'

export function useTableColumnWidths(tableId, columns) {
  const key = `aiis-ics-architecture:table-widths:${tableId}`
  const widths = reactive(Object.fromEntries(Object.entries(columns).map(([field, column]) => [field, column.width])))
  const version = ref(0)
  try {
    const saved = JSON.parse(localStorage.getItem(key) || '{}')
    for (const [field, column] of Object.entries(columns)) {
      if (Number.isFinite(saved?.[field]) && saved[field] >= column.minWidth && saved[field] <= 3000) widths[field] = saved[field]
    }
  } catch { /* 本机偏好不可用时使用默认列宽。 */ }

  function onHeaderDragEnd(newWidth, oldWidth, column) {
    const field = column?.property
    if (!Object.hasOwn(columns, field) || !Number.isFinite(newWidth)) return
    widths[field] = Math.max(columns[field].minWidth, Math.min(3000, Math.round(newWidth)))
    column.width = column.realWidth = widths[field]
    try { localStorage.setItem(key, JSON.stringify({ ...widths })) } catch { /* 不阻塞查询。 */ }
  }

  function reset() {
    for (const [field, column] of Object.entries(columns)) widths[field] = column.width
    try { localStorage.removeItem(key) } catch { /* 不阻塞查询。 */ }
    // 重建 Element Plus 列，清除其内部拖拽宽度。
    version.value++
  }
  return { widths, version, onHeaderDragEnd, reset }
}
