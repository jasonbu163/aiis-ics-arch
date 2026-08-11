/**
 * 文件路径: /frontend-js/src/app/system/api/mock/dict.js
 * 功能描述: dict 前端 mock 诊断实现
 * 主要功能:
 *   - 在 VITE_FRONTEND_MOCK_ENABLED=true 时提供模块本地诊断数据
 *   - 与 /frontend-js/src/app/system/api/dict.js 保持同名导出
 */
import {
  MOCK_LABEL,
  createMockMarker,
  createMockMutation,
  createMockPage,
  createMockRecord,
  mockNow
} from '@/api/mock/_diagnostic'

const makeDict = (apiName, index) => createMockRecord(apiName, index, {
  dictType: `frontend_mock_type_${index}`,
  dictName: `${MOCK_LABEL}-DICT-${index}`,
  description: `${MOCK_LABEL}-DICTIONARY`,
  status: 'active',
  createTime: mockNow()
})

const makeDictItem = (apiName, index) => createMockRecord(apiName, index, {
  dictId: 900001,
  label: `${MOCK_LABEL}-LABEL-${index}`,
  value: `frontend_mock_value_${index}`,
  sort: index,
  status: 'active'
})

export async function getDictList(params) {
  const apiName = 'dict.getDictList'
  return createMockPage(apiName, params, [makeDict(apiName, 1), makeDict(apiName, 2)])
}

export async function getDictByType(dictType) {
  const apiName = 'dict.getDictByType'
  const items = [makeDictItem(apiName, 1), makeDictItem(apiName, 2)]
  return { ...createMockMarker(apiName), dictType, items, list: items }
}

export async function createDict(data) {
  return createMockMutation('dict.createDict', data)
}

export async function updateDict(id, data) {
  return createMockMutation('dict.updateDict', data, id)
}

export async function deleteDict(id) {
  return createMockMutation('dict.deleteDict', {}, id)
}

export async function getDictItemList(params) {
  const apiName = 'dict.getDictItemList'
  return createMockPage(apiName, params, [makeDictItem(apiName, 1), makeDictItem(apiName, 2)])
}

export async function createDictItem(data) {
  return createMockMutation('dict.createDictItem', data)
}

export async function updateDictItem(id, data) {
  return createMockMutation('dict.updateDictItem', data, id)
}

export async function deleteDictItem(id) {
  return createMockMutation('dict.deleteDictItem', {}, id)
}
