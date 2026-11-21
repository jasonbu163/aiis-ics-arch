<!-- 公共状态胶囊：纯展示 tone/label，可追加标记，不推断设备或网络状态。 -->
<template><span class="status-capsule" :class="`status-capsule--${tone}`"><span class="status-dot" aria-hidden="true" /><span class="status-capsule__label">{{ label }}</span><slot /></span></template>
<script setup lang="ts">
import type { UiTone } from '../types'
withDefaults(defineProps<{ label: string; tone?: UiTone }>(), { tone: 'neutral' })
</script>
