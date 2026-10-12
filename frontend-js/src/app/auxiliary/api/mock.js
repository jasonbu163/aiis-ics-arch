/**
 * 文件路径: /frontend-next-js/src/app/auxiliary/api/mock.js
 * 功能描述: auxiliary 前端 mock 诊断实现
 * 主要功能:
 *   - 在 VITE_FRONTEND_MOCK_ENABLED=true 时提供模块本地诊断数据
 *   - 与 /frontend-next-js/src/app/auxiliary/api/index.js 保持同名导出
 */
import {
  MOCK_LABEL,
  createMockMutation,
  createMockPage,
  createMockRecord,
  mockNow,
  mockToday
} from '@/api/mock/_diagnostic'

const makeShiftTeam = (apiName, index) => createMockRecord(apiName, index, {
  teamName: `${MOCK_LABEL}-TEAM-${index}`,
  leader: `${MOCK_LABEL}-LEADER-${index}`,
  members: 90 + index,
  phone: `1990000000${index}`,
  status: 'active'
})

const makeShift = (apiName, index) => createMockRecord(apiName, index, {
  date: mockToday(),
  dayTeamId: 900001,
  nightTeamId: 900002,
  dayLeader: `${MOCK_LABEL}-DAY-LEADER`,
  nightLeader: `${MOCK_LABEL}-NIGHT-LEADER`,
  shiftMode: 'two_shift'
})

const makeStopRecord = (apiName, index) => createMockRecord(apiName, index, {
  startTime: mockNow(),
  endTime: mockNow(),
  duration: 999 + index,
  shift: index === 1 ? 'dayShift' : 'nightShift',
  operator: `${MOCK_LABEL}-OPERATOR-${index}`,
  stopType: 'equipment',
  reason: `${MOCK_LABEL}-STOP-REASON`
})

const makePrice = (apiName, index) => createMockRecord(apiName, index, {
  electricPrice: 99.99 + index,
  hydrogenPrice: 88.88 + index,
  argonPrice: 77.77 + index,
  operator: `${MOCK_LABEL}-OPERATOR-${index}`
})

export async function getShiftTeamList(params) {
  const apiName = 'auxiliary.getShiftTeamList'
  return createMockPage(apiName, params, [makeShiftTeam(apiName, 1), makeShiftTeam(apiName, 2)])
}

export async function getShiftTeamById(id) {
  return makeShiftTeam('auxiliary.getShiftTeamById', Number(id) || 1)
}

export async function createShiftTeam(data) {
  return createMockMutation('auxiliary.createShiftTeam', data)
}

export async function updateShiftTeam(id, data) {
  return createMockMutation('auxiliary.updateShiftTeam', data, id)
}

export async function deleteShiftTeam(id) {
  return createMockMutation('auxiliary.deleteShiftTeam', {}, id)
}

export async function getShiftList(params) {
  const apiName = 'auxiliary.getShiftList'
  return createMockPage(apiName, params, [makeShift(apiName, 1), makeShift(apiName, 2)])
}

export async function getShiftById(id) {
  return makeShift('auxiliary.getShiftById', Number(id) || 1)
}

export async function createShift(data) {
  return createMockMutation('auxiliary.createShift', data)
}

export async function updateShift(id, data) {
  return createMockMutation('auxiliary.updateShift', data, id)
}

export async function deleteShift(id) {
  return createMockMutation('auxiliary.deleteShift', {}, id)
}

export async function getShiftRule() {
  return createMockRecord('auxiliary.getShiftRule', 1, {
    name: 'default',
    shiftMode: 'two_shift',
    cycleName: MOCK_LABEL,
    dayShiftStart: '08:00',
    dayShiftEnd: '20:00',
    middleShiftStart: '08:00',
    middleShiftEnd: '16:00',
    nightShiftStart: '20:00',
    nightShiftEnd: '08:00'
  })
}

export async function updateShiftRule(id, data) {
  return createMockMutation('auxiliary.updateShiftRule', data, id)
}

export async function getStopRecordList(params) {
  const apiName = 'auxiliary.getStopRecordList'
  return createMockPage(apiName, params, [makeStopRecord(apiName, 1), makeStopRecord(apiName, 2)])
}

export async function getStopRecordById(id) {
  return makeStopRecord('auxiliary.getStopRecordById', Number(id) || 1)
}

export async function createStopRecord(data) {
  return createMockMutation('auxiliary.createStopRecord', data)
}

export async function updateStopRecord(id, data) {
  return createMockMutation('auxiliary.updateStopRecord', data, id)
}

export async function deleteStopRecord(id) {
  return createMockMutation('auxiliary.deleteStopRecord', {}, id)
}

export async function getCurrentPrice() {
  return makePrice('auxiliary.getCurrentPrice', 1)
}

export async function getPriceList(params) {
  const apiName = 'auxiliary.getPriceList'
  return createMockPage(apiName, params, [makePrice(apiName, 1), makePrice(apiName, 2)])
}

export async function createPrice(data) {
  return createMockMutation('auxiliary.createPrice', data)
}
