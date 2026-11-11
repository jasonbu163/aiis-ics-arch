/** 文件路径: /frontend-js/src/app/acquisition-data/api/index.js
 * 功能描述: 采集数据只读接口，使用共享认证与响应解包。 */
import request from '@/utils/request'

const localErrors = { suppressErrorMessage: true }
export const getOptions = () => request.get('/acquisition-data/options', localErrors)
export const getLatest = params => request.get('/acquisition-data/latest', { ...localErrors, params })
export const browseLatest = params => request.get('/acquisition-data/latest/browse', { ...localErrors, params })
export const getHistory = params => request.get('/acquisition-data/history', { ...localErrors, params })
export const getHistoryDetail = id => request.get(`/acquisition-data/history/${encodeURIComponent(id)}`, localErrors)
