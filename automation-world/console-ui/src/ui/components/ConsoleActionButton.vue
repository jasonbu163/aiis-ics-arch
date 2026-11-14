<!-- 公共动作按钮：复用 Element Plus，支持普通文案和圆形图标模式。 -->
<template>
  <ElButton class="console-action-button" :class="[`console-action-button--${size}`, { 'console-action-button--round-icon': roundIcon }]" :type="tone === 'secondary' ? 'default' : tone" :size="size" :disabled="disabled" :loading="loading" :title="roundIcon ? (title || label) : title" :aria-label="roundIcon ? (label || title) : undefined" @click="emit('click', $event)">
    <template v-if="icon" #icon><ElIcon :size="roundIcon ? 20 : undefined" :aria-hidden="roundIcon ? 'true' : undefined"><component :is="icon" /></ElIcon></template>
    <template v-if="roundIcon" #loading><ElIcon class="is-loading" :size="20" aria-hidden="true"><Loading /></ElIcon></template>
    <template v-if="!roundIcon" #default><slot>{{ label }}</slot></template>
  </ElButton>
</template>
<script setup lang="ts">
import type { Component } from 'vue'
import { ElButton, ElIcon } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import type { ActionTone } from '../types'
withDefaults(defineProps<{ label?: string; title?: string; icon?: Component; tone?: ActionTone; size?: 'large' | 'small'; disabled?: boolean; loading?: boolean; roundIcon?: boolean }>(), { tone: 'secondary', size: 'large' })
const emit = defineEmits<{ click: [event: MouseEvent] }>()
</script>
