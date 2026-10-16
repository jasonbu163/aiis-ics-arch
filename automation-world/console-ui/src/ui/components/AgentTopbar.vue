<!-- 公共顶栏：文案和动作由宿主提供，不依赖 i18n 实例或运行时。 -->
<template>
  <div class="agent-topbar-shell">
    <div class="topbar-left">
      <button class="sidebar-toggle-button" type="button" :aria-label="sidebarLabel" :aria-pressed="sidebarHidden" @click="emit('toggle-sidebar')">
        <ElIcon><Expand v-if="sidebarHidden" /><Fold v-else /></ElIcon>
      </button>
      <div class="topbar-title"><h1>{{ title }}</h1><p v-if="subtitle">{{ subtitle }}</p></div>
    </div>
    <div class="topbar-actions"><slot name="actions" /></div>
  </div>
</template>
<script setup lang="ts">
import { ElIcon } from 'element-plus'
import { Expand, Fold } from '@element-plus/icons-vue'
defineProps<{ title: string; subtitle?: string; sidebarLabel: string; sidebarHidden?: boolean }>()
const emit = defineEmits<{ 'toggle-sidebar': [] }>()
</script>
