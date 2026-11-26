<!-- SMA 业务弹窗采用共享主题、独立滚动正文及可见的操作页脚。 -->
<script setup lang="ts">
import { ElDialog } from "element-plus";

defineProps<{ title: string; error?: string; compact?: boolean }>();
const open = defineModel<boolean>({ required: true });
</script>

<template>
  <ElDialog v-model="open" :title="title" append-to="#sma-overlays" align-center
    :close-on-click-modal="true" :show-close="!compact"
    class="sma-dialog standard-form-dialog compact-form-dialog sma-http-dialog" :class="{ 'sma-http-dialog--compact': compact }">
    <template #header="{ titleId, titleClass }">
      <h2 :id="titleId" :class="titleClass">{{ title }}</h2>
    </template>
    <p v-if="error" class="warning http-dialog-error" role="alert">{{ error }}</p>
    <slot />
    <template #footer><div class="action-row"><slot name="footer" /></div></template>
  </ElDialog>
</template>
