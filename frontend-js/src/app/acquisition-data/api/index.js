/** 文件路径: /frontend-js/src/app/acquisition-data/api/index.js
 * 功能描述: 采集数据和来源管理接口，使用共享认证与响应解包。 */
import request from '@/utils/request'

const localErrors = { suppressErrorMessage: true }
export const getOptions = params => request.get('/acquisition-data/options', { ...localErrors, params })
export const getLatest = params => request.get('/acquisition-data/latest', { ...localErrors, params })
export const browseLatest = params => request.get('/acquisition-data/latest/browse', { ...localErrors, params })
export const getHistory = params => request.get('/acquisition-data/history', { ...localErrors, params })
export const getHistoryDetail = id => request.get(`/acquisition-data/history/${encodeURIComponent(id)}`, localErrors)
export const getSources = params => request.get('/admin/acquisition-sources', { ...localErrors, params })
export const createSource = body => request.post('/admin/acquisition-sources', body, localErrors)
export const updateSource = body => request.patch('/admin/acquisition-sources', body, localErrors)
