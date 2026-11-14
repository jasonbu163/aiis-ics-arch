<!-- 公共语言控件：显示目标语言，标签和目标提示由宿主翻译提供。 -->
<template>
  <button class="aw-language-switch" type="button" :title="label" :aria-label="label" @click="emit('toggle')">
    {{ locale === 'zh-CN' ? enLabel : zhLabel }}
  </button>
</template>
<script setup lang="ts">
defineProps<{ locale: 'zh-CN' | 'en-US'; zhLabel: string; enLabel: string; label: string }>()
const emit = defineEmits<{ toggle: [] }>()
</script>
