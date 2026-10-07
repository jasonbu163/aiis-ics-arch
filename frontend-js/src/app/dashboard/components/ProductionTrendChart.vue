<!--
  文件路径: /frontend-next-js/src/app/dashboard/components/ProductionTrendChart.vue
  功能描述: 产量趋势图表组件
  主要功能:
    - 展示近7日产量趋势
    - 支持线图/柱状图切换
    - 使用 ECharts 官方主题支持日夜模式
    - 后端返回英文键名，前端根据语言翻译显示
-->
<template>
  <BaseCard class="chart-card" :title="$t('dashboard.charts.productionTrend')">
    <template #actions>
      <el-radio-group v-model="trendChartType" size="small" class="card-action-segmented">
        <el-radio-button label="line">{{ $t('dashboard.charts.lineChart') }}</el-radio-button>
        <el-radio-button label="bar">{{ $t('dashboard.charts.barChart') }}</el-radio-button>
      </el-radio-group>
    </template>
    <div ref="chartRef" class="chart-container" style="height: 320px;"></div>
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
  data: { type: Object, default: () => ({ days: [], actual: [], target: [] }) }
})

const trendChartType = ref('line')
const chartRef = ref()
let chart = null

// 将英文键名翻译成当前语言
const translatedDays = computed(() => {
  const dayMap = {
    'mon': t('dashboard.weekdays.mon'),
    'tue': t('dashboard.weekdays.tue'),
    'wed': t('dashboard.weekdays.wed'),
    'thu': t('dashboard.weekdays.thu'),
    'fri': t('dashboard.weekdays.fri'),
    'sat': t('dashboard.weekdays.sat'),
    'sun': t('dashboard.weekdays.sun')
  }
  return (props.data?.days || []).map(day => dayMap[day] || day)
})

const initChart = () => {
  if (!chartRef.value) return
  // 使用官方主题
  const theme = getEChartsTheme(themeStore.theme)
  chart = echarts.init(chartRef.value, theme)
  updateChart()
}

const updateChart = () => {
  if (!chart) return
  const option = {
    tooltip: { 
      trigger: 'axis', 
      axisPointer: { type: 'shadow' }
    },
    legend: { 
      data: [t('dashboard.chart.actual'), t('dashboard.chart.target')], 
      top: 0
    },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '50px', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: translatedDays.value,
      axisLabel: { fontSize: 11 }
    },
    yAxis: { 
      type: 'value', 
      name: t('dashboard.chart.productionUnit'),
      axisLabel: { fontSize: 11 }
    },
    series: [
      { 
        name: t('dashboard.chart.actual'), 
        type: trendChartType.value, 
        data: props.data?.actual || [], 
        smooth: true
      },
      { 
        name: t('dashboard.chart.target'), 
        type: 'line', 
        data: props.data?.target || [], 
        lineStyle: { type: 'dashed' }
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
watch(trendChartType, () => updateChart())

onMounted(() => { nextTick(() => initChart()); window.addEventListener('resize', handleResize) })
onBeforeUnmount(() => { chart?.dispose(); window.removeEventListener('resize', handleResize) })
</script>
