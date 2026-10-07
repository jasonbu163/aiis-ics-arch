/**
 * 文件路径: /frontend-next-js/src/app/dashboard/api/mock.js
 * 功能描述: dashboard 前端 mock 诊断实现
 * 主要功能:
 *   - 在 VITE_FRONTEND_MOCK_ENABLED=true 时提供模块本地诊断数据
 *   - 与 /frontend-next-js/src/app/dashboard/api/index.js 保持同名导出
 */
import {
  MOCK_LABEL,
  createMockMarker,
  createMockRecord
} from '@/api/mock/_diagnostic'

export async function getDashboardStats() {
  const apiName = 'dashboard.getDashboardStats'
  return {
    ...createMockMarker(apiName),
    todayProduction: 99999,
    pendingPlans: 999,
    completedCoils: 888,
    oee: 12.34,
    energyConsumption: 999999
  }
}

export async function getProductionTrend() {
  const apiName = 'dashboard.getProductionTrend'
  return {
    ...createMockMarker(apiName),
    days: ['MOCK-1', 'MOCK-2', 'MOCK-3'],
    actual: [999, 888, 777],
    target: [111, 111, 111]
  }
}

export async function getQualityDistribution() {
  const apiName = 'dashboard.getQualityDistribution'
  return {
    ...createMockMarker(apiName),
    grades: [
      { name: MOCK_LABEL, value: 999 },
      { name: 'NOT_REAL_API', value: 1 }
    ]
  }
}

export async function getOEEAnalysis() {
  const apiName = 'dashboard.getOEEAnalysis'
  return {
    ...createMockMarker(apiName),
    indicators: ['A', 'P', 'Q'],
    currentWeek: [12, 34, 56],
    lastWeek: [98, 76, 54]
  }
}

export async function getTemperatureTrend() {
  const apiName = 'dashboard.getTemperatureTrend'
  return {
    ...createMockMarker(apiName),
    zones: ['MOCK-Z1', 'MOCK-Z2'],
    hours: ['08:00', '12:00', '16:00'],
    data: [[999, 998, 997], [888, 887, 886]]
  }
}

export async function getEnergyConsumption() {
  const apiName = 'dashboard.getEnergyConsumption'
  return {
    ...createMockMarker(apiName),
    hours: ['08:00', '12:00', '16:00'],
    electricity: [999, 888, 777],
    gas: [666, 555, 444]
  }
}

export async function getDowntimeAnalysis() {
  const apiName = 'dashboard.getDowntimeAnalysis'
  return {
    ...createMockMarker(apiName),
    reasons: [MOCK_LABEL, 'NOT_REAL_API'],
    duration: [999, 1],
    colors: ['#ff4d4f', '#faad14']
  }
}

export async function getProductionStatus() {
  const apiName = 'dashboard.getProductionStatus'
  return {
    ...createMockMarker(apiName),
    onlineCoil: { id: 'MOCK-ONLINE-COIL', progress: 99, status: MOCK_LABEL },
    readyCoil: { id: 'MOCK-READY-COIL', grade: MOCK_LABEL, weight: 999 },
    currentSpeed: 999,
    furnaceTemp: 999
  }
}

export async function getRecentPlans() {
  const apiName = 'dashboard.getRecentPlans'
  const plans = [1, 2].map((index) => createMockRecord(apiName, index, {
    planNo: `MOCK-PLAN-${String(index).padStart(4, '0')}`,
    coilNo: `MOCK-COIL-${String(index).padStart(4, '0')}`,
    grade: MOCK_LABEL,
    status: 'planned'
  }))
  return { ...createMockMarker(apiName), plans }
}
