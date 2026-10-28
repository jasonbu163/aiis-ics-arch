<!-- 历史迁入摘要兼容组件，普通页面不挂接；仅消费显式传入的只读摘要。 -->
<template>
  <el-dialog v-if="attention && summary" :model-value="modelValue" :title="t('common.local.migration.title')" width="560px" class="standard-form-dialog" append-to-body destroy-on-close @update:model-value="$emit('update:modelValue', $event)">
    <div class="console-stack">
      <el-alert :title="t(unknown ? 'common.local.migration.persistenceUnknown' : 'common.local.migration.failed')" type="warning" :closable="false" show-icon />
      <p v-if="summary.errorCode">{{ te(`common.local.codes.${summary.errorCode}`) ? t(`common.local.codes.${summary.errorCode}`) : t('common.local.code', { code: summary.errorCode }) }}</p>
    </div>
    <template #footer>
      <ConsoleActionButton label-key="common.local.migration.close" @click="$emit('update:modelValue', false)" />
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { MigrationSummary } from '../../services/localAcquisition'
import ConsoleActionButton from './ConsoleActionButton.vue'
const props = defineProps<{ modelValue: boolean; summary: MigrationSummary | null }>()
defineEmits<{ 'update:modelValue': [value: boolean] }>()
const { t, te } = useI18n()
const unknown = computed(() => props.summary?.statusPersistence === 'unknown')
const attention = computed(() => unknown.value || props.summary?.status === 'failed')
</script>
