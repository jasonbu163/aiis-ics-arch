/**
 * 文件路径: /frontend-next-js/src/app/plan/api/index.js
 * 功能描述: 生产计划管理相关 API 接口封装
 * 主要功能:
 *   - 计划列表查询与详情获取
 *   - 计划创建/更新/删除
 */
import request from '@/utils/request'
import { callApi } from '@/api/mockMode'
import * as mockApi from './mock'

/**
 * 获取计划列表
 * @param {Object} params - 查询参数 { page, pageSize, coilNo, grade, status }
 */
export async function getPlanList(params) {
  return callApi(() => mockApi.getPlanList(params), () => request.get('/plans', { params }), 'plan.getPlanList')
}

const buildPlanExportQuery = (params = {}) => {
  const query = new URLSearchParams()
  const appendValue = (key, value) => {
    if (value === undefined || value === null || value === '') return
    query.append(key, value)
  }

  if (Array.isArray(params.planIds)) {
    params.planIds.forEach((id) => appendValue('planIds', id))
  }
  appendValue('coilNo', params.coilNo)
  appendValue('grade', params.grade)
  appendValue('materialStatus', params.materialStatus)
  appendValue('status', params.status)

  const queryString = query.toString()
  return queryString ? `?${queryString}` : ''
}

/**
 * 下载计划 XLSX 导入模板。
 */
export async function downloadPlanXlsxTemplate() {
  return callApi(
    () => mockApi.downloadPlanXlsxTemplate(),
    () => request.get('/plans/xlsx/template', { responseType: 'blob' }),
    'plan.downloadPlanXlsxTemplate'
  )
}

/**
 * 导出计划 XLSX。
 * @param {Object} params - { planIds, coilNo, grade, materialStatus, status }
 */
export async function exportPlanXlsx(params) {
  return callApi(
    () => mockApi.exportPlanXlsx(params),
    () => request.get(`/plans/xlsx/export${buildPlanExportQuery(params)}`, { responseType: 'blob' }),
    'plan.exportPlanXlsx'
  )
}

/**
 * 导入计划 XLSX。
 * @param {File} file - XLSX 文件
 * @param {Object} options - { dryRun, conflictStrategy }
 */
export async function importPlanXlsx(file, options = {}) {
  const dryRun = options.dryRun !== false
  const conflictStrategy = options.conflictStrategy || 'reject'
  const formData = new FormData()
  formData.append('file', file)

  return callApi(
    () => mockApi.importPlanXlsx(file, { dryRun, conflictStrategy }),
    () => request.post(
      `/plans/xlsx/import?dryRun=${dryRun ? 'true' : 'false'}&conflictStrategy=${encodeURIComponent(conflictStrategy)}`,
      formData
    ),
    'plan.importPlanXlsx'
  )
}

/**
 * 查询某条实绩可关联的计划候选。
 * @param {number} performanceId - 实绩 ID
 */
export async function getPlanLinkCandidates(performanceId) {
  return callApi(
    () => mockApi.getPlanLinkCandidates(performanceId),
    () => request.get(`/plans/linkage/performances/${performanceId}/candidates`),
    'plan.getPlanLinkCandidates'
  )
}

/**
 * 按实绩同步已有计划观察状态；后端不会自动创建计划。
 * @param {number} performanceId - 实绩 ID
 */
export async function syncPlanObservation(performanceId) {
  return callApi(
    () => mockApi.syncPlanObservation(performanceId),
    () => request.post(`/plans/linkage/performances/${performanceId}/sync-observation`),
    'plan.syncPlanObservation'
  )
}

/**
 * 手动把已有计划关联到实绩。
 * @param {number} performanceId - 实绩 ID
 * @param {number} planId - 计划 ID
 */
export async function linkPlanToPerformance(performanceId, planId) {
  return callApi(
    () => mockApi.linkPlanToPerformance(performanceId, planId),
    () => request.post(`/plans/linkage/performances/${performanceId}/link`, { planId }),
    'plan.linkPlanToPerformance'
  )
}

/**
 * 从未计划实绩回补计划并回链。
 * @param {number} performanceId - 实绩 ID
 * @param {Object} data - 计划创建数据
 */
export async function backfillPlanFromPerformance(performanceId, data) {
  return callApi(
    () => mockApi.backfillPlanFromPerformance(performanceId, data),
    () => request.post(`/plans/linkage/performances/${performanceId}/backfill`, data),
    'plan.backfillPlanFromPerformance'
  )
}

/**
 * 获取计划详情
 * @param {number} id - 计划 ID
 */
export async function getPlanById(id) {
  return callApi(() => mockApi.getPlanById(id), () => request.get(`/plans/${id}`), 'plan.getPlanById')
}

/**
 * 创建计划
 * @param {Object} data - 计划数据
 */
export async function createPlan(data) {
  return callApi(() => mockApi.createPlan(data), () => request.post('/plans', data), 'plan.createPlan')
}

/**
 * 更新计划
 * @param {number} id - 计划 ID
 * @param {Object} data - 更新数据
 */
export async function updatePlan(id, data) {
  return callApi(() => mockApi.updatePlan(id, data), () => request.put(`/plans/${id}`, data), 'plan.updatePlan')
}

/**
 * 删除计划
 * @param {number} id - 计划 ID
 */
export async function deletePlan(id) {
  return callApi(() => mockApi.deletePlan(id), () => request.delete(`/plans/${id}`), 'plan.deletePlan')
}
