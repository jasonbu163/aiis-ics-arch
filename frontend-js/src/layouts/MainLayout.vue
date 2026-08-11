<!--
  文件路径: /frontend-js/src/layouts/MainLayout.vue
  功能描述: 主布局组件，包含侧边栏导航和顶部栏
  主要功能:
    - 侧边栏菜单导航（支持折叠、权限过滤）
    - 顶部面包屑和用户信息
    - 路由视图容器
    - 用户登出功能
    - 主题切换支持
-->
<template>
  <el-container class="main-layout">
    <el-aside
      :width="isCollapse ? '0' : '236px'"
      :class="[
        'sidebar',
        {
          'sidebar-hidden': isSidebarFloatingMode,
          'sidebar-floating-open': isSidebarFloatingMode && isFloatingSidebarOpen
        }
      ]"
      @mouseenter="handleSidebarEnter"
      @mouseleave="handleSidebarLeave"
    >
      <el-menu
        :default-active="activeMenu"
        :collapse="false"
        :unique-opened="true"
        :background-color="sidebarBg"
        :text-color="sidebarText"
        :active-text-color="sidebarActive"
        class="nav-menu"
        router
        @select="handleMenuSelect"
      >
        <el-sub-menu v-if="userStore.isAdmin || hasPageAccess('system.user')" index="system">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>{{ $t('nav.system') }}</span>
          </template>
          <el-menu-item v-if="hasPageAccess('system.user')" index="/system/user">
            <el-icon><User /></el-icon>
            <span>{{ $t('system.user') }}</span>
          </el-menu-item>
          <el-menu-item v-if="userStore.isAdmin && hasPageAccess('system.projection-mapping')" index="/system/dict">
            <el-icon><Collection /></el-icon>
            <span>{{ $t('system.mapping.title') }}</span>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>

      <div v-if="!isCollapse" class="sidebar-brand-footer">
        <div class="sidebar-brand-surface">
          <BrandLogo class="sidebar-brand-logo" variant="shell" />
        </div>
      </div>
    </el-aside>

    <!-- 主内容区 -->
    <el-container :class="['main-container', { 'main-container-sidebar-hidden': isCollapse }]">
      <el-header class="header">
        <div class="header-shell">
          <div class="header-left">
            <button
              :class="['collapse-btn', { 'collapse-btn-active': isCollapse }]"
              type="button"
              @click="toggleCollapse"
              @mouseenter="handleTriggerEnter"
              @mouseleave="handleTriggerLeave"
              @focus="handleTriggerEnter"
              @blur="handleTriggerLeave"
            >
              <el-icon>
                <Fold v-if="!isCollapse" />
                <Expand v-else />
              </el-icon>
            </button>
            <div class="header-copy">
              <div class="header-breadcrumb">
                <el-breadcrumb separator="/">
                  <el-breadcrumb-item v-if="currentRoute.meta?.parentTitleKey">
                    {{ $t(currentRoute.meta.parentTitleKey) }}
                  </el-breadcrumb-item>
                  <el-breadcrumb-item v-if="currentRoute.meta?.titleKey">
                    {{ $t(currentRoute.meta.titleKey) }}
                  </el-breadcrumb-item>
                </el-breadcrumb>
              </div>
            </div>
          </div>

          <!-- <div class="header-brand-zone">
            <div class="header-brand-surface">
              <BrandLogo class="header-brand-logo" variant="shell" />
            </div>
          </div> -->

          <HeaderUtilityCapsule variant="inline" class="header-right">
            <div
              class="user-menu"
              @mouseenter="handleUserMenuEnter"
              @mouseleave="handleUserMenuLeave"
              @focusin="handleUserMenuEnter"
              @focusout="handleUserMenuFocusOut"
            >
              <button
                class="user-info"
                type="button"
                @click="toggleUserMenu"
              >
                <el-avatar :size="32" class="user-avatar" icon="User" />
                <span class="username">{{ userStore.username }}</span>
                <el-tag size="small" class="role-tag" :type="userStore.isAdmin ? 'danger' : 'success'">
                  {{ getRoleLabel(userStore.role) }}
                </el-tag>
              </button>
              <transition name="user-menu-fade">
                <div v-if="isUserMenuOpen" class="user-menu-panel">
                  <button class="user-menu-action" type="button" @click="openProfileDialog">
                    <el-icon><User /></el-icon>
                    <span>{{ $t('user.profile') }}</span>
                  </button>
                  <button class="user-menu-action" type="button" @click="openPasswordDialog">
                    <el-icon><Lock /></el-icon>
                    <span>{{ $t('user.changePassword') }}</span>
                  </button>
                  <button class="user-menu-action" type="button" @click="handleLogout">
                    <el-icon><SwitchButton /></el-icon>
                    <span>{{ $t('user.logout') }}</span>
                  </button>
                </div>
              </transition>
            </div>
          </HeaderUtilityCapsule>
        </div>
      </el-header>

      <el-main class="main-content">
        <div class="content-shell">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </el-main>

      <el-backtop
        target=".main-content"
        :right="32"
        :bottom="32"
        :visibility-height="240"
        class="main-backtop"
        :title="$t('common.backToTop')"
        :aria-label="$t('common.backToTop')"
      >
        <el-icon><ArrowUp /></el-icon>
      </el-backtop>
    </el-container>

    <el-dialog
      v-model="profileDialogVisible"
      :title="$t('user.profileTitle')"
      width="640px"
      class="standard-form-dialog"
      destroy-on-close
      @close="handleProfileDialogClose"
    >
      <el-form
        ref="profileFormRef"
        v-loading="profileLoading"
        :model="profileForm"
        :rules="profileRules"
        label-position="top"
        class="standard-dialog-form"
      >
        <section class="dialog-section">
          <h3 class="dialog-section__title">{{ $t('common.basicInfo') }}</h3>
          <div class="dialog-form-grid">
            <el-form-item :label="$t('system.name')" prop="name">
              <el-input v-model="profileForm.name" :placeholder="$t('user.pleaseInputName')" />
            </el-form-item>
            <el-form-item :label="$t('system.phone')" prop="phone">
              <el-input v-model="profileForm.phone" :placeholder="$t('user.pleaseInputPhone')" />
            </el-form-item>
            <el-form-item :label="$t('system.email')" prop="email">
              <el-input v-model="profileForm.email" :placeholder="$t('user.pleaseInputEmail')" />
            </el-form-item>
          </div>
        </section>
      </el-form>

      <template #footer>
        <div class="core-dialog-footer">
          <el-button @click="profileDialogVisible = false">{{ $t('common.cancel') }}</el-button>
          <el-button type="primary" :loading="profileSubmitLoading" @click="handleProfileSubmit">
            {{ $t('common.save') }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="passwordDialogVisible"
      :title="$t('user.changePassword')"
      width="560px"
      class="standard-form-dialog"
      destroy-on-close
      @close="handlePasswordDialogClose"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-position="top"
        class="standard-dialog-form"
      >
        <section class="dialog-section">
          <h3 class="dialog-section__title">{{ $t('user.passwordSecurity') }}</h3>
          <div class="account-password-form-grid">
            <el-form-item :label="$t('user.oldPassword')" prop="oldPassword">
              <el-input v-model="passwordForm.oldPassword" type="password" :placeholder="$t('user.pleaseInputOldPassword')" show-password />
            </el-form-item>
            <el-form-item :label="$t('user.newPassword')" prop="newPassword">
              <el-input v-model="passwordForm.newPassword" type="password" :placeholder="$t('user.pleaseInputNewPassword')" show-password />
            </el-form-item>
            <el-form-item :label="$t('user.confirmPassword')" prop="confirmPassword">
              <el-input v-model="passwordForm.confirmPassword" type="password" :placeholder="$t('user.pleaseConfirmPassword')" show-password />
            </el-form-item>
          </div>
        </section>
      </el-form>

      <template #footer>
        <div class="core-dialog-footer">
          <el-button @click="passwordDialogVisible = false">{{ $t('common.cancel') }}</el-button>
          <el-button type="primary" :loading="passwordSubmitLoading" @click="handlePasswordSubmit">
            {{ $t('common.confirm') }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { ref, reactive, computed, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { useThemeStore } from '@/store/theme'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import HeaderUtilityCapsule from '@/components/shell/HeaderUtilityCapsule.vue'
import BrandLogo from '@/components/shell/BrandLogo.vue'
import {
  changeCurrentUserPassword,
  getCurrentUser,
  updateCurrentUserProfile
} from '@/api/auth'

const { t, te } = useI18n()
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()

const isCollapse = ref(false)
const isFloatingSidebarOpen = ref(false)
const isUserMenuOpen = ref(false)
const isSidebarFloatingMode = ref(false)
const profileDialogVisible = ref(false)
const profileLoading = ref(false)
const profileSubmitLoading = ref(false)
const passwordDialogVisible = ref(false)
const passwordSubmitLoading = ref(false)
const profileFormRef = ref()
const passwordFormRef = ref()
const currentRoute = computed(() => route)
const activeMenu = computed(() => route.path)
let floatingSidebarTimer = null
let userMenuTimer = null
let sidebarTransitionTimer = null

const profileForm = reactive({
  name: '',
  phone: '',
  email: ''
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error(t('user.pleaseConfirmPassword')))
    return
  }
  if (value !== passwordForm.newPassword) {
    callback(new Error(t('user.passwordMismatch')))
    return
  }
  callback()
}

const profileRules = {
  name: [
    { required: true, message: t('user.pleaseInputName'), trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: t('user.invalidEmail'), trigger: 'blur' }
  ]
}

const passwordRules = {
  oldPassword: [
    { required: true, message: t('user.pleaseInputOldPassword'), trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: t('user.pleaseInputNewPassword'), trigger: 'blur' },
    { min: 6, max: 20, message: t('user.passwordLength'), trigger: 'blur' }
  ],
  confirmPassword: [
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const sidebarBg = computed(() => 'var(--sidebar-bg)')
const sidebarText = computed(() => 'var(--sidebar-text)')
const sidebarActive = computed(() => 'var(--sidebar-active)')
const hasPageAccess = (pageId) => {
  return userStore.hasPageAccess(pageId)
}

const getRoleLabel = (role) => {
  const roleKeyMap = {
    'admin': 'admin',
    'supervisor': 'supervisor',
    'operator': 'operator',
    '管理员': 'admin',
    '班组长': 'supervisor',
    '操作员': 'operator'
  }
  const key = roleKeyMap[role] || role
  return t(`system.roles.${key}`) || role
}

const toggleCollapse = () => {
  isFloatingSidebarOpen.value = false
  clearSidebarTransitionTimer()

  if (isCollapse.value) {
    isSidebarFloatingMode.value = false
    window.requestAnimationFrame(() => {
      isCollapse.value = false
    })
    return
  }

  isCollapse.value = true
  isSidebarFloatingMode.value = false
  sidebarTransitionTimer = window.setTimeout(() => {
    if (isCollapse.value) {
      isSidebarFloatingMode.value = true
    }
  }, 320)
}

const clearFloatingSidebarTimer = () => {
  if (floatingSidebarTimer) {
    window.clearTimeout(floatingSidebarTimer)
    floatingSidebarTimer = null
  }
}

const clearUserMenuTimer = () => {
  if (userMenuTimer) {
    window.clearTimeout(userMenuTimer)
    userMenuTimer = null
  }
}

const clearSidebarTransitionTimer = () => {
  if (sidebarTransitionTimer) {
    window.clearTimeout(sidebarTransitionTimer)
    sidebarTransitionTimer = null
  }
}

const openFloatingSidebar = () => {
  if (!isCollapse.value) {
    return
  }
  clearFloatingSidebarTimer()
  isFloatingSidebarOpen.value = true
}

const scheduleFloatingSidebarClose = () => {
  if (!isCollapse.value) {
    return
  }
  clearFloatingSidebarTimer()
  floatingSidebarTimer = window.setTimeout(() => {
    isFloatingSidebarOpen.value = false
  }, 180)
}

const handleTriggerEnter = () => {
  openFloatingSidebar()
}

const handleTriggerLeave = () => {
  scheduleFloatingSidebarClose()
}

const handleSidebarEnter = () => {
  openFloatingSidebar()
}

const handleSidebarLeave = () => {
  scheduleFloatingSidebarClose()
}

const handleMenuSelect = () => {
  if (isCollapse.value) {
    isFloatingSidebarOpen.value = false
  }
}

const openUserMenu = () => {
  clearUserMenuTimer()
  isUserMenuOpen.value = true
}

const scheduleUserMenuClose = () => {
  clearUserMenuTimer()
  userMenuTimer = window.setTimeout(() => {
    isUserMenuOpen.value = false
  }, 140)
}

const toggleUserMenu = () => {
  clearUserMenuTimer()
  isUserMenuOpen.value = !isUserMenuOpen.value
}

const handleUserMenuEnter = () => {
  openUserMenu()
}

const handleUserMenuLeave = () => {
  scheduleUserMenuClose()
}

const handleUserMenuFocusOut = (event) => {
  if (event.currentTarget.contains(event.relatedTarget)) {
    return
  }
  scheduleUserMenuClose()
}

const fillProfileForm = (userInfo = {}) => {
  profileForm.name = userInfo.name || ''
  profileForm.phone = userInfo.phone || ''
  profileForm.email = userInfo.email || ''
}

const getAccountErrorMessage = (error, fallback) => {
  const code = error?.errorCode || error?.error_code || error?.data?.errorCode || error?.response?.data?.errorCode || error?.message
  const key = code ? `user.errorCodes.${code}` : ''

  if (key && te(key)) {
    return t(key)
  }

  return error?.response?.data?.detail || error?.message || fallback
}

const openProfileDialog = async () => {
  isUserMenuOpen.value = false
  fillProfileForm(userStore.userInfo)
  profileDialogVisible.value = true
  profileLoading.value = true

  try {
    const currentUser = await getCurrentUser()
    userStore.setUserInfo(currentUser)
    fillProfileForm(currentUser)
  } catch (error) {
    ElMessage.error(getAccountErrorMessage(error, t('user.profileLoadFailed')))
  } finally {
    profileLoading.value = false
  }
}

const openPasswordDialog = () => {
  isUserMenuOpen.value = false
  passwordDialogVisible.value = true
}

const handleProfileSubmit = async () => {
  if (!profileFormRef.value) return

  const valid = await profileFormRef.value.validate().catch(() => false)
  if (!valid) return

  profileSubmitLoading.value = true
  try {
    const updatedUser = await updateCurrentUserProfile({
      name: profileForm.name,
      phone: profileForm.phone,
      email: profileForm.email
    })
    userStore.setUserInfo(updatedUser)
    profileDialogVisible.value = false
    ElMessage.success(t('user.profileSaveSuccess'))
  } catch (error) {
    ElMessage.error(getAccountErrorMessage(error, t('user.profileSaveFailed')))
  } finally {
    profileSubmitLoading.value = false
  }
}

const handlePasswordSubmit = async () => {
  if (!passwordFormRef.value) return

  const valid = await passwordFormRef.value.validate().catch(() => false)
  if (!valid) return

  passwordSubmitLoading.value = true
  try {
    const result = await changeCurrentUserPassword({
      oldPassword: passwordForm.oldPassword,
      newPassword: passwordForm.newPassword
    })
    passwordDialogVisible.value = false

    if (result?.requiresRelogin || result?.requires_relogin) {
      userStore.clearSession()
      ElMessage.success(t('user.passwordChangedRelogin'))
      router.replace('/login')
      return
    }

    ElMessage.success(t('user.passwordChanged'))
  } catch (error) {
    ElMessage.error(getAccountErrorMessage(error, t('user.passwordChangeFailed')))
  } finally {
    passwordSubmitLoading.value = false
  }
}

const handleProfileDialogClose = () => {
  profileFormRef.value?.resetFields()
}

const handlePasswordDialogClose = () => {
  passwordFormRef.value?.resetFields()
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
}

const handleLogout = async () => {
  try {
    isUserMenuOpen.value = false
    await ElMessageBox.confirm(
      t('user.logoutConfirm'),
      t('common.tip'),
      { type: 'warning' }
    )

    await userStore.logout()

    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')

    ElMessage.success(t('user.logoutSuccess'))

    router.replace('/login')
  } catch (error) {
    // 取消退出
  }
}

onBeforeUnmount(() => {
  clearFloatingSidebarTimer()
  clearUserMenuTimer()
  clearSidebarTransitionTimer()
})
</script>

<style scoped>
.main-layout {
  --layout-gutter: 20px;
  height: 100vh;
  background: transparent;
}

.main-container {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100vh;
  min-width: 0;
}

.sidebar {
  display: flex;
  flex-direction: column;
  padding: 0;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--border-primary);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  transition:
    width 320ms cubic-bezier(0.2, 0.8, 0.2, 1),
    opacity var(--transition-normal),
    transform var(--transition-normal),
    background-color var(--transition-normal);
  min-height: 0;
  overflow-x: hidden;
}

.sidebar-hidden {
  position: fixed;
  top: 76px;
  left: var(--layout-gutter);
  z-index: 2200;
  width: 236px !important;
  height: auto;
  max-height: calc(100vh - 96px);
  border: 1px solid var(--border-primary);
  border-radius: 16px;
  box-shadow: var(--shadow-xl);
  opacity: 0;
  pointer-events: none;
  transform: translateX(calc(-100% - 32px));
  overflow-y: auto;
}

.sidebar-hidden.sidebar-floating-open {
  opacity: 1;
  pointer-events: auto;
  transform: translateX(0);
}

.nav-menu {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  background: transparent;
  padding: 18px 14px 14px;
}

.sidebar-brand-footer {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  min-height: 96px;
  padding: 12px 20px;
  border-top: 1px solid var(--header-border);
}

.sidebar-brand-surface {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
  height: 72px;
}

.sidebar-brand-logo {
  width: 100%;
  height: 100%;
}

:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  margin-bottom: 6px;
}

:deep(.el-menu-item > span),
:deep(.el-sub-menu__title > span:first-of-type) {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.el-sub-menu .el-menu-item) {
  min-width: 0;
}

:deep(.el-sub-menu__title .el-sub-menu__icon-arrow) {
  margin-left: auto;
  flex-shrink: 0;
}

:deep(.el-sub-menu__title:hover),
:deep(.el-menu-item:hover) {
  background-color: var(--sidebar-active-bg) !important;
}

.header {
  position: absolute;
  top: 0;
  right: 0;
  left: 0;
  z-index: 1200;
  height: auto;
  min-height: 84px;
  padding: 10px var(--layout-gutter) 0;
  background: transparent;
  border-bottom: 0;
  overflow: visible;
  pointer-events: none;
}

.header-shell {
  position: relative;
  container-name: app-header;
  container-type: inline-size;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 99.5%;
  min-height: 64px;
  gap: 16px;
  padding: 10px 12px;
  border: 1px solid var(--border-primary);
  border-radius: 22px;
  background: var(--header-glass-bg);
  box-shadow: var(--header-glass-shadow);
  backdrop-filter: blur(34px) saturate(1.08);
  -webkit-backdrop-filter: blur(34px) saturate(1.08);
  pointer-events: auto;
  transform-origin: right top;
  animation: header-capsule-enter 420ms cubic-bezier(0.2, 0.8, 0.2, 1) both;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
  animation: header-content-enter 300ms ease 120ms both;
}

.collapse-btn {
  width: 40px;
  height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-primary);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.02);
  cursor: pointer;
  color: var(--text-secondary);
  appearance: none;
}

.collapse-btn:hover {
  color: var(--text-primary);
  border-color: var(--border-strong);
  background: rgba(255, 255, 255, 0.05);
}

.collapse-btn-active {
  color: var(--primary);
  border-color: rgba(113, 112, 255, 0.35);
  background: var(--primary-subtle);
}

.header-copy {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
}

.header-breadcrumb {
  min-width: 0;
  overflow: hidden;
}

.header-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  flex: 0 0 auto;
  flex-wrap: wrap;
  animation: header-content-enter 300ms ease 80ms both;
}

.header-brand-zone {
  position: absolute;
  top: 50%;
  left: 50%;
  width: clamp(196px, 16vw, 252px);
  height: 56px;
  pointer-events: none;
  transform: translate(-50%, -50%);
}

.header-brand-surface {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.header-brand-logo {
  width: 100%;
  height: 100%;
}

.user-menu {
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  height: 44px;
  box-sizing: border-box;
  gap: 10px;
  cursor: pointer;
  padding: 0 10px 0 6px;
  border: 1px solid var(--border-primary);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.03);
  color: inherit;
  transition: all var(--transition-normal);
  appearance: none;
}

.user-info:hover {
  border-color: var(--border-strong);
  background: rgba(255, 255, 255, 0.05);
  box-shadow: var(--shadow-sm);
}

.user-avatar {
  background: linear-gradient(135deg, var(--primary), var(--primary-light));
  color: var(--text-inverse);
}

.username {
  font-weight: 510;
  color: var(--text-primary);
}

.role-tag {
  border: none;
}

.user-menu-panel {
  position: absolute;
  top: calc(100% + 12px);
  right: 0;
  z-index: 2500;
  min-width: 168px;
  padding: 8px;
  border: 1px solid var(--border-primary);
  border-radius: 14px;
  background: var(--bg-dialog);
  box-shadow: var(--shadow-xl);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
}

.user-menu-panel::before {
  position: absolute;
  top: -7px;
  right: 48px;
  width: 12px;
  height: 12px;
  content: "";
  border-top: 1px solid var(--border-primary);
  border-left: 1px solid var(--border-primary);
  background: var(--bg-dialog);
  transform: rotate(45deg);
}

.user-menu-action {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  width: 100%;
  height: 44px;
  gap: 10px;
  padding: 0 14px;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: var(--text-secondary);
  font: inherit;
  cursor: pointer;
  appearance: none;
}

.user-menu-action:hover {
  background: var(--sidebar-active-bg);
  color: var(--text-primary);
}

.account-password-form-grid {
  display: grid;
  gap: 18px;
}

.user-menu-fade-enter-active,
.user-menu-fade-leave-active {
  transition: opacity var(--transition-fast), transform var(--transition-fast);
}

.user-menu-fade-enter-from,
.user-menu-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.main-content {
  background: transparent;
  padding: 90px var(--layout-gutter) var(--layout-gutter);
  overflow-y: auto;
  flex: 1;
}

.content-shell {
  width: 100%;
}

:deep(.main-backtop.el-backtop) {
  width: 44px;
  height: 44px;
  color: var(--primary);
  background: var(--header-glass-bg);
  border: 1px solid var(--border-primary);
  box-shadow: var(--header-glass-shadow);
  backdrop-filter: blur(22px) saturate(1.08);
  -webkit-backdrop-filter: blur(22px) saturate(1.08);
  transition:
    color var(--transition-fast),
    background-color var(--transition-fast),
    border-color var(--transition-fast),
    transform var(--transition-fast),
    box-shadow var(--transition-fast);
}

:deep(.main-backtop.el-backtop:hover),
:deep(.main-backtop.el-backtop:focus-visible) {
  color: var(--primary);
  background: var(--primary-subtle);
  border-color: var(--border-strong);
  box-shadow: var(--header-glass-shadow);
  transform: translateY(-1px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.24s ease, transform 0.24s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

:deep(.el-breadcrumb__inner),
:deep(.el-breadcrumb__inner a) {
  color: var(--text-secondary);
  font-weight: 510;
}

:deep(.el-breadcrumb__inner a:hover) {
  color: var(--primary);
}

:deep(.el-breadcrumb__separator) {
  color: var(--text-muted);
}

:deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: var(--text-primary);
  font-weight: 590;
}

@keyframes header-capsule-enter {
  0% {
    opacity: 0.82;
    transform: translateY(-10px) scaleX(0.36);
    filter: blur(1px);
  }

  62% {
    opacity: 1;
    transform: translateY(0) scaleX(1.012);
    filter: blur(0);
  }

  100% {
    opacity: 1;
    transform: translateY(0) scaleX(1);
    filter: blur(0);
  }
}

@keyframes header-content-enter {
  from {
    opacity: 0;
    transform: translateY(-3px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .header-shell,
  .header-left,
  .header-right {
    animation: none;
  }
}

@container app-header (max-width: 1600px) {
  .header-brand-zone {
    display: none;
  }
}

@media (max-width: 768px) {
  .sidebar {
    padding: 0;
  }

  .nav-menu {
    padding: 0 10px 12px;
  }

  .sidebar-brand-footer {
    min-height: 84px;
    padding: 14px 16px;
  }

  .sidebar-brand-surface {
    width: 160px;
    height: 56px;
  }

  .header {
    height: auto;
    min-height: 0;
    padding: 12px 12px 0;
  }

  .header-shell {
    align-items: stretch;
    flex-direction: column;
    gap: 12px;
    padding: 12px;
    border-radius: 18px;
  }

  .header-left,
  .header-right {
    width: 100%;
    justify-content: space-between;
    gap: 8px;
  }

  .username {
    display: none;
  }

  .main-content {
    padding: 144px 12px 12px;
  }

  :deep(.main-backtop.el-backtop) {
    right: 18px !important;
    bottom: 18px !important;
  }

  .sidebar-hidden {
    top: 84px;
    left: 12px;
    max-height: calc(100vh - 104px);
  }
}
</style>
