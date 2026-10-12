<!--
  文件路径: /frontend-next-js/src/app/monitor/components/TensionCurve.vue
  功能描述: 张力曲线组件
  主要功能:
    - 展示开卷机/收卷机/炉内张力实时数据及趋势
    - 支持日夜模式切换
-->
<template>
  <div class="curve-component">
    <BaseCard :title="t('monitor.temperatureTabs.tension')">
      <div ref="chartRef" class="chart-box"></div>
    </BaseCard>

    <BaseCard class="table-card" :title="t('monitor.tensionCurve.sectionTitle')">
      <div class="table-scroll">
        <el-table :data="tableData" border stripe class="vibe-table monitor-curve-table">
          <el-table-column prop="position" :label="t('monitor.tensionCurve.position')" />
          <el-table-column prop="value" :label="t('monitor.tensionCurve.actTension')" align="center" />
          <el-table-column prop="unit" :label="t('monitor.tensionCurve.unit')" align="center" width="100" />
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
    { position: t('monitor.tensionCurve.positions.uncoiler'), value: latest.uncTension || 0, unit: '%' },
    { position: t('monitor.tensionCurve.positions.recoiler'), value: latest.recTension || 0, unit: '%' },
    { position: t('monitor.tensionCurve.positions.furnace'), value: latest.furnTension || 0, unit: 'kg' },
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
    legend: { top: 0, textStyle: { color: getCssVar('--text-secondary') } },
    grid: { left: 48, right: 24, top: 58, bottom: 36 },
    xAxis: {
      type: 'category',
      data: timeLabels,
      axisLabel: { color: getCssVar('--text-tertiary') }
    },
    yAxis: {
      type: 'value',
      name: t('monitor.tensionCurve.yAxisName'),
      axisLabel: { color: getCssVar('--text-tertiary') },
      splitLine: { lineStyle: { type: 'dashed', color: getCssVar('--border-secondary') } }
    },
    series: [
      { name: t('monitor.tensionCurve.series.uncoiler'), type: 'line', smooth: true, data: trends.map(t => t.uncTension) },
      { name: t('monitor.tensionCurve.series.recoiler'), type: 'line', smooth: true, data: trends.map(t => t.recTension) },
      { name: t('monitor.tensionCurve.series.furnace'), type: 'line', smooth: true, data: trends.map(t => t.furnTension) }
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
