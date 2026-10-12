<!--
  文件路径: /frontend-next-js/src/app/quality/views/list/index.vue
  功能描述: 质量列表页面，展示质量检验数据
  主要功能:
    - 展示质量检验列表
    - 支持分页、筛选与 CSV 导出
    - 提供新增、查看详情、编辑入口
    - 国际化 (i18n) 支持
    - 日夜模式 (Theme) 适配
-->
<template>
  <div class="quality-list-page page-layout">
    <BaseCard class="list-card" :title="$t('quality.listPage.title')">
      <template #actions>
        <div class="table-actions">
          <ActionButton variant="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            {{ $t('quality.listPage.newInspection') }}
          </ActionButton>
          <ActionButton @click="handleExport">
            <el-icon><Download /></el-icon>
            {{ $t('quality.listPage.exportReport') }}
          </ActionButton>
        </div>
      </template>

      <div class="filter-section">
        <el-form :model="searchForm" class="filter-form" label-position="top">
          <el-form-item :label="$t('quality.listPage.fields.coilNo')">
            <el-input
              v-model="searchForm.coilNo"
              :placeholder="$t('quality.listPage.placeholder.coilNo')"
              clearable
            />
          </el-form-item>
          <el-form-item :label="$t('quality.listPage.fields.grade')">
            <el-input
              v-model="searchForm.grade"
              :placeholder="$t('quality.listPage.placeholder.grade')"
              clearable
            />
          </el-form-item>
          <el-form-item :label="$t('quality.listPage.fields.qualityGrade')">
            <el-select v-model="searchForm.qualityGrade" :placeholder="$t('quality.listPage.placeholder.select')" clearable>
              <el-option :label="$t('quality.listPage.grade.excellent')" value="excellent" />
              <el-option :label="$t('quality.listPage.grade.firstClass')" value="firstClass" />
              <el-option :label="$t('quality.listPage.grade.qualified')" value="qualified" />
              <el-option :label="$t('quality.listPage.grade.unqualified')" value="unqualified" />
              <el-option :label="$t('quality.listPage.grade.pending')" value="pending" />
            </el-select>
          </el-form-item>
          <el-form-item :label="$t('quality.listPage.fields.inspectDate')">
            <el-date-picker
              v-model="searchForm.dateRange"
              type="daterange"
              :range-separator="$t('quality.listPage.placeholder.rangeSeparator')"
              :start-placeholder="$t('quality.listPage.placeholder.startDate')"
              :end-placeholder="$t('quality.listPage.placeholder.endDate')"
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
          border
          stripe
          class="vibe-table quality-table"
          :row-style="{ cursor: 'pointer' }"
          @row-click="handleDetail"
        >
          <el-table-column prop="coilNo" :label="$t('quality.listPage.fields.coilNo')" width="150" fixed />
          <el-table-column prop="grade" :label="$t('quality.listPage.fields.grade')" width="110" />
          <el-table-column prop="spec" :label="$t('quality.listPage.fields.spec')" min-width="150" />
          <el-table-column prop="weight" :label="$t('quality.listPage.fields.weight')" width="120" align="right">
            <template #default="{ row }">
              {{ formatWeight(row.weight) }}
            </template>
          </el-table-column>
          <el-table-column prop="qualityGrade" :label="$t('quality.listPage.fields.qualityGrade')" width="120" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.qualityGrade" :type="getGradeTagType(row.qualityGrade)">
                {{ formatQualityGrade(row.qualityGrade) }}
              </el-tag>
              <span v-else class="empty-value">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="judgment" :label="$t('quality.listPage.fields.judgment')" width="120" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.judgment" :type="getJudgmentTagType(row.judgment)">
                {{ formatJudgment(row.judgment) }}
              </el-tag>
              <span v-else class="empty-value">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="inspector" :label="$t('quality.listPage.fields.inspector')" width="110" />
          <el-table-column prop="inspectTime" :label="$t('quality.listPage.fields.inspectTime')" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.inspectTime) }}
            </template>
          </el-table-column>
          <el-table-column :label="$t('common.actions')" width="170" fixed="right" align="center">
            <template #default="{ row }">
              <div class="row-actions" @click.stop>
                <ActionButton variant="row" size="small" @click="handleDetail(row)">
                  {{ $t('common.detail') }}
                </ActionButton>
                <ActionButton variant="success" size="small" @click="handleEdit(row)">
                  {{ $t('common.edit') }}
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
        class="pagination"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </BaseCard>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import { getQualityList } from '@/app/quality/api'
import { exportRowsAsCsv } from '@/utils/exportCsv'

const router = useRouter()
const { t, te, locale } = useI18n()

const searchForm = reactive({
  coilNo: '',
  grade: '',
  qualityGrade: '',
  dateRange: []
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

const tableData = ref([])
const loading = ref(false)

const getLocaleKey = (group, value) => {
  if (!value) return ''
  const key = `quality.listPage.${group}.${value}`
  return te(key) ? key : ''
}

const formatLocaleValue = (group, value) => {
  const key = getLocaleKey(group, value)
  return key ? t(key) : (value || '-')
}

const formatQualityGrade = (grade) => formatLocaleValue('grade', grade)
const formatJudgment = (judgment) => formatLocaleValue('judgment', judgment)

const formatWeight = (weight) => {
  if (weight === null || weight === undefined || weight === '') return '-'
  return Number(weight).toFixed(3)
}

const getGradeTagType = (grade) => {
  const typeMap = {
    excellent: 'success',
    firstClass: 'primary',
    first: 'primary',
    qualified: 'warning',
    unqualified: 'danger',
    pending: 'info',
    recheck: 'info'
  }
  return typeMap[grade] || 'info'
}

const getJudgmentTagType = (judgment) => {
  const typeMap = {
    qualified: 'success',
    unqualified: 'danger',
    concession: 'warning',
    recheck: 'info'
  }
  return typeMap[judgment] || 'info'
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return Number.isNaN(date.getTime()) ? '-' : date.toLocaleString(locale.value)
}

const buildQueryParams = (extra = {}) => ({
  ...extra,
  coilNo: searchForm.coilNo || undefined,
  grade: searchForm.grade || undefined,
  qualityGrade: searchForm.qualityGrade || undefined,
  startDate: searchForm.dateRange?.[0] || undefined,
  endDate: searchForm.dateRange?.[1] || undefined
})

const loadData = async () => {
  loading.value = true
  try {
    const params = buildQueryParams({
      page: pagination.currentPage,
      pageSize: pagination.pageSize
    })
    const res = await getQualityList(params)
    tableData.value = res.items || []
    pagination.total = res.total || 0
  } catch (error) {
    console.error('加载质量列表失败:', error)
    ElMessage.error(t('common.loadFailed'))
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.currentPage = 1
  loadData()
}

const handleReset = () => {
  searchForm.coilNo = ''
  searchForm.grade = ''
  searchForm.qualityGrade = ''
  searchForm.dateRange = []
  handleSearch()
}

const handleAdd = () => {
  router.push('/quality/control/new')
}

const handleDetail = (row) => {
  router.push(`/quality/control/${row.id}`)
}

const handleEdit = (row) => {
  router.push(`/quality/control/${row.id}`)
}

const handleExport = async () => {
  try {
    const response = await getQualityList(buildQueryParams({
      page: 1,
      pageSize: 1000
    }))
    const exported = exportRowsAsCsv({
      filename: `quality-list-${Date.now()}.csv`,
      headers: [
        { key: 'coilNo', label: t('quality.listPage.fields.coilNo') },
        { key: 'grade', label: t('quality.listPage.fields.grade') },
        { key: 'spec', label: t('quality.listPage.fields.spec') },
        { label: t('quality.listPage.fields.weight'), value: row => formatWeight(row.weight) },
        { label: t('quality.listPage.fields.qualityGrade'), value: row => formatQualityGrade(row.qualityGrade) },
        { label: t('quality.listPage.fields.judgment'), value: row => formatJudgment(row.judgment) },
        { key: 'inspector', label: t('quality.listPage.fields.inspector') },
        { label: t('quality.listPage.fields.inspectTime'), value: row => formatDateTime(row.inspectTime) }
      ],
      rows: response?.items || []
    })

    if (!exported) {
      ElMessage.warning(t('common.noData'))
      return
    }

    ElMessage.success(t('quality.listPage.exportSuccess'))
  } catch (error) {
    console.error('导出质量报表失败:', error)
    ElMessage.error(t('common.loadFailed'))
  }
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

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.quality-list-page {
  animation: fadeIn var(--transition-normal);
}

.list-card :deep(.base-card__body) {
  padding: 0;
}

.filter-section {
  padding: 24px 24px 20px;
  border-bottom: 1px solid var(--border-secondary);
}

.filter-form {
  display: grid;
  grid-template-columns: minmax(180px, 1fr) minmax(150px, 0.8fr) minmax(180px, 0.8fr) minmax(280px, 1.2fr) auto;
  gap: 16px;
  align-items: end;
}

.filter-form :deep(.el-date-editor),
.filter-form :deep(.el-select) {
  width: 100%;
}

.filter-actions {
  align-self: end;
}

.filter-actions :deep(.el-form-item__content) {
  display: flex;
  flex-wrap: nowrap;
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

.table-scroll {
  width: 100%;
  padding: 24px 24px 0;
  overflow: hidden;
}

.quality-table {
  width: 100%;
}

.quality-table :deep(.el-tag) {
  min-width: 56px;
  justify-content: center;
  font-weight: 590;
}

.quality-table :deep(.el-table-fixed-column--left),
.quality-table :deep(.el-table-fixed-column--right) {
  background: var(--table-fixed-bg) !important;
}

.empty-value {
  color: var(--text-muted);
}

.pagination {
  display: flex;
  justify-content: flex-end;
  padding: 18px 24px 24px;
}

@media (max-width: 1280px) {
  .filter-form {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .filter-actions :deep(.el-form-item__content) {
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {
  .filter-form {
    grid-template-columns: 1fr;
  }

}
</style>
