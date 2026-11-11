<!-- 计划与实绩列表、详情及业务字段编辑；业务数据来自对应正式 API。 -->
<template>
  <div ref="pageRoot" class="page-layout" :style="{ paddingTop: `${pagePadding}px` }">
    <BaseCard class="list-card">
      <template #title>
        <h3 class="card-title">{{ tr('title') }}</h3>
        <el-tooltip placement="bottom-start" :trigger="['hover', 'focus']" :trigger-keys="[]">
          <template #content><div class="help-content">{{ tr('timeZone') }}</div></template>
          <button class="help-trigger" type="button" :aria-label="tr('timeZone')" @click="$event.currentTarget.focus()" @keydown.esc.stop="$event.currentTarget.blur()">
            <el-icon><QuestionFilled /></el-icon>
          </button>
        </el-tooltip>
      </template>
      <template #actions>
        <div class="table-actions">
          <ActionButton v-if="kind === 'plan' && canManage && configAvailable" variant="primary" @click="newPlan">{{ tr('newPlan') }}</ActionButton>
          <ActionButton v-if="user.isAdmin && configAvailable" @click="configOpen = true"><el-icon><Setting /></el-icon> {{ tr('fieldSettings') }}</ActionButton>
          <ActionButton @click="columns.reset">{{ tr('resetWidths') }}</ActionButton>
          <ActionButton :loading="loading" @click="load">{{ tr('refresh') }}</ActionButton>
        </div>
      </template>
      <div class="filter-section">
        <el-form class="filter-form" label-position="top" @submit.prevent="search">
          <el-form-item :label="tr('taskNo')"><el-input v-model="filters.taskNo" clearable /></el-form-item>
          <el-form-item :label="tr('targetKey')"><el-input v-model="filters.targetKey" clearable /></el-form-item>
          <el-form-item :label="tr('productionStatus')"><el-select v-model="filters.productionStatus" clearable><el-option v-for="s in productionStates" :key="s" :value="s" :label="tr(`statuses.${s}`)" /></el-select></el-form-item>
          <el-form-item v-if="kind === 'plan'" :label="tr('dispatchStatus')"><el-select v-model="filters.dispatchStatus" clearable><el-option v-for="s in dispatchStates" :key="s" :value="s" :label="tr(`statuses.${s}`)" /></el-select></el-form-item>
          <el-form-item :label="tr('createdFrom')"><el-date-picker v-model="filters.createdFrom" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss[+08:00]" clearable /></el-form-item>
          <el-form-item :label="tr('createdTo')"><el-date-picker v-model="filters.createdTo" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss[+08:00]" clearable /></el-form-item>
          <el-form-item class="filter-actions"><ActionButton variant="primary" @click="search">{{ $t('common.search') }}</ActionButton><ActionButton @click="resetFilters">{{ $t('common.reset') }}</ActionButton></el-form-item>
        </el-form>
      </div>
      <div class="table-scroll">
        <el-table :key="columns.version.value" v-loading="loading" :data="items" stripe border class="vibe-table" @header-dragend="columns.onHeaderDragEnd" @row-click="openDetail">
          <el-table-column v-for="col in fixedColumns" :key="col" :prop="col" :label="tr(col)" :width="columns.widths[col]" :min-width="100" show-overflow-tooltip>
            <template #default="{ row }">{{ displayFixed(row, col) }}</template>
          </el-table-column>
          <el-table-column v-for="field in visibleFields" :key="fieldKey(field)" :prop="fieldKey(field)" :label="fieldLabel(field)" :width="columns.widths[fieldKey(field)]" :min-width="100" show-overflow-tooltip>
            <template #default="{ row }">{{ displayValue((field.scope === 'shared_sync' ? row.syncValues : row.localValues)?.[field.name]) }}</template>
          </el-table-column>
          <el-table-column :label="tr('actions')" width="100" fixed="right"><template #default="{ row }"><div class="row-actions" @click.stop><ActionButton size="small" variant="row" @click="openDetail(row)">{{ tr('detail') }}</ActionButton></div></template></el-table-column>
        </el-table>
      </div>
      <div class="pagination-scroll">
        <el-pagination v-model:current-page="filters.page" v-model:page-size="filters.pageSize" :page-sizes="[10,20,50,100]" :total="total" layout="total, sizes, prev, pager, next, jumper" class="pagination" @current-change="load" @size-change="load" />
      </div>
    </BaseCard>

    <el-dialog v-model="detailOpen" :title="tr(mode === 'new' ? 'newPlan' : mode === 'supplement' ? 'supplement' : 'detail')" width="760px" class="standard-form-dialog" @closed="closeDetail">
      <el-form v-if="form" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item :label="tr('taskNo')"><el-input v-model="form.taskNo" :disabled="mode !== 'new'" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tr('targetKey')"><el-input v-model="form.targetKey" :disabled="mode === 'supplement' || !canEditOrders" /></el-form-item></el-col>
          <el-col v-if="kind === 'plan' || mode === 'supplement'" :span="12"><el-form-item :label="tr('priority')"><el-input-number v-model="form.priority" :min="1" :max="10" :disabled="!canEditOrders" /></el-form-item></el-col>
          <el-col v-if="record" :span="12"><el-form-item :label="tr('productionStatus')">{{ stateLabel(record.productionStatus) }}</el-form-item></el-col>
          <el-col v-if="record && kind === 'plan'" :span="12"><el-form-item :label="tr('dispatchStatus')">{{ stateLabel(record.dispatchStatus) }}</el-form-item></el-col>
          <el-col v-if="record && kind === 'performance'" :span="12"><el-form-item :label="tr('lastObservedAt')">{{ formatShanghaiDateTime(record.lastObservedAt) || '—' }}</el-form-item></el-col>
          <el-col v-for="field in formFields" :key="fieldKey(field)" :span="12">
            <el-form-item :label="fieldLabel(field)">
              <el-input v-if="field.type === 'string'" v-model="form[valueGroup(field)][field.name]" :maxlength="255" :disabled="!fieldEditable(field)" />
              <el-input-number v-else-if="field.type === 'number'" v-model="form[valueGroup(field)][field.name]" :precision="4" :disabled="!fieldEditable(field)" controls-position="right" />
              <el-select v-else v-model="form[valueGroup(field)][field.name]" :disabled="!fieldEditable(field)" :clearable="field.isNullable" @clear="form[valueGroup(field)][field.name] = null">
                <el-option :label="tr('yes')" :value="true" /><el-option :label="tr('no')" :value="false" />
              </el-select>
              <el-button v-if="field.isNullable && fieldEditable(field)" link @click="form[valueGroup(field)][field.name] = null">{{ tr('clearValue') }}</el-button>
            </el-form-item>
          </el-col>
          <el-col :span="24"><el-form-item :label="tr('remark')"><el-input v-model="form.remark" type="textarea" :maxlength="500" :disabled="!canEditRemark" /></el-form-item></el-col>
          <el-col v-if="mode === 'supplement'" :span="24"><el-checkbox v-model="form.backfillExisting">{{ tr('backfillExisting') }}</el-checkbox></el-col>
        </el-row>
      </el-form>
      <el-descriptions v-if="record && mode !== 'supplement'" :column="2" border>
        <el-descriptions-item v-for="key in detailKeys" :key="key" :label="tr(key)">{{ displayFixed(record, key) }}</el-descriptions-item>
      </el-descriptions>
      <template v-if="record && mode !== 'supplement' && kind === 'plan' && record.latestDispatchAttempt">
        <h4>{{ tr('latestAttempt') }}</h4>
        <el-descriptions :column="2" border>
          <el-descriptions-item v-for="key in attemptKeys" :key="key" :label="tr(key)">{{ displayFixed(record.latestDispatchAttempt, key) }}</el-descriptions-item>
        </el-descriptions>
      </template>
      <template v-if="record && mode !== 'supplement' && kind === 'plan' && record.recentActionEvents?.length">
        <h4>{{ tr('recentActions') }}</h4>
        <el-table :data="record.recentActionEvents" border>
          <el-table-column v-for="key in eventKeys" :key="key" :prop="key" :label="tr(key)" min-width="130" show-overflow-tooltip><template #default="{ row }">{{ displayFixed(row, key) }}</template></el-table-column>
        </el-table>
      </template>
      <template #footer>
        <el-button v-if="canSupplement && mode !== 'supplement'" @click="startSupplement">{{ tr('supplement') }}</el-button>
        <el-button v-if="canAction('pause')" @click="runAction('pause')">{{ tr('pause') }}</el-button>
        <el-button v-if="canAction('save-and-resume')" @click="runAction('save-and-resume')">{{ tr('saveResume') }}</el-button>
        <el-button v-if="canAction('cancel')" @click="runAction('cancel')">{{ tr('cancelPlan') }}</el-button>
        <el-button v-if="canAction('return-to-paused')" @click="runAction('return-to-paused')">{{ tr('returnPaused') }}</el-button>
        <el-button @click="detailOpen = false">{{ $t('common.close') }}</el-button>
        <el-button v-if="canEditRemark || mode === 'supplement'" type="primary" :loading="saving" @click="save">{{ $t('common.save') }}</el-button>
      </template>
    </el-dialog>
    <TaskConfigDialog v-model="configOpen" :kind="kind" :api="api" @saved="loadConfigAndList" />
  </div>
</template>
<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { QuestionFilled, Setting } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { useTableColumnWidths } from '@/utils/tableColumnWidths'
import { formatShanghaiDateTime } from '@/utils/date'
import BaseCard from '@/components/common/BaseCard.vue'
import ActionButton from '@/components/common/ActionButton.vue'
import TaskConfigDialog from './TaskConfigDialog.vue'

const props = defineProps({ kind: { type: String, required: true }, api: { type: Object, required: true } })
const { t, te, locale } = useI18n()
const tr = key => t(`${props.kind}.workflow.${key}`)
const pageRoot = ref(null), pagePadding = ref(0)
let layoutObserver
// 按壳层真实高度留白；加回滚动量，避免滚动时不断增大顶距。
function updatePagePadding() {
  const root = pageRoot.value
  const main = root?.closest('main')
  const header = main?.parentElement?.querySelector('header.header')
  if (!root || !main || !header) return
  const naturalTop = root.getBoundingClientRect().top + main.scrollTop
  pagePadding.value = Math.max(0, Math.ceil(header.getBoundingClientRect().bottom - naturalTop + 8))
}
const user = useUserStore()
const canManage = computed(() => user.isAdmin || user.role === 'supervisor')
const productionStates = ['running','completed']
const dispatchStates = ['pending','paused','claimed','exception','plc_accepted','cancelled','not_required']
const defaults = { page: 1, pageSize: 20, taskNo: '', targetKey: '', productionStatus: '', dispatchStatus: '', createdFrom: '', createdTo: '', sortOrder: 'desc' }
const filterKey = `aiis-ics:task-filters:${props.kind}:${user.username}`
const draftKey = `aiis-ics:task-draft:${props.kind}:${user.username}`
function readStorage(key, fallback) { try { return JSON.parse(localStorage.getItem(key)) || fallback } catch { return fallback } }
function store(key, value) { try { localStorage.setItem(key, JSON.stringify(value)) } catch { /* 本机偏好不可用不影响业务。 */ } }
function clear(key) { try { localStorage.removeItem(key) } catch { /* 本机偏好不可用不影响业务。 */ } }
const filters = reactive({ ...defaults, ...readStorage(filterKey, {}) })
const fixedColumns = computed(() => props.kind === 'plan' ? ['taskNo','targetKey','dispatchStatus','productionStatus','priority','createdAt','updatedAt'] : ['taskNo','targetKey','productionStatus','hasPlan','createdAt','lastObservedAt','updatedAt'])
const widthDefinitions = Object.fromEntries(['taskNo','targetKey','dispatchStatus','productionStatus','priority','hasPlan','createdAt','updatedAt','lastObservedAt'].map(k => [k,{ width: k.endsWith('At') ? 180 : 150, minWidth: 100 }]))
for (const scope of ['shared_sync',`${props.kind}_local`]) for (let slot=1; slot<=100; slot++) widthDefinitions[`${scope}.${String(slot).padStart(2,'0')}`] = { width: 150, minWidth: 100 }
const columns = useTableColumnWidths(`generic-task.${props.kind}`, widthDefinitions)
const fieldKey = field => `${field.scope}.${String(field.slotNo).padStart(2,'0')}`
const fieldLabel = field => `${field.labels?.[locale.value] || field.labels?.['en-US'] || field.name}${field.unit ? ` (${field.unit})` : ''}`
const fields = ref([]), listedFields = ref([]), formFields = ref([]), items = ref([]), total = ref(0), loading = ref(false), saving = ref(false), configAvailable = ref(false)
const configOpen = ref(false), detailOpen = ref(false), record = ref(null), form = ref(null), original = ref(null), mode = ref('view'), planFields = ref(null)
const visibleFields = computed(() => listedFields.value.filter(f => f.enabled && f[props.kind === 'plan' ? 'planVisible' : 'performanceVisible']).sort((a,b) => (a[`${props.kind}Order`] ?? a.slotNo) - (b[`${props.kind}Order`] ?? b.slotNo)))
const canEditOrders = computed(() => mode.value === 'new' || mode.value === 'supplement' || (props.kind === 'plan' && canManage.value && ['pending','paused'].includes(record.value?.dispatchStatus) && !record.value?.productionStatus))
const canEditRemark = computed(() => mode.value === 'new' || mode.value === 'supplement' || (props.kind === 'performance' ? ['admin','supervisor','operator'].includes(user.role) : canManage.value && record.value?.dispatchStatus !== 'cancelled'))
const canSupplement = computed(() => props.kind === 'performance' && canManage.value && user.hasPageAccess('plan.list') && record.value && !record.value.hasPlan && planFields.value)
const detailKeys = computed(() => props.kind === 'performance' ? ['createdAt','updatedAt','startedAt','completedAt','observationSeq','recordSource','hasPlan'] : ['createdAt','updatedAt'])
const attemptKeys = computed(() => ['dispatchId','attemptNo','attemptStatus','submissionPhase','requestSeq','ackSeq','ackObservedAt','claimedAt', ...(canManage.value ? ['failureKey','failureDetail'] : [])])
const eventKeys = ['actionKey','actorId','fromStatus','toStatus','dispatchId','reason','evidence','createdAt']
const clone = value => JSON.parse(JSON.stringify(value))
const valueGroup = field => field.scope === 'shared_sync' ? 'syncValues' : 'localValues'
function displayValue(value) { return value === undefined || value === null ? '—' : typeof value === 'boolean' ? tr(value ? 'yes' : 'no') : String(value) }
function stateLabel(value) { return value ? (te(`${props.kind}.workflow.statuses.${value}`) ? tr(`statuses.${value}`) : value) : '—' }
function displayFixed(row, key) { if (key.endsWith('At')) return formatShanghaiDateTime(row[key]) || '—'; if (key.endsWith('Status')) return stateLabel(row[key]); if (key === 'submissionPhase' && row[key]) return tr(`phases.${row[key]}`); if (key === 'recordSource' && row[key]) return tr(`sources.${row[key]}`); return displayValue(row[key]) }
function fieldEditable(field) {
  if (mode.value === 'supplement' || props.kind === 'plan') return canEditOrders.value && field.planEditable && !field.syncEnabled
  return field.performanceOwner === 'manual' && field.performanceEditable && canEditRemark.value
}
function showError(error) {
  const key = error.response?.data?.errorCode?.replace('task.', '')
  ElMessage.error(key && te(`${props.kind}.workflow.errors.${key}`) ? tr(`errors.${key}`) : tr('requestFailed'))
}
async function load() {
  loading.value = true
  try {
    const params = Object.fromEntries(Object.entries(filters).filter(([,v]) => v !== '' && v !== null))
    const result = await props.api.list(params)
    const versions = [...new Set(result.items.map(row => row.fieldConfigVersion))]
    const configs = await Promise.all(versions.map(version => props.api.getConfig(props.kind, version)))
    const union = new Map()
    for (const field of fields.value) if (field.enabled && field[props.kind === 'plan' ? 'planVisible' : 'performanceVisible']) union.set(fieldKey(field), field)
    for (const config of configs) for (const field of config.fields) if (field.enabled && field[props.kind === 'plan' ? 'planVisible' : 'performanceVisible']) union.set(fieldKey(field), field)
    listedFields.value = [...union.values()]
    items.value = result.items; total.value = result.total
  }
  catch (e) { showError(e) } finally { loading.value = false }
}
async function loadConfigAndList() { try { fields.value = (await props.api.getConfig(props.kind)).fields; configAvailable.value = true; await load() } catch (e) { configAvailable.value = false; showError(e) } }
function search() { filters.page = 1; load() }
function resetFilters() { Object.assign(filters, defaults); load() }
function makeForm(row) { return { taskNo: row?.taskNo || '', targetKey: row?.targetKey || '', priority: row?.priority ?? 5, remark: row?.remark ?? null,
  fieldConfigVersion: row?.fieldConfigVersion, syncValues: clone(row?.syncValues || {}), localValues: clone(row?.localValues || {}), backfillExisting: false } }
async function newPlan() {
  try { const config = await props.api.getConfig('plan'); record.value = null; formFields.value = config.fields.filter(f => f.enabled); form.value = makeForm({ fieldConfigVersion: config.fieldConfigVersion }); original.value = clone(form.value); mode.value = 'new'; detailOpen.value = true }
  catch (e) { showError(e) }
}
async function openDetail(row) {
  try {
    const value = await props.api.detail(row.id)
    const config = await props.api.getConfig(props.kind, value.fieldConfigVersion)
    record.value = value; formFields.value = config.fields.filter(f => f.enabled); form.value = makeForm(value); original.value = clone(form.value); mode.value = 'view'; planFields.value = null
    if (props.kind === 'performance' && canManage.value && user.hasPageAccess('plan.list') && !value.hasPlan) {
      try { planFields.value = (await props.api.getConfig('plan', value.fieldConfigVersion)).fields.filter(f => f.enabled) } catch { planFields.value = null }
    }
    detailOpen.value = true
  } catch (e) { showError(e) }
}
function startSupplement() { mode.value = 'supplement'; formFields.value = planFields.value; form.value = makeForm({ taskNo: record.value.taskNo, targetKey: record.value.targetKey, fieldConfigVersion: record.value.fieldConfigVersion }); original.value = clone(form.value) }
function changedValues() {
  const result = { fieldConfigVersion: form.value.fieldConfigVersion }
  for (const key of ['targetKey','priority','remark']) if ((key !== 'priority' || props.kind === 'plan' || mode.value === 'supplement') && form.value[key] !== original.value[key]) result[key] = form.value[key]
  for (const group of ['syncValues','localValues']) {
    const changes = {}
    for (const [key,value] of Object.entries(form.value[group])) if (value !== original.value[group][key]) changes[key] = value
    if (Object.keys(changes).length) result[group] = changes
  }
  return result
}
async function save() {
  saving.value = true
  try {
    let body = changedValues()
    if (mode.value === 'new') body = { ...body, taskNo: form.value.taskNo, targetKey: form.value.targetKey, priority: form.value.priority }
    else if (mode.value === 'supplement') body = { ...body, targetKey: form.value.targetKey, backfillExisting: form.value.backfillExisting }
    else body.taskNo = form.value.taskNo
    if (mode.value === 'supplement') await props.api.supplement(record.value.id, body)
    else await props.api.upsert(body)
    clear(draftKey); form.value = null; detailOpen.value = false; ElMessage.success(tr('saved')); await load()
  } catch (e) { showError(e) } finally { saving.value = false }
}
function canAction(action) {
  if (props.kind !== 'plan' || !record.value || !canManage.value || mode.value !== 'view' || record.value.productionStatus) return false
  const status = record.value.dispatchStatus
  return action === 'pause' ? status === 'pending' : action === 'save-and-resume' ? status === 'paused' : action === 'cancel' ? ['pending','paused'].includes(status) : ['claimed','exception'].includes(status)
}
async function runAction(action) {
  const pendingKey = `${draftKey}:action:${record.value.id}:${action}`
  let body = readStorage(pendingKey, null)
  try {
    if (!body) {
      body = { actionRequestId: crypto.randomUUID() }
      if (action === 'save-and-resume') Object.assign(body, changedValues())
      if (['cancel','return-to-paused'].includes(action)) body.reason = (await ElMessageBox.prompt(tr('enterReason'), tr(action === 'cancel' ? 'cancelPlan' : 'returnPaused'))).value
      if (action === 'return-to-paused') { body.dispatchId = record.value.latestDispatchAttempt?.dispatchId; body.evidence = (await ElMessageBox.prompt(tr('enterEvidence'), tr('returnPaused'))).value }
      store(pendingKey, body)
    }
    await props.api.action(record.value.id, action, body); clear(pendingKey); clear(draftKey); form.value = null; detailOpen.value = false; ElMessage.success(tr('saved')); await load()
  } catch (e) { if (e?.response?.status >= 400 && e?.response?.status < 500) clear(pendingKey); if (e !== 'cancel' && e !== 'close') showError(e) }
}
function closeDetail() { if (!form.value) return; if (JSON.stringify(form.value) !== JSON.stringify(original.value)) store(draftKey, { mode: mode.value, id: record.value?.id || null, form: form.value }); else clear(draftKey) }
watch(filters, value => store(filterKey, value), { deep: true })
watch(form, value => { if (detailOpen.value && value) store(draftKey, { mode: mode.value, id: record.value?.id || null, form: value }) }, { deep: true })
onMounted(async () => {
  const main = pageRoot.value?.closest('main')
  const header = main?.parentElement?.querySelector('header.header')
  if (main && header) {
    layoutObserver = new ResizeObserver(updatePagePadding)
    layoutObserver.observe(main)
    layoutObserver.observe(header)
    layoutObserver.observe(pageRoot.value)
    updatePagePadding()
  }
  await loadConfigAndList()
  const draft = readStorage(draftKey, null)
  if (draft?.mode === 'new' && props.kind === 'plan' && canManage.value) { await newPlan(); if (detailOpen.value) form.value = draft.form }
  else if (draft?.id) { await openDetail({ id: draft.id }); if (detailOpen.value && draft.mode === 'supplement' && canSupplement.value) startSupplement(); if (detailOpen.value) form.value = draft.form }
})
onBeforeUnmount(() => layoutObserver?.disconnect())
</script>

<style scoped>
.page-layout { container-type: inline-size; }
.list-card :deep(.base-card__body) { padding: 0; }
.list-card :deep(.base-card__header) { flex-wrap: wrap; padding-block: 12px; }
.list-card :deep(.base-card__actions) { min-width: 0; max-width: 100%; flex: 0 1 auto; }
.list-card :deep(.table-actions) { min-width: 0; max-width: 100%; flex-wrap: wrap; }
.card-title { margin: 0; color: var(--text-primary); font-size: 16px; font-weight: 590; line-height: 1.35; overflow-wrap: anywhere; }
.help-trigger { display: inline-flex; flex: 0 0 auto; align-items: center; justify-content: center; width: 24px; height: 24px; padding: 0; border: 0; border-radius: 50%; background: transparent; color: var(--text-secondary); font-size: 16px; cursor: pointer; }
.help-trigger:hover { color: var(--primary); }
.help-trigger:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
.help-content { max-width: min(340px, calc(100vw - 56px)); white-space: normal; overflow-wrap: anywhere; }
.filter-section { padding: 16px 24px; border-bottom: 1px solid var(--border-secondary); }
.filter-form { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 185px), 1fr)); gap: 12px; align-items: end; }
.filter-form :deep(.el-form-item) { min-width: 0; margin-bottom: 0; }
.filter-form :deep(.el-form-item__label) { height: auto; line-height: 1.4; white-space: normal; overflow-wrap: anywhere; }
.filter-form :deep(.el-select), .filter-form :deep(.el-input), .filter-form :deep(.el-date-editor) { width: 100%; max-width: 100%; min-width: 0; }
.filter-actions { grid-column: -2 / -1; }
.filter-actions :deep(.el-form-item__content) { display: flex; justify-content: flex-end; flex-wrap: wrap; gap: 8px; }
.filter-actions :deep(.el-button + .el-button) { margin-left: 0; }
.table-scroll { width: 100%; padding: 20px 24px 0; overflow-x: auto; }
.pagination-scroll { width: 100%; padding: 18px 24px 24px; overflow-x: auto; }
.pagination { display: flex; justify-content: flex-end; width: max-content; min-width: 100%; }
@container (max-width: 700px) {
  .filter-actions { grid-column: auto; }
  .filter-actions :deep(.el-form-item__content) { justify-content: flex-start; }
}
@media (max-width: 600px) {
  .filter-section, .table-scroll, .pagination-scroll { padding-inline: 16px; }
}
</style>
