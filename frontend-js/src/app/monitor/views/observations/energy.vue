<!-- 表计原始采样与明确口径统计，不把缺测伪装为零。 -->
<template>
  <div class="page-layout">
    <BaseCard :title="t('monitor.energy')" v-loading="loading">
      <div class="toolbar">
        <el-select v-model="meter" :placeholder="t('monitor.observation.selectMeter')" filterable>
          <el-option v-for="item in meters" :key="item.meterId" :value="item.meterId" :label="locale.startsWith('en') ? item.nameEn : item.nameZh" />
        </el-select>
        <el-select v-model="group" :placeholder="t('equipment.observation.group')">
          <el-option v-for="item in groups" :key="item" :value="item" :label="item" />
        </el-select>
        <el-select v-model="metric" :placeholder="t('monitor.observation.selectMetric')">
          <el-option v-for="item in groupMetrics" :key="item.metricKey" :value="item.metricKey" :label="locale.startsWith('en') ? item.nameEn : item.nameZh" />
        </el-select>
        <el-date-picker v-model="range" type="datetimerange" value-format="YYYY-MM-DD HH:mm:ss" format="YYYY-MM-DD HH:mm:ss" :range-separator="'–'" />
        <ActionButton variant="primary" @click="load">{{ t('equipment.observation.search') }}</ActionButton>
      </div>
      <el-alert v-if="failed" :title="t('equipment.observation.loadFailed')" type="error" show-icon :closable="false">
        <ActionButton @click="retry">{{ t('monitor.observation.retry') }}</ActionButton>
      </el-alert>
      <EmptyAxes v-else-if="!meter" :reason="t(meters.length ? 'monitor.observation.selectMeter' : 'monitor.observation.noMeters')" />
      <EmptyAxes v-else-if="!definitions.length" :reason="t('monitor.observation.noEnergyMetrics')" />
      <EmptyAxes v-else-if="!range?.length" :reason="t('monitor.observation.chooseRange')" />
      <template v-else>
        <div v-if="summary" class="summary">
          <span>{{ t('monitor.observation.latestReading') }}: {{ summary.latest ?? '—' }} <template v-if="summary.latestState !== 'known'">({{ t(`monitor.observation.latestState.${summary.latestState}`) }})</template></span>
          <span>{{ t('monitor.observation.usage') }}: {{ summary.amount ?? '—' }}<template v-if="summary.amount !== null && summary.unit"> {{ summary.unit }}</template></span>
          <span>{{ t(`monitor.observation.result.${summary.state}`) }}<template v-if="summary.reason"> · {{ t(`monitor.observation.reason.${summary.reason}`) }}</template></span>
        </div>
        <EmptyAxes v-if="!chartGroups.length" :reason="t('monitor.observation.noEnergyMetrics')" />
        <CurveChart v-for="item in chartGroups" :key="item.curveGroupKey" :group="item" :range="chartRange" />
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
import CurveChart from '../../components/observations/CurveChart.vue'
import EmptyAxes from '../../components/observations/EmptyAxes.vue'
import { energyOptions, energyDefinitions, energySamples, energySummary } from '../../api/observations'
const { t, locale } = useI18n()
const meters = ref([]), meter = ref(''), definitions = ref([]), group = ref(''), metric = ref('')
const range = ref(null), records = ref([]), summary = ref(null), loading = ref(false), failed = ref(false)
const groups = computed(() => [...new Set(definitions.value.map(item => item.groupKey))])
const groupMetrics = computed(() => definitions.value.filter(item => item.groupKey === group.value))
const chartRange = computed(() => range.value?.length === 2 ? range.value.map(shanghaiInputToRfc3339) : [])
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
  return [...byUnit.values()]
})
let generation = 0
let definitionGeneration = 0
let definitionPending
function invalidateSamples() {
  generation++
  records.value = []
  summary.value = null
  loading.value = false
}
function loadDefinitions() {
  if (!meter.value) return
  const selected = meter.value
  if (definitionPending?.meter === selected) return definitionPending.promise
  const current = ++definitionGeneration
  const promise = Promise.resolve().then(() => energyDefinitions(selected)).then(result => {
    if (current === definitionGeneration && selected === meter.value) {
      definitions.value = result; group.value = groups.value[0] || ''; failed.value = false
    }
  }).catch(() => {
    if (current === definitionGeneration && selected === meter.value) failed.value = true
  }).finally(() => {
    if (definitionPending?.generation === current) definitionPending = null
  })
  definitionPending = { meter: selected, generation: current, promise }
  return promise
}
async function load() {
  if (!meter.value || !group.value || !metric.value || chartRange.value.length !== 2) return
  const current = ++generation; loading.value = true
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
    if (current === generation) { records.value = all.reverse(); summary.value = stats; failed.value = false }
  } catch { if (current === generation) failed.value = true }
  finally { if (current === generation) loading.value = false }
}
async function retry() {
  if (!meters.value.length) { try { meters.value = await energyOptions(); meter.value = meters.value[0]?.meterId || ''; failed.value = false } catch { failed.value = true; return } }
  if (meter.value && !definitions.value.length) await loadDefinitions()
  if (range.value?.length) await load()
}
watch(meter, () => {
  definitionGeneration++; definitionPending = null; invalidateSamples(); definitions.value = []; group.value = ''; metric.value = ''; failed.value = false
  loadDefinitions()
}, { flush: 'sync' })
watch(group, () => { invalidateSamples(); metric.value = groupMetrics.value[0]?.metricKey || ''; failed.value = false }, { flush: 'sync' })
watch([metric, range], () => { invalidateSamples(); failed.value = false }, { flush: 'sync', deep: true })
onMounted(retry)
onBeforeUnmount(() => { generation++; definitionGeneration++ })
</script>
<style scoped>
.toolbar { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 18px; }
.toolbar .el-select { width: 190px; }
.summary { display: flex; flex-wrap: wrap; gap: 18px; margin: 12px 0; }
</style>
