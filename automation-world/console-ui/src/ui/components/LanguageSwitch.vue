<!-- 公共语言控件：高亮宿主语言，标签和目标提示由宿主翻译提供。 -->
<template>
  <button class="aw-language-switch" type="button" :title="label" :aria-label="label" @click="emit('toggle')">
    <span class="aw-language-switch__text" :class="{ 'is-active': locale === 'zh-CN' }">{{ zhLabel }}</span>
    <span class="aw-language-switch__divider" aria-hidden="true">/</span>
    <span class="aw-language-switch__text" :class="{ 'is-active': locale === 'en-US' }">{{ enLabel }}</span>
  </button>
</template>
<script setup lang="ts">
defineProps<{ locale: 'zh-CN' | 'en-US'; zhLabel: string; enLabel: string; label: string }>()
const emit = defineEmits<{ toggle: [] }>()
</script>
