<!--
  文件路径: /frontend-next-js/src/app/maintenance/views/log/index.vue
  功能描述: 保养日志页面，管理设备保养记录
  主要功能:
    - 保养记录列表展示
    - 按设备名称、保养类型、状态筛选
    - 新增、编辑、删除和完成保养记录
    - 保养周期状态监控
-->
<template>
  <div class="maintenance-log-page page-layout">
    <BaseCard class="maintenance-main-card" :title="$t('maintenance.log.title')">
      <template #actions>
        <ActionButton variant="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          {{ $t('maintenance.log.actions.add') }}
        </ActionButton>
        <ActionButton variant="secondary" :loading="updateLoading" @click="handleUpdateCycle">
          <el-icon><RefreshRight /></el-icon>
          {{ $t('maintenance.log.actions.updateCycle') }}
        </ActionButton>
      </template>

      <section class="filter-section">
        <el-form :model="searchForm" label-position="top" class="maintenance-filter-form">
          <el-form-item :label="$t('maintenance.log.search.equipmentName')">
            <el-input
              v-model="searchForm.equipmentName"
              :placeholder="$t('maintenance.log.dialog.equipmentNamePlaceholder')"
              clearable
            />
          </el-form-item>
          <el-form-item :label="$t('maintenance.log.search.maintenanceType')">
            <el-select v-model="searchForm.maintenanceType" :placeholder="$t('maintenance.log.dialog.maintenanceTypePlaceholder')" clearable>
              <el-option :label="$t('maintenance.log.type.daily')" value="daily" />
              <el-option :label="$t('maintenance.log.type.level1')" value="level1" />
              <el-option :label="$t('maintenance.log.type.level2')" value="level2" />
              <el-option :label="$t('maintenance.log.type.level3')" value="level3" />
            </el-select>
          </el-form-item>
          <el-form-item :label="$t('maintenance.log.search.status')">
            <el-select v-model="searchForm.status" :placeholder="$t('maintenance.log.search.status')" clearable>
              <el-option :label="$t('maintenance.log.status.normal')" value="normal" />
              <el-option :label="$t('maintenance.log.status.warning')" value="warning" />
              <el-option :label="$t('maintenance.log.status.overdue')" value="overdue" />
            </el-select>
          </el-form-item>
          <el-form-item class="filter-actions">
            <ActionButton variant="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              {{ $t('common.search') }}
            </ActionButton>
            <ActionButton variant="secondary" @click="handleReset">
              <el-icon><Refresh /></el-icon>
              {{ $t('common.reset') }}
            </ActionButton>
          </el-form-item>
        </el-form>
      </section>

      <section class="maintenance-table-section">
        <el-alert
          v-if="overdueCount > 0"
          :title="$t('maintenance.log.messages.overdueAlert', { count: overdueCount })"
          type="error"
          :closable="false"
          show-icon
          class="maintenance-alert"
        />

        <div class="table-scroll">
          <el-table
            :data="tableData"
            v-loading="loading"
            border
            row-key="id"
            class="vibe-table"
            :row-class-name="tableRowClassName"
          >
            <el-table-column prop="maintenanceName" :label="$t('maintenance.log.table.equipmentName')" width="160" show-overflow-tooltip />
            <el-table-column prop="maintenanceCode" :label="$t('maintenance.log.table.equipmentCode')" width="150" />
            <el-table-column prop="maintenanceType" :label="$t('maintenance.log.table.maintenanceType')" width="130">
              <template #default="{ row }">
                <el-tag :type="getTypeTag(row.maintenanceType)">
                  {{ $t(`maintenance.log.type.${row.maintenanceType}`) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="content" :label="$t('maintenance.log.table.maintenanceContent')" min-width="220" show-overflow-tooltip />
            <el-table-column prop="lastDate" :label="$t('maintenance.log.table.lastDate')" width="150" />
            <el-table-column prop="nextDate" :label="$t('maintenance.log.table.nextDate')" width="150">
              <template #default="{ row }">
                <span :style="{ color: getDateColor(row) }">{{ row.nextDate }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="cycleDays" :label="$t('maintenance.log.table.cycleDays')" width="130" align="center" />
            <el-table-column prop="status" :label="$t('maintenance.log.table.status')" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ $t(`maintenance.log.status.${row.status}`) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="operator" :label="$t('maintenance.log.table.operator')" width="120" />
            <el-table-column prop="remark" :label="$t('maintenance.log.table.remark')" width="170" show-overflow-tooltip />
            <el-table-column :label="$t('maintenance.log.table.actions')" width="230" fixed="right" align="center">
              <template #default="{ row }">
                <div class="row-actions">
                  <ActionButton variant="row" size="small" @click="handleEdit(row)">{{ $t('maintenance.log.actions.edit') }}</ActionButton>
                  <ActionButton variant="success" size="small" @click="handleComplete(row)">{{ $t('maintenance.log.actions.complete') }}</ActionButton>
                  <ActionButton variant="danger" size="small" @click="handleDelete(row)">{{ $t('maintenance.log.actions.delete') }}</ActionButton>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="pagination">
          <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </section>
    </BaseCard>

    <MaintenanceFormDialog
      v-model="dialogVisible"
      :title="dialogTitle"
      :formData="form"
      :loading="submitLoading"
      @submit="handleSubmit"
    />

    <MaintenanceCompleteDialog
      v-model="completeDialogVisible"
      :rowData="completeRow"
      :loading="completeLoading"
      @submit="handleSubmitComplete"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import {
  getMaintenanceLogList,
  createMaintenanceLog,
  updateMaintenanceLog,
  deleteMaintenanceLog
} from '@/app/maintenance/api'
import MaintenanceFormDialog from '@/app/maintenance/components/MaintenanceFormDialog.vue'
import MaintenanceCompleteDialog from '@/app/maintenance/components/MaintenanceCompleteDialog.vue'

const { t } = useI18n()

const searchForm = reactive({
  equipmentName: '',
  maintenanceType: '',
  status: ''
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

const tableData = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)

const form = ref({
  id: null,
  maintenanceId: null,
  maintenanceName: '',
  maintenanceCode: '',
  maintenanceType: '',
  content: '',
  lastDate: '',
  cycleDays: 30,
  operator: '',
  remark: ''
})

const completeDialogVisible = ref(false)
const completeLoading = ref(false)
const completeRow = ref({})
const updateLoading = ref(false)

const overdueCount = computed(() => tableData.value.filter(item => item.status === 'overdue').length)

const getTypeTag = (type) => {
  const map = {
    daily: 'info',
    level1: 'success',
    level2: 'warning',
    level3: 'danger'
  }
  return map[type] || 'info'
}

const getStatusType = (status) => {
  const map = {
    normal: 'success',
    warning: 'warning',
    overdue: 'danger',
    pending: 'info'
  }
  return map[status] || 'info'
}

const getDateColor = (row) => {
  if (row.status === 'overdue') return 'var(--danger)'
  if (row.status === 'warning') return 'var(--warning)'
  return 'inherit'
}

const tableRowClassName = ({ row }) => (row.status === 'overdue' ? 'overdue-row' : '')

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.currentPage,
      pageSize: pagination.pageSize,
      equipmentName: searchForm.equipmentName || undefined,
      maintenanceType: searchForm.maintenanceType || undefined,
      status: searchForm.status || undefined
    }

    const res = await getMaintenanceLogList(params)
    tableData.value = res.items || []
    pagination.total = res.total || 0
  } catch (error) {
    ElMessage.error(t('maintenance.log.messages.loadFailed'))
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.currentPage = 1
  loadData()
}

const handleReset = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key] = ''
  })
  handleSearch()
}

const handleAdd = () => {
  dialogTitle.value = t('maintenance.log.dialog.addTitle')
  form.value = {
    id: null,
    maintenanceId: null,
    maintenanceName: '',
    maintenanceCode: '',
    maintenanceType: '',
    content: '',
    lastDate: new Date().toISOString().split('T')[0],
    cycleDays: 30,
    operator: '',
    remark: ''
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = t('maintenance.log.dialog.editTitle')
  form.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(t('maintenance.log.messages.deleteConfirm'), t('common.tip'), { type: 'warning' })
    await deleteMaintenanceLog(row.id)
    ElMessage.success(t('maintenance.log.messages.deleteSuccess'))
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('maintenance.log.messages.deleteFailed'))
    }
  }
}

const handleComplete = (row) => {
  completeRow.value = { ...row }
  completeDialogVisible.value = true
}

const handleSubmitComplete = async (submitData) => {
  completeLoading.value = true
  try {
    const updateData = {
      lastDate: submitData.completeDate.split(' ')[0],
      operator: submitData.operator,
      remark: submitData.remark,
      status: 'normal'
    }

    await updateMaintenanceLog(submitData.id, updateData)
    ElMessage.success(t('maintenance.log.messages.completeSuccess'))
    completeDialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error(t('maintenance.log.messages.updateFailed'))
  } finally {
    completeLoading.value = false
  }
}

const handleUpdateCycle = async () => {
  try {
    await ElMessageBox.confirm(t('maintenance.log.messages.updateConfirm'), t('common.tip'), { type: 'warning' })
    updateLoading.value = true
    await loadData()
    ElMessage.success(t('maintenance.log.messages.updateSuccess'))
  } catch (error) {
    // 用户取消确认框时不提示错误。
  } finally {
    updateLoading.value = false
  }
}

const calculateNextDate = (lastDate, cycleDays) => {
  const last = new Date(lastDate)
  const next = new Date(last.getTime() + cycleDays * 24 * 60 * 60 * 1000)
  return next.toISOString().split('T')[0]
}

const calculateStatus = (nextDate) => {
  const next = new Date(nextDate)
  const now = new Date()
  const diff = (next - now) / (1000 * 60 * 60 * 24)

  if (diff < 0) return 'overdue'
  if (diff <= 7) return 'warning'
  return 'normal'
}

const handleSubmit = async (submitData) => {
  submitLoading.value = true
  try {
    const data = { ...submitData }
    data.nextDate = calculateNextDate(data.lastDate, data.cycleDays)
    data.status = calculateStatus(data.nextDate)

    delete data.maintenanceName
    delete data.maintenanceCode

    if (data.id) {
      await updateMaintenanceLog(data.id, data)
    } else {
      await createMaintenanceLog(data)
    }

    ElMessage.success(t('maintenance.log.messages.saveSuccess'))
    dialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error(t('maintenance.log.messages.saveFailed'))
  } finally {
    submitLoading.value = false
  }
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
.maintenance-log-page {
  animation: fadeIn var(--transition-normal);
}

.maintenance-main-card :deep(.base-card__body) {
  padding: 0;
}

.maintenance-filter-form {
  display: grid;
  grid-template-columns: minmax(220px, 1fr) minmax(220px, 0.8fr) minmax(220px, 0.8fr) auto;
  gap: 16px;
  align-items: end;
}

.maintenance-filter-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.maintenance-filter-form :deep(.el-select) {
  width: 100%;
}

.filter-section {
  padding: 24px;
  border-bottom: 1px solid var(--border-secondary);
}

.filter-actions :deep(.el-form-item__content) {
  display: flex;
  gap: 12px;
  flex-wrap: nowrap;
}

.maintenance-table-section {
  padding: 28px 32px 32px;
  border-top: 1px solid var(--border-secondary);
}

.maintenance-alert {
  margin-bottom: 18px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.overdue-row) {
  background-color: color-mix(in srgb, var(--danger) 8%, transparent) !important;
}

:deep(.overdue-row:hover > td) {
  background-color: color-mix(in srgb, var(--danger) 12%, var(--bg-primary)) !important;
}

@media (max-width: 1200px) {
  .maintenance-filter-form {
    grid-template-columns: 1fr;
  }
}
</style>
