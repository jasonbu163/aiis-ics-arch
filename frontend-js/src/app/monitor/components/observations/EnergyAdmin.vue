<!-- 管理员按表计配置指标并只标注不可改写的能耗样本。 -->
<template>
  <BaseCard v-bind="cardProps">
    <template v-if="kind === 'config'" #actions>
      <div class="table-actions">
        <ActionButton variant="primary" :disabled="!meters.length || saving || loading || failed" @click="openConfig()">{{ tr('add') }}</ActionButton>
        <el-tooltip :content="tr('resetWidths')" placement="top">
          <ActionButton @click="widths.reset">{{ tr('resetWidthsButton') }}</ActionButton>
        </el-tooltip>
      </div>
    </template>
    <template v-else #actions>
      <el-tooltip :content="tr('resetWidths')" placement="top">
        <ActionButton @click="widths.reset">{{ tr('resetWidthsButton') }}</ActionButton>
      </el-tooltip>
    </template>
    <el-form v-if="kind === 'config'" class="config-toolbar" label-position="top" @submit.prevent="searchConfig">
      <el-form-item :label="t('monitor.observation.meter')">
        <el-select v-model="draft.meter" clearable :placeholder="tr('allConfigs')">
          <el-option v-for="item in meters" :key="item.meterId" :value="item.meterId" :label="meterLabel(item.meterId)" />
        </el-select>
      </el-form-item>
      <el-form-item :label="tr('group')"><el-input v-model="draft.group" clearable /></el-form-item>
      <el-form-item class="config-toolbar__keyword" :label="tr('configKeyword')"><el-input v-model="draft.keyword" clearable /></el-form-item>
      <el-form-item class="config-toolbar__actions">
        <div class="table-actions">
          <ActionButton variant="primary" @click="searchConfig">{{ tr('search') }}</ActionButton>
          <ActionButton @click="resetConfigFilters">{{ t('common.reset') }}</ActionButton>
        </div>
      </el-form-item>
    </el-form>
    <form v-else class="config-toolbar sample-toolbar" @submit.prevent="searchSamples">
      <label>{{ t('monitor.observation.meter') }}
        <el-select v-model="sampleFilters.meter" :disabled="saving" :placeholder="t('monitor.observation.selectMeter')">
          <el-option v-for="item in meters" :key="item.meterId" :value="item.meterId" :label="meterLabel(item.meterId)" />
        </el-select>
      </label>
      <label>{{ tr('group') }} <el-input v-model="sampleFilters.group" :disabled="saving" clearable /></label>
      <div class="table-actions">
        <ActionButton variant="primary" native-type="submit" :disabled="saving">{{ tr('search') }}</ActionButton>
        <ActionButton :disabled="saving" @click="resetSamples">{{ t('common.reset') }}</ActionButton>
      </div>
    </form>
    <el-alert v-if="failed" type="error" show-icon :closable="false" :title="t('equipment.observation.loadFailed')" />
    <el-alert v-if="kind === 'config' && !failed && !loading && !meters.length" type="info" :closable="false" :title="t('monitor.observation.noMeters')" />
    <template v-if="kind === 'config'">
      <el-table v-if="!failed" :key="widths.version.value" v-loading="loading" :data="filteredConfigs" :empty-text="emptyText"
        border @header-dragend="widths.onHeaderDragEnd">
        <el-table-column prop="meterId" :label="t('monitor.observation.meter')" :width="widths.widths.meterId" :min-width="160">
          <template #default="{ row }">{{ meterLabel(row.meterId) }}</template>
        </el-table-column>
        <el-table-column prop="groupKey" :label="t('equipment.observation.group')" :width="widths.widths.groupKey" :min-width="110" />
        <el-table-column prop="metricKey" :label="t('equipment.observation.key')" :width="widths.widths.metricKey" :min-width="140" />
        <el-table-column prop="nameZh" :label="tr(locale.startsWith('en') ? 'nameEn' : 'nameZh')" :width="widths.widths.nameZh" :min-width="130">
          <template #default="{ row }">{{ locale.startsWith('en') ? row.nameEn : row.nameZh }}</template>
        </el-table-column>
        <el-table-column prop="measurementMode" :label="t('monitor.observation.measurementMode')" :width="widths.widths.measurementMode" :min-width="120"><template #default="{ row }">{{ t(`monitor.observation.mode.${row.measurementMode}`) }}</template></el-table-column>
        <el-table-column prop="unit" :label="t('equipment.observation.unit')" :width="widths.widths.unit" :min-width="80" />
        <el-table-column prop="enabled" :label="tr('enabled')" :width="widths.widths.enabled" :min-width="100">
          <template #default="{ row }">{{ tr(row.enabled ? 'yes' : 'no') }}</template>
        </el-table-column>
        <el-table-column :label="t('equipment.observation.actions')" width="120"><template #default="{ row }"><div class="row-actions">
          <ActionButton size="small" variant="row" :disabled="saving" @click="openConfig(row)">{{ t('equipment.observation.edit') }}</ActionButton>
        </div></template></el-table-column>
      </el-table>
    </template>
    <el-table v-else :key="widths.version.value" v-loading="loading" :data="samples" border @header-dragend="widths.onHeaderDragEnd">
      <el-table-column prop="id" :label="t('equipment.observation.recordId')" :width="widths.widths.id" :min-width="80" />
      <el-table-column prop="meterId" :label="t('monitor.observation.meter')" :width="widths.widths.meterId" min-width="140">
        <template #default="{ row }">{{ meterLabel(row.meterId) }}</template>
      </el-table-column>
      <el-table-column prop="groupKey" :label="t('equipment.observation.group')" :width="widths.widths.groupKey" :min-width="110" />
      <el-table-column prop="observedAt" :label="t('equipment.observation.sampledAt')" :width="widths.widths.observedAt" :min-width="170"><template #default="{ row }">{{ formatShanghaiDateTime(row.observedAt) }}</template></el-table-column>
      <el-table-column prop="quality" :label="t('equipment.observation.quality')" :width="widths.widths.quality" :min-width="100"><template #default="{ row }">{{ qualityLabel(row.quality) }}</template></el-table-column>
      <el-table-column prop="reviewMark" :label="tr('reviewMark')" :width="widths.widths.reviewMark" min-width="105">
        <template #default="{ row }">{{ row.reviewMark ? tr(row.reviewMark) : '—' }}</template>
      </el-table-column>
      <el-table-column v-for="field in visibleColumns" :key="fieldKey(field)" :prop="fieldKey(field)"
        :label="metricTitle(field)" :width="widths.widths[fieldKey(field)]" :min-width="120">
        <template #default="{ row }">{{ metricValue(row, field) }}</template>
      </el-table-column>
      <el-table-column :label="t('equipment.observation.actions')" width="88" fixed="right"><template #default="{ row }"><div class="row-actions">
        <ActionButton size="small" variant="row" :disabled="saving" @click="openSample(row)">{{ tr('detail') }}</ActionButton>
      </div></template></el-table-column>
    </el-table>
    <el-pagination v-if="kind === 'samples'" v-model:current-page="page" :disabled="saving" :page-size="20" :total="total" layout="total, prev, pager, next" @current-change="load" />
    <el-dialog v-model="dialog" :title="tr(isConfig ? (editing ? 'edit' : 'add') : 'detail')" class="standard-form-dialog"
      :class="{ 'observation-config-dialog': isConfig }" width="min(680px, 94vw)" :align-center="isConfig"
      :show-close="!isConfig" :close-on-click-modal="!isConfig">
      <el-form v-if="kind === 'config'" label-position="top">
        <el-form-item :label="t('monitor.observation.meter')">
          <el-select v-model="form.meterId" :disabled="editing" :placeholder="t('monitor.observation.selectMeter')">
            <el-option v-for="item in meters" :key="item.meterId" :value="item.meterId" :label="meterLabel(item.meterId)" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('equipment.observation.group')"><el-input v-model="form.groupKey" :disabled="editing" /></el-form-item>
        <el-form-item :label="t('equipment.observation.key')"><el-input v-model="form.metricKey" :disabled="editing" /></el-form-item>
        <el-form-item :label="t('equipment.observation.slot')"><el-input-number v-model="form.slotNo" :min="1" :max="100" :disabled="editing && !!form.firstUsedAt" /></el-form-item>
        <el-form-item :label="t('equipment.observation.nameZh')"><el-input v-model="form.nameZh" /></el-form-item>
        <el-form-item :label="t('equipment.observation.nameEn')"><el-input v-model="form.nameEn" /></el-form-item>
        <el-form-item :label="t('monitor.observation.quantityKey')"><el-input v-model="form.quantityKey" /></el-form-item>
        <el-form-item :label="t('monitor.observation.measurementMode')"><el-select v-model="form.measurementMode">
          <el-option v-for="mode in modes" :key="mode" :value="mode" :label="t(`monitor.observation.mode.${mode}`)" />
        </el-select></el-form-item>
        <el-form-item :label="t('equipment.observation.unit')"><el-input v-model="form.unit" clearable /></el-form-item>
        <el-form-item :label="t('equipment.observation.decimals')"><el-input-number v-model="form.decimals" :min="0" :max="12" /></el-form-item>
        <el-form-item :label="t('equipment.observation.enabled')"><el-switch v-model="form.enabled" /></el-form-item>
        <el-form-item :label="t('equipment.observation.columnVisible')"><el-switch v-model="form.listVisible" /></el-form-item>
        <el-form-item :label="t('equipment.observation.columnOrder')"><el-input-number v-model="form.listOrder" :min="0" :max="2147483647" /></el-form-item>
        <el-form-item :label="t('monitor.observation.continuityConfirmed')"><el-switch v-model="form.rules.continuityConfirmed" /></el-form-item>
        <el-form-item :label="t('monitor.observation.maxGapSeconds')"><el-input-number v-model="form.rules.maxGapSeconds" :min="1" /></el-form-item>
      </el-form>
      <template v-else-if="sampleDetail">
        <el-descriptions :title="tr('recordOverview')" :column="2" border>
          <el-descriptions-item :label="tr('recordId')">{{ sampleDetail.id }}</el-descriptions-item>
          <el-descriptions-item :label="t('monitor.observation.meter')">{{ meterLabel(sampleDetail.meterId) }}</el-descriptions-item>
          <el-descriptions-item :label="tr('group')">{{ sampleDetail.groupKey }}</el-descriptions-item>
          <el-descriptions-item :label="tr('sampledAt')">{{ formatShanghaiDateTime(sampleDetail.observedAt) }}</el-descriptions-item>
          <el-descriptions-item :label="tr('quality')">{{ qualityLabel(sampleDetail.quality) }}</el-descriptions-item>
        </el-descriptions>
        <h3>{{ tr('sampleValues') }}</h3>
        <el-table :data="sampleDetail.values" border>
          <el-table-column prop="metricKey" :label="tr('key')" min-width="130" />
          <el-table-column :label="tr('value')" min-width="100">
            <template #default="{ row }">{{ String(row.value) }}</template>
          </el-table-column>
        </el-table>
        <h3>{{ tr('managementRecord') }}</h3>
      </template>
      <el-form v-if="!isConfig" label-position="top">
        <el-form-item :label="t('equipment.observation.remark')"><el-input v-model="form.remark" type="textarea" /></el-form-item>
        <el-form-item :label="t('equipment.observation.reviewMark')"><el-select v-model="form.reviewMark" clearable>
          <el-option value="abnormal" :label="t('equipment.observation.abnormal')" /><el-option value="reviewed" :label="t('equipment.observation.reviewed')" />
        </el-select></el-form-item>
      </el-form>
      <template #footer>
        <div class="core-dialog-footer">
          <ActionButton @click="dialog = false">{{ t('equipment.observation.cancel') }}</ActionButton>
          <ActionButton variant="primary" :loading="saving" :disabled="kind === 'config' && !form.meterId" @click="save">{{ t('equipment.observation.save') }}</ActionButton>
        </div>
      </template>
    </el-dialog>
  </BaseCard>
</template>
<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, shallowRef, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import { useTableColumnWidths } from '@/utils/tableColumnWidths'
import { formatShanghaiDateTime } from '@/utils/date'
import { energyOptions, energyConfigs, createEnergyConfig, updateEnergyConfig, energyAdminSamples, updateEnergySample } from '../../api/observations'
const props = defineProps({ kind: { type: String, required: true }, active: { type: Boolean, default: true } })
const { t, locale } = useI18n()
const tr = key => t(`equipment.observation.${key}`)
const isConfig = props.kind === 'config'
const cardProps = computed(() => isConfig ? { title: t('monitor.observation.energyConfig') }
  : { title: t('monitor.observation.energyRecords'), class: 'energy-sample-card' })
const modes = ['cumulative', 'interval', 'instantaneous']
const baseColumns = {
  id: { width: 100, minWidth: 80 }, groupKey: { width: 140, minWidth: 110 }, metricKey: { width: 180, minWidth: 140 },
  nameZh: { width: 180, minWidth: 130 }, measurementMode: { width: 140, minWidth: 120 }, unit: { width: 100, minWidth: 80 },
  observedAt: { width: 190, minWidth: 170 }, quality: { width: 120, minWidth: 100 }
}
const sampleColumns = { meterId: { width: 172, minWidth: 140 }, reviewMark: { width: 115, minWidth: 105 } }
const widths = shallowRef(useTableColumnWidths(`observation.energy.${props.kind}`, isConfig ? {
  ...baseColumns, meterId: { width: 210, minWidth: 160 }, enabled: { width: 100, minWidth: 100 }
} : { ...baseColumns, ...sampleColumns }))
const meter = ref(''), group = ref(''), meters = ref([]), configs = ref([]), samples = ref([])
const page = ref(1), total = ref(0), failed = ref(false), dialog = ref(false), saving = ref(false), editing = ref(false), loading = ref(false)
const form = reactive({})
const sampleFilters = reactive({ meter: '', group: '' })
const sampleDetail = ref(null)
const blankFilters = () => ({ meter: '', group: '', keyword: '' })
const draft = reactive(blankFilters())
const submitted = ref(blankFilters())
const filteredConfigs = computed(() => {
  const needle = submitted.value.keyword.toLowerCase()
  return configs.value.filter(row => !needle || [row.metricKey, row.nameZh, row.nameEn]
    .some(value => value?.toLowerCase().includes(needle)))
})
const metersById = computed(() => new Map(meters.value.map(item => [item.meterId, item])))
const emptyText = computed(() => loading.value ? t('common.loading') :
  tr(Object.values(submitted.value).some(Boolean) ? 'noMatchingConfigs' : 'noConfigs'))
function meterLabel(id) {
  const meter = metersById.value.get(id)
  const name = locale.value.startsWith('en') ? meter?.nameEn : meter?.nameZh
  return name && name !== id ? `${name} (${id})` : id
}
function searchConfig() {
  submitted.value = { ...draft, group: draft.group.trim(), keyword: draft.keyword.trim() }
  return loadConfig()
}
function resetConfigFilters() { Object.assign(draft, blankFilters()); return searchConfig() }
let generation = 0, loadedSelection = null, editSelection = null, editTarget = null
function selection() {
  return JSON.stringify(isConfig ? submitted.value : [meter.value, group.value, page.value])
}
function invalidate(current, previous) {
  generation++; loadedSelection = null; editSelection = null; editTarget = null
  configs.value = []; samples.value = []; failed.value = false; loading.value = false; dialog.value = false
  if (!previous || current[0] !== previous[0] || current[1] !== previous[1]) total.value = 0
}
const visibleColumns = computed(() => configs.value.filter(field => field.listVisible).sort((a, b) =>
  (a.listOrder ?? Infinity) - (b.listOrder ?? Infinity) || a.groupKey.localeCompare(b.groupKey) ||
  a.slotNo - b.slotNo || a.metricKey.localeCompare(b.metricKey)))
function fieldKey(field) { return `metric:${field.groupKey}:${field.metricKey}` }
function metricTitle(field) { const name = locale.value.startsWith('en') ? field.nameEn : field.nameZh; return field.unit ? `${name} (${field.unit})` : name }
function metricValue(row, field) { const item = row.groupKey === field.groupKey && row.values.find(value => value.metricKey === field.metricKey); return item ? String(item.value) : '—' }
function qualityLabel(value) { return t({ good: 'equipment.observation.qualityGood', bad: 'equipment.observation.qualityBad', unknown: 'equipment.observation.qualityUnknown' }[value] || 'equipment.observation.qualityUnknown') }
function assign(value) { for (const key of Object.keys(form)) delete form[key]; Object.assign(form, value) }
function openConfig(row) {
  if (props.active === false || !meters.value.length || failed.value || loadedSelection !== selection() || saving.value ||
      (row && (!filteredConfigs.value.includes(row) || !metersById.value.has(row.meterId)))) return
  editing.value = !!row
  editSelection = selection()
  editTarget = row ? { meterId: row.meterId, groupKey: row.groupKey, metricKey: row.metricKey } : null
  assign(row ? JSON.parse(JSON.stringify(row)) : { meterId: submitted.value.meter || '', groupKey: submitted.value.group, metricKey: '', slotNo: 1,
    nameZh: '', nameEn: '', valueType: 'number', quantityKey: '', measurementMode: 'cumulative', unit: null, decimals: null,
    enabled: true, listVisible: false, listOrder: null, rules: {} })
  dialog.value = true
}
function searchSamples() {
  const sameMeter = meter.value === sampleFilters.meter
  group.value = sampleFilters.group.trim()
  page.value = 1
  meter.value = sampleFilters.meter
  if (sameMeter) return load()
}
function resetSamples() {
  Object.assign(sampleFilters, { meter: meters.value[0]?.meterId || '', group: '' })
  return searchSamples()
}
function openSample(row) {
  if (loadedSelection !== selection() || saving.value || !samples.value.includes(row) || row.meterId !== meter.value) return
  sampleDetail.value = row
  editSelection = selection(); editTarget = { id: row.id }
  assign({ id: row.id, remark: row.remark || '', reviewMark: row.reviewMark || '' }); dialog.value = true
}
async function loadConfig() {
  const request = ++generation, selected = selection()
  loadedSelection = null; editSelection = null; editTarget = null; dialog.value = false
  configs.value = []; failed.value = false; loading.value = true
  const current = () => props.active !== false && request === generation && selected === selection()
  try {
    const { meter, group } = submitted.value
    const [options, fields] = await Promise.all([
      energyOptions(),
      energyConfigs({ meterId: meter || undefined, groupKey: group || undefined })
    ])
    if (!current()) return
    meters.value = options
    configs.value = fields
    loadedSelection = selected
  } catch {
    if (current()) failed.value = true
  } finally {
    if (current()) loading.value = false
  }
}
async function load() {
  const request = ++generation, selected = selection()
  loadedSelection = null; editSelection = null; editTarget = null; dialog.value = false
  configs.value = []; samples.value = []; failed.value = false; loading.value = true
  const current = () => request === generation && selected === selection()
  try {
    if (!meter.value) {
      const options = await energyOptions()
      if (!current()) return
      meters.value = options
      if (options.length) { sampleFilters.meter = options[0].meterId; meter.value = sampleFilters.meter }
      return
    }
    const params = { meterId: meter.value, groupKey: group.value || undefined }
    const fields = await energyConfigs(params)
    if (!current()) return
    let data
    if (props.kind === 'samples') {
      data = await energyAdminSamples({ ...params, page: page.value, pageSize: 20 })
      if (!current()) return
      samples.value = data.items; total.value = data.total
      const columnWidths = Object.fromEntries(fields.map(field => [fieldKey(field), { width: 160, minWidth: 120 }]))
      widths.value = useTableColumnWidths(`observation.energy.${props.kind}`, { ...baseColumns, ...sampleColumns, ...columnWidths })
    }
    configs.value = fields; loadedSelection = selected
  } catch { if (current()) failed.value = true }
  finally { if (current()) loading.value = false }
}
async function save() {
  if (props.active === false || !dialog.value || saving.value || !editSelection || editSelection !== selection()) return
  if (isConfig && !metersById.value.has(editTarget?.meterId ?? form.meterId)) return
  const selected = editSelection, target = editTarget, isEditing = editing.value, request = generation
  saving.value = true
  try {
    if (props.kind === 'config') {
      const payload = JSON.parse(JSON.stringify(form)); payload.unit = payload.unit || null
      if (payload.rules?.maxGapSeconds == null) delete payload.rules.maxGapSeconds
      if (isEditing) {
        delete payload.meterId; delete payload.groupKey; delete payload.metricKey; delete payload.firstUsedAt
        await updateEnergyConfig(target.meterId, target.groupKey, target.metricKey, payload)
      } else await createEnergyConfig(payload)
    } else await updateEnergySample(target.id, { remark: form.remark || null, reviewMark: form.reviewMark || null })
    if (isConfig) {
      if (props.active !== false) await loadConfig()
    } else if (editSelection === selected && selection() === selected && dialog.value) {
      dialog.value = false
      await load()
    }
  } catch {
    if (editSelection === selected && selection() === selected && (!isConfig || request === generation)) failed.value = true
  }
  finally { saving.value = false }
}
if (isConfig) {
  watch(() => props.active, active => {
    generation++
    dialog.value = false
    editSelection = null
    if (active) {
      Object.assign(draft, submitted.value)
      loadConfig()
    }
  }, { flush: 'sync' })
  onMounted(() => { if (props.active) loadConfig() })
} else {
  watch([meter, group, page], invalidate, { flush: 'sync' })
  watch(meter, () => { page.value = 1; if (meter.value) load() }, { flush: 'sync' })
  watch(group, () => { page.value = 1 }, { flush: 'sync' })
  onMounted(load)
}
onBeforeUnmount(() => { generation++; dialog.value = false })
</script>
<style scoped>
.config-toolbar {
  --config-card-inset: var(--space-lg);
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 4px 16px;
  margin: 0 calc(-1 * var(--config-card-inset)) 16px;
  padding-inline: var(--config-card-inset);
  border-bottom: 1px solid var(--border-secondary);
}
.config-toolbar :deep(.el-form-item) { flex: 0 1 180px; min-width: 0; }
.config-toolbar :deep(.config-toolbar__keyword) { flex: 1 1 180px; }
.config-toolbar :deep(.config-toolbar__actions) { flex: 0 1 auto; margin-inline-start: auto; max-width: 100%; }
@media (max-width: 768px) {
  .config-toolbar { --config-card-inset: 18px; }
}
@container observation-config (max-width: 300px) {
  .config-toolbar { --config-card-inset: 8px; }
}
.config-toolbar :deep(.el-input), .config-toolbar :deep(.el-select) { width: 100%; }
.energy-sample-card { min-width: 0; height: auto; }
.sample-toolbar label { flex: 1 1 140px; min-width: 0; display: grid; gap: 6px; color: var(--text-secondary); }
.sample-toolbar .table-actions { margin-inline-start: auto; }

</style>
