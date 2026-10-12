/**
 * 文件路径: /frontend-next-js/src/app/maintenance/api/index.js
 * 功能描述: 维保管理相关 API 接口封装
 * 主要功能:
 *   - 维保项目列表查询与详情获取
 *   - 维保记录管理
 *   - 直接消费后端统一契约
 */
import request from '@/utils/request'
import { callApi } from '@/api/mockMode'
import * as mockApi from './mock'

/**
 * 获取维保项目列表
 */
export async function getMaintenanceItems(params) {
  return callApi(() => mockApi.getMaintenanceItems(params), () => request.get('/items', { params }), 'maintenance.getMaintenanceItems')
}

/**
 * 获取维保日志列表
 */
export async function getMaintenanceLogList(params) {
  return callApi(() => mockApi.getMaintenanceLogList(params), () => request.get('/maintenance-logs', { params }), 'maintenance.getMaintenanceLogList')
}

/**
 * 创建维保日志
 */
export async function createMaintenanceLog(data) {
  return callApi(() => mockApi.createMaintenanceLog(data), () => request.post('/maintenance-logs', data), 'maintenance.createMaintenanceLog')
}

/**
 * 更新维保日志
 */
export async function updateMaintenanceLog(id, data) {
  return callApi(() => mockApi.updateMaintenanceLog(id, data), () => request.put(`/maintenance-logs/${id}`, data), 'maintenance.updateMaintenanceLog')
}

/**
 * 删除维保日志
 */
export async function deleteMaintenanceLog(id) {
  return callApi(() => mockApi.deleteMaintenanceLog(id), () => request.delete(`/maintenance-logs/${id}`), 'maintenance.deleteMaintenanceLog')
}
