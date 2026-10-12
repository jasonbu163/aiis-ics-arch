/**
 * 文件路径: /frontend-next-js/src/app/performance/api/mock/_helpers.js
 * 功能描述: performance 模块本地 mock 数据构造器
 * 主要功能:
 *   - 生成实绩、分卷和效率模块诊断记录
 *   - 保持 performance 业务字段归属于本模块
 */
import {
  MOCK_LABEL,
  createMockRecord,
  mockNow,
  mockToday
} from '@/api/mock/_diagnostic'

export const makePerformanceRecord = (apiName, index) => createMockRecord(apiName, index, {
  coilNo: `MOCK-COIL-${String(index).padStart(4, '0')}`,
  parentCoilNo: `MOCK-PARENT-${String(index).padStart(4, '0')}`,
  grade: MOCK_LABEL,
  spec: '99.99 x 9999',
  weight: 999 + index,
  totalLength: 9999 + index,
  diameter: 999 + index,
  outerDiameter: 999 + index,
  density: 9.99,
  observationStatus: index === 1 ? 'in_production' : 'not_in_production',
  recordSource: index === 1 ? 'unplanned_plc' : 'manual_entry',
  planId: index === 1 ? null : 880000 + index,
  totalDurationSeconds: index === 1 ? 999 : 1999,
  totalDurationSource: index === 1 ? 'plc_observed' : 'manual_time',
  isSplit: false,
  operator: `${MOCK_LABEL}-OPERATOR-${index}`,
  shift: index === 1 ? 'dayShift' : 'nightShift',
  startTime: mockNow(),
  endTime: mockNow()
})

export const makeSplitRecord = (apiName, index) => createMockRecord(apiName, index, {
  performanceId: 900000 + index,
  splitNo: `MOCK-SPLIT-${String(index).padStart(4, '0')}`,
  performanceCoilNo: `MOCK-COIL-${String(index).padStart(4, '0')}`,
  coilNo: `MOCK-COIL-${String(index).padStart(4, '0')}`,
  spec: '99.99 x 9999',
  weight: 499 + index,
  grade: MOCK_LABEL
})

export const makeEfficiencyRecord = (apiName, index) => createMockRecord(apiName, index, {
  date: mockToday(),
  shift: index === 1 ? 'dayShift' : 'nightShift',
  plannedTime: 24,
  runningTime: 9.99,
  downtime: 8.88,
  processedCoils: 99 + index,
  oee: 88.88
})
