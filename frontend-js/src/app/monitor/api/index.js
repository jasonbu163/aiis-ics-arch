/**
 * 文件路径: /frontend-next-js/src/app/monitor/api/index.js
 * 功能描述: 过程监控相关 API 接口封装
 * 主要功能:
 *   - 温度数据监控
 *   - 能耗数据监控
 *   - 实时采集 latest snapshot 与 collector 状态查询
 */
import request from '@/utils/request'
import { callApi } from '@/api/mockMode'
import * as mockApi from './mock'

/**
 * 获取温度监控数据
 * @param {Object} params - 查询参数
 * @returns {Promise<Object>} 温度监控数据
 */
export async function getTemperatureData(params) {
  return callApi(() => mockApi.getTemperatureData(params), () => request.get('/monitor/temperature', { params }), 'monitor.getTemperatureData')
}

/**
 * 获取能耗监控数据
 * @param {Object} params - 查询参数
 * @returns {Promise<Object>} 能耗监控数据
 */
export async function getEnergyData(params) {
  return callApi(() => mockApi.getEnergyData(params), () => request.get('/monitor/energy', { params }), 'monitor.getEnergyData')
}

/**
 * 获取实时采集 latest snapshot
 * @param {Object} params - 查询参数
 * @returns {Promise<Object>} 实时采集快照
 */
export async function getRealtimeLatest(params) {
  return callApi(() => mockApi.getRealtimeLatest(params), () => request.get('/monitor/realtime/latest', { params }), 'monitor.getRealtimeLatest')
}

/**
 * 获取采集器运行状态
 * @param {Object} params - 查询参数
 * @returns {Promise<Object>} 采集器状态
 */
export async function getCollectorStatus(params) {
  return callApi(() => mockApi.getCollectorStatus(params), () => request.get('/monitor/collector/status', { params }), 'monitor.getCollectorStatus')
}

/**
 * 获取 HMI P0.5 业务 API 实时总览
 * @param {Object} params - 查询参数
 * @returns {Promise<Object>} HMI 业务总览
 */
export async function getHmiRealtimeOverview(params) {
  return callApi(() => mockApi.getHmiRealtimeOverview(params), () => request.get('/monitor/hmi/realtime-overview', { params }), 'monitor.getHmiRealtimeOverview')
}
