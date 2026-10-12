<!--
  文件路径: /frontend-next-js/src/app/performance/views/efficiency/index.vue
  功能描述: 效率统计页面，展示 OEE 设备综合效率分析
  主要功能:
    - OEE 核心指标展示
    - OEE 三要素分析
    - OEE 趋势图表
    - 停机原因分析饼图
    - 按天/班次统计详细数据
    - 报表导出功能
    - 国际化 (i18n) 支持
    - 日夜模式 (Theme) 适配
-->
<template>
  <div class="efficiency-page page-layout">
    <BaseCard class="efficiency-workspace-card" :title="$t('performance.modules.efficiency')" body-class="efficiency-workspace-body">
      <template #actions>
        <ActionButton variant="primary" @click="handleExport">
          <el-icon><Download /></el-icon>
          {{ $t('performance.efficiency.exportReport') }}
        </ActionButton>
      </template>

      <el-form :model="searchForm" class="filter-form" label-position="top">
        <el-form-item :label="$t('performance.common.dateRange')">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            :range-separator="$t('performance.common.to')"
            :start-placeholder="$t('performance.common.startDate')"
            :end-placeholder="$t('performance.common.endDate')"
            value-format="YYYY-MM-DD"
            :shortcuts="dateShortcuts"
          />
        </el-form-item>
        <el-form-item :label="$t('performance.common.shift')">
          <el-select v-model="searchForm.shift" :placeholder="$t('common.all')" clearable>
            <el-option :label="$t('performance.common.dayShift')" value="dayShift" />
            <el-option :label="$t('performance.common.middleShift')" value="middleShift" />
            <el-option :label="$t('performance.common.nightShift')" value="nightShift" />
          </el-select>
        </el-form-item>
        <el-form-item class="filter-actions">
          <ActionButton variant="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            {{ $t('common.search') }}
          </ActionButton>
          <ActionButton @click="handleReset">
            <el-icon><Refresh /></el-icon>
            {{ $t('common.reset') }}
          </ActionButton>
        </el-form-item>
      </el-form>

      <div class="efficiency-results-section">
        <div class="efficiency-export-area">
          <div class="metric-grid">
            <MetricCard
              v-for="metric in metricCards"
              :key="metric.key"
              :title="metric.title"
              :value="metric.value"
              :unit="metric.unit"
              :details="metric.details"
              align="start"
            >
              <template #icon>
                <el-icon>
                  <component :is="metric.icon" />
                </el-icon>
              </template>
            </MetricCard>
          </div>

          <BaseCard :title="$t('performance.efficiency.oeeFactors')">
            <div class="factor-grid">
              <section v-for="factor in factorCards" :key="factor.key" class="factor-panel">
                <header class="factor-header">
                  <div>
                    <h4>{{ factor.title }}</h4>
                    <p>{{ factor.description }}</p>
                  </div>
                  <el-tag :type="getTagType(factor.value)" size="small">{{ factor.value }}%</el-tag>
                </header>
                <el-progress
                  :percentage="factor.value"
                  :color="getProgressColor(factor.value)"
                  :stroke-width="10"
                />
                <div class="factor-detail">
                  <div v-for="detail in factor.details" :key="detail.label" class="detail-row">
                    <span>{{ detail.label }}</span>
                    <strong>{{ detail.value }}</strong>
                  </div>
                </div>
              </section>
            </div>
          </BaseCard>

          <el-row :gutter="20" class="chart-row">
            <el-col :xs="24" :lg="16">
              <BaseCard :title="$t('performance.efficiency.oeeTrend')">
                <div ref="oeeTrendChart" class="chart-canvas"></div>
              </BaseCard>
            </el-col>
            <el-col :xs="24" :lg="8">
              <BaseCard :title="$t('performance.efficiency.downtimeAnalysis')">
                <div ref="downtimeChart" class="chart-canvas"></div>
              </BaseCard>
            </el-col>
          </el-row>

          <BaseCard class="list-card" :title="$t('performance.efficiency.detailedData')">
            <template #actions>
              <el-radio-group v-model="tableType" size="small" class="card-action-segmented">
                <el-radio-button label="daily">{{ $t('performance.common.daily') }}</el-radio-button>
                <el-radio-button label="shift">{{ $t('performance.common.shift') }}</el-radio-button>
              </el-radio-group>
            </template>

            <div class="table-scroll">
              <el-table
                :data="tableData"
                v-loading="loading"
                border
                stripe
                class="vibe-table efficiency-table"
                max-height="420"
              >
                <el-table-column prop="date" :label="$t('performance.common.date')" width="130" fixed />
                <el-table-column v-if="tableType === 'shift'" prop="shift" :label="$t('performance.common.shift')" width="110">
                  <template #default="{ row }">
                    {{ formatShift(row.shift) }}
                  </template>
                </el-table-column>
                <el-table-column prop="plannedTime" :label="`${$t('performance.efficiency.factors.plannedTime')}(${$t('common.unit.hour')})`" width="150" align="right" />
                <el-table-column prop="runningTime" :label="`${$t('performance.efficiency.runningTime')}(${$t('common.unit.hour')})`" width="140" align="right" />
                <el-table-column prop="downtime" :label="`${$t('performance.efficiency.downtime')}(${$t('common.unit.hour')})`" width="140" align="right" />
                <el-table-column prop="processedCoils" :label="$t('performance.efficiency.processedCoils')" width="120" align="right" />
                <el-table-column :label="$t('performance.efficiency.availability')" width="120" align="center">
                  <template #default="{ row }">
                    <el-tag :type="getTagType(row.availability)">{{ row.availability }}%</el-tag>
                  </template>
                </el-table-column>
                <el-table-column :label="$t('performance.efficiency.performance')" width="120" align="center">
                  <template #default="{ row }">
                    <el-tag :type="getTagType(row.performance)">{{ row.performance }}%</el-tag>
                  </template>
                </el-table-column>
                <el-table-column :label="$t('performance.efficiency.quality')" width="120" align="center">
                  <template #default="{ row }">
                    <el-tag :type="getTagType(row.quality)">{{ row.quality }}%</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="OEE" width="110" align="center">
                  <template #default="{ row }">
                    <el-tag :type="getTagType(row.oee)" effect="dark">{{ row.oee }}%</el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <el-pagination
              v-model:current-page="pagination.currentPage"
              v-model:page-size="pagination.pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="pagination.total"
              layout="total, sizes, prev, pager, next, jumper"
              class="pagination"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </BaseCard>
        </div>
      </div>
    </BaseCard>
  </div>
</template>

<script setup>
import { computed, ref, reactive, onMounted, nextTick, onBeforeUnmount, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Box, Clock, TrendCharts, Warning } from '@element-plus/icons-vue'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import MetricCard from '@/components/common/MetricCard.vue'
import echarts, { getEChartsTheme } from '@/utils/echarts'
import { useThemeStore } from '@/store/theme'
import { getEfficiencyData, getEfficiencyOverview, getOEEData } from '@/app/performance/api'

const { t } = useI18n()
const themeStore = useThemeStore()

const searchForm = reactive({
  dateRange: [],
  shift: ''
})

const dateShortcuts = [
  {
    text: t('performance.common.today'),
    value: () => {
      const end = new Date()
      const start = new Date()
      return [start, end]
    }
  },
  {
    text: t('performance.common.last7days'),
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    }
  },
  {
    text: t('performance.common.last30days'),
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    }
  },
  {
    text: t('performance.common.thisMonth'),
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setDate(1)
      return [start, end]
    }
  }
]

const statistics = reactive({
  totalRunningTime: 0,
  oee: 0,
  processedCoils: 0,
  downtime: 0,
  runningTimeChange: 0,
  oeeChange: 0,
  coilsChange: 0,
  downtimeChange: 0
})

const oeeFactors = reactive({
  availability: 0,
  performance: 0,
  quality: 0,
  plannedTime: 0,
  actualTime: 0,
  downtimeLoss: 0,
  theoreticalOutput: 0,
  actualOutput: 0,
  speedLoss: 0,
  totalOutput: 0,
  qualifiedOutput: 0,
  defectOutput: 0
})

const tableType = ref('daily')
const tableData = ref([])
const trendData = ref([])
const downtimeAnalysis = ref([])
const loading = ref(false)

const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

const oeeTrendChart = ref(null)
const downtimeChart = ref(null)
let oeeTrendChartInstance = null
let downtimeChartInstance = null

const getDefaultDateRange = () => {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 6)
  return [
    start.toISOString().slice(0, 10),
    end.toISOString().slice(0, 10)
  ]
}

const formatPercentChange = (value) => `${value >= 0 ? '+' : ''}${Number(value || 0).toFixed(1)}%`

const changeStyle = (value, reversed = false) => {
  const positive = reversed ? Number(value || 0) <= 0 : Number(value || 0) >= 0
  return { color: positive ? 'var(--success)' : 'var(--danger)' }
}

const formatMetric = (value, precision = 1) => Number(value || 0).toFixed(precision)

const formatWithUnit = (value, unitKey, precision = 1) => `${formatMetric(value, precision)}${t(unitKey)}`

const formatShift = (value) => {
  if (!value) return '-'
  const shiftMap = {
    dayShift: 'performance.common.dayShift',
    middleShift: 'performance.common.middleShift',
    nightShift: 'performance.common.nightShift',
    白班: 'performance.common.dayShift',
    中班: 'performance.common.middleShift',
    夜班: 'performance.common.nightShift'
  }
  return t(shiftMap[value] || value)
}

const metricCards = computed(() => [
  {
    key: 'runningTime',
    title: t('performance.efficiency.runningTime'),
    value: formatMetric(statistics.totalRunningTime),
    unit: t('common.unit.hour'),
    icon: Clock,
    details: [
      {
        label: t('performance.efficiency.comparison'),
        value: formatPercentChange(statistics.runningTimeChange),
        valueStyle: changeStyle(statistics.runningTimeChange)
      }
    ]
  },
  {
    key: 'oee',
    title: 'OEE',
    value: formatMetric(statistics.oee),
    unit: '%',
    icon: TrendCharts,
    details: [
      {
        label: t('performance.efficiency.comparison'),
        value: formatPercentChange(statistics.oeeChange),
        valueStyle: changeStyle(statistics.oeeChange)
      }
    ]
  },
  {
    key: 'processedCoils',
    title: t('performance.efficiency.processedCoils'),
    value: statistics.processedCoils,
    unit: t('performance.common.unit.coil'),
    icon: Box,
    details: [
      {
        label: t('performance.efficiency.comparison'),
        value: formatPercentChange(statistics.coilsChange),
        valueStyle: changeStyle(statistics.coilsChange)
      }
    ]
  },
  {
    key: 'downtime',
    title: t('performance.efficiency.downtime'),
    value: formatMetric(statistics.downtime),
    unit: t('common.unit.hour'),
    icon: Warning,
    details: [
      {
        label: t('performance.efficiency.comparison'),
        value: formatPercentChange(statistics.downtimeChange),
        valueStyle: changeStyle(statistics.downtimeChange, true)
      }
    ]
  }
])

const factorCards = computed(() => [
  {
    key: 'availability',
    title: t('performance.efficiency.availability'),
    description: t('performance.efficiency.factorDescriptions.availability'),
    value: oeeFactors.availability,
    details: [
      { label: t('performance.efficiency.factors.plannedTime'), value: formatWithUnit(oeeFactors.plannedTime, 'common.unit.hour') },
      { label: t('performance.efficiency.factors.actualTime'), value: formatWithUnit(oeeFactors.actualTime, 'common.unit.hour') },
      { label: t('performance.efficiency.factors.downtimeLoss'), value: formatWithUnit(oeeFactors.downtimeLoss, 'common.unit.hour') }
    ]
  },
  {
    key: 'performance',
    title: t('performance.efficiency.performance'),
    description: t('performance.efficiency.factorDescriptions.performance'),
    value: oeeFactors.performance,
    details: [
      { label: t('performance.efficiency.factors.theoreticalOutput'), value: `${formatMetric(oeeFactors.theoreticalOutput)}${t('performance.common.unit.coil')}` },
      { label: t('performance.efficiency.factors.actualOutput'), value: `${formatMetric(oeeFactors.actualOutput)}${t('performance.common.unit.coil')}` },
      { label: t('performance.efficiency.factors.speedLoss'), value: `${formatMetric(oeeFactors.speedLoss)}${t('performance.common.unit.coil')}` }
    ]
  },
  {
    key: 'quality',
    title: t('performance.efficiency.quality'),
    description: t('performance.efficiency.factorDescriptions.quality'),
    value: oeeFactors.quality,
    details: [
      { label: t('performance.efficiency.factors.totalOutput'), value: `${formatMetric(oeeFactors.totalOutput)}${t('performance.common.unit.coil')}` },
      { label: t('performance.efficiency.factors.qualifiedOutput'), value: `${formatMetric(oeeFactors.qualifiedOutput)}${t('performance.common.unit.coil')}` },
      { label: t('performance.efficiency.factors.defectOutput'), value: `${formatMetric(oeeFactors.defectOutput)}${t('performance.common.unit.coil')}` }
    ]
  }
])

const buildQueryParams = (extra = {}) => {
  const params = { ...extra }
  if (searchForm.dateRange?.length === 2) {
    params.startDate = searchForm.dateRange[0]
    params.endDate = searchForm.dateRange[1]
  }
  if (searchForm.shift) {
    params.shift = searchForm.shift
  }
  return params
}

const currentGroupBy = () => (tableType.value === 'shift' ? 'shift' : 'day')

const handleSearch = () => {
  pagination.currentPage = 1
  loadData()
}

const handleReset = () => {
  searchForm.dateRange = getDefaultDateRange()
  searchForm.shift = ''
  pagination.currentPage = 1
  loadData()
}

const handleExport = async () => {
  await nextTick()
  handleResize()
  document.body.classList.add('efficiency-printing')
  window.addEventListener('afterprint', () => {
    document.body.classList.remove('efficiency-printing')
  }, { once: true })
  window.print()
}

const loadData = async () => {
  loading.value = true
  try {
    const params = buildQueryParams()
    const [overview, oeeData, efficiencyData] = await Promise.all([
      getEfficiencyOverview(params),
      getOEEData(params),
      getEfficiencyData({
        ...params,
        groupBy: currentGroupBy(),
        page: pagination.currentPage,
        pageSize: pagination.pageSize
      })
    ])

    statistics.totalRunningTime = overview.totalRunningTime || 0
    statistics.runningTimeChange = overview.runningTimeChange || 0
    statistics.oee = overview.oee || 0
    statistics.oeeChange = overview.oeeChange || 0
    statistics.processedCoils = overview.processedCoils || 0
    statistics.coilsChange = overview.coilsChange || 0
    statistics.downtime = overview.downtime || 0
    statistics.downtimeChange = overview.downtimeChange || 0

    oeeFactors.availability = oeeData.availability || 0
    oeeFactors.performance = oeeData.performance || 0
    oeeFactors.quality = oeeData.quality || 0
    oeeFactors.plannedTime = oeeData.plannedTime || 0
    oeeFactors.actualTime = oeeData.actualTime || 0
    oeeFactors.downtimeLoss = oeeData.downtimeLoss || 0
    oeeFactors.theoreticalOutput = oeeData.theoreticalOutput || 0
    oeeFactors.actualOutput = oeeData.actualOutput || 0
    oeeFactors.speedLoss = oeeData.speedLoss || 0
    oeeFactors.totalOutput = oeeData.totalOutput || 0
    oeeFactors.qualifiedOutput = oeeData.qualifiedOutput || 0
    oeeFactors.defectOutput = oeeData.defectOutput || 0

    tableData.value = efficiencyData.items || []
    pagination.total = efficiencyData.total || 0
    trendData.value = oeeData.trend || []
    downtimeAnalysis.value = efficiencyData.downtimeAnalysis || []

    await nextTick()
    initOeeTrendChart()
    initDowntimeChart()
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error(t('performance.messages.loadFailed'))
  } finally {
    loading.value = false
  }
}

const cssVar = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim()

const chartTextColor = () => cssVar('--text-tertiary')
const chartBorderColor = () => cssVar('--border-secondary')
const chartPalette = () => [
  cssVar('--primary'),
  cssVar('--success'),
  cssVar('--warning'),
  cssVar('--danger'),
  cssVar('--info')
]

const initChartInstance = (instance, element) => {
  if (!element) return null
  if (instance) {
    instance.dispose()
  }
  return echarts.init(element, getEChartsTheme(themeStore.isDark ? 'dark' : 'light'))
}

const initOeeTrendChart = () => {
  oeeTrendChartInstance = initChartInstance(oeeTrendChartInstance, oeeTrendChart.value)
  if (!oeeTrendChartInstance) return

  const [primaryColor, successColor, warningColor, dangerColor] = chartPalette()
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: [t('performance.efficiency.availability'), t('performance.efficiency.performance'), t('performance.efficiency.quality'), 'OEE'],
      top: 0,
      textStyle: { color: chartTextColor() }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: 50,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: trendData.value.map(item => item.date.slice(5)),
      axisLabel: { color: chartTextColor() },
      axisLine: { lineStyle: { color: chartBorderColor() } }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLabel: {
        formatter: '{value}%',
        color: chartTextColor()
      },
      splitLine: { lineStyle: { color: chartBorderColor() } }
    },
    series: [
      {
        name: t('performance.efficiency.availability'),
        type: 'line',
        smooth: true,
        data: trendData.value.map(item => item.availability),
        itemStyle: { color: primaryColor }
      },
      {
        name: t('performance.efficiency.performance'),
        type: 'line',
        smooth: true,
        data: trendData.value.map(item => item.performance),
        itemStyle: { color: warningColor }
      },
      {
        name: t('performance.efficiency.quality'),
        type: 'line',
        smooth: true,
        data: trendData.value.map(item => item.quality),
        itemStyle: { color: successColor }
      },
      {
        name: 'OEE',
        type: 'line',
        smooth: true,
        lineStyle: { width: 3 },
        data: trendData.value.map(item => item.oee),
        itemStyle: { color: dangerColor }
      }
    ]
  }

  oeeTrendChartInstance.setOption(option)
}

const initDowntimeChart = () => {
  downtimeChartInstance = initChartInstance(downtimeChartInstance, downtimeChart.value)
  if (!downtimeChartInstance) return

  const [primaryColor, successColor, warningColor, dangerColor, infoColor] = chartPalette()
  const downtimeColorMap = {
    scheduled: warningColor,
    coilChange: primaryColor,
    equipment: dangerColor,
    material: successColor,
    other: infoColor
  }

  const option = {
    title: downtimeAnalysis.value.length
      ? undefined
      : {
          text: t('common.noData'),
          left: 'center',
          top: 'middle',
          textStyle: {
            color: chartTextColor(),
            fontSize: 14,
            fontWeight: 500
          }
        },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}h ({d}%)'
    },
    legend: {
      show: downtimeAnalysis.value.length > 0,
      orient: 'vertical',
      right: '5%',
      top: 'center',
      textStyle: { color: chartTextColor() }
    },
    series: [
      {
        name: t('performance.efficiency.downtimeAnalysis'),
        type: 'pie',
        showEmptyCircle: false,
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: cssVar('--table-fixed-bg'),
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold',
            color: cssVar('--text-primary')
          }
        },
        labelLine: { show: false },
        data: downtimeAnalysis.value.map(item => ({
          name: t(`dashboard.downtimeReasons.${item.name}`),
          value: item.value,
          itemStyle: { color: downtimeColorMap[item.name] || cssVar('--text-muted') }
        }))
      }
    ]
  }

  downtimeChartInstance.setOption(option)
}

const getProgressColor = (percentage) => {
  if (percentage >= 90) return cssVar('--success')
  if (percentage >= 80) return cssVar('--warning')
  return cssVar('--danger')
}

const getTagType = (percentage) => {
  if (percentage >= 90) return 'success'
  if (percentage >= 80) return 'warning'
  return 'danger'
}

const handleSizeChange = (val) => {
  pagination.pageSize = val
  pagination.currentPage = 1
  loadData()
}

const handleCurrentChange = (val) => {
  pagination.currentPage = val
  loadData()
}

const handleResize = () => {
  oeeTrendChartInstance?.resize()
  downtimeChartInstance?.resize()
}

watch(tableType, () => {
  pagination.currentPage = 1
  loadData()
})

watch(
  () => themeStore.isDark,
  async () => {
    await nextTick()
    initOeeTrendChart()
    initDowntimeChart()
  }
)

onMounted(async () => {
  searchForm.dateRange = getDefaultDateRange()
  await loadData()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  oeeTrendChartInstance?.dispose()
  downtimeChartInstance?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.efficiency-page {
  animation: fadeIn var(--transition-normal);
}

.efficiency-workspace-card :deep(.efficiency-workspace-body),
.list-card :deep(.base-card__body) {
  padding: 0;
}

.filter-form {
  display: grid;
  grid-template-columns: minmax(320px, 1.3fr) minmax(180px, 0.7fr) auto;
  gap: 16px;
  align-items: end;
  padding: 24px;
  border-bottom: 1px solid var(--border-secondary);
}

.filter-form :deep(.el-date-editor),
.filter-form :deep(.el-select) {
  width: 100%;
}

.filter-actions {
  align-self: end;
  justify-self: end;
}

.filter-actions :deep(.el-form-item__content) {
  display: flex;
  flex-wrap: nowrap;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-form-item) {
  margin-bottom: 0;
}

:deep(.el-form-item__label) {
  margin-bottom: 8px;
  padding: 0;
  color: var(--text-secondary);
  font-weight: 520;
  line-height: 1.2;
}

.efficiency-export-area {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 24px;
}

.efficiency-results-section {
  min-width: 0;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
}

.factor-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.factor-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 214px;
  padding: 18px;
  border: 1px solid var(--border-secondary);
  border-radius: calc(var(--card-radius) - 8px);
  background: var(--table-fixed-bg);
}

.factor-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.factor-header h4 {
  margin: 0;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 650;
}

.factor-header p {
  margin: 6px 0 0;
  color: var(--text-tertiary);
  font-size: 13px;
  line-height: 1.45;
}

.factor-detail {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 4px;
}

.detail-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-secondary);
  color: var(--text-secondary);
  font-size: 13px;
}

.detail-row:last-child {
  padding-bottom: 0;
  border-bottom: 0;
}

.detail-row strong {
  color: var(--text-primary);
  font-weight: 590;
  text-align: right;
}

.chart-row {
  margin-bottom: 0;
}

.chart-row .el-col {
  margin-bottom: 0;
}

.chart-canvas {
  width: 100%;
  height: 350px;
}

.table-scroll {
  width: 100%;
  padding: 24px 24px 0;
  overflow: hidden;
}

.efficiency-table {
  width: 100%;
}

.efficiency-table :deep(.el-table__fixed),
.efficiency-table :deep(.el-table-fixed-column--left) {
  background: var(--table-fixed-bg) !important;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  padding: 18px 24px 24px;
}

:deep(.el-progress-bar__outer) {
  background-color: var(--border-primary);
}

@media print {
  :global(body.efficiency-printing *) {
    visibility: hidden !important;
  }

  :global(body.efficiency-printing .efficiency-export-area),
  :global(body.efficiency-printing .efficiency-export-area *) {
    visibility: visible !important;
  }

  :global(body.efficiency-printing .efficiency-export-area) {
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
  }

  :global(body) {
    background: #fff !important;
  }

  :global(.app-sidebar),
  :global(.layout-sidebar),
  :global(.sidebar),
  :global(.app-header),
  :global(.layout-header),
  :global(.topbar),
  .filter-form,
  .pagination {
    display: none !important;
  }

  .efficiency-page {
    gap: 12px;
    padding: 0 !important;
    animation: none !important;
  }

  .efficiency-export-area {
    gap: 12px;
    padding: 0;
  }

  .metric-grid,
  .factor-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
  }

  .factor-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .chart-row {
    display: flex;
    margin-left: -5px !important;
    margin-right: -5px !important;
  }

  .chart-row :deep(.el-col) {
    padding-left: 5px !important;
    padding-right: 5px !important;
    margin-bottom: 12px;
  }

  .chart-row :deep(.el-col:first-child) {
    max-width: 66.6667% !important;
    flex: 0 0 66.6667% !important;
  }

  .chart-row :deep(.el-col:last-child) {
    max-width: 33.3333% !important;
    margin-bottom: 12px;
    flex: 0 0 33.3333% !important;
  }

  :deep(.base-card),
  .factor-panel {
    break-inside: avoid;
    background: #fff !important;
    color: #111 !important;
    border: 1px solid #d8dde7 !important;
    box-shadow: none !important;
  }

  :deep(.base-card__header),
  .detail-row,
  .table-scroll {
    border-color: #d8dde7 !important;
  }

  .chart-canvas {
    height: 260px;
  }

  .table-scroll {
    padding: 12px 12px 0;
    overflow: visible;
  }

  .list-card :deep(.el-table) {
    max-height: none !important;
  }

  @page {
    size: A4 landscape;
    margin: 10mm;
  }
}

@media (max-width: 1200px) {
  .metric-grid,
  .factor-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .filter-form,
  .metric-grid,
  .factor-grid {
    grid-template-columns: 1fr;
  }

  .filter-actions :deep(.el-form-item__content) {
    justify-content: flex-start;
  }

  .filter-actions {
    justify-self: start;
  }
}
</style>
