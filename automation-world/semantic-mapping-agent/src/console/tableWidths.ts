/** SMA公共表格列宽：稳定字段ID、本机偏好、最小宽度及显式恢复。 */
import { computed, onBeforeUnmount, ref, watchEffect } from "vue";
export interface TableColumn { id: string; width: number; min?: number; fixed?: boolean }
export function resolveTableWidths(columns: readonly TableColumn[], stored: unknown): Record<string, number> {
  const values = stored && typeof stored === "object" ? stored as Record<string, unknown> : {};
  return Object.fromEntries(columns.map(column => {
    const saved = values[column.id];
    return [column.id, typeof saved === "number" && Number.isFinite(saved)
      ? Math.max(column.min ?? 100, saved) : column.width];
  }));
}
export function useTableWidths(tableId: string, columns: readonly TableColumn[]) {
  const key = `sma.table-widths.v1.${tableId}`;
  let stored: unknown;
  try { stored = JSON.parse(window.localStorage.getItem(key) ?? "null"); } catch { stored = null; }
  const widths = ref(resolveTableWidths(columns, stored));
  const totalWidth = computed(() => Object.values(widths.value).reduce((sum, width) => sum + width, 0));
  let cleanup: (() => void) | undefined;
  function reset() {
    cleanup?.();
    widths.value = resolveTableWidths(columns, null);
    try { window.localStorage.removeItem(key); } catch { /* local preference can be unavailable */ }
  }
  function startResize(id: string, event: PointerEvent) {
    if (event.button !== 0) return;
    const column = columns.find(value => value.id === id);
    if (!column) return;
    cleanup?.();
    event.preventDefault();
    const origin = event.clientX;
    const width = widths.value[id] ?? column.width;
    const move = (next: PointerEvent) => { widths.value[id] = Math.max(column.min ?? 100, width + next.clientX - origin); };
    const finish = () => {
      try { window.localStorage.setItem(key, JSON.stringify(widths.value)); } catch { /* best-effort local preference */ }
      cleanup?.();
    };
    cleanup = () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", finish);
      window.removeEventListener("pointercancel", finish);
      cleanup = undefined;
    };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", finish);
    window.addEventListener("pointercancel", finish);
  }
  onBeforeUnmount(() => cleanup?.());
  return { tableId, columns, widths, totalWidth, reset, startResize };
}

/** 为既有原生业务表接入同一列宽状态，保留其表格/表单业务模板。 */
type WidthState = ReturnType<typeof useTableWidths>;
const tableRefresh = new WeakMap<HTMLTableElement, (label: string) => void>();
const tableCleanup = new WeakMap<HTMLTableElement, () => void>();
export const vTableWidths: import("vue").ObjectDirective<HTMLTableElement, [WidthState, string]> = {
  mounted(element, binding) {
    const [state, label] = binding.value;
    element.dataset.smaTable = state.tableId;
    const group = document.createElement("colgroup");
    const cols = state.columns.map(column => {
      const col = document.createElement("col"); group.append(col); return col;
    });
    element.prepend(group);
    const removers: (() => void)[] = [];
    const handles: { header: HTMLTableCellElement; handle: HTMLSpanElement }[] = [];
    element.querySelectorAll<HTMLTableCellElement>("thead tr:first-child > th").forEach((header, index) => {
      const column = state.columns[index];
      if (!column || column.fixed) return;
      const handle = document.createElement("span");
      handle.className = "sma-column-resizer";
      handle.setAttribute("role", "separator"); handle.setAttribute("aria-label", label);
      const resize = (event: PointerEvent) => state.startResize(column.id, event);
      handle.addEventListener("pointerdown", resize); header.append(handle);
      handles.push({ header, handle });
      removers.push(() => { handle.removeEventListener("pointerdown", resize); handle.remove(); });
    });
    tableRefresh.set(element, text => handles.forEach(({ header, handle }) => {
      handle.setAttribute("aria-label", text);
      // Vue更新表头文本时会替换textContent；复用原handle与listener。
      if (!header.contains(handle)) header.append(handle);
    }));
    const stop = watchEffect(() => {
      cols.forEach((col, index) => {
        const width = `${state.widths.value[state.columns[index].id]}px`;
        col.style.width = width;
        const header = element.querySelectorAll<HTMLTableCellElement>("thead tr:first-child > th")[index];
        if (header) { header.style.width = width; header.style.minWidth = "0"; }
      });
      element.style.width = `${state.totalWidth.value}px`;
    });
    tableCleanup.set(element, () => { stop(); removers.forEach(remove => remove()); group.remove(); });
  },
  updated(element, binding) { tableRefresh.get(element)?.(binding.value[1]); },
  beforeUnmount(element) { tableCleanup.get(element)?.(); tableCleanup.delete(element); tableRefresh.delete(element); },
};
