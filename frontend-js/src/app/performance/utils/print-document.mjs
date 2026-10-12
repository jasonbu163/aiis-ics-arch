/**
 * 文件路径: /frontend-next-js/src/app/performance/utils/print-document.mjs
 * 功能描述: 创建独立浏览器打印文档并触发原生打印预览
 * 主要功能:
 *   - 生成 iframe 打印上下文
 *   - 注入普通 HTML/CSS 标签内容
 *   - 调用浏览器原生 print()
 *   - 打印后清理临时节点
 */
import { normalizePrintTemplate, renderPrintDocumentHtml } from './print-template.mjs'

export const createPerformancePrintDocument = async (labels, template, t) => {
  const safeLabels = Array.isArray(labels) ? labels.filter(Boolean) : []
  if (!safeLabels.length) return false

  const iframe = document.createElement('iframe')
  iframe.setAttribute('aria-hidden', 'true')
  iframe.style.position = 'fixed'
  iframe.style.right = '0'
  iframe.style.bottom = '0'
  iframe.style.width = '0'
  iframe.style.height = '0'
  iframe.style.border = '0'
  iframe.style.opacity = '0'

  document.body.appendChild(iframe)

  const printWindow = iframe.contentWindow
  const printDocument = iframe.contentDocument || printWindow?.document
  if (!printWindow || !printDocument) {
    iframe.remove()
    return false
  }

  printDocument.open()
  printDocument.write(renderPrintDocumentHtml(safeLabels, normalizePrintTemplate(template), t))
  printDocument.close()

  await new Promise((resolve) => {
    if (printDocument.readyState === 'complete') {
      resolve()
      return
    }
    iframe.onload = resolve
    window.setTimeout(resolve, 150)
  })

  const cleanup = () => {
    window.setTimeout(() => iframe.remove(), 300)
  }

  printWindow.addEventListener('afterprint', cleanup, { once: true })
  printWindow.focus()
  printWindow.print()
  window.setTimeout(cleanup, 1200)
  return true
}
