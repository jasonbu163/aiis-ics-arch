<!-- 配置删除只在显式确认后提交，关闭或点击遮罩取消。 -->
<script setup lang="ts">
import { ConsoleActionButton } from "@aw-ui";
import { useHttpMessages } from "../messages";
import SmaDialog from "./SmaDialog.vue";

defineProps<{ name: string; busy: boolean; error: string }>();
const emit = defineEmits<{ confirm: [] }>();
const open = defineModel<boolean>({ required: true });
const ui = useHttpMessages();
</script>

<template>
  <SmaDialog v-model="open" :title="ui.deleteTitle" :error="error">
    <p>{{ ui.deleteConfirm.replace('{name}', name) }}</p>
    <template #footer>
      <ConsoleActionButton @click="open = false">{{ ui.cancel }}</ConsoleActionButton>
      <ConsoleActionButton tone="danger" :loading="busy" @click="emit('confirm')">{{ ui.remove }}</ConsoleActionButton>
    </template>
  </SmaDialog>
</template>
