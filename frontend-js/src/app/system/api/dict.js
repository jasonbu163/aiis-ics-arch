/**
 * 文件路径: /frontend-js/src/app/system/api/dict.js
 * 功能描述: 系统字典管理相关 API 接口封装
 * 主要功能:
 *   - 字典类型管理 CRUD
 *   - 按类型获取字典
 *   - 字典项管理 CRUD
 *   - 直接消费后端统一契约
 */
import request from '@/utils/request'
import { callApi } from '@/api/mockMode'
import * as mockApi from './mock'

export async function getDictList(params) {
  return callApi(() => mockApi.getDictList(params), () => request.get('/sys-dict', { params }), 'dict.getDictList')
}

export async function getDictByType(dictType) {
  return callApi(() => mockApi.getDictByType(dictType), () => request.get(`/sys-dict/type/${dictType}`), 'dict.getDictByType')
}

export async function createDict(data) {
  return callApi(() => mockApi.createDict(data), () => request.post('/sys-dict', data), 'dict.createDict')
}

export async function updateDict(id, data) {
  return callApi(() => mockApi.updateDict(id, data), () => request.put(`/sys-dict/${id}`, data), 'dict.updateDict')
}

export async function deleteDict(id) {
  return callApi(() => mockApi.deleteDict(id), () => request.delete(`/sys-dict/${id}`), 'dict.deleteDict')
}

export async function getDictItemList(params) {
  return callApi(() => mockApi.getDictItemList(params), () => request.get('/sys-dict-items', { params }), 'dict.getDictItemList')
}

export async function createDictItem(data) {
  return callApi(() => mockApi.createDictItem(data), () => request.post('/sys-dict-items', data), 'dict.createDictItem')
}

export async function updateDictItem(id, data) {
  return callApi(() => mockApi.updateDictItem(id, data), () => request.put(`/sys-dict-items/${id}`, data), 'dict.updateDictItem')
}

export async function deleteDictItem(id) {
  return callApi(() => mockApi.deleteDictItem(id), () => request.delete(`/sys-dict-items/${id}`), 'dict.deleteDictItem')
}
