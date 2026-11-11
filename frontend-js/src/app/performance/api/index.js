/** 通用实绩、人工字段和补建计划 API。 */
import request from '@/utils/request'
const options = { suppressErrorMessage: true }
export const list = params => request.get('/performances', { ...options, params })
export const detail = id => request.get(`/performances/${id}`, options)
export const upsert = body => request.post('/performances/upsert', body, options)
export const supplement = (id, body) => request.post(`/performances/${id}/actions/supplement-plan`, body, options)
export const getConfig = (module, version) => request.get('/task-field-configs', { ...options, params: { module, fieldConfigVersion: version } })
export const saveConfig = body => request.put('/task-field-configs', body, options)
