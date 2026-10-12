/**
 * 文件路径: /frontend-next-js/src/app/performance/api/mock/print.js
 * 功能描述: print 前端 mock 诊断实现
 * 主要功能:
 *   - 在 VITE_FRONTEND_MOCK_ENABLED=true 时提供模块本地诊断数据
 *   - 与 /frontend-next-js/src/app/performance/api/print.js 保持同名导出
 */
import {
  createMockMutation,
  createMockPage
} from '@/api/mock/_diagnostic'
import { makePerformanceRecord } from './_helpers'

const makePrintRecord = (apiName, index) => ({
  ...makePerformanceRecord(apiName, index),
  thickness: 99.99,
  width: 9999,
  entryTension: 99.99,
  entryLoopTension: 88.88,
  furnaceTension: 77.77,
  exitLoopTension: 66.66,
  exitTension: 55.55,
  entrySpeed: 999,
  furnaceSpeed: 888,
  exitSpeed: 777,
  furnaceTemp: 999,
  residenceTime: 99,
  dewPoint: -99,
  oxygenContent: '999 ppm'
})

export async function getPrintList(params) {
  const apiName = 'print.getPrintList'
  return createMockPage(apiName, params, [makePrintRecord(apiName, 1), makePrintRecord(apiName, 2)])
}

export async function getPrintData(performanceId) {
  return makePrintRecord('print.getPrintData', Number(performanceId) || 1)
}

export async function submitPrint(performanceIds) {
  return createMockMutation('print.submitPrint', { performanceIds })
}
