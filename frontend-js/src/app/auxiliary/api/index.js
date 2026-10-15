/**
 * 文件路径: /frontend-next-js/src/app/auxiliary/api/index.js
 * 功能描述: 辅助管理相关 API 接口封装
 * 主要功能:
 *   - 班组管理 CRUD
 *   - 班次管理 CRUD
 *   - 排班规则维护
 *   - 停机记录管理
 *   - 能耗单价维护
 */
import request from '@/utils/request'
import { callApi } from '@/api/mockMode'
import * as mockApi from './mock'

export async function getShiftTeamList(params) {
  return callApi(() => mockApi.getShiftTeamList(params), () => request.get('/shift-teams', { params }), 'auxiliary.getShiftTeamList')
}

export async function getShiftTeamById(id) {
  return callApi(() => mockApi.getShiftTeamById(id), () => request.get(`/shift-teams/${id}`), 'auxiliary.getShiftTeamById')
}

export async function createShiftTeam(data) {
  return callApi(() => mockApi.createShiftTeam(data), () => request.post('/shift-teams', data), 'auxiliary.createShiftTeam')
}

export async function updateShiftTeam(id, data) {
  return callApi(() => mockApi.updateShiftTeam(id, data), () => request.put(`/shift-teams/${id}`, data), 'auxiliary.updateShiftTeam')
}

export async function deleteShiftTeam(id) {
  return callApi(() => mockApi.deleteShiftTeam(id), () => request.delete(`/shift-teams/${id}`), 'auxiliary.deleteShiftTeam')
}

export async function getShiftList(params) {
  return callApi(() => mockApi.getShiftList(params), () => request.get('/shifts', { params }), 'auxiliary.getShiftList')
}

export async function getShiftById(id) {
  return callApi(() => mockApi.getShiftById(id), () => request.get(`/shifts/${id}`), 'auxiliary.getShiftById')
}

export async function createShift(data) {
  return callApi(() => mockApi.createShift(data), () => request.post('/shifts', data), 'auxiliary.createShift')
}

export async function updateShift(id, data) {
  return callApi(() => mockApi.updateShift(id, data), () => request.put(`/shifts/${id}`, data), 'auxiliary.updateShift')
}

export async function deleteShift(id) {
  return callApi(() => mockApi.deleteShift(id), () => request.delete(`/shifts/${id}`), 'auxiliary.deleteShift')
}

export async function getShiftRule() {
  return callApi(() => mockApi.getShiftRule(), () => request.get('/shift-rules'), 'auxiliary.getShiftRule')
}

export async function updateShiftRule(id, data) {
  return callApi(() => mockApi.updateShiftRule(id, data), () => request.put(`/shift-rules/${id}`, data), 'auxiliary.updateShiftRule')
}

export async function getStopRecordList(params) {
  return callApi(() => mockApi.getStopRecordList(params), () => request.get('/stop-records', { params }), 'auxiliary.getStopRecordList')
}

export async function getStopRecordById(id) {
  return callApi(() => mockApi.getStopRecordById(id), () => request.get(`/stop-records/${id}`), 'auxiliary.getStopRecordById')
}

export async function createStopRecord(data) {
  return callApi(() => mockApi.createStopRecord(data), () => request.post('/stop-records', data), 'auxiliary.createStopRecord')
}

export async function updateStopRecord(id, data) {
  return callApi(() => mockApi.updateStopRecord(id, data), () => request.put(`/stop-records/${id}`, data), 'auxiliary.updateStopRecord')
}

export async function deleteStopRecord(id) {
  return callApi(() => mockApi.deleteStopRecord(id), () => request.delete(`/stop-records/${id}`), 'auxiliary.deleteStopRecord')
}

export async function getCurrentPrice() {
  return callApi(() => mockApi.getCurrentPrice(), () => request.get('/energy/current'), 'auxiliary.getCurrentPrice')
}

// date selects a Shanghai business day; page/pageSize keep the existing response contract.
export async function getPriceList(params) {
  return callApi(() => mockApi.getPriceList(params), () => request.get('/energy', { params }), 'auxiliary.getPriceList')
}

export async function createPrice(data) {
  return callApi(() => mockApi.createPrice(data), () => request.post('/energy', data), 'auxiliary.createPrice')
}
