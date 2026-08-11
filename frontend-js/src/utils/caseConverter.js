/**
 * 文件路径: /frontend-js/src/utils/caseConverter.js
 * 功能描述: 命名格式转换工具
 * 主要功能:
 *   - snake_case 与 camelCase 相互转换
 *   - 支持对象、数组、嵌套对象的递归转换
 */

/**
 * 将 snake_case 转换为 camelCase
 * @param {*} obj - 需要转换的数据（对象、数组或基本类型）
 * @returns {*} 转换后的数据
 * @example
 * toCamelCase({ coil_no: 'C001', created_at: '2024-01-01' })
 * // 返回: { coilNo: 'C001', createdAt: '2024-01-01' }
 */
export const toCamelCase = (obj) => {
  if (Array.isArray(obj)) {
    return obj.map(toCamelCase)
  }
  if (obj instanceof Date || obj instanceof File || obj instanceof Blob) {
    return obj
  }
  if (obj !== null && typeof obj === 'object') {
    return Object.keys(obj).reduce((acc, key) => {
      const camelKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())
      acc[camelKey] = toCamelCase(obj[key])
      return acc
    }, {})
  }
  return obj
}

/**
 * 将 camelCase 转换为 snake_case
 * @param {*} obj - 需要转换的数据（对象、数组或基本类型）
 * @returns {*} 转换后的数据
 * @example
 * toSnakeCase({ coilNo: 'C001', createdAt: '2024-01-01' })
 * // 返回: { coil_no: 'C001', created_at: '2024-01-01' }
 */
export const toSnakeCase = (obj) => {
  if (Array.isArray(obj)) {
    return obj.map(toSnakeCase)
  }
  if (obj instanceof Date || obj instanceof File || obj instanceof Blob) {
    return obj
  }
  if (obj !== null && typeof obj === 'object') {
    return Object.keys(obj).reduce((acc, key) => {
      const snakeKey = key.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`)
      acc[snakeKey] = toSnakeCase(obj[key])
      return acc
    }, {})
  }
  return obj
}
