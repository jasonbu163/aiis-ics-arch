<!--
  File Path: /control-agent/src/components/console/ConsoleOperationDialog.vue
  Description: CA-owned operation confirmation dialog
  Main Features:
    - Provides a two-segment dialog for high-risk local operations
    - Uses ConsoleActionButton for footer actions
    - Keeps dialog copy in the control-agent i18n namespace
-->
<template>
  <ElDialog
    v-model="visibleModel"
    align-center
    append-to-body
    :close-on-click-modal="!loading"
    :close-on-press-escape="!loading"
    class="console-operation-dialog"
    :show-close="false"
    width="min(520px, calc(100vw - 32px))"
  >
    <template #header>
      <div class="console-operation-dialog__header">
        <h2>{{ t(titleKey) }}</h2>
        <button
          :aria-label="t('common.operationDialog.close')"
          class="console-operation-dialog__close"
          :disabled="loading"
          type="button"
          @click="visibleModel = false"
        >
          <el-icon>
            <Close />
          </el-icon>
        </button>
      </div>
    </template>

    <div class="console-operation-dialog__body">
      <div class="console-operation-dialog__notice" :class="`console-operation-dialog__notice--${tone}`">
        <span class="console-operation-dialog__notice-icon">
          <el-icon>
            <WarningFilled />
          </el-icon>
        </span>
        <p>{{ t(messageKey, messageParams ?? {}) }}</p>
      </div>

      <footer class="console-operation-dialog__footer">
        <ConsoleActionButton
          :disabled="loading"
          :label-key="cancelLabelKey"
          tone="secondary"
          @click="visibleModel = false"
        />
        <ConsoleActionButton
          :disabled="loading"
          :label-key="confirmLabelKey"
          :loading="loading"
          :tone="confirmTone"
          @click="emit('confirm')"
        />
      </footer>
    </div>
  </ElDialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Close, WarningFilled } from '@element-plus/icons-vue'
import { ElDialog } from 'element-plus'
import { useI18n } from 'vue-i18n'
import ConsoleActionButton from './ConsoleActionButton.vue'

const props = withDefaults(
  defineProps<{
    cancelLabelKey: string
    confirmLabelKey: string
    loading?: boolean
    messageKey: string
    messageParams?: Record<string, string | number>
    modelValue: boolean
    titleKey: string
    confirmTone?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger'
    tone?: 'warning' | 'info'
  }>(),
  {
    confirmTone: 'primary',
    loading: false,
    tone: 'warning'
  }
)

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  confirm: []
}>()

const { t } = useI18n()

const visibleModel = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value)
})
</script>
