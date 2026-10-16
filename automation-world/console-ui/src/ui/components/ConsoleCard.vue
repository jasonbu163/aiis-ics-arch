<!-- 公共卡片：复用既有标题、工具、内容、页脚分区；接收宿主文案。 -->
<template>
  <section class="console-card" :class="{ 'console-card--compact': compact }">
    <header class="console-card__header">
      <div class="console-card__title-wrap">
        <span v-if="icon" class="console-card__icon"><ElIcon><component :is="icon" /></ElIcon></span>
        <h2>{{ title }}</h2>
      </div>
      <div v-if="$slots.actions" class="console-card__actions"><slot name="actions" /></div>
    </header>
    <div v-if="$slots.tools" class="console-card__tools"><slot name="tools" /></div>
    <div class="console-card__body"><slot /></div>
    <footer v-if="$slots.footer" class="console-card__footer"><slot name="footer" /></footer>
  </section>
</template>
<script setup lang="ts">
import type { Component } from 'vue'
import { ElIcon } from 'element-plus'
defineProps<{ title: string; icon?: Component; compact?: boolean }>()
</script>
