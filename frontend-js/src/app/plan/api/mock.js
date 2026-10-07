/**
 * 文件路径: /frontend-next-js/src/app/plan/api/mock.js
 * 功能描述: plan 前端 mock 诊断实现
 * 主要功能:
 *   - 在 VITE_FRONTEND_MOCK_ENABLED=true 时提供模块本地诊断数据
 *   - 与 /frontend-next-js/src/app/plan/api/index.js 保持同名导出
 */
import {
  MOCK_LABEL,
  createMockMutation,
  createMockPage,
  createMockRecord
} from '@/api/mock/_diagnostic'

const makePlan = (apiName, index) => createMockRecord(apiName, index, {
  planNo: `MOCK-PLAN-${String(index).padStart(4, '0')}`,
  coilNo: `MOCK-COIL-${String(index).padStart(4, '0')}`,
  grade: MOCK_LABEL,
  materialStatus: 'ready',
  spec: '99.99 x 9999',
  weight: 999,
  thickness: 99.99,
  width: 9999,
  status: 'planned',
  priority: index
})

const createMockXlsxBlob = (apiName) => new Blob([`${MOCK_LABEL}:${apiName}`], {
  type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
})

export async function getPlanList(params) {
  const apiName = 'plan.getPlanList'
  return createMockPage(apiName, params, [makePlan(apiName, 1), makePlan(apiName, 2)])
}

export async function getPlanById(id) {
  return makePlan('plan.getPlanById', Number(id) || 1)
}

export async function createPlan(data) {
  return createMockMutation('plan.createPlan', data)
}

export async function updatePlan(id, data) {
  return createMockMutation('plan.updatePlan', data, id)
}

export async function deletePlan(id) {
  return createMockMutation('plan.deletePlan', {}, id)
}

export async function downloadPlanXlsxTemplate() {
  return createMockXlsxBlob('plan.downloadPlanXlsxTemplate')
}

export async function exportPlanXlsx(params) {
  return createMockXlsxBlob(`plan.exportPlanXlsx:${JSON.stringify(params || {})}`)
}

export async function importPlanXlsx(file, options = {}) {
  return {
    dryRun: options.dryRun !== false,
    valid: true,
    createdCount: options.dryRun === false ? 1 : 0,
    errorCount: 0,
    errors: [],
    mockLabel: MOCK_LABEL,
    fileName: file?.name || 'mock.xlsx'
  }
}

export async function getPlanLinkCandidates(performanceId) {
  const apiName = 'plan.getPlanLinkCandidates'
  const candidate = makePlan(apiName, Number(performanceId) || 1)
  return {
    performanceId,
    performanceCoilNo: candidate.coilNo,
    canonicalCoilNo: candidate.coilNo.toLowerCase(),
    candidateCount: 1,
    candidates: [candidate]
  }
}

export async function syncPlanObservation(performanceId) {
  return {
    performanceId,
    performanceCoilNo: `MOCK-COIL-${performanceId}`,
    canonicalCoilNo: `mock-coil-${performanceId}`,
    action: 'synced_observation',
    linked: true,
    planId: 900000 + Number(performanceId || 0),
    planStatus: 'observed',
    candidateCount: 1,
    mockLabel: MOCK_LABEL
  }
}

export async function linkPlanToPerformance(performanceId, planId) {
  return {
    performanceId,
    performanceCoilNo: `MOCK-COIL-${performanceId}`,
    canonicalCoilNo: `mock-coil-${performanceId}`,
    action: 'linked_existing_plan',
    linked: true,
    planId,
    planStatus: 'observed',
    candidateCount: 1,
    mockLabel: MOCK_LABEL
  }
}

export async function backfillPlanFromPerformance(performanceId, data) {
  return {
    performanceId,
    performanceCoilNo: data?.coilNo || `MOCK-COIL-${performanceId}`,
    canonicalCoilNo: String(data?.coilNo || `MOCK-COIL-${performanceId}`).toLowerCase(),
    action: 'backfilled_plan',
    linked: true,
    planId: 990000 + Number(performanceId || 0),
    planStatus: 'observed',
    candidateCount: 1,
    mockLabel: MOCK_LABEL
  }
}
