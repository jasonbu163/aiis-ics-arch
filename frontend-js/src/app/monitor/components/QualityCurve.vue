<!--
  文件路径: /frontend-next-js/src/app/monitor/components/QualityCurve.vue
  功能描述: 质量曲线组件
  主要功能:
    - 展示耗氢/耗氮/氧含量/露点/马弗压力趋势及当前值表格
    - 支持日夜模式切换
-->
<template>
  <div class="curve-component">
    <BaseCard :title="t('monitor.temperatureTabs.quality')">
      <div ref="chartRef" class="chart-box"></div>
    </BaseCard>

    <BaseCard class="table-card" :title="t('monitor.qualityCurve.sectionTitle')">
      <div class="table-scroll">
        <el-table :data="tableData" border stripe class="vibe-table monitor-curve-table">
          <el-table-column prop="parameter" :label="t('monitor.qualityCurve.parameter')" />
          <el-table-column prop="value" :label="t('monitor.qualityCurve.currentValue')" align="center" />
          <el-table-column prop="unit" :label="t('monitor.qualityCurve.unit')" align="center" width="100" />
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
    { parameter: t('monitor.qualityCurve.parameters.h2Flow'), value: latest.h2Flow || 0, unit: 'm³/h' },
    { parameter: t('monitor.qualityCurve.parameters.n2Flow'), value: latest.n2Flow || 0, unit: 'm³/h' },
    { parameter: t('monitor.qualityCurve.parameters.oxygen'), value: latest.oxygen || 0, unit: 'ppm' },
    { parameter: t('monitor.qualityCurve.parameters.dewPoint'), value: latest.dewPoint || 0, unit: '℃' },
    { parameter: t('monitor.qualityCurve.parameters.pressure'), value: latest.pressure || 0, unit: 'Pa' },
  ]
})

const initChart = () => {
  if (!chartRef.value || !props.active || !props.data.trends) return

  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = echarts.init(chartRef.value, getEChartsTheme(themeStore.theme))

  const trends = props.data.trends
  const timeLabels = trends.map(t => t.time)

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { top: 0, type: 'scroll', textStyle: { color: getCssVar('--text-secondary') } },
    grid: { left: 48, right: 52, top: 58, bottom: 36 },
    xAxis: {
      type: 'category',
      data: timeLabels,
      axisLabel: { color: getCssVar('--text-tertiary') }
    },
    yAxis: [
      {
        type: 'value',
        name: t('monitor.qualityCurve.yAxisFlow'),
        axisLabel: { color: getCssVar('--text-tertiary') },
        splitLine: { lineStyle: { type: 'dashed', color: getCssVar('--border-secondary') } }
      },
      {
        type: 'value',
        name: t('monitor.qualityCurve.yAxisOther'),
        axisLabel: { color: getCssVar('--text-tertiary') },
        splitLine: { show: false }
      }
    ],
    series: [
      { name: t('monitor.qualityCurve.series.h2Flow'), type: 'line', smooth: true, data: trends.map(t => t.h2Flow), yAxisIndex: 0 },
      { name: t('monitor.qualityCurve.series.n2Flow'), type: 'line', smooth: true, data: trends.map(t => t.n2Flow), yAxisIndex: 0 },
      { name: t('monitor.qualityCurve.series.oxygen'), type: 'line', smooth: true, data: trends.map(t => t.oxygen), yAxisIndex: 1 },
      { name: t('monitor.qualityCurve.series.dewPoint'), type: 'line', smooth: true, data: trends.map(t => t.dewPoint), yAxisIndex: 1 },
      { name: t('monitor.qualityCurve.series.pressure'), type: 'line', smooth: true, data: trends.map(t => t.pressure), yAxisIndex: 1 }
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

@media (max-width: 768px) {
  .chart-box {
    height: 320px;
  }

  .table-scroll {
    padding: 16px;
  }
}
</style>
