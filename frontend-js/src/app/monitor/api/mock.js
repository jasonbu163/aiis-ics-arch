/**
 * 文件路径: /frontend-next-js/src/app/monitor/api/mock.js
 * 功能描述: monitor 前端 mock 诊断实现
 * 主要功能:
 *   - 在 VITE_FRONTEND_MOCK_ENABLED=true 时提供模块本地诊断数据
 *   - 与 /frontend-next-js/src/app/monitor/api/index.js 保持同名导出
 */
import {
  MOCK_LABEL,
  MOCK_SOURCE_TYPE,
  createMockMarker,
  mockNow
} from '@/api/mock/_diagnostic'

const createRealtimePayload = () => ({
  CoilNo: 'MOCK-HMI-COIL',
  CoilType: MOCK_LABEL,
  Width: 9999,
  Thickness: 99.99
})

export async function getTemperatureData() {
  const apiName = 'monitor.getTemperatureData'
  return {
    ...createMockMarker(apiName),
    times: ['08:00', '10:00', '12:00'],
    z1TempAct: [999, 998, 997],
    z1TempSet: [111, 111, 111],
    z2TempAct: [899, 898, 897],
    z2TempSet: [222, 222, 222],
    tension: [999, 888, 777],
    speed: [99, 88, 77],
    quality: [9, 8, 7]
  }
}

export async function getEnergyData() {
  const apiName = 'monitor.getEnergyData'
  return {
    ...createMockMarker(apiName),
    todayTotal: { elect: 99999, n2: 88888 },
    monthTotal: { elect: 999999, n2: 888888 },
    currentPower: 999,
    trends: [
      { time: 'MOCK-08:00', elect: 999, n2: 888 },
      { time: 'MOCK-12:00', elect: 888, n2: 777 }
    ]
  }
}

export async function getRealtimeLatest() {
  const apiName = 'monitor.getRealtimeLatest'
  const payload = createRealtimePayload()
  return {
    ...createMockMarker(apiName),
    updatedAt: mockNow(),
    payload,
    data: payload
  }
}

export async function getCollectorStatus() {
  const apiName = 'monitor.getCollectorStatus'
  return {
    ...createMockMarker(apiName),
    status: 'running',
    stale: false,
    lastSampleAt: mockNow()
  }
}

export async function getHmiRealtimeOverview() {
  const apiName = 'monitor.getHmiRealtimeOverview'
  return {
    ...createMockMarker(apiName),
    updatedAt: mockNow(),
    collector: {
      status: 'running',
      stale: false,
      lastSampleAt: mockNow(),
      sourceType: MOCK_SOURCE_TYPE
    },
    recipe: {
      coilNumber: 'MOCK-HMI-COIL',
      coilType: MOCK_LABEL,
      width: 9999,
      thickness: 99.99
    },
    payload: createRealtimePayload()
  }
}
