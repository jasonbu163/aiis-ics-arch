<!--
  文件路径: /frontend-next-js/src/app/dashboard/components/DowntimeAnalysisChart.vue
  功能描述: 停机原因分析图组件
  主要功能:
    - 展示停机原因分析柱状图
    - 使用 ECharts 官方主题支持日夜模式
    - 后端返回英文键名，前端根据语言翻译显示
-->
<template>
  <BaseCard class="chart-card" :title="$t('dashboard.charts.downtimeAnalysis')">
    <div ref="chartRef" class="chart-container" style="height: 280px;"></div>
  </BaseCard>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import echarts, { getEChartsTheme } from '@/utils/echarts'
import { useThemeStore } from '@/store/theme'
import BaseCard from '@/components/common/BaseCard.vue'

const { t } = useI18n()
const themeStore = useThemeStore()

const props = defineProps({
  data: { type: Object, default: () => ({ reasons: [], duration: [], colors: [] }) }
})

const chartRef = ref()
let chart = null

// 将英文键名翻译成当前语言
const translatedReasons = computed(() => {
  const reasonMap = {
    'scheduled': t('dashboard.downtimeReasons.scheduled'),
    'coilChange': t('dashboard.downtimeReasons.coilChange'),
    'equipment': t('dashboard.downtimeReasons.equipment'),
    'material': t('dashboard.downtimeReasons.material'),
    'other': t('dashboard.downtimeReasons.other')
  }
  return (props.data?.reasons || []).map(reason => reasonMap[reason] || reason)
})

const initChart = () => {
  if (!chartRef.value) return
  const theme = getEChartsTheme(themeStore.theme)
  chart = echarts.init(chartRef.value, theme)
  updateChart()
}

const updateChart = () => {
  if (!chart) return
  const reasons = translatedReasons.value
  const duration = props.data?.duration || []
  const chartColors = props.data?.colors || []
  const data = reasons.map((reason, index) => ({ 
    value: duration[index] || 0, 
    itemStyle: { color: chartColors[index] }
  }))
  const option = {
    tooltip: { 
      trigger: 'axis', 
      axisPointer: { type: 'shadow' }
    },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '20px', containLabel: true },
    xAxis: { 
      type: 'value', 
      name: t('common.unit.min'),
      axisLabel: { fontSize: 10 }
    },
    yAxis: { 
      type: 'category', 
      data: reasons,
      axisLabel: { fontSize: 10 }
    },
    series: [{ 
      name: t('dashboard.chart.downtimeDuration'), 
      type: 'bar', 
      data: data, 
      barWidth: '60%',
      label: { 
        show: true, 
        position: 'right', 
        formatter: '{c}' + t('common.unit.min')
      } 
    }]
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
