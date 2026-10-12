/**
 * 文件路径: /frontend-next-js/src/app/performance/utils/print-template.mjs
 * 功能描述: Performance 打印模板 schema、字段定义和普通 HTML 输出 helper
 * 主要功能:
 *   - 提供默认打印模板
 *   - 归一化打印模板设置
 *   - 生成普通 HTML/CSS 打印标签
 *   - 保存和读取本地默认打印模板
 */

const STORAGE_KEY = 'performance.print.template.v1'

export const PRINT_SECTION_KEYS = [
  'basicInfo',
  'productionRecord',
  'tension',
  'speed',
  'processParams',
  'quality'
]

export const DEFAULT_PRINT_TEMPLATE = {
  title: '',
  paper: 'A4',
  orientation: 'portrait',
  margin: {
    top: 10,
    right: 10,
    bottom: 10,
    left: 10
  },
  fontSize: 12,
  scale: 100,
  appearance: {
    enhanced: false
  },
  sections: {
    basicInfo: true,
    productionRecord: true,
    tension: true,
    speed: true,
    processParams: true,
    quality: true
  }
}

const clampNumber = (value, fallback, min, max) => {
  const numberValue = Number(value)
  if (!Number.isFinite(numberValue)) return fallback
  return Math.min(Math.max(numberValue, min), max)
}

export const normalizePrintTemplate = (template = {}) => {
  const base = DEFAULT_PRINT_TEMPLATE
  const margin = template.margin || {}
  const appearance = template.appearance || {}
  const sections = template.sections || {}

  return {
    title: typeof template.title === 'string' ? template.title.slice(0, 40) : base.title,
    paper: ['A4', 'A5', 'label'].includes(template.paper) ? template.paper : base.paper,
    orientation: ['portrait', 'landscape'].includes(template.orientation) ? template.orientation : base.orientation,
    margin: {
      top: clampNumber(margin.top, base.margin.top, 0, 50),
      right: clampNumber(margin.right, base.margin.right, 0, 50),
      bottom: clampNumber(margin.bottom, base.margin.bottom, 0, 50),
      left: clampNumber(margin.left, base.margin.left, 0, 50)
    },
    fontSize: clampNumber(template.fontSize, base.fontSize, 9, 18),
    scale: clampNumber(template.scale, base.scale, 70, 130),
    appearance: {
      enhanced: appearance.enhanced === true
    },
    sections: PRINT_SECTION_KEYS.reduce((result, key) => {
      result[key] = sections[key] !== false
      return result
    }, {})
  }
}

export const getPrintTemplateTitle = (template, t) => {
  const normalized = normalizePrintTemplate(template)
  return normalized.title.trim() || t('performance.common.productionLabel')
}

export const createPrintPreviewSampleLabel = () => ({
  id: 'print-template-sample',
  coilNo: '8888.88',
  grade: 'AAA',
  weight: 99.99,
  thickness: 1.2,
  width: 1250,
  totalLength: 9999.99,
  diameter: 888.88,
  outerDiameter: 888.88,
  operator: 'Administrator',
  shift: 'dayShift',
  entryTension: 15.5,
  entryLoopTension: 12,
  furnaceTension: 10,
  exitLoopTension: 12,
  exitTension: 15.5,
  entrySpeed: 25,
  furnaceSpeed: 20,
  exitSpeed: 25,
  furnaceTemp: 820,
  residenceTime: 18,
  dewPoint: -35,
  oxygenContent: '20 ppm'
})

export const loadStoredPrintTemplate = () => {
  if (typeof window === 'undefined') return normalizePrintTemplate()

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    return normalizePrintTemplate(raw ? JSON.parse(raw) : undefined)
  } catch (error) {
    console.warn('Failed to load local print template:', error)
    return normalizePrintTemplate()
  }
}

export const saveStoredPrintTemplate = (template) => {
  if (typeof window === 'undefined') return

  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(normalizePrintTemplate(template)))
  } catch (error) {
    console.warn('Failed to save local print template:', error)
  }
}

export const getPaperSize = (template) => {
  const normalized = normalizePrintTemplate(template)
  if (normalized.paper === 'A5') return 'A5'
  if (normalized.paper === 'label') return '100mm 150mm'
  return 'A4'
}

export const getSectionTitle = (sectionKey, t) => {
  const keyMap = {
    basicInfo: 'performance.quality.basicInfo',
    productionRecord: 'performance.common.productionRecord',
    tension: 'performance.tensionCurve',
    speed: 'performance.speedCurve',
    processParams: 'performance.common.processParams',
    quality: 'performance.quality.inspectItems'
  }
  return t(keyMap[sectionKey])
}

export const getQualityRows = (t) => [
  {
    item: t('performance.printQuality.surfaceQuality'),
    standard: t('performance.printQuality.noDefect'),
    actual: t('performance.printQuality.noDefect'),
    result: t('performance.printQuality.results.qualified')
  },
  {
    item: t('performance.printQuality.thicknessDeviation'),
    standard: t('performance.printQuality.thicknessStandard'),
    actual: t('performance.printQuality.thicknessActual'),
    result: t('performance.printQuality.results.qualified')
  },
  {
    item: t('performance.printQuality.widthDeviation'),
    standard: t('performance.printQuality.widthStandard'),
    actual: t('performance.printQuality.widthActual'),
    result: t('performance.printQuality.results.qualified')
  },
  {
    item: t('performance.printQuality.flatness'),
    standard: t('performance.printQuality.flatnessStandard'),
    actual: t('performance.printQuality.flatnessActual'),
    result: t('performance.printQuality.results.qualified')
  }
]

export const formatPrintNumber = (value, precision = 2) => {
  if (value === null || value === undefined || value === '') return '-'
  const numberValue = Number(value)
  if (!Number.isFinite(numberValue)) return '-'
  return numberValue.toFixed(precision)
}

export const formatPrintValue = (value, unitKey, precision, t) => {
  const formatted = formatPrintNumber(value, precision)
  if (formatted === '-') return '-'
  return `${formatted} ${t(unitKey)}`
}

export const formatPrintShift = (value, t) => {
  if (!value) return '-'
  const shiftMap = {
    dayShift: 'performance.common.dayShift',
    middleShift: 'performance.common.middleShift',
    nightShift: 'performance.common.nightShift',
    白班: 'performance.common.dayShift',
    中班: 'performance.common.middleShift',
    夜班: 'performance.common.nightShift'
  }
  return t(shiftMap[value] || value)
}

export const formatPrintTemperature = (value, t) => {
  if (value === null || value === undefined || value === '') return '-'
  return `${value}${t('performance.units.celsius')}`
}

export const getPrintFields = (label, t) => ({
  basicInfo: [
    { label: t('performance.coilNo'), value: label.coilNo || '-' },
    { label: t('performance.grade'), value: label.grade || '-' },
    { label: t('performance.weight'), value: formatPrintValue(label.weight, 'common.unit.ton', 4, t) },
    { label: t('performance.common.thickness'), value: formatPrintValue(label.thickness, 'common.unit.mm', 2, t) },
    { label: t('performance.common.width'), value: formatPrintValue(label.width, 'common.unit.mm', 2, t) },
    { label: t('performance.totalLength'), value: formatPrintValue(label.totalLength, 'common.unit.m', 2, t) },
    { label: t('performance.diameter'), value: formatPrintValue(label.outerDiameter ?? label.diameter, 'common.unit.mm', 2, t) }
  ],
  productionRecord: [
    { label: t('performance.common.operator'), value: label.operator || '-' },
    { label: t('performance.common.shift'), value: formatPrintShift(label.shift, t) }
  ],
  tension: [
    { label: t('performance.common.entryTension'), value: formatPrintValue(label.entryTension, 'performance.units.kN', 2, t) },
    { label: t('performance.common.entryLoopTension'), value: formatPrintValue(label.entryLoopTension, 'performance.units.kN', 2, t) },
    { label: t('performance.common.furnaceTension'), value: formatPrintValue(label.furnaceTension, 'performance.units.kN', 2, t) },
    { label: t('performance.common.exitLoopTension'), value: formatPrintValue(label.exitLoopTension, 'performance.units.kN', 2, t) },
    { label: t('performance.common.exitTension'), value: formatPrintValue(label.exitTension, 'performance.units.kN', 2, t) }
  ],
  speed: [
    { label: t('performance.common.entrySpeed'), value: formatPrintValue(label.entrySpeed, 'common.unit.speed', 2, t) },
    { label: t('performance.common.furnaceSpeed'), value: formatPrintValue(label.furnaceSpeed, 'common.unit.speed', 2, t) },
    { label: t('performance.common.exitSpeed'), value: formatPrintValue(label.exitSpeed, 'common.unit.speed', 2, t) }
  ],
  processParams: [
    { label: t('performance.common.furnaceTemp'), value: formatPrintTemperature(label.furnaceTemp, t) },
    { label: t('performance.table.duration'), value: formatPrintValue(label.residenceTime, 'common.unit.min', 0, t) },
    { label: t('performance.common.dewPoint'), value: formatPrintValue(label.dewPoint, 'performance.units.celsius', 0, t) },
    { label: t('performance.common.oxygenContent'), value: label.oxygenContent || '-' }
  ]
})

export const escapeHtml = (value) => String(value ?? '')
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#39;')

export const renderLabelHtml = (label, template, t) => {
  const normalized = normalizePrintTemplate(template)
  const fields = getPrintFields(label || {}, t)
  const printTime = new Date().toLocaleString()

  const renderSection = (sectionKey) => {
    if (!normalized.sections[sectionKey]) return ''

    if (sectionKey === 'quality') {
      const rows = getQualityRows(t)
      return `
        <section class="print-label-section">
          <h3>${escapeHtml(getSectionTitle(sectionKey, t))}</h3>
          <table class="print-quality-table">
            <thead>
              <tr>
                <th>${escapeHtml(t('performance.quality.inspectItems'))}</th>
                <th>${escapeHtml(t('performance.quality.standard'))}</th>
                <th>${escapeHtml(t('performance.quality.actual'))}</th>
                <th>${escapeHtml(t('performance.quality.result'))}</th>
              </tr>
            </thead>
            <tbody>
              ${rows.map(row => `
                <tr>
                  <td>${escapeHtml(row.item)}</td>
                  <td>${escapeHtml(row.standard)}</td>
                  <td>${escapeHtml(row.actual)}</td>
                  <td>${escapeHtml(row.result)}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </section>
      `
    }

    return `
      <section class="print-label-section">
        <h3>${escapeHtml(getSectionTitle(sectionKey, t))}</h3>
        <div class="print-field-grid">
          ${(fields[sectionKey] || []).map(field => `
            <div class="print-field">
              <span class="print-field-label">${escapeHtml(field.label)}</span>
              <span class="print-field-value">${escapeHtml(field.value)}</span>
            </div>
          `).join('')}
        </div>
      </section>
    `
  }

  return `
    <article class="print-label-page${normalized.appearance.enhanced ? ' print-label-page--enhanced' : ''}">
      <header class="print-label-header">
        <h2>${escapeHtml(getPrintTemplateTitle(normalized, t))}</h2>
        <div>${escapeHtml(t('performance.common.labelNo'))}: ${escapeHtml(label?.coilNo || '-')}</div>
      </header>
      ${PRINT_SECTION_KEYS.map(renderSection).join('')}
      <footer class="print-label-footer">
        <span>${escapeHtml(t('performance.common.printTime'))}: ${escapeHtml(printTime)}</span>
        <span>${escapeHtml(t('performance.common.operatorSign'))}: ________________</span>
      </footer>
    </article>
  `
}

export const getPrintDocumentCss = (template) => {
  const normalized = normalizePrintTemplate(template)
  const margin = normalized.margin
  const paperSize = getPaperSize(normalized)

  return `
    @page {
      size: ${paperSize} ${normalized.orientation};
      margin: ${margin.top}mm ${margin.right}mm ${margin.bottom}mm ${margin.left}mm;
    }

    * {
      box-sizing: border-box;
    }

    html,
    body {
      margin: 0;
      padding: 0;
      background: #ffffff;
      color: #000000;
      font-family: Arial, "Microsoft YaHei", sans-serif;
      font-size: ${normalized.fontSize}px;
      line-height: 1.45;
    }

    .print-label-document {
      width: 100%;
    }

    .print-label-page {
      width: 100%;
      min-height: calc(100vh - 1px);
      padding: 8mm;
      border: 1px solid #000000;
      break-after: page;
      page-break-after: always;
      transform: scale(${normalized.scale / 100});
      transform-origin: top left;
    }

    .print-label-page--enhanced {
      print-color-adjust: exact;
      -webkit-print-color-adjust: exact;
    }

    .print-label-page:last-child {
      break-after: auto;
      page-break-after: auto;
    }

    .print-label-header {
      display: flex;
      flex-direction: column;
      gap: 3mm;
      align-items: center;
      padding-bottom: 5mm;
      border-bottom: 1px solid #000000;
      text-align: center;
    }

    .print-label-header h2 {
      margin: 0;
      font-size: 1.6em;
      line-height: 1.2;
    }

    .print-label-section {
      padding-top: 5mm;
    }

    .print-label-section h3 {
      margin: 0 0 3mm;
      font-size: 1.15em;
    }

    .print-field-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      border-top: 1px solid #000000;
      border-left: 1px solid #000000;
    }

    .print-field {
      display: grid;
      grid-template-columns: 40% 60%;
      min-height: 9mm;
      border-right: 1px solid #000000;
      border-bottom: 1px solid #000000;
    }

    .print-field-label,
    .print-field-value {
      padding: 2mm;
      overflow-wrap: anywhere;
    }

    .print-field-label {
      border-right: 1px solid #000000;
      font-weight: 700;
    }

    .print-label-page--enhanced .print-field-label,
    .print-label-page--enhanced .print-quality-table th {
      background: #f5f5f5;
      font-weight: 700;
    }

    .print-quality-table {
      width: 100%;
      border-collapse: collapse;
    }

    .print-quality-table th,
    .print-quality-table td {
      border: 1px solid #000000;
      padding: 2mm;
      text-align: left;
      vertical-align: top;
    }

    .print-label-footer {
      display: flex;
      justify-content: space-between;
      gap: 8mm;
      margin-top: 7mm;
      padding-top: 5mm;
      border-top: 1px solid #000000;
      white-space: nowrap;
    }

    @media screen {
      body {
        padding: 16px;
        background: #f5f5f5;
      }

      .print-label-page {
        max-width: 900px;
        min-height: auto;
        margin: 0 auto 16px;
        background: #ffffff;
      }
    }
  `
}

export const renderPrintDocumentHtml = (labels, template, t) => {
  const safeLabels = Array.isArray(labels) ? labels : []
  return `
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>${escapeHtml(t('performance.printSettings.printDocumentTitle'))}</title>
        <style>${getPrintDocumentCss(template)}</style>
      </head>
      <body>
        <main class="print-label-document">
          ${safeLabels.map(label => renderLabelHtml(label, template, t)).join('')}
        </main>
      </body>
    </html>
  `
}
