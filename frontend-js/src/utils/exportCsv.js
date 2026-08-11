/**
 * 文件路径: /frontend-js/src/utils/exportCsv.js
 * 功能描述: 浏览器端 CSV 导出工具
 * 主要功能:
 *   - 将结构化行数据转换为 CSV 文本
 *   - 自动处理 CSV 转义与 UTF-8 BOM
 *   - 触发浏览器文件下载
 */

const escapeCsvValue = (value) => {
  if (value === null || value === undefined) return ''
  return `"${String(value).replace(/"/g, '""')}"`
}

export function exportRowsAsCsv({ filename, headers, rows }) {
  if (!Array.isArray(rows) || rows.length === 0) return false

  const lines = [
    headers.map((header) => escapeCsvValue(header.label)).join(','),
    ...rows.map((row, index) => headers
      .map((header) => {
        const value = typeof header.value === 'function'
          ? header.value(row, index)
          : row[header.key]
        return escapeCsvValue(value)
      })
      .join(','))
  ]

  const blob = new Blob([`\uFEFF${lines.join('\r\n')}`], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)

  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  return true
}
