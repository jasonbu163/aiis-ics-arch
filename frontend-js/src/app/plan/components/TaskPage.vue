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
            <template #default="{ row }">{{ displayValue(row.items?.[field.name]) }}</template>
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
          <el-col :span="12"><el-form-item :label="tr('targetKey')"><el-input v-model="form.targetKey" :disabled="!canEditOrders || (mode === 'view' && Boolean(record?.targetKey))" /></el-form-item></el-col>
          <el-col v-if="kind === 'plan' || mode === 'supplement'" :span="12"><el-form-item :label="tr('priority')"><el-input-number v-model="form.priority" :min="1" :max="10" :disabled="!canEditOrders" /></el-form-item></el-col>
          <el-col :span="12">
            <el-form-item :label="tr('productionStatus')">
              <el-select v-if="canEditOrders" v-model="form.productionStatus" clearable>
                <el-option v-for="s in productionStates" :key="s" :value="s" :label="tr(`statuses.${s}`)" />
              </el-select>
              <span v-else>{{ stateLabel(record?.productionStatus) }}</span>
            </el-form-item>
          </el-col>
          <el-col v-if="record && kind === 'performance'" :span="12"><el-form-item :label="tr('lastObservedAt')">{{ displayFixed(record, 'lastObservedAt') }}</el-form-item></el-col>
          <el-col v-for="field in formFields" :key="fieldKey(field)" :span="12">
            <el-form-item :label="fieldLabel(field)">
              <el-input v-if="field.type === 'string'" v-model="form.items[field.name]" :maxlength="255" :disabled="!fieldEditable(field)" />
              <el-input-number v-else-if="field.type === 'number'" v-model="form.items[field.name]" :precision="4" :disabled="!fieldEditable(field)" controls-position="right" />
              <el-select v-else v-model="form.items[field.name]" :disabled="!fieldEditable(field)" :clearable="field.isNullable" @clear="form.items[field.name] = null">
                <el-option :label="tr('yes')" :value="true" /><el-option :label="tr('no')" :value="false" />
              </el-select>
              <el-button v-if="field.isNullable && fieldEditable(field)" link @click="form.items[field.name] = null">{{ tr('clearValue') }}</el-button>
            </el-form-item>
          </el-col>
          <el-col :span="24"><el-form-item :label="tr('remark')"><el-input v-model="form.remark" type="textarea" :maxlength="500" :disabled="!canEditRemark" /></el-form-item></el-col>
          <el-col v-if="mode === 'supplement'" :span="24"><el-checkbox v-model="form.backfillExisting">{{ tr('backfillExisting') }}</el-checkbox></el-col>
        </el-row>
      </el-form>
      <el-descriptions v-if="record && mode !== 'supplement'" :column="2" border>
        <el-descriptions-item v-for="key in detailKeys" :key="key" :label="tr(key)">{{ displayFixed(record, key) }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button v-if="canSupplement && mode !== 'supplement'" @click="startSupplement">{{ tr('supplement') }}</el-button>
        <el-button @click="detailOpen = false">{{ $t('common.close') }}</el-button>
        <el-button v-if="canEditRemark || mode === 'supplement'" type="primary" :loading="saving" @click="save">{{ $t('common.save') }}</el-button>
      </template>
    </el-dialog>
    <TaskConfigDialog v-if="user.isAdmin" v-model="configOpen" :kind="kind" :api="api" @saved="loadConfigAndList" />
  </div>
</template>
<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { QuestionFilled, Setting } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { useTableColumnWidths } from '@/utils/tableColumnWidths'
import BaseCard from '@/components/common/BaseCard.vue'
import ActionButton from '@/components/common/ActionButton.vue'
import TaskConfigDialog from './TaskConfigDialog.vue'
import { useTaskPagePadding } from './useTaskPagePadding'

const props = defineProps({ kind: { type: String, required: true }, api: { type: Object, required: true } })
const { t, te, locale } = useI18n()
const tr = key => t(`${props.kind}.workflow.${key}`)
const user = useUserStore()
const canManage = computed(() => user.isAdmin || user.role === 'supervisor')
const productionStates = ['new', 'running', 'completed', 'error']
const defaults = { page: 1, pageSize: 20, taskNo: '', targetKey: '', productionStatus: '', createdFrom: '', createdTo: '', sortOrder: 'desc' }
const filterKey = `aiis-ics:task-filters:${props.kind}:${user.username}`
const filters = reactive({ ...defaults })
try {
  const saved = JSON.parse(localStorage.getItem(filterKey))
  for (const key of Object.keys(defaults)) if (saved && Object.hasOwn(saved, key)) filters[key] = saved[key]
  if (!productionStates.includes(filters.productionStatus)) filters.productionStatus = ''
} catch { /* 本机偏好不可用时使用默认筛选。 */ }

const { pageRoot, pagePadding } = useTaskPagePadding()

const fields = ref([]), formFields = ref([]), items = ref([]), total = ref(0)
const loading = ref(false), saving = ref(false), configAvailable = ref(false)
const configOpen = ref(false), detailOpen = ref(false)
const record = ref(null), form = ref(null), original = ref(null), mode = ref('view'), planFields = ref(null)
const fixedColumns = computed(() => props.kind === 'plan'
  ? ['taskNo', 'targetKey', 'productionStatus', 'priority', 'createdAt', 'updatedAt']
  : ['taskNo', 'targetKey', 'productionStatus', 'hasPlan', 'createdAt', 'lastObservedAt', 'updatedAt'])
const visibleFields = computed(() => fields.value.filter(f => f.enabled && f[`${props.kind}Visible`])
  .sort((a, b) => (a[`${props.kind}Order`] ?? a.slotNo) - (b[`${props.kind}Order`] ?? b.slotNo)))
const fieldKey = field => `${field.scope}.${field.name}`
const columns = computed(() => useTableColumnWidths(`generic-task.${props.kind}`, Object.fromEntries([
  ...fixedColumns.value.map(key => [key, { width: key.endsWith('At') ? 180 : 150, minWidth: 100 }]),
  ...visibleFields.value.map(field => [fieldKey(field), { width: 150, minWidth: 100 }])
])))
const fieldLabel = field => `${field.labels?.[locale.value] || field.labels?.['en-US'] || field.name}${field.unit ? ` (${field.unit})` : ''}`
const canEditOrders = computed(() => canManage.value && (props.kind === 'plan' || mode.value === 'supplement'))
const canEditRemark = computed(() => !!form.value && (canEditOrders.value || (props.kind === 'performance' && ['admin', 'supervisor', 'operator'].includes(user.role))))
const canSupplement = computed(() => props.kind === 'performance' && canManage.value && user.hasPageAccess('plan.list') && record.value && !record.value.hasPlan && planFields.value)
const detailKeys = computed(() => props.kind === 'performance'
  ? ['createdAt', 'updatedAt', 'startedAt', 'completedAt', 'hasPlan']
  : ['createdAt', 'updatedAt'])

function displayValue(value) {
  if (value == null) return '—'
  return typeof value === 'boolean' ? tr(value ? 'yes' : 'no') : String(value)
}
function stateLabel(value) { return productionStates.includes(value) ? tr(`statuses.${value}`) : '—' }
function displayFixed(row, key) {
  // API 已返回固定业务时区的墙钟时间，只截取页面需要的秒级精度。
  if (key.endsWith('At')) return row[key] ? row[key].slice(0, 19).replace('T', ' ') : '—'
  return key === 'productionStatus' ? stateLabel(row[key]) : displayValue(row[key])
}
function fieldEditable(field) {
  if (canEditOrders.value) return field.planEditable
  return props.kind === 'performance' && field.performanceOwner === 'manual' && field.performanceEditable && canEditRemark.value
}
function showError(error) {
  const key = error.response?.data?.errorCode?.replace('task.', '')
  ElMessage.error(key && te(`${props.kind}.workflow.errors.${key}`) ? tr(`errors.${key}`) : tr('requestFailed'))
}
let loadId = 0
async function load() {
  const id = ++loadId
  loading.value = true
  try {
    const params = Object.fromEntries(Object.entries(filters).filter(([,v]) => v != null && v !== ''))
    const [config, result] = await Promise.all([props.api.getConfig(props.kind), props.api.list(params)])
    if (id !== loadId) return
    fields.value = config.fields
    configAvailable.value = true
    items.value = result.items
    total.value = result.total
  } catch (error) {
    if (id === loadId) showError(error)
  } finally {
    if (id === loadId) loading.value = false
  }
}
const loadConfigAndList = load
function search() { filters.page = 1; load() }
function resetFilters() { Object.assign(filters, defaults); load() }
function setForm(row) {
  const initial = { taskNo: row?.taskNo ?? '', targetKey: row?.targetKey ?? '', priority: row?.priority ?? 5,
    remark: row?.remark ?? null, productionStatus: row?.productionStatus ?? null, items: { ...row?.items }, backfillExisting: false }
  original.value = initial
  form.value = { ...initial, items: { ...initial.items } }
}
async function newPlan() {
  try {
    const config = await props.api.getConfig('plan')
    record.value = null
    formFields.value = config.fields.filter(f => f.enabled)
    setForm()
    mode.value = 'new'
    detailOpen.value = true
  } catch (error) { showError(error) }
}
async function openDetail(row) {
  try {
    const [value, config] = await Promise.all([props.api.detail(row.id), props.api.getConfig(props.kind)])
    record.value = value
    formFields.value = config.fields.filter(f => f.enabled)
    setForm(value)
    mode.value = 'view'
    planFields.value = null
    if (props.kind === 'performance' && canManage.value && user.hasPageAccess('plan.list') && !value.hasPlan) {
      try { planFields.value = (await props.api.getConfig('plan')).fields.filter(f => f.enabled) } catch { planFields.value = null }
    }
    detailOpen.value = true
  } catch (error) { showError(error) }
}
function startSupplement() {
  mode.value = 'supplement'
  formFields.value = planFields.value
  setForm({ taskNo: record.value.taskNo })
}
function changedValues() {
  const current = form.value
  const initial = original.value
  const body = { taskNo: current.taskNo }
  if (current.remark !== initial.remark) body.remark = current.remark
  if (canEditOrders.value) {
    if (current.targetKey && current.targetKey !== initial.targetKey) body.targetKey = current.targetKey
    if (Number.isInteger(current.priority) && current.priority !== initial.priority) body.priority = current.priority
    if (current.productionStatus && current.productionStatus !== initial.productionStatus) body.productionStatus = current.productionStatus
  }
  if (mode.value === 'supplement' && current.backfillExisting) body.backfillExisting = true
  const patch = Object.fromEntries(formFields.value.filter(field => {
    const value = current.items[field.name]
    return fieldEditable(field) && value !== undefined && value !== initial.items[field.name] && (value !== null || field.isNullable)
  }).map(field => [field.name, current.items[field.name]]))
  if (Object.keys(patch).length) body.items = patch
  return body
}
async function save() {
  saving.value = true
  try {
    const update = mode.value === 'supplement' ? props.api.upsertPlan : props.api.upsert
    await update(changedValues())
    detailOpen.value = false
    ElMessage.success(tr('saved'))
    await load()
  } catch (error) { showError(error) } finally { saving.value = false }
}
function closeDetail() { form.value = null; record.value = null }

watch(filters, value => {
  try { localStorage.setItem(filterKey, JSON.stringify(value)) } catch { /* 本机偏好不可用不影响查询。 */ }
}, { deep: true })
onMounted(load)
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
