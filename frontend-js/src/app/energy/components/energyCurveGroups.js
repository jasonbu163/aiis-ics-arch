/** 能耗曲线的本地校验、显示名称及所选指标定义。 */
export function curveTitle(row, locale) {
  return (locale.startsWith('en') ? row.titleEn || row.titleZh : row.titleZh || row.titleEn) || row.curveGroupKey
}

export function curveIssue(series, definitions) {
  const keys = series.map(item => item.metricKey)
  const enabled = series.filter(item => item.enabled)
  if (!enabled.length) return 'requiresEnabled'
  if (new Set(keys).size !== keys.length) return 'duplicateMetric'
  const byKey = new Map(definitions.map(item => [item.metricKey, item]))
  if (keys.some(key => byKey.get(key)?.valueType !== 'number')) return 'invalidMetrics'
  const kinds = new Set(enabled.map(({ metricKey }) => {
    const { quantityKey, unit } = byKey.get(metricKey)
    return JSON.stringify([quantityKey, unit || ''])
  }))
  return kinds.size > 1 ? 'mixedUnits' : ''
}
