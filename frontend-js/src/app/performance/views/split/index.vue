<!--
  文件路径: /frontend-next-js/src/app/performance/views/split/index.vue
  功能描述: 实绩分卷管理表单卡片页面
  主要功能:
    - 在单张分卷管理主卡片内展示筛选区和管理表
    - 通过标准弹窗承接 B17 split / merge transform 操作
    - 使用 lineage summary 展示有效卷重、可用卷重和记录来源
-->
<template>
  <div class="performance-split-page">
    <BaseCard class="split-management-card" :title="$t('performance.splitManagement.title')">
      <template #actions>
        <div class="table-actions">
          <ActionButton variant="primary" @click="openActionDialog">
            {{ $t('performance.splitManagement.actions.add') }}
          </ActionButton>
          <ActionButton variant="refresh" :loading="loading" @click="loadRows">
            {{ $t('common.refresh') }}
          </ActionButton>
        </div>
      </template>

      <section class="split-management-section split-management-section--filters">
        <el-form class="split-management-form" :model="filters" label-position="top">
          <el-form-item :label="$t('performance.splitManagement.filters.keyword')">
            <el-input
              v-model="filters.keyword"
              clearable
              :placeholder="$t('performance.splitManagement.filters.keywordPlaceholder')"
              @keyup.enter="applyFilters"
            />
          </el-form-item>
          <el-form-item :label="$t('performance.common.status')">
            <el-select
              v-model="filters.status"
              clearable
              :placeholder="$t('performance.splitManagement.filters.statusPlaceholder')"
            >
              <el-option
                v-for="item in statusOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item :label="$t('performance.common.dateRange')">
            <el-date-picker
              v-model="filters.dateRange"
              class="split-management-date"
              type="daterange"
              unlink-panels
              value-format="YYYY-MM-DD"
              :start-placeholder="$t('performance.common.startDate')"
              :end-placeholder="$t('performance.common.endDate')"
            />
          </el-form-item>
          <el-form-item class="split-management-actions-item">
            <div class="table-actions split-management-actions">
              <ActionButton variant="primary" @click="applyFilters">
                {{ $t('common.search') }}
              </ActionButton>
              <ActionButton variant="secondary" @click="resetFilters">
                {{ $t('common.reset') }}
              </ActionButton>
            </div>
          </el-form-item>
        </el-form>
      </section>

      <section class="split-management-section split-management-section--table">
        <el-alert
          v-if="tableErrorCode"
          class="split-management-table__alert"
          :title="formatError(tableErrorCode)"
          type="warning"
          :closable="false"
        />

        <div class="table-scroll">
          <el-table
            v-loading="loading"
            :data="pagedRows"
            border
            :empty-text="$t('performance.splitManagement.table.empty')"
          >
            <el-table-column prop="coilNo" :label="$t('performance.coilNo')" min-width="150" />
            <el-table-column prop="parentCoilNo" :label="$t('performance.parentCoilNo')" min-width="150" />
            <el-table-column prop="grade" :label="$t('performance.grade')" min-width="110" />
            <el-table-column prop="spec" :label="$t('performance.spec')" min-width="130" />
            <el-table-column :label="$t('performance.weight')" min-width="110">
              <template #default="{ row }">
                {{ formatWeight(row.weight) }}
              </template>
            </el-table-column>
            <el-table-column :label="$t('performance.splitWorkbench.source.effectiveWeight')" min-width="140">
              <template #default="{ row }">
                {{ formatWeight(getSummary(row.id).effectiveWeight) }}
              </template>
            </el-table-column>
            <el-table-column :label="$t('performance.splitWorkbench.source.availableWeight')" min-width="140">
              <template #default="{ row }">
                {{ formatWeight(getSummary(row.id).availableWeight) }}
              </template>
            </el-table-column>
            <el-table-column :label="$t('performance.splitWorkbench.source.recordSource')" min-width="150">
              <template #default="{ row }">
                {{ formatDict('recordSources', row.recordSource) }}
              </template>
            </el-table-column>
            <el-table-column :label="$t('performance.splitManagement.table.lineageStatus')" min-width="170">
              <template #default="{ row }">
                <el-tag :type="statusTagType(resolveRowStatus(row))">
                  {{ formatRowStatus(resolveRowStatus(row)) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="$t('performance.splitManagement.table.lineageSummary')" min-width="220">
              <template #default="{ row }">
                {{ formatLineageSummary(row) }}
              </template>
            </el-table-column>
          </el-table>
        </div>

        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          class="pagination"
          layout="total, sizes, prev, pager, next, jumper"
          :page-sizes="[10, 20, 50, 100]"
          :total="filteredRows.length"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </section>
    </BaseCard>

    <SplitMergeActionDialog
      v-model="dialogVisible"
      :candidates="rows"
      :summaries="summaries"
      :loading-sources="loading"
      @refresh-sources="loadRows"
      @submitted="handleTransformSubmitted"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import BaseCard from '@/components/common/BaseCard.vue'
import ActionButton from '@/components/common/ActionButton.vue'
import SplitMergeActionDialog from '@/app/performance/components/SplitMergeActionDialog.vue'
import {
  getPerformanceLineageSummary,
  getPerformanceList
} from '@/app/performance/api'

const { t, te } = useI18n()

const rows = ref([])
const summaries = reactive({})
const loading = ref(false)
const tableErrorCode = ref('')
const dialogVisible = ref(false)
const filters = reactive({
  keyword: '',
  status: '',
  dateRange: []
})
const pagination = reactive({
  page: 1,
  pageSize: 20
})

const extractRows = (response) => {
  if (Array.isArray(response)) return response
  if (Array.isArray(response?.list)) return response.list
  if (Array.isArray(response?.data)) return response.data
  if (Array.isArray(response?.records)) return response.records
  if (Array.isArray(response?.rows)) return response.rows
  if (Array.isArray(response?.items)) return response.items
  return []
}

const statusOptions = computed(() => [
  { value: 'actionable', label: t('performance.splitManagement.status.actionable') },
  { value: 'split_generated', label: t('performance.splitWorkbench.recordSources.split_generated') },
  { value: 'merge_generated', label: t('performance.splitWorkbench.recordSources.merge_generated') },
  { value: 'backend_unavailable', label: t('performance.splitManagement.status.backend_unavailable') }
])

const filteredRows = computed(() => rows.value.filter((row) => {
  const keyword = filters.keyword.trim().toLowerCase()
  const keywordMatched = !keyword || [
    row.coilNo,
    row.parentCoilNo,
    row.splitNo,
    row.performanceCoilNo
  ].some((value) => String(value || '').toLowerCase().includes(keyword))

  const statusMatched = !filters.status || resolveRowStatus(row) === filters.status
  const dateMatched = matchDateRange(row)

  return keywordMatched && statusMatched && dateMatched
}))

const pagedRows = computed(() => {
  const start = (pagination.page - 1) * pagination.pageSize
  return filteredRows.value.slice(start, start + pagination.pageSize)
})

const resetPagination = () => {
  pagination.page = 1
}

const applyFilters = () => {
  resetPagination()
}

const resetFilters = () => {
  filters.keyword = ''
  filters.status = ''
  filters.dateRange = []
  resetPagination()
}

const handleSizeChange = (pageSize) => {
  pagination.pageSize = pageSize
  resetPagination()
}

const handleCurrentChange = (page) => {
  pagination.page = page
}

const openActionDialog = () => {
  dialogVisible.value = true
}

const handleTransformSubmitted = async () => {
  await loadRows()
}

const loadRows = async () => {
  loading.value = true
  tableErrorCode.value = ''

  try {
    const response = await getPerformanceList({ page: 1, pageSize: 100 })
    rows.value = extractRows(response)
    await loadLineageSummaries(rows.value)
  } catch (error) {
    rows.value = []
    tableErrorCode.value = error?.errorCode || 'source_load_failed'
    ElMessage.error(formatError(tableErrorCode.value))
  } finally {
    loading.value = false
    resetPagination()
  }
}

const loadLineageSummaries = async (records) => {
  Object.keys(summaries).forEach((key) => {
    delete summaries[key]
  })

  const ids = records
    .map((item) => item.id)
    .filter((id) => id !== null && id !== undefined)

  await Promise.all(ids.map(async (id) => {
    try {
      summaries[id] = await getPerformanceLineageSummary(id)
    } catch (error) {
      const fallback = records.find((item) => item.id === id) || {}
      summaries[id] = {
        performanceId: id,
        effectiveWeight: fallback.effectiveWeight ?? fallback.weight ?? null,
        effectiveWeightSource: fallback.effectiveWeightSource || '',
        committedSourceAllocatedWeight: fallback.committedSourceAllocatedWeight ?? null,
        availableWeight: fallback.availableWeight ?? null,
        errorCode: error?.errorCode || 'lineage_summary_unavailable'
      }
    }
  }))
}

const getSummary = (id) => summaries?.[id] || {}

const matchDateRange = (row) => {
  if (!Array.isArray(filters.dateRange) || filters.dateRange.length !== 2) return true
  const [start, end] = filters.dateRange
  const rowDate = String(row.createdAt || row.startTime || row.endTime || '').slice(0, 10)
  if (!rowDate) return false
  return rowDate >= start && rowDate <= end
}

const resolveRowStatus = (row) => {
  const summary = getSummary(row.id)
  if (summary.errorCode) return 'backend_unavailable'
  if (row.recordSource === 'split_generated') return 'split_generated'
  if (row.recordSource === 'merge_generated') return 'merge_generated'
  return 'actionable'
}

const statusTagType = (status) => {
  if (status === 'split_generated') return 'success'
  if (status === 'merge_generated') return 'warning'
  if (status === 'backend_unavailable') return 'info'
  return 'primary'
}

const formatRowStatus = (status) => {
  const key = `performance.splitManagement.status.${status}`
  return te(key) ? t(key) : status
}

const formatWeight = (value) => {
  if (value === null || value === undefined || value === '') return t('performance.splitWorkbench.empty')
  const numericValue = Number(value)
  return Number.isFinite(numericValue) ? numericValue.toFixed(3) : String(value)
}

const formatDict = (dictName, value) => {
  if (!value) return t('performance.splitWorkbench.empty')
  const key = `performance.splitWorkbench.${dictName}.${value}`
  return te(key) ? t(key) : value
}

const formatLineageSummary = (row) => {
  const summary = getSummary(row.id)
  if (summary.errorCode) return formatError(summary.errorCode)
  if (summary.availableWeight !== null && summary.availableWeight !== undefined) {
    return t('performance.splitManagement.table.availableSummary', {
      value: formatWeight(summary.availableWeight)
    })
  }
  return t('performance.splitManagement.status.unavailable')
}

const formatError = (errorCode) => {
  const key = `performance.splitWorkbench.errors.${errorCode}`
  return te(key) ? t(key) : errorCode
}

onMounted(() => {
  loadRows()
})
</script>

<style scoped>
.performance-split-page {
  min-height: 100%;
  animation: fadeIn var(--transition-normal);
}

.split-management-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.split-management-section + .split-management-section {
  margin-top: 22px;
  padding-top: 22px;
  border-top: 1px solid var(--border-secondary);
}

.split-management-form {
  width: 100%;
  display: grid;
  grid-template-columns: minmax(260px, 1.25fr) minmax(150px, 0.7fr) minmax(320px, 1.35fr) auto;
  gap: 16px;
  align-items: end;
}

.split-management-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.split-management-date {
  width: 100%;
}

.split-management-actions-item {
  justify-self: end;
}

.split-management-actions-item :deep(.el-form-item__content) {
  justify-content: flex-end;
}

.split-management-actions {
  flex-wrap: nowrap;
  justify-content: flex-end;
}

.split-management-table__alert {
  margin-bottom: 0;
}

.table-scroll {
  width: 100%;
  overflow-x: auto;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

@media (max-width: 768px) {
  .split-management-form {
    grid-template-columns: 1fr;
  }

  .split-management-actions-item {
    justify-self: start;
  }

  .split-management-actions,
  .pagination {
    justify-content: flex-start;
  }
}
</style>
