/**
 * 文件路径: /frontend-next-js/src/app/performance/api/transform.js
 * 功能描述: 实绩 split / merge transform API facade
 * 主要功能:
 *   - 对接 B17 /performance-transforms split / merge 合同
 *   - 保留 BusinessException envelope 中的 errorCode 供页面本地化
 *   - 与模块内 mock 成对暴露，不让组件直接依赖 mock
 */
import axios from 'axios'
import API_CONFIG from '@/config/api'
import { callApi } from '@/api/mockMode'
import * as mockApi from './mock/transform'

const transformRequest = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT
})

transformRequest.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

const unwrapSuccessResponse = (response) => {
  const body = response?.data

  if (!body || typeof body !== 'object' || !Object.prototype.hasOwnProperty.call(body, 'code')) {
    return body
  }

  if (body.code === 200) {
    return body.data
  }

  const error = new Error(body.message || body.errorCode || 'performance_transform_failed')
  error.code = body.code
  error.errorCode = body.errorCode
  error.data = body.data
  throw error
}

export const requestPerformanceTransform = async (config) => {
  try {
    return unwrapSuccessResponse(await transformRequest(config))
  } catch (error) {
    if (error?.response?.data) {
      const body = error.response.data
      error.errorCode = body.errorCode || error.errorCode
      error.data = body.data || error.data
      error.message = body.message || error.message
    }
    throw error
  }
}

export const createSplitTransform = (data) => callApi(
  () => mockApi.createSplitTransform(data),
  () => requestPerformanceTransform({
    method: 'post',
    url: '/performance-transforms/split',
    data
  }),
  'performanceTransform.createSplitTransform'
)

export const createMergeTransform = (data) => callApi(
  () => mockApi.createMergeTransform(data),
  () => requestPerformanceTransform({
    method: 'post',
    url: '/performance-transforms/merge',
    data
  }),
  'performanceTransform.createMergeTransform'
)

export const getPerformanceTransform = (transformId) => callApi(
  () => mockApi.getPerformanceTransform(transformId),
  () => requestPerformanceTransform({
    method: 'get',
    url: `/performance-transforms/${transformId}`
  }),
  'performanceTransform.getPerformanceTransform'
)
