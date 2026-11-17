/** 设备状态的真实查询与管理员配置接口。 */
import request from '@/utils/request'

const quiet = { suppressErrorMessage: true }
export const equipmentOptions = () => request.get('/equipment/observation-options', quiet)
export const latestCards = (params, language) => request.get('/equipment/latest-cards', { ...quiet, params, headers: { 'Accept-Language': language } })
export const sampledTasks = equipmentId => request.get('/equipment/sampled-tasks', { ...quiet, params: { equipmentId } })
export const metricGroups = () => request.get('/equipment/metric-groups', quiet)
export const createMetricGroup = data => request.post('/equipment/metric-groups', data)
export const updateMetricGroup = (key, data) => request.patch(`/equipment/metric-groups/${encodeURIComponent(key)}`, data)
export const metrics = () => request.get('/equipment/metric-configs', quiet)
export const createMetric = data => request.post('/equipment/metric-configs', data)
export const updateMetric = (key, data) => request.patch(`/equipment/metric-configs/${encodeURIComponent(key)}`, data)
export const bindings = params => request.get('/equipment/metric-slot-bindings', { ...quiet, params })
export const createBinding = data => request.post('/equipment/metric-slot-bindings', data)
export const updateBinding = (target, group, slot, data) => request.patch(
  `/equipment/metric-slot-bindings/${encodeURIComponent(target)}/${encodeURIComponent(group)}/${slot}`, data)
export const observationListColumns = target => request.get('/equipment/observation-list-columns', { ...quiet, params: { target } })
export const cards = () => request.get('/equipment/card-configs', quiet)
export const createCard = data => request.post('/equipment/card-configs', data)
export const updateCard = (key, data) => request.patch(`/equipment/card-configs/${encodeURIComponent(key)}`, data)
export const latestList = params => request.get('/equipment/admin/latest-snapshots', { ...quiet, params })
export const latestDetail = id => request.get(`/equipment/admin/latest-snapshots/${encodeURIComponent(id)}`, quiet)
export const updateLatest = (id, data) => request.patch(`/equipment/admin/latest-snapshots/${encodeURIComponent(id)}`, data)
