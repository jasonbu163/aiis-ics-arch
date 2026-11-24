/**
 * 文件路径: /frontend-next-js/src/app/quality/api/mock.js
 * 功能描述: quality 前端 mock 诊断实现
 * 主要功能:
 *   - 在 VITE_FRONTEND_MOCK_ENABLED=true 时提供模块本地诊断数据
 *   - 与 /frontend-next-js/src/app/quality/api/index.js 保持同名导出
 */
import {
  MOCK_LABEL,
  createMockMarker,
  createMockMutation,
  createMockPage,
  createMockRecord,
  mockNow
} from '@/api/mock/_diagnostic'

const makeQualityRecord = (apiName, index) => createMockRecord(apiName, index, {
  coilNo: `MOCK-COIL-${String(index).padStart(4, '0')}`,
  grade: MOCK_LABEL,
  spec: '99.99 x 9999',
  weight: 999 + index,
  qualityGrade: 'frontend_mock',
  judgment: 'qualified',
  inspector: `${MOCK_LABEL}-INSPECTOR-${index}`,
  inspectTime: mockNow(),
  qualityItems: [],
  defects: []
})

export async function getQualityList(params) {
  const apiName = 'quality.getQualityList'
  return createMockPage(apiName, params, [makeQualityRecord(apiName, 1), makeQualityRecord(apiName, 2)])
}

export async function getQualityById(id) {
  return makeQualityRecord('quality.getQualityById', Number(id) || 1)
}

export async function createQuality(data) {
  return createMockMutation('quality.createQuality', data)
}

export async function updateQuality(id, data) {
  return createMockMutation('quality.updateQuality', data, id)
}

export async function deleteQuality(id) {
  return createMockMutation('quality.deleteQuality', {}, id)
}

export async function addDefect(qualityId, data) {
  return createMockMutation('quality.addDefect', data, qualityId)
}

export async function deleteDefect(qualityId, defectId) {
  return createMockMutation('quality.deleteDefect', { qualityId }, defectId)
}

export async function getSPCData() {
  const apiName = 'quality.getSPCData'
  return Array.from({ length: 10 }, (_, offset) => {
    const index = offset + 1
    return {
      ...createMockMarker(apiName),
      id: index,
      subgroup: Math.ceil(index / 5),
      coilNo: `MOCK-COIL-${String(index).padStart(4, '0')}`,
      grade: MOCK_LABEL,
      value: 1 + index / 100,
      isNormal: index !== 10,
      time: mockNow(),
      operator: `${MOCK_LABEL}-OPERATOR`
    }
  })
}

export async function getSPCStats() {
  const apiName = 'quality.getSPCStats'
  return {
    ...createMockMarker(apiName),
    cp: 9.99,
    cpk: 8.88,
    sigma: 0.0123,
    defectRate: 99.99,
    mean: 1.05,
    ucl: 1.09,
    lcl: 1.01,
    usl: 1.1,
    lsl: 1
  }
}

const demoTask = 'DEMO-QUALITY'
const demoReport = {
  name: 'reportUrl', labels: { 'zh-CN': '检测报告', 'en-US': 'Inspection report' },
  type: 'link', unit: null, linkText: 'PDF', editable: true, enabled: true,
  visible: true, isNullable: true, order: 0
}
let demoConfig = { revision: 1, definitions: [demoReport] }
let demoResult = { id: 'demo-quality-1', taskNo: demoTask, targetKey: 'demo',
  items: { reportUrl: 'https://example.com/report/demo.pdf' },
  createdAt: '2026-11-23T08:00:00+08:00', updatedAt: '2026-11-23T08:00:00+08:00' }

function enabledDefinitions() {
  return demoConfig.definitions.filter(field => field.enabled)
}

export async function getQualityResult() {
  return { ...demoResult, items: Object.fromEntries(enabledDefinitions()
    .map(field => [field.name, demoResult.items[field.name] ?? null])) }
}

export async function listQualityResults(params) {
  const matches = (!params?.taskNo || params.taskNo.trim().toUpperCase() === demoTask) &&
    (!params?.targetKey || params.targetKey === demoResult.targetKey) &&
    (!params?.createdFrom || Date.parse(params.createdFrom) <= Date.parse(demoResult.createdAt)) &&
    (!params?.createdTo || Date.parse(params.createdTo) > Date.parse(demoResult.createdAt))
  return {
    ...createMockPage('quality.listQualityResults', params, matches ? [await getQualityResult()] : []),
    fields: enabledDefinitions()
  }
}

export async function saveQualityResult(body) {
  demoResult = { ...demoResult, items: { ...demoResult.items, ...body.items } }
  return { outcome: 'updated', quality: await getQualityResult() }
}

export async function getQualityFieldConfig() {
  return demoConfig
}

export async function saveQualityFieldConfig(body) {
  demoConfig = { ...body, revision: body.revision + 1 }
  return demoConfig
}
