<!--
  文件路径: /frontend-next-js/src/app/dashboard/components/QualityPieChart.vue
  功能描述: 质量分布饼图组件
  主要功能:
    - 展示生产质量分布
    - 使用 ECharts 官方主题支持日夜模式
    - 后端返回英文键名，前端根据语言翻译显示
-->
<template>
  <BaseCard class="chart-card" :title="$t('dashboard.charts.qualityDistribution')">
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
  data: { type: Object, default: () => ({ grades: [] }) }
})

const chartRef = ref()
let chart = null

// 将英文键名翻译成当前语言
const translatedGrades = computed(() => {
  const gradeMap = {
    'excellent': t('dashboard.qualityGrades.excellent'),
    'firstClass': t('dashboard.qualityGrades.firstClass'),
    'qualified': t('dashboard.qualityGrades.qualified'),
    'pending': t('dashboard.qualityGrades.pending')
  }
  return (props.data?.grades || []).map(item => ({
    ...item,
    name: gradeMap[item.name] || item.name
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
      trigger: 'item', 
      formatter: '{b}: {c}' + t('common.unit.ton') + ' ({d}%)'
    },
    legend: { 
      orient: 'vertical', 
      right: '2%', 
      bottom: '2%',
      itemWidth: 10,
      itemHeight: 10,
      itemGap: 8,
      textStyle: {
        fontSize: 11
      }
    },
    series: [{ 
      name: t('dashboard.chart.qualityDistribution'), 
      type: 'pie', 
      radius: ['45%', '75%'], 
      center: ['38%', '48%'], 
      avoidLabelOverlap: false, 
      padAngle: 2,
      itemStyle: { 
        borderRadius: 10, 
        borderColor: 'transparent', 
        borderWidth: 2 
      }, 
      label: { 
        show: false, 
        position: 'center', 
        formatter: '{b}\n{d}%',
        fontSize: 2
      }, 
      labelLine: { 
        show: false,
        length: 10,
        length2: 5
      }, 
      emphasis: { 
        label: { 
          show: true, 
          fontSize: 12, 
          fontWeight: 'bold' 
        },
        itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' }
      }, 
      data: translatedGrades.value 
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
