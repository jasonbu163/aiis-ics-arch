<!-- 当前模式仅作展示；不将模式色解释为设备或上传成功。 -->
<template>
  <StatusCapsule :label="statusText" tone="neutral" />
</template>
<script setup lang="ts">
import { StatusCapsule } from '@aw-ui'
defineProps<{
  statusText: string
}>()
</script>
