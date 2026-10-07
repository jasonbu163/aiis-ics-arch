/**
 * 文件路径: /frontend-next-js/src/app/dashboard/api/index.js
 * 功能描述: Dashboard 看板 API 接口封装
 * 主要功能:
 *   - 封装看板数据获取接口
 *   - 直接消费后端统一契约
 */
import request from '@/utils/request'
import { callApi } from '@/api/mockMode'
import * as mockApi from './mock'

const BASE_URL = '/dashboard'

// 获取统计数据
export const getDashboardStats = async () => {
  return callApi(() => mockApi.getDashboardStats(), () => request.get(`${BASE_URL}/stats`), 'dashboard.getDashboardStats')
}

// 获取产量趋势
export const getProductionTrend = async () => {
  return callApi(() => mockApi.getProductionTrend(), () => request.get(`${BASE_URL}/production-trend`), 'dashboard.getProductionTrend')
}

// 获取质量分布
export const getQualityDistribution = async () => {
  return callApi(() => mockApi.getQualityDistribution(), () => request.get(`${BASE_URL}/quality-distribution`), 'dashboard.getQualityDistribution')
}

// 获取 OEE 分析
export const getOEEAnalysis = async () => {
  return callApi(() => mockApi.getOEEAnalysis(), () => request.get(`${BASE_URL}/oee-analysis`), 'dashboard.getOEEAnalysis')
}

// 获取温度趋势
export const getTemperatureTrend = async () => {
  return callApi(() => mockApi.getTemperatureTrend(), () => request.get(`${BASE_URL}/temperature-trend`), 'dashboard.getTemperatureTrend')
}

// 获取能耗数据
export const getEnergyConsumption = async () => {
  return callApi(() => mockApi.getEnergyConsumption(), () => request.get(`${BASE_URL}/energy-consumption`), 'dashboard.getEnergyConsumption')
}

// 获取停机分析
export const getDowntimeAnalysis = async () => {
  return callApi(() => mockApi.getDowntimeAnalysis(), () => request.get(`${BASE_URL}/downtime-analysis`), 'dashboard.getDowntimeAnalysis')
}

// 获取生产状态
export const getProductionStatus = async () => {
  return callApi(() => mockApi.getProductionStatus(), () => request.get(`${BASE_URL}/production-status`), 'dashboard.getProductionStatus')
}

// 获取近期计划
export const getRecentPlans = async () => {
  return callApi(() => mockApi.getRecentPlans(), () => request.get(`${BASE_URL}/recent-plans`), 'dashboard.getRecentPlans')
}
