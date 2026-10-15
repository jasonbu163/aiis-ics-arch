<!--
  File Path: /control-agent/src/components/console/ConsoleMetricCard.vue
  Description: Standard metric card for Control Agent console pages
  Main Features:
    - Renders featured and compact metric values with one CA-owned grammar
    - Keeps metric labels behind the control-agent i18n namespace
    - Provides stable overflow behavior for dense operations-console layouts
-->
<template>
  <article class="console-metric-card" :class="{ 'console-metric-card--featured': featured }">
    <header class="console-metric-card__header">
      <span class="console-metric-card__label">{{ t(labelKey) }}</span>
    </header>
    <div class="console-metric-card__content">
      <strong class="console-metric-card__value">{{ value }}</strong>
      <small v-if="detail" class="console-metric-card__detail">{{ detail }}</small>
    </div>
  </article>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

defineProps<{
  detail?: string
  featured?: boolean
  labelKey: string
  value: string
}>()

const { t } = useI18n()
</script>
