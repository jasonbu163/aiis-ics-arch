/** 过程曲线和管理员历史记录接口。 */
import request from '@/utils/request'

const quiet = { suppressErrorMessage: true }
export const monitorOptions = includeDeleted => request.get('/monitor/observation-options', {
  ...quiet, params: includeDeleted ? { includeDeleted: true } : undefined
})
export const historyDefaultContext = params => request.get('/monitor/history-default-context', { ...quiet, params })
export const historyCurves = (params, language) => request.get('/monitor/history-curves', { ...quiet, params, headers: { 'Accept-Language': language } })
export const curves = params => request.get('/monitor/curve-configs', { ...quiet, params })
export const createCurve = data => request.post('/monitor/curve-configs', data)
export const updateCurve = (key, data) => request.patch(`/monitor/curve-configs/${encodeURIComponent(key)}`, data)
export const historyList = params => request.get('/monitor/admin/history-samples', { ...quiet, params })
export const historyDetail = id => request.get(`/monitor/admin/history-samples/${encodeURIComponent(id)}`, quiet)
export const updateHistory = (id, data) => request.patch(`/monitor/admin/history-samples/${encodeURIComponent(id)}`, data)
