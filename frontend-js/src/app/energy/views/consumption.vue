<!-- 表计原始采样与明确口径统计，不把缺测伪装为零。 -->
<template>
  <div class="page-layout energy-consumption">
    <BaseCard :title="t('energy.consumption')">
      <template #actions>
        <ActionButton variant="refresh" @click="retry">{{ t('common.refresh') }}</ActionButton>
      </template>
      <el-form class="energy-toolbar" label-position="top" @submit.prevent="load">
        <el-form-item :label="tr('selector')">
          <el-select v-model="curveKey" :empty-values="[null, undefined]" :loading="curvesLoading" filterable>
            <el-option value="" :label="tr('manual')" />
            <el-option v-if="curveKey && !selectedCurve" :value="curveKey" :label="curveKey" disabled />
            <el-option v-for="row in curveGroups" :key="row.curveGroupKey" :value="row.curveGroupKey"
              :label="curveTitle(row, locale)" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!curveKey" :label="t('energy.observation.meter')">
          <el-select v-model="meter" :placeholder="t('energy.observation.selectMeter')" filterable>
            <el-option v-for="item in meters" :key="item.meterId" :value="item.meterId" :label="locale.startsWith('en') ? item.nameEn : item.nameZh" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!curveKey" :label="t('energy.observation.group')">
          <el-select v-model="group">
            <el-option v-for="item in groups" :key="item" :value="item" :label="item" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!curveKey" :label="t('energy.observation.metric')">
          <el-select v-model="metric" :placeholder="t('energy.observation.selectMetric')">
            <el-option v-for="item in groupMetrics" :key="item.metricKey" :value="item.metricKey"
              :label="t('energy.observation.metricOptionLabel', { name: locale.startsWith('en') ? item.nameEn : item.nameZh, key: item.metricKey })" />
          </el-select>
        </el-form-item>
        <el-form-item class="energy-time-range" :label="t('energy.observation.historyTimeRange')" :error="rangeError">
          <el-date-picker v-model="range" type="datetimerange" value-format="YYYY-MM-DD HH:mm:ss" format="YYYY-MM-DD HH:mm:ss" :range-separator="'–'" />
        </el-form-item>
        <el-form-item class="energy-filter-actions">
          <div class="table-actions">
            <ActionButton variant="primary" native-type="submit" :disabled="!summaryMetric || !!curveUnavailable || !!failureStage && failureStage !== 'samples'">{{ t('energy.observation.search') }}</ActionButton>
            <ActionButton @click="restore">{{ t('energy.observation.restoreDefault') }}</ActionButton>
          </div>
        </el-form-item>
      </el-form>
      <el-alert v-if="curvesFailed" :title="tr('loadFailed')" type="warning" :closable="false" show-icon>
        <ActionButton size="small" @click="retry">{{ t('energy.observation.retry') }}</ActionButton>
      </el-alert>
      <p v-else-if="!curvesLoading && !curveGroups.length && !curveKey" class="curve-group-note" role="status">
        {{ tr('noneEnabled') }}
      </p>
      <el-alert v-if="curveUnavailable" :title="tr('unavailable')" type="warning" :closable="false" show-icon />
      <el-alert v-else-if="failureStage" :title="t('energy.observation.loadFailed')" type="error" show-icon :closable="false">
        <ActionButton @click="retry">{{ t('energy.observation.retry') }}</ActionButton>
      </el-alert>
      <template v-else>
        <div v-if="summary" class="summary">
          <strong v-if="curveKey">{{ tr('summaryMetric', { name: metricName(summaryMetric) }) }}</strong>
          <span>{{ t('energy.observation.latestReading') }}: {{ summaryValue(summary.latest, !!curveKey) }} <template v-if="summary.latestState !== 'known'">({{ t(`energy.observation.latestState.${summary.latestState}`) }})</template></span>
          <span>{{ t('energy.observation.usage') }}: {{ summaryValue(summary.amount) }}</span>
          <span>{{ t(`energy.observation.result.${summary.state}`) }}<template v-if="summary.reason"> · {{ t(`energy.observation.reason.${summary.reason}`) }}</template></span>
        </div>
        <p v-if="emptyMessage" class="curve-message" role="status">{{ emptyMessage }}</p>
        <div v-else-if="chartGroups.length" class="curve-grid">
          <p v-if="hasGaps" class="curve-group-note" role="status">{{ tr('gaps') }}</p>
          <CurveChart v-for="item in chartGroups" :key="item.curveGroupKey" :group="item" :range="chartRange"
            :zoom="!!curveKey" message-namespace="energy.observation" />
        </div>
      </template>
    </BaseCard>
  </div>
</template>
<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import { shanghaiInputToRfc3339 } from '@/utils/date'
import CurveChart from '@/app/monitor/components/observations/CurveChart.vue'
import { energyOptions, energyDefinitions, energySamples, energySummary, energyConsumptionCurveGroups } from '../api/observations'
import { curveIssue, curveTitle } from '../components/energyCurveGroups'

const { t, locale } = useI18n()
const tr = (key, params) => t(`energy.curves.${key}`, params || {})
const meters = ref([]), meter = ref(''), group = ref(''), metric = ref('')
const curveGroups = ref([]), curveKey = ref('')
const curvesLoading = ref(true), curvesFailed = ref(false)
const definitions = ref([])
const range = ref(null), records = ref([]), summary = ref(null), loading = ref(false)
const optionsLoading = ref(true), definitionsLoading = ref(false), failureStage = ref('')
const rangeError = ref('')
const selectedCurve = computed(() => curveGroups.value.find(row => row.curveGroupKey === curveKey.value))
const activeMeter = computed(() => curveKey.value ? selectedCurve.value?.meterId || '' : meter.value)
const activeGroup = computed(() => curveKey.value ? selectedCurve.value?.groupKey || '' : group.value)
const groups = computed(() => [...new Set(definitions.value.map(item => item.groupKey))])
const groupMetrics = computed(() => definitions.value.filter(item => item.groupKey === activeGroup.value))
const enabledSeries = computed(() => selectedCurve.value?.series.filter(item => item.enabled) || [])
const curveUnavailable = computed(() => {
  if (!curveKey.value || curvesLoading.value || definitionsLoading.value) return false
  if (!selectedCurve.value) return !curvesFailed.value
  if (['definitionsUnavailable', 'selectionUnavailable'].includes(failureStage.value)) return true
  return !failureStage.value && !!curveIssue(selectedCurve.value.series, groupMetrics.value)
})
const summaryMetric = computed(() => {
  const key = curveKey.value ? enabledSeries.value[0]?.metricKey : metric.value
  return groupMetrics.value.find(item => item.metricKey === key)
})
const metricName = item => (locale.value.startsWith('en') ? item.nameEn || item.nameZh : item.nameZh || item.nameEn) || item.metricKey
const chartRange = computed(() => {
  if (range.value?.length !== 2) return []
  const [from, to] = range.value.map(shanghaiInputToRfc3339)
  return from && to && from < to ? [from, to] : []
})
function summaryValue(value, showUnit = true) {
  if (value == null) return '—'
  const decimals = curveKey.value ? summaryMetric.value?.decimals : null
  const display = Number.isInteger(decimals) && Number.isFinite(value) ? value.toFixed(decimals) : value
  return showUnit && summary.value.unit ? `${display} ${summary.value.unit}` : String(display)
}
const valuesBySample = computed(() => records.value.map(record => ({
  observedAt: record.observedAt, recordId: record.id, values: new Map(record.values.map(item => [item.metricKey, item.value]))
})))
function line(item, config) {
  return {
    groupKey: item.groupKey, metricKey: item.metricKey, label: metricName(item),
    lineStyle: config?.lineStyle, decimals: config ? item.decimals : undefined,
    points: valuesBySample.value.map(({ observedAt, recordId, values }) => ({
      observedAt, recordId, present: values.has(item.metricKey), value: values.get(item.metricKey) ?? null
    }))
  }
}
const finitePoint = point => point.present && Number.isFinite(point.value)
const chartGroups = computed(() => {
  if (!summary.value) return []
  if (selectedCurve.value && summaryMetric.value) {
    const series = enabledSeries.value.map(config => line(
      groupMetrics.value.find(item => item.metricKey === config.metricKey), config
    ))
    return series.some(item => item.points.some(finitePoint)) ? [{
      curveGroupKey: selectedCurve.value.curveGroupKey, title: curveTitle(selectedCurve.value, locale.value),
      unit: summaryMetric.value.unit, series
    }] : []
  }
  const byUnit = new Map()
  for (const item of groupMetrics.value) {
    const key = JSON.stringify([item.quantityKey, item.unit || ''])
    if (!byUnit.has(key)) byUnit.set(key, { curveGroupKey: key, title: metricName(item), unit: item.unit, series: [] })
    byUnit.get(key).series.push(line(item))
  }
  return [...byUnit.values()].filter(item => item.series.some(series => series.points.some(finitePoint)))
})
const hasGaps = computed(() => chartGroups.value.some(group => group.series.some(series => series.points.some(point => !finitePoint(point)))))
const emptyMessage = computed(() => {
  if ((!curveKey.value && optionsLoading.value) || definitionsLoading.value || loading.value ||
      (curveKey.value && curvesLoading.value)) return t('common.loading')
  if (curveKey.value && curvesFailed.value && !selectedCurve.value) return ''
  if (!activeMeter.value) return t(meters.value.length ? 'energy.observation.selectMeter' : 'energy.observation.noMeters')
  if (!definitions.value.length) return t('energy.observation.noEnergyMetrics')
  if (!chartRange.value.length) return t('energy.observation.chooseRange')
  if (!summary.value) return t('energy.observation.queryCurves')
  if (!records.value.length) return tr('noSamples')
  return chartGroups.value.length ? '' : tr('noValues')
})
let generation = 0
let definitionsGeneration = 0
let optionsGeneration = 0
let curvesGeneration = 0
let actionGeneration = 0
let definitionPending
let definitionsMeter
let alive = true

function invalidateSamples() {
  generation++
  records.value = []
  summary.value = null
  loading.value = false
  if (['samples', 'selectionUnavailable'].includes(failureStage.value)) failureStage.value = ''
}
function setManualDefaults() {
  if (curveKey.value) return
  if (!groups.value.includes(group.value)) group.value = groups.value[0] || ''
  if (!groupMetrics.value.some(item => item.metricKey === metric.value)) metric.value = groupMetrics.value[0]?.metricKey || ''
}
function loadDefinitions(refresh = false) {
  if (!activeMeter.value) return
  const selected = activeMeter.value
  if (definitionPending?.meter === selected) return definitionPending.promise
  if (!refresh && definitionsMeter === selected) return
  const current = ++definitionsGeneration
  definitionsLoading.value = true
  if (failureStage.value.startsWith('definitions')) failureStage.value = ''
  const promise = energyDefinitions(selected).then(result => {
    if (current !== definitionsGeneration) return
    definitions.value = result
    definitionsMeter = selected
    setManualDefaults()
  }).catch(error => {
    if (current !== definitionsGeneration) return
    definitions.value = []
    definitionsMeter = undefined
    failureStage.value = curveKey.value && [403, 404].includes(error.response?.status) ? 'definitionsUnavailable' : 'definitions'
  }).finally(() => {
    if (current !== definitionsGeneration) return
    definitionPending = null
    definitionsLoading.value = false
  })
  definitionPending = { meter: selected, promise }
  return promise
}
async function load() {
  if (!summaryMetric.value || curveUnavailable.value) return
  if (!chartRange.value.length) {
    rangeError.value = t(range.value?.length ? 'energy.observation.invalidHistoryRange' : 'energy.observation.chooseRange')
    return
  }
  invalidateSamples()
  const current = generation
  loading.value = true
  const selectedMetric = summaryMetric.value.metricKey
  const params = { meterId: activeMeter.value, groupKey: activeGroup.value, from: chartRange.value[0], to: chartRange.value[1] }
  try {
    const all = []
    let page = 1, result
    do {
      result = await energySamples({ ...params, page, pageSize: 100 })
      if (current !== generation) return
      all.push(...result.items)
      page++
    } while (page <= result.totalPages)
    const stats = await energySummary({ ...params, metricKey: selectedMetric })
    if (current === generation) {
      records.value = all.reverse()
      summary.value = stats
    }
  } catch (error) {
    if (current === generation) failureStage.value = curveKey.value && [403, 404].includes(error.response?.status)
      ? 'selectionUnavailable' : 'samples'
  } finally {
    if (current === generation) loading.value = false
  }
}
async function loadOptions() {
  const current = ++optionsGeneration
  optionsLoading.value = true
  if (failureStage.value === 'options') failureStage.value = ''
  try {
    const result = await energyOptions()
    if (current !== optionsGeneration) return
    meters.value = result
    if (!result.some(item => item.meterId === meter.value)) meter.value = result[0]?.meterId || ''
  } catch {
    if (current === optionsGeneration && !curveKey.value) failureStage.value = 'options'
  } finally {
    if (current === optionsGeneration) optionsLoading.value = false
  }
}
async function loadCurves() {
  const current = ++curvesGeneration
  curvesLoading.value = true
  curvesFailed.value = false
  try {
    const result = await energyConsumptionCurveGroups()
    if (current === curvesGeneration) curveGroups.value = result
  } catch {
    if (current === curvesGeneration) curvesFailed.value = true
  } finally {
    if (current === curvesGeneration) curvesLoading.value = false
  }
}
async function retry() {
  const action = ++actionGeneration
  invalidateSamples()
  const options = loadOptions()
  const curves = loadCurves()
  await (curveKey.value ? curves : options)
  if (action !== actionGeneration) return
  await loadDefinitions(true)
  if (action === actionGeneration && chartRange.value.length) await load()
}
function restore() {
  range.value = null
  rangeError.value = ''
  curveKey.value = ''
  meter.value = meters.value[0]?.meterId || ''
  group.value = groups.value[0] || ''
  metric.value = groupMetrics.value[0]?.metricKey || ''
  if (!meter.value || !definitions.value.length) return retry()
}
watch(meter, () => {
  group.value = ''
  metric.value = ''
}, { flush: 'sync' })
watch(activeMeter, () => {
  definitionsGeneration++
  definitionsMeter = undefined
  definitionPending = null
  definitions.value = []
  definitionsLoading.value = false
  if (failureStage.value.startsWith('definitions')) failureStage.value = ''
  loadDefinitions()
}, { flush: 'sync' })
watch(group, setManualDefaults, { flush: 'sync' })
watch([curveKey, activeMeter, activeGroup, selectedCurve, summaryMetric, range], () => {
  invalidateSamples()
  rangeError.value = ''
}, { flush: 'sync', deep: true })
watch(curveKey, async key => {
  const action = ++actionGeneration
  if (!key) {
    setManualDefaults()
    return
  }
  if (failureStage.value === 'options') failureStage.value = ''
  await loadDefinitions()
  if (alive && action === actionGeneration && chartRange.value.length) await load()
}, { flush: 'post' })
onMounted(retry)
onBeforeUnmount(() => {
  alive = false
  generation++
  definitionsGeneration++
  optionsGeneration++
  curvesGeneration++
  actionGeneration++
})
</script>
<style scoped>
.energy-consumption { min-width: 0; }
.energy-toolbar {
  --energy-card-inset: var(--space-lg);
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 4px var(--space-md);
  margin: 0 calc(-1 * var(--energy-card-inset)) var(--space-md);
  padding-inline: var(--energy-card-inset);
  border-bottom: 1px solid var(--border-secondary);
}
.energy-toolbar :deep(.el-form-item) { flex: 1 1 145px; min-width: 0; }
.energy-toolbar :deep(.el-select), .energy-toolbar :deep(.el-date-editor) { width: 100%; min-width: 0; }
.energy-toolbar .energy-time-range { flex: 1 1 330px; }
.energy-toolbar .energy-filter-actions { flex: 0 1 auto; margin-inline-start: auto; }
.summary { display: flex; flex-wrap: wrap; gap: 18px; margin: 12px 0; }
.curve-grid { display: grid; gap: var(--space-md); min-width: 0; }
.curve-group-note { color: var(--text-secondary); margin: var(--space-sm) 0; }
.curve-message { color: var(--text-secondary); text-align: center; padding: var(--space-md); }
@media (max-width: 1279px) {
  :global(body:has(.energy-consumption)) { min-width: 0; }
}
@media (max-width: 768px) { .energy-toolbar { --energy-card-inset: 18px; } }
@media (max-width: 600px) {
  :global(.main-layout:has(.energy-consumption)) { flex-direction: column; }
  :global(.main-layout:has(.energy-consumption) > .main-container) { flex: 1; min-height: 0; height: auto; }
  :global(.main-layout:has(.energy-consumption):not(:has(> .main-container-sidebar-hidden)) > .sidebar) {
    width: 100% !important; max-height: min(150px, 22dvh);
    flex: none; border-right: 0; border-bottom: 1px solid var(--border-primary);
  }
  :global(.main-layout:has(.energy-consumption):not(:has(> .main-container-sidebar-hidden)) .sidebar-brand-footer) {
    display: none;
  }
}
</style>
