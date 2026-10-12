/**
 * 文件路径: /frontend-next-js/src/app/quality/api/index.js
 * 功能描述: 质量管理相关 API 接口封装
 * 主要功能:
 *   - 质量检验列表查询与详情获取
 *   - 质量检验创建/更新/删除
 *   - 缺陷记录管理
 *   - SPC 统计分析数据获取
 */
import request from '@/utils/request'
import { callApi } from '@/api/mockMode'
import * as mockApi from './mock'

export async function getQualityList(params) {
  return callApi(() => mockApi.getQualityList(params), () => request.get('/quality', { params }), 'quality.getQualityList')
}

export async function getQualityById(id) {
  return callApi(() => mockApi.getQualityById(id), () => request.get(`/quality/${id}`), 'quality.getQualityById')
}

export async function createQuality(data) {
  return callApi(() => mockApi.createQuality(data), () => request.post('/quality', data), 'quality.createQuality')
}

export async function updateQuality(id, data) {
  return callApi(() => mockApi.updateQuality(id, data), () => request.put(`/quality/${id}`, data), 'quality.updateQuality')
}

export async function deleteQuality(id) {
  return callApi(() => mockApi.deleteQuality(id), () => request.delete(`/quality/${id}`), 'quality.deleteQuality')
}

export async function addDefect(qualityId, data) {
  return callApi(() => mockApi.addDefect(qualityId, data), () => request.post(`/quality/${qualityId}/defects`, data), 'quality.addDefect')
}

export async function deleteDefect(qualityId, defectId) {
  return callApi(() => mockApi.deleteDefect(qualityId, defectId), () => request.delete(`/quality/${qualityId}/defects/${defectId}`), 'quality.deleteDefect')
}

export async function getSPCData(params) {
  return callApi(() => mockApi.getSPCData(params), () => request.get('/quality/spc/data', { params }), 'quality.getSPCData')
}

export async function getSPCStats(params) {
  return callApi(() => mockApi.getSPCStats(params), () => request.get('/quality/spc/stats', { params }), 'quality.getSPCStats')
}
