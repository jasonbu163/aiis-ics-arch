/**
 * 文件路径: /frontend-js/src/api/mock/auth.js
 * 功能描述: auth 前端 mock 诊断实现
 * 主要功能:
 *   - 在 VITE_FRONTEND_MOCK_ENABLED=true 时提供明显的前端 mock 数据
 *   - 与 /frontend-js/src/api/auth.js 保持同名导出
 */
import {
  MOCK_LABEL,
  MOCK_SOURCE_TYPE,
  createMockMarker,
  createMockMutation
} from './_diagnostic'

export async function login(data = {}) {
  const apiName = 'auth.login'
  return {
    ...createMockMarker(apiName),
    accessToken: 'FRONTEND_MOCK_ACCESS_TOKEN',
    refreshToken: 'FRONTEND_MOCK_REFRESH_TOKEN',
    user: {
      id: 900001,
      username: data.username || 'frontend_mock_admin',
      name: MOCK_LABEL,
      role: 'admin',
      sourceType: MOCK_SOURCE_TYPE
    }
  }
}

export async function logout() {
  return createMockMutation('auth.logout')
}

export async function getCurrentUser() {
  const apiName = 'auth.getCurrentUser'
  return {
    ...createMockMarker(apiName),
    id: 900001,
    username: 'frontend_mock_admin',
    name: MOCK_LABEL,
    role: 'admin',
    phone: '19900000001',
    email: 'frontend-mock-admin@example.invalid',
    status: 'active',
    isActive: true
  }
}

export async function updateCurrentUserProfile(data = {}) {
  const apiName = 'auth.updateCurrentUserProfile'
  return {
    ...createMockMarker(apiName),
    id: 900001,
    username: 'frontend_mock_admin',
    name: data.name || MOCK_LABEL,
    role: 'admin',
    phone: data.phone || '',
    email: data.email || '',
    status: 'active',
    isActive: true
  }
}

export async function changeCurrentUserPassword() {
  return {
    ...createMockMutation('auth.changeCurrentUserPassword'),
    requiresRelogin: true
  }
}

export async function refreshToken() {
  const apiName = 'auth.refreshToken'
  return {
    ...createMockMarker(apiName),
    accessToken: 'FRONTEND_MOCK_ACCESS_TOKEN_REFRESHED'
  }
}
