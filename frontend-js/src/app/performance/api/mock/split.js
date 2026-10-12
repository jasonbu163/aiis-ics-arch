/**
 * 文件路径: /frontend-next-js/src/app/performance/api/mock/split.js
 * 功能描述: split 前端 mock 诊断实现
 * 主要功能:
 *   - 在 VITE_FRONTEND_MOCK_ENABLED=true 时提供模块本地诊断数据
 *   - 与 /frontend-next-js/src/app/performance/api/split.js 保持同名导出
 */
import {
  createMockMarker,
  createMockMutation,
  createMockPage
} from '@/api/mock/_diagnostic'
import { makePerformanceRecord, makeSplitRecord } from './_helpers'

export async function getSplitList(params) {
  const apiName = 'split.getSplitList'
  return createMockPage(apiName, params, [makeSplitRecord(apiName, 1), makeSplitRecord(apiName, 2)])
}

export async function getParentCoils() {
  const apiName = 'split.getParentCoils'
  return createMockPage(apiName, {}, [makePerformanceRecord(apiName, 1), makePerformanceRecord(apiName, 2)])
}

export async function getSplitById(id) {
  return makeSplitRecord('split.getSplitById', Number(id) || 1)
}

export async function createSplit(data) {
  return createMockMutation('split.createSplit', data)
}

export async function updateSplit(id, data) {
  return createMockMutation('split.updateSplit', data, id)
}

export async function deleteSplit(id) {
  return createMockMutation('split.deleteSplit', {}, id)
}

export async function generateSplitNo(performanceId) {
  const apiName = 'split.generateSplitNo'
  return {
    ...createMockMarker(apiName),
    performanceId,
    splitNo: `MOCK-SPLIT-${performanceId}-1`
  }
}
