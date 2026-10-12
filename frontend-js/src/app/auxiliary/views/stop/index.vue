<!--
  文件路径: /frontend-next-js/src/app/auxiliary/views/stop/index.vue
  功能描述: 停机实绩页面，记录和管理设备停机信息
-->
<template>
  <div class="stop-page page-layout">
    <BaseCard class="stop-main-card" :title="$t('auxiliary.stop.subTitle')">
      <template #actions>
        <ActionButton variant="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          {{ $t('common.add') }}
        </ActionButton>
      </template>

      <div class="filter-section">
        <el-form :model="searchForm" class="filter-form" label-position="top">
          <el-form-item :label="$t('auxiliary.stop.search.dateRange')">
            <el-date-picker
              v-model="searchForm.dateRange"
              type="daterange"
              :range-separator="$t('auxiliary.stop.search.rangeSeparator')"
              :start-placeholder="$t('auxiliary.stop.search.startPlaceholder')"
              :end-placeholder="$t('auxiliary.stop.search.endPlaceholder')"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item :label="$t('auxiliary.stop.search.shift')">
            <el-select v-model="searchForm.shift" :placeholder="$t('auxiliary.stop.search.shiftPlaceholder')" clearable>
              <el-option :label="$t('auxiliary.shift.teams.teamA')" value="甲班" />
              <el-option :label="$t('auxiliary.shift.teams.teamB')" value="乙班" />
              <el-option :label="$t('auxiliary.shift.teams.teamC')" value="丙班" />
              <el-option :label="$t('auxiliary.shift.teams.teamD')" value="丁班" />
            </el-select>
          </el-form-item>
          <el-form-item :label="$t('auxiliary.stop.table.stopType')">
            <el-select v-model="searchForm.stopType" :placeholder="$t('auxiliary.stop.dialog.placeholder.stopType')" clearable>
              <el-option v-for="item in stopTypeOptions" :key="item.value" :label="$t(item.labelKey)" :value="item.value" />
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
      </div>

      <div class="table-scroll">
        <el-table :data="tableData" v-loading="loading" stripe border class="vibe-table">
          <el-table-column prop="startTime" :label="$t('auxiliary.stop.table.startTime')" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.startTime) }}
            </template>
          </el-table-column>
          <el-table-column prop="endTime" :label="$t('auxiliary.stop.table.endTime')" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.endTime) }}
            </template>
          </el-table-column>
          <el-table-column prop="duration" :label="$t('auxiliary.stop.table.duration')" width="120">
            <template #default="{ row }">
              <el-tag :type="getDurationType(row.duration)">
                {{ row.duration ? `${row.duration} ${$t('common.unit.min')}` : '-' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="shift" :label="$t('auxiliary.stop.table.shift')" width="100">
            <template #default="{ row }">
              {{ getShiftText(row.shift) }}
            </template>
          </el-table-column>
          <el-table-column prop="operator" :label="$t('auxiliary.stop.table.operator')" width="110" />
          <el-table-column prop="stopType" :label="$t('auxiliary.stop.table.stopType')" width="130">
            <template #default="{ row }">
              {{ getStopTypeText(row.stopType) }}
            </template>
          </el-table-column>
          <el-table-column prop="reason" :label="$t('auxiliary.stop.table.reason')" min-width="240">
            <template #default="{ row }">
              <span v-if="row.reason">{{ row.reason }}</span>
              <el-tag v-else type="warning" size="small">{{ $t('auxiliary.stop.table.toBeAdded') }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column :label="$t('common.operation')" width="140" fixed="right" align="center">
            <template #default="{ row }">
              <div class="row-actions">
                <ActionButton variant="row" size="small" @click="handleEdit(row)">{{ $t('common.edit') }}</ActionButton>
                <ActionButton variant="danger" size="small" @click="handleDelete(row)">{{ $t('common.delete') }}</ActionButton>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="920px" class="standard-form-dialog" @close="handleDialogClose">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="standard-dialog-form">
        <section class="dialog-section">
          <h3>{{ $t('common.basicInfo') }}</h3>
          <div class="dialog-form-grid">
            <el-form-item :label="$t('auxiliary.stop.dialog.startTime')" prop="startTime">
              <el-date-picker v-model="form.startTime" type="datetime" :placeholder="$t('auxiliary.stop.dialog.placeholder.startTime')" value-format="YYYY-MM-DD HH:mm:ss" />
            </el-form-item>
            <el-form-item :label="$t('auxiliary.stop.dialog.endTime')" prop="endTime">
              <el-date-picker v-model="form.endTime" type="datetime" :placeholder="$t('auxiliary.stop.dialog.placeholder.endTime')" value-format="YYYY-MM-DD HH:mm:ss" />
            </el-form-item>
            <el-form-item :label="$t('auxiliary.stop.dialog.shift')" prop="shift">
              <el-select v-model="form.shift" :placeholder="$t('auxiliary.stop.dialog.placeholder.shift')">
                <el-option :label="$t('auxiliary.shift.teams.teamA')" value="甲班" />
                <el-option :label="$t('auxiliary.shift.teams.teamB')" value="乙班" />
                <el-option :label="$t('auxiliary.shift.teams.teamC')" value="丙班" />
                <el-option :label="$t('auxiliary.shift.teams.teamD')" value="丁班" />
              </el-select>
            </el-form-item>
            <el-form-item :label="$t('auxiliary.stop.dialog.operator')" prop="operator">
              <el-input v-model="form.operator" :placeholder="$t('auxiliary.stop.dialog.placeholder.operator')" />
            </el-form-item>
            <el-form-item :label="$t('auxiliary.stop.dialog.stopType')" prop="stopType">
              <el-select v-model="form.stopType" :placeholder="$t('auxiliary.stop.dialog.placeholder.stopType')">
                <el-option v-for="item in stopTypeOptions" :key="item.value" :label="$t(item.labelKey)" :value="item.value" />
              </el-select>
            </el-form-item>
          </div>
        </section>
        <section class="dialog-section">
          <h3>{{ $t('auxiliary.stop.dialog.reason') }}</h3>
          <el-form-item :label="$t('auxiliary.stop.dialog.reason')" prop="reason">
            <el-input v-model="form.reason" type="textarea" :rows="4" :placeholder="$t('auxiliary.stop.dialog.placeholder.reason')" />
          </el-form-item>
        </section>
      </el-form>
      <template #footer>
        <div class="vibe-dialog-footer">
          <ActionButton variant="secondary" @click="dialogVisible = false">{{ $t('common.cancel') }}</ActionButton>
          <ActionButton variant="primary" :loading="submitLoading" @click="handleSubmit">{{ $t('common.confirm') }}</ActionButton>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createStopRecord, deleteStopRecord, getStopRecordList, updateStopRecord } from '@/app/auxiliary/api'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'

const { t } = useI18n()

const stopTypeOptions = [
  { labelKey: 'auxiliary.stop.types.fault', value: 'equipment', legacyValue: '设备故障' },
  { labelKey: 'auxiliary.stop.types.roll', value: 'coilChange', legacyValue: '换辊' },
  { labelKey: 'auxiliary.stop.types.material', value: 'material', legacyValue: '待料' },
  { labelKey: 'auxiliary.stop.types.planned', value: 'scheduled', legacyValue: '计划停机' },
  { labelKey: 'auxiliary.stop.types.quality', value: 'qualityIssue', legacyValue: '质量问题' },
  { labelKey: 'auxiliary.stop.types.other', value: 'other', legacyValue: '其他' }
]

const searchForm = reactive({
  dateRange: [],
  shift: '',
  stopType: ''
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

const tableData = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const formRef = ref()
const submitLoading = ref(false)

const form = reactive({
  id: null,
  startTime: '',
  endTime: '',
  duration: null,
  shift: '',
  operator: '',
  stopType: '',
  reason: ''
})

const dialogTitle = computed(() => {
  return form.id ? t('auxiliary.stop.dialog.editTitle') : t('auxiliary.stop.dialog.addTitle')
})

const rules = computed(() => ({
  startTime: [{ required: true, message: t('auxiliary.stop.dialog.rules.startTime'), trigger: 'change' }],
  shift: [{ required: true, message: t('auxiliary.stop.dialog.rules.shift'), trigger: 'change' }],
  operator: [{ required: true, message: t('auxiliary.stop.dialog.rules.operator'), trigger: 'blur' }]
}))

const normalizeStopType = (type) => {
  const option = stopTypeOptions.find(item => item.value === type || item.legacyValue === type)
  return option?.value || type || ''
}

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  return new Date(datetime).toLocaleString()
}

const getDurationType = (duration) => {
  if (!duration) return 'info'
  if (duration <= 10) return 'info'
  if (duration <= 30) return 'warning'
  return 'danger'
}

const getShiftText = (shift) => {
  if (!shift) return '-'
  const shiftMap = {
    '甲班': 'teamA',
    '乙班': 'teamB',
    '丙班': 'teamC',
    '丁班': 'teamD'
  }
  const key = shiftMap[shift]
  return key ? t(`auxiliary.shift.teams.${key}`) : shift
}

const getStopTypeText = (type) => {
  const normalized = normalizeStopType(type)
  const option = stopTypeOptions.find(item => item.value === normalized)
  return option ? t(option.labelKey) : t('auxiliary.stop.types.other')
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.currentPage,
      pageSize: pagination.pageSize,
      shift: searchForm.shift || undefined,
      stopType: searchForm.stopType || undefined
    }

    if (searchForm.dateRange?.length === 2) {
      params.startTime = `${searchForm.dateRange[0]}T00:00:00`
      params.endTime = `${searchForm.dateRange[1]}T23:59:59`
    }

    const res = await getStopRecordList(params)
    tableData.value = res.items || []
    pagination.total = res.total || 0
  } catch (error) {
    ElMessage.error(t('auxiliary.stop.messages.loadError'))
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.currentPage = 1
  loadData()
}

const handleReset = () => {
  searchForm.dateRange = []
  searchForm.shift = ''
  searchForm.stopType = ''
  handleSearch()
}

const resetForm = () => {
  Object.assign(form, {
    id: null,
    startTime: '',
    endTime: '',
    duration: null,
    shift: '',
    operator: '',
    stopType: '',
    reason: ''
  })
}

const handleAdd = () => {
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  Object.assign(form, {
    ...row,
    stopType: normalizeStopType(row.stopType)
  })
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(t('auxiliary.stop.messages.confirmDelete'), t('common.tip'), { type: 'warning' })
    await deleteStopRecord(row.id)
    ElMessage.success(t('auxiliary.stop.messages.deleteSuccess'))
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('auxiliary.stop.messages.deleteError'))
    }
  }
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    if (form.endTime && form.startTime) {
      const start = new Date(form.startTime).getTime()
      const end = new Date(form.endTime).getTime()
      form.duration = Number.isNaN(start) || Number.isNaN(end) ? 0 : Math.max(0, Math.round((end - start) / 60000))
    } else {
      form.duration = 0
    }

    const payload = {
      ...form,
      stopType: normalizeStopType(form.stopType)
    }

    if (form.id) {
      await updateStopRecord(form.id, payload)
      ElMessage.success(t('auxiliary.stop.messages.updateSuccess'))
    } else {
      await createStopRecord(payload)
      ElMessage.success(t('auxiliary.stop.messages.createSuccess'))
    }
    dialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error(t('auxiliary.stop.messages.actionError'))
  } finally {
    submitLoading.value = false
  }
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
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
.stop-page {
  display: block;
}

.stop-main-card :deep(.base-card__body) {
  padding: 0;
}

.stop-main-card :deep(.base-card__header) {
  min-height: 76px;
}

.filter-section {
  padding: 24px;
  border-bottom: 1px solid var(--border-secondary);
}

.filter-form {
  display: grid;
  grid-template-columns: minmax(280px, 1.4fr) minmax(160px, 0.8fr) minmax(180px, 0.8fr) auto;
  gap: 16px;
  align-items: end;
}

.filter-form :deep(.el-form-item) {
  margin: 0;
}

.filter-form :deep(.el-date-editor),
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
  display: flex;
  justify-content: flex-end;
  padding: 18px 24px 24px;
}

.standard-dialog-form {
  display: grid;
  gap: 28px;
}

.dialog-section {
  display: grid;
  gap: 18px;
}

.dialog-section h3 {
  margin: 0;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-secondary);
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 680;
}

.dialog-form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.dialog-form-grid :deep(.el-form-item),
.dialog-section :deep(.el-form-item) {
  margin: 0;
}

.dialog-form-grid :deep(.el-date-editor),
.dialog-form-grid :deep(.el-select) {
  width: 100%;
}

.form-item-wide {
  grid-column: 1 / -1;
}

@media (max-width: 1200px) {
  .filter-form {
    grid-template-columns: repeat(2, minmax(180px, 1fr));
  }
}

@media (max-width: 768px) {
  .filter-form,
  .dialog-form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
