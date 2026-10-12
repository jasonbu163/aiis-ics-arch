/**
 * 文件路径: /frontend-next-js/src/app/performance/api/mock/efficiency.js
 * 功能描述: efficiency 前端 mock 诊断实现
 * 主要功能:
 *   - 在 VITE_FRONTEND_MOCK_ENABLED=true 时提供模块本地诊断数据
 *   - 与 /frontend-next-js/src/app/performance/api/efficiency.js 保持同名导出
 */
import {
  MOCK_LABEL,
  createMockMarker,
  createMockPage
} from '@/api/mock/_diagnostic'
import { makeEfficiencyRecord } from './_helpers'

export async function getEfficiencyData(params) {
  const apiName = 'efficiency.getEfficiencyData'
  const page = createMockPage(apiName, params, [makeEfficiencyRecord(apiName, 1), makeEfficiencyRecord(apiName, 2)])
  return {
    ...page,
    downtimeAnalysis: [
      { reason: MOCK_LABEL, duration: 999 },
      { reason: 'NOT_REAL_API', duration: 1 }
    ]
  }
}

export async function getOEEData() {
  const apiName = 'efficiency.getOEEData'
  return {
    ...createMockMarker(apiName),
    availability: 99.9,
    performance: 88.8,
    quality: 77.7,
    plannedTime: 24,
    actualTime: 9.99,
    downtimeLoss: 8.88,
    theoreticalOutput: 999,
    actualOutput: 888,
    speedLoss: 111,
    totalOutput: 999,
    qualifiedOutput: 888,
    defectOutput: 111,
    trend: [
      { date: 'MOCK-1', oee: 99.9 },
      { date: 'MOCK-2', oee: 88.8 }
    ]
  }
}

export async function getEfficiencyOverview() {
  const apiName = 'efficiency.getEfficiencyOverview'
  return {
    ...createMockMarker(apiName),
    totalRunningTime: 999,
    runningTimeChange: 99.9,
    oee: 88.8,
    oeeChange: 77.7,
    processedCoils: 999,
    coilsChange: 66.6,
    downtime: 55.5,
    downtimeChange: -44.4
  }
}
