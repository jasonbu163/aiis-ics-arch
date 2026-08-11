<!--
  文件路径: /frontend-js/src/app/system/views/user/index.vue
  功能描述: 用户管理页面，管理系统用户账号
  主要功能:
    - 用户列表展示与分页
    - 按用户名、角色筛选查询
    - 新增、编辑、删除用户
    - 用户状态管理
-->
<template>
  <div class="system-user-page page-layout">
    <BaseCard class="system-user-main-card" :title="$t('system.user')">
      <template #actions>
        <ActionButton variant="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          {{ $t('system.userManage.addUser') }}
        </ActionButton>
      </template>

      <section class="filter-section">
        <el-form :model="searchForm" label-position="top" class="system-user-filter-form">
          <el-form-item :label="$t('system.username')">
            <el-input v-model="searchForm.username" :placeholder="$t('system.userManage.pleaseInputUsername')" clearable />
          </el-form-item>
          <el-form-item :label="$t('system.role')">
            <el-select v-model="searchForm.role" :placeholder="$t('system.userManage.pleaseSelectRole')" clearable>
              <el-option
                v-for="option in roleFilterOptions"
                :key="option.value"
                :label="$t(option.labelKey)"
                :value="option.value"
              />
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

      <section class="system-user-table-section">
        <div class="table-scroll">
          <el-table :data="filteredTableData" v-loading="loading" border class="core-table">
            <el-table-column prop="username" :label="$t('system.username')" width="150" />
            <el-table-column prop="name" :label="$t('system.name')" width="120" />
            <el-table-column prop="role" :label="$t('system.role')" width="130">
              <template #default="{ row }">
                <el-tag :type="row.role === 'admin' ? 'danger' : row.role === 'supervisor' ? 'warning' : 'success'">
                  {{
                    row.role === 'admin' ? $t('system.roles.admin') :
                    row.role === 'supervisor' ? $t('system.roles.supervisor') :
                    row.role === 'operator' ? $t('system.roles.operator') :
                    $t('system.userManage.unknownRole')
                  }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="phone" :label="$t('system.phone')" width="150" />
            <el-table-column prop="email" :label="$t('system.email')" min-width="200" />
            <el-table-column prop="status" :label="$t('common.status')" width="110">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
                  {{ row.status === 'active' ? $t('common.enable') : $t('common.disable') }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="createdAt" :label="$t('system.createdAt')" width="180">
              <template #default="{ row }">
                {{ formatDateTime(row.createdAt) }}
              </template>
            </el-table-column>
            <el-table-column :label="$t('common.operation')" width="320" fixed="right" align="center">
              <template #default="{ row }">
                <div class="row-actions">
                  <ActionButton variant="row" size="small" :disabled="!canEditTarget(row)" @click="handleEdit(row)">{{ $t('common.edit') }}</ActionButton>
                  <ActionButton
                    :variant="row.status === 'active' ? 'warning' : 'success'"
                    size="small"
                    :disabled="!canToggleStatus(row)"
                    @click="handleToggleStatus(row)"
                  >
                    {{ row.status === 'active' ? $t('common.disable') : $t('common.enable') }}
                  </ActionButton>
                  <ActionButton variant="warning" size="small" :disabled="!canResetTarget(row)" @click="handleResetPassword(row)">
                    {{ $t('system.userManage.resetPassword') }}
                  </ActionButton>
                  <ActionButton variant="danger" size="small" :disabled="!canDeleteTarget(row)" @click="handleDelete(row)">{{ $t('common.delete') }}</ActionButton>
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

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="920px"
      class="standard-form-dialog"
      destroy-on-close
      @close="handleDialogClose"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="standard-dialog-form">
        <section class="dialog-section">
          <h3 class="dialog-section__title">{{ $t('common.basicInfo') }}</h3>
          <div class="dialog-form-grid">
            <el-form-item :label="$t('system.username')" prop="username">
              <el-input v-model="form.username" :placeholder="$t('system.userManage.pleaseInputUsername')" :disabled="isEdit" />
            </el-form-item>
            <el-form-item :label="$t('system.name')" prop="name">
              <el-input v-model="form.name" :placeholder="$t('system.userManage.pleaseInputName')" />
            </el-form-item>
            <el-form-item v-if="!isEdit" :label="$t('system.password')" prop="password">
              <el-input v-model="form.password" type="password" :placeholder="$t('system.userManage.pleaseInputPassword')" show-password />
            </el-form-item>
            <el-form-item v-if="showRoleField" :label="$t('system.role')" prop="role">
              <el-select v-model="form.role" :placeholder="$t('system.userManage.pleaseSelectRole')">
                <el-option :label="$t('system.roles.supervisor')" value="supervisor" />
                <el-option :label="$t('system.roles.operator')" value="operator" />
              </el-select>
            </el-form-item>
            <el-form-item :label="$t('system.phone')" prop="phone">
              <el-input v-model="form.phone" :placeholder="$t('system.userManage.pleaseInputPhone')" />
            </el-form-item>
            <el-form-item :label="$t('system.email')" prop="email">
              <el-input v-model="form.email" :placeholder="$t('system.userManage.pleaseInputEmail')" />
            </el-form-item>
          </div>
        </section>
      </el-form>

      <template #footer>
        <div class="core-dialog-footer">
          <ActionButton variant="secondary" @click="dialogVisible = false">{{ $t('common.cancel') }}</ActionButton>
          <ActionButton variant="primary" :loading="submitLoading" @click="handleSubmit">{{ $t('common.confirm') }}</ActionButton>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="resetPasswordDialogVisible"
      :title="$t('system.userManage.resetPassword')"
      width="560px"
      class="standard-form-dialog"
      destroy-on-close
      @close="handleResetPasswordDialogClose"
    >
      <el-form
        ref="resetPasswordFormRef"
        :model="resetPasswordForm"
        :rules="resetPasswordRules"
        label-position="top"
        class="standard-dialog-form"
      >
        <section class="dialog-section">
          <h3 class="dialog-section__title">{{ $t('system.userManage.targetAccount') }}</h3>
          <div class="dialog-form-grid">
            <el-form-item :label="$t('system.username')">
              <el-input :model-value="resetPasswordForm.username" disabled />
            </el-form-item>
            <el-form-item :label="$t('system.name')">
              <el-input :model-value="resetPasswordForm.name" disabled />
            </el-form-item>
          </div>
        </section>

        <section class="dialog-section">
          <h3 class="dialog-section__title">{{ $t('system.userManage.passwordSecurity') }}</h3>
          <div class="dialog-form-grid">
            <el-form-item :label="$t('system.userManage.newPassword')" prop="newPassword">
              <el-input v-model="resetPasswordForm.newPassword" type="password" :placeholder="$t('system.userManage.pleaseInputNewPassword')" show-password />
            </el-form-item>
            <el-form-item :label="$t('system.userManage.confirmPassword')" prop="confirmPassword">
              <el-input v-model="resetPasswordForm.confirmPassword" type="password" :placeholder="$t('system.userManage.pleaseConfirmPassword')" show-password />
            </el-form-item>
          </div>
        </section>
      </el-form>

      <template #footer>
        <div class="core-dialog-footer">
          <ActionButton variant="secondary" @click="resetPasswordDialogVisible = false">{{ $t('common.cancel') }}</ActionButton>
          <ActionButton variant="primary" :loading="resetPasswordSubmitLoading" @click="handleResetPasswordSubmit">{{ $t('common.confirm') }}</ActionButton>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import { getUserList, createUser, updateUser, deleteUser, resetUserPassword } from '@/app/system/api'
import { formatDateTime } from '@/utils/date'
import { useUserStore } from '@/store/user'

const { t, te } = useI18n()
const userStore = useUserStore()

const normalizeRole = (role) => {
  const roleMap = {
    admin: 'admin',
    supervisor: 'supervisor',
    operator: 'operator',
    '管理员': 'admin',
    '班组长': 'supervisor',
    '操作员': 'operator'
  }

  return roleMap[role] || role || ''
}

const currentActorRole = computed(() => normalizeRole(userStore.role))
const currentUserId = computed(() => Number(userStore.userInfo?.id))
const showRoleField = computed(() => userStore.isAdmin)
const roleFilterOptions = computed(() => {
  if (userStore.isAdmin) {
    return [
      { labelKey: 'system.roles.supervisor', value: 'supervisor' },
      { labelKey: 'system.roles.operator', value: 'operator' }
    ]
  }

  if (currentActorRole.value === 'supervisor') {
    return [
      { labelKey: 'system.roles.operator', value: 'operator' }
    ]
  }

  return []
})

const searchForm = reactive({
  username: '',
  role: ''
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

const tableData = ref([])
const loading = ref(false)

const isSelfTarget = (row) => Number(row.id) === currentUserId.value

const canManageTarget = (row) => {
  const targetRole = normalizeRole(row.role)

  if (isSelfTarget(row)) {
    return false
  }

  if (userStore.isAdmin) {
    return targetRole !== 'admin'
  }

  if (currentActorRole.value === 'supervisor') {
    return targetRole === 'operator'
  }

  return false
}

const isVisibleTarget = (row) => {
  const targetRole = normalizeRole(row.role)

  if (userStore.isAdmin) {
    return targetRole !== 'admin'
  }

  if (currentActorRole.value === 'supervisor') {
    return targetRole === 'operator'
  }

  return false
}

const canEditTarget = (row) => canManageTarget(row)
const canToggleStatus = (row) => canManageTarget(row)
const canDeleteTarget = (row) => canManageTarget(row)
const canResetTarget = (row) => canManageTarget(row)
const filteredTableData = computed(() => tableData.value.filter(isVisibleTarget))

const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const formRef = ref()
const submitLoading = ref(false)
const resetPasswordDialogVisible = ref(false)
const resetPasswordFormRef = ref()
const resetPasswordSubmitLoading = ref(false)

const form = reactive({
  id: null,
  username: '',
  name: '',
  password: '',
  role: 'operator',
  phone: '',
  email: ''
})

const resetPasswordForm = reactive({
  id: null,
  username: '',
  name: '',
  newPassword: '',
  confirmPassword: ''
})

const validateResetConfirmPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error(t('system.userManage.pleaseConfirmPassword')))
    return
  }
  if (value !== resetPasswordForm.newPassword) {
    callback(new Error(t('system.userManage.passwordMismatch')))
    return
  }
  callback()
}

const rules = {
  username: [
    { required: true, message: t('system.userManage.pleaseInputUsername'), trigger: 'blur' },
    { min: 3, max: 20, message: t('system.userManage.usernameLength'), trigger: 'blur' }
  ],
  name: [
    { required: true, message: t('system.userManage.pleaseInputName'), trigger: 'blur' }
  ],
  password: [
    { required: true, message: t('system.userManage.pleaseInputPassword'), trigger: 'blur' },
    { min: 6, max: 20, message: t('system.userManage.passwordLength'), trigger: 'blur' }
  ],
  role: [
    { required: true, message: t('system.userManage.pleaseSelectRole'), trigger: 'change' }
  ]
}

const resetPasswordRules = {
  newPassword: [
    { required: true, message: t('system.userManage.pleaseInputNewPassword'), trigger: 'blur' },
    { min: 6, max: 20, message: t('system.userManage.passwordLength'), trigger: 'blur' }
  ],
  confirmPassword: [
    { validator: validateResetConfirmPassword, trigger: 'blur' }
  ]
}

const getAccountErrorMessage = (error, fallback) => {
  const code = error?.errorCode || error?.error_code || error?.data?.errorCode || error?.response?.data?.errorCode || error?.message
  const key = code ? `system.userManage.errorCodes.${code}` : ''

  if (key && te(key)) {
    return t(key)
  }

  return error?.response?.data?.detail || error?.message || fallback
}

const showActionDenied = () => {
  ElMessage.warning(t('system.userManage.actionNotAllowed'))
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.currentPage,
      pageSize: pagination.pageSize,
      username: searchForm.username || undefined,
      role: searchForm.role || (currentActorRole.value === 'supervisor' ? 'operator' : undefined)
    }

    const res = await getUserList(params)

    if (res && res.items) {
      tableData.value = res.items
      pagination.total = res.total || 0
    }
  } catch (error) {
    ElMessage.error(getAccountErrorMessage(error, t('system.userManage.loadFailed')))
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
  if (!userStore.isAdmin && currentActorRole.value !== 'supervisor') {
    showActionDenied()
    return
  }

  dialogTitle.value = t('system.userManage.addUser')
  isEdit.value = false
  Object.keys(form).forEach(key => {
    form[key] = key === 'id' ? null : (key === 'role' ? 'operator' : '')
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  if (!canEditTarget(row)) {
    showActionDenied()
    return
  }

  dialogTitle.value = t('system.userManage.editUser')
  isEdit.value = true
  Object.keys(form).forEach(key => {
    form[key] = row[key] !== undefined ? row[key] : ''
  })
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  if (!canDeleteTarget(row)) {
    showActionDenied()
    return
  }

  try {
    await ElMessageBox.confirm(t('system.messages.deleteConfirm'), t('common.tip'), { type: 'warning' })
    await deleteUser(row.id)
    ElMessage.success(t('system.messages.deleteSuccess'))
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(getAccountErrorMessage(error, t('common.error')))
    }
  }
}

const handleToggleStatus = async (row) => {
  if (!canToggleStatus(row)) {
    showActionDenied()
    return
  }

  const action = row.status === 'active' ? t('common.disable') : t('common.enable')
  const newStatus = row.status === 'active' ? 'inactive' : 'active'

  try {
    await ElMessageBox.confirm(t('system.messages.toggleStatusConfirm', { action }), t('common.tip'), { type: 'warning' })
    await updateUser(row.id, { status: newStatus })
    ElMessage.success(t('common.success'))
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(getAccountErrorMessage(error, t('common.error')))
    }
  }
}

const handleResetPassword = (row) => {
  if (!canResetTarget(row)) {
    showActionDenied()
    return
  }

  resetPasswordForm.id = row.id
  resetPasswordForm.username = row.username || ''
  resetPasswordForm.name = row.name || ''
  resetPasswordForm.newPassword = ''
  resetPasswordForm.confirmPassword = ''
  resetPasswordDialogVisible.value = true
}

const handleResetPasswordSubmit = async () => {
  if (!resetPasswordFormRef.value) return

  const valid = await resetPasswordFormRef.value.validate().catch(() => false)
  if (!valid) return

  resetPasswordSubmitLoading.value = true
  try {
    await resetUserPassword(resetPasswordForm.id, {
      newPassword: resetPasswordForm.newPassword
    })
    resetPasswordDialogVisible.value = false
    ElMessage.success(t('system.userManage.resetPasswordSuccess'))
  } catch (error) {
    ElMessage.error(getAccountErrorMessage(error, t('system.userManage.resetPasswordFailed')))
  } finally {
    resetPasswordSubmitLoading.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        const submitData = {
          name: form.name,
          phone: form.phone,
          email: form.email
        }

        if (userStore.isAdmin) {
          submitData.role = form.role
        }

        if (!isEdit.value) {
          submitData.username = form.username
          submitData.password = form.password
        }

        if (form.id) {
          await updateUser(form.id, submitData)
        } else {
          await createUser(submitData)
        }

        ElMessage.success(t('system.messages.saveSuccess'))
        dialogVisible.value = false
        loadData()
      } catch (error) {
        ElMessage.error(getAccountErrorMessage(error, t('common.error')))
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
}

const handleResetPasswordDialogClose = () => {
  resetPasswordFormRef.value?.resetFields()
  resetPasswordForm.id = null
  resetPasswordForm.username = ''
  resetPasswordForm.name = ''
  resetPasswordForm.newPassword = ''
  resetPasswordForm.confirmPassword = ''
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
.system-user-page {
  animation: fadeIn var(--transition-normal);
}

.system-user-main-card :deep(.base-card__body) {
  padding: 0;
}

.system-user-filter-form {
  display: grid;
  grid-template-columns: minmax(220px, 1fr) minmax(220px, 0.8fr) auto;
  gap: 16px;
  align-items: end;
}

.system-user-filter-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.system-user-filter-form :deep(.el-select) {
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

.system-user-table-section {
  padding: 28px 32px 32px;
  border-top: 1px solid var(--border-secondary);
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 1200px) {
  .system-user-filter-form {
    grid-template-columns: 1fr;
  }
}
</style>
