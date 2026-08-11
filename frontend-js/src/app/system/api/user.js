/**
 * 文件路径: /frontend-js/src/app/system/api/user.js
 * 功能描述: 用户管理相关 API 接口封装
 * 主要功能:
 *   - 用户列表查询
 *   - 用户详情获取
 *   - 用户创建/更新/删除
 *   - 直接消费后端统一契约
 */
import axios from 'axios'
import API_CONFIG from '@/config/api'
import { callApi } from '@/api/mockMode'
import * as mockApi from './mock'

const systemUserRequest = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT
})

systemUserRequest.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

const unwrapUserResponse = (response) => {
  const body = response?.data

  if (!body || typeof body !== 'object' || !Object.prototype.hasOwnProperty.call(body, 'code')) {
    return body
  }

  if (body.code === 200) {
    return body.data
  }

  const error = new Error(body.message || body.errorCode || 'system_user_request_failed')
  error.code = body.code
  error.errorCode = body.errorCode
  error.data = body.data
  throw error
}

const requestUserContract = async (config) => {
  try {
    return unwrapUserResponse(await systemUserRequest(config))
  } catch (error) {
    if (error?.response?.data) {
      const body = error.response.data
      error.code = body.code || error.response.status || error.code
      error.errorCode = body.errorCode || error.error_code || error.errorCode
      error.data = body.data || error.data
      error.message = body.message || body.detail || error.message
    }
    if (error?.response?.status === 401 || error?.code === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      window.location.href = '/login'
    }
    throw error
  }
}

/**
 * 获取用户列表
 * @param {Object} params - 查询参数 { page, page_size, username, role }
 */
export async function getUserList(params) {
  return callApi(
    () => mockApi.getUserList(params),
    () => requestUserContract({ method: 'get', url: '/users', params }),
    'user.getUserList'
  )
}

/**
 * 获取用户详情
 * @param {number} id - 用户 ID
 */
export async function getUserById(id) {
  return callApi(
    () => mockApi.getUserById(id),
    () => requestUserContract({ method: 'get', url: `/users/${id}` }),
    'user.getUserById'
  )
}

/**
 * 创建用户
 * @param {Object} data - 用户数据 { username, name, password, role, phone, email }
 */
export async function createUser(data) {
  return callApi(
    () => mockApi.createUser(data),
    () => requestUserContract({ method: 'post', url: '/users', data }),
    'user.createUser'
  )
}

/**
 * 更新用户
 * @param {number} id - 用户 ID
 * @param {Object} data - 更新数据 { name, role, phone, email }
 */
export async function updateUser(id, data) {
  return callApi(
    () => mockApi.updateUser(id, data),
    () => requestUserContract({ method: 'put', url: `/users/${id}`, data }),
    'user.updateUser'
  )
}

/**
 * 重置目标用户密码
 * @param {number} id - 用户 ID
 * @param {Object} data - { newPassword }
 */
export async function resetUserPassword(id, data) {
  return callApi(
    () => mockApi.resetUserPassword(id, data),
    () => requestUserContract({ method: 'patch', url: `/users/${id}/password`, data }),
    'user.resetUserPassword'
  )
}

/**
 * 删除用户
 * @param {number} id - 用户 ID
 */
export async function deleteUser(id) {
  return callApi(
    () => mockApi.deleteUser(id),
    () => requestUserContract({ method: 'delete', url: `/users/${id}` }),
    'user.deleteUser'
  )
}
