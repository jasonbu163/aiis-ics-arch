<!-- 按任务、设备和采样组管理实时快照或过程历史。 -->
<template>
  <BaseCard class="record-card" :title="isHistory ? t('monitor.observation.processRecords') : tr('snapshots')">
    <template #actions>
      <div class="table-actions">
        <ActionButton :disabled="columnSaving" @click="openColumnSettings">{{ tr('columnSettings') }}</ActionButton>
        <el-tooltip :content="tr('resetWidths')" placement="top">
          <ActionButton @click="columns.reset">{{ tr('resetWidthsButton') }}</ActionButton>
        </el-tooltip>
      </div>
    </template>
    <form class="record-toolbar" @submit.prevent="search">
      <label>{{ tr('deviceOrSource') }}
        <el-select v-model="filters.equipmentId" clearable :placeholder="tr('allConfigs')" filterable>
          <el-option v-for="device in devices" :key="device.equipmentId" :value="device.equipmentId"
            :label="recordSourceLabel(device, locale.startsWith('en') ? device.nameEn : device.nameZh)" />
        </el-select>
      </label>
      <label>{{ tr('group') }} <el-input v-model="filters.groupKey" clearable /></label>
      <label>{{ tr('taskNo') }} <el-input v-model="filters.taskNo" clearable /></label>
      <label v-if="isHistory" class="record-toolbar__range">{{ tr('sampledAt') }}
        <el-date-picker v-model="range" type="datetimerange" value-format="YYYY-MM-DD HH:mm:ss"
          format="YYYY-MM-DD HH:mm:ss" :range-separator="'–'" />
      </label>
      <div class="table-actions">
        <ActionButton variant="primary" native-type="submit">{{ tr('search') }}</ActionButton>
        <ActionButton @click="resetFilters">{{ t('common.reset') }}</ActionButton>
      </div>
    </form>
    <el-alert v-if="failed || columnFailed" :title="t('equipment.observation.loadFailed')" type="error" show-icon :closable="false" />
    <el-table :key="columns.version.value" v-loading="loading" :data="items" border scrollbar-always-on
      @header-dragend="(...args) => resizeFlexibleColumn(columns, ...args)">
      <el-table-column prop="id" :label="t('equipment.observation.recordId')" :min-width="columns.widths.id" />
      <el-table-column prop="taskNo" :label="t('equipment.observation.taskNo')" :min-width="columns.widths.taskNo" />
      <el-table-column prop="equipmentId" :label="t('equipment.observation.deviceOrSource')" :min-width="columns.widths.equipmentId">
        <template #default="{ row }">{{ recordSourceLabel(row, row.equipmentId) }}</template>
      </el-table-column>
      <el-table-column prop="groupKeys" :label="t('equipment.observation.group')" :min-width="columns.widths.groupKeys">
        <template #default="{ row }">{{ row.groupKeys?.join(', ') || '—' }}</template>
      </el-table-column>
      <el-table-column prop="observedAt" :label="t('equipment.observation.sampledAt')" :min-width="columns.widths.observedAt">
        <template #default="{ row }">{{ formatShanghaiDateTime(row.observedAt) }}</template>
      </el-table-column>
      <el-table-column prop="quality" :label="t('equipment.observation.quality')" :min-width="columns.widths.quality">
        <template #default="{ row }">{{ qualityLabel(row.quality) }}</template>
      </el-table-column>
      <el-table-column v-if="isHistory" prop="reviewMark" :label="t('equipment.observation.reviewMark')" :min-width="columns.widths.reviewMark">
        <template #default="{ row }">{{ reviewLabel(row.reviewMark) }}</template>
      </el-table-column>
      <el-table-column v-for="field in visibleColumns" :key="field.metricKey" :prop="metricField(field.metricKey)"
        :label="metricTitle(field)" :min-width="columns.widths[metricField(field.metricKey)]">
        <template #default="{ row }">{{ metricValue(row, field.metricKey) }}</template>
      </el-table-column>
      <el-table-column :label="tr('actions')" width="88" fixed="right" :resizable="false">
        <template #default="{ row }"><div class="row-actions"><ActionButton size="small" variant="row" @click="open(row.id)">{{ t('equipment.observation.detail') }}</ActionButton></div></template>
      </el-table-column>
    </el-table>
    <el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="total, prev, pager, next"
      @current-change="load" />
    <el-dialog v-model="columnDialog" :title="tr('columnSettings')" class="standard-form-dialog record-column-dialog"
      :show-close="false" :close-on-click-modal="false" :close-on-press-escape="!columnSaving" width="min(760px, 94vw)">
      <template #header="{ titleId }">
        <div class="record-dialog-title">
          <h2 :id="titleId" class="el-dialog__title">{{ tr('columnSettings') }}</h2>
          <el-tooltip :content="tr('columnSettingsHint')" placement="top">
            <button type="button" class="record-dialog-help" :aria-label="tr('columnSettingsHint')">
              <el-icon><QuestionFilled /></el-icon>
            </button>
          </el-tooltip>
        </div>
        <el-tooltip :content="tr('resetWidths')" placement="top">
          <ActionButton @click="columnWidths.reset">{{ tr('resetWidthsButton') }}</ActionButton>
        </el-tooltip>
      </template>
      <form class="record-toolbar column-toolbar" @submit.prevent="searchColumnSettings">
        <label>{{ tr('group') }}
          <el-select v-model="columnFilters.group" :placeholder="tr('allConfigs')" clearable filterable>
            <el-option v-for="group in columnGroups" :key="group" :value="group" :label="group" />
          </el-select>
        </label>
        <label>{{ tr('columnVisible') }}
          <el-select v-model="columnFilters.visibility" :placeholder="tr('allConfigs')" clearable>
            <el-option value="shown" :label="tr('yes')" />
            <el-option value="hidden" :label="tr('no')" />
          </el-select>
        </label>
        <label class="record-toolbar__keyword">{{ tr('configKeyword') }}
          <el-input v-model="columnFilters.keyword" :placeholder="tr('columnKeywordPlaceholder')" clearable />
        </label>
        <div class="table-actions">
          <ActionButton variant="primary" native-type="submit">{{ tr('search') }}</ActionButton>
          <ActionButton @click="resetColumnSettings">{{ t('common.reset') }}</ActionButton>
        </div>
      </form>
      <div class="column-table-section">
        <el-alert v-if="columnSaveFailures.length" type="error" :closable="false" show-icon
          :title="tr('columnSaveFailed', { fields: columnSaveFailures.join(', ') })" />
        <el-table :key="columnWidths.version.value" :data="columnPageRows"
          :empty-text="tr(listColumns.length ? 'noMatchingConfigs' : 'empty')" row-key="metricKey" border scrollbar-always-on
          @header-dragend="columnWidths.onHeaderDragEnd">
          <el-table-column prop="metricKey" :label="tr('key')" :width="columnWidths.widths.metricKey" :min-width="140">
            <template #default="{ row }"><strong>{{ metricTitle(row) }}</strong><br><small>{{ row.groupKey }} · {{ row.metricKey }}</small></template>
          </el-table-column>
          <el-table-column prop="enabled" :label="tr('writeEnabled')" :width="columnWidths.widths.enabled" :min-width="100">
            <template #default="{ row }">{{ tr(row.enabled ? 'yes' : 'no') }}</template>
          </el-table-column>
          <el-table-column prop="listVisible" :label="tr('columnVisible')" :width="columnWidths.widths.listVisible" :min-width="95">
            <template #default="{ row }">
              <el-switch v-model="row.listVisible" :disabled="columnSaving" :aria-label="metricTitle(row) + ' · ' + tr('columnVisible')" />
            </template>
          </el-table-column>
          <el-table-column prop="listOrder" :label="tr('columnOrder')" :width="columnWidths.widths.listOrder" :min-width="176">
            <template #default="{ row }">
              <el-input-number class="column-order-input" :model-value="row.listOrder" :min="0" :max="2147483647" :precision="0" :disabled="columnSaving"
                :aria-label="metricTitle(row) + ' · ' + tr('columnOrder')" @change="row.listOrder = $event ?? null" />
            </template>
          </el-table-column>
        </el-table>
        <el-pagination v-model:current-page="columnPage" :page-size="columnPageSize" :total="filteredColumns.length"
          layout="total, prev, pager, next" :pager-count="5" />
      </div>
      <template #footer>
        <div class="core-dialog-footer">
          <ActionButton :disabled="columnSaving" @click="columnDialog = false">{{ tr('cancel') }}</ActionButton>
          <ActionButton variant="primary" :loading="columnSaving" @click="saveColumnSettings">{{ tr('save') }}</ActionButton>
        </div>
      </template>
    </el-dialog>
    <el-dialog v-model="dialog" :title="tr(isHistory ? 'historyDetail' : 'snapshotDetail')"
      class="standard-form-dialog record-detail-dialog" width="min(820px, 94vw)" align-center destroy-on-close
      :show-close="false" :close-on-click-modal="false" :close-on-press-escape="!saving">
      <template #header="{ titleId }">
        <h2 :id="titleId" class="el-dialog__title record-detail-title">{{ tr(isHistory ? 'historyDetail' : 'snapshotDetail') }}</h2>
        <el-tag v-if="detail" :type="detail.quality === 'good' ? 'success' : detail.quality === 'bad' ? 'danger' : 'info'">
          {{ tr('quality') }} · {{ qualityLabel(detail.quality) }}
        </el-tag>
      </template>
      <template v-if="detail">
        <section class="record-detail-section">
          <h3>{{ tr('recordOverview') }}</h3>
          <dl class="record-detail-facts">
            <div><dt>{{ tr('recordId') }}</dt><dd>{{ detail.id }}</dd></div>
            <div><dt>{{ tr('taskNo') }}</dt><dd>{{ detail.taskNo }}</dd></div>
            <div><dt>{{ tr('deviceOrSource') }}</dt><dd>{{ recordSourceLabel(detail, detail.equipmentId) }}</dd></div>
            <div><dt>{{ tr('sampledAtShanghai') }}</dt><dd>{{ formatShanghaiDateTime(detail.observedAt) }}</dd></div>
            <div><dt>{{ tr('group') }}</dt><dd>{{ detail.groupKeys?.join(', ') || '—' }}</dd></div>
          </dl>
        </section>
        <section class="record-detail-section">
          <div class="record-detail-heading">
            <h3>{{ tr('sampleValues') }} <small>· {{ tr('detailMetricCount', { count: detail.values?.length ?? 0 }) }}</small></h3>
            <el-tooltip :content="tr('resetWidths')" placement="top">
              <ActionButton size="small" @click="detailColumns.reset">{{ tr('resetWidthsButton') }}</ActionButton>
            </el-tooltip>
          </div>
          <el-table :key="detailColumns.version.value" :data="detail.values" border scrollbar-always-on
            @header-dragend="(...args) => resizeFlexibleColumn(detailColumns, ...args)">
            <el-table-column prop="nameZh" :label="tr('detailMetric')" :min-width="detailColumns.widths.nameZh">
              <template #default="{ row }">{{ metricTitle(row) }}</template>
            </el-table-column>
            <el-table-column prop="metricKey" :label="tr('key')" :min-width="detailColumns.widths.metricKey" />
            <el-table-column prop="value" :label="tr('value')" :min-width="detailColumns.widths.value" align="right">
              <template #default="{ row }"><strong>{{ String(row.value) }}</strong></template>
            </el-table-column>
          </el-table>
          <details class="record-detail-source">
            <summary>{{ tr('detailSource') }}</summary>
            <dl class="record-detail-facts">
              <div><dt>{{ tr('detailProducer') }}</dt><dd>{{ detail.producerId || '—' }}</dd></div>
              <div><dt>{{ tr('detailMapping') }}</dt><dd>{{ detail.mappingId || '—' }}</dd></div>
              <div><dt>{{ tr('detailMappingRevision') }}</dt><dd>{{ detail.mappingRevision || '—' }}</dd></div>
            </dl>
            <pre v-if="detail.sourceRefs != null">{{ JSON.stringify(detail.sourceRefs, null, 2) }}</pre>
          </details>
        </section>
        <section class="record-detail-section">
          <h3>{{ tr('managementRecord') }}</h3>
          <el-form label-position="top" class="dialog-form-grid record-detail-form" :class="{ 'is-history': isHistory }">
            <el-form-item :label="tr('remark')"><el-input v-model="edit.remark" type="textarea" /></el-form-item>
            <el-form-item v-if="isHistory" :label="tr('reviewMark')">
              <el-select v-model="edit.reviewMark" clearable>
                <el-option value="abnormal" :label="tr('abnormal')" />
                <el-option value="reviewed" :label="tr('reviewed')" />
              </el-select>
            </el-form-item>
          </el-form>
        </section>
      </template>
      <template #footer>
        <div class="core-dialog-footer">
          <ActionButton :disabled="saving" @click="dialog = false">{{ tr('cancel') }}</ActionButton>
          <ActionButton variant="primary" :loading="saving" @click="save">{{ tr('save') }}</ActionButton>
        </div>
      </template>
    </el-dialog>
  </BaseCard>
</template>

<script setup>
import { computed, onMounted, reactive, ref, shallowRef, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { QuestionFilled } from '@element-plus/icons-vue'
import BaseCard from '@/components/common/BaseCard.vue'
import ActionButton from '@/components/common/ActionButton.vue'
import { formatShanghaiDateTime, shanghaiInputToRfc3339 } from '@/utils/date'
import { useTableColumnWidths } from '@/utils/tableColumnWidths'
import { equipmentOptions, latestList, latestDetail, updateLatest, observationListColumns, updateBinding } from '../../api/observations'
import { monitorOptions, historyList, historyDetail, updateHistory } from '@/app/monitor/api/observations'
import { metricField, metricTitle as localizedMetricTitle, metricValue, sourceLabel } from './columnModel'

const props = defineProps({ target: { type: String, required: true } })
const isHistory = computed(() => props.target === 'history')
const { t, locale } = useI18n()
const tr = (key, params) => t(`equipment.observation.${key}`, params)
const fixedColumns = {
  id: { width: 100, minWidth: 80 },
  taskNo: { width: 150, minWidth: 120 }, equipmentId: { width: 150, minWidth: 120 },
  groupKeys: { width: 140, minWidth: 110 }, observedAt: { width: 190, minWidth: 170 },
  quality: { width: 120, minWidth: 110 }, reviewMark: { width: 130, minWidth: 110 }
}
const columns = shallowRef(useTableColumnWidths(`observation.${props.target}`, fixedColumns))
const detailColumns = useTableColumnWidths(`observation.${props.target}.detail`, {
  metricKey: { width: 190, minWidth: 140 }, nameZh: { width: 180, minWidth: 140 },
  value: { width: 130, minWidth: 100 }
})
const columnWidthDefaults = {
  metricKey: { width: 235, minWidth: 140 }, enabled: { width: 115, minWidth: 100 },
  listVisible: { width: 105, minWidth: 95 }, listOrder: { width: 184, minWidth: 176 }
}
const columnWidths = shallowRef(useTableColumnWidths(`observation.${props.target}.column-settings`, columnWidthDefaults))
const filters = reactive({ equipmentId: '', groupKey: '', taskNo: '' })
const range = ref(null)
let submittedFilters = {}
const devices = ref([])
const items = ref([])
const page = ref(1)
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const failed = ref(false)
const columnFailed = ref(false)
const dialog = ref(false)
const columnDialog = ref(false)
const columnSaving = ref(false)
const listColumns = ref([])
const visibleColumns = computed(() => listColumns.value.filter(field => field.listVisible))
const columnDraft = ref([])
const columnFilters = reactive({ group: '', visibility: '', keyword: '' })
const appliedColumnFilters = ref({})
const columnSaveFailures = ref([])
const columnPage = ref(1)
const columnPageSize = 8
const columnGroups = computed(() => [...new Set(columnDraft.value.map(field => field.groupKey))])
const filteredColumns = computed(() => {
  const { group, matchingVisibility, keyword } = appliedColumnFilters.value
  return columnDraft.value.filter(field => (!group || field.groupKey === group) &&
    (!matchingVisibility || matchingVisibility.has(field.metricKey)) &&
    (!keyword || [field.metricKey, field.nameZh, field.nameEn].some(value => value?.toLowerCase().includes(keyword))))
})
const columnPageRows = computed(() => filteredColumns.value.slice((columnPage.value - 1) * columnPageSize, columnPage.value * columnPageSize))
const detail = ref(null)
const edit = reactive({ remark: '', reviewMark: '' })
let generation = 0
let detailGeneration = 0
let columnGeneration = 0

function recordSourceLabel(row, fallback) {
  const label = sourceLabel(row, fallback)
  return row.sourceDeleted ? t('equipment.observation.deletedSource', { label }) : label
}

function resizeFlexibleColumn(layout, newWidth, oldWidth, column) {
  // 只保存拖动的变化量，剩余空间由表格重新分配。
  const preferredWidth = layout.widths[column.property] + newWidth - oldWidth
  layout.onHeaderDragEnd(preferredWidth, oldWidth, column)
  column.width = undefined
}

function metricTitle(field) { return localizedMetricTitle(field, locale.value) }
async function loadColumns() {
  const current = ++columnGeneration
  const target = props.target
  try {
    const result = await observationListColumns(target)
    if (current !== columnGeneration || target !== props.target) return
    listColumns.value = result.items
    columnFailed.value = false
    const fields = Object.fromEntries(result.items.map(field => [metricField(field.metricKey), { width: 160, minWidth: 120 }]))
    columns.value = useTableColumnWidths(`observation.${target}`, { ...fixedColumns, ...fields })
  } catch { if (current === columnGeneration) columnFailed.value = true }
}
function openColumnSettings() {
  columnDraft.value = listColumns.value.map(field => ({ ...field }))
  columnSaveFailures.value = []
  resetColumnSettings()
  columnDialog.value = true
}
function searchColumnSettings() {
  const { group, visibility, keyword } = columnFilters
  const matchingVisibility = visibility
    ? new Set(columnDraft.value.filter(field => field.listVisible === (visibility === 'shown')).map(field => field.metricKey))
    : null
  appliedColumnFilters.value = { group, matchingVisibility, keyword: keyword.trim().toLowerCase() }
  columnPage.value = 1
}
function resetColumnSettings() {
  Object.assign(columnFilters, { group: '', visibility: '', keyword: '' })
  searchColumnSettings()
}
async function saveColumnSettings() {
  if (columnSaving.value) return
  const target = props.target
  const originals = new Map(listColumns.value.map(field => [field.metricKey, field]))
  const edits = columnDraft.value.flatMap(field => {
    const before = originals.get(field.metricKey)
    if (!before) return []
    const changes = {}
    if (before.listVisible !== field.listVisible) changes.listVisible = field.listVisible
    if (before.listOrder !== field.listOrder) changes.listOrder = field.listOrder
    return Object.keys(changes).length ? [{ field, changes }] : []
  })
  if (!edits.length) { columnDialog.value = false; return }
  columnSaving.value = true
  columnSaveFailures.value = []
  const saved = new Map(), failures = []
  try {
    for (const { field, changes } of edits) {
      try {
        await updateBinding(target, field.groupKey, field.slotNo, changes)
        saved.set(field.metricKey, changes)
      } catch { failures.push(field.metricKey) }
    }
    if (props.target !== target) return
    listColumns.value = listColumns.value.map(field => ({ ...field, ...saved.get(field.metricKey) })).sort((a, b) =>
      (a.listOrder ?? Infinity) - (b.listOrder ?? Infinity) || a.groupKey.localeCompare(b.groupKey) || a.metricKey.localeCompare(b.metricKey))
    columnSaveFailures.value = failures
    if (!failures.length) columnDialog.value = false
  } finally { columnSaving.value = false }
}

function reviewLabel(value) {
  if (value === 'abnormal') return t('equipment.observation.abnormal')
  if (value === 'reviewed') return t('equipment.observation.reviewed')
  return value ?? ''
}

function qualityLabel(value) {
  if (value === 'good') return t('equipment.observation.qualityGood')
  if (value === 'bad') return t('equipment.observation.qualityBad')
  if (value === 'unknown') return t('equipment.observation.qualityUnknown')
  return value ?? '—'
}

async function load() {
  const current = ++generation
  loading.value = true
  const params = { ...submittedFilters, page: page.value, pageSize: 20 }
  try {
    const result = await (isHistory.value ? historyList(params) : latestList(params))
    if (current === generation) { items.value = result.items; total.value = result.total; failed.value = false }
  } catch { if (current === generation) failed.value = true }
  finally { if (current === generation) loading.value = false }
}
function search() {
  submittedFilters = Object.fromEntries(Object.entries(filters).filter(([, value]) => value))
  if (isHistory.value && range.value?.length === 2) {
    submittedFilters.from = shanghaiInputToRfc3339(range.value[0])
    submittedFilters.to = shanghaiInputToRfc3339(range.value[1])
  }
  page.value = 1
  detailGeneration++
  dialog.value = false
  return load()
}
function resetFilters() {
  Object.assign(filters, { equipmentId: '', groupKey: '', taskNo: '' })
  range.value = null
  search()
}
async function open(id) {
  const current = ++detailGeneration
  try {
    const value = await (isHistory.value ? historyDetail(id) : latestDetail(id))
    if (current !== detailGeneration) return
    detail.value = value
    edit.remark = value.remark || ''
    edit.reviewMark = value.reviewMark || ''
    dialog.value = true
  } catch { if (current === detailGeneration) failed.value = true }
}
async function save() {
  if (!detail.value) return
  saving.value = true
  try {
    const payload = { remark: edit.remark || null }
    if (isHistory.value) payload.reviewMark = edit.reviewMark || null
    await (isHistory.value ? updateHistory(detail.value.id, payload) : updateLatest(detail.value.id, payload))
    dialog.value = false
    await load()
  } finally { saving.value = false }
}
watch(filteredColumns, rows => {
  columnPage.value = Math.min(columnPage.value, Math.max(1, Math.ceil(rows.length / columnPageSize)))
})
watch(() => props.target, target => {
  columnWidths.value = useTableColumnWidths(`observation.${target}.column-settings`, columnWidthDefaults)
  generation++; detailGeneration++; columnGeneration++
  submittedFilters = {}
  items.value = []; listColumns.value = []; page.value = 1; total.value = 0
  dialog.value = false; columnDialog.value = false
  loadColumns(); load()
})
onMounted(async () => {
  try { devices.value = await (isHistory.value ? monitorOptions(true) : equipmentOptions(true)); await Promise.all([load(), loadColumns()]) }
  catch { failed.value = true }
})
</script>

<style scoped>
.record-card { height: auto; min-width: 0; }
.record-card :deep(.base-card__header) { flex-wrap: wrap; padding-block: 10px; }
.record-card :deep(.base-card__actions) { min-width: 0; max-width: 100%; }
.record-toolbar {
  --record-inset: var(--space-lg);
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 10px 16px;
  margin: 0 calc(-1 * var(--record-inset)) 16px;
  padding: 0 var(--record-inset) 16px;
  border-bottom: 1px solid var(--border-secondary);
}
.record-toolbar label { display: grid; gap: 6px; flex: 1 1 130px; min-width: 0; color: var(--text-secondary); }
.record-toolbar .record-toolbar__range { flex-basis: 310px; }
.record-toolbar .record-toolbar__keyword { flex-grow: 1.5; }
.record-toolbar :deep(.el-date-editor), .record-toolbar :deep(.el-select) { width: 100%; }
.record-toolbar .table-actions { margin-inline-start: auto; }
:global(.record-column-dialog.el-dialog) {
  --column-dialog-inset: 24px;
  max-width: calc(100vw - 24px);
  padding: 0;
}
:global(:is(.record-column-dialog, .record-detail-dialog) .el-dialog__header) {
  flex: none;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px 16px;
  min-height: 68px;
  padding: 10px var(--space-lg);
}
:global(.record-column-dialog .el-dialog__body) { padding: 0; }
:global(.record-column-dialog .el-dialog__footer) { padding: 16px var(--column-dialog-inset); }
.record-toolbar.column-toolbar { margin: 0; padding: 16px var(--column-dialog-inset); }
.column-table-section { min-width: 0; padding: 16px var(--column-dialog-inset); }
.column-order-input { width: 100%; max-width: 150px; }
.record-dialog-title, .record-detail-heading { display: flex; align-items: center; gap: 8px; }
.record-dialog-title h2.el-dialog__title, h2.record-detail-title.el-dialog__title {
  margin: 0;
  font-size: 16px;
  font-weight: 590;
  line-height: 1.35;
}
.record-detail-heading h3 { margin: 0; }
.record-detail-heading { justify-content: space-between; gap: 12px; margin-bottom: 8px; }
:global(.record-detail-dialog.el-dialog) {
  --detail-inset: 24px;
  display: flex;
  flex-direction: column;
  max-width: calc(100vw - 24px);
  max-height: calc(100dvh - 24px);
  padding: 0;
}
:global(.record-detail-dialog .el-dialog__body) {
  min-height: 0;
  padding: 0;
  overflow: auto;
  overscroll-behavior: contain;
}
:global(.record-detail-dialog .el-dialog__footer) {
  flex: none;
  padding: 12px var(--detail-inset);
}
.record-detail-title { min-width: 0; overflow-wrap: anywhere; }
.record-detail-heading small { color: var(--text-secondary); }
.record-detail-section { min-width: 0; padding: 14px var(--detail-inset); }
.record-detail-section + .record-detail-section { border-top: 1px solid var(--border-secondary); }
.record-detail-section h3 { margin: 0 0 8px; font-size: 15px; }
.record-detail-section .record-detail-heading h3 { margin: 0; }
.record-detail-facts {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px 16px;
  margin: 0;
  padding: 10px 12px;
  border: 1px solid var(--border-secondary);
  border-radius: 10px;
  background: var(--bg-secondary);
}
.record-detail-facts dt { color: var(--text-secondary); font-size: 12px; }
.record-detail-facts dd { margin: 2px 0 0; overflow-wrap: anywhere; }
.record-detail-source { margin-top: 10px; }
.record-detail-source summary { width: fit-content; color: var(--text-secondary); cursor: pointer; }
.record-detail-source .record-detail-facts { margin-top: 8px; }
.record-detail-source pre { margin-bottom: 0; padding: 8px; background: var(--bg-secondary); border-radius: 8px; }
.record-detail-form { grid-template-columns: minmax(0, 1fr); }
.record-detail-form.is-history { grid-template-columns: minmax(0, 1fr) minmax(140px, 25%); }
.record-detail-form :deep(.el-form-item) { margin-bottom: 0; }
.record-dialog-help { display: inline-grid; place-items: center; border: 0; background: transparent; color: var(--text-secondary); cursor: pointer; }
.el-pagination { margin-top: 14px; max-width: 100%; overflow-x: auto; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; }
@media (max-width: 768px) {
  :global(:is(.record-column-dialog, .record-detail-dialog) .el-dialog__header) {
    min-height: 60px;
    padding-inline: 18px;
  }
  :global(.record-column-dialog.el-dialog) { --column-dialog-inset: 12px; }
  :global(.record-detail-dialog.el-dialog) { --detail-inset: 14px; }
  .record-detail-facts { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .record-detail-form.is-history { grid-template-columns: minmax(0, 1fr); }
  .record-toolbar:not(.column-toolbar) { --record-inset: 18px; }
  .record-toolbar .record-toolbar__range { flex-basis: 100%; }
}
</style>
