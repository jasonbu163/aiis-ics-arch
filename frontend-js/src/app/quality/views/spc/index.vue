<!--
  文件路径: /frontend-next-js/src/app/quality/views/spc/index.vue
  功能描述: SPC 统计过程控制分析页面
  主要功能:
    - 基于后端 SPC 测量点进行控制图、分布图和过程能力分析
    - 支持分析项目、牌号、时间范围与子组大小筛选
    - 展示异常点、分析结论、原始数据与 CSV 导出
    - 兼容日夜模式与国际化
-->
<template>
  <div class="spc-page page-layout">
    <BaseCard class="spc-workspace-card" :title="$t('quality.spc')" body-class="spc-workspace-body">
      <template #actions>
        <div class="page-actions">
          <ActionButton @click="handleExport">
            <el-icon><Download /></el-icon>
            {{ $t('quality.spcPage.form.exportReport') }}
          </ActionButton>
        </div>
      </template>

      <el-form :model="searchForm" class="filter-form" label-position="top">
        <el-form-item :label="$t('quality.spcPage.form.analysisItem')">
          <el-select v-model="searchForm.item" :placeholder="$t('quality.spcPage.form.selectAnalysisItem')">
            <el-option
              v-for="item in analysisItems"
              :key="item"
              :label="$t(`quality.spcPage.items.${item}`)"
              :value="item"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('quality.spcPage.form.grade')">
          <el-select v-model="searchForm.grade" :placeholder="$t('quality.spcPage.form.selectGrade')" clearable>
            <el-option v-for="grade in gradeOptions" :key="grade" :label="grade" :value="grade" />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('quality.spcPage.form.dateRange')">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            :range-separator="$t('quality.spcPage.form.rangeSeparator')"
            :start-placeholder="$t('quality.spcPage.form.startDate')"
            :end-placeholder="$t('quality.spcPage.form.endDate')"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item :label="$t('quality.spcPage.form.subgroupSize')">
          <el-select v-model="searchForm.subgroupSize" :placeholder="$t('quality.spcPage.form.subgroupSize')">
            <el-option v-for="size in subgroupOptions" :key="size" :label="String(size)" :value="size" />
          </el-select>
        </el-form-item>
        <el-form-item class="filter-actions">
          <ActionButton variant="primary" :loading="loading" @click="handleAnalyze">
            <el-icon><DataAnalysis /></el-icon>
            {{ $t('quality.spcPage.form.analyze') }}
          </ActionButton>
          <ActionButton @click="handleReset">
            <el-icon><Refresh /></el-icon>
            {{ $t('common.reset') }}
          </ActionButton>
        </el-form-item>
      </el-form>

      <div class="spc-results-section spc-print-area">
        <el-row :gutter="24" class="metric-row">
          <el-col v-for="metric in metrics" :key="metric.key" :xs="24" :sm="12" :lg="6">
            <MetricCard
              :title="metric.title"
              :value="metric.value"
              :unit="metric.unit"
              :details="metric.details"
              align="start"
            >
              <template #icon>
                <el-icon><component :is="metric.icon" /></el-icon>
              </template>
            </MetricCard>
          </el-col>
        </el-row>

        <el-row :gutter="24" class="chart-row">
          <el-col :xs="24" :lg="16">
            <BaseCard :title="$t(getChartTitleKey(chartType))">
              <template #actions>
                <el-radio-group v-model="chartType" size="small" class="card-action-segmented">
                  <el-radio-button label="xbar">{{ $t('quality.spcPage.charts.xbarTab') }}</el-radio-button>
                  <el-radio-button label="r">{{ $t('quality.spcPage.charts.rTab') }}</el-radio-button>
                  <el-radio-button label="s">{{ $t('quality.spcPage.charts.sTab') }}</el-radio-button>
                </el-radio-group>
              </template>
              <div ref="controlChartRef" class="chart-canvas"></div>
            </BaseCard>
          </el-col>
          <el-col :xs="24" :lg="8">
            <BaseCard :title="$t('quality.spcPage.charts.histogram')">
              <div ref="histogramChartRef" class="chart-canvas"></div>
            </BaseCard>
          </el-col>
        </el-row>

        <el-row :gutter="24" class="chart-row">
          <el-col :xs="24" :lg="12">
            <BaseCard :title="$t('quality.spcPage.charts.capability')">
              <div ref="capabilityChartRef" class="chart-canvas chart-canvas--compact"></div>
            </BaseCard>
          </el-col>
          <el-col :xs="24" :lg="12">
            <BaseCard class="table-card" :title="$t('quality.spcPage.charts.abnormal')">
              <div class="table-scroll">
                <el-table :data="abnormalPoints" border stripe class="vibe-table spc-table" max-height="320">
                  <el-table-column prop="subgroup" :label="$t('quality.spcPage.charts.subgroup')" width="90" />
                  <el-table-column prop="value" :label="$t('quality.spcPage.charts.value')" width="120" align="right">
                    <template #default="{ row }">{{ formatNumber(row.value, 4) }}</template>
                  </el-table-column>
                  <el-table-column prop="type" :label="$t('quality.spcPage.charts.abnormalType')" width="140">
                    <template #default="{ row }">
                      <el-tag :type="row.type === 'outOfLimit' ? 'danger' : 'warning'">
                        {{ $t(`quality.spcPage.abnormal.${row.type}`) }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column :label="$t('quality.spcPage.charts.rule')" min-width="160">
                    <template #default="{ row }">{{ $t(`quality.spcPage.abnormal.${row.rule}`) }}</template>
                  </el-table-column>
                  <el-table-column prop="time" :label="$t('quality.spcPage.charts.time')" width="170">
                    <template #default="{ row }">{{ formatDateTime(row.time) }}</template>
                  </el-table-column>
                </el-table>
              </div>
            </BaseCard>
          </el-col>
        </el-row>

        <BaseCard :title="$t('quality.spcPage.charts.conclusion')">
          <div class="conclusion-section">
            <el-alert
              :title="conclusion.title"
              :type="conclusion.type"
              :description="conclusion.description"
              show-icon
              :closable="false"
            />
            <div class="recommendations">
              <h4>{{ $t('quality.spcPage.charts.recommendations') }}</h4>
              <ul>
                <li v-for="(item, index) in recommendations" :key="index">{{ item }}</li>
              </ul>
            </div>
          </div>
        </BaseCard>

        <BaseCard class="table-card" :title="$t('quality.spcPage.charts.rawData')">
          <template #actions>
            <ActionButton size="small" @click="handleExportData">
              <el-icon><Download /></el-icon>
              {{ $t('quality.spcPage.charts.exportData') }}
            </ActionButton>
          </template>
          <div class="table-scroll">
            <el-table :data="rawData" border stripe class="vibe-table spc-table" max-height="360">
              <el-table-column type="index" :label="$t('quality.spcPage.charts.index')" width="70" />
              <el-table-column prop="coilNo" :label="$t('quality.spcPage.charts.coilNo')" min-width="150" />
              <el-table-column prop="grade" :label="$t('quality.spcPage.charts.grade')" width="100" />
              <el-table-column prop="value" :label="$t('quality.spcPage.charts.value')" width="130" align="right">
                <template #default="{ row }">{{ formatNumber(row.value, 4) }}</template>
              </el-table-column>
              <el-table-column prop="time" :label="$t('quality.spcPage.charts.measureTime')" width="180">
                <template #default="{ row }">{{ formatDateTime(row.time) }}</template>
              </el-table-column>
              <el-table-column prop="operator" :label="$t('quality.spcPage.charts.operator')" width="130" />
              <el-table-column :label="$t('quality.spcPage.charts.status')" width="110" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.isNormal ? 'success' : 'danger'">
                    {{ row.isNormal ? $t('quality.spcPage.status.normalPoint') : $t('quality.spcPage.status.abnormalPoint') }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </BaseCard>
      </div>
    </BaseCard>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Aim,
  DataAnalysis,
  DataLine,
  Download,
  Refresh,
  TrendCharts,
  Warning
} from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import MetricCard from '@/components/common/MetricCard.vue'
import { getSPCData, getSPCStats } from '@/app/quality/api'
import { useThemeStore } from '@/store/theme'
import echarts, { getEChartsTheme } from '@/utils/echarts'
import { exportRowsAsCsv } from '@/utils/exportCsv'

const themeStore = useThemeStore()
const { t, tm, locale } = useI18n()

const analysisItems = ['thickness', 'width', 'tensile', 'yield', 'hardness', 'elongation']
const gradeOptions = ['TA1', 'TA2', 'TA3', 'TC4']
const subgroupOptions = [2, 3, 4, 5]

const searchForm = reactive({
  item: 'thickness',
  grade: '',
  dateRange: [],
  subgroupSize: 5
})

const chartType = ref('xbar')
const loading = ref(false)
const rawData = ref([])
const abnormalPoints = ref([])
const recommendations = ref(tm('quality.spcPage.recommendations'))

const spcStats = reactive({
  cp: 0,
  cpk: 0,
  sigma: 0,
  defectRate: 0,
  mean: 0,
  ucl: 0,
  lcl: 0,
  usl: 0,
  lsl: 0
})

const conclusion = reactive({
  title: '',
  type: 'info',
  description: ''
})

const controlChartRef = ref(null)
const histogramChartRef = ref(null)
const capabilityChartRef = ref(null)

let controlChart = null
let histogramChart = null
let capabilityChart = null

const getCssVar = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim()

const formatNumber = (value, digits = 3) => {
  const number = Number(value)
  return Number.isFinite(number) ? number.toFixed(digits) : '-'
}

const formatDateTime = (value) => {
  if (!value) return '-'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '-' : date.toLocaleString(locale.value)
}

const metricStatus = (value) => {
  if (value >= 1.33) return t('quality.spcPage.status.capable')
  if (value >= 1) return t('quality.spcPage.status.normal')
  return t('quality.spcPage.status.insufficient')
}

const metrics = computed(() => [
  {
    key: 'cp',
    title: t('quality.spcPage.stats.cp'),
    value: formatNumber(spcStats.cp, 3),
    unit: '',
    icon: TrendCharts,
    details: [{ label: t('quality.spcPage.charts.status'), value: metricStatus(spcStats.cp) }]
  },
  {
    key: 'cpk',
    title: t('quality.spcPage.stats.cpk'),
    value: formatNumber(spcStats.cpk, 3),
    unit: '',
    icon: Aim,
    details: [{ label: t('quality.spcPage.charts.status'), value: metricStatus(spcStats.cpk) }]
  },
  {
    key: 'sigma',
    title: t('quality.spcPage.stats.sigma'),
    value: formatNumber(spcStats.sigma, 4),
    unit: '',
    icon: DataLine,
    details: [{ label: 'UCL / LCL', value: `${formatNumber(spcStats.ucl, 4)} / ${formatNumber(spcStats.lcl, 4)}` }]
  },
  {
    key: 'defectRate',
    title: t('quality.spcPage.stats.defectRate'),
    value: formatNumber(spcStats.defectRate, 2),
    unit: '%',
    icon: Warning,
    details: [{ label: t('quality.spcPage.charts.abnormal'), value: String(abnormalPoints.value.length) }]
  }
])

const getChartTitleKey = (type) => {
  const map = {
    xbar: 'quality.spcPage.charts.xbar',
    r: 'quality.spcPage.charts.r',
    s: 'quality.spcPage.charts.s'
  }
  return map[type] || map.xbar
}

const buildParams = () => ({
  item: searchForm.item,
  grade: searchForm.grade || undefined,
  startDate: searchForm.dateRange?.[0] || undefined,
  endDate: searchForm.dateRange?.[1] || undefined,
  subgroupSize: searchForm.subgroupSize
})

const updateConclusion = () => {
  if (!rawData.value.length) {
    conclusion.title = t('common.noData')
    conclusion.type = 'info'
    conclusion.description = t('quality.spcPage.conclusion.emptyDesc')
    return
  }

  if (spcStats.cpk >= 1.33) {
    conclusion.title = t('quality.spcPage.conclusion.excellentTitle')
    conclusion.type = 'success'
    conclusion.description = t('quality.spcPage.conclusion.excellentDesc', { cpk: formatNumber(spcStats.cpk, 2) })
  } else if (spcStats.cpk >= 1) {
    conclusion.title = t('quality.spcPage.conclusion.goodTitle')
    conclusion.type = 'success'
    conclusion.description = t('quality.spcPage.conclusion.goodDesc', { cpk: formatNumber(spcStats.cpk, 2) })
  } else {
    conclusion.title = t('quality.spcPage.conclusion.improveTitle')
    conclusion.type = 'warning'
    conclusion.description = t('quality.spcPage.conclusion.improveDesc', { cpk: formatNumber(spcStats.cpk, 2) })
  }
}

const buildAbnormalPoints = () => {
  abnormalPoints.value = rawData.value
    .filter(item => !item.isNormal)
    .map(item => ({
      subgroup: Math.ceil(item.id / searchForm.subgroupSize),
      value: Number(item.value),
      type: Number(item.value) > spcStats.ucl || Number(item.value) < spcStats.lcl ? 'outOfLimit' : 'trend',
      rule: Number(item.value) > spcStats.ucl ? 'aboveUcl' : 'belowLcl',
      time: item.time
    }))
}

const getSubgroups = () => {
  const subgroupSize = searchForm.subgroupSize
  const subgroupCount = Math.floor(rawData.value.length / subgroupSize)
  const subgroups = []

  for (let index = 0; index < subgroupCount; index += 1) {
    const values = rawData.value
      .slice(index * subgroupSize, (index + 1) * subgroupSize)
      .map(item => Number(item.value))
      .filter(Number.isFinite)

    if (!values.length) continue

    const mean = values.reduce((sum, value) => sum + value, 0) / values.length
    const range = Math.max(...values) - Math.min(...values)
    const std = Math.sqrt(values.reduce((sum, value) => sum + (value - mean) ** 2, 0) / values.length)
    subgroups.push({ mean, range, std })
  }

  return subgroups
}

const initControlChart = () => {
  if (!controlChartRef.value) return
  controlChart?.dispose()
  controlChart = echarts.init(controlChartRef.value, getEChartsTheme(themeStore.theme))

  const subgroups = getSubgroups()
  if (!subgroups.length) {
    controlChart.setOption(emptyChartOption())
    return
  }

  const dataMap = {
    xbar: subgroups.map(item => item.mean),
    r: subgroups.map(item => item.range),
    s: subgroups.map(item => item.std)
  }
  const chartData = dataMap[chartType.value] || dataMap.xbar
  const xAxisData = chartData.map((_, index) => index + 1)
  const center = chartData.reduce((sum, value) => sum + value, 0) / chartData.length
  const upper = chartType.value === 'xbar' ? spcStats.ucl : Math.max(...chartData) * 1.15
  const lower = chartType.value === 'xbar' ? spcStats.lcl : Math.max(0, Math.min(...chartData) * 0.85)

  controlChart.setOption({
    legend: {
      top: 4,
      right: 24,
      data: [t('quality.spcPage.charts.value'), 'UCL', 'LCL', 'CL'],
      textStyle: { color: getCssVar('--text-secondary') }
    },
    tooltip: { trigger: 'axis' },
    grid: { left: 48, right: 24, top: 56, bottom: 36 },
    xAxis: {
      type: 'category',
      data: xAxisData,
      name: t('quality.spcPage.charts.subgroupNo')
    },
    yAxis: {
      type: 'value',
      name: t('quality.spcPage.charts.value')
    },
    series: [
      {
        name: t('quality.spcPage.charts.value'),
        type: 'line',
        data: chartData,
        symbol: 'circle',
        symbolSize: 7,
        lineStyle: { width: 2, color: getCssVar('--primary') },
        itemStyle: { color: getCssVar('--primary') }
      },
      buildLimitLineSeries('UCL', xAxisData, upper, getCssVar('--danger')),
      buildLimitLineSeries('LCL', xAxisData, lower, getCssVar('--danger')),
      buildLimitLineSeries('CL', xAxisData, center, getCssVar('--success'))
    ]
  })
}

const initHistogramChart = () => {
  if (!histogramChartRef.value) return
  histogramChart?.dispose()
  histogramChart = echarts.init(histogramChartRef.value, getEChartsTheme(themeStore.theme))

  const values = rawData.value.map(item => Number(item.value)).filter(Number.isFinite)
  if (!values.length) {
    histogramChart.setOption(emptyChartOption())
    return
  }

  const min = Math.min(...values)
  const max = Math.max(...values)
  const binCount = 12
  const binWidth = max === min ? 1 : (max - min) / binCount
  const bins = Array(binCount).fill(0)

  values.forEach(value => {
    const binIndex = Math.min(Math.floor((value - min) / binWidth), binCount - 1)
    bins[binIndex] += 1
  })

  histogramChart.setOption({
    legend: {
      top: 4,
      right: 16,
      data: [t('quality.spcPage.charts.frequency')],
      textStyle: { color: getCssVar('--text-secondary') }
    },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 44, right: 20, top: 56, bottom: 56 },
    xAxis: {
      type: 'category',
      data: bins.map((_, index) => formatNumber(min + index * binWidth, 3)),
      axisLabel: { rotate: 35 }
    },
    yAxis: { type: 'value', name: t('quality.spcPage.charts.frequency') },
    series: [{
      name: t('quality.spcPage.charts.frequency'),
      type: 'bar',
      data: bins,
      itemStyle: { color: getCssVar('--primary'), borderRadius: [6, 6, 0, 0] }
    }]
  })
}

const initCapabilityChart = () => {
  if (!capabilityChartRef.value) return
  capabilityChart?.dispose()
  capabilityChart = echarts.init(capabilityChartRef.value, getEChartsTheme(themeStore.theme))

  if (!rawData.value.length || !spcStats.sigma) {
    capabilityChart.setOption(emptyChartOption())
    return
  }

  const start = spcStats.lsl - (spcStats.usl - spcStats.lsl) * 0.2
  const end = spcStats.usl + (spcStats.usl - spcStats.lsl) * 0.2
  const points = 80
  const xData = []
  const yData = []

  for (let index = 0; index <= points; index += 1) {
    const x = start + ((end - start) * index) / points
    const y = (1 / (spcStats.sigma * Math.sqrt(2 * Math.PI))) *
      Math.exp(-((x - spcStats.mean) ** 2) / (2 * spcStats.sigma ** 2))
    xData.push(formatNumber(x, 3))
    yData.push(Number(y.toFixed(4)))
  }

  capabilityChart.setOption({
    legend: {
      top: 4,
      right: 24,
      data: [t('quality.spcPage.charts.distribution'), 'LSL', 'USL', 'Mean'],
      textStyle: { color: getCssVar('--text-secondary') }
    },
    tooltip: { trigger: 'axis' },
    grid: { left: 48, right: 24, top: 56, bottom: 42 },
    xAxis: { type: 'category', data: xData },
    yAxis: { type: 'value', name: t('quality.spcPage.charts.density') },
    series: [
      {
        name: t('quality.spcPage.charts.distribution'),
        type: 'line',
        data: yData,
        smooth: true,
        symbol: 'none',
        lineStyle: { color: getCssVar('--primary'), width: 2 },
        areaStyle: { color: getCssVar('--chart-area-weak') }
      },
      buildVerticalLineSeries('LSL', xData, spcStats.lsl, Math.max(...yData), getCssVar('--warning')),
      buildVerticalLineSeries('USL', xData, spcStats.usl, Math.max(...yData), getCssVar('--warning')),
      buildVerticalLineSeries('Mean', xData, spcStats.mean, Math.max(...yData), getCssVar('--success'))
    ]
  })
}

const buildLimitLineSeries = (name, xAxisData, value, color) => ({
  name,
  type: 'line',
  data: xAxisData.map(() => value),
  symbol: 'none',
  lineStyle: { color, width: 1.5, type: 'dashed' },
  tooltip: { valueFormatter: (item) => formatNumber(item, 4) }
})

const buildVerticalLineSeries = (name, xData, value, maxValue, color) => {
  const target = formatNumber(value, 3)
  const index = xData.findIndex(item => Number(item) >= Number(target))
  const data = Array(xData.length).fill(null)
  if (index >= 0) data[index] = maxValue
  return {
    name,
    type: 'bar',
    barWidth: 2,
    data,
    itemStyle: { color },
    tooltip: { valueFormatter: () => target }
  }
}

const emptyChartOption = () => ({
  title: {
    text: t('common.noData'),
    left: 'center',
    top: 'middle',
    textStyle: { color: getCssVar('--text-tertiary'), fontSize: 14, fontWeight: 500 }
  },
  xAxis: { show: false },
  yAxis: { show: false },
  series: []
})

const initCharts = () => {
  initControlChart()
  initHistogramChart()
  initCapabilityChart()
}

const handleAnalyze = async () => {
  loading.value = true
  try {
    const params = buildParams()
    const [dataRes, statsRes] = await Promise.all([
      getSPCData(params),
      getSPCStats(params)
    ])

    rawData.value = dataRes || []
    Object.assign(spcStats, {
      cp: Number(statsRes?.cp || 0),
      cpk: Number(statsRes?.cpk || 0),
      sigma: Number(statsRes?.sigma || 0),
      defectRate: Number(statsRes?.defectRate || 0),
      mean: Number(statsRes?.mean || 0),
      ucl: Number(statsRes?.ucl || 0),
      lcl: Number(statsRes?.lcl || 0),
      usl: Number(statsRes?.usl || 0),
      lsl: Number(statsRes?.lsl || 0)
    })
    buildAbnormalPoints()
    updateConclusion()
    await nextTick()
    initCharts()
    window.setTimeout(() => {
      handleResize()
    }, 120)
  } catch (error) {
    console.error(t('quality.spcPage.messages.analyzeFailed'), error)
    ElMessage.error(t('quality.spcPage.messages.analyzeFailed'))
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  searchForm.item = 'thickness'
  searchForm.grade = ''
  searchForm.dateRange = []
  searchForm.subgroupSize = 5
  handleAnalyze()
}

const handleExport = () => {
  if (!rawData.value.length) {
    ElMessage.warning(t('common.noData'))
    return
  }

  nextTick(() => {
    handleResize()
    document.body.classList.add('spc-printing')
    window.addEventListener('afterprint', () => {
      document.body.classList.remove('spc-printing')
    }, { once: true })
    window.print()
  })
}

const handleExportData = () => {
  const exported = exportRowsAsCsv({
    filename: `spc-raw-data-${Date.now()}.csv`,
    headers: [
      { label: t('quality.spcPage.charts.index'), value: (_, index) => index + 1 },
      { key: 'coilNo', label: t('quality.spcPage.charts.coilNo') },
      { key: 'grade', label: t('quality.spcPage.charts.grade') },
      { label: t('quality.spcPage.charts.value'), value: row => formatNumber(row.value, 4) },
      { label: t('quality.spcPage.charts.measureTime'), value: row => formatDateTime(row.time) },
      { key: 'operator', label: t('quality.spcPage.charts.operator') },
      {
        label: t('quality.spcPage.charts.status'),
        value: row => row.isNormal ? t('quality.spcPage.status.normalPoint') : t('quality.spcPage.status.abnormalPoint')
      }
    ],
    rows: rawData.value
  })

  if (!exported) {
    ElMessage.warning(t('common.noData'))
    return
  }
  ElMessage.success(t('quality.spcPage.messages.exportDataSuccess'))
}

const handleResize = () => {
  controlChart?.resize()
  histogramChart?.resize()
  capabilityChart?.resize()
}

onMounted(() => {
  handleAnalyze()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  controlChart?.dispose()
  histogramChart?.dispose()
  capabilityChart?.dispose()
  window.removeEventListener('resize', handleResize)
})

watch(chartType, () => nextTick(initControlChart))
watch(() => themeStore.theme, () => nextTick(initCharts))
</script>

<style scoped>
.spc-page {
  animation: fadeIn var(--transition-normal);
}

.spc-workspace-card :deep(.spc-workspace-body) {
  padding: 0;
}

.page-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
}

.filter-form {
  display: grid;
  grid-template-columns: minmax(180px, 1fr) minmax(140px, 0.8fr) minmax(280px, 1.3fr) minmax(130px, 0.6fr) auto;
  gap: 16px;
  align-items: end;
  padding: 24px;
  border-bottom: 1px solid var(--border-secondary);
}

.filter-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.filter-form :deep(.el-form-item__label) {
  margin-bottom: 8px;
  padding: 0;
  color: var(--text-secondary);
  font-weight: 520;
  line-height: 1.2;
}

.filter-form :deep(.el-select),
.filter-form :deep(.el-date-editor) {
  width: 100%;
}

.filter-actions :deep(.el-form-item__content) {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  flex-wrap: nowrap;
}

.spc-results-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
}

.metric-row,
.chart-row {
  margin-bottom: 0;
}

.metric-row .el-col,
.chart-row .el-col {
  margin-bottom: 0;
}

.chart-canvas {
  width: 100%;
  height: 360px;
}

.chart-canvas--compact {
  height: 320px;
}

.table-card :deep(.base-card__body) {
  padding: 0;
}

.table-scroll {
  width: 100%;
  padding: 24px;
  overflow: hidden;
}

.spc-table {
  width: 100%;
}

.spc-table :deep(.el-tag) {
  min-width: 56px;
  justify-content: center;
  font-weight: 590;
}

.conclusion-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.recommendations h4 {
  margin: 0 0 10px;
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 590;
}

.recommendations ul {
  display: grid;
  gap: 8px;
  margin: 0;
  padding-left: 18px;
}

.recommendations li {
  color: var(--text-secondary);
  line-height: 1.6;
}

@media (max-width: 1280px) {
  .filter-form {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .filter-actions :deep(.el-form-item__content) {
    justify-content: flex-start;
  }
}

@media print {
  :global(body.spc-printing *) {
    visibility: hidden !important;
  }

  :global(body.spc-printing .spc-print-area),
  :global(body.spc-printing .spc-print-area *) {
    visibility: visible !important;
  }

  :global(body.spc-printing .spc-print-area) {
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
  .page-actions {
    display: none !important;
  }

  .spc-page,
  .spc-print-area {
    padding: 0 !important;
    animation: none !important;
  }

  .spc-print-area {
    gap: 12px;
  }

  .metric-row,
  .chart-row {
    display: flex;
    margin-left: -5px !important;
    margin-right: -5px !important;
  }

  .metric-row :deep(.el-col),
  .chart-row :deep(.el-col) {
    padding-left: 5px !important;
    padding-right: 5px !important;
    margin-bottom: 12px;
  }

  :deep(.base-card) {
    break-inside: avoid;
    background: #fff !important;
    color: #111 !important;
    border: 1px solid #d8dde7 !important;
    box-shadow: none !important;
  }

  :deep(.base-card__header),
  .table-scroll {
    border-color: #d8dde7 !important;
  }

  .chart-canvas,
  .chart-canvas--compact {
    height: 260px;
  }

  .table-scroll {
    padding: 12px;
    overflow: visible;
  }

  .spc-table {
    max-height: none !important;
  }

  @page {
    size: A4 landscape;
    margin: 10mm;
  }
}

@media (max-width: 768px) {
  .page-actions {
    justify-content: flex-start;
  }

  .filter-form {
    grid-template-columns: 1fr;
  }

  .filter-actions :deep(.el-form-item__content) {
    flex-wrap: wrap;
  }

  .chart-canvas,
  .chart-canvas--compact {
    height: 300px;
  }

  .table-scroll {
    padding: 16px;
  }

  .spc-results-section,
  .filter-form {
    padding: 18px;
  }
}
</style>
