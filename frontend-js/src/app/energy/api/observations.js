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

export const energyMeters = () => request.get('/energy/meters', quiet)
export const createEnergyMeter = data => request.post('/energy/meters', data, quiet)
export const updateEnergyMeter = data => request.patch('/energy/meters', data, quiet)

export const energyCurveGroups = params => request.get('/energy/curve-configs', { ...quiet, params })
export const energyConsumptionCurveGroups = () => request.get('/energy/consumption/curve-configs', quiet)
export const createEnergyCurveGroup = data => request.post('/energy/curve-configs', data, quiet)

const curvePathKey = key => {
  // 浏览器会移除单独的点段；以不同编码保留字面百分号标识。
  if (key === '.' || key === '..') return key.replaceAll('.', '%252e')
  if (key === '%2e' || key === '%2e%2e') return key.replaceAll('%2e', '%25%32%65')
  return encodeURIComponent(key)
}
export const updateEnergyCurveGroup = (key, data) =>
  request.patch(`/energy/curve-configs/${curvePathKey(key)}`, data, quiet)
