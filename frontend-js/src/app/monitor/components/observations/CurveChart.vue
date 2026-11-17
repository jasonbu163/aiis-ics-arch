<!-- 同单位图框支持区域多选、真实时间缺测与同刻样本。 -->
<template>
  <section class="curve-group">
    <div class="curve-heading">
      <h3>{{ group.title }}</h3>
      <div class="area-controls">
        <el-select v-model="selected" multiple collapse-tags :placeholder="t('monitor.observation.selectAreas')">
          <el-option v-for="key in available" :key="key" :value="key" :label="areaLabel(key)" />
        </el-select>
        <ActionButton size="small" @click="selected = [...available]">{{ t('monitor.observation.selectAll') }}</ActionButton>
      </div>
    </div>
    <div ref="element" class="curve-plot" :aria-label="t('monitor.observation.chartLabel')" role="img" />
    <p v-if="precisionLimited" role="status">{{ t('monitor.observation.precisionLimited') }}</p>
    <p v-if="!hasPoints" class="curve-empty">{{ t('monitor.observation.noChartData') }}</p>
  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import echarts, { getEChartsTheme } from '@/utils/echarts'
import { formatShanghaiDateTime } from '@/utils/date'
import { useThemeStore } from '@/store/theme'
import ActionButton from '@/components/common/ActionButton.vue'
import { splitObservedPoints } from './curveSeries'

const props = defineProps({ group: { type: Object, required: true }, range: { type: Array, default: () => [] } })
const { t } = useI18n()
const element = ref()
const theme = useThemeStore()
const available = computed(() => [...new Set(props.group.series.map(item => item.groupKey))])
function areaLabel(key) { return props.group.series.find(item => item.groupKey === key)?.groupLabel || key }
const selected = ref([...available.value])
const visible = computed(() => props.group.series.filter(item => selected.value.includes(item.groupKey)))
const hasPoints = computed(() => visible.value.some(item => item.points.some(point => point.present !== false && point.value !== null)))
const precisionLimited = ref(false)
let chart
let observer
let legendSelected = {}

function escapeText(value) {
  return String(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]))
}
function formatTime(value, origin) { return formatShanghaiDateTime(new Date(origin + value).toISOString()) }
function render() {
  if (!element.value) return
  if (chart) {
    legendSelected = { ...legendSelected, ...chart.getOption().legend?.[0]?.selected }
    chart.dispose()
  }
  chart = echarts.init(element.value, getEChartsTheme(theme.theme))
  const start = Date.parse(props.range[0])
  const end = Date.parse(props.range[1])
  const origin = Number.isFinite(start) ? Math.floor(start / 86400000) * 86400000 : 0
  const series = []
  const names = new Map()
  const counts = new Map()
  for (const item of visible.value) {
    const label = `${areaLabel(item.groupKey)} · ${item.label}`
    counts.set(label, (counts.get(label) || 0) + 1)
  }
  let limited = false
  for (const item of visible.value) {
    const key = JSON.stringify([item.groupKey, item.metricKey])
    const label = `${areaLabel(item.groupKey)} · ${item.label}`
    names.set(key, counts.get(label) > 1 ? `${label} (${key})` : label)
    const values = splitObservedPoints(item.points, item.intervalSeconds, origin)
    limited ||= values.precisionLimited
    series.push({ name: key, type: 'line', showSymbol: true, connectNulls: false, data: values.line })
    if (values.simultaneous.length) series.push({ name: key, type: 'line', showSymbol: true,
      lineStyle: { opacity: 0 }, data: values.simultaneous })
  }
  precisionLimited.value = limited
  chart.setOption({
    tooltip: { trigger: 'axis', formatter: params => {
      if (!params.length) return ''
      return [escapeText(formatTime(params[0].axisValue, origin)), ...params.map(item =>
        `${item.marker}${escapeText(names.get(item.seriesName) || item.seriesName)}: ${escapeText(item.value?.[1] ?? '—')}` +
        (item.data?.[2] ? ` · ${escapeText(item.data[2])}` : ''))].join('<br>')
    } },
    legend: { data: [...names.keys()], selected: legendSelected, formatter: key => names.get(key) || key },
    grid: { left: 55, right: 25, top: 45, bottom: 48 },
    xAxis: { type: 'time', min: Number.isFinite(start) ? start - origin : undefined,
      max: Number.isFinite(end) ? end - origin : undefined,
      axisLine: { show: true },
      axisLabel: { show: props.range.length === 2, hideOverlap: true, formatter: value => formatTime(value, origin).slice(11, 19) } },
    yAxis: { type: 'value', name: props.group.unit || '', scale: true,
      axisLine: { show: true },
      axisLabel: { show: hasPoints.value }, splitLine: { show: hasPoints.value } },
    series
  })
}
onMounted(() => { nextTick(render); observer = new ResizeObserver(() => chart?.resize()); observer.observe(element.value) })
watch(() => props.group, () => {
  selected.value = selected.value.filter(key => available.value.includes(key))
  nextTick(render)
}, { deep: true })
watch([selected, () => props.range, () => theme.theme], () => nextTick(render), { deep: true })
onBeforeUnmount(() => { observer?.disconnect(); chart?.dispose() })
</script>

<style scoped>
.curve-group { border: 1px solid var(--border-color); border-radius: 8px; padding: 14px; }
.curve-heading { display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; align-items: center; }
.curve-heading h3 { margin: 0; font-size: 15px; }
.area-controls { display: flex; gap: 8px; align-items: center; }
.area-controls .el-select { min-width: 180px; }
.curve-plot { width: 100%; height: 320px; }
.curve-empty { text-align: center; color: var(--text-secondary); }
</style>
