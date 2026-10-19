<!--
  File Path: /frontend-next-js/src/app/equipment/views/temperature/index.vue
  功能描述: 温控部分工艺参数页面，展示加热区温度控制数据
  主要功能:
    - 加热区温度监控（5个加热区）
    - 设定温度与实测温度对比
    - 温度偏差计算与预警
    - 温度曲线总览图表
    - 历史温度记录表格
    - 自动刷新数据
-->
<template>
  <div class="temperature-page page-layout">
    <BaseCard class="temperature-workspace-card" :title="$t('equipment.tempParams.title')" v-loading="loading">
      <template #actions>
        <ActionButton variant="refresh" :loading="loading" @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          {{ $t('common.refresh') }}
        </ActionButton>
      </template>
      <BusinessDataSourceSelect v-model="sourceSelection" />

      <section class="temperature-zone-section">
        <div class="zone-grid">
          <div
            v-for="(zone, index) in heatingZones"
            :key="index"
            class="zone-card"
            :class="`zone-card--${getZoneStatus(zone).tone}`"
          >
            <div class="zone-header">
              <span class="zone-name">{{ $t('equipment.tempParams.zone', { n: index + 1 }) }}</span>
              <el-tag :type="getZoneStatus(zone).type" size="small">
                {{ getZoneStatus(zone).text }}
              </el-tag>
            </div>
            <div class="zone-value">
              {{ formatTemperature(zone.actualTemp) }}
              <span>{{ $t('equipment.common.unit.celsius') }}</span>
            </div>
            <div class="zone-details">
              <div class="detail-row">
                <span>{{ $t('equipment.common.set') }}</span>
                <strong>{{ formatTemperature(zone.setTemp) }}{{ $t('equipment.common.unit.celsius') }}</strong>
              </div>
              <div class="detail-row">
                <span>{{ $t('equipment.common.deviation') }}</span>
                <strong :class="`detail-value--${getZoneStatus(zone).tone}`">
                  {{ getDeviation(zone.actualTemp, zone.setTemp) }}{{ $t('equipment.common.unit.celsius') }}
                </strong>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="temperature-detail-section">
        <div class="content-panel">
          <div class="panel-header">
            <h3>{{ $t('equipment.tempParams.trend') }}</h3>
          </div>
          <div ref="overviewChartRef" class="chart-canvas"></div>
        </div>

        <div class="content-panel">
          <div class="panel-header">
            <h3>{{ $t('equipment.tempParams.history') }}</h3>
          </div>
          <div class="table-scroll">
            <el-table :data="temperatureHistory" border stripe class="vibe-table">
              <el-table-column prop="time" :label="$t('equipment.common.lastUpdate')" width="180" />
              <el-table-column
                v-for="i in 5"
                :key="i"
                :prop="'zone' + i"
                :label="$t('equipment.tempParams.zone', { n: i }) + ' ' + $t('equipment.common.unit.celsius')"
                min-width="130"
              />
            </el-table>
          </div>
        </div>
      </section>
    </BaseCard>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import BusinessDataSourceSelect from '@/components/BusinessDataSourceSelect.vue'
import { parseBusinessDataSource, businessDataSourceQuery, createRequestGeneration } from '@/utils/businessDataSource.mjs'

import { ref, onMounted, onBeforeUnmount, nextTick, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import echarts, { getEChartsTheme } from '@/utils/echarts'
import { useThemeStore } from '@/store/theme'
import { getTemperatureControlData } from '@/app/equipment/api'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const sourceSelection = computed({
  get: () => parseBusinessDataSource(route.query),
  set: value => router.replace({ query: businessDataSourceQuery(route.query, value) })
})
const requestGeneration = createRequestGeneration()

const themeStore = useThemeStore()
const currentTheme = computed(() => themeStore.isDark ? 'dark' : 'light')

// CSS 变量缓存
const cssVarCache = new Map()

/**
 * 获取 CSS 变量值
 * @param {string} name 变量名或包含 var() 的字符串
 * @returns {string} 变量值
 */
const getCSSVar = (name) => {
  if (!name) return ''
  if (cssVarCache.has(name)) return cssVarCache.get(name)
  
  const property = name.startsWith('var(') 
    ? name.replace(/^var\((--.*?)\)$/, '$1') 
    : name
  const value = getComputedStyle(document.documentElement).getPropertyValue(property).trim()
  cssVarCache.set(name, value)
  return value
}

const loading = ref(false)
let updateTimer = null
const overviewChartRef = ref()
let overviewChart = null

const heatingZones = ref([])

const temperatureHistory = ref([])

const getZoneStatus = (zone) => {
  const diff = Math.abs(zone.actualTemp - zone.setTemp)
  if (diff <= 5) return { type: 'success', tone: 'success', text: t('equipment.tempParams.normal') }
  if (diff <= 10) return { type: 'warning', tone: 'warning', text: t('equipment.tempParams.offset') }
  return { type: 'danger', tone: 'danger', text: t('equipment.tempParams.abnormal') }
}

const getDeviation = (actual, set) => {
  const diff = actual - set
  const formattedDiff = diff.toFixed(1)
  return diff > 0 ? `+${formattedDiff}` : formattedDiff
}

const formatTemperature = (value) => value === null || value === undefined ? '-' : Number(value).toFixed(1)

const initOverviewChart = () => {
  if (!overviewChartRef.value) return
  if (!overviewChart) {
    overviewChart = echarts.init(overviewChartRef.value, getEChartsTheme(currentTheme.value))
  }
  updateOverviewChart()
}

const updateOverviewChart = () => {
  if (!overviewChart) return
  
  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: getCSSVar('--card-bg'),
      borderColor: getCSSVar('--border-primary'),
      textStyle: { color: getCSSVar('--text-primary') }
    },
    legend: {
      data: heatingZones.value.map((_, i) => t('equipment.tempParams.zone', { n: i + 1 })),
      bottom: 16,
      textStyle: { color: getCSSVar('--text-secondary') }
    },
    grid: {
      left: 56,
      right: 36,
      top: 36,
      bottom: 78,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: temperatureHistory.value.map(h => h.time),
      axisLine: { lineStyle: { color: getCSSVar('--border-primary') } },
      axisLabel: { color: getCSSVar('--text-tertiary') }
    },
    yAxis: {
      type: 'value',
      name: t('equipment.common.tempUnitLabel'),
      min: (value) => Math.floor(value.min / 10) * 10 - 10,
      max: (value) => Math.ceil(value.max / 10) * 10 + 10,
      axisLine: { lineStyle: { color: getCSSVar('--border-primary') } },
      axisLabel: { color: getCSSVar('--text-tertiary') },
      splitLine: { lineStyle: { color: getCSSVar('--border-secondary'), type: 'dashed' } }
    },
    series: heatingZones.value.map((_, i) => ({
      name: t('equipment.tempParams.zone', { n: i + 1 }),
      type: 'line',
      data: temperatureHistory.value.map(h => h[`zone${i + 1}`]),
      smooth: true,
      symbolSize: 6
    }))
  }
  
  overviewChart.setOption(option, true)
}

const handleRefresh = () => {
  loadData()
}

const applyTemperatureData = (data) => {
  if (!data) return

  heatingZones.value = data.heatingZones || []
  temperatureHistory.value = data.temperatureHistory || []
}

const loadData = async () => {
  const generation = requestGeneration.begin()
  if (!sourceSelection.value.ready) { clearSourceData(); loading.value = false; return }
  loading.value = true
  try {
    const data = await getTemperatureControlData(sourceSelection.value)
    if (!requestGeneration.isCurrent(generation)) return
    applyTemperatureData(data)
    
    await nextTick()
    initOverviewChart()
  } catch (error) {
    if (!requestGeneration.isCurrent(generation)) return
    clearSourceData()
    console.error('Failed to load temperature data:', error)
    ElMessage.error(t('common.loadFailed'))
  } finally {
    if (requestGeneration.isCurrent(generation)) loading.value = false
  }
}

const updateData = () => loadData()

// 监听主题变化，重新初始化图表
watch(currentTheme, () => {
  cssVarCache.clear()
  nextTick(() => {
    initOverviewChart()
  })
})

const clearSourceData = () => {
  heatingZones.value = []
  temperatureHistory.value = []
  overviewChart?.clear()
}
watch(() => [route.query.dataSource, route.query.equipmentId], () => {
  requestGeneration.invalidate()
  clearSourceData()
  loadData()
})

onMounted(() => {
  clearSourceData()
  loadData()
  updateTimer = setInterval(updateData, 5000)
  
  window.addEventListener('resize', handleResize)
})

const handleResize = () => {
  overviewChart?.resize()
}

onBeforeUnmount(() => {
  if (updateTimer) {
    clearInterval(updateTimer)
  }
  window.removeEventListener('resize', handleResize)
  overviewChart?.dispose()
})
</script>

<style scoped>
.temperature-page {
  animation: fadeIn var(--transition-normal);
}

.temperature-workspace-card :deep(.base-card__body) {
  padding: 0;
}

.temperature-zone-section {
  padding: 24px;
  border-bottom: 1px solid var(--border-secondary);
}

.zone-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 16px;
}

.zone-card {
  min-width: 0;
  background: var(--card-bg);
  border: 1px solid var(--border-secondary);
  border-left: 4px solid var(--success);
  border-radius: calc(var(--card-radius) - 4px);
  padding: 18px;
  box-shadow: var(--shadow-sm);
  transition: border-color var(--transition-normal), box-shadow var(--transition-normal);
}

.zone-card:hover {
  border-color: var(--border-primary);
  box-shadow: var(--shadow-sm);
}

.zone-card--warning {
  border-left-color: var(--warning);
}

.zone-card--danger {
  border-left-color: var(--danger);
}

.zone-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.zone-name {
  font-size: 14px;
  font-weight: 650;
  color: var(--text-primary);
}

.zone-value {
  margin-top: 22px;
  color: var(--text-primary);
  font-size: 34px;
  font-weight: 720;
  line-height: 1;
}

.zone-value span {
  margin-left: 4px;
  color: var(--text-secondary);
  font-size: 15px;
  font-weight: 590;
}

.zone-details {
  display: grid;
  gap: 10px;
  margin-top: 22px;
  padding-top: 16px;
  border-top: 1px solid var(--border-secondary);
}

.detail-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.detail-row span {
  color: var(--text-secondary);
  font-size: 13px;
}

.detail-row strong {
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 650;
}

.detail-value--success {
  color: var(--success) !important;
}

.detail-value--warning {
  color: var(--warning) !important;
}

.detail-value--danger {
  color: var(--danger) !important;
}

.chart-canvas {
  width: 100%;
  height: 420px;
}

.temperature-detail-section {
  display: grid;
  gap: 24px;
  padding: 24px;
}

.content-panel {
  min-width: 0;
  overflow: hidden;
  background: var(--card-bg);
  border: 1px solid var(--border-secondary);
  border-radius: var(--card-radius);
  box-shadow: var(--shadow-sm);
}

.panel-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-secondary);
}

.panel-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 650;
}

.table-scroll {
  width: 100%;
  padding: 24px;
  overflow-x: auto;
}

@media (max-width: 1400px) {
  .zone-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .zone-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .temperature-page {
    animation: fadeIn var(--transition-normal);
  }

  .temperature-zone-section,
  .temperature-detail-section {
    padding: 16px;
  }

  .zone-grid {
    grid-template-columns: 1fr;
  }

  .table-scroll {
    padding: 16px;
  }

  .chart-canvas {
    height: 320px;
  }
}
</style>
