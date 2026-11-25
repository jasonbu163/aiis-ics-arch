<!-- 表计原始采样与明确口径统计，不把缺测伪装为零。 -->
<template>
  <div class="page-layout energy-consumption">
    <BaseCard :title="t('energy.consumption')">
      <template #actions>
        <ActionButton variant="refresh" @click="retry">{{ t('common.refresh') }}</ActionButton>
      </template>
      <el-form class="energy-toolbar" label-position="top" @submit.prevent="load">
        <el-form-item :label="t('energy.observation.meter')">
          <el-select v-model="meter" :placeholder="t('energy.observation.selectMeter')" filterable>
            <el-option v-for="item in meters" :key="item.meterId" :value="item.meterId" :label="locale.startsWith('en') ? item.nameEn : item.nameZh" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('energy.observation.group')">
          <el-select v-model="group">
            <el-option v-for="item in groups" :key="item" :value="item" :label="item" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('energy.observation.metric')">
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
            <ActionButton variant="primary" native-type="submit" :disabled="!meter || !group || !metric">{{ t('energy.observation.search') }}</ActionButton>
            <ActionButton @click="restore">{{ t('energy.observation.restoreDefault') }}</ActionButton>
          </div>
        </el-form-item>
      </el-form>
      <el-alert v-if="failed" :title="t('energy.observation.loadFailed')" type="error" show-icon :closable="false">
        <ActionButton @click="retry">{{ t('energy.observation.retry') }}</ActionButton>
      </el-alert>
      <template v-else>
        <div v-if="summary" class="summary">
          <span>{{ t('energy.observation.latestReading') }}: {{ summary.latest ?? '—' }} <template v-if="summary.latestState !== 'known'">({{ t(`energy.observation.latestState.${summary.latestState}`) }})</template></span>
          <span>{{ t('energy.observation.usage') }}: {{ summary.amount ?? '—' }}{{ summary.amount != null && summary.unit ? ` ${summary.unit}` : '' }}</span>
          <span>{{ t(`energy.observation.result.${summary.state}`) }}<template v-if="summary.reason"> · {{ t(`energy.observation.reason.${summary.reason}`) }}</template></span>
        </div>
        <p v-if="emptyMessage" class="curve-message" role="status">{{ emptyMessage }}</p>
        <div v-else-if="chartGroups.length" class="curve-grid">
          <CurveChart v-for="item in chartGroups" :key="item.curveGroupKey" :group="item" :range="chartRange"
            message-namespace="energy.observation" />
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
import { energyOptions, energyDefinitions, energySamples, energySummary } from '../api/observations'
const { t, locale } = useI18n()
const meters = ref([]), meter = ref(''), definitions = ref([]), group = ref(''), metric = ref('')
const range = ref(null), records = ref([]), summary = ref(null), loading = ref(false)
const optionsLoading = ref(true), definitionsLoading = ref(false), failureStage = ref('')
const failed = computed(() => !!failureStage.value)
const rangeError = ref('')
const groups = computed(() => [...new Set(definitions.value.map(item => item.groupKey))])
const groupMetrics = computed(() => definitions.value.filter(item => item.groupKey === group.value))
const chartRange = computed(() => {
  if (range.value?.length !== 2) return []
  const [from, to] = range.value.map(shanghaiInputToRfc3339)
  return from && to && from < to ? [from, to] : []
})
const chartGroups = computed(() => {
  const byUnit = new Map()
  for (const item of groupMetrics.value) {
    const key = `${item.quantityKey}|${item.unit || ''}`
    if (!byUnit.has(key)) byUnit.set(key, { curveGroupKey: key, title: locale.value.startsWith('en') ? item.nameEn : item.nameZh, unit: item.unit, series: [] })
    byUnit.get(key).series.push({ groupKey: item.groupKey, metricKey: item.metricKey,
      label: locale.value.startsWith('en') ? item.nameEn : item.nameZh,
      points: records.value.map(record => {
        const value = record.values.find(entry => entry.metricKey === item.metricKey)
        return { observedAt: record.observedAt, recordId: record.id, present: !!value, value: value ? value.value : null }
      }) })
  }
  return [...byUnit.values()].filter(item => item.series.some(series => series.points.some(point =>
    point.present !== false && Number.isFinite(point.value))))
})
const emptyMessage = computed(() => {
  if (optionsLoading.value || definitionsLoading.value || loading.value) return t('common.loading')
  if (!meter.value) return t(meters.value.length ? 'energy.observation.selectMeter' : 'energy.observation.noMeters')
  if (!definitions.value.length) return t('energy.observation.noEnergyMetrics')
  if (!chartRange.value.length) return t('energy.observation.chooseRange')
  if (!summary.value) return t('energy.observation.queryCurves')
  return chartGroups.value.length ? '' : t('energy.observation.noChartData')
})
let generation = 0
let definitionGeneration = 0
let definitionPending
function invalidateSamples() {
  generation++
  records.value = []
  summary.value = null
  loading.value = false
  if (failureStage.value === 'samples') failureStage.value = ''
}
function loadDefinitions() {
  if (!meter.value) return
  const selected = meter.value
  if (definitionPending?.meter === selected) return definitionPending.promise
  const current = ++definitionGeneration
  definitionsLoading.value = true
  if (failureStage.value === 'definitions') failureStage.value = ''
  const promise = Promise.resolve().then(() => energyDefinitions(selected)).then(result => {
    if (current === definitionGeneration && selected === meter.value) {
      definitions.value = result; group.value = groups.value[0] || ''
    }
  }).catch(() => {
    if (current === definitionGeneration && selected === meter.value) failureStage.value = 'definitions'
  }).finally(() => {
    if (definitionPending?.generation === current) {
      definitionPending = null
      if (current === definitionGeneration) definitionsLoading.value = false
    }
  })
  definitionPending = { meter: selected, generation: current, promise }
  return promise
}
async function load() {
  if (!meter.value || !group.value || !metric.value) return
  if (!chartRange.value.length) {
    rangeError.value = t(range.value?.length ? 'energy.observation.invalidHistoryRange' : 'energy.observation.chooseRange')
    return
  }
  invalidateSamples()
  const current = generation; loading.value = true
  const selectedMetric = metric.value
  try {
    const params = { meterId: meter.value, groupKey: group.value, from: chartRange.value[0], to: chartRange.value[1] }
    const all = []; let page = 1, result
    do {
      result = await energySamples({ ...params, page, pageSize: 100 })
      if (current !== generation) return
      all.push(...result.items); page++
    } while (page <= result.totalPages)
    const stats = await energySummary({ ...params, metricKey: selectedMetric })
    if (current === generation) { records.value = all.reverse(); summary.value = stats }
  } catch { if (current === generation) failureStage.value = 'samples' }
  finally { if (current === generation) loading.value = false }
}
let optionsPending
let alive = true
function loadOptions() {
  if (!optionsPending) {
    optionsLoading.value = true
    failureStage.value = ''
    optionsPending = energyOptions().then(options => {
      if (!alive) return
      meters.value = options
      meter.value = options[0]?.meterId || ''
    }).catch(() => { if (alive) failureStage.value = 'options' }).finally(() => {
      optionsPending = null
      if (alive) optionsLoading.value = false
    })
  }
  return optionsPending
}
async function retry() {
  if (!meters.value.length) await loadOptions()
  if (!alive) return
  const selected = meter.value
  if (selected && !definitions.value.length) await loadDefinitions()
  if (alive && selected === meter.value && chartRange.value.length) await load()
}
function restore() {
  range.value = null
  rangeError.value = ''
  meter.value = meters.value[0]?.meterId || ''
  group.value = groups.value[0] || ''
  metric.value = groupMetrics.value[0]?.metricKey || ''
  if (!meter.value || !definitions.value.length) return retry()
}
watch(meter, () => {
  definitionGeneration++; definitionPending = null; definitionsLoading.value = false
  invalidateSamples(); definitions.value = []; group.value = ''; metric.value = ''
  if (failureStage.value === 'definitions') failureStage.value = ''
  loadDefinitions()
}, { flush: 'sync' })
watch(group, () => { invalidateSamples(); metric.value = groupMetrics.value[0]?.metricKey || '' }, { flush: 'sync' })
watch([metric, range], () => { invalidateSamples(); rangeError.value = '' }, { flush: 'sync', deep: true })
onMounted(retry)
onBeforeUnmount(() => { alive = false; generation++; definitionGeneration++ })
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
