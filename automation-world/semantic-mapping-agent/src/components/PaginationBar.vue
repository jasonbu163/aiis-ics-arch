<!--
File Path: /automation-world/semantic-mapping-agent/src/components/PaginationBar.vue
Description: Shared compact pager for SMA data lists.
Main Features: Displays range, page count, page-size selection, and previous/next controls.
-->
<script setup lang="ts">
import { ConsoleActionButton } from "@aw-ui";
import { computed } from "vue";

import type { LocaleMessages } from "../locales";

const props = withDefaults(defineProps<{
  labels: LocaleMessages;
  page: number;
  pageSize: number;
  total: number;
  busy?: boolean;
  pageSizeOptions?: number[];
}>(), {
  busy: false,
  pageSizeOptions: () => [10, 25, 50],
});

const emit = defineEmits<{
  "update:page": [value: number];
  "update:pageSize": [value: number];
}>();

const pageCount = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)));
const start = computed(() => props.total === 0 ? 0 : (props.page - 1) * props.pageSize + 1);
const end = computed(() => Math.min(props.total, props.page * props.pageSize));

function format(template: string, values: Record<string, number>) {
  return Object.entries(values).reduce((result, [key, value]) => result.replace(`{${key}}`, String(value)), template);
}
</script>

<template>
  <footer v-if="total > pageSize" class="pagination-bar">
    <span>{{ format(labels.paginationRange, { start, end, total }) }}</span>
    <div class="pagination-actions">
      <label class="pagination-size">
        <span>{{ labels.paginationPageSize }}</span>
        <select :value="pageSize" :disabled="busy" @change="emit('update:pageSize', Number(($event.target as HTMLSelectElement).value))">
          <option v-for="option in pageSizeOptions" :key="option" :value="option">{{ option }}</option>
        </select>
      </label>
      <ConsoleActionButton size="small" :disabled="busy || page <= 1" @click="emit('update:page', page - 1)">{{ labels.previousPage }}</ConsoleActionButton>
      <strong>{{ format(labels.paginationPage, { page, pages: pageCount }) }}</strong>
      <ConsoleActionButton size="small" :disabled="busy || page >= pageCount" @click="emit('update:page', page + 1)">{{ labels.nextPage }}</ConsoleActionButton>
    </div>
  </footer>
</template>

<style scoped>
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-width: 0;
  flex-wrap: wrap;
  margin-top: 12px;
  color: var(--agent-text-muted);
  font-size: 12px;
}

.pagination-actions,
.pagination-size {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  flex-wrap: wrap;
}

.pagination-size select {
  min-width: 64px;
  padding: 6px 8px;
  color: var(--agent-text);
  background: var(--agent-surface);
  border: 1px solid var(--agent-border);
  border-radius: 5px;
}

@media (max-width: 980px) {
  .pagination-bar {
    align-items: stretch;
    flex-direction: column;
  }

  .pagination-actions {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .pagination-size,
  .pagination-actions strong {
    grid-column: 1 / -1;
  }

  .pagination-actions button {
    width: 100%;
  }
}
</style>
