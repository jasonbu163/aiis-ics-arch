/** 能耗统计、表计配置与样本标注的现有登录接口。 */
import request from '@/utils/request'

const quiet = { suppressErrorMessage: true }
export const energyOptions = () => request.get('/energy/consumption/options', quiet)
export const energyDefinitions = meterId => request.get('/energy/consumption/definitions', { ...quiet, params: { meterId } })
export const energySamples = params => request.get('/energy/consumption/samples', { ...quiet, params })
export const energySummary = params => request.get('/energy/consumption/summary', { ...quiet, params })
export const energyConfigs = params => request.get('/energy/metric-configs', { ...quiet, params })
export const createEnergyConfig = data => request.post('/energy/metric-configs', data)
export const updateEnergyConfig = (meter, group, key, data) => request.patch(`/energy/metric-configs/${encodeURIComponent(meter)}/${encodeURIComponent(group)}/${encodeURIComponent(key)}`, data)
export const energyAdminSamples = params => request.get('/energy/admin/consumption-samples', { ...quiet, params })
export const updateEnergySample = (id, data) => request.patch(`/energy/admin/consumption-samples/${encodeURIComponent(id)}`, data)

const sourcePath = key => '/energy/write-sources/' + (
  key === '.' || key === '..' ? key.replaceAll('.', '%252E') : encodeURIComponent(key)
)
export const energyWriteSources = () => request.get('/energy/write-sources', quiet)
export const createEnergyWriteSource = data => request.post('/energy/write-sources', data, quiet)
export const updateEnergyWriteSource = (key, data) => request.patch(sourcePath(key), data, quiet)
export const deleteEnergyWriteSource = key => request.delete(sourcePath(key), quiet)
