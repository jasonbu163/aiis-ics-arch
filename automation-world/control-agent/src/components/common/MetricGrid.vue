<!--
  File Path: /control-agent/src/components/common/MetricGrid.vue
  Description: Shared metric grid for Control Agent overview panels
  Main Features:
    - Renders a featured runtime or collector card
    - Renders compact metric tiles from CA-local data
    - Keeps labels behind the control-agent i18n namespace
-->
<template>
  <div
    class="metric-grid"
    :class="{ 'collection-metric-grid': collection }"
    :aria-label="t(accessibilityLabelKey)"
  >
    <ConsoleMetricCard
      class="runtime-card"
      featured
      :detail="featuredDetail"
      :label-key="featuredLabelKey"
      :value="featuredValue"
    />
    <ConsoleMetricCard
      v-for="item in items"
      :key="item.key"
      class="metric-tile"
      :label-key="item.labelKey"
      :value="item.value"
    />
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import ConsoleMetricCard from '../console/ConsoleMetricCard.vue'
import type { MetricItem } from '../../console/types'

defineProps<{
  accessibilityLabelKey: string
  collection?: boolean
  featuredDetail: string
  featuredLabelKey: string
  featuredValue: string
  items: MetricItem[]
}>()

const { t } = useI18n()
</script>
