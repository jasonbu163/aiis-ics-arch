<!--
  文件路径: /frontend-next-js/src/app/monitor/components/EnergyTrendChart.vue
  功能描述: 能耗趋势图表组件
  主要功能:
    - 渲染天然气 (n2) 和电力 (elect) 的变化趋势
    - 支持日夜模式切换
    - 响应式调整图表尺寸
-->
<template>
  <div class="energy-chart-wrapper">
    <div v-if="!trends.length" class="chart-empty">
      <el-empty :description="t('common.noData')" />
    </div>
    <div v-else ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import echarts, { getEChartsTheme } from '@/utils/echarts'
import { useThemeStore } from '@/store/theme'

const { t } = useI18n()
const themeStore = useThemeStore()
const chartRef = ref()
let chart = null

const props = defineProps({
  trends: {
    type: Array,
    default: () => []
  }
})

const initChart = () => {
  if (!chartRef.value || !props.trends.length) return

  if (chart) {
    chart.dispose()
  }

  chart = echarts.init(chartRef.value, getEChartsTheme(themeStore.theme))

  const timeLabels = props.trends.map(item => item.time)
  const primary = getCssVar('--primary')
  const success = getCssVar('--success')

  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: getCssVar('--card-bg'),
      borderColor: getCssVar('--border-primary'),
      textStyle: { color: getCssVar('--text-primary') }
    },
    legend: {
      top: 0,
      data: [t('monitor.energyTrendChart.legendNaturalGas'), t('monitor.energyTrendChart.legendElectricity')],
      textStyle: { color: getCssVar('--text-secondary') }
    },
    grid: {
      left: 48,
      right: 24,
      top: 58,
      bottom: 36
    },
    xAxis: {
      type: 'category',
      data: timeLabels,
      axisLabel: { color: getCssVar('--text-tertiary') }
    },
    yAxis: {
      type: 'value',
      name: t('monitor.energyTrendChart.yAxisName'),
      axisLabel: { color: getCssVar('--text-tertiary') },
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: getCssVar('--border-secondary')
        }
      }
    },
    series: [
      {
        name: t('monitor.energyTrendChart.seriesNaturalGas'),
        type: 'line',
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: success },
            { offset: 1, color: 'transparent' }
          ])
        },
        itemStyle: { color: success },
        data: props.trends.map(item => item.n2)
      },
      {
        name: t('monitor.energyTrendChart.seriesElectricity'),
        type: 'line',
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: primary },
            { offset: 1, color: 'transparent' }
          ])
        },
        itemStyle: { color: primary },
        data: props.trends.map(item => item.elect)
      }
    ]
  }

  chart.setOption(option)
  window.setTimeout(handleResize, 80)
}

const handleResize = () => chart?.resize()
const getCssVar = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim()

watch(() => props.trends, () => nextTick(initChart), { deep: true })
watch(() => themeStore.theme, () => nextTick(initChart))

onMounted(() => {
  nextTick(initChart)
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
})
</script>

<style scoped>
.energy-chart-wrapper {
  width: 100%;
  min-height: 400px;
}

.chart-container {
  width: 100%;
  height: 400px;
}

.chart-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
}
</style>
