/**
 * 文件路径: /frontend-next-js/src/app/quality/api/index.js
 * 功能描述: 质量管理相关 API 接口封装
 * 主要功能:
 *   - 任务质量结果查询、人工创建和编辑
 *   - 本地质量字段管理
 *   - SPC 统计分析数据获取
 */
import axios from 'axios'
import request from '@/utils/request'
import { callApi } from '@/api/mockMode'
import API_CONFIG from '@/config/api'
import * as mockApi from './mock'

export async function getSPCData(params) {
  return callApi(() => mockApi.getSPCData(params), () => request.get('/quality/spc/data', { params }), 'quality.getSPCData')
}

export async function getSPCStats(params) {
  return callApi(() => mockApi.getSPCStats(params), () => request.get('/quality/spc/stats', { params }), 'quality.getSPCStats')
}

const qualityResultOptions = { suppressErrorMessage: true }

export const listQualityResults = params => callApi(
  () => mockApi.listQualityResults(params),
  () => request.get('/quality/results', { ...qualityResultOptions, params }),
  'quality.listQualityResults'
)
export const getQualityResult = taskNo => callApi(
  () => mockApi.getQualityResult(taskNo),
  () => request.get(`/quality/results/by-task/${encodeURIComponent(taskNo)}`, qualityResultOptions),
  'quality.getQualityResult'
)

// 新增失败时保留弹窗草稿，由页面处理 401。每次提交均读取当前登录凭据。
async function postQualityResult(body) {
  const token = localStorage.getItem('token')
  const { data: envelope } = await axios.post('/quality/results', body, {
    baseURL: API_CONFIG.BASE_URL,
    timeout: API_CONFIG.TIMEOUT,
    headers: token ? { Authorization: `Bearer ${token}` } : undefined
  })
  if (envelope?.code !== 200 || envelope.data?.outcome !== 'created') {
    throw new Error('Unexpected quality create response')
  }
  return envelope.data
}

export const createQualityResult = body => callApi(
  () => mockApi.createQualityResult(body),
  () => postQualityResult(body),
  'quality.createQualityResult'
)
export const saveQualityResult = body => callApi(
  () => mockApi.saveQualityResult(body),
  () => request.post('/quality/results/upsert', body, qualityResultOptions),
  'quality.saveQualityResult'
)
export const getQualityFieldConfig = () => callApi(
  () => mockApi.getQualityFieldConfig(),
  () => request.get('/quality/field-config', qualityResultOptions),
  'quality.getQualityFieldConfig'
)
export const saveQualityFieldConfig = body => callApi(
  () => mockApi.saveQualityFieldConfig(body),
  () => request.put('/quality/field-config', body, qualityResultOptions),
  'quality.saveQualityFieldConfig'
)
