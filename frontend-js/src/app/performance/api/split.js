/**
 * 文件路径: /frontend-next-js/src/app/performance/api/split.js
 * 功能描述: 分卷管理相关 API 接口封装
 * 主要功能:
 *   - 分卷列表查询与详情获取
 *   - 可分卷母卷列表获取
 *   - 分卷创建/更新/删除
 *   - 自动生成分卷号
 *   - 国际化 (i18n) 支持
 *   - 日夜模式 (Theme) 适配
 */
import request from '@/utils/request'
import { callApi } from '@/api/mockMode'
import * as mockApi from './mock'

/**
 * 获取分卷列表
 * @param {Object} params - 查询参数
 */
export async function getSplitList(params) {
  return callApi(() => mockApi.getSplitList(params), () => request.get('/splits', { params }), 'split.getSplitList')
}

/**
 * 获取可分卷的母卷列表
 */
export async function getParentCoils() {
  return callApi(() => mockApi.getParentCoils(), () => request.get('/splits/parent-coils'), 'split.getParentCoils')
}

/**
 * 获取分卷详情
 * @param {number} id - 分卷 ID
 */
export async function getSplitById(id) {
  return callApi(() => mockApi.getSplitById(id), () => request.get(`/splits/${id}`), 'split.getSplitById')
}

/**
 * 创建分卷
 * @param {Object} data - 分卷数据
 */
export async function createSplit(data) {
  return callApi(() => mockApi.createSplit(data), () => request.post('/splits', data), 'split.createSplit')
}

/**
 * 更新分卷
 * @param {number} id - 分卷 ID
 * @param {Object} data - 分卷数据
 */
export async function updateSplit(id, data) {
  return callApi(() => mockApi.updateSplit(id, data), () => request.put(`/splits/${id}`, data), 'split.updateSplit')
}

/**
 * 删除分卷
 * @param {number} id - 分卷 ID
 */
export async function deleteSplit(id) {
  return callApi(() => mockApi.deleteSplit(id), () => request.delete(`/splits/${id}`), 'split.deleteSplit')
}

/**
 * 自动生成分卷号
 * @param {number} performanceId - 实绩 ID
 */
export async function generateSplitNo(performanceId) {
  return callApi(() => mockApi.generateSplitNo(performanceId), () => request.get(`/splits/${performanceId}/generate-split-no`), 'split.generateSplitNo')
}
