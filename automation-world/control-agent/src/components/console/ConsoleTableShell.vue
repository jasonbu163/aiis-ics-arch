<!--
  File Path: /control-agent/src/components/console/ConsoleTableShell.vue
  Description: Lightweight table layout shell for Control Agent console cards
  Main Features:
    - Leaves horizontal scrolling and fixed columns to the table component
    - Moves pagination into a bottom footer segment
    - Keeps the outer ConsoleCard as the only visual card surface
-->
<template>
  <div class="console-table-shell">
    <div class="console-table-shell__scroll">
      <slot />
    </div>

    <footer v-if="pagination" class="console-table-shell__footer">
      <slot name="footer-start" />
      <el-pagination
        v-model:current-page="currentPageModel"
        v-model:page-size="pageSizeModel"
        :layout="layout"
        :page-sizes="pageSizes"
        :total="total"
        size="small"
      />
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    currentPage: number
    layout?: string
    pageSize: number
    pageSizes?: number[]
    pagination?: boolean
    total: number
  }>(),
  {
    layout: 'total, sizes, prev, pager, next',
    pageSizes: () => [5, 10, 15, 20],
    pagination: true
  }
)

const emit = defineEmits<{
  'update:currentPage': [page: number]
  'update:pageSize': [pageSize: number]
}>()

const currentPageModel = computed({
  get: () => props.currentPage,
  set: (page: number) => emit('update:currentPage', page)
})

const pageSizeModel = computed({
  get: () => props.pageSize,
  set: (pageSize: number) => emit('update:pageSize', pageSize)
})
</script>
