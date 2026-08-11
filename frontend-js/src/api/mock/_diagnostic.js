/**
 * 文件路径: /frontend-js/src/api/mock/_diagnostic.js
 * 功能描述: 模块无关的前端 mock 诊断原语
 * 主要功能:
 *   - 提供稳定且明显的前端 mock 标记
 *   - 提供通用记录、分页和变更响应构造器
 *   - 不包含业务模块字段或按 API 名称分发的业务逻辑
 */

export const MOCK_SOURCE_TYPE = 'frontend_mock'
export const MOCK_LABEL = 'FRONTEND_MOCK_ONLY'

export const mockNow = () => new Date().toISOString()
export const mockToday = () => mockNow().slice(0, 10)

export const createMockMarker = (apiName) => ({
  sourceType: MOCK_SOURCE_TYPE,
  mock: true,
  mockLabel: MOCK_LABEL,
  apiName
})

export const createMockRecord = (apiName, index = 1, fields = {}) => ({
  ...createMockMarker(apiName),
  id: 900000 + index,
  code: `MOCK-${index}`,
  name: `${MOCK_LABEL}-${index}`,
  title: `${MOCK_LABEL}-${apiName}`,
  status: 'frontend_mock',
  statusKey: 'frontend_mock',
  date: mockToday(),
  createdAt: mockNow(),
  updatedAt: mockNow(),
  value: 999 + index,
  remark: `${MOCK_LABEL}: ${apiName}`,
  ...fields
})

export const createMockPage = (apiName, params = {}, rows = []) => {
  const page = params?.page || params?.pageNum || params?.currentPage || 1
  const pageSize = params?.pageSize || params?.page_size || 10

  return {
    ...createMockMarker(apiName),
    data: rows,
    list: rows,
    items: rows,
    records: rows,
    rows,
    total: rows.length,
    page,
    pageSize,
    currentPage: page
  }
}

export const createMockMutation = (apiName, payload = {}, id) => {
  const fields = payload && typeof payload === 'object' && !Array.isArray(payload) ? payload : {}

  return {
    ...createMockMarker(apiName),
    success: true,
    id: fields.id || id || 900001,
    ...fields,
    updatedAt: mockNow()
  }
}
