/**
 * 文件路径: /frontend-next-js/src/app/performance/api/efficiency.js
 * 功能描述: 效率统计相关 API 接口封装
 * 主要功能:
 *   - 效率数据查询
 *   - OEE 数据查询
 *   - 效率概览数据获取
 *   - 国际化 (i18n) 支持
 *   - 日夜模式 (Theme) 适配
 */
import request from '@/utils/request'
import { callApi } from '@/api/mockMode'
import * as mockApi from './mock'

export async function getEfficiencyData(params) {
  return callApi(() => mockApi.getEfficiencyData(params), () => request.get('/statistics/efficiency', { params }), 'efficiency.getEfficiencyData')
}

export async function getOEEData(params) {
  return callApi(() => mockApi.getOEEData(params), () => request.get('/statistics/oee', { params }), 'efficiency.getOEEData')
}

export async function getEfficiencyOverview(params) {
  return callApi(() => mockApi.getEfficiencyOverview(params), () => request.get('/statistics/overview', { params }), 'efficiency.getEfficiencyOverview')
}
