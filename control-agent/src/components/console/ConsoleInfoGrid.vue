<!--
  File Path: /control-agent/src/components/console/ConsoleInfoGrid.vue
  Description: Standard read-only detail grid for Control Agent console cards
  Main Features:
    - Wraps Element Plus descriptions with CA-owned detail-grid semantics
    - Removes the old bordered diagnostics-table presentation from pages
    - Supports compact one-column and wider multi-column fact layouts
-->
<template>
  <div class="console-info-grid" :class="{ 'console-info-grid--compact': compact }">
    <el-descriptions :column="column" :size="size">
      <slot />
    </el-descriptions>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    column?: number
    compact?: boolean
    size?: 'small' | 'default' | 'large'
  }>(),
  {
    column: 1,
    compact: false,
    size: 'small'
  }
)
</script>
