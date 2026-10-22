<!-- DAA 动作薄适配：保留原事件/禁用/翻译合同，尺寸外观由 CU 提供。 -->
<template>
  <CuAction
    :label="labelKey ? t(labelKey)
    : ''"
    :icon="icon"
    :disabled="disabled"
    :loading="loading"
    :size="size"
    :title="title"
    :tone="tone"
    @click="emit('click', $event)"
  >
    <slot>
      {{ labelKey ? t(labelKey) : '' }}
    </slot>
  </CuAction>
</template>
<script setup lang="ts">
import type { Component } from 'vue'
import { useI18n } from 'vue-i18n'
import { ConsoleActionButton as CuAction, type ActionTone } from '@aw-ui'
withDefaults(defineProps<{
  disabled?: boolean
  icon?: Component
  labelKey?: string
  loading?: boolean
  size?: 'small' | 'large'
  title?: string
  tone?: ActionTone
}>(), { size: 'large', tone: 'secondary' })
const emit = defineEmits<{
  click: [
    event: MouseEvent
  ]
}>()
const { t } = useI18n()
</script>
