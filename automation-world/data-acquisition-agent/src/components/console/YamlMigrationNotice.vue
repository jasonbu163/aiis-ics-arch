<!-- 当前迁入故障小弹窗：仅消费同一owner的权威摘要与原安全重试，不展示迁入历史。 -->
<template>
  <el-dialog v-if="attention && local?.migration" :model-value="modelValue" :title="t('common.local.migration.title')" width="560px" class="standard-form-dialog" append-to-body destroy-on-close @update:model-value="$emit('update:modelValue', $event)">
    <div class="console-stack">
      <el-alert :title="t(unknown ? 'common.local.migration.persistenceUnknown' : 'common.local.migration.failed')" type="warning" :closable="false" show-icon />
      <p v-if="local.migration.errorCode">{{ local.label(local.migration.errorCode) }}</p>
      <p v-if="!unknown && (local.dirty || local.editing)">{{ t('common.local.migration.unsaved') }}</p>
    </div>
    <template #footer>
      <ConsoleActionButton label-key="common.local.migration.close" @click="$emit('update:modelValue', false)" />
      <ConsoleActionButton v-if="!unknown && local.migration.retryAllowed" label-key="common.local.migration.retry" :disabled="local.busy || local.dirty || local.editing" @click="local.retryMigration()" />
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { computed, inject } from 'vue'
import { useI18n } from 'vue-i18n'
import { localConsoleKey } from '../../console/composables/useLocalAcquisitionConsole'
import ConsoleActionButton from './ConsoleActionButton.vue'
defineProps<{ modelValue: boolean }>()
defineEmits<{ 'update:modelValue': [value: boolean] }>()
const local = inject(localConsoleKey)
const { t } = useI18n()
const unknown = computed(() => local?.migration?.statusPersistence === 'unknown')
const attention = computed(() => unknown.value || (local?.migration?.status === 'failed' && local.migration.retryAllowed === true))
</script>
