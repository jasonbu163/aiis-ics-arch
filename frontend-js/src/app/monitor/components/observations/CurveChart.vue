<!-- 同单位图框支持区域多选、真实时间缺测与同刻样本。 -->
<template>
  <section class="curve-group">
    <header class="curve-heading">
      <h3>{{ group.title }}</h3>
      <div class="area-controls">
        <el-select v-model="selected" multiple collapse-tags :placeholder="tr('selectAreas')" :aria-label="tr('selectAreas')">
          <el-option v-for="key in available" :key="key" :value="key" :label="areaLabels.get(key)" />
        </el-select>
        <ActionButton size="small" @click="selected = [...available]">{{ tr('selectAll') }}</ActionButton>
      </div>
    </header>
    <div class="curve-content">
      <div v-show="canPlot" ref="element" class="curve-plot" :aria-label="tr('chartLabel')" role="img" />
      <p v-if="!canPlot" class="curve-empty" role="status">{{ tr(emptyReason) }}</p>
      <p v-if="canPlot && precisionLimited" class="curve-empty" role="status">{{ tr('precisionLimited') }}</p>
      <div v-if="shown.length" class="curve-legend" role="group" :aria-label="tr('curveLegend')">
        <button v-for="item in shown" :key="item.key" type="button" class="curve-legend-item"
          :aria-pressed="!hidden.has(item.key)" @click="toggleSeries(item.key)">
          <span class="curve-swatch" :class="{ 'curve-swatch--dashed': item.type === 'dashed' }"
            :style="{ borderColor: `var(${item.color})` }" aria-hidden="true"></span>
          <span>{{ item.label }}</span>
        </button>
      </div>
    </div>
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

const props = defineProps({
  group: { type: Object, required: true },
  range: { type: Array, default: () => [] },
  messageNamespace: { type: String, default: 'monitor.observation' }
})
const { t } = useI18n()
const tr = key => t(`${props.messageNamespace}.${key}`)
const element = ref()
const theme = useThemeStore()
const palette = ['--primary', '--success', '--warning', '--danger', '--info', '--text-secondary']
const seriesKey = item => JSON.stringify([item.groupKey, item.metricKey])
const areaLabels = computed(() => new Map(props.group.series.map(item => [item.groupKey, item.groupLabel || item.groupKey])))
const available = computed(() => [...areaLabels.value.keys()])
const selected = ref([...available.value])
const hidden = ref(new Set())
const shown = computed(() => {
  const items = props.group.series.map((item, index) => ({
    ...item,
    key: seriesKey(item),
    label: available.value.length > 1 ? `${areaLabels.value.get(item.groupKey)} · ${item.label}` : item.label,
    color: palette[index % palette.length],
    type: item.lineStyle === 'dashed' ? 'dashed' : 'solid'
  })).filter(item => selected.value.includes(item.groupKey))
  const counts = new Map()
  for (const item of items) counts.set(item.label, (counts.get(item.label) || 0) + 1)
  return items.map(item => counts.get(item.label) === 1 ? item : { ...item, label: `${item.label} (${item.key})` })
})
const visible = computed(() => shown.value.filter(item => !hidden.value.has(item.key)))
const canPlot = computed(() => visible.value.some(item => item.points.some(point =>
  point.present !== false && Number.isFinite(point.value))))
const emptyReason = computed(() => !selected.value.length ? 'selectAreas' : !visible.value.length ? 'noVisibleSeries' : 'noChartData')
const precisionLimited = ref(false)
let chart
let observer
let activeTheme
let disposed = false

function toggleSeries(key) {
  if (hidden.value.has(key)) hidden.value.delete(key)
  else hidden.value.add(key)
}
function escapeText(value) {
  return String(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]))
}
function formatTime(value, origin) {
  const date = new Date(origin + value)
  return Number.isFinite(date.getTime()) ? formatShanghaiDateTime(date.toISOString()) : ''
}
function render() {
  if (disposed || !element.value || !canPlot.value) return
  if (!chart || activeTheme !== theme.theme) {
    chart?.dispose()
    activeTheme = theme.theme
    chart = echarts.init(element.value, getEChartsTheme(activeTheme))
  }
  const start = Date.parse(props.range[0])
  const origin = Number.isFinite(start) ? Math.floor(start / 86400000) * 86400000 : 0
  const bounds = props.range.map(observedAt => splitObservedPoints([{ observedAt, value: 0 }], null, origin).line[0]?.[0])
  const crossDay = props.range.length === 2 && formatShanghaiDateTime(props.range[0]).slice(0, 10) !==
    formatShanghaiDateTime(props.range[1]).slice(0, 10)
  const names = new Map()
  const series = []
  const colors = getComputedStyle(element.value)
  let limited = false
  for (const item of visible.value) {
    names.set(item.key, item.label)
    const points = item.points.map(point => Number.isFinite(point.value) ? point : { ...point, present: false })
    const values = splitObservedPoints(points, item.intervalSeconds, origin)
    limited ||= values.precisionLimited
    const color = colors.getPropertyValue(item.color).trim()
    const line = { name: item.key, type: 'line', showSymbol: true, connectNulls: false, itemStyle: { color } }
    series.push({ ...line, lineStyle: { color, type: item.type }, data: values.line })
    if (values.simultaneous.length) series.push({ ...line, lineStyle: { opacity: 0 }, data: values.simultaneous })
  }
  precisionLimited.value = limited
  chart.setOption({
    tooltip: { trigger: 'axis', confine: true, formatter: params => {
      if (!params.length) return ''
      return [escapeText(formatTime(params[0].axisValue, origin)), ...params.map(item =>
        `${item.marker}${escapeText(names.get(item.seriesName) || item.seriesName)}: ${escapeText(item.value?.[1] ?? '—')}` +
        (item.data?.[2] ? ` · ${escapeText(item.data[2])}` : ''))].join('<br>')
    } },
    grid: { left: 58, right: 14, top: 33, bottom: crossDay ? 55 : 38 },
    xAxis: { type: 'time', min: bounds[0], max: bounds[1],
      axisLine: { show: true },
      axisLabel: { hideOverlap: true, formatter: value => {
        const stamp = formatTime(value, origin)
        return crossDay ? stamp.slice(0, 10) + '\n' + stamp.slice(11) : stamp.slice(11)
      } } },
    yAxis: { type: 'value', name: props.group.unit || '', scale: true,
      axisLine: { show: true }, splitLine: { show: true } },
    series
  }, { notMerge: true })
}
onMounted(() => {
  render()
  observer = new ResizeObserver(() => { if (canPlot.value) chart?.resize() })
  observer.observe(element.value)
})
watch(available, (areas, previous) => {
  const wasAll = previous.every(key => selected.value.includes(key))
  selected.value = wasAll ? [...areas] : selected.value.filter(key => areas.includes(key))
})
watch(() => props.group.series, items => {
  const existing = new Set(items.map(seriesKey))
  hidden.value = new Set([...hidden.value].filter(key => existing.has(key)))
})
watch([visible, () => props.range, () => theme.theme], () => nextTick(render), { flush: 'post' })
onBeforeUnmount(() => {
  disposed = true
  observer?.disconnect()
  chart?.dispose()
})
</script>

<style scoped>
.curve-group {
  min-width: 0; border: 1px solid var(--border-secondary);
  border-radius: var(--el-border-radius-base); background: var(--card-bg);
}
.curve-heading {
  display: flex; justify-content: space-between; gap: 10px; flex-wrap: wrap; align-items: center;
  padding: 10px 14px; border-bottom: 1px solid var(--border-secondary);
}
.curve-heading h3 { margin: 0; font-size: 15px; overflow-wrap: anywhere; }
.area-controls { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; min-width: 0; max-width: 100%; }
.area-controls .el-select { width: 180px; max-width: 100%; }
.curve-content { padding: 8px 14px 12px; }
.curve-plot { width: 100%; height: 270px; }
.curve-legend { display: flex; gap: 4px 10px; justify-content: center; flex-wrap: wrap; }
.curve-legend-item {
  display: flex; align-items: center; gap: 6px; max-width: 100%; padding: 4px 7px;
  border: 0; border-radius: var(--el-border-radius-small); background: transparent;
  color: var(--text-secondary); font: inherit; font-size: 12px; cursor: pointer; overflow-wrap: anywhere;
}
.curve-legend-item:hover { background: var(--primary-subtle); }
.curve-legend-item[aria-pressed="false"] { opacity: .65; text-decoration: line-through; }
.curve-swatch { width: 20px; flex: none; border-top: 2px solid; }
.curve-swatch--dashed { border-top-style: dashed; }
.curve-empty { text-align: center; color: var(--text-secondary); }
</style>
