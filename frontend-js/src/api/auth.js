/**
 * 文件路径: /frontend-js/src/api/auth.js
 * 功能描述: 用户认证相关 API 接口封装
 * 主要功能:
 *   - 用户登录/登出
 *   - 获取当前用户信息
 *   - Token 刷新
 */
import axios from 'axios'
import API_CONFIG from '@/config/api'
import { callApi } from './mockMode'
import * as mockApi from './mock/auth'

const authRequest = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT
})

const isLoginRequest = (config) => config?.url?.split('?')[0]?.endsWith('/auth/login')

authRequest.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

const unwrapAuthResponse = (response) => {
  const body = response?.data

  if (!body || typeof body !== 'object' || !Object.prototype.hasOwnProperty.call(body, 'code')) {
    return body
  }

  if (body.code === 200) {
    return body.data
  }

  const error = new Error(body.message || body.errorCode || 'auth_request_failed')
  error.code = body.code
  error.errorCode = body.errorCode
  error.data = body.data
  throw error
}

const requestAuthContract = async (config) => {
  try {
    return unwrapAuthResponse(await authRequest(config))
  } catch (error) {
    if (error?.response?.data) {
      const body = error.response.data
      error.code = body.code || error.response.status || error.code
      error.errorCode = body.errorCode || error.error_code || error.errorCode
      error.data = body.data || error.data
      error.message = body.message || body.detail || error.message
    }
    if ((error?.response?.status === 401 || error?.code === 401) && !isLoginRequest(config)) {
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      window.location.href = '/login'
    }
    throw error
  }
}

/**
 * 用户登录
 * @param {Object} data - 登录信息 { username, password }
 */
export async function login(data) {
  return callApi(
    () => mockApi.login(data),
    () => requestAuthContract({ method: 'post', url: '/auth/login', data }),
    'auth.login'
  )
}

/**
 * 用户登出
 */
export async function logout() {
  return callApi(
    () => mockApi.logout(),
    () => requestAuthContract({ method: 'post', url: '/auth/logout' }),
    'auth.logout'
  )
}

/**
 * 获取当前用户信息
 */
export async function getCurrentUser() {
  return callApi(
    () => mockApi.getCurrentUser(),
    () => requestAuthContract({ method: 'get', url: '/auth/me' }),
    'auth.getCurrentUser'
  )
}

/**
 * 更新当前用户资料
 * @param {Object} data - { name, phone, email }
 */
export async function updateCurrentUserProfile(data) {
  return callApi(
    () => mockApi.updateCurrentUserProfile(data),
    () => requestAuthContract({ method: 'patch', url: '/auth/me', data }),
    'auth.updateCurrentUserProfile'
  )
}

/**
 * 当前用户修改密码
 * @param {Object} data - { oldPassword, newPassword }
 */
export async function changeCurrentUserPassword(data) {
  return callApi(
    () => mockApi.changeCurrentUserPassword(data),
    () => requestAuthContract({ method: 'patch', url: '/auth/me/password', data }),
    'auth.changeCurrentUserPassword'
  )
}

/**
 * 刷新 Token
 * @param {Object} data - { refresh_token }
 */
export async function refreshToken(data) {
  return callApi(
    () => mockApi.refreshToken(data),
    () => requestAuthContract({ method: 'post', url: '/auth/refresh', data }),
    'auth.refreshToken'
  )
}
