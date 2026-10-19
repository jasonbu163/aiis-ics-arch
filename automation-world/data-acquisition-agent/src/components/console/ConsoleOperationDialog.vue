<!-- 既有全体操作确认：Element Plus 弹层留在宿主显式 CU 主题作用域。 -->
<template>
  <ElDialog
    v-model="visibleModel"
    :title="t(titleKey)"
    align-center
    :append-to-body="false"
    :close-on-click-modal="!loading"
    :close-on-press-escape="!loading"
    :show-close="!loading"
    width="min(520px, calc(100vw
    - 32px))"
  >
    <p class="daa-confirm-message">
      {{ t(messageKey,messageParams??{}) }}
    </p>
    <template #footer>
      <div class="aw-form-actions">
        <ConsoleActionButton :disabled="loading" :label-key="cancelLabelKey" @click="visibleModel=false" />
        <ConsoleActionButton
          :disabled="loading"
          :label-key="confirmLabelKey"
          :loading="loading"
          :tone="confirmTone"
          @click="emit('confirm')"
        />
      </div>
    </template>
  </ElDialog>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import { ElDialog } from 'element-plus'
import { useI18n } from 'vue-i18n'
import ConsoleActionButton from './ConsoleActionButton.vue'
const props = withDefaults(defineProps<{
  cancelLabelKey: string
  confirmLabelKey: string
  loading?: boolean
  messageKey: string
  messageParams?: Record<string, string | number>
  modelValue: boolean
  titleKey: string
  confirmTone?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger'
  tone?: 'warning' | 'info'
}>(), { confirmTone: 'primary', loading: false, tone: 'warning' })
const emit = defineEmits<{
  'update:modelValue': [
    value: boolean
  ]
  confirm: []
}>()
const { t } = useI18n()
const visibleModel = computed({ get: () => props.modelValue, set: (v: boolean) => emit('update:modelValue', v) })
</script>
