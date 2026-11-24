<!-- 计划、实绩本地字段与共享字段复用的主表和配置操作。 -->
<template>
  <div ref="pageRoot" class="shared-field-page" :style="{ paddingTop: `${pagePadding}px` }">
    <BaseCard>
      <template #title>
        <h3 class="card-title">{{ tr(isLocal ? 'local.title' : 'sharedFieldSettings') }}</h3>
        <el-tooltip placement="bottom-start" :trigger="['hover', 'focus']" :trigger-keys="[]">
          <template #content><div class="help-content">{{ tr(isLocal ? 'local.help' : 'shared.help') }}</div></template>
          <button class="help-trigger" type="button" :aria-label="tr(isLocal ? 'local.helpLabel' : 'shared.helpLabel')"
            @click="$event.currentTarget.focus()" @keydown.esc.stop="$event.currentTarget.blur()">
            <el-icon><QuestionFilled /></el-icon>
          </button>
        </el-tooltip>
      </template>
      <template #actions>
        <div class="table-actions">
          <ActionButton v-if="isLocal" :disabled="busy" @click="router.push(`/${module}/list`)">{{ tr('local.back') }}</ActionButton>
          <span v-if="config" class="card-status-pill">{{ tr('configVersion') }} {{ config.configVersion }} / {{ tr('revision') }} {{ config.configRevision }}</span>
          <ActionButton variant="primary" :disabled="!config || loading" @click="addField">{{ tr('addField') }}</ActionButton>
          <el-tooltip :content="tr('resetWidthsHint')" :trigger="['hover', 'focus']">
            <ActionButton @click="columns.reset">{{ tr('resetWidths') }}</ActionButton>
          </el-tooltip>
          <ActionButton :loading="loading" @click="load">{{ tr('refresh') }}</ActionButton>
        </div>
      </template>

      <el-form class="shared-filters" :class="{ 'shared-filters--plan': !settings.owners.length }" label-position="top" @submit.prevent="search">
        <el-form-item :label="tr('shared.search')"><el-input v-model="filters.keyword" :aria-label="tr('shared.search')" clearable /></el-form-item>
        <el-form-item :label="tr('enabled')">
          <el-select v-model="filters.enabled" :empty-values="[null, undefined]" :aria-label="tr('enabled')">
            <el-option value="" :label="tr('shared.all')" />
            <el-option value="enabled" :label="tr('shared.enabled')" />
            <el-option value="disabled" :label="tr('shared.disabled')" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="settings.owners.length" :label="tr('owner')">
          <el-select v-model="filters.owner" :empty-values="[null, undefined]" :aria-label="tr('owner')">
            <el-option value="" :label="tr('shared.all')" />
            <el-option v-for="owner in settings.owners" :key="owner" :value="owner" :label="tr('owners.' + owner)" />
          </el-select>
        </el-form-item>
        <div class="table-actions">
          <ActionButton variant="primary" native-type="submit">{{ t('common.search') }}</ActionButton>
          <ActionButton @click="resetFilters">{{ t('common.reset') }}</ActionButton>
        </div>
      </el-form>

      <el-alert v-if="loadError" :title="groupText('loadFailed')" type="error" :closable="false" show-icon />
      <div class="shared-selection">
        <span aria-live="polite">{{ tr('shared.selected', { count: selections.size }) }}</span>
        <div class="table-actions">
          <ActionButton :disabled="!selections.size || loading" @click="openEdit('batch', selectedRows)">{{ tr('shared.batchEdit') }}</ActionButton>
          <ActionButton :disabled="!selections.size || loading" @click="openDelete('batch', selectedRows)">{{ tr('shared.batchDelete') }}</ActionButton>
        </div>
      </div>

      <div class="shared-table-wrap">
        <el-table :key="columns.version.value" v-loading="loading" :data="pageRows" :row-key="identity"
          :empty-text="config && fields.length ? tr('shared.noMatches') : groupText('noFields')"
          border stripe class="vibe-table" @header-dragend="columns.onHeaderDragEnd">
          <el-table-column width="54" :resizable="false">
            <template #header>
              <el-checkbox :model-value="wholePage" :indeterminate="someOnPage && !wholePage" :disabled="!pageRows.length"
                :aria-label="tr('shared.selectPage')" @change="selectPage" />
            </template>
            <template #default="{ row }">
              <el-checkbox :model-value="selections.has(identity(row))" :aria-label="tr('shared.selectRow', { name: row.name })"
                @change="value => selectRow(row, value)" />
            </template>
          </el-table-column>
          <el-table-column v-for="(label, key) in columnLabels" :key="key" :prop="key" :label="tr(label)"
            :width="columns.widths[key]" :min-width="columnDefinitions[key].minWidth" show-overflow-tooltip>
            <template #default="{ row }">
              <el-tag v-if="key === 'enabled'" :type="row.enabled ? 'success' : 'info'" effect="plain">{{ tr(row.enabled ? 'shared.enabled' : 'shared.disabled') }}</el-tag>
              <template v-else>{{ cell(row, key) }}</template>
            </template>
          </el-table-column>
          <el-table-column :label="tr('actions')" width="130" fixed="right" :resizable="false">
            <template #default="{ row }">
              <div class="row-actions">
                <ActionButton variant="row" :disabled="loading" @click="openEdit('single', [row])">{{ tr('shared.edit') }}</ActionButton>
                <ActionButton size="small" variant="danger" :disabled="loading" @click="openDelete('single', [row])">{{ tr('deleteField') }}</ActionButton>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <el-pagination v-model:current-page="page" v-model:page-size="pageSize"
        :total="filtered.length" :page-sizes="[10,20,50,100]" :pager-count="5" layout="total, sizes, prev, pager, next" />
    </BaseCard>

    <el-dialog v-model="editOpen" :title="tr(editTitle)"
      :width="editMode === 'batch' ? 'min(1400px, calc(100vw - 24px))' : 'min(720px, calc(100vw - 24px))'"
      align-center destroy-on-close class="standard-form-dialog shared-dialog" :class="{ 'single-field-dialog': editMode !== 'batch' }"
      :close-on-click-modal="false" :close-on-press-escape="!busy" :show-close="editMode === 'batch' && !isLocal && !busy">
      <el-alert v-if="message" ref="editAlert" :title="message" type="warning" :closable="false" show-icon />
      <ActionButton v-if="isLocal && pendingReconciliation && !reconciliation.length"
        :loading="busy" @click="retryReconciliation">{{ tr('local.retryRead') }}</ActionButton>
      <div v-if="reconciliation.length" class="shared-reconciliation" role="status">
        <p>{{ tr('shared.currentRevision', { revision: config.configRevision }) }}</p>
        <ul><li v-for="item in reconciliation" :key="identity(item)">{{ describe(item) }} · {{ tr(item.status) }}</li></ul>
      </div>
      <p v-if="editMode === 'batch'" class="shared-description">{{ tr('shared.batchHint', { count: draftRows.length }) }}</p>
      <TaskFieldEditor v-if="editMode === 'batch'" v-loading="busy" :kind="settingsKind" :module="module" :draft-rows="draftRows" />
      <SharedFieldForm v-else-if="draftRows.length" v-model="draftRows[0]" :kind="settingsKind" :tr="tr" :is-new="editMode === 'new'" :disabled="busy" />
      <template #footer>
        <div class="table-actions" :class="{ 'single-field-actions': editMode !== 'batch' }">
          <ActionButton :disabled="busy" @click="editOpen = false">{{ t('common.cancel') }}</ActionButton>
          <ActionButton variant="primary" :loading="busy" :disabled="blocked" @click="save">{{ t('common.save') }}</ActionButton>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="deleteOpen" :title="deleteMode === 'single' ? tr('dialog.deleteTitle') : groupText('deleteTitle', { count: targets.length })"
      width="min(540px, calc(100vw - 24px))" align-center destroy-on-close class="standard-form-dialog shared-dialog"
      :class="{ 'single-field-dialog': deleteMode === 'single' }"
      :close-on-click-modal="false" :close-on-press-escape="!busy" :show-close="deleteMode === 'batch' && !isLocal && !busy">
      <el-alert v-if="message" ref="deleteAlert" :title="message" type="warning" :closable="false" show-icon />
      <ActionButton v-if="isLocal && pendingReconciliation && !reconciliation.length"
        :loading="busy" @click="retryReconciliation">{{ tr('local.retryRead') }}</ActionButton>
      <p class="shared-description">{{ tr(deleteMode === 'single' ? 'dialog.deletePrompt' : 'shared.deleteHint') }}</p>
      <p v-if="deleteMode === 'single'" class="shared-description">{{ tr('dialog.externalReferences') }}</p>
      <p v-if="reconciliation.length">{{ tr('shared.currentRevision', { revision: config.configRevision }) }}</p>
      <ul class="shared-targets">
        <li v-for="item in (reconciliation.length ? reconciliation : targets)" :key="identity(item)">
          {{ describe(item) }}<template v-if="item.status"> · {{ tr(item.status) }}</template>
        </li>
      </ul>
      <template #footer>
        <div class="table-actions" :class="{ 'single-field-actions': deleteMode === 'single' }">
          <ActionButton :disabled="busy" @click="deleteOpen = false">{{ t('common.cancel') }}</ActionButton>
          <ActionButton variant="danger" :loading="busy" :disabled="blocked" @click="confirmDelete">{{ tr(deleteMode === 'single' || isLocal ? 'local.confirmDelete' : 'deleteField') }}</ActionButton>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'
import BaseCard from '@/components/common/BaseCard.vue'
import ActionButton from '@/components/common/ActionButton.vue'
import { useTableColumnWidths } from '@/utils/tableColumnWidths'
import TaskFieldEditor from '../../components/TaskFieldEditor.vue'
import { fieldSettings } from '../../components/fieldSettings'
import { useTaskPagePadding } from '../../components/useTaskPagePadding'
import { getConfig, saveConfig, deleteField, deleteSharedFields, deleteLocalFields } from '../../api'
import SharedFieldForm from './SharedFieldForm.vue'

const props = defineProps({ module: { type: String, required: true }, scope: { type: String, default: 'shared_sync' } })
const { t, te, locale } = useI18n()
const tr = (key, params = {}) => t(`${props.module}.workflow.${key}`, params)
const { pageRoot, pagePadding } = useTaskPagePadding()
const router = useRouter()
const scope = props.scope ?? 'shared_sync'
const isLocal = scope !== 'shared_sync'
const groupText = (key, params) => tr(`${isLocal ? 'local' : 'shared'}.${key}`, params)
const settingsKind = isLocal ? props.module : 'shared'
const settings = fieldSettings[settingsKind]

const nameLocales = { labelZh: 'zh-CN', labelEn: 'en-US' }
const columnLabels = { name:'fieldName', labelZh:'labelZh', labelEn:'labelEn', slotNo:'slot', type:'type', unit:'unit',
  ...(settings.owners.length ? { performanceOwner:'owner' } : {}), enabled:'enabled' }
const columnDefinitions = { name:{width:190,minWidth:130}, labelZh:{width:146,minWidth:110}, labelEn:{width:174,minWidth:130}, slotNo:{width:80,minWidth:64},
  type:{width:100,minWidth:85}, unit:{width:90,minWidth:65}, performanceOwner:{width:130,minWidth:110}, enabled:{width:104,minWidth:84} }
const columns = useTableColumnWidths(isLocal ? `generic-task.local-fields.${settingsKind}` : 'generic-task.shared-fields', columnDefinitions)
const identity = row => `${row.scope}/${row.slotNo}/${row.name}`
const wireIdentity = ({ scope, slotNo, name }) => ({ scope, slotNo, name })
const describe = row => tr('shared.identity', { ...wireIdentity(row), label: row.labels?.[locale.value] || row.name })
function cell(row, key) {
  if (nameLocales[key]) return row.labels?.[nameLocales[key]] ?? '—'
  if (key === 'type') return tr('types.' + row.type)
  if (key === 'performanceOwner') return tr('owners.' + row.performanceOwner)
  return row[key] ?? '—'
}

const config = ref(null)
const fields = computed(() => (config.value?.fields ?? []).filter(row => row.scope === scope).sort((a, b) => a.slotNo - b.slotNo))
const loading = ref(false)
const loadError = ref(false)
const page = ref(1)
const pageSize = ref(20)
const emptyFilters = { keyword: '', enabled: '', owner: '' }
const filters = reactive({ ...emptyFilters })
const applied = ref(emptyFilters)
const filtered = computed(() => {
  const { keyword, enabled, owner } = applied.value
  return fields.value.filter(row => (!keyword || [row.name, ...Object.values(row.labels)].some(value => value.toLowerCase().includes(keyword)))
    && (!enabled || row.enabled === (enabled === 'enabled')) && (!owner || row.performanceOwner === owner))
})
const pageRows = computed(() => filtered.value.slice((page.value - 1) * pageSize.value, page.value * pageSize.value))
watch([() => filtered.value.length, pageSize], () => { page.value = Math.min(page.value, Math.max(1, Math.ceil(filtered.value.length / pageSize.value))) })
const selections = ref(new Set())
const selectedRows = computed(() => fields.value.filter(row => selections.value.has(identity(row))))
const wholePage = computed(() => !!pageRows.value.length && pageRows.value.every(row => selections.value.has(identity(row))))
const someOnPage = computed(() => pageRows.value.some(row => selections.value.has(identity(row))))

function selectRow(row, value) {
  if (value) selections.value.add(identity(row))
  else selections.value.delete(identity(row))
}
function selectPage(value) { for (const row of pageRows.value) selectRow(row, value) }
function search() {
  applied.value = { ...filters, keyword: filters.keyword.trim().toLowerCase() }
  page.value = 1
  selections.value.clear()
}
function resetFilters() { Object.assign(filters, emptyFilters); search() }
function adopt(result, inform = false) {
  const previous = config.value?.configRevision
  config.value = result
  loadError.value = false
  if (previous && previous !== result.configRevision) {
    if (inform && selections.value.size) ElMessage.info(tr('shared.selectionChanged'))
    selections.value.clear()
  } else selections.value = new Set(selectedRows.value.map(identity))
}
let loadSequence = 0
async function load() {
  if (busy.value) return
  const sequence = ++loadSequence
  loading.value = true
  try {
    const result = await getConfig(props.module)
    if (sequence === loadSequence) adopt(result, true)
  } catch {
    if (sequence === loadSequence) loadError.value = true
  } finally {
    if (sequence === loadSequence) loading.value = false
  }
}

const editOpen = ref(false), deleteOpen = ref(false), busy = ref(false), blocked = ref(false)
const message = ref('')
const editAlert = ref(null), deleteAlert = ref(null)
const reconciliation = ref([])
const pendingReconciliation = ref(null)
const editMode = ref('')
const editTitle = computed(() => editMode.value === 'single' && isLocal
  ? 'local.editTitle' : ({ new:'addField', single:'shared.editTitle', batch:'shared.batchEdit' })[editMode.value])
const draftRows = ref([])
const targets = ref([])
let original = []
let revision
const deleteMode = ref('')
watch(message, value => {
  if (!value) return
  const alert = editOpen.value && editMode.value !== 'batch' ? editAlert.value
    : deleteOpen.value && deleteMode.value === 'single' ? deleteAlert.value : null
  alert?.$el.scrollIntoView({ block: 'nearest' })
}, { flush: 'post' })
const cloneRows = rows => rows.map(row => ({ ...row, labels: { ...row.labels } }))
const changeKeys = ['name', 'type', 'unit', ...(settings.owners.length ? ['performanceOwner'] : []),
  ...settings.orders, ...settings.switches]

function beginOperation() {
  revision = config.value.configRevision
  blocked.value = false
  message.value = ''
  reconciliation.value = []
  pendingReconciliation.value = null
}
function openEdit(mode, rows) {
  beginOperation()
  editMode.value = mode
  original = mode === 'new' ? [] : rows
  draftRows.value = cloneRows(rows)
  editOpen.value = true
}
function addField() {
  const used = new Set(fields.value.map(row => row.slotNo))
  const slotNo = Array.from({ length: 100 }, (_, index) => index + 1).find(slot => !used.has(slot))
  if (!slotNo) { ElMessage.warning(tr('noSlots')); return }
  openEdit('new', [{ scope, slotNo, name:'', type:'string', unit:null, labels:{ 'zh-CN':'', 'en-US':'' },
    ...(settings.owners.length ? { performanceOwner:'manual' } : {}),
    ...Object.fromEntries(settings.switches.map(name => [name, false])),
    ...Object.fromEntries(settings.orders.map(name => [name, null])) }])
}
function openDelete(mode, rows) {
  beginOperation()
  deleteMode.value = mode
  targets.value = rows
  deleteOpen.value = true
}
function changes() {
  return draftRows.value.map((row, index) => {
    const before = original[index]
    const patch = { scope: row.scope, slotNo: row.slotNo }
    for (const key of changeKeys) {
      const nullable = ['unit', 'planOrder', 'performanceOrder'].includes(key)
      const value = nullable ? row[key] ?? null : row[key]
      const previous = nullable ? before?.[key] ?? null : before?.[key]
      if (!before || value !== previous) patch[key] = value
    }
    if (!before || ['zh-CN','en-US'].some(lang => row.labels[lang] !== before.labels[lang])) patch.labels = { ...row.labels }
    return patch
  }).filter(patch => Object.keys(patch).length > 2)
}
function validDraft() {
  return draftRows.value.every(row => /^[a-z][A-Za-z0-9_]{0,63}$/.test(row.name)
    && Number.isInteger(row.slotNo) && row.slotNo >= 1 && row.slotNo <= 100
    && ['zh-CN','en-US'].every(lang => row.labels[lang]?.trim() && row.labels[lang].length <= 128))
}
function submittedValuesMatch(current, patch) {
  return Object.entries(patch).every(([key, value]) => key === 'labels'
    ? Object.entries(value).every(([lang, text]) => current.labels[lang] === text) : current[key] === value)
}
async function reconcile() {
  const { rows, isDelete, patches } = pendingReconciliation.value
  message.value = tr('shared.unknown')
  try {
    adopt(await getConfig(props.module), true)
    const current = new Map(fields.value.map(row => [identity(row), row]))
    reconciliation.value = rows.map((row, index) => {
      const actual = current.get(identity(row))
      let status = actual ? 'shared.present' : 'shared.absent'
      if (actual && !isDelete) status = submittedValuesMatch(actual, patches[index]) ? 'shared.matches' : 'shared.differs'
      return { ...wireIdentity(row), labels: row.labels, status }
    })
  } catch { message.value = groupText('unknownRefreshFailed') }
}
async function retryReconciliation() {
  if (busy.value || !pendingReconciliation.value) return
  busy.value = true
  try { await reconcile() } finally { busy.value = false }
}
async function reportFailure(error, rows, isDelete, patches = []) {
  const body = error.response?.data
  const code = body?.errorCode?.replace('task.', '')
  if (!error.response || code === 'commit_unknown') {
    blocked.value = true
    pendingReconciliation.value = { rows, isDelete, patches }
    await reconcile()
    return
  }
  const path = body?.details?.field ?? ''
  const reason = body?.details?.reason
  const index = /^fields\.(\d+)\.(?:name|scope|slotNo)$/.exec(path)?.[1]
  const row = index !== undefined ? rows[Number(index)] : isDelete && deleteMode.value === 'single' && path === 'name' ? rows[0] : null
  const reasonKey = `shared.reasons.${reason}`
  const localSaveKey = `local.saveReasons.${reason}`
  const errorKey = `errors.${code}`
  const exists = key => te(`${props.module}.workflow.${key}`)
  const details = isLocal && !isDelete && code === 'invalid_request' && exists(localSaveKey) ? tr(localSaveKey)
    : exists(reasonKey) ? tr(reasonKey) : exists(errorKey) ? tr(errorKey) : tr('requestFailed')
  message.value = row ? `${describe(row)} · ${details}` : details
  blocked.value = isDelete || code === 'config_revision_conflict'
}
async function save() {
  if (busy.value || blocked.value) return
  if (!validDraft()) { message.value = tr('shared.invalidDraft'); return }
  if (editMode.value === 'new' && fields.value.some(row => row.slotNo === draftRows.value[0].slotNo)) {
    message.value = groupText('slotOccupied', { slot: draftRows.value[0].slotNo })
    return
  }
  const patch = changes()
  if (!patch.length) { editOpen.value = false; return }
  const submitted = patch.map(change => {
    const row = draftRows.value.find(draft => draft.slotNo === change.slotNo)
    return { ...wireIdentity(row), labels: { ...row.labels } }
  })
  busy.value = true
  message.value = ''
  try {
    adopt(await saveConfig({ module: settingsKind, configRevision: revision, changes: patch }))
    editOpen.value = false
    ElMessage.success(tr('saved'))
  } catch (error) { await reportFailure(error, submitted, false, patch) }
  finally { busy.value = false }
}
async function confirmDelete() {
  if (busy.value || blocked.value) return
  busy.value = true
  message.value = ''
  const rows = targets.value
  const requested = rows.map(wireIdentity)
  const batch = { fields: requested, configRevision: revision }
  try {
    const result = deleteMode.value === 'single' ? await deleteField({ ...requested[0], configRevision: revision })
      : isLocal ? await deleteLocalFields({ ...batch, module: settingsKind }) : await deleteSharedFields(batch)
    const removed = new Set((result.deleted ?? [result]).map(identity))
    config.value = { ...config.value, configVersion: result.configVersion, configRevision: result.configRevision,
      fields: config.value.fields.filter(row => !removed.has(identity(row))) }
    for (const key of removed) selections.value.delete(key)
    deleteOpen.value = false
    ElMessage.success(tr('deletedField'))
  } catch (error) { await reportFailure(error, rows, true) }
  finally { busy.value = false }
}
onMounted(load)
watch(() => props.module, () => {
  if (busy.value) return
  editOpen.value = false
  deleteOpen.value = false
  config.value = null
  loadError.value = false
  resetFilters()
  load()
})
</script>

<style scoped>
.shared-field-page { min-width: 0; container-type: inline-size; --shared-inset: 24px; }
.shared-field-page :deep(.base-card__body) { min-width: 0; padding: 0 0 var(--shared-inset); }
.shared-field-page :deep(.base-card__header) { flex-wrap: wrap; padding-block: 12px; }
.shared-field-page :deep(.base-card__actions) { min-width: 0; max-width: 100%; flex: 0 1 auto; }
.card-title { margin: 0; color: var(--text-primary); font-size: 16px; font-weight: 590; line-height: 1.35; overflow-wrap: anywhere; }
.help-trigger { display: inline-flex; flex: 0 0 auto; align-items: center; justify-content: center; width: 24px; height: 24px; padding: 0; border: 0; border-radius: 50%; background: transparent; color: var(--text-secondary); font-size: 16px; cursor: pointer; }
.help-trigger:hover { color: var(--primary); }
.help-trigger:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
.help-content { max-width: min(340px, calc(100vw - 56px)); white-space: normal; overflow-wrap: anywhere; }
.shared-filters { display: grid; grid-template-columns: minmax(0, 2fr) repeat(var(--shared-filter-columns, 2), minmax(0, 1fr)) auto; gap: 12px; align-items: end; padding: 16px var(--shared-inset); border-bottom: 1px solid var(--border-secondary); }
.shared-filters--plan { --shared-filter-columns: 1; }
.shared-filters :deep(.el-form-item) { min-width: 0; margin-bottom: 0; }
.shared-filters :deep(.el-form-item__label) { height: auto; line-height: 1.4; white-space: normal; overflow-wrap: anywhere; }
.shared-filters :deep(.el-select) { width: 100%; min-width: 0; }
.shared-selection { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin: 14px var(--shared-inset) 10px; }
.shared-table-wrap { min-width: 0; margin-inline: var(--shared-inset); }
.shared-field-page :deep(.el-pagination) { display: flex; flex-wrap: wrap; gap: 8px; margin: 18px var(--shared-inset) 0; justify-content: flex-end; }
.shared-description { margin: 0 0 12px; }
.shared-targets, .shared-reconciliation ul { padding-inline-start: 20px; margin: 8px 0; overflow-wrap: anywhere; }
.shared-dialog :deep(.el-alert) { margin-bottom: 10px; }
:global(.standard-form-dialog.shared-dialog.el-dialog) { max-height: calc(100dvh - 24px); overflow: auto; }
:global(.standard-form-dialog.shared-dialog.single-field-dialog.el-dialog) {
  --field-dialog-inset: clamp(16px, 4vw, 32px);
  display: flex;
  flex-direction: column;
  max-width: calc(100vw - 24px);
  padding: 0;
  overflow: hidden;
}
:global(.single-field-dialog .el-dialog__header) {
  flex: none;
  min-height: 0;
  padding: 16px var(--field-dialog-inset);
}
:global(.single-field-dialog .el-dialog__title) {
  min-width: 0;
  font-size: 16px;
  font-weight: 590;
  line-height: 1.35;
  overflow-wrap: anywhere;
}
:global(.single-field-dialog .el-dialog__body) {
  min-height: 0;
  overflow: auto;
  overscroll-behavior: contain;
  padding: 18px var(--field-dialog-inset);
}
:global(.single-field-dialog .el-dialog__footer) {
  flex: none;
  padding: 14px var(--field-dialog-inset);
}
.single-field-actions { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 8px; }
.single-field-actions :deep(.el-button + .el-button) { margin-left: 0; }
@container (max-width: 680px) {
  .shared-filters { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .shared-filters > :first-child { grid-column: 1 / -1; }
  .shared-filters .table-actions { grid-column: 1 / -1; }
}
@container (max-width: 400px) {
  .shared-filters { grid-template-columns: minmax(0, 1fr); }
  .shared-field-page :deep(.base-card__header) { padding-inline: 12px; }
}
@media (max-width: 600px) {
  .shared-field-page { --shared-inset: 16px; }
}
</style>
