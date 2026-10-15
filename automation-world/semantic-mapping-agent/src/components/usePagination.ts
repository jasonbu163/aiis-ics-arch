/**
 * File Path: /automation-world/semantic-mapping-agent/src/components/usePagination.ts
 * Description: Shared client-side pagination state for bounded TSS lists.
 * Main Features: Clamps page state and exposes a stable page slice without mutating source data.
 */
import { computed, ref, watch } from "vue";

export function usePagination<T>(items: () => readonly T[], initialPageSize = 10) {
  const page = ref(1);
  const pageSize = ref(initialPageSize);
  const total = computed(() => items().length);
  const pageCount = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)));
  const pagedItems = computed(() => {
    const start = (page.value - 1) * pageSize.value;
    return items().slice(start, start + pageSize.value);
  });

  watch([total, pageSize], () => {
    page.value = Math.min(Math.max(1, page.value), pageCount.value);
  });

  function setPage(value: number) {
    page.value = Math.min(Math.max(1, value), pageCount.value);
  }

  function setPageSize(value: number) {
    pageSize.value = value;
    page.value = 1;
  }

  return { page, pageSize, total, pageCount, pagedItems, setPage, setPageSize };
}
