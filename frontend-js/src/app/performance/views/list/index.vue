<!--
  文件路径: /frontend-next-js/src/app/performance/views/list/index.vue
  功能描述: 实绩列表页面，展示生产实绩数据，支持增删改查和打印标签
  主要功能:
    - 展示实绩数据表格，支持分页和排序
    - 提供料卷号、生产状态、日期范围筛选
    - 支持新增、编辑、删除实绩记录
    - 提供打印标签功能
    - 支持导出数据
    - 国际化 (i18n) 支持
    - 日夜模式 (Theme) 适配
-->
<template>
  <div class="performance-list-page page-layout">
    <BaseCard class="list-card" :title="$t('performance.list')">
      <template #actions>
        <div class="table-actions">
          <ActionButton
            v-if="!isHttpSource"
            variant="primary"
            :disabled="!selectedRows.length"
            :loading="printing"
            @click="handlePrintSelected"
          >
            <el-icon><Printer /></el-icon>
            {{ $t('performance.common.printSelected') }}
          </ActionButton>
          <ActionButton variant="refresh" :loading="loading" @click="handleRefresh">
            <el-icon><Refresh /></el-icon>
            {{ $t('common.refresh') }}
          </ActionButton>
        </div>
      </template>

      <BusinessDataSourceSelect v-model="sourceSelection" />
      <div class="filter-section">
        <el-form :model="searchForm" class="filter-form" label-position="top">
          <el-form-item :label="$t('performance.coilNo')">
            <el-input v-model="searchForm.coilNo" :placeholder="$t('performance.form.placeholder', { label: $t('performance.coilNo') })" clearable />
          </el-form-item>
          <el-form-item :label="$t('performance.observationStatus')">
            <el-select
              v-model="searchForm.observationStatus"
              :placeholder="$t('performance.form.selectPlaceholder', { label: $t('performance.observationStatus') })"
              clearable
            >
              <el-option
                v-for="option in observationStatusOptions"
                :key="option"
                :label="$t(`performance.observationStatusMap.${option}`)"
                :value="option"
              />
            </el-select>
          </el-form-item>
          <el-form-item :label="$t('performance.common.dateRange')">
            <el-date-picker
              v-model="searchForm.dateRange"
              type="daterange"
              :range-separator="$t('performance.common.to')"
              :start-placeholder="$t('performance.common.startDate')"
              :end-placeholder="$t('performance.common.endDate')"
              value-format="YYYY-MM-DD"
            />
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
      </div>

      <div class="table-scroll">
        <el-table
          :data="tableData"
          v-loading="loading"
          @selection-change="handleSelectionChange"
          stripe
          border
          class="vibe-table performance-table"
        >
          <el-table-column type="selection" width="52" />
          <el-table-column prop="coilNo" :label="$t('performance.coilNo')" width="150" />
          <el-table-column prop="parentCoilNo" :label="$t('performance.parentCoilNo')" width="150">
            <template #default="{ row }">
              {{ displayParentCoilNo(row) }}
            </template>
          </el-table-column>
          <el-table-column prop="grade" :label="$t('performance.grade')" width="100" />
          <el-table-column prop="spec" :label="$t('performance.spec')" width="130">
            <template #default="{ row }">
              {{ displayText(row.spec) }}
            </template>
          </el-table-column>
          <el-table-column prop="weight" :label="`${$t('performance.weight')}(${$t('common.unit.ton')})`" width="120" align="right">
            <template #default="{ row }">
              {{ formatNullableNumber(row.weight, 4) }}
            </template>
          </el-table-column>
          <el-table-column prop="totalLength" :label="`${$t('performance.totalLength')}(${$t('common.unit.m')})`" width="120" align="right">
            <template #default="{ row }">
              {{ formatNullableNumber(row.totalLength, 2) }}
            </template>
          </el-table-column>
          <el-table-column prop="diameter" :label="`${$t('performance.diameter')}(${$t('common.unit.mm')})`" width="120" align="right">
            <template #default="{ row }">
              {{ formatNullableNumber(row.diameter, 2) }}
            </template>
          </el-table-column>
          <el-table-column prop="density" :label="$t('performance.density')" width="110" align="right">
            <template #default="{ row }">
              {{ formatNullableNumber(row.density, 3) }}
            </template>
          </el-table-column>
          <el-table-column prop="observationStatus" :label="$t('performance.observationStatus')" width="130">
            <template #default="{ row }">
              <el-tag :type="observationStatusTagType(row.observationStatus)" size="small">
                {{ $t(`performance.observationStatusMap.${observationStatusKey(row.observationStatus)}`) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="planId" :label="$t('performance.planLink.statusColumn')" width="120">
            <template #default="{ row }">
              <el-tag :type="row.planId ? 'success' : 'info'" size="small">
                {{ row.planId ? $t('performance.planLink.linked') : $t('performance.planLink.unlinked') }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="recordSource" :label="$t('performance.recordSource')" width="150">
            <template #default="{ row }">
              {{ formatRecordSource(row.recordSource) }}
            </template>
          </el-table-column>
          <el-table-column prop="totalDurationSeconds" :label="$t('performance.totalDuration')" width="130">
            <template #default="{ row }">
              <el-tooltip :content="$t(`performance.durationSourceMap.${durationSourceKey(row.totalDurationSource)}`)" placement="top">
                <span>{{ formatBackendDuration(row.totalDurationSeconds, t) }}</span>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column prop="isSplit" :label="$t('performance.splitStatus')" width="110">
            <template #default="{ row }">
              <div v-if="isRootPerformance(row)">
                <el-tag v-if="row.isSplitted" type="warning" size="small">
                  {{ $t('performance.splitStatusMap.splitted') }} ({{ row.splitCount || 0 }})
                </el-tag>
                <el-tag v-else type="info" size="small">{{ $t('performance.splitStatusMap.notSplit') }}</el-tag>
              </div>
              <el-tag v-else type="success" size="small">{{ $t('performance.splitStatusMap.child') }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column :label="$t('common.actions')" width="270" fixed="right" align="center">
            <template #default="{ row }">
              <div class="row-actions" @click.stop>
                <ActionButton variant="row" size="small" @click="handleEdit(row)">
                  {{ $t('common.edit') }}
                </ActionButton>
                <ActionButton v-if="!isHttpSource" variant="success" size="small" @click="handlePrint(row)">
                  {{ $t('common.print') }}
                </ActionButton>
                <ActionButton variant="warning" size="small" @click="handleChart(row)">
                  {{ $t('common.data') }}
                </ActionButton>
                <ActionButton
                  v-if="isPlanLinkable(row)"
                  variant="secondary"
                  size="small"
                  @click="handleOpenPlanLink(row)"
                >
                  {{ $t('performance.planLink.rowAction') }}
                </ActionButton>
              </div>
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
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        class="pagination"
      />
    </BaseCard>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="$t('performance.edit')"
      width="920px"
      @close="handleDialogClose"
      class="standard-form-dialog"
      modal-class="performance-dialog-mask"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="isHttpSource ? {} : rules"
        label-position="top"
        class="standard-dialog-form"
      >
        <section class="dialog-section">
          <h3 class="dialog-section__title">{{ $t('performance.formSections.basicInfo') }}</h3>
          <div class="dialog-form-grid">
            <el-form-item :label="$t('performance.form.coilNo')" prop="coilNo">
              <el-input v-model="form.coilNo" disabled>
                <template #prefix>
                  <el-icon><Tickets /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item :label="$t('performance.form.grade')" prop="grade">
              <el-input v-model="form.grade" :disabled="isHttpSource" :placeholder="$t('performance.form.placeholder', { label: $t('performance.form.grade') })">
                <template #prefix>
                  <el-icon><PriceTag /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item :label="$t('performance.form.density')" prop="density">
              <el-input-number v-model="form.density" :disabled="isHttpSource" :min="0" :precision="4" :step="0.001" :value-on-clear="null" clearable />
            </el-form-item>
          </div>
        </section>

        <section class="dialog-section">
          <h3 class="dialog-section__title">{{ $t('performance.formSections.specParams') }}</h3>
          <div class="dialog-form-grid">
            <el-form-item :label="$t('performance.form.weight')" prop="weight">
              <el-input-number v-model="form.weight" :min="0" :precision="isHttpSource ? 4 : 3" :step="0.1" :value-on-clear="null" clearable>
                <template #suffix>
                  <span class="unit-text">{{ $t('common.unit.ton') }}</span>
                </template>
              </el-input-number>
            </el-form-item>
            <el-form-item :label="$t('performance.form.spec')" prop="spec">
              <el-input v-model="form.spec" :disabled="isHttpSource" :placeholder="$t('performance.form.placeholder', { label: $t('performance.form.spec') })">
                <template #prefix>
                  <el-icon><Grid /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item :label="$t('performance.form.totalLength')" prop="totalLength">
              <el-input-number v-model="form.totalLength" :disabled="isHttpSource" :min="0" :precision="2" :step="1" :value-on-clear="null" clearable>
                <template #suffix>
                  <span class="unit-text">{{ $t('common.unit.m') }}</span>
                </template>
              </el-input-number>
            </el-form-item>
            <el-form-item :label="$t('performance.form.diameter')" prop="diameter">
              <el-input-number v-model="form.diameter" :disabled="isHttpSource" :min="0" :precision="2" :step="1" :value-on-clear="null" clearable>
                <template #suffix>
                  <span class="unit-text">{{ $t('common.unit.mm') }}</span>
                </template>
              </el-input-number>
            </el-form-item>
            <el-form-item :label="$t('performance.form.startTime')" prop="startTime">
              <el-date-picker
                v-model="form.startTime" :disabled="isHttpSource"
                type="datetime"
                :placeholder="$t('performance.form.selectPlaceholder', { label: $t('performance.form.startTime') })"
                value-format="YYYY-MM-DD HH:mm:ss"
                clearable
              />
            </el-form-item>
            <el-form-item :label="$t('performance.form.endTime')" prop="endTime">
              <el-date-picker
                v-model="form.endTime" :disabled="isHttpSource"
                type="datetime"
                :placeholder="$t('performance.form.selectPlaceholder', { label: $t('performance.form.endTime') })"
                value-format="YYYY-MM-DD HH:mm:ss"
                clearable
              />
            </el-form-item>
          </div>
        </section>

        <section class="dialog-section">
          <h3 class="dialog-section__title">{{ $t('performance.formSections.otherInfo') }}</h3>
          <el-form-item class="form-item-wide" :label="$t('performance.form.remark')" prop="remark">
            <el-input v-model="form.remark" type="textarea" :rows="3" :placeholder="$t('performance.form.placeholder', { label: $t('performance.form.remark') })" show-word-limit maxlength="500" />
          </el-form-item>
        </section>
      </el-form>
      <template #footer>
        <div class="vibe-dialog-footer">
          <ActionButton @click="dialogVisible = false">
            <el-icon><Close /></el-icon>
            {{ $t('common.cancel') }}
          </ActionButton>
          <ActionButton variant="primary" @click="handleSubmit" :loading="submitLoading">
            <el-icon><Check /></el-icon>
            {{ $t('common.save') }}
          </ActionButton>
        </div>
      </template>
    </el-dialog>

    <!-- 图表数据对话框 -->
    <el-dialog
      v-model="chartDialogVisible"
      :title="$t('performance.processData')"
      width="85%"
      top="3vh"
      class="process-dialog"
      modal-class="performance-dialog-mask"
      destroy-on-close
    >
      <el-tabs v-model="activeChartTab" class="process-tabs">
        <el-tab-pane :label="$t('performance.temperatureCurve')" name="temperature">
          <div class="chart-section">
            <div ref="tempChartRef" class="process-chart"></div>
            <el-table :data="tempTableData" border stripe class="vibe-table process-table">
              <el-table-column prop="zone" :label="$t('performance.table.zone')" width="120" />
              <el-table-column prop="maxTemp" :label="`${$t('performance.table.maxTemp')}(${$t('performance.units.celsius')})`" width="120">
                <template #default="{ row }">
                  {{ formatNullableNumber(row.maxTemp, 2) }}
                </template>
              </el-table-column>
              <el-table-column prop="minTemp" :label="`${$t('performance.table.minTemp')}(${$t('performance.units.celsius')})`" width="120">
                <template #default="{ row }">
                  {{ formatNullableNumber(row.minTemp, 2) }}
                </template>
              </el-table-column>
              <el-table-column prop="avgTemp" :label="`${$t('performance.table.avgTemp')}(${$t('performance.units.celsius')})`" width="120">
                <template #default="{ row }">
                  {{ formatNullableNumber(row.avgTemp, 2) }}
                </template>
              </el-table-column>
              <el-table-column prop="duration" :label="`${$t('performance.table.duration')}(${$t('common.unit.min')})`" width="120">
                <template #default="{ row }">
                  {{ row.duration || '-' }}
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
        <el-tab-pane :label="$t('performance.tensionCurve')" name="tension">
          <div class="chart-section">
            <div ref="tensionChartRef" class="process-chart"></div>
            <el-table :data="tensionTableData" border stripe class="vibe-table process-table">
              <el-table-column prop="zone" :label="$t('performance.table.zone')" width="150" />
              <el-table-column prop="setTension" :label="`${$t('performance.table.setTension')}(${$t('performance.units.kN')})`" width="120">
                <template #default="{ row }">
                  {{ formatNullableNumber(row.setTension, 2) }}
                </template>
              </el-table-column>
              <el-table-column prop="avgTension" :label="`${$t('performance.table.avgTension')}(${$t('performance.units.kN')})`" width="120">
                <template #default="{ row }">
                  {{ formatNullableNumber(row.avgTension, 2) }}
                </template>
              </el-table-column>
              <el-table-column prop="maxTension" :label="`${$t('performance.table.maxTension')}(${$t('performance.units.kN')})`" width="120">
                <template #default="{ row }">
                  {{ formatNullableNumber(row.maxTension, 2) }}
                </template>
              </el-table-column>
              <el-table-column prop="minTension" :label="`${$t('performance.table.minTension')}(${$t('performance.units.kN')})`" width="120">
                <template #default="{ row }">
                  {{ formatNullableNumber(row.minTension, 2) }}
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
        <el-tab-pane :label="$t('performance.speedCurve')" name="speed">
          <div class="chart-section">
            <div ref="speedChartRef" class="process-chart"></div>
            <el-table :data="speedTableData" border stripe class="vibe-table process-table">
              <el-table-column prop="zone" :label="$t('performance.table.zone')" width="150" />
              <el-table-column prop="setSpeed" :label="`${$t('performance.table.setSpeed')}(${$t('common.unit.speed')})`" width="140">
                <template #default="{ row }">
                  {{ formatNullableNumber(row.setSpeed, 2) }}
                </template>
              </el-table-column>
              <el-table-column prop="avgSpeed" :label="`${$t('performance.table.avgSpeed')}(${$t('common.unit.speed')})`" width="140">
                <template #default="{ row }">
                  {{ formatNullableNumber(row.avgSpeed, 2) }}
                </template>
              </el-table-column>
              <el-table-column prop="maxSpeed" :label="`${$t('performance.table.maxSpeed')}(${$t('common.unit.speed')})`" width="140">
                <template #default="{ row }">
                  {{ formatNullableNumber(row.maxSpeed, 2) }}
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>

    <PerformancePlanLinkDialog
      v-model="planLinkDialogVisible"
      :performance="planLinkPerformance"
      @linked="handlePlanLinked"
    />
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import BusinessDataSourceSelect from '@/components/BusinessDataSourceSelect.vue'
import { parseBusinessDataSource, businessDataSourceQuery, createRequestGeneration } from '@/utils/businessDataSource.mjs'

import { ref, reactive, onMounted, onUnmounted, nextTick, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import echarts, { getEChartsTheme } from '@/utils/echarts'
import { useThemeStore } from '@/store/theme'
import { getPerformanceList, updatePerformance, getProcessData, getPrintData } from '@/app/performance/api'
import { createPerformancePrintDocument } from '@/app/performance/utils/print-document.mjs'
import {
  loadStoredPrintTemplate,
  normalizePrintTemplate
} from '@/app/performance/utils/print-template.mjs'
import {
  displayParentCoilNo,
  displayText,
  durationSourceKey,
  formatBackendDuration,
  formatNullableNumber,
  isRootPerformance,
  normalizeNullableDateTime,
  normalizeNullableNumber,
  observationStatusKey
} from './performance-presentation.mjs'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import PerformancePlanLinkDialog from '@/app/performance/components/PerformancePlanLinkDialog.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const sourceSelection = computed({
  get: () => parseBusinessDataSource(route.query),
  set: value => router.replace({ query: businessDataSourceQuery(route.query, value) })
})
const requestGeneration = createRequestGeneration()
const processGeneration = createRequestGeneration()
const isHttpSource = computed(() => sourceSelection.value.dataSource === 'http')

const themeStore = useThemeStore()

const searchForm = reactive({
  coilNo: '',
  observationStatus: '',
  dateRange: []
})

const observationStatusOptions = computed(() => [
  'in_production',
  'not_in_production',
  'unknown',
  ...(isHttpSource.value ? [] : ['manual_historical'])
])

const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

const tableData = ref([])
const loading = ref(false)
const printing = ref(false)
const selectedRows = ref([])
const planLinkDialogVisible = ref(false)
const planLinkPerformance = ref(null)

const dialogVisible = ref(false)
const formRef = ref()
const submitLoading = ref(false)

const form = reactive({
  id: null,
  coilNo: '',
  grade: '',
  density: null,
  weight: null,
  spec: '',
  totalLength: null,
  diameter: null,
  startTime: null,
  endTime: null,
  remark: ''
})

const rules = {
  grade: [
    { required: true, message: t('performance.form.placeholder', { label: t('performance.form.grade') }), trigger: 'blur' }
  ]
}

const chartDialogVisible = ref(false)
const activeChartTab = ref('temperature')
const tempChartRef = ref()
const tensionChartRef = ref()
const speedChartRef = ref()
const tempTableData = ref([])
const tensionTableData = ref([])
const speedTableData = ref([])
const currentCoilNo = ref('')

let tempChartInstance = null
let tensionChartInstance = null
let speedChartInstance = null

const getCssVar = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim()

const getChartTokens = () => ({
  primary: getCssVar('--primary'),
  success: getCssVar('--success'),
  warning: getCssVar('--warning'),
  danger: getCssVar('--danger'),
  textPrimary: getCssVar('--text-primary'),
  textSecondary: getCssVar('--text-secondary'),
  border: getCssVar('--border-secondary')
})

const getChartAxis = (tokens) => ({
  axisLabel: { color: tokens.textSecondary },
  axisLine: { lineStyle: { color: tokens.border } },
  splitLine: { lineStyle: { color: tokens.border } }
})

const observationStatusTagType = (status) => {
  const key = observationStatusKey(status)
  if (key === 'in_production') return 'success'
  if (key === 'not_in_production') return 'info'
  if (key === 'unknown') return 'warning'
  return ''
}

const formatRecordSource = (recordSource) => {
  if (!recordSource) return '-'
  const key = `performance.recordSources.${recordSource}`
  const translated = t(key)
  return translated === key ? recordSource : translated
}

const isPlanLinkable = (row) => {
  return row?.recordSource === 'unplanned_plc' && !row?.planId
}

const loadData = async () => {
  const generation = requestGeneration.begin()
  if (!sourceSelection.value.ready) { tableData.value = []; pagination.total = 0; loading.value = false; return }
  loading.value = true
  try {
    const params = {
      ...sourceSelection.value,
      page: pagination.currentPage,
      pageSize: pagination.pageSize
    }
    
    if (searchForm.coilNo) {
      params.coilNo = searchForm.coilNo
    }
    if (searchForm.observationStatus) {
      params.observationStatus = searchForm.observationStatus
    }
    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.startDate = searchForm.dateRange[0]
      params.endDate = searchForm.dateRange[1]
    }
    
    const res = await getPerformanceList(params)
    if (!requestGeneration.isCurrent(generation)) return
    
    if (res && res.items) {
      tableData.value = res.items || []
      pagination.total = res.total || 0
    } else {
      ElMessage.error(res?.message || t('performance.messages.loadFailed'))
    }
  } catch (error) {
    if (!requestGeneration.isCurrent(generation)) return
    tableData.value = []
    pagination.total = 0
    console.error('加载数据失败:', error)
    ElMessage.error(t('performance.messages.loadFailed'))
  } finally {
    if (requestGeneration.isCurrent(generation)) loading.value = false
  }
}

const handleSearch = () => {
  pagination.currentPage = 1
  loadData()
}

const handleReset = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key] = key === 'dateRange' ? [] : ''
  })
  handleSearch()
}

const handleRefresh = () => loadData()

const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

const handleOpenPlanLink = (row) => {
  planLinkPerformance.value = row
  planLinkDialogVisible.value = true
}

const handlePlanLinked = () => {
  loadData()
}

const handleEdit = (row) => {
  form.id = row.id
  form.coilNo = row.coilNo
  form.grade = row.grade
  form.density = normalizeNullableNumber(row.density)
  form.weight = normalizeNullableNumber(row.weight)
  form.spec = row.spec || ''
  form.totalLength = normalizeNullableNumber(row.totalLength)
  form.diameter = normalizeNullableNumber(row.diameter)
  form.startTime = normalizeNullableDateTime(isHttpSource.value ? row.effectiveStartTime : row.startTime)
  form.endTime = normalizeNullableDateTime(isHttpSource.value ? row.effectiveEndTime : row.endTime)
  form.remark = row.remark || ''
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        const updateData = {
          grade: form.grade,
          density: normalizeNullableNumber(form.density),
          weight: normalizeNullableNumber(form.weight),
          spec: form.spec,
          totalLength: normalizeNullableNumber(form.totalLength),
          diameter: normalizeNullableNumber(form.diameter),
          startTime: normalizeNullableDateTime(form.startTime),
          endTime: normalizeNullableDateTime(form.endTime),
          remark: form.remark
        }
        
        const submitted = isHttpSource.value
          ? { weight: normalizeNullableNumber(form.weight), ...(form.remark ? { remark: form.remark } : {}) }
          : updateData
        const res = await updatePerformance(form.id, submitted, sourceSelection.value)
        
        if (res) {
          ElMessage.success(t('performance.messages.saveSuccess'))
          dialogVisible.value = false
          loadData()
        } else {
          ElMessage.error(res.message || t('performance.messages.loadFailed'))
        }
      } catch (error) {
        console.error('保存失败:', error)
        ElMessage.error(t('performance.messages.loadFailed'))
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
}

const fetchPrintLabels = async (rows) => {
  const safeRows = Array.isArray(rows) ? rows.filter(Boolean) : []
  if (!safeRows.length) return []

  const labels = await Promise.all(safeRows.map(row => getPrintData(row.id)))
  return labels.filter(Boolean)
}

const printRows = async (rows) => {
  if (!rows.length) {
    ElMessage.warning(t('performance.messages.selectBeforePrint'))
    return
  }

  printing.value = true
  try {
    const labels = await fetchPrintLabels(rows)
    if (!labels.length) {
      ElMessage.warning(t('performance.messages.loadFailed'))
      return
    }

    await createPerformancePrintDocument(labels, normalizePrintTemplate(loadStoredPrintTemplate()), t)
  } catch (error) {
    console.error('打印数据准备失败:', error)
    ElMessage.error(t('performance.messages.loadFailed'))
  } finally {
    printing.value = false
  }
}

const handlePrint = (row) => {
  printRows([row])
}

const handlePrintSelected = () => {
  printRows(selectedRows.value)
}

const handleChart = async (row) => {
  const generation = processGeneration.begin()
  const selection = { ...sourceSelection.value }
  tempTableData.value = []
  tensionTableData.value = []
  speedTableData.value = []
  currentCoilNo.value = row.coilNo
  chartDialogVisible.value = true
  activeChartTab.value = 'temperature'
  
  try {
    const res = await getProcessData(row.id, selection)
    if (!processGeneration.isCurrent(generation)) return
    
    if (res) {
      tempTableData.value = res.temperature || []
      tensionTableData.value = res.tension || []
      speedTableData.value = res.speed || []
    } else {
      ElMessage.error(res.message || t('performance.messages.loadFailed'))
    }
  } catch (error) {
    if (!processGeneration.isCurrent(generation)) return
    console.error('获取过程数据失败:', error)
    ElMessage.error(t('performance.messages.loadFailed'))
  }
  
  await nextTick()
  
  drawTempChart()
  drawTensionChart()
  drawSpeedChart()
}

const drawTempChart = () => {
  if (!tempChartRef.value) return
  if (tempChartInstance) {
    tempChartInstance.dispose()
  }
  tempChartInstance = echarts.init(tempChartRef.value, getEChartsTheme(themeStore.isDark ? 'dark' : 'light'))
  const zones = tempTableData.value.map(item => item.zone)
  const setTemps = tempTableData.value.map(item => normalizeNullableNumber(item.setTemp))
  const avgTemps = tempTableData.value.map(item => normalizeNullableNumber(item.avgTemp))
  const tokens = getChartTokens()
  const axisStyle = getChartAxis(tokens)
  
  const option = {
    title: {
      text: `${t('performance.coilNo')} ${currentCoilNo.value} ${t('performance.temperatureCurve')}`,
      left: 'center',
      textStyle: { fontSize: 14, color: tokens.textPrimary }
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: [t('performance.table.setTemp'), t('performance.table.avgTemp')],
      top: 50,
      textStyle: { color: tokens.textSecondary }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '80px',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: zones,
      ...axisStyle
    },
    yAxis: {
      type: 'value',
      name: `${t('performance.chart.temperatureAxis')}(${t('performance.units.celsius')})`,
      nameTextStyle: { color: tokens.textSecondary },
      ...axisStyle
    },
    series: [
      {
        name: t('performance.table.setTemp'),
        type: 'line',
        data: setTemps,
        smooth: true,
        lineStyle: { width: 2, color: tokens.primary },
        itemStyle: { color: tokens.primary }
      },
      {
        name: t('performance.table.avgTemp'),
        type: 'line',
        data: avgTemps,
        smooth: true,
        lineStyle: { width: 2, color: tokens.success },
        itemStyle: { color: tokens.success }
      }
    ]
  }
  tempChartInstance.setOption(option)
}

const drawTensionChart = () => {
  if (!tensionChartRef.value) return
  if (tensionChartInstance) {
    tensionChartInstance.dispose()
  }
  tensionChartInstance = echarts.init(tensionChartRef.value, getEChartsTheme(themeStore.isDark ? 'dark' : 'light'))
  const zones = tensionTableData.value.map(item => item.zone)
  const setTensions = tensionTableData.value.map(item => normalizeNullableNumber(item.setTension))
  const avgTensions = tensionTableData.value.map(item => normalizeNullableNumber(item.avgTension))
  const tokens = getChartTokens()
  const axisStyle = getChartAxis(tokens)
  
  const option = {
    title: {
      text: `${t('performance.coilNo')} ${currentCoilNo.value} ${t('performance.tensionCurve')}`,
      left: 'center',
      textStyle: { fontSize: 14, color: tokens.textPrimary }
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: [t('performance.table.setTension'), t('performance.table.avgTension')],
      top: 50,
      textStyle: { color: tokens.textSecondary }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '80px',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: zones,
      ...axisStyle
    },
    yAxis: {
      type: 'value',
      name: `${t('performance.chart.tensionAxis')}(${t('performance.units.kN')})`,
      nameTextStyle: { color: tokens.textSecondary },
      ...axisStyle
    },
    series: [
      {
        name: t('performance.table.setTension'),
        type: 'line',
        data: setTensions,
        smooth: true,
        lineStyle: { width: 2, color: tokens.primary },
        itemStyle: { color: tokens.primary }
      },
      {
        name: t('performance.table.avgTension'),
        type: 'line',
        data: avgTensions,
        smooth: true,
        lineStyle: { width: 2, color: tokens.warning },
        itemStyle: { color: tokens.warning }
      }
    ]
  }
  tensionChartInstance.setOption(option)
}

const drawSpeedChart = () => {
  if (!speedChartRef.value) return
  if (speedChartInstance) {
    speedChartInstance.dispose()
  }
  speedChartInstance = echarts.init(speedChartRef.value, getEChartsTheme(themeStore.isDark ? 'dark' : 'light'))
  const zones = speedTableData.value.map(item => item.zone)
  const setSpeeds = speedTableData.value.map(item => normalizeNullableNumber(item.setSpeed))
  const avgSpeeds = speedTableData.value.map(item => normalizeNullableNumber(item.avgSpeed))
  const tokens = getChartTokens()
  const axisStyle = getChartAxis(tokens)
  
  const option = {
    title: {
      text: `${t('performance.coilNo')} ${currentCoilNo.value} ${t('performance.speedCurve')}`,
      left: 'center',
      textStyle: { fontSize: 14, color: tokens.textPrimary }
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: [t('performance.table.setSpeed'), t('performance.table.avgSpeed')],
      top: 50,
      textStyle: { color: tokens.textSecondary }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '80px',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: zones,
      ...axisStyle
    },
    yAxis: {
      type: 'value',
      name: `${t('performance.chart.speedAxis')}(${t('common.unit.speed')})`,
      nameTextStyle: { color: tokens.textSecondary },
      ...axisStyle
    },
    series: [
      {
        name: t('performance.table.setSpeed'),
        type: 'line',
        data: setSpeeds,
        smooth: true,
        lineStyle: { width: 2, color: tokens.primary },
        itemStyle: { color: tokens.primary }
      },
      {
        name: t('performance.table.avgSpeed'),
        type: 'line',
        data: avgSpeeds,
        smooth: true,
        lineStyle: { width: 2, color: tokens.danger },
        itemStyle: { color: tokens.danger }
      }
    ]
  }
  speedChartInstance.setOption(option)
}

const handleSizeChange = (val) => {
  pagination.pageSize = val
  loadData()
}

const handleCurrentChange = (val) => {
  pagination.currentPage = val
  loadData()
}

watch(activeChartTab, async (newVal) => {
  await nextTick()
  if (newVal === 'temperature') {
    drawTempChart()
  } else if (newVal === 'tension') {
    drawTensionChart()
  } else if (newVal === 'speed') {
    drawSpeedChart()
  }
})

const handleResize = () => {
  tempChartInstance?.resize()
  tensionChartInstance?.resize()
  speedChartInstance?.resize()
}

watch(() => [route.query.dataSource, route.query.equipmentId], () => {
  requestGeneration.invalidate()
  processGeneration.invalidate()
  tableData.value = []
  pagination.total = 0
  pagination.currentPage = 1
  selectedRows.value = []
  tempTableData.value = []
  tensionTableData.value = []
  speedTableData.value = []
  chartDialogVisible.value = false
  dialogVisible.value = false
  searchForm.observationStatus = ''
  loadData()
})

onMounted(() => {
  loadData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  tempChartInstance?.dispose()
  tensionChartInstance?.dispose()
  speedChartInstance?.dispose()
})
</script>

<style scoped>
.performance-list-page {
  animation: fadeIn var(--transition-normal);
}

.list-card :deep(.base-card__body) {
  padding: 0;
}

.list-card :deep(.base-card__header) {
  min-height: 76px;
}

.filter-section {
  padding: 24px;
  border-bottom: 1px solid var(--border-secondary);
}

.filter-form {
  display: grid;
  grid-template-columns: minmax(180px, 1fr) minmax(180px, 1fr) minmax(320px, 1.2fr) auto;
  gap: 16px;
  align-items: end;
}

.filter-actions {
  align-self: end;
}

.filter-actions :deep(.el-form-item__content) {
  display: flex;
  gap: 10px;
  flex-wrap: nowrap;
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

.filter-form :deep(.el-date-editor.el-input__wrapper) {
  width: 100%;
}

.table-scroll {
  width: 100%;
  padding: 24px 24px 0;
  overflow: hidden;
}

.performance-table {
  width: 100%;
}

.performance-table :deep(.el-table__fixed-right),
.performance-table :deep(.el-table__fixed-right-patch),
.performance-table :deep(.el-table-fixed-column--right) {
  background: var(--table-fixed-bg) !important;
}

.filter-actions :deep(.el-button + .el-button) {
  margin-left: 0;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  padding: 18px 24px 24px;
}

.chart-section {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 8px 0 0;
}

.process-chart {
  width: 100%;
  height: 350px;
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-lg);
  background: var(--bg-secondary);
}

.process-table {
  width: 100%;
}

:global(.process-dialog.el-dialog) {
  overflow: hidden;
  background: var(--table-fixed-bg);
  border: 1px solid var(--card-border);
  border-radius: var(--card-radius);
}

:global(.process-dialog .el-dialog__header) {
  min-height: 72px;
  margin: 0;
  padding: 0 32px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid var(--border-secondary);
  background: var(--table-fixed-bg);
}

:global(.process-dialog .el-dialog__title) {
  color: var(--text-primary);
  font-size: 20px;
  font-weight: 650;
}

:global(.process-dialog .el-dialog__headerbtn) {
  top: 18px;
  right: 24px;
}

.unit-text {
  color: var(--text-tertiary);
  font-size: 12px;
}

:global(.process-dialog .el-dialog__body) {
  max-height: calc(94vh - 104px);
  overflow-y: auto;
  padding: 24px 32px 32px;
  background: var(--table-fixed-bg);
}

.process-tabs :deep(.el-tabs__header) {
  margin-bottom: 18px;
}

.process-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background: var(--border-secondary);
}

.process-tabs :deep(.el-tabs__item) {
  color: var(--text-secondary);
  font-weight: 590;
}

.process-tabs :deep(.el-tabs__item.is-active) {
  color: var(--primary);
}

:global(.performance-dialog-mask) {
  background-color: var(--el-mask-color);
}

@media (max-width: 1280px) {
  .filter-form {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .filter-form {
    grid-template-columns: 1fr;
  }

  .filter-actions :deep(.el-form-item__content) {
    justify-content: flex-start;
  }

  :global(.process-dialog.el-dialog) {
    width: calc(100vw - 24px) !important;
  }
}
</style>
