/** 来源/设备URL选择和请求代次；纯规则，不调用业务API。 */
export function parseBusinessDataSource(query = {}) {
  const dataSource = query.dataSource === undefined ? 'legacy' : query.dataSource
  const equipmentId = typeof query.equipmentId === 'string' ? query.equipmentId : ''
  const valid = dataSource === 'legacy' || dataSource === 'http'
  const ready = valid && (dataSource === 'legacy' || equipmentId.length > 0)
  return { dataSource, equipmentId, valid, ready }
}
export function businessDataSourceQuery(query, selection) {
  return { ...query, dataSource: selection.dataSource, equipmentId: selection.equipmentId || undefined }
}
export function requireBusinessSource(params = {}) {
  const selected = parseBusinessDataSource(params)
  if (!selected.ready) throw new Error('business_data_source_invalid')
  return selected
}
export function createRequestGeneration() {
  let current = 0
  return { begin: () => ++current, isCurrent: token => token === current, invalidate: () => ++current }
}
