/**
 * 文件路径: /frontend-js/src/utils/date.js
 * 功能描述: 日期时间格式化工具函数
 * 主要功能:
 *   - 日期时间格式化
 *   - 日期范围计算
 *   - 相对时间显示
 */

/**
 * 格式化日期时间
 * @param {string|Date} date - 日期时间字符串或 Date 对象
 * @param {string} format - 格式模板，默认 'YYYY-MM-DD HH:mm:ss'
 * @returns {string} 格式化后的字符串
 */
export function formatDateTime(date, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!date) return '-'

  const d = new Date(date)
  if (isNaN(d.getTime())) return '-'

  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')

  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 格式化日期
 * @param {string|Date} date - 日期字符串或 Date 对象
 * @returns {string} 格式化为 YYYY-MM-DD
 */
export function formatDate(date) {
  return formatDateTime(date, 'YYYY-MM-DD')
}

/**
 * 格式化时间
 * @param {string|Date} date - 时间字符串或 Date 对象
 * @returns {string} 格式化为 HH:mm:ss
 */
export function formatTime(date) {
  return formatDateTime(date, 'HH:mm:ss')
}

/**
 * 获取相对时间描述
 * @param {string|Date} date - 日期时间
 * @returns {string} 相对时间描述，如"刚刚"、"5分钟前"等
 */
export function getRelativeTime(date) {
  if (!date) return '-'

  const d = new Date(date)
  if (isNaN(d.getTime())) return '-'

  const now = new Date()
  const diff = now.getTime() - d.getTime()
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (seconds < 60) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 30) return `${days}天前`

  return formatDate(date)
}

/**
 * 获取今日日期范围
 * @returns {{start: Date, end: Date}} 今日开始和结束时间
 */
export function getTodayRange() {
  const now = new Date()
  const start = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0)
  const end = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59)
  return { start, end }
}

/**
 * 获取最近 N 天的日期范围
 * @param {number} days - 天数
 * @returns {{start: Date, end: Date}} 日期范围
 */
export function getLastDaysRange(days) {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - days + 1)
  start.setHours(0, 0, 0, 0)
  end.setHours(23, 59, 59, 999)
  return { start, end }
}
