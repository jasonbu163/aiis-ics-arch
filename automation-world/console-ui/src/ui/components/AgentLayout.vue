<!-- 公共壳层：通过插槽组合侧栏、顶栏和内容；主题由宿主显式传入。 -->
<template>
  <div class="aw-ui agent-layout" :data-aw-theme="theme">
    <aside v-if="!sidebarHidden" class="agent-sidebar"><slot name="sidebar" /></aside>
    <div class="agent-workspace">
      <header class="agent-topbar"><slot name="topbar" /></header>
      <main class="agent-main"><slot /></main>
    </div>
  </div>
</template>
<script setup lang="ts">
import type { UiTheme } from '../types'
withDefaults(defineProps<{ theme?: UiTheme; sidebarHidden?: boolean }>(), { theme: 'light', sidebarHidden: false })
</script>
