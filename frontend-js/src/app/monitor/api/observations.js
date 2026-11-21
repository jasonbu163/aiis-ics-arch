/** 过程曲线和管理员历史记录接口。 */
import request from '@/utils/request'

const quiet = { suppressErrorMessage: true }
export const monitorOptions = includeDeleted => request.get('/monitor/observation-options', {
  ...quiet, params: includeDeleted ? { includeDeleted: true } : undefined
})
export const historyCurves = (params, language) => request.get('/monitor/history-curves', { ...quiet, params, headers: { 'Accept-Language': language } })
export const curves = params => request.get('/monitor/curve-configs', { ...quiet, params })
export const createCurve = data => request.post('/monitor/curve-configs', data)
export const updateCurve = (key, data) => request.patch(`/monitor/curve-configs/${encodeURIComponent(key)}`, data)
export const historyList = params => request.get('/monitor/admin/history-samples', { ...quiet, params })
export const historyDetail = id => request.get(`/monitor/admin/history-samples/${encodeURIComponent(id)}`, quiet)
export const updateHistory = (id, data) => request.patch(`/monitor/admin/history-samples/${encodeURIComponent(id)}`, data)
export const energyOptions = () => request.get('/energy/consumption/options', quiet)
export const energyDefinitions = meterId => request.get('/energy/consumption/definitions', { ...quiet, params: { meterId } })
export const energySamples = params => request.get('/energy/consumption/samples', { ...quiet, params })
export const energySummary = params => request.get('/energy/consumption/summary', { ...quiet, params })
export const energyConfigs = params => request.get('/energy/metric-configs', { ...quiet, params })
export const createEnergyConfig = data => request.post('/energy/metric-configs', data)
export const updateEnergyConfig = (meter, group, key, data) => request.patch(`/energy/metric-configs/${encodeURIComponent(meter)}/${encodeURIComponent(group)}/${encodeURIComponent(key)}`, data)
export const energyAdminSamples = params => request.get('/energy/admin/consumption-samples', { ...quiet, params })
export const updateEnergySample = (id, data) => request.patch(`/energy/admin/consumption-samples/${encodeURIComponent(id)}`, data)
