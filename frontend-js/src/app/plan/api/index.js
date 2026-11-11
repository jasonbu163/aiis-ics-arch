/** 通用计划及字段配置 API；请求与响应的业务键原样保留。 */
import request from '@/utils/request'
const options = { suppressErrorMessage: true }
export const list = params => request.get('/plans', { ...options, params })
export const detail = id => request.get(`/plans/${id}`, options)
export const upsert = body => request.post('/plans/upsert', body, options)
export const action = (id, actionName, body) => request.post(`/plans/${id}/actions/${actionName}`, body, options)
export const getConfig = (module, version) => request.get('/task-field-configs', { ...options, params: { module, fieldConfigVersion: version } })
export const saveConfig = body => request.put('/task-field-configs', body, options)
