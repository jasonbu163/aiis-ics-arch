<!--
  文件路径: /frontend-next-js/src/app/dashboard/components/TemperatureTrendChart.vue
  功能描述: 炉区温度趋势图组件
  主要功能:
    - 展示炉区温度趋势
    - 支持刷新按钮
    - 使用 ECharts 官方主题支持日夜模式
    - 后端返回英文键名，前端根据语言翻译显示
-->
<template>
  <BaseCard class="chart-card" :title="$t('dashboard.charts.temperatureTrend')">
    <template #actions>
      <el-button text type="primary" size="small" class="card-action-button" @click="$emit('refresh')">
        <el-icon><Refresh /></el-icon>
        {{ $t('common.refresh') }}
      </el-button>
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
  data: { type: Object, default: () => ({ zones: [], hours: [], data: [] }) }
})

defineEmits(['refresh'])

const chartRef = ref()
let chart = null

// 将英文键名翻译成当前语言
const translatedZones = computed(() => {
  const zoneMap = {
    'rtf1': t('dashboard.furnaceZones.rtf') + '1',
    'rtf2': t('dashboard.furnaceZones.rtf') + '2',
    'rtf3': t('dashboard.furnaceZones.rtf') + '3',
    'sf': t('dashboard.furnaceZones.sf'),
    'cf1': t('dashboard.furnaceZones.cf') + '1',
    'cf2': t('dashboard.furnaceZones.cf') + '2'
  }
  return (props.data?.zones || []).map(zone => zoneMap[zone] || zone)
})

const initChart = () => {
  if (!chartRef.value) return
  const theme = getEChartsTheme(themeStore.theme)
  chart = echarts.init(chartRef.value, theme)
  updateChart()
}

const updateChart = () => {
  if (!chart) return
  const zones = translatedZones.value
  const data = props.data?.data || []
  const series = zones.map((zone, index) => ({ 
    name: zone, 
    type: 'line', 
    smooth: true, 
    symbol: 'none', 
    data: data[index] || []
  }))
  const option = {
    tooltip: { 
      trigger: 'axis', 
      axisPointer: { type: 'cross' }
    },
    legend: { 
      data: zones, 
      top: 0
    },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '50px', containLabel: true },
    xAxis: { 
      type: 'category', 
      boundaryGap: false, 
      data: props.data?.hours || [],
      axisLabel: { fontSize: 10 }
    },
    yAxis: { 
      type: 'value', 
      name: t('performance.table.avgTemp') + '(℃)',
      axisLabel: { fontSize: 10 }
    },
    series: series
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
