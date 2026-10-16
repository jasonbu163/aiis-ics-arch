<!-- 公共侧栏：只接收已翻译导航与品牌文案，通过事件返回选择。 -->
<template>
  <div class="agent-sidebar-shell">
    <ElMenu :default-active="activeId" class="agent-menu" @select="emit('select', $event)">
      <ElMenuItem v-for="item in items" :key="item.id" :index="item.id">
        <ElIcon v-if="item.icon"><component :is="item.icon" /></ElIcon>
        <span>{{ item.label }}</span>
      </ElMenuItem>
    </ElMenu>
    <div class="sidebar-footer-brand"><strong>{{ brand }}</strong><small>{{ detail }}</small></div>
  </div>
</template>
<script setup lang="ts">
import { ElIcon, ElMenu, ElMenuItem } from 'element-plus'
import type { NavigationItem } from '../types'
defineProps<{ activeId: string; items: NavigationItem[]; brand: string; detail?: string }>()
const emit = defineEmits<{ select: [id: string] }>()
</script>
