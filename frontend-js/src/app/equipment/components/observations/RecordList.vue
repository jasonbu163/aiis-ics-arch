<!-- 按任务、设备和采样组管理实时快照或过程历史。 -->
<template>
  <div>
    <div class="record-toolbar">
      <el-select v-model="filters.equipmentId" clearable :placeholder="t('equipment.observation.device')" filterable>
        <el-option v-for="device in devices" :key="device.equipmentId" :value="device.equipmentId"
          :label="locale.startsWith('en') ? device.nameEn : device.nameZh" />
      </el-select>
      <el-input v-model="filters.groupKey" clearable :placeholder="t('equipment.observation.group')" />
      <el-input v-model="filters.taskNo" clearable :placeholder="t('equipment.observation.taskNo')" />
      <el-date-picker v-if="isHistory" v-model="range" type="datetimerange" value-format="YYYY-MM-DD HH:mm:ss"
        format="YYYY-MM-DD HH:mm:ss" :range-separator="'–'" />
      <ActionButton variant="primary" @click="search">{{ t('equipment.observation.search') }}</ActionButton>
      <ActionButton @click="columnDialog = true">{{ t('equipment.observation.columnSettings') }}</ActionButton>
      <ActionButton @click="columns.reset">{{ t('equipment.observation.resetWidths') }}</ActionButton>
    </div>
    <el-alert v-if="failed || columnFailed" :title="t('equipment.observation.loadFailed')" type="error" show-icon :closable="false" />
    <el-table :key="columns.version.value" v-loading="loading" :data="items" border
      @header-dragend="columns.onHeaderDragEnd">
      <el-table-column prop="id" :label="t('equipment.observation.recordId')" :width="columns.widths.id" :min-width="80" />
      <el-table-column prop="taskNo" :label="t('equipment.observation.taskNo')" :width="columns.widths.taskNo" :min-width="120" />
      <el-table-column prop="equipmentId" :label="t('equipment.observation.device')" :width="columns.widths.equipmentId" :min-width="120" />
      <el-table-column prop="groupKeys" :label="t('equipment.observation.group')" :width="columns.widths.groupKeys" :min-width="110">
        <template #default="{ row }">{{ row.groupKeys?.join(', ') || '—' }}</template>
      </el-table-column>
      <el-table-column prop="observedAt" :label="t('equipment.observation.sampledAt')" :width="columns.widths.observedAt" :min-width="170">
        <template #default="{ row }">{{ formatShanghaiDateTime(row.observedAt) }}</template>
      </el-table-column>
      <el-table-column prop="quality" :label="t('equipment.observation.quality')" :width="columns.widths.quality" :min-width="110">
        <template #default="{ row }">{{ qualityLabel(row.quality) }}</template>
      </el-table-column>
      <el-table-column v-if="isHistory" prop="reviewMark" :label="t('equipment.observation.reviewMark')" :width="columns.widths.reviewMark" :min-width="110">
        <template #default="{ row }">{{ reviewLabel(row.reviewMark) }}</template>
      </el-table-column>
      <el-table-column v-for="field in visibleColumns" :key="field.metricKey" :prop="metricField(field.metricKey)"
        :label="metricTitle(field)" :width="columns.widths[metricField(field.metricKey)]" :min-width="120">
        <template #default="{ row }">{{ metricValue(row, field.metricKey) }}</template>
      </el-table-column>
      <el-table-column :label="t('equipment.observation.actions')" width="120">
        <template #default="{ row }"><div class="row-actions"><ActionButton size="small" variant="row" @click="open(row.id)">{{ t('equipment.observation.detail') }}</ActionButton></div></template>
      </el-table-column>
    </el-table>
    <el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="total, prev, pager, next"
      @current-change="load" />
    <el-dialog v-model="columnDialog" :title="t('equipment.observation.columnSettings')" width="min(760px, 94vw)">
      <p>{{ t('equipment.observation.columnSettingsHint') }}</p>
      <div v-if="!listColumns.length">{{ t('equipment.observation.empty') }}</div>
      <div v-for="field in listColumns" :key="field.metricKey" class="column-setting">
        <div><strong>{{ metricTitle(field) }}</strong><br><small>{{ field.groupKey }} · {{ field.metricKey }}</small></div>
        <span>{{ t('equipment.observation.writeEnabled') }}: {{ t(field.enabled ? 'equipment.observation.yes' : 'equipment.observation.no') }}</span>
        <label>{{ t('equipment.observation.columnVisible') }} <el-switch :model-value="field.listVisible" :disabled="columnSaving"
          :aria-label="t('equipment.observation.columnVisible')" @change="setColumn(field, { listVisible: $event })" /></label>
        <label>{{ t('equipment.observation.columnOrder') }} <el-input-number :model-value="field.listOrder" :min="0" :max="2147483647" :disabled="columnSaving"
          :aria-label="t('equipment.observation.columnOrder')" @change="setColumn(field, { listOrder: $event ?? null })" /></label>
      </div>
      <template #footer><ActionButton @click="columnDialog = false">{{ t('equipment.observation.close') }}</ActionButton></template>
    </el-dialog>
    <el-dialog v-model="dialog" :title="t('equipment.observation.detail')" class="standard-form-dialog" width="min(760px, 94vw)">
      <template v-if="detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="t('equipment.observation.taskNo')">{{ detail.taskNo }}</el-descriptions-item>
          <el-descriptions-item :label="t('equipment.observation.device')">{{ detail.equipmentId }}</el-descriptions-item>
          <el-descriptions-item :label="t('equipment.observation.group')">{{ detail.groupKeys?.join(', ') || '—' }}</el-descriptions-item>
          <el-descriptions-item :label="t('equipment.observation.sampledAt')">{{ formatShanghaiDateTime(detail.observedAt) }}</el-descriptions-item>
          <el-descriptions-item :label="t('equipment.observation.quality')">{{ qualityLabel(detail.quality) }}</el-descriptions-item>
        </el-descriptions>
        <div class="table-actions"><ActionButton @click="detailColumns.reset">{{ t('equipment.observation.resetWidths') }}</ActionButton></div>
        <el-table :key="detailColumns.version.value" :data="detail.values" border @header-dragend="detailColumns.onHeaderDragEnd">
          <el-table-column prop="metricKey" :label="t('equipment.observation.key')" :width="detailColumns.widths.metricKey" :min-width="140" />
          <el-table-column prop="nameZh" :label="t(locale.startsWith('en') ? 'equipment.observation.nameEn' : 'equipment.observation.nameZh')" :width="detailColumns.widths.nameZh" :min-width="140">
            <template #default="{ row }">{{ locale.startsWith('en') ? row.nameEn : row.nameZh }}<span v-if="row.unit"> ({{ row.unit }})</span></template>
          </el-table-column>
          <el-table-column prop="value" :label="t('equipment.observation.value')" :width="detailColumns.widths.value" :min-width="100">
            <template #default="{ row }">{{ String(row.value) }}</template>
          </el-table-column>
        </el-table>
        <el-collapse>
          <el-collapse-item :title="t('equipment.observation.source')">
            <div>{{ detail.producerId }} · {{ detail.mappingId }} · {{ detail.mappingRevision }}</div>
            <pre>{{ JSON.stringify(detail.sourceRefs, null, 2) }}</pre>
          </el-collapse-item>
        </el-collapse>
        <el-form label-position="top">
          <el-form-item :label="t('equipment.observation.remark')"><el-input v-model="edit.remark" type="textarea" /></el-form-item>
          <el-form-item v-if="isHistory" :label="t('equipment.observation.reviewMark')">
            <el-select v-model="edit.reviewMark" clearable>
              <el-option value="abnormal" :label="t('equipment.observation.abnormal')" />
              <el-option value="reviewed" :label="t('equipment.observation.reviewed')" />
            </el-select>
          </el-form-item>
        </el-form>
      </template>
      <template #footer>
        <ActionButton @click="dialog = false">{{ t('equipment.observation.cancel') }}</ActionButton>
        <ActionButton variant="primary" :loading="saving" @click="save">{{ t('equipment.observation.save') }}</ActionButton>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, shallowRef, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import ActionButton from '@/components/common/ActionButton.vue'
import { formatShanghaiDateTime, shanghaiInputToRfc3339 } from '@/utils/date'
import { useTableColumnWidths } from '@/utils/tableColumnWidths'
import { equipmentOptions, latestList, latestDetail, updateLatest, observationListColumns, updateBinding } from '../../api/observations'
import { monitorOptions, historyList, historyDetail, updateHistory } from '@/app/monitor/api/observations'
import { metricField, metricTitle as localizedMetricTitle, metricValue } from './columnModel'

const props = defineProps({ target: { type: String, required: true } })
const isHistory = computed(() => props.target === 'history')
const { t, locale } = useI18n()
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
const filters = reactive({ equipmentId: '', groupKey: '', taskNo: '' })
const range = ref(null)
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
const detail = ref(null)
const edit = reactive({ remark: '', reviewMark: '' })
let generation = 0
let detailGeneration = 0
let columnGeneration = 0

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
async function setColumn(field, changes) {
  const target = props.target
  columnSaving.value = true
  try {
    await updateBinding(target, field.groupKey, field.slotNo, changes)
    if (target === props.target) await loadColumns()
  } catch { columnFailed.value = true }
  finally { columnSaving.value = false }
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
  const params = { page: page.value, pageSize: 20 }
  for (const [key, value] of Object.entries(filters)) if (value) params[key] = value
  if (isHistory.value && range.value?.length === 2) {
    params.from = shanghaiInputToRfc3339(range.value[0])
    params.to = shanghaiInputToRfc3339(range.value[1])
  }
  try {
    const result = await (isHistory.value ? historyList(params) : latestList(params))
    if (current === generation) { items.value = result.items; total.value = result.total; failed.value = false }
  } catch { if (current === generation) failed.value = true }
  finally { if (current === generation) loading.value = false }
}
function search() { page.value = 1; load() }
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
watch([() => filters.equipmentId, () => filters.groupKey, () => filters.taskNo, range], () => {
  generation++
  detailGeneration++
  items.value = []
  total.value = 0
  loading.value = false
  detail.value = null
  dialog.value = false
})
watch(() => props.target, () => {
  generation++; detailGeneration++; columnGeneration++
  items.value = []; listColumns.value = []; page.value = 1; total.value = 0
  dialog.value = false; columnDialog.value = false
  loadColumns(); load()
})
onMounted(async () => {
  try { devices.value = await (isHistory.value ? monitorOptions() : equipmentOptions()); await Promise.all([load(), loadColumns()]) }
  catch { failed.value = true }
})
</script>

<style scoped>
.record-toolbar { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 14px; }
.record-toolbar .el-select, .record-toolbar .el-input { width: 180px; }
.el-pagination { margin-top: 14px; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; }
.column-setting { display: grid; grid-template-columns: minmax(180px, 1fr) auto auto 180px; align-items: center; gap: 14px; padding: 10px 0; border-bottom: 1px solid var(--el-border-color); }
.column-setting label { display: grid; gap: 4px; }
.column-setting small { color: var(--el-text-color-secondary); }
@media (max-width: 640px) { .column-setting { grid-template-columns: 1fr auto; } }
</style>
