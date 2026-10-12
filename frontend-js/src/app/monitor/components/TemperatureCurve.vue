<!--
  文件路径: /frontend-next-js/src/app/monitor/components/TemperatureCurve.vue
  功能描述: 温度曲线组件
  主要功能:
    - 展示炉区温度实时数据及历史趋势曲线
    - 支持日夜模式切换
-->
<template>
  <div class="curve-component">
    <BaseCard :title="t('monitor.temperatureTabs.temperature')">
      <div ref="chartRef" class="chart-box"></div>
    </BaseCard>

    <BaseCard class="table-card" :title="t('monitor.temperatureCurve.sectionTitle')">
      <div class="table-scroll">
        <el-table :data="tableData" border stripe class="vibe-table monitor-curve-table">
          <el-table-column prop="zone" :label="t('monitor.temperatureCurve.zone')" width="150" />
          <el-table-column prop="set" :label="t('monitor.temperatureCurve.setTemp')" align="center" />
          <el-table-column prop="act" :label="t('monitor.temperatureCurve.actTemp')" align="center">
            <template #default="{ row }">
              <span :class="{ 'temp-warning': row.deviation > 5 }">{{ row.act }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="deviation" :label="t('monitor.temperatureCurve.deviation')" align="center">
            <template #default="{ row }">
              <span :class="{ 'temp-warning': row.deviation > 5 }">{{ row.deviation }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </BaseCard>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import BaseCard from '@/components/common/BaseCard.vue'
import echarts, { getEChartsTheme } from '@/utils/echarts'
import { useThemeStore } from '@/store/theme'

const { t } = useI18n()
const themeStore = useThemeStore()
const chartRef = ref()
let chartInstance = null

const props = defineProps({
  data: {
    type: Object,
    default: () => ({ trends: [], latest: {} })
  },
  active: {
    type: Boolean,
    default: true
  }
})

const tableData = computed(() => {
  const latest = props.data.latest || {}
  return [
    { zone: t('monitor.temperatureCurve.zoneNames.heating1'), set: latest.z1TempSet || 0, act: latest.z1TempAct || 0 },
    { zone: t('monitor.temperatureCurve.zoneNames.heating2'), set: latest.z2TempSet || 0, act: latest.z2TempAct || 0 },
    { zone: t('monitor.temperatureCurve.zoneNames.heating3'), set: latest.z3TempSet || 0, act: latest.z3TempAct || 0 },
    { zone: t('monitor.temperatureCurve.zoneNames.soaking1'), set: latest.z4TempSet || 0, act: latest.z4TempAct || 0 },
    { zone: t('monitor.temperatureCurve.zoneNames.soaking2'), set: latest.z5TempSet || 0, act: latest.z5TempAct || 0 },
    { zone: t('monitor.temperatureCurve.zoneNames.soaking3'), set: latest.z6TempSet || 0, act: latest.z6TempAct || 0 },
  ].map(row => ({ ...row, deviation: (row.act - row.set).toFixed(1) }))
})

const initChart = () => {
  if (!chartRef.value || !props.active || !props.data.trends) return

  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = echarts.init(chartRef.value, getEChartsTheme(themeStore.theme))

  const trends = props.data.trends
  const timeLabels = trends.map(t => t.time)

  const createSeries = (nameKey, field, solid = true) => ({
    name: t(nameKey),
    type: 'line',
    smooth: true,
    ...(solid ? {} : { lineStyle: { type: 'dashed' } }),
    data: trends.map(t => t[field])
  })

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { top: 0, type: 'scroll', textStyle: { color: getCssVar('--text-secondary') } },
    grid: { left: 48, right: 24, top: 58, bottom: 36 },
    xAxis: {
      type: 'category',
      data: timeLabels,
      axisLabel: { color: getCssVar('--text-tertiary') }
    },
    yAxis: {
      type: 'value',
      name: t('monitor.temperatureCurve.yAxisName'),
      axisLabel: { color: getCssVar('--text-tertiary') },
      splitLine: { lineStyle: { type: 'dashed', color: getCssVar('--border-secondary') } }
    },
    series: [
      createSeries('monitor.temperatureCurve.series.z1Act', 'z1TempAct'),
      createSeries('monitor.temperatureCurve.series.z1Set', 'z1TempSet', false),
      createSeries('monitor.temperatureCurve.series.z2Act', 'z2TempAct'),
      createSeries('monitor.temperatureCurve.series.z2Set', 'z2TempSet', false),
      createSeries('monitor.temperatureCurve.series.z3Act', 'z3TempAct'),
      createSeries('monitor.temperatureCurve.series.z3Set', 'z3TempSet', false),
      createSeries('monitor.temperatureCurve.series.z4Act', 'z4TempAct'),
      createSeries('monitor.temperatureCurve.series.z4Set', 'z4TempSet', false),
      createSeries('monitor.temperatureCurve.series.z5Act', 'z5TempAct'),
      createSeries('monitor.temperatureCurve.series.z5Set', 'z5TempSet', false),
      createSeries('monitor.temperatureCurve.series.z6Act', 'z6TempAct'),
      createSeries('monitor.temperatureCurve.series.z6Set', 'z6TempSet', false),
    ]
  }

  chartInstance.setOption(option)
  window.setTimeout(handleResize, 80)
}

const handleResize = () => chartInstance?.resize()
const getCssVar = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim()

watch(() => props.data, () => nextTick(initChart), { deep: true })
watch(() => props.active, (active) => {
  if (active) nextTick(initChart)
})
watch(() => themeStore.theme, () => nextTick(initChart))

onMounted(() => {
  nextTick(initChart)
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})
</script>

<style scoped>
.curve-component {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.chart-box {
  width: 100%;
  height: 440px;
}

.table-card :deep(.base-card__body) {
  padding: 0;
}

.table-scroll {
  width: 100%;
  padding: 24px;
  overflow: hidden;
}

.monitor-curve-table {
  width: 100%;
}

.temp-warning {
  color: var(--danger);
  font-weight: 650;
}

@media (max-width: 768px) {
  .chart-box {
    height: 320px;
  }

  .table-scroll {
    padding: 16px;
  }
}
</style>
