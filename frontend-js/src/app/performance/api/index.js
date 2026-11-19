/** 当前实绩与人工反馈 API；补建复用普通计划创建。 */
import request from '@/utils/request'

export { getConfig, saveConfig, deleteField, upsert as upsertPlan } from '@/app/plan/api'

const options = { suppressErrorMessage: true }

export const list = params => request.get('/performances', { ...options, params })
export const detail = id => request.get(`/performances/${id}`, options)
export const upsert = body => request.post('/performances/upsert', body, options)
