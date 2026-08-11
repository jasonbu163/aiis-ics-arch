<!--
  File Path: /control-agent/src/components/console/ReadinessGrid.vue
  Description: Readiness-state grid for Control Agent operational gates
  Main Features:
    - Renders ready/observing/locked/blocked states consistently
    - Uses CA-local operation item data
    - Keeps static labels in the i18n namespace
-->
<template>
  <div class="readiness-grid" :aria-label="t(accessibilityLabelKey)">
    <article
      v-for="item in items"
      :key="item.key"
      class="readiness-item"
      :class="`readiness-item-${item.tone}`"
    >
      <span>{{ t(item.labelKey) }}</span>
      <strong>{{ item.stateText }}</strong>
      <p>{{ item.detailText }}</p>
    </article>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { OperationItem } from '../../console/types'

defineProps<{
  accessibilityLabelKey: string
  items: OperationItem[]
}>()

const { t } = useI18n()
</script>
