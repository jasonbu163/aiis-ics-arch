/**
 * 文件路径: /frontend-js/src/app/system/api/projectionMapping.js
 * 功能描述: Projection 映射设置控制面 API facade。
 * 主要功能:
 *   - 仅消费后端已注册的 handler、候选点与 revision 合同
 *   - 暴露草稿 binding、校验、发布、复制和回滚意图
 *   - 不读取 PLC、YAML、数据库或 Projection runner
 */
import request from '@/utils/request'

const BASE_URL = '/projection-mappings'

export function getProjectionHandlers() {
  return request.get(`${BASE_URL}/handlers`)
}

export function getProjectionCandidates(params) {
  return request.get(`${BASE_URL}/candidates`, { params })
}

export function getProjectionMappingSets() {
  return request.get(`${BASE_URL}/sets`)
}

export function getProjectionMappingSet(mappingSetId) {
  return request.get(`${BASE_URL}/sets/${mappingSetId}`)
}

export function getProjectionCurrentRevision(mappingSetId) {
  return request.get(`${BASE_URL}/sets/${mappingSetId}/current`)
}

export function createProjectionMappingSet(data) {
  return request.post(`${BASE_URL}/sets`, data)
}

export function replaceProjectionMappingBindings(revisionId, data) {
  return request.put(`${BASE_URL}/revisions/${revisionId}/bindings`, data)
}

export function validateProjectionMappingRevision(revisionId) {
  return request.post(`${BASE_URL}/revisions/${revisionId}/validate`)
}

export function publishProjectionMappingRevision(revisionId) {
  return request.post(`${BASE_URL}/revisions/${revisionId}/publish`)
}

export function copyProjectionMappingRevision(revisionId, data) {
  return request.post(`${BASE_URL}/revisions/${revisionId}/copy`, data)
}

export function rollbackProjectionMappingRevision(mappingSetId, data) {
  return request.post(`${BASE_URL}/sets/${mappingSetId}/rollback`, data)
}
