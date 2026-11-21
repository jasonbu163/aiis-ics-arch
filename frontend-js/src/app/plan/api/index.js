/** 当前计划及字段配置，业务键原样保留。 */
import request from '@/utils/request'

const options = { suppressErrorMessage: true }

export const list = params => request.get('/plans', { ...options, params })
export const detail = id => request.get(`/plans/${id}`, options)
export const upsert = body => request.post('/plans/upsert', body, options)
export const getConfig = module => request.get('/task-field-configs', { ...options, params: { module } })
export const saveConfig = body => request.put('/task-field-configs', body, options)
export const deleteField = body => request.post('/task-field-configs/delete', body, options)
export const deleteSharedFields = body => request.post('/task-field-configs/batch-delete', body, options)
export const deleteLocalFields = body => request.post('/task-field-configs/local/batch-delete', body, options)
