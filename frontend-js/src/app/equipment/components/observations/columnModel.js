/** 管理列表指标列使用稳定指标键，并区分缺测和有效假值。 */
export function metricField(key) { return `metric:${key}` }

export function metricTitle(field, locale) {
  const name = locale.startsWith('en') ? field.nameEn : field.nameZh
  return field.unit ? `${name} (${field.unit})` : name
}

export function metricValue(row, key) {
  const item = row.values?.find(value => value.metricKey === key)
  return item ? String(item.value) : '—'
}

export function sourceLabel(row, fallback) {
  if (!row.sourceKey) return fallback
  return row.sourceName && row.sourceName !== row.sourceKey ? `${row.sourceName} (${row.sourceKey})` : row.sourceKey
}
