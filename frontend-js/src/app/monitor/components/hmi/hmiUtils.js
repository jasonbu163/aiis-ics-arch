/**
 * 文件路径: /frontend-next-js/src/app/monitor/components/hmi/hmiUtils.js
 * 功能描述: HMI 实时监控组件工具函数
 * 主要功能:
 *   - 读取 latest snapshot payload 中的点位值
 *   - 格式化数值、单位和状态值
 *   - 为 HMI 组件提供统一空值处理
 */

const toResponseCamelKey = (key, lowerSegmentRest = false) => key
  .split('_')
  .map((segment, index) => {
    if (index === 0) return segment
    const rest = lowerSegmentRest ? segment.slice(1).toLowerCase() : segment.slice(1)
    return `${segment.charAt(0).toUpperCase()}${rest}`
  })
  .join('')

const keyCandidates = (key) => {
  if (!key) return []
  return [
    key,
    toResponseCamelKey(key),
    toResponseCamelKey(key, true),
    key.replaceAll('_', '')
  ]
}

export const readPoint = (payload, key, fallbackKey) => {
  if (!payload || !key) return undefined
  const keys = [
    ...keyCandidates(key),
    ...keyCandidates(fallbackKey)
  ]
  for (const candidate of keys) {
    const value = payload[candidate]
    if (value !== undefined && value !== null && value !== '') return value
  }
  return payload[key]
}

export const formatPointValue = (value, decimals = 0) => {
  if (value === undefined || value === null || value === '') return '-'
  const numberValue = Number(value)
  if (Number.isNaN(numberValue)) return String(value)
  return numberValue.toFixed(decimals)
}

export const isActiveState = (value) => value === true || value === 1 || value === '1' || value === 'true'
