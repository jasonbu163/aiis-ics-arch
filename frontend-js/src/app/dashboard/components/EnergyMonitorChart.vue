<!--
  文件路径: /frontend-next-js/src/app/dashboard/components/EnergyMonitorChart.vue
  功能描述: 能耗监控图组件
  主要功能:
    - 展示电力和燃气能耗趋势
    - 使用 ECharts 官方主题支持日夜模式
-->
<template>
  <BaseCard class="chart-card" :title="$t('dashboard.charts.energyMonitor')">
    <div ref="chartRef" class="chart-container" style="height: 280px;"></div>
  </BaseCard>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import echarts, { getEChartsTheme } from '@/utils/echarts'
import { useThemeStore } from '@/store/theme'
import BaseCard from '@/components/common/BaseCard.vue'

const { t } = useI18n()
const themeStore = useThemeStore()

const props = defineProps({
  data: { type: Object, default: () => ({ hours: [], electricity: [], gas: [] }) }
})

const chartRef = ref()
let chart = null

const initChart = () => {
  if (!chartRef.value) return
  const theme = getEChartsTheme(themeStore.theme)
  chart = echarts.init(chartRef.value, theme)
  updateChart()
}

const updateChart = () => {
  if (!chart) return
  const option = {
    tooltip: { 
      trigger: 'axis', 
      axisPointer: { type: 'cross' }
    },
    legend: { 
      data: [t('dashboard.chart.electricity'), t('dashboard.chart.gas')], 
      top: 0
    },
    grid: { left: '3%', right: '8%', bottom: '3%', top: '50px', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: props.data?.hours || [], 
      boundaryGap: false,
      axisLabel: { fontSize: 10 }
    },
    yAxis: [
      { 
        type: 'value', 
        name: t('dashboard.chart.electricityUnit'), 
        position: 'left',
        axisLabel: { fontSize: 10 }
      }, 
      { 
        type: 'value', 
        name: t('dashboard.chart.gasUnit'), 
        position: 'right',
        axisLabel: { fontSize: 10 }
      }
    ],
    series: [
      { 
        name: t('dashboard.chart.electricity'), 
        type: 'line', 
        smooth: true, 
        data: props.data?.electricity || [],
        areaStyle: {}
      },
      { 
        name: t('dashboard.chart.gas'), 
        type: 'line', 
        smooth: true, 
        yAxisIndex: 1, 
        data: props.data?.gas || [],
        areaStyle: {}
      }
    ]
  }
  chart.setOption(option)
}

const handleResize = () => chart?.resize()

// 监听主题变化，重新初始化图表
watch(() => themeStore.theme, () => {
  if (chart) {
    chart.dispose()
    initChart()
  }
})

watch(() => props.data, () => { nextTick(() => { if (!chart) initChart(); else updateChart(); }) }, { deep: true })

onMounted(() => { nextTick(() => initChart()); window.addEventListener('resize', handleResize) })
onBeforeUnmount(() => { chart?.dispose(); window.removeEventListener('resize', handleResize) })
</script>
