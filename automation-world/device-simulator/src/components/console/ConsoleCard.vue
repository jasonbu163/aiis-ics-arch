<!-- DAA 卡片薄适配：翻译与业务内容布局交给宿主，外观由 CU 公共卡片提供。 -->
<template>
  <CuCard :title="t(titleKey)" :icon="icon" :compact="compact">
    <template v-if="$slots.actions" #actions>
      <slot name="actions" />
    </template>
    <template v-if="$slots.tools" #tools>
      <slot name="tools" />
    </template>
    <div class="ds-card-stack" :class="bodyClass">
      <slot />
    </div>
    <template v-if="$slots.footer" #footer>
      <slot name="footer" />
    </template>
  </CuCard>
</template>
<script setup lang="ts">
import type { Component } from 'vue'
import { useI18n } from 'vue-i18n'
import { ConsoleCard as CuCard } from '@aw-ui'
defineProps<{
  bodyClass?: string
  compact?: boolean
  icon?: Component
  titleKey: string
}>()
const { t } = useI18n()
</script>
