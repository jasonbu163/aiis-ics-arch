export function isRootPerformance(row) {
  return row.parentCoilNo === row.coilNo
}

export function displayParentCoilNo(row) {
  return row.parentCoilNo || row.coilNo
}

export function hasDisplayValue(value) {
  return value !== null && value !== undefined && value !== ''
}

export function displayText(value) {
  return hasDisplayValue(value) ? value : '-'
}

export function formatNullableNumber(value, precision) {
  if (!hasDisplayValue(value)) return '-'
  const numericValue = Number(value)
  if (!Number.isFinite(numericValue)) return '-'
  return numericValue.toFixed(precision)
}

export function normalizeNullableNumber(value) {
  if (!hasDisplayValue(value)) return null
  const numericValue = Number(value)
  return Number.isFinite(numericValue) ? numericValue : null
}

export function normalizeNullableDateTime(value) {
  return hasDisplayValue(value) ? value : null
}

export function observationStatusKey(status) {
  return hasDisplayValue(status) ? status : 'manual_historical'
}

export function durationSourceKey(source) {
  return hasDisplayValue(source) ? source : 'unavailable'
}

export function formatBackendDuration(seconds, translate) {
  if (!hasDisplayValue(seconds)) return '-'
  const totalSeconds = Number(seconds)
  if (!Number.isFinite(totalSeconds) || totalSeconds < 0) return '-'

  const wholeSeconds = Math.floor(totalSeconds)
  const hours = Math.floor(wholeSeconds / 3600)
  const minutes = Math.floor((wholeSeconds % 3600) / 60)
  const remainingSeconds = wholeSeconds % 60

  if (hours > 0) {
    return `${hours}${translate('common.unit.hour')}${minutes}${translate('common.unit.min')}${remainingSeconds}${translate('performance.durationUnits.second')}`
  }
  if (minutes > 0) {
    return `${minutes}${translate('common.unit.min')}${remainingSeconds}${translate('performance.durationUnits.second')}`
  }
  return `${remainingSeconds}${translate('performance.durationUnits.second')}`
}
