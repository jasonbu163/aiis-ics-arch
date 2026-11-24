<!-- CA 应用入口。只有原生端选择旧模式时才加载兼容控制台。 -->
<script setup lang="ts">
import { defineAsyncComponent, onMounted, ref } from 'vue'
import { invoke } from '@tauri-apps/api/core'
import { useI18n } from 'vue-i18n'
import Workspace from './app/flow-editor/Workspace.vue'
const Legacy = defineAsyncComponent(() => import('./app/flow-editor/LegacyConsole.vue'))
const mode = ref('')
const { t } = useI18n()
onMounted(async () => {
  try { mode.value = await invoke<string>('ca_app_mode') }
  catch { mode.value = 'offline' }
})
</script>
<template>
  <Legacy v-if="mode === 'legacy'" />
  <Workspace v-else-if="mode === 'editor' || mode === 'offline'" :offline="mode === 'offline'" />
  <p v-else>{{ t('flow-editor.loading') }}</p>
</template>
