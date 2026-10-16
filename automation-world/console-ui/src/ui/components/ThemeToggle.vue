<!-- 公共主题控件：呈现宿主主题与目标提示，仅发出切换请求。 -->
<template>
  <button class="aw-theme-toggle" :class="{ 'is-dark': theme === 'dark' }" type="button" :title="label" :aria-label="label" :aria-pressed="theme === 'dark'" @click="emit('toggle')">
    <ElIcon :size="20" aria-hidden="true"><Moon /></ElIcon>
  </button>
</template>
<script setup lang="ts">
import { ElIcon } from 'element-plus'
import { Moon } from '@element-plus/icons-vue'
import type { UiTheme } from '../types'
defineProps<{ theme: UiTheme; label: string }>()
const emit = defineEmits<{ toggle: [] }>()
</script>
