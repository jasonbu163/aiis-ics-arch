<!--
  文件路径: /frontend-next-js/src/app/plan/views/list/index.vue
  功能描述: 生产计划列表管理页面，支持国际化
  主要功能:
    - 计划列表展示与分页
    - 按料卷号、牌号、状态筛选查询
    - 新增/编辑/删除计划
-->
<template>
  <div class="plan-list-page page-layout">
    <BaseCard class="list-card" :title="$t('plan.list')">
      <template #actions>
        <div class="table-actions">
          <ActionButton variant="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            {{ $t('plan.add') }}
          </ActionButton>
          <ActionButton variant="secondary" :loading="templateLoading" @click="handleDownloadTemplate">
            <el-icon><Download /></el-icon>
            {{ $t('plan.xlsx.downloadTemplate') }}
          </ActionButton>
          <ActionButton variant="warning" @click="openImportDialog">
            <el-icon><Upload /></el-icon>
            {{ $t('plan.xlsx.import') }}
          </ActionButton>
          <ActionButton variant="success" :loading="exportLoading" @click="handleExportXlsx">
            <el-icon><Download /></el-icon>
            {{ $t('plan.xlsx.export') }}
          </ActionButton>
          <el-tooltip :content="$t('plan.xlsx.refreshTooltip')" placement="top">
            <ActionButton
              variant="refresh"
              circle
              :aria-label="$t('plan.xlsx.refreshTooltip')"
              :loading="loading"
              @click="handleRefresh"
            >
              <el-icon><Refresh /></el-icon>
            </ActionButton>
          </el-tooltip>
        </div>
      </template>

      <div class="filter-section">
        <el-form :model="searchForm" class="filter-form" label-position="top">
          <el-form-item :label="$t('plan.coilNo')">
            <el-input
              v-model="searchForm.coilNo"
              :placeholder="$t('plan.coilNo')"
              clearable
            />
          </el-form-item>
          <el-form-item :label="$t('plan.steelGrade')">
            <el-input
              v-model="searchForm.grade"
              :placeholder="$t('plan.steelGrade')"
              clearable
            />
          </el-form-item>
          <el-form-item :label="$t('plan.materialStatus')">
            <el-select v-model="searchForm.materialStatus" :placeholder="$t('plan.rules.materialStatusRequired')" clearable>
              <el-option
                v-for="(label, key) in $tm('plan.materialStatusMap')"
                :key="key"
                :label="label"
                :value="key"
              />
            </el-select>
          </el-form-item>
          <el-form-item :label="$t('plan.status')">
            <el-select
              v-model="searchForm.status"
              :placeholder="$t('plan.rules.taskStatusRequired')"
              clearable
            >
              <el-option
                v-for="(label, key) in $tm('plan.statusMap')"
                :key="key"
                :label="label"
                :value="key"
              />
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
      </div>

      <div class="table-scroll">
        <el-table
          :data="tableData"
          v-loading="loading"
          @selection-change="handleSelectionChange"
          @row-click="handleRowClick"
          stripe
          border
          class="vibe-table plan-table"
          :row-style="{ cursor: 'pointer' }"
        >
          <el-table-column type="selection" width="52" />
          <el-table-column prop="coilNo" :label="$t('plan.coilNo')" width="150" />
          <el-table-column prop="grade" :label="$t('plan.steelGrade')" width="120" />
          <el-table-column prop="materialStatus" :label="$t('plan.materialStatus')" width="110">
            <template #default="{ row }">
              <el-tag :type="materialStatusMap[row.materialStatus]?.type || 'info'">
                {{ $t(`plan.materialStatusMap.${row.materialStatus}`) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="spec" :label="$t('plan.spec')" min-width="150" />
          <el-table-column prop="weight" :label="$t('plan.weight') + ' (' + $t('common.unit.ton') + ')'" width="110" align="right">
            <template #default="{ row }">
              {{ parseFloat(row.weight).toFixed(4) }}
            </template>
          </el-table-column>
          <el-table-column prop="thickness" :label="$t('plan.thickness') + ' (' + $t('common.unit.mm') + ')'" width="120" align="right">
            <template #default="{ row }">
              {{ parseFloat(row.thickness).toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="width" :label="$t('plan.width') + ' (' + $t('common.unit.mm') + ')'" width="110" align="right">
            <template #default="{ row }">
              {{ row.width }}
            </template>
          </el-table-column>
          <el-table-column prop="status" :label="$t('plan.status')" width="110">
            <template #default="{ row }">
              <PlanStatusTag :status="row.status" />
            </template>
          </el-table-column>
          <el-table-column prop="priority" :label="$t('plan.priority')" width="90">
            <template #default="{ row }">
              <PlanPriorityTag :priority="row.priority" size="small" />
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" :label="$t('plan.createTime')" width="180">
            <template #default="{ row }">
              {{ formatDate(row.createdAt) }}
            </template>
          </el-table-column>
          <el-table-column :label="$t('common.actions')" width="180" fixed="right" align="center">
            <template #default="{ row }">
              <div class="row-actions" @click.stop>
                <ActionButton
                  v-if="canEditOrDelete(row.status)"
                  size="small"
                  variant="row"
                  @click="handleEdit(row)"
                >
                  {{ $t('common.edit') }}
                </ActionButton>
                <ActionButton
                  v-if="canEditOrDelete(row.status)"
                  size="small"
                  variant="danger"
                  @click="handleConfirmDelete(row)"
                >
                  {{ $t('common.delete') }}
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

    <PlanFormDialog ref="formDialogRef" @success="loadData" />

    <el-dialog
      v-model="importDialogVisible"
      :title="$t('plan.xlsx.importDialogTitle')"
      width="820px"
      class="standard-form-dialog plan-xlsx-dialog"
      modal-class="plan-dialog-mask"
      destroy-on-close
      @closed="resetImportDialog"
    >
      <section class="dialog-section">
        <h3 class="dialog-section__title">{{ $t('plan.xlsx.selectFile') }}</h3>
        <el-upload
          ref="importUploadRef"
          drag
          action="#"
          accept=".xlsx"
          :auto-upload="false"
          :limit="1"
          :on-change="handleImportFileChange"
          :on-remove="handleImportFileRemove"
          :on-exceed="handleImportFileExceed"
        >
          <el-icon class="plan-xlsx-upload-icon"><Upload /></el-icon>
          <div class="el-upload__text">{{ $t('plan.xlsx.uploadText') }}</div>
          <template #tip>
            <div class="el-upload__tip">{{ $t('plan.xlsx.uploadTip') }}</div>
          </template>
        </el-upload>
      </section>

      <section v-if="importResult" class="dialog-section">
        <h3 class="dialog-section__title">{{ $t('plan.xlsx.previewResult') }}</h3>
        <el-alert
          :type="importResult.valid ? 'success' : 'error'"
          :title="importResult.valid ? $t('plan.xlsx.previewValid') : $t('plan.xlsx.previewInvalid', { count: importResult.errorCount || importResult.errors?.length || 0 })"
          show-icon
          :closable="false"
        />
        <el-descriptions class="plan-xlsx-summary" :column="3" border>
          <el-descriptions-item :label="$t('plan.xlsx.dryRun')">
            {{ importResult.dryRun ? $t('common.yes') : $t('common.no') }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('plan.xlsx.createdCount')">
            {{ importResult.createdCount ?? 0 }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('plan.xlsx.errorCount')">
            {{ importResult.errorCount ?? importResult.errors?.length ?? 0 }}
          </el-descriptions-item>
        </el-descriptions>
        <el-table
          v-if="importResult.errors?.length"
          :data="importResult.errors"
          border
          stripe
          class="vibe-table plan-xlsx-error-table"
        >
          <el-table-column prop="row" :label="$t('plan.xlsx.errorRow')" width="90">
            <template #default="{ row }">{{ row.row ?? '-' }}</template>
          </el-table-column>
          <el-table-column prop="field" :label="$t('plan.xlsx.errorField')" width="150">
            <template #default="{ row }">{{ row.field || '-' }}</template>
          </el-table-column>
          <el-table-column prop="errorCode" :label="$t('plan.xlsx.errorCode')" width="240" />
          <el-table-column :label="$t('plan.xlsx.errorMessage')" min-width="220">
            <template #default="{ row }">{{ formatImportError(row) }}</template>
          </el-table-column>
        </el-table>
      </section>

      <template #footer>
        <div class="vibe-dialog-footer">
          <ActionButton @click="importDialogVisible = false">
            <el-icon><Close /></el-icon>
            {{ $t('common.close') }}
          </ActionButton>
          <ActionButton
            variant="primary"
            :disabled="!selectedImportFile || importPreviewLoading || !importResult?.valid"
            :loading="importPreviewLoading || importCommitLoading"
            @click="handleCommitImport"
          >
            <el-icon><Check /></el-icon>
            {{ $t('plan.xlsx.confirmImport') }}
          </ActionButton>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  deletePlan,
  downloadPlanXlsxTemplate,
  exportPlanXlsx,
  getPlanList,
  importPlanXlsx
} from '@/app/plan/api'
import PlanStatusTag from '@/app/plan/components/PlanStatusTag.vue'
import PlanPriorityTag from '@/app/plan/components/PlanPriorityTag.vue'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import PlanFormDialog from '@/app/plan/components/PlanFormDialog.vue'

const { t } = useI18n()

const getErrorMessage = (error, fallback) => {
  return error?.response?.data?.detail || error?.message || fallback
}

const downloadBlob = (content, filename) => {
  const blob = content instanceof Blob ? content : new Blob([content])
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

const searchForm = reactive({
  coilNo: '',
  grade: '',
  materialStatus: '',
  status: ''
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

const tableData = ref([])
const loading = ref(false)
const selectedRows = ref([])
const templateLoading = ref(false)
const exportLoading = ref(false)
const importDialogVisible = ref(false)
const importUploadRef = ref()
const selectedImportFile = ref(null)
const importResult = ref(null)
const importPreviewLoading = ref(false)
const importCommitLoading = ref(false)

const materialStatusMap = {
  degreasing: { type: 'primary' },
  annealing: { type: 'success' },
  tension: { type: 'warning' },
  special: { type: 'danger' }
}

const canEditOrDelete = (status) => {
  return status === 'planned'
}

const formDialogRef = ref()

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.currentPage,
      pageSize: pagination.pageSize,
      coilNo: searchForm.coilNo || undefined,
      grade: searchForm.grade || undefined,
      materialStatus: searchForm.materialStatus || undefined,
      status: searchForm.status || undefined
    }

    const res = await getPlanList(params)

    if (res?.items) {
      tableData.value = res.items
      pagination.total = res.total || 0
    }
    return true
  } catch (error) {
    ElMessage.error(getErrorMessage(error, t('plan.messages.loadError')))
    return false
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
  searchForm.materialStatus = ''
  searchForm.status = ''
  handleSearch()
}

const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

const handleRowClick = (row) => {
  if (row.status === 'planned') {
    formDialogRef.value?.open('edit', row)
  } else {
    formDialogRef.value?.open('view', row)
  }
}

const handleAdd = () => {
  formDialogRef.value?.open('add')
}

const handleEdit = (row) => {
  formDialogRef.value?.open('edit', row)
}

const handleConfirmDelete = (row) => {
  ElMessageBox.confirm(t('plan.messages.deleteConfirm'), t('common.confirm'))
    .then(() => handleDelete(row))
    .catch(() => {})
}

const handleDelete = async (row) => {
  try {
    await deletePlan(row.id)
    ElMessage.success(t('plan.messages.deleteSuccess'))
    loadData()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, t('plan.messages.deleteError')))
  }
}

const handleDownloadTemplate = async () => {
  templateLoading.value = true
  try {
    const content = await downloadPlanXlsxTemplate()
    downloadBlob(content, 'plan-import-template.xlsx')
    ElMessage.success(t('plan.xlsx.templateDownloaded'))
  } catch (error) {
    ElMessage.error(getErrorMessage(error, t('plan.xlsx.templateDownloadFailed')))
  } finally {
    templateLoading.value = false
  }
}

const getExportParams = () => {
  if (selectedRows.value.length) {
    return {
      planIds: selectedRows.value.map((row) => row.id).filter(Boolean)
    }
  }

  return {
    coilNo: searchForm.coilNo || undefined,
    grade: searchForm.grade || undefined,
    materialStatus: searchForm.materialStatus || undefined,
    status: searchForm.status || undefined
  }
}

const handleExportXlsx = async () => {
  exportLoading.value = true
  try {
    const content = await exportPlanXlsx(getExportParams())
    downloadBlob(content, 'plans-export.xlsx')
    ElMessage.success(t('plan.xlsx.exportSuccess'))
  } catch (error) {
    ElMessage.error(getErrorMessage(error, t('plan.xlsx.exportFailed')))
  } finally {
    exportLoading.value = false
  }
}

const handleRefresh = async () => {
  const refreshed = await loadData()
  if (refreshed) {
    ElMessage.success(t('common.refreshSuccess'))
  }
}

const resetImportDialog = () => {
  selectedImportFile.value = null
  importResult.value = null
  importPreviewLoading.value = false
  importCommitLoading.value = false
  importUploadRef.value?.clearFiles()
}

const openImportDialog = () => {
  resetImportDialog()
  importDialogVisible.value = true
}

const isXlsxFile = (file) => {
  const fileName = file?.name || ''
  return fileName.toLowerCase().endsWith('.xlsx')
}

const runImportPreview = async (file) => {
  if (!file) return
  importPreviewLoading.value = true
  importResult.value = null
  try {
    const result = await importPlanXlsx(file, { dryRun: true, conflictStrategy: 'reject' })
    importResult.value = result
    if (result?.valid) {
      ElMessage.success(t('plan.xlsx.previewSuccess'))
    } else {
      ElMessage.warning(t('plan.xlsx.previewHasErrors'))
    }
  } catch (error) {
    ElMessage.error(getErrorMessage(error, t('plan.xlsx.previewFailed')))
  } finally {
    importPreviewLoading.value = false
  }
}

const handleImportFileChange = (uploadFile) => {
  const rawFile = uploadFile?.raw
  if (!rawFile || !isXlsxFile(rawFile)) {
    selectedImportFile.value = null
    importResult.value = null
    importUploadRef.value?.clearFiles()
    ElMessage.warning(t('plan.xlsx.onlyXlsx'))
    return
  }

  selectedImportFile.value = rawFile
  runImportPreview(rawFile)
}

const handleImportFileRemove = () => {
  selectedImportFile.value = null
  importResult.value = null
}

const handleImportFileExceed = (files) => {
  importUploadRef.value?.clearFiles()
  const file = files?.[0]
  if (file) {
    importUploadRef.value?.handleStart(file)
  }
}

const handleCommitImport = async () => {
  if (!selectedImportFile.value) {
    ElMessage.warning(t('plan.xlsx.fileRequired'))
    return
  }
  if (!importResult.value?.valid) {
    ElMessage.warning(t('plan.xlsx.fixErrorsBeforeImport'))
    return
  }

  importCommitLoading.value = true
  try {
    const result = await importPlanXlsx(selectedImportFile.value, { dryRun: false, conflictStrategy: 'reject' })
    importResult.value = result
    if (!result?.valid) {
      ElMessage.warning(t('plan.xlsx.importHasErrors'))
      return
    }
    ElMessage.success(t('plan.xlsx.importSuccess', { count: result.createdCount || 0 }))
    importDialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, t('plan.xlsx.importFailed')))
  } finally {
    importCommitLoading.value = false
  }
}

const formatImportError = (error) => {
  const code = error?.errorCode || error?.error_code
  if (!code) return error?.message || '-'
  const key = `plan.xlsx.errorCodes.${code}`
  const translated = t(key)
  if (translated !== key) return translated
  return error?.message || code
}

const handleSizeChange = (val) => {
  pagination.pageSize = val
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
.plan-list-page {
  display: block;
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
  grid-template-columns: repeat(4, minmax(160px, 1fr)) auto;
  gap: 16px;
  align-items: end;
}

.filter-form :deep(.el-form-item) {
  margin: 0;
}

.filter-form :deep(.el-input),
.filter-form :deep(.el-select) {
  width: 100%;
}

.filter-actions :deep(.el-form-item__content) {
  display: flex;
  gap: 10px;
  flex-wrap: nowrap;
}

.table-scroll {
  width: 100%;
  padding: 24px 24px 0;
}

.pagination {
  padding: 18px 24px 24px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-tag) {
  font-weight: 500;
}

.plan-xlsx-upload-icon {
  color: var(--primary);
  font-size: 32px;
}

.plan-xlsx-summary {
  margin-top: 14px;
}

.plan-xlsx-error-table {
  width: 100%;
  margin-top: 14px;
}

:global(.plan-xlsx-dialog .el-dialog__body) {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

@media (max-width: 1200px) {
  .filter-form {
    grid-template-columns: repeat(2, minmax(180px, 1fr));
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
