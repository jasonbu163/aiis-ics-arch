<!-- 管理员按表计配置指标并只标注不可改写的能耗样本。 -->
<template>
  <div>
    <div class="toolbar">
      <el-select v-model="meter" :disabled="saving" :placeholder="t('monitor.observation.selectMeter')">
        <el-option v-for="item in meters" :key="item.meterId" :value="item.meterId" :label="locale.startsWith('en') ? item.nameEn : item.nameZh" />
      </el-select>
      <el-input v-model="group" :disabled="saving" :placeholder="t('equipment.observation.group')" />
      <ActionButton :disabled="saving" @click="load">{{ t('equipment.observation.search') }}</ActionButton>
      <ActionButton v-if="kind === 'config'" variant="primary" :disabled="!meter || saving || loading" @click="openConfig()">{{ t('equipment.observation.add') }}</ActionButton>
      <ActionButton @click="widths.reset">{{ t('equipment.observation.resetWidths') }}</ActionButton>
    </div>
    <el-alert v-if="failed" type="error" show-icon :closable="false" :title="t('equipment.observation.loadFailed')" />
    <el-table v-if="kind === 'config'" :key="widths.version.value" v-loading="loading" :data="configs" border @header-dragend="widths.onHeaderDragEnd">
      <el-table-column prop="groupKey" :label="t('equipment.observation.group')" :width="widths.widths.groupKey" :min-width="110" />
      <el-table-column prop="metricKey" :label="t('equipment.observation.key')" :width="widths.widths.metricKey" :min-width="140" />
      <el-table-column prop="nameZh" :label="t('equipment.observation.nameZh')" :width="widths.widths.nameZh" :min-width="130" />
      <el-table-column prop="measurementMode" :label="t('monitor.observation.measurementMode')" :width="widths.widths.measurementMode" :min-width="120"><template #default="{ row }">{{ t(`monitor.observation.mode.${row.measurementMode}`) }}</template></el-table-column>
      <el-table-column prop="unit" :label="t('equipment.observation.unit')" :width="widths.widths.unit" :min-width="80" />
      <el-table-column :label="t('equipment.observation.actions')" width="120"><template #default="{ row }"><div class="row-actions">
        <ActionButton size="small" variant="row" :disabled="saving" @click="openConfig(row)">{{ t('equipment.observation.edit') }}</ActionButton>
      </div></template></el-table-column>
    </el-table>
    <el-table v-else :key="widths.version.value" v-loading="loading" :data="samples" border @header-dragend="widths.onHeaderDragEnd">
      <el-table-column prop="id" :label="t('equipment.observation.recordId')" :width="widths.widths.id" :min-width="80" />
      <el-table-column prop="groupKey" :label="t('equipment.observation.group')" :width="widths.widths.groupKey" :min-width="110" />
      <el-table-column prop="observedAt" :label="t('equipment.observation.sampledAt')" :width="widths.widths.observedAt" :min-width="170"><template #default="{ row }">{{ formatShanghaiDateTime(row.observedAt) }}</template></el-table-column>
      <el-table-column prop="quality" :label="t('equipment.observation.quality')" :width="widths.widths.quality" :min-width="100"><template #default="{ row }">{{ qualityLabel(row.quality) }}</template></el-table-column>
      <el-table-column v-for="field in visibleColumns" :key="fieldKey(field)" :prop="fieldKey(field)"
        :label="metricTitle(field)" :width="widths.widths[fieldKey(field)]" :min-width="120">
        <template #default="{ row }">{{ metricValue(row, field) }}</template>
      </el-table-column>
      <el-table-column :label="t('equipment.observation.actions')" width="120"><template #default="{ row }"><div class="row-actions">
        <ActionButton size="small" variant="row" :disabled="saving" @click="openSample(row)">{{ t('equipment.observation.edit') }}</ActionButton>
      </div></template></el-table-column>
    </el-table>
    <el-pagination v-if="kind === 'samples'" v-model:current-page="page" :disabled="saving" :page-size="20" :total="total" layout="total, prev, pager, next" @current-change="load" />
    <el-dialog v-model="dialog" :title="t('equipment.observation.edit')" class="standard-form-dialog" width="min(680px, 94vw)">
      <el-form v-if="kind === 'config'" label-position="top">
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
      <el-form v-else label-position="top">
        <el-form-item :label="t('equipment.observation.remark')"><el-input v-model="form.remark" type="textarea" /></el-form-item>
        <el-form-item :label="t('equipment.observation.reviewMark')"><el-select v-model="form.reviewMark" clearable>
          <el-option value="abnormal" :label="t('equipment.observation.abnormal')" /><el-option value="reviewed" :label="t('equipment.observation.reviewed')" />
        </el-select></el-form-item>
      </el-form>
      <template #footer><ActionButton @click="dialog = false">{{ t('equipment.observation.cancel') }}</ActionButton>
        <ActionButton variant="primary" :loading="saving" @click="save">{{ t('equipment.observation.save') }}</ActionButton></template>
    </el-dialog>
  </div>
</template>
<script setup>
import { computed, onMounted, reactive, ref, shallowRef, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import ActionButton from '@/components/common/ActionButton.vue'
import { useTableColumnWidths } from '@/utils/tableColumnWidths'
import { formatShanghaiDateTime } from '@/utils/date'
import { energyOptions, energyConfigs, createEnergyConfig, updateEnergyConfig, energyAdminSamples, updateEnergySample } from '../../api/observations'
const props = defineProps({ kind: { type: String, required: true } })
const { t, locale } = useI18n()
const modes = ['cumulative', 'interval', 'instantaneous']
const baseColumns = {
  id: { width: 100, minWidth: 80 }, groupKey: { width: 140, minWidth: 110 }, metricKey: { width: 180, minWidth: 140 },
  nameZh: { width: 180, minWidth: 130 }, measurementMode: { width: 140, minWidth: 120 }, unit: { width: 100, minWidth: 80 },
  observedAt: { width: 190, minWidth: 170 }, quality: { width: 120, minWidth: 100 }
}
const widths = shallowRef(useTableColumnWidths(`observation.energy.${props.kind}`, baseColumns))
const meter = ref(''), group = ref(''), meters = ref([]), configs = ref([]), samples = ref([])
const page = ref(1), total = ref(0), failed = ref(false), dialog = ref(false), saving = ref(false), editing = ref(false), loading = ref(false)
const form = reactive({})
let generation = 0, loadedSelection = null, editSelection = null, editTarget = null
function selection() { return JSON.stringify([meter.value, group.value, page.value]) }
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
  if (!meter.value || loadedSelection !== selection() || saving.value || (row && (!configs.value.includes(row) || row.meterId !== meter.value))) return
  editing.value = !!row
  editSelection = selection()
  editTarget = row ? { meterId: row.meterId, groupKey: row.groupKey, metricKey: row.metricKey } : null
  assign(row ? JSON.parse(JSON.stringify(row)) : { meterId: meter.value, groupKey: group.value, metricKey: '', slotNo: 1,
    nameZh: '', nameEn: '', valueType: 'number', quantityKey: '', measurementMode: 'cumulative', unit: null, decimals: null,
    enabled: true, listVisible: false, listOrder: null, rules: {} })
  dialog.value = true
}
function openSample(row) {
  if (loadedSelection !== selection() || saving.value || !samples.value.includes(row) || row.meterId !== meter.value) return
  editSelection = selection(); editTarget = { id: row.id }
  assign({ id: row.id, remark: row.remark || '', reviewMark: row.reviewMark || '' }); dialog.value = true
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
      if (options.length) meter.value = options[0].meterId
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
      widths.value = useTableColumnWidths(`observation.energy.${props.kind}`, { ...baseColumns, ...columnWidths })
    }
    configs.value = fields; loadedSelection = selected
  } catch { if (current()) failed.value = true }
  finally { if (current()) loading.value = false }
}
async function save() {
  if (!dialog.value || saving.value || !editSelection || editSelection !== selection()) return
  const selected = editSelection, target = editTarget, isEditing = editing.value
  saving.value = true
  try {
    if (props.kind === 'config') {
      const payload = JSON.parse(JSON.stringify(form)); payload.unit = payload.unit || null
      if (payload.rules?.maxGapSeconds == null) delete payload.rules.maxGapSeconds
      if (isEditing) {
        delete payload.meterId; delete payload.groupKey; delete payload.metricKey; delete payload.firstUsedAt
        await updateEnergyConfig(target.meterId, target.groupKey, target.metricKey, payload)
      } else { payload.meterId = meter.value; await createEnergyConfig(payload) }
    } else await updateEnergySample(target.id, { remark: form.remark || null, reviewMark: form.reviewMark || null })
    if (editSelection === selected && selection() === selected && dialog.value) { dialog.value = false; await load() }
  } catch { if (editSelection === selected && selection() === selected) failed.value = true }
  finally { saving.value = false }
}
watch([meter, group, page], invalidate, { flush: 'sync' })
watch(meter, () => { page.value = 1; if (meter.value) load() }, { flush: 'sync' })
watch(group, () => { page.value = 1 }, { flush: 'sync' })
onMounted(load)
</script>
<style scoped>
.toolbar { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 16px; }
.toolbar .el-select, .toolbar .el-input { width: 200px; }
</style>
