/**
 * 文件路径: /frontend-next-js/src/app/equipment/api/index.js
 * 功能描述: 设备管理相关 API 接口封装
 * 主要功能:
 *   - 设备列表查询与详情获取
 *   - 设备创建/更新/删除
 *   - 维护记录管理
 */
import request from '@/utils/request'
import { callApi } from '@/api/mockMode'
import * as mockApi from './mock'
import { requireBusinessSource } from '@/utils/businessDataSource.mjs'

export async function getEquipmentList(params) {
  return callApi(() => mockApi.getEquipmentList(params), () => request.get('/equipments', { params }), 'equipment.getEquipmentList')
}

export async function getEquipmentById(id) {
  return callApi(() => mockApi.getEquipmentById(id), () => request.get(`/equipments/${id}`), 'equipment.getEquipmentById')
}

export async function createEquipment(data) {
  return callApi(() => mockApi.createEquipment(data), () => request.post('/equipments', data), 'equipment.createEquipment')
}

export async function updateEquipment(id, data) {
  return callApi(() => mockApi.updateEquipment(id, data), () => request.put(`/equipments/${id}`, data), 'equipment.updateEquipment')
}

export async function deleteEquipment(id) {
  return callApi(() => mockApi.deleteEquipment(id), () => request.delete(`/equipments/${id}`), 'equipment.deleteEquipment')
}

export async function getMaintenanceLogList(params) {
  return callApi(() => mockApi.getMaintenanceLogList(params), () => request.get('/maintenance-logs', { params }), 'equipment.getMaintenanceLogList')
}

export async function getMaintenanceLogById(id) {
  return callApi(() => mockApi.getMaintenanceLogById(id), () => request.get(`/maintenance-logs/${id}`), 'equipment.getMaintenanceLogById')
}

export async function createMaintenanceLog(data) {
  return callApi(() => mockApi.createMaintenanceLog(data), () => request.post('/maintenance-logs', data), 'equipment.createMaintenanceLog')
}

export async function updateMaintenanceLog(id, data) {
  return callApi(() => mockApi.updateMaintenanceLog(id, data), () => request.put(`/maintenance-logs/${id}`, data), 'equipment.updateMaintenanceLog')
}

export async function deleteMaintenanceLog(id) {
  return callApi(() => mockApi.deleteMaintenanceLog(id), () => request.delete(`/maintenance-logs/${id}`), 'equipment.deleteMaintenanceLog')
}

/**
 * 获取传动监控数据
 * @param {Object} params - 查询参数
 * @returns {Promise<Object>} 传动监控数据
 */
export async function getDriveData(params = {}) {
  const selected = requireBusinessSource(params)
  if (selected.dataSource === 'http') {
    const data = await request.get('/equipment/drive-samples', { params: { equipmentId: selected.equipmentId, recordId: params.recordId, limit: params.limit } })
    return data.dashboard
  }
  return callApi(() => mockApi.getDriveData(params), () => request.get('/equipment/drive', { params }), 'equipment.getDriveData')
}

/**
 * 获取温控监控数据
 * @param {Object} params - 查询参数
 * @returns {Promise<Object>} 温控监控数据
 */
export async function getTemperatureControlData(params = {}) {
  const selected = requireBusinessSource(params)
  if (selected.dataSource === 'http') {
    const data = await request.get('/equipment/temperature-sample-dashboard', { params: { equipmentId: selected.equipmentId, recordId: params.recordId, limit: params.limit } })
    return data
  }
  return callApi(() => mockApi.getTemperatureControlData(params), () => request.get('/equipment/temperature-control', { params }), 'equipment.getTemperatureControlData')
}

/**
 * 获取生产参数数据
 * @param {Object} params - 查询参数
 * @returns {Promise<Object>} 生产参数数据
 */
export async function getProductionParametersData(params = {}) {
  const selected = requireBusinessSource(params)
  if (selected.dataSource === 'http') {
    const data = await request.get('/equipment/production-parameter-samples', { params: { equipmentId: selected.equipmentId, recordId: params.recordId, limit: params.limit } })
    return data.dashboard
  }
  return callApi(
    () => mockApi.getProductionParametersData(params),
    () => request.get('/equipment/production-parameters', { params }),
    'equipment.getProductionParametersData'
  )
}
