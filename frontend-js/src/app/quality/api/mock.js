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
  createMockPage,
  mockNow
} from '@/api/mock/_diagnostic'
import { formatShanghaiDateTime, shanghaiInputToRfc3339 } from '@/utils/date'

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
const demoResults = [{ id: 'demo-quality-1', taskNo: demoTask, targetKey: 'demo',
  items: { reportUrl: 'https://example.com/report/demo.pdf' },
  createdAt: '2026-11-23T08:00:00+08:00', updatedAt: '2026-11-23T08:00:00+08:00' }]
let nextId = 2

function enabledDefinitions() {
  return demoConfig.definitions.filter(field => field.enabled)
}

function projectResult(row) {
  return { ...row, items: Object.fromEntries(enabledDefinitions()
    .map(field => [field.name, row.items[field.name] ?? null])) }
}

export async function getQualityResult(taskNo) {
  const row = demoResults.find(result => result.taskNo === taskNo)
  if (!row) throw new Error('quality.not_found')
  return projectResult(row)
}

export async function listQualityResults(params) {
  const matches = demoResults.filter(row =>
    (!params?.taskNo || params.taskNo.trim().toUpperCase() === row.taskNo) &&
    (!params?.targetKey || params.targetKey === row.targetKey) &&
    (!params?.createdFrom || Date.parse(params.createdFrom) <= Date.parse(row.createdAt)) &&
    (!params?.createdTo || Date.parse(params.createdTo) > Date.parse(row.createdAt)))
  const page = params?.page ?? 1
  const pageSize = params?.pageSize ?? 20
  const start = (page - 1) * pageSize
  const results = matches.slice(start, start + pageSize).map(projectResult)
  return {
    ...createMockPage('quality.listQualityResults', { page, pageSize }, results),
    total: matches.length, totalPages: Math.ceil(matches.length / pageSize), fields: enabledDefinitions()
  }
}

export async function createQualityResult(body) {
  const taskNo = body.taskNo.trim().toUpperCase()
  if (demoResults.some(row => row.taskNo === taskNo)) {
    throw Object.assign(new Error('quality.task_no_conflict'),
      { response: { status: 409, data: { errorCode: 'quality.task_no_conflict' } } })
  }
  const now = shanghaiInputToRfc3339(formatShanghaiDateTime(new Date()))
  const row = { id: `demo-quality-${nextId++}`, taskNo, targetKey: body.targetKey ?? null,
    items: { ...body.items }, createdAt: now, updatedAt: now }
  demoResults.unshift(row)
  return { outcome: 'created', quality: projectResult(row) }
}

export async function saveQualityResult(body) {
  const row = demoResults.find(result => result.taskNo === body.taskNo)
  if (!row) throw new Error('quality.not_found')
  row.items = { ...row.items, ...body.items }
  return { outcome: 'updated', quality: projectResult(row) }
}

export async function getQualityFieldConfig() {
  return demoConfig
}

export async function saveQualityFieldConfig(body) {
  demoConfig = { ...body, revision: body.revision + 1 }
  return demoConfig
}
