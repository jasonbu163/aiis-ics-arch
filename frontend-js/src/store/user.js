/**
 * 文件路径: /frontend-js/src/store/user.js
 * 功能描述: 用户认证状态管理，处理登录登出及用户信息
 * 主要功能:
 *   - 用户登录/登出状态管理
 *   - Token 持久化存储
 *   - 用户角色权限判断
 *   - 权限检查方法
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, logout as logoutApi } from '@/api/auth'
import { ROLE_PAGE_ACCESS } from '@/config/permissions'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')

  let parsedUserInfo = {}
  try {
    const info = localStorage.getItem('userInfo')
    if (info) {
      parsedUserInfo = JSON.parse(info)
    }
  } catch (error) {
    console.error('解析 userInfo 失败:', error)
    localStorage.removeItem('userInfo')
  }

  const userInfo = ref(parsedUserInfo)

  const username = computed(() => userInfo.value.username || '')
  // A missing or unknown role must not inherit operator page access.
  const role = computed(() => userInfo.value.role || '')
  const roleName = computed(() => {
    const roleMap = {
      admin: '系统管理员',
      supervisor: '班组长',
      operator: '操作员'
    }
    return roleMap[role.value] || '未知'
  })
  const isAdmin = computed(() => role.value === 'admin')
  const isLoggedIn = computed(() => !!token.value)

  const pageAccess = computed(() => {
    return ROLE_PAGE_ACCESS[role.value] || []
  })

  const hasPageAccess = (pageId) => {
    if (isAdmin.value) {
      return true
    }
    return pageAccess.value.includes(pageId)
  }

  const hasAnyPageAccess = (pageIds) => {
    if (isAdmin.value) {
      return true
    }
    return pageIds.some(pageId => pageAccess.value.includes(pageId))
  }

  const login = async (loginData) => {
    try {
      const response = await loginApi(loginData)
      const accessToken = response.accessToken || response.access_token
      const { user } = response

      token.value = accessToken
      userInfo.value = user

      localStorage.setItem('token', accessToken)
      localStorage.setItem('userInfo', JSON.stringify(user))

      console.log('登录成功，用户信息:', user)
      console.log('页面访问配置:', ROLE_PAGE_ACCESS[user.role] || [])

      return user
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    }
  }

  const setUserInfo = (nextUserInfo = {}) => {
    userInfo.value = {
      ...userInfo.value,
      ...nextUserInfo
    }
    localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
  }

  const clearSession = () => {
    token.value = ''
    userInfo.value = {}
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  const logout = async () => {
    try {
      await logoutApi()
    } catch (error) {
      console.error('登出失败:', error)
    } finally {
      clearSession()
    }
  }

  return {
    token,
    userInfo,
    username,
    role,
    roleName,
    isAdmin,
    isLoggedIn,
    pageAccess,
    hasPageAccess,
    hasAnyPageAccess,
    login,
    setUserInfo,
    clearSession,
    logout
  }
})
