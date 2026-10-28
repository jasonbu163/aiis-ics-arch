/** DS本机列宽偏好：应用/表格/稳定字段隔离，不接触业务草稿、版本或IPC。 */
export interface ColumnSizing {
    key: string;
    minWidth: number;
    defaultWidth?: number;
    resizable: boolean;
}
export type Widths = Record<string, number>;
export type WidthStorage = Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>;
export const MAX_COLUMN_WIDTH = 2000;
export const tableWidthKey = (tableId: string) => `aiis.device-simulator.table-widths.v1:${tableId}`;

export function readTableWidths(storage: () => WidthStorage, tableId: string): {widths: Widths; available: boolean} {
    let raw: string | null;
    try {
        raw = storage().getItem(tableWidthKey(tableId));
    } catch { return {widths: {}, available: false}; }
    try {
        if (!raw) return {widths: {}, available: true};
        const value = JSON.parse(raw);
        return {widths: value?.version === 1 && value.widths && typeof value.widths === 'object' && !Array.isArray(value.widths) ? value.widths : {}, available: true};
    } catch {
        // 无效旧记录回退默认，不影响业务表格。
        return {widths: {}, available: true};
    }
}

export function validTableWidths(widths: Widths, columns: readonly ColumnSizing[]): Widths {
    return Object.fromEntries(columns.filter(column => column.resizable).flatMap(column => {
        const width = widths[column.key];
        return Number.isFinite(width) && width >= column.minWidth && width <= MAX_COLUMN_WIDTH
            ? [[column.key, Math.round(width)]] : [];
    }));
}

export function resizedTableWidths(widths: Widths, columns: readonly ColumnSizing[], key: string, width: number): Widths {
    const clean = validTableWidths(widths, columns);
    const column = columns.find(column => column.key === key && column.resizable);
    if (!column || !Number.isFinite(width)) return clean;
    return {...clean, [key]: Math.max(column.minWidth, Math.min(MAX_COLUMN_WIDTH, Math.round(width)))};
}

export function saveTableWidths(storage: () => WidthStorage, tableId: string, widths: Widths): boolean {
    try {
        storage().setItem(tableWidthKey(tableId), JSON.stringify({version: 1, widths}));
        return true;
    } catch { return false; }
}

export function resetTableWidths(storage: () => WidthStorage, tableId: string): boolean {
    try {
        storage().removeItem(tableWidthKey(tableId));
        return true;
    } catch { return false; }
}
