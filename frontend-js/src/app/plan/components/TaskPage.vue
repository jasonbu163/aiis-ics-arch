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
          <el-tooltip :content="tr('resetWidthsHint')" placement="top" :trigger="['hover', 'focus']">
            <ActionButton @click="columns.reset">{{ tr('resetWidths') }}</ActionButton>
          </el-tooltip>
          <ActionButton :loading="loading" @click="load">{{ tr('refresh') }}</ActionButton>
        </div>
      </template>
      <div class="filter-section">
        <el-form class="filter-form" label-position="top" @submit.prevent="search">
          <div class="filter-keywords">
            <el-form-item :label="tr('taskNo')"><el-input v-model="filters.taskNo" clearable /></el-form-item>
            <el-form-item :label="tr('targetKey')"><el-input v-model="filters.targetKey" clearable /></el-form-item>
          </div>
          <div class="filter-conditions">
            <el-form-item :label="tr('productionStatus')"><el-select v-model="filters.productionStatus" clearable><el-option v-for="s in productionStates" :key="s" :value="s" :label="tr(`statuses.${s}`)" /></el-select></el-form-item>
            <el-form-item :label="tr('createdFrom')"><el-date-picker v-model="filters.createdFrom" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss[+08:00]" clearable /></el-form-item>
            <el-form-item :label="tr('createdTo')"><el-date-picker v-model="filters.createdTo" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss[+08:00]" clearable /></el-form-item>
            <el-form-item class="filter-actions"><ActionButton variant="primary" @click="search">{{ $t('common.search') }}</ActionButton><ActionButton @click="resetFilters">{{ $t('common.reset') }}</ActionButton></el-form-item>
          </div>
        </el-form>
      </div>
      <div class="table-scroll">
        <el-table :key="columns.version.value" v-loading="loading" :data="items" stripe border class="vibe-table" @header-dragend="columns.onHeaderDragEnd" @row-click="openDetail($event)">
          <el-table-column v-for="col in fixedColumns" :key="col" :prop="col" :label="tr(col)" :width="columns.widths[col]" :min-width="100" show-overflow-tooltip>
            <template #default="{ row }">{{ displayFixed(row, col) }}</template>
          </el-table-column>
          <el-table-column v-for="field in visibleFields" :key="fieldKey(field)" :prop="fieldKey(field)" :label="fieldLabel(field)" :width="columns.widths[fieldKey(field)]" :min-width="100" show-overflow-tooltip>
            <template #default="{ row }">{{ displayValue(row.items?.[field.name]) }}</template>
          </el-table-column>
          <el-table-column :label="tr('actions')" :width="canEditRecord ? 144 : 100" fixed="right">
            <template #default="{ row }">
              <div class="row-actions" :class="{ 'task-row-actions-pair': canEditRecord }" @click.stop>
                <ActionButton size="small" variant="row" class="task-row-detail" @click="openDetail(row)">{{ tr('detail') }}</ActionButton>
                <ActionButton v-if="canEditRecord" size="small" variant="row" @click="openDetail(row, 'edit')">{{ tr('dialog.edit') }}</ActionButton>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div class="pagination-scroll">
        <el-pagination v-model:current-page="filters.page" v-model:page-size="filters.pageSize" :page-sizes="[10,20,50,100]" :total="total" layout="total, sizes, prev, pager, next, jumper" class="pagination" @current-change="load" @size-change="load" />
      </div>
    </BaseCard>

    <el-dialog :model-value="detailOpen" :title="dialogTitle" width="min(760px, calc(100vw - 24px))"
      class="standard-form-dialog task-detail-dialog" align-center
      :show-close="false" :close-on-click-modal="false" :before-close="closeDetail">
      <template #header="{ titleId, titleClass }">
        <h2 :id="titleId" ref="dialogHeading" :class="titleClass" tabindex="-1">{{ dialogTitle }}</h2>
        <div v-if="mode === 'view' && canSupplement" class="detail-actions">
          <ActionButton @click="startSupplement">{{ tr('supplement') }}</ActionButton>
        </div>
      </template>
      <p v-if="detailLoading" class="detail-state" role="status">{{ tr('dialog.loading') }}</p>
      <div v-else-if="detailError" class="detail-load-error">
        <el-alert :title="detailError" type="error" :closable="false" show-icon />
        <ActionButton @click="openDetail(detailTarget, mode)">{{ tr('dialog.retry') }}</ActionButton>
      </div>
      <template v-else-if="record && mode === 'view'">
        <section class="detail-section">
          <h3>{{ tr('dialog.basic') }}</h3>
          <dl class="detail-grid">
            <div v-for="key in basicKeys" :key="key"><dt>{{ tr(key) }}</dt><dd>{{ displayFixed(record, key) }}</dd></div>
          </dl>
        </section>
        <section class="detail-section">
          <h3>{{ tr('dialog.business') }}</h3>
          <dl class="detail-grid">
            <div v-for="field in formFields" :key="fieldKey(field)">
              <dt>{{ fieldLabel(field) }}</dt><dd>{{ displayValue(record.items?.[field.name]) }}</dd>
            </div>
            <div class="detail-full"><dt>{{ tr('remark') }}</dt><dd>{{ displayValue(record.remark) }}</dd></div>
          </dl>
        </section>
        <section class="detail-section">
          <h3>{{ tr('dialog.times') }}</h3>
          <dl class="detail-grid">
            <div v-for="key in timeKeys" :key="key"><dt>{{ tr(key) }}</dt><dd>{{ displayFixed(record, key) }}</dd></div>
          </dl>
        </section>
      </template>
      <template v-else-if="form">
        <div v-if="saveError" ref="saveAlert" class="detail-save-error">
          <el-alert :title="saveError" type="error" :closable="false" show-icon />
        </div>
        <el-form label-position="top" :disabled="saving" @submit.prevent>
          <section class="detail-section">
            <h3>{{ tr('dialog.basic') }}</h3>
            <el-row :gutter="16" class="detail-form-row">
              <el-col :span="12"><el-form-item :label="tr('taskNo')" :required="mode === 'new'"><el-input v-model="form.taskNo" :disabled="mode !== 'new'" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item :label="tr('targetKey')"><el-input v-model="form.targetKey" :disabled="!canEditTarget" /></el-form-item></el-col>
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
            </el-row>
          </section>
          <section class="detail-section">
            <h3>{{ tr('dialog.business') }}</h3>
            <el-row :gutter="16" class="detail-form-row">
              <el-col v-for="field in formFields" :key="fieldKey(field)" :span="12">
                <el-form-item :label="fieldLabel(field)">
                  <el-input v-if="field.type === 'string'" v-model="form.items[field.name]" :maxlength="255" :disabled="!fieldEditable(field)" />
                  <el-input-number v-else-if="field.type === 'number'" v-model="form.items[field.name]" :precision="4" :disabled="!fieldEditable(field)" controls-position="right" />
                  <el-select v-else v-model="form.items[field.name]" :disabled="!fieldEditable(field)" :clearable="field.isNullable" @clear="form.items[field.name] = null">
                    <el-option :label="tr('yes')" :value="true" /><el-option :label="tr('no')" :value="false" />
                  </el-select>
                  <el-button v-if="mode !== 'new' && field.isNullable && fieldEditable(field)" link :disabled="saving" @click="form.items[field.name] = null">{{ tr('clearValue') }}</el-button>
                </el-form-item>
              </el-col>
              <el-col :span="24"><el-form-item :label="tr('remark')"><el-input v-model="form.remark" type="textarea" :maxlength="500" :disabled="!canEditRemark" /></el-form-item></el-col>
              <el-col v-if="mode === 'supplement'" :span="24">
                <div class="backfill-option">
                  <el-checkbox v-model="form.backfillExisting">{{ tr('backfillExisting') }}</el-checkbox>
                  <el-tooltip placement="top" :trigger="['hover', 'focus']" :trigger-keys="[]">
                    <template #content><div class="help-content">{{ tr('dialog.backfillHint') }}</div></template>
                    <button class="help-trigger" type="button" :aria-label="tr('dialog.backfillHint')"
                      @click="$event.currentTarget.focus()" @keydown.esc.stop="$event.currentTarget.blur()">
                      <el-icon><QuestionFilled /></el-icon>
                    </button>
                  </el-tooltip>
                </div>
              </el-col>
            </el-row>
          </section>
        </el-form>
      </template>
      <template #footer>
        <div class="detail-actions">
          <ActionButton v-if="mode === 'view'" @click="closeDetail">{{ $t('common.close') }}</ActionButton>
          <template v-else>
            <ActionButton :disabled="saving" @click="cancelEdit">{{ $t('common.cancel') }}</ActionButton>
            <ActionButton v-if="canEditRemark" variant="primary" :loading="saving" @click="save">{{ $t('common.save') }}</ActionButton>
          </template>
        </div>
      </template>
    </el-dialog>
  </div>
</template>
<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { onBeforeRouteLeave } from 'vue-router'
import { ElMessage } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { useTableColumnWidths } from '@/utils/tableColumnWidths'
import BaseCard from '@/components/common/BaseCard.vue'
import ActionButton from '@/components/common/ActionButton.vue'
import { useTaskPagePadding } from './useTaskPagePadding'

const props = defineProps({ kind: { type: String, required: true }, api: { type: Object, required: true } })
const { t, te, locale } = useI18n()
const tr = (key, params = {}) => t(`${props.kind}.workflow.${key}`, params)
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

const fields = ref([]), recordFields = ref([]), items = ref([]), total = ref(0)
const loading = ref(false), saving = ref(false), configAvailable = ref(false)
const detailOpen = ref(false)
const record = ref(null), form = ref(null), original = ref(null), mode = ref('view'), planFields = ref(null)
const detailTarget = ref(null), detailLoading = ref(false), detailError = ref(''), saveError = ref('')
const dialogHeading = ref(null), saveAlert = ref(null)
const formFields = computed(() => mode.value === 'supplement' ? planFields.value ?? [] : recordFields.value)
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
const canEditTarget = computed(() => canEditOrders.value && (mode.value !== 'edit' || !record.value?.targetKey))
const canEditRecord = computed(() => props.kind === 'plan'
  ? canManage.value
  : ['admin', 'supervisor', 'operator'].includes(user.role))
const canEditRemark = computed(() => !!form.value && (canEditOrders.value || canEditRecord.value))
const canSupplement = computed(() => props.kind === 'performance' && canManage.value && user.hasPageAccess('plan.list') && record.value && !record.value.hasPlan && planFields.value)
const basicKeys = computed(() => ['taskNo', 'targetKey', 'productionStatus', props.kind === 'plan' ? 'priority' : 'hasPlan'])
const timeKeys = computed(() => props.kind === 'performance'
  ? ['createdAt', 'updatedAt', 'lastObservedAt', 'startedAt', 'completedAt']
  : ['createdAt', 'updatedAt'])
const dialogTitle = computed(() => {
  if (mode.value === 'new') return tr('newPlan')
  const identity = record.value?.taskNo ?? detailTarget.value?.taskNo ?? detailTarget.value?.id
  const key = { view: 'viewTitle', edit: 'editTitle', supplement: 'supplementTitle' }[mode.value]
  return identity == null ? tr('detail') : tr(`dialog.${key}`, { taskNo: identity })
})

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
function errorLabel(error) {
  const key = error.response?.data?.errorCode?.replace('task.', '')
  return key && te(`${props.kind}.workflow.errors.${key}`) ? tr(`errors.${key}`) : tr('requestFailed')
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
    if (id === loadId) ElMessage.error(errorLabel(error))
  } finally {
    if (id === loadId) loading.value = false
  }
}
function search() { filters.page = 1; load() }
function resetFilters() { Object.assign(filters, defaults); load() }
function setForm(row) {
  const initial = { taskNo: row?.taskNo ?? '', targetKey: row?.targetKey ?? '', priority: row?.priority ?? 5,
    remark: row?.remark ?? null, productionStatus: row?.productionStatus ?? null, items: { ...row?.items }, backfillExisting: false }
  original.value = initial
  form.value = { ...initial, items: { ...initial.items } }
}
let intent = 0
function resetDetail(nextMode, target = null) {
  intent += 1
  mode.value = nextMode
  detailTarget.value = target
  record.value = null
  form.value = null
  original.value = null
  recordFields.value = []
  planFields.value = null
  detailLoading.value = false
  detailError.value = ''
  saveError.value = ''
  saving.value = false
  return intent
}
function closeDetail() {
  // 关闭时立即失效，淡出期间保留画面。每次打开初始化，不消费动画结束后的 model 更新。
  intent += 1
  detailOpen.value = false
  saving.value = false
  detailLoading.value = false
}
async function newPlan() {
  const id = resetDetail('new')
  detailOpen.value = false
  try {
    const config = await props.api.getConfig('plan')
    if (id !== intent) return
    recordFields.value = config.fields.filter(f => f.enabled)
    setForm()
    detailOpen.value = true
  } catch (error) {
    if (id === intent) ElMessage.error(errorLabel(error))
  }
}
async function openDetail(row, nextMode = 'view') {
  if (nextMode === 'edit' && !canEditRecord.value) return
  const id = resetDetail(nextMode, { id: row.id, taskNo: row.taskNo })
  detailLoading.value = true
  detailOpen.value = true
  try {
    const [value, config] = await Promise.all([props.api.detail(row.id), props.api.getConfig(props.kind)])
    if (id !== intent) return
    record.value = value
    recordFields.value = config.fields.filter(f => f.enabled)
    setForm(value)
  } catch (error) {
    if (id === intent) detailError.value = errorLabel(error)
    return
  } finally {
    if (id === intent) detailLoading.value = false
  }
  if (nextMode === 'view' && props.kind === 'performance' && canManage.value && user.hasPageAccess('plan.list') && !record.value.hasPlan) {
    try {
      const config = await props.api.getConfig('plan')
      if (id === intent) planFields.value = config.fields.filter(f => f.enabled)
    } catch { /* 实绩可继续查看，补建入口等待有效计划配置。 */ }
  }
}
function focusHeading() {
  const id = intent
  nextTick(() => { if (id === intent) dialogHeading.value?.focus() })
}
function startSupplement() {
  if (mode.value !== 'view' || !canSupplement.value) return
  mode.value = 'supplement'
  setForm({ taskNo: record.value.taskNo })
  focusHeading()
}
function cancelEdit() {
  if (saving.value) return
  if (mode.value !== 'supplement') {
    closeDetail()
    return
  }
  mode.value = 'view'
  saveError.value = ''
  setForm(record.value)
  focusHeading()
}
function changedValues() {
  const current = form.value
  const initial = original.value
  const body = { taskNo: current.taskNo }
  if (current.remark !== initial.remark) body.remark = current.remark
  if (canEditOrders.value) {
    if (canEditTarget.value && current.targetKey && current.targetKey !== initial.targetKey) body.targetKey = current.targetKey
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
  if (!detailOpen.value || mode.value === 'view' || saving.value || !canEditRemark.value) return
  const id = intent
  saving.value = true
  saveError.value = ''
  try {
    const update = mode.value === 'supplement' ? props.api.upsertPlan : props.api.upsert
    await update(changedValues())
    if (id !== intent) return
    closeDetail()
    ElMessage.success(tr('saved'))
    await load()
  } catch (error) {
    if (id !== intent) return
    if (mode.value === 'new') ElMessage.error(errorLabel(error))
    else {
      saveError.value = errorLabel(error)
      nextTick(() => { if (id === intent) saveAlert.value?.scrollIntoView({ block: 'nearest' }) })
    }
  } finally {
    if (id === intent) saving.value = false
  }
}

watch(filters, value => {
  try { localStorage.setItem(filterKey, JSON.stringify(value)) } catch { /* 本机偏好不可用不影响查询。 */ }
}, { deep: true })
onMounted(load)
onBeforeRouteLeave(closeDetail)
onBeforeUnmount(() => { closeDetail(); loadId += 1 })
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
.filter-form { display: flex; flex-wrap: wrap; gap: 12px; align-items: end; }
.filter-keywords, .filter-conditions { display: grid; min-width: 0; gap: 12px; align-items: end; }
.filter-keywords { flex: 1 1 240px; grid-template-columns: repeat(2, minmax(0, 1fr)); }
.filter-conditions {
  flex: 2 1 680px;
  grid-template-columns: minmax(110px, 1fr) repeat(2, minmax(180px, 1.4fr)) max-content;
}
.filter-form :deep(.el-form-item) { min-width: 0; margin-bottom: 0; }
.filter-form :deep(.el-form-item__label) { height: auto; line-height: 1.4; white-space: normal; overflow-wrap: anywhere; }
.filter-form :deep(.el-select), .filter-form :deep(.el-input), .filter-form :deep(.el-date-editor) { width: 100%; max-width: 100%; min-width: 0; }
.filter-actions :deep(.el-form-item__content) { display: flex; justify-content: flex-end; flex-wrap: wrap; gap: 8px; }
.filter-actions :deep(.el-button + .el-button) { margin-left: 0; }
.table-scroll { width: 100%; padding: 20px 24px 0; overflow-x: auto; }
.task-row-actions-pair { display: grid; grid-auto-flow: column; grid-auto-columns: 1fr; }
.task-row-detail.el-button {
  background: transparent;
  border-color: var(--border-strong);
  color: var(--text-secondary);
}
.task-row-detail.el-button:hover,
.task-row-detail.el-button:focus-visible {
  background: var(--bg-overlay);
  color: var(--text-primary);
}
.pagination-scroll { width: 100%; padding: 18px 24px 24px; overflow-x: auto; }
.pagination { display: flex; justify-content: flex-end; width: max-content; min-width: 100%; }
@container (max-width: 730px) {
  .filter-conditions { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .filter-conditions > :first-child, .filter-actions { grid-column: 1 / -1; }
}
@container (max-width: 440px) {
  .filter-conditions { grid-template-columns: minmax(0, 1fr); }
  .filter-actions :deep(.el-form-item__content) { justify-content: flex-start; }
}
@media (max-width: 600px) {
  .filter-section, .table-scroll, .pagination-scroll { padding-inline: 16px; }
}


:global(.task-detail-dialog.el-dialog) {
  --task-dialog-inset: clamp(16px, 4vw, 32px);
  display: flex;
  flex-direction: column;
  max-width: calc(100vw - 24px);
  padding: 0;
  max-height: calc(100dvh - 24px);
}
:global(.task-detail-dialog .el-dialog__header) {
  flex: none;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 8px 16px;
  min-height: 0;
  padding: 16px var(--task-dialog-inset);
}
:global(.task-detail-dialog .el-dialog__title) {
  min-width: 0;
  margin: 0;
  font-size: 16px;
  font-weight: 590;
  line-height: 1.35;
  overflow-wrap: anywhere;
}
:global(.task-detail-dialog .el-dialog__body) {
  min-height: 0;
  overflow: auto;
  overscroll-behavior: contain;
  padding: 18px var(--task-dialog-inset);
}
:global(.task-detail-dialog .el-dialog__footer) {
  flex: none;
  padding: 14px var(--task-dialog-inset);
}
.detail-actions { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 8px; margin-left: auto; }
.detail-actions :deep(.el-button + .el-button) { margin-left: 0; }
.detail-state { margin: 0; color: var(--text-secondary); }
.detail-load-error { display: grid; gap: 12px; justify-items: start; }
.detail-save-error { margin-bottom: 12px; }
.detail-section {
  min-width: 0;
  padding: 14px 16px;
  border: 1px solid var(--border-secondary);
  border-radius: 12px;
}
.detail-section + .detail-section { margin-top: 12px; }
.detail-section h3 { margin: 0 0 12px; color: var(--text-primary); font-size: 14px; font-weight: 590; }
.detail-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px 16px; margin: 0; }
.detail-grid dt { color: var(--text-secondary); overflow-wrap: anywhere; }
.detail-grid dd { margin: 4px 0 0; color: var(--text-primary); white-space: pre-wrap; overflow-wrap: anywhere; }
.detail-full { grid-column: 1 / -1; }
.detail-form-row :deep(.el-form-item__label) { height: auto; white-space: normal; overflow-wrap: anywhere; }
.detail-form-row :deep(.el-input-number), .detail-form-row :deep(.el-select) { width: 100%; }
.detail-form-row :deep(.el-checkbox), .detail-form-row :deep(.el-checkbox__label) { height: auto; white-space: normal; }
.backfill-option { display: flex; align-items: center; gap: 4px; }
@media (max-width: 520px) {
  .detail-grid { grid-template-columns: minmax(0, 1fr); }
  .detail-form-row :deep(.el-col-12) { flex: 0 0 100%; max-width: 100%; }
}
</style>
