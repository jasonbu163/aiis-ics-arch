<!-- 计划与实绩列表的本地字段管理弹窗。 -->
<template>
  <el-dialog v-model="open" :title="t(`${kind}.workflow.fieldSettings`)" width="calc(100% - 32px)" align-center destroy-on-close class="standard-form-dialog task-field-config-dialog">
    <TaskFieldEditor :kind="kind" :module="kind" :api="api" @cancel="open = false" @saved="closeAfterSave" @deleted="emit('saved')" />
  </el-dialog>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import TaskFieldEditor from './TaskFieldEditor.vue'

defineProps({ kind: { type: String, required: true }, api: { type: Object, required: true } })
const { t } = useI18n()
const open = defineModel({ type: Boolean, default: false })
const emit = defineEmits(['saved'])

function closeAfterSave() {
  open.value = false
  emit('saved')
}
</script>

<style scoped>
/* 宽表弹窗保留标准外壳，但独立限制尺寸和内部滚动。 */
:global(.standard-form-dialog.task-field-config-dialog.el-dialog) { max-width: min(1400px, calc(100vw - 32px)); max-height: calc(100vh - 32px); max-height: calc(100dvh - 32px); display: flex; flex-direction: column; }
:global(.standard-form-dialog.task-field-config-dialog .el-dialog__header) { flex: 0 0 auto; }
:global(.standard-form-dialog.task-field-config-dialog .el-dialog__body) { min-height: 0; overflow-y: auto; }
@media (max-width: 600px) {
  :global(.standard-form-dialog.task-field-config-dialog .el-dialog__header) { min-height: 64px; padding: 20px 24px; }
  :global(.standard-form-dialog.task-field-config-dialog .el-dialog__body) { padding: 16px; }
}
</style>
