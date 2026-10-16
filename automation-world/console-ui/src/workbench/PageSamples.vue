<!-- CU 私有页面设计样例：Element Plus 列表/校验表单/弹窗，仅内存演示；不进入公共出口。 -->
<template>
  <section class="workbench-samples" :aria-label="t('workbench.pageSamples.pages')">
    <ConsoleCard :title="t('workbench.pageSamples.listTitle')">
      <template #tools>
        <ElRadioGroup v-model="state" :aria-label="t('workbench.pageSamples.state')">
          <ElRadioButton v-for="value in states" :key="value" :value="value">{{ t(`workbench.pageSamples.${value}`) }}</ElRadioButton>
        </ElRadioGroup>
      </template>
      <div class="aw-page-state" :aria-busy="state === 'loading'" aria-live="polite">
        <p v-if="state === 'loading'">{{ t('workbench.pageSamples.loadingNote') }}</p>
        <ElEmpty v-else-if="state === 'empty'" :description="t('workbench.pageSamples.emptyNote')" />
        <div v-else-if="state === 'error'">
          <p>{{ t('workbench.pageSamples.errorNote') }}</p>
          <ConsoleActionButton :label="t('workbench.pageSamples.retry')" @click="state = 'normal'; feedback = 'retried'" />
        </div>
        <ElTable v-else class="aw-data-table" :data="rows" stripe>
          <ElTableColumn :label="t('workbench.pageSamples.name')" min-width="160"><template #default="{ row }">{{ row.name || t(`workbench.pageSamples.${row.key}`) }}</template></ElTableColumn>
          <ElTableColumn :label="t('workbench.pageSamples.kind')" min-width="120"><template #default="{ row }">{{ t(`workbench.pageSamples.${row.kind}`) }}</template></ElTableColumn>
          <ElTableColumn :label="t('workbench.pageSamples.actions')" width="160"><template #default="{ row }"><ConsoleActionButton size="small" :label="t('workbench.pageSamples.edit')" @click="openEditor(row.key)" /></template></ElTableColumn>
        </ElTable>
      </div>
      <p v-if="feedback" class="workbench-feedback" role="status">{{ t(`workbench.pageSamples.${feedback}`) }}</p>
      <template #footer>{{ t('workbench.footer') }}</template>
    </ConsoleCard>
    <ConsoleCard :title="t('workbench.pageSamples.formTitle')">
      <ElForm ref="formRef" class="aw-sample-form" :model="form" :rules="rules" label-position="top" @submit.prevent="submitPreview">
        <ElFormItem prop="name" :label="t('workbench.pageSamples.name')"><ElInput v-model="form.name" :placeholder="t('workbench.pageSamples.nameHint')" /></ElFormItem>
        <ElFormItem prop="kind" :label="t('workbench.pageSamples.kind')"><ElSelect v-model="form.kind" :teleported="false"><ElOption v-for="kind in kinds" :key="kind" :value="kind" :label="t(`workbench.pageSamples.${kind}`)" /></ElSelect></ElFormItem>
        <div class="aw-form-actions"><ConsoleActionButton tone="primary" :label="t('workbench.pageSamples.submit')" @click="submitPreview" /><ConsoleActionButton :label="t('workbench.pageSamples.reset')" @click="formRef?.resetFields(); formFeedback = 'resetDone'" /></div>
      </ElForm>
      <p v-if="formFeedback" class="workbench-feedback" role="status">{{ t(`workbench.pageSamples.${formFeedback}`) }}</p>
      <template #footer>{{ t('workbench.footer') }}</template>
    </ConsoleCard>
  </section>
  <Teleport to="body">
    <div class="aw-ui aw-sample-overlays" :data-aw-theme="theme" :style="previewVariables">
      <ElDialog v-model="dialogOpen" :title="t('workbench.pageSamples.dialogTitle')" :append-to-body="false" width="min(480px, 90vw)" :close-on-click-modal="false" @closed="editRef?.clearValidate()">
        <p>{{ t('workbench.pageSamples.dialogNote') }}</p>
        <ElForm ref="editRef" class="aw-sample-form" :model="draft" :rules="rules" label-position="top" @submit.prevent="confirmEdit">
          <ElFormItem prop="name" :label="t('workbench.pageSamples.name')"><ElInput v-model="draft.name" /></ElFormItem>
          <ElFormItem prop="kind" :label="t('workbench.pageSamples.kind')"><ElSelect v-model="draft.kind" :teleported="false"><ElOption v-for="kind in kinds" :key="kind" :value="kind" :label="t(`workbench.pageSamples.${kind}`)" /></ElSelect></ElFormItem>
        </ElForm>
        <template #footer><div class="aw-form-actions"><ConsoleActionButton :label="t('workbench.pageSamples.cancel')" @click="dialogOpen = false; feedback = 'cancelled'" /><ConsoleActionButton tone="primary" :label="t('workbench.pageSamples.confirm')" @click="confirmEdit" /></div></template>
      </ElDialog>
    </div>
  </Teleport>
</template>
<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElDialog, ElEmpty, ElForm, ElFormItem, ElInput, ElOption, ElRadioButton, ElRadioGroup, ElSelect, ElTable, ElTableColumn, type FormInstance, type FormRules } from 'element-plus'
import { ConsoleActionButton, ConsoleCard, type UiTheme } from '../ui'
defineProps<{ theme: UiTheme; previewVariables: Record<string, string> }>()
const { t, locale } = useI18n()
const states = ['normal', 'loading', 'empty', 'error'] as const
const kinds = ['standard', 'compact'] as const
const state = ref<(typeof states)[number]>('normal')
const rows = ref([{ key: 'alpha', name: '', kind: 'standard' }, { key: 'beta', name: '', kind: 'compact' }, { key: 'gamma', name: '', kind: 'standard' }])
const form = reactive({ name: '', kind: 'standard' })
const draft = reactive({ name: '', kind: 'standard' })
const formRef = ref<FormInstance>()
const editRef = ref<FormInstance>()
const rules = computed<FormRules>(() => ({ name: [{ required: true, whitespace: true, message: t('workbench.pageSamples.required'), trigger: 'blur' }, { min: 2, max: 24, message: t('workbench.pageSamples.length'), trigger: 'blur' }], kind: [{ required: true, message: t('workbench.pageSamples.kindRequired'), trigger: 'change' }] }))
const dialogOpen = ref(false)
const editingKey = ref('')
const feedback = ref('')
const formFeedback = ref('')
watch(locale, () => { formRef.value?.clearValidate(); editRef.value?.clearValidate() })
async function submitPreview() {
  if (!await formRef.value?.validate().catch(() => false)) return
  rows.value[0] = { ...rows.value[0], name: form.name.trim(), kind: form.kind }
  formFeedback.value = 'submitted'
}
function openEditor(key: string) {
  const row = rows.value.find(item => item.key === key)
  if (!row) return
  editingKey.value = row.key
  Object.assign(draft, { name: row.name || t(`workbench.pageSamples.${row.key}`), kind: row.kind })
  dialogOpen.value = true
}
async function confirmEdit() {
  if (!await editRef.value?.validate().catch(() => false)) return
  const row = rows.value.find(item => item.key === editingKey.value)
  if (row) Object.assign(row, { name: draft.name.trim(), kind: draft.kind })
  dialogOpen.value = false
  feedback.value = 'edited'
}
</script>
