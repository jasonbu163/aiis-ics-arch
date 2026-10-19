<!--
  文件路径: /frontend-next-js/src/app/monitor/components/SpeedCurve.vue
  功能描述: 速度曲线组件
  主要功能:
    - 展示产线设定/实际速度趋势及当前值表格
    - 支持日夜模式切换
-->
<template>
  <div class="curve-component">
    <BaseCard :title="t('monitor.temperatureTabs.speed')">
      <div ref="chartRef" class="chart-box"></div>
    </BaseCard>

    <BaseCard class="table-card" :title="t('monitor.speedCurve.sectionTitle')">
      <div class="table-scroll">
        <el-table :data="tableData" border stripe class="vibe-table monitor-curve-table">
          <el-table-column prop="label" :label="t('monitor.speedCurve.indicator')" />
          <el-table-column prop="value" :label="t('monitor.speedCurve.speedUnit')" align="center" />
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
    { label: t('monitor.speedCurve.setSpeed'), value: latest.lineSpeedSet ?? '-' },
    { label: t('monitor.speedCurve.actSpeed'), value: latest.lineSpeedAct ?? '-' },
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
    legend: {
      top: 0,
      textStyle: { color: getCssVar('--text-secondary') }
    },
    grid: { left: 48, right: 24, top: 58, bottom: 36 },
    xAxis: {
      type: 'category',
      data: timeLabels,
      axisLabel: { color: getCssVar('--text-tertiary') }
    },
    yAxis: {
      type: 'value',
      name: t('monitor.speedCurve.yAxisName'),
      axisLabel: { color: getCssVar('--text-tertiary') },
      splitLine: { lineStyle: { type: 'dashed', color: getCssVar('--border-secondary') } }
    },
    series: [
      { name: t('monitor.speedCurve.series.actSpeed'), type: 'line', smooth: true, data: trends.map(t => t.lineSpeedAct) },
      { name: t('monitor.speedCurve.series.setSpeed'), type: 'line', smooth: true, lineStyle: { type: 'dashed' }, data: trends.map(t => t.lineSpeedSet) }
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
