/**
 * 文件路径: /frontend-next-js/src/app/performance/api/print.js
 * 功能描述: 打印管理相关 API 接口封装
 * 主要功能:
 *   - 打印列表查询
 *   - 打印数据获取
 *   - 打印任务提交
 *   - 国际化 (i18n) 支持
 *   - 日夜模式 (Theme) 适配
 */
import request from '@/utils/request'
import { callApi } from '@/api/mockMode'
import * as mockApi from './mock'

export async function getPrintList(params) {
  return callApi(() => mockApi.getPrintList(params), () => request.get('/print/list', { params }), 'print.getPrintList')
}

export async function getPrintData(performanceId) {
  return callApi(() => mockApi.getPrintData(performanceId), () => request.get(`/print/data/${performanceId}`), 'print.getPrintData')
}

export async function submitPrint(performanceIds) {
  return callApi(() => mockApi.submitPrint(performanceIds), () => request.post('/print/submit', performanceIds), 'print.submitPrint')
}
