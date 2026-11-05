/** 历史样本只读展示：仅从原样本及冻结上下文取值；JSON美化只改变字符串外的空白。 */
import type { RawSample } from '../services/localAcquisition'

type JsonObject = Record<string, unknown>
const object = (value: unknown): JsonObject => value !== null && typeof value === 'object' && !Array.isArray(value) ? value as JsonObject : {}
const text = (value: unknown): string => typeof value === 'string' ? value : ''
function parseObject(value: string): JsonObject {
  try { return object(JSON.parse(value)) } catch { return {} }
}
function name(context: JsonObject, collection: string, id: string): string {
  const items = context[collection]
  return Array.isArray(items) ? text(object(items.find(item => object(item).id === id)).name) || id : id
}
export function sampleValue(value: unknown): string {
  return value === null || value === undefined ? '—' : JSON.stringify(value)
}
export function sampleDetails(raw: RawSample) {
  const payload = parseObject(raw.payload), context = parseObject(raw.context)
  if (!payload.sampleId || !payload.points || Array.isArray(payload.points) || typeof payload.points !== 'object') return null
  const rows = Object.entries(object(payload.points)).map(([id, value]) => {
    const fact = object(value), definition = object(fact.definition), address = object(definition.address)
    return {
      id,
      name: text(definition.name) || text(definition.sourcePath) || id,
      sourcePath: text(definition.sourcePath),
      dataType: text(definition.dataType),
      value: sampleValue(fact.value),
      address: Number.isInteger(address.offset) ? `${address.offset}${Number.isInteger(address.bit) ? `.${address.bit}` : ''}` : '—',
      observedAt: text(fact.observedAt),
      quality: text(fact.quality),
      reason: text(fact.reason)
    }
  })
  return {
    plc: name(context, 'plcs', text(payload.plcId)),
    group: name(context, 'groups', text(payload.groupId)),
    dbNumber: typeof payload.dbNumber === 'number' ? String(payload.dbNumber) : '—',
    savedAt: text(payload.savedAt),
    origin: text(payload.origin),
    good: rows.filter(row => row.quality === 'good').length,
    rows
  }
}

/** 不重新编码数字、Unicode或转义序列，避免格式化视图产生精度/词法差异；原文与SHA始终另存。 */
export function formatSampleJson(raw: string): string {
  try { JSON.parse(raw) } catch { return raw }
  let result = '', depth = 0, quoted = false, escaped = false, previous = ''
  const newline = () => '\n' + '  '.repeat(depth)
  for (let i = 0; i < raw.length; i++) {
    const char = raw[i]
    if (quoted) {
      result += char
      if (escaped) escaped = false
      else if (char === '\\') escaped = true
      else if (char === '"') quoted = false
      continue
    }
    if (/\s/.test(char)) continue
    if (char === '"') { quoted = true; result += char }
    else if (char === '{' || char === '[') {
      result += char; depth++
      let next = i + 1
      while (/\s/.test(raw[next] ?? '') && next < raw.length) next++
      if (raw[next] !== '}' && raw[next] !== ']') result += newline()
    } else if (char === '}' || char === ']') {
      depth--
      if (previous !== '{' && previous !== '[') result += newline()
      result += char
    } else if (char === ',') result += ',' + newline()
    else if (char === ':') result += ': '
    else result += char
    previous = char
  }
  return result
}
