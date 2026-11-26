/** 上海时间转换、精确文本录价与本地化项目显示。 */
const businessParts = value => Object.fromEntries(new Intl.DateTimeFormat('en-CA', {
  timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit',
  hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23'
}).formatToParts(new Date(value)).map(part => [part.type, part.value]))
export const businessDate = value => { const p = businessParts(value); return `${p.year}-${p.month}-${p.day}` }
export const businessDateTime = value => { const p = businessParts(value); return `${p.year}-${p.month}-${p.day} ${p.hour}:${p.minute}:${p.second}` }
// Resolve picker civil fields in Shanghai independently of the browser timezone.
// Multiple instants in a repeated hour choose the earliest (fold=0); gaps are invalid.
export const encodeObservedAt = value => {
  if (!value) return null
  const civil = Date.parse(`${value}Z`)
  if (!Number.isFinite(civil)) throw new Error('invalid_observed_at')
  const offsets = new Set()
  for (let hour = -14; hour <= 14; hour++) {
    const sample = civil + hour * 3600000
    offsets.add(Date.parse(`${businessDateTime(sample).replace(' ', 'T')}Z`) - sample)
  }
  const candidates = [...offsets].map(offset => civil - offset)
    .filter(instant => businessDateTime(instant).replace(' ', 'T') === value)
  if (!candidates.length) throw new Error('nonexistent_observed_at')
  return new Date(Math.min(...candidates)).toISOString()
}

export const validPrice = value => typeof value === 'number' || typeof value === 'string'
  ? /^[+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)$/.test(String(value)) && Number(value) >= 0 && Number(value) <= 999999.9999
    && !/\.[0-9]{4}[0-9]*[1-9]/.test(String(value)) : false


export const priceItemName = (item, locale) => locale.startsWith('zh')
  ? item.nameZh || item.nameEn : item.nameEn || item.nameZh

export function priceItemUnit(item, t) {
  if (item.itemKey === 'electric' && item.unit === 'CNY/kWh') return t('energy.price.units.electric')
  if (['hydrogen', 'argon'].includes(item.itemKey) && item.unit === 'CNY/Nm³') return t('energy.price.units.gas')
  return item.unit
}
