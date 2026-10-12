/**
 * 文件路径: /frontend-next-js/src/app/performance/api/mock/performance.js
 * 功能描述: performance 前端 mock 诊断实现
 * 主要功能:
 *   - 在 VITE_FRONTEND_MOCK_ENABLED=true 时提供模块本地诊断数据
 *   - 与 /frontend-next-js/src/app/performance/api/performance.js 保持同名导出
 */
import {
  createMockMarker,
  createMockMutation,
  createMockPage
} from '@/api/mock/_diagnostic'
import { makePerformanceRecord } from './_helpers'

export async function getPerformanceList(params) {
  const apiName = 'performance.getPerformanceList'
  return createMockPage(apiName, params, [makePerformanceRecord(apiName, 1), makePerformanceRecord(apiName, 2)])
}

export async function getPerformanceById(id) {
  return makePerformanceRecord('performance.getPerformanceById', Number(id) || 1)
}

export async function createPerformance(data) {
  return createMockMutation('performance.createPerformance', data)
}

export async function updatePerformance(id, data) {
  return createMockMutation('performance.updatePerformance', data, id)
}

export async function deletePerformance(id) {
  return createMockMutation('performance.deletePerformance', {}, id)
}

export async function getProcessData() {
  const apiName = 'performance.getProcessData'
  return {
    ...createMockMarker(apiName),
    temperature: [
      { zone: 'MOCK-Z1', maxTemp: 999, minTemp: 888, avgTemp: 944, duration: 99 },
      { zone: 'MOCK-Z2', maxTemp: 998, minTemp: 887, avgTemp: 943, duration: 98 }
    ],
    tension: [
      { zone: 'MOCK-ENTRY', setTension: 999, avgTension: 888, maxTension: 998, minTension: 777 },
      { zone: 'MOCK-EXIT', setTension: 999, avgTension: 887, maxTension: 997, minTension: 776 }
    ],
    speed: [
      { zone: 'MOCK-ENTRY', setSpeed: 999, avgSpeed: 888, maxSpeed: 998 },
      { zone: 'MOCK-EXIT', setSpeed: 999, avgSpeed: 887, maxSpeed: 997 }
    ]
  }
}
