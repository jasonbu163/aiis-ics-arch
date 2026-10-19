/**
 * 文件路径: /frontend-next-js/src/app/performance/api/performance.js
 * 功能描述: 实绩管理相关 API 接口封装
 * 主要功能:
 *   - 获取实绩列表（支持分页、筛选）
 *   - 获取单个实绩详情
 *   - 创建/更新/删除实绩记录
 *   - 实绩数据统计
 *   - 国际化 (i18n) 支持
 *   - 日夜模式 (Theme) 适配
 */
import request from '@/utils/request'
import { callApi } from '@/api/mockMode'
import * as mockApi from './mock'
import { requireBusinessSource } from '@/utils/businessDataSource.mjs'

export async function getPerformanceList(params = {}) {
  const selected = requireBusinessSource(params)
  if (selected.dataSource === 'http') {
    const { dataSource, valid, ready, ...query } = params
    return request.get('/performances/mapping-records', { params: query })
  }
  return callApi(() => mockApi.getPerformanceList(params), () => request.get('/performances', { params }), 'performance.getPerformanceList')
}

export async function getPerformanceById(id, selection = {}) {
  const selected = requireBusinessSource(selection)
  if (selected.dataSource === 'http') return request.get(`/performances/mapping-records/${id}`, { params: { equipmentId: selected.equipmentId } })
  return callApi(() => mockApi.getPerformanceById(id), () => request.get(`/performances/${id}`), 'performance.getPerformanceById')
}

export async function createPerformance(data) {
  return callApi(() => mockApi.createPerformance(data), () => request.post('/performances', data), 'performance.createPerformance')
}

export async function updatePerformance(id, data, selection = {}) {
  const selected = requireBusinessSource(selection)
  if (selected.dataSource === 'http') return request.put(`/performances/${id}`, data, { params: { dataSource: 'http', equipmentId: selected.equipmentId } })
  return callApi(() => mockApi.updatePerformance(id, data), () => request.put(`/performances/${id}`, data), 'performance.updatePerformance')
}

export async function deletePerformance(id) {
  return callApi(() => mockApi.deletePerformance(id), () => request.delete(`/performances/${id}`), 'performance.deletePerformance')
}

export async function getProcessData(id, selection = {}) {
  const selected = requireBusinessSource(selection)
  if (selected.dataSource === 'http') return request.get(`/performances/mapping-records/${id}/process-data`, { params: { equipmentId: selected.equipmentId } })
  return callApi(() => mockApi.getProcessData(id), () => request.get(`/performances/${id}/process-data`), 'performance.getProcessData')
}
