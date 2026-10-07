<!--
  文件路径: /frontend-next-js/src/app/dashboard/components/OEERadarChart.vue
  功能描述: OEE雷达图组件
  主要功能:
    - 展示OEE分析雷达图
    - 支持本周/上周对比
    - 使用 ECharts 官方主题支持日夜模式
    - 后端返回英文键名，前端根据语言翻译显示
-->
<template>
  <BaseCard class="chart-card" :title="$t('dashboard.charts.oeeAnalysis')">
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
  data: { type: Object, default: () => ({ indicators: [], currentWeek: [], lastWeek: [] }) }
})

const chartRef = ref()
let chart = null

// 将英文键名翻译成当前语言
const translatedIndicators = computed(() => {
  const indicatorMap = {
    'availability': t('dashboard.oeeIndicators.availability'),
    'performance': t('dashboard.oeeIndicators.performance'),
    'quality': t('dashboard.oeeIndicators.quality'),
    'equipmentStability': t('dashboard.oeeIndicators.equipmentStability'),
    'planAchievement': t('dashboard.oeeIndicators.planAchievement')
  }
  return (props.data?.indicators || []).map(indicator => ({
    name: indicatorMap[indicator] || indicator,
    max: 100
  }))
})

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
      trigger: 'item'
    },
    legend: { 
      data: [t('dashboard.chart.thisWeek'), t('dashboard.chart.lastWeek')], 
      top: 0
    },
    radar: { 
      indicator: translatedIndicators.value, 
      center: ['50%', '55%'], 
      radius: '65%'
    },
    series: [{ 
      name: 'OEE', 
      type: 'radar', 
      data: [
        { 
          value: props.data?.currentWeek || [], 
          name: t('dashboard.chart.thisWeek')
        }, 
        { 
          value: props.data?.lastWeek || [], 
          name: t('dashboard.chart.lastWeek')
        }
      ] 
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
