<!-- SMA HTTP 业务表格共用本机列宽、横向滚动和布局状态。 -->
<script setup lang="ts">
import { ConsoleActionButton } from "@aw-ui";
import { ElPagination } from "element-plus";
import { useTableWidths, vTableWidths, type TableColumn } from "../../../console/tableWidths";
import { useHttpMessages } from "../messages";

const props = defineProps<{
  tableId: string;
  columns: (TableColumn & { title: string })[];
  total: number;
  busy?: boolean;
  caption: string;
}>();
const page = defineModel<number>("page");
const pageSize = defineModel<number>("pageSize");
const ui = useHttpMessages();
const table = useTableWidths(props.tableId, props.columns);
</script>

<template>
  <div class="http-table-tools">
    <div class="http-table-filters"><slot name="filters" /></div>
    <ConsoleActionButton :title="ui.resetHelp" @click="table.reset">{{ ui.reset }}</ConsoleActionButton>
  </div>
  <div class="table-scroll http-table-scroll" role="region" tabindex="0" :aria-label="caption" :aria-busy="busy">
    <table v-table-widths="[table, ui.resize]" class="http-table" :aria-label="caption">
      <thead><tr><th v-for="column in columns" :key="column.id" scope="col">{{ column.title }}</th></tr></thead>
      <tbody>
        <slot />
        <tr v-if="!total"><td :colspan="columns.length" class="http-table-empty">{{ busy ? ui.loading : ui.empty }}</td></tr>
      </tbody>
    </table>
  </div>
  <ElPagination v-if="page !== undefined && pageSize !== undefined && total > 10"
    v-model:current-page="page" v-model:page-size="pageSize" :total="total"
    :page-sizes="[10, 25, 50]" :pager-count="5" layout="total, sizes, prev, pager, next"
    size="small" append-size-to="#sma-overlays" class="http-pagination" />
</template>
