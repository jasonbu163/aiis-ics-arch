<!-- 文件路径: /frontend-js/src/app/acquisition-data/views/sources/index.vue
     功能描述: 管理员登记、接管或删除 PLC 来源。 -->
<template>
  <div ref="pageRoot" class="page-layout" :style="{ paddingTop: `${pagePadding}px` }">
    <BaseCard>
      <template #title><h3>{{ t('acquisition-data.sourceConfig.title') }}</h3></template>
      <template #actions>
        <ActionButton @click="columns.reset">{{ t('acquisition-data.resetWidths') }}</ActionButton>
        <ActionButton variant="refresh" :loading="loading" @click="load">{{ t('acquisition-data.refresh') }}</ActionButton>
        <ActionButton variant="primary" @click="openNew">{{ t('acquisition-data.sourceConfig.new') }}</ActionButton>
      </template>
      <div v-if="loadError" role="alert">{{ t('acquisition-data.sourceConfig.loadFailed') }}</div>
      <div class="table-scroll">
        <el-table :key="columns.version.value" v-loading="loading" :data="rows" border stripe
          :empty-text="t('acquisition-data.sourceConfig.empty')" @header-dragend="columns.onHeaderDragEnd">
          <el-table-column prop="plcId" :label="t('acquisition-data.sourceConfig.plcId')" :width="columns.widths.plcId" min-width="130" show-overflow-tooltip />
          <el-table-column prop="sourceType" :label="t('acquisition-data.sourceConfig.sourceType')" :width="columns.widths.sourceType" min-width="110">
            <template #default="{ row }">{{ t(`acquisition-data.source.${row.sourceType}`) }}</template>
          </el-table-column>
          <el-table-column prop="instanceId" :label="t('acquisition-data.sourceConfig.instanceId')" :width="columns.widths.instanceId" min-width="130" show-overflow-tooltip />
          <el-table-column prop="sourceGeneration" :label="t('acquisition-data.sourceConfig.generation')" :width="columns.widths.sourceGeneration" min-width="130" show-overflow-tooltip />
          <el-table-column prop="createdAt" :label="t('acquisition-data.sourceConfig.createdAt')" :width="columns.widths.createdAt" min-width="170">
            <template #default="{ row }">{{ formatShanghaiDateTime(row.createdAt) || '—' }}</template>
          </el-table-column>
          <el-table-column :label="t('acquisition-data.columns.actions')" width="320" fixed="right">
            <template #default="{ row }">
              <ActionButton size="small" @click="openEdit(row)">{{ t('acquisition-data.sourceConfig.edit') }}</ActionButton>
              <ActionButton size="small" @click="showParameters(row)">{{ t('acquisition-data.sourceConfig.parameters') }}</ActionButton>
              <ActionButton size="small" :loading="deleting === row.plcId" @click="removeSource(row)">{{ t('acquisition-data.sourceConfig.delete') }}</ActionButton>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <el-pagination v-if="!loadError" :current-page="page" :page-size="pageSize" :total="total"
        :page-sizes="[20, 50, 100]" layout="total, sizes, prev, pager, next"
        @current-change="changePage" @size-change="changeSize" />
    </BaseCard>

    <el-dialog v-model="visible" :title="t(editing ? 'acquisition-data.sourceConfig.editTitle' : 'acquisition-data.sourceConfig.new')" width="min(680px, 95vw)">
      <el-form label-position="top" @submit.prevent="save">
        <div class="source-fields">
          <el-form-item :label="t('acquisition-data.sourceConfig.sourceType')">
            <el-select v-model="draft.sourceType">
              <el-option :label="t('acquisition-data.source.daa')" value="daa" />
              <el-option :label="t('acquisition-data.source.external')" value="external" />
            </el-select>
          </el-form-item>
          <el-form-item :label="t('acquisition-data.sourceConfig.plcId')">
            <el-input v-model="draft.plcId" :disabled="!!editing" />
            <small v-if="editing">{{ t('acquisition-data.sourceConfig.readonly') }}</small>
          </el-form-item>
          <el-form-item :label="t('acquisition-data.sourceConfig.instanceId')">
            <el-input v-model="draft.instanceId" />
          </el-form-item>
          <el-form-item :label="t('acquisition-data.sourceConfig.generation')">
            <el-input v-model="draft.sourceGeneration" />
          </el-form-item>
        </div>
        <div v-if="formError" role="alert" class="source-error">{{ formError }}</div>
        <div class="source-actions">
          <ActionButton @click="visible = false">{{ t('acquisition-data.sourceConfig.cancel') }}</ActionButton>
          <ActionButton variant="primary" :loading="saving" @click="save">{{ t('acquisition-data.sourceConfig.save') }}</ActionButton>
        </div>
      </el-form>
    </el-dialog>
    <el-dialog v-model="parametersVisible" :title="t('acquisition-data.sourceConfig.parameters')" width="min(680px, 95vw)">
      <el-input ref="parametersInput" :model-value="parameters" type="textarea" :rows="8" readonly />
      <template #footer>
        <ActionButton @click="copyParameters">{{ t('acquisition-data.sourceConfig.copy') }}</ActionButton>
        <ActionButton @click="parametersVisible = false">{{ t('acquisition-data.close') }}</ActionButton>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import { formatShanghaiDateTime } from '@/utils/date'
import { useTableColumnWidths } from '@/utils/tableColumnWidths'
import { createSource, getSources, updateSource } from '../../api/index'

const { t } = useI18n()
const pageRoot = ref(null)
const pagePadding = ref(0)
const rows = ref([])
const page = ref(1)
const pageSize = ref(50)
const total = ref(0)
const loading = ref(false)
const loadError = ref(false)
const saving = ref(false)
const deleting = ref('')
const visible = ref(false)
const editing = ref(null)
const formError = ref('')
const parametersVisible = ref(false)
const parameters = ref('')
const parametersInput = ref(null)
const draft = reactive({ sourceType: 'daa', plcId: '', instanceId: '', sourceGeneration: '' })
const columns = useTableColumnWidths('acquisition-data.sources', {
  plcId: { width: 180, minWidth: 130 }, sourceType: { width: 130, minWidth: 110 },
  instanceId: { width: 180, minWidth: 130 }, sourceGeneration: { width: 180, minWidth: 130 },
  createdAt: { width: 190, minWidth: 170 }
})
// Match backend edge whitespace; /u rejects lone surrogates but accepts valid pairs.
const validId = value => {
  return typeof value === 'string' && !!value &&
    !/[\u0000-\u001f\u007f\uD800-\uDFFF]|^\p{White_Space}|\p{White_Space}$/u.test(value) &&
    new TextEncoder().encode(value).length <= 128
}
let requestSequence = 0
let observer

async function load() {
  const current = ++requestSequence
  loading.value = true
  loadError.value = false
  try {
    const data = await getSources({ page: page.value, pageSize: pageSize.value })
    if (current !== requestSequence) return
    rows.value = data.items
    total.value = data.total
  } catch {
    if (current === requestSequence) loadError.value = true
  } finally {
    if (current === requestSequence) loading.value = false
  }
}
function changePage(value) { page.value = value; load() }
function changeSize(value) { pageSize.value = value; page.value = 1; load() }
function openNew() {
  editing.value = null
  Object.assign(draft, { sourceType: 'daa', plcId: '', instanceId: '', sourceGeneration: '' })
  formError.value = ''
  visible.value = true
}
function openEdit(row) {
  editing.value = row
  Object.assign(draft, { sourceType: row.sourceType, plcId: row.plcId, instanceId: row.instanceId,
    sourceGeneration: row.sourceGeneration })
  formError.value = ''
  visible.value = true
}
function showParameters(row) {
  parameters.value = JSON.stringify({ instanceId: row.instanceId, plcId: row.plcId,
    sourceGeneration: row.sourceGeneration }, null, 2)
  parametersVisible.value = true
}
async function copyParameters() {
  try {
    await navigator.clipboard.writeText(parameters.value)
    ElMessage.success(t('acquisition-data.sourceConfig.copied'))
  } catch {
    parametersInput.value?.textarea?.select()
    ElMessage.warning(t('acquisition-data.sourceConfig.copyFailed'))
  }
}
async function removeSource(row) {
  if (deleting.value) return
  try {
    await ElMessageBox.confirm(t('acquisition-data.sourceConfig.deleteNotice', { plcId: row.plcId }),
      t('acquisition-data.sourceConfig.deleteTitle'), {
        confirmButtonText: t('acquisition-data.sourceConfig.deleteConfirm'),
        cancelButtonText: t('acquisition-data.sourceConfig.cancel'), type: 'warning'
      })
  } catch { return }
  deleting.value = row.plcId
  try {
    await updateSource({ action: 'delete', plcId: row.plcId,
      expected: { instanceId: row.instanceId, sourceGeneration: row.sourceGeneration,
        registrationRevision: row.registrationRevision }, confirmDelete: true })
    ElMessage.success(t('acquisition-data.sourceConfig.deleted'))
    if (rows.value.length === 1 && page.value > 1) page.value--
    await load()
  } catch (error) {
    const code = error?.response?.data?.errorCode
    const status = error?.response?.status
    const message = code === 'acquisition_sources.not_ready' ? 'notReady'
      : status === 409 ? 'conflict' : status === 404 ? 'deleteMissing' : 'deleteUnknown'
    ElMessage.error(t(`acquisition-data.sourceConfig.${message}`))
    if (status === 409 || status === 404 || message === 'deleteUnknown') await load()
  } finally { deleting.value = '' }
}
async function save() {
  if (saving.value) return
  if (![draft.plcId, draft.instanceId, draft.sourceGeneration].every(validId)) {
    formError.value = t('acquisition-data.sourceConfig.invalid')
    return
  }
  const before = editing.value
  const takeover = before && (before.instanceId !== draft.instanceId ||
    before.sourceGeneration !== draft.sourceGeneration)
  if (takeover) {
    try {
      await ElMessageBox.confirm(t('acquisition-data.sourceConfig.takeoverNotice', {
        plcId: before.plcId, oldType: t(`acquisition-data.source.${before.sourceType}`),
        oldInstance: before.instanceId, oldGeneration: before.sourceGeneration,
        newType: t(`acquisition-data.source.${draft.sourceType}`),
        newInstance: draft.instanceId, newGeneration: draft.sourceGeneration
      }), t('acquisition-data.sourceConfig.takeoverTitle'), {
        confirmButtonText: t('acquisition-data.sourceConfig.confirm'), cancelButtonText: t('acquisition-data.sourceConfig.cancel'), type: 'warning'
      })
    } catch { return }
  }
  const body = before ? {
    action: takeover ? 'takeover' : 'edit', plcId: before.plcId,
    expected: { instanceId: before.instanceId, sourceGeneration: before.sourceGeneration, registrationRevision: before.registrationRevision },
    ...(takeover ? { replacement: { sourceType: draft.sourceType, instanceId: draft.instanceId,
      sourceGeneration: draft.sourceGeneration }, confirmTakeover: true } : { sourceType: draft.sourceType })
  } : { sourceType: draft.sourceType, plcId: draft.plcId, instanceId: draft.instanceId,
    sourceGeneration: draft.sourceGeneration }
  saving.value = true
  formError.value = ''
  try {
    await (before ? updateSource(body) : createSource(body))
    visible.value = false
    ElMessage.success(t('acquisition-data.sourceConfig.saved'))
    await load()
  } catch (error) {
    const messages = {
      'acquisition_sources.not_ready': 'notReady',
      'acquisition_sources.commit_outcome_unknown': 'saveFailed',
      'acquisition_sources.generation_reused': 'generationReused',
      'acquisition_sources.source_conflict': 'sourceConflict',
      'acquisition_sources.revision_conflict': 'conflict',
      'acquisition_sources.invalid_request': 'invalid'
    }
    const message = messages[error?.response?.data?.errorCode] || (error?.response?.status === 409 ? 'conflict' : 'saveFailed')
    formError.value = t(`acquisition-data.sourceConfig.${message}`)
    if (error?.response?.status === 409) await load()
  } finally { saving.value = false }
}
onMounted(() => {
  const main = pageRoot.value?.closest('main')
  const header = main?.parentElement?.querySelector('header.header')
  if (main && header) {
    const update = () => { pagePadding.value = Math.max(0, Math.ceil(header.getBoundingClientRect().bottom - pageRoot.value.getBoundingClientRect().top - main.scrollTop + 8)) }
    observer = new ResizeObserver(update)
    observer.observe(main); observer.observe(header); observer.observe(pageRoot.value)
    update()
  }
  load()
})
onBeforeUnmount(() => { requestSequence++; observer?.disconnect() })
</script>

<style scoped>
.source-fields { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 16px; }
.source-fields small { display: block; width: 100%; color: var(--el-text-color-secondary); }
.source-actions { display: flex; justify-content: flex-end; gap: 8px; }
.source-error { color: var(--el-color-danger); margin-bottom: 12px; }
.table-scroll { overflow-x: auto; }
@media (max-width: 620px) { .source-fields { grid-template-columns: minmax(0, 1fr); } }
</style>
