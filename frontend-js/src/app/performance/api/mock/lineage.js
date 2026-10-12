/**
 * 文件路径: /frontend-next-js/src/app/performance/api/mock/lineage.js
 * 功能描述: F23 lineage API 前端诊断 mock
 * 主要功能:
 *   - 提供明显的 FRONTEND_MOCK_ONLY lineage summary
 *   - 与真实 B17 API facade 同名成对
 *   - 不作为业务验收依据
 */
import { createMockMarker, createMockMutation, mockNow } from '@/api/mock/_diagnostic'

const numericId = (id) => {
  const value = Number(id)
  return Number.isFinite(value) ? value : 900001
}

export const getPerformanceLineageSummary = async (performanceId) => {
  const id = numericId(performanceId)

  return {
    ...createMockMarker('performanceLineage.getPerformanceLineageSummary'),
    performanceId: id,
    effectiveWeight: 120 + (id % 5) * 10,
    effectiveWeightSource: id % 2 === 0 ? 'manual_override_weight' : 'collected_weight',
    committedSourceAllocatedWeight: id % 3 === 0 ? 20 : 0,
    availableWeight: 100 + (id % 5) * 10,
    updatedAt: mockNow()
  }
}

export const overridePerformanceEffectiveWeight = async (performanceId, data = {}) => createMockMutation(
  'performanceLineage.overridePerformanceEffectiveWeight',
  {
    performanceId: numericId(performanceId),
    effectiveWeight: data.effectiveWeight,
    reason: data.reason,
    effectiveWeightSource: 'manual_override_weight'
  },
  numericId(performanceId)
)
