<!-- DS表格薄封装：保留原生EP列/插槽/事件，统一列宽记忆、恢复、密度和滚动。 -->
<script lang="ts">
import { cloneVNode, defineComponent, Fragment, h, mergeProps, nextTick, ref, watch, type VNode } from 'vue';
import { ElTable, ElTableColumn, type TableInstance } from 'element-plus';
import { useI18n } from 'vue-i18n';
import ConsoleActionButton from './ConsoleActionButton.vue';
import { readTableWidths, resetTableWidths, resizedTableWidths, saveTableWidths, validTableWidths, type ColumnSizing, type Widths } from '../../console/tableWidths';

function flatten(nodes: VNode[]): VNode[] {
    return nodes.flatMap(node => node.type === Fragment && Array.isArray(node.children) ? flatten(node.children as VNode[]) : [node]);
}

export default defineComponent({
    name: 'ConsoleDataTable',
    inheritAttrs: false,
    props: { tableId: {type: String, required: true} },
    setup(props, {attrs, slots}) {
        const {t} = useI18n();
        const table = ref<TableInstance>();
        const widths = ref<Widths>({});
        const available = ref(true);
        const storage = () => window.localStorage;
        let columns: ColumnSizing[] = [];
        watch(() => props.tableId, id => {
            const saved = readTableWidths(storage, id);
            widths.value = saved.widths;
            available.value = saved.available;
        }, {immediate: true});

        function drag(width: number, _oldWidth: number, column: {columnKey?: string; width: number; realWidth: number}) {
            if (!column.columnKey) return;
            widths.value = resizedTableWidths(widths.value, columns, column.columnKey, width);
            const accepted = widths.value[column.columnKey];
            if (accepted === undefined) return;
            column.width = column.realWidth = accepted;
            available.value = saveTableWidths(storage, props.tableId, widths.value);
            void nextTick(() => table.value?.doLayout());
        }
        function reset() {
            widths.value = {};
            available.value = resetTableWidths(storage, props.tableId);
            // 不重建表格，保留选择/分页/编辑控件状态，只让原生列重新布局。
            void nextTick(() => table.value?.doLayout());
        }
        function renderColumns() {
            const nodes = flatten(slots.default?.() || []);
            columns = nodes.filter(node => node.type === ElTableColumn).map(node => {
                const p = node.props || {};
                const defaultWidth = Number(p.width) || undefined;
                return {
                    key: String(p.columnKey || p['column-key'] || p.prop || ''),
                    minWidth: Math.max(40, Number(p.minWidth || p['min-width']) || defaultWidth || 140),
                    defaultWidth,
                    resizable: p.resizable !== false,
                };
            });
            const saved = validTableWidths(widths.value, columns);
            return nodes.map(node => {
                if (node.type !== ElTableColumn) return node;
                const p = node.props || {};
                const key = String(p.columnKey || p['column-key'] || p.prop || '');
                const spec = columns.find(column => column.key === key)!;
                return cloneVNode(node, {
                    columnKey: key,
                    width: saved[key] ?? spec.defaultWidth,
                    minWidth: spec.minWidth,
                    resizable: spec.resizable,
                    showOverflowTooltip: p.showOverflowTooltip ?? p['show-overflow-tooltip'] ?? true,
                });
            });
        }
        return () => h('div', {class: 'ds-data-table', 'data-table-id': props.tableId}, [
            h('div', {class: 'ds-data-table__tools'}, [
                !available.value ? h('small', {class: 'ds-table-preference-warning'}, t('simulator.tables.storageUnavailable')) : null,
                h(ConsoleActionButton, {labelKey: 'simulator.tables.resetWidths', size: 'small', title: t('simulator.tables.dragHint'), 'data-testid': 'table-reset-widths', onClick: reset}),
            ]),
            h(ElTable, mergeProps({
                ref: table,
                border: true,
                allowDragLastColumn: true,
                maxHeight: 440,
                emptyText: t('simulator.tables.empty'),
                tooltipOptions: {showAfter: 300, popperClass: 'ds-table-tooltip'},
            }, attrs, {class: 'aw-data-table ds-data-table__grid', onHeaderDragend: drag}), {...slots, default: renderColumns}),
        ]);
    },
});
</script>
