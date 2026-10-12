/**
 * 文件路径: /frontend-next-js/src/app/performance/api/mock/transform.js
 * 功能描述: F23 split / merge transform 前端诊断 mock
 * 主要功能:
 *   - 提供明显的 FRONTEND_MOCK_ONLY transform 响应
 *   - 保持 split / merge 响应字段与 B17 camelCase 合同一致
 *   - 不生成业务关系或自动 coil_no 规则
 */
import { createMockMarker, mockNow } from '@/api/mock/_diagnostic'

const makeLineageEntry = ({ transformId, performanceId, role, allocatedWeight }, index) => ({
  ...createMockMarker('performanceTransform.lineageEntry'),
  id: 920000 + index,
  transformId,
  performanceId,
  role,
  allocatedWeight,
  effectiveWeightSnapshot: allocatedWeight,
  effectiveWeightSourceSnapshot: role === 'source' ? 'collected_weight' : 'split_generated',
  availableWeightBeforeSnapshot: role === 'source' ? allocatedWeight + 20 : allocatedWeight,
  availableWeightAfterSnapshot: role === 'source' ? 20 : allocatedWeight,
  createdAt: mockNow()
})

const makeTransform = ({ transformType, reason, lineageEntries }) => {
  const transformId = Number(`${Date.now()}`.slice(-6))

  return {
    ...createMockMarker(`performanceTransform.${transformType}`),
    id: transformId,
    transformType,
    status: 'committed',
    quantityDimension: 'weight',
    requestedById: 900001,
    requestedReason: reason || '',
    confirmedById: 900001,
    confirmedAt: mockNow(),
    effectiveWeightContext: createMockMarker('performanceTransform.effectiveWeightContext'),
    createdAt: mockNow(),
    updatedAt: mockNow(),
    lineageEntries: lineageEntries.map((entry, index) => makeLineageEntry({ transformId, ...entry }, index + 1))
  }
}

export const createSplitTransform = async (data = {}) => makeTransform({
  transformType: 'split',
  reason: data.reason,
  lineageEntries: [
    {
      performanceId: data.sourcePerformanceId,
      role: 'source',
      allocatedWeight: data.targets?.reduce((total, item) => total + Number(item.allocatedWeight || 0), 0) || 0
    },
    ...(data.targets || []).map((target, index) => ({
      performanceId: target.targetPerformanceId || 930000 + index,
      role: 'target',
      allocatedWeight: Number(target.allocatedWeight || 0)
    }))
  ]
})

export const createMergeTransform = async (data = {}) => makeTransform({
  transformType: 'merge',
  reason: data.reason,
  lineageEntries: [
    ...(data.sources || []).map((source) => ({
      performanceId: source.performanceId,
      role: 'source',
      allocatedWeight: Number(source.allocatedWeight || 0)
    })),
    {
      performanceId: data.target?.targetPerformanceId || 940000,
      role: 'target',
      allocatedWeight: (data.sources || []).reduce((total, item) => total + Number(item.allocatedWeight || 0), 0)
    }
  ]
})

export const getPerformanceTransform = async (transformId) => ({
  ...createMockMarker('performanceTransform.getPerformanceTransform'),
  id: Number(transformId),
  transformType: 'split',
  status: 'committed',
  quantityDimension: 'weight',
  requestedById: 900001,
  requestedReason: '',
  confirmedById: 900001,
  confirmedAt: mockNow(),
  effectiveWeightContext: createMockMarker('performanceTransform.effectiveWeightContext'),
  createdAt: mockNow(),
  updatedAt: mockNow(),
  lineageEntries: []
})
