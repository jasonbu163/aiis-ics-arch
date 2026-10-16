<!-- 公共动作按钮：复用 Element Plus，文案通过 slot 或 label 提供。 -->
<template>
  <ElButton class="console-action-button" :class="`console-action-button--${size}`" :type="tone === 'secondary' ? 'default' : tone" :size="size" :disabled="disabled" :loading="loading" :title="title" @click="emit('click', $event)">
    <template v-if="icon" #icon><ElIcon><component :is="icon" /></ElIcon></template>
    <slot>{{ label }}</slot>
  </ElButton>
</template>
<script setup lang="ts">
import type { Component } from 'vue'
import { ElButton, ElIcon } from 'element-plus'
import type { ActionTone } from '../types'
withDefaults(defineProps<{ label?: string; title?: string; icon?: Component; tone?: ActionTone; size?: 'large' | 'small'; disabled?: boolean; loading?: boolean }>(), { tone: 'secondary', size: 'large' })
const emit = defineEmits<{ click: [event: MouseEvent] }>()
</script>
