/** 按真实观测时刻显示缺测与同刻多样本，不虚构中间时间或同刻先后。 */
export function splitObservedPoints(points, intervalSeconds, origin = 0) {
  const source = points.map(point => {
    const milliseconds = Date.parse(point.observedAt)
    if (!Number.isFinite(milliseconds)) return null
    const fraction = String(point.observedAt).match(/\.(\d+)(?=Z|[+-]\d{2}:\d{2}$)/i)?.[1] || ''
    const remainingMicroseconds = Number(fraction.padEnd(6, '0').slice(3, 6))
    return { ...point, time: (milliseconds - origin) + remainingMicroseconds / 1000,
      instant: BigInt(milliseconds) * 1000n + BigInt(remainingMicroseconds) }
  }).filter(Boolean)
  const counts = new Map()
  const coordinates = new Map()
  let precisionLimited = false
  for (const point of source) counts.set(point.instant, (counts.get(point.instant) || 0) + 1)
  for (const point of source) {
    if (coordinates.has(point.time) && coordinates.get(point.time) !== point.instant) precisionLimited = true
    else coordinates.set(point.time, point.instant)
  }
  const line = []
  const simultaneous = []
  let previous = null
  let lastDuplicate = null
  for (const point of source) {
    const value = point.present === false ? null : point.value
    if (counts.get(point.instant) > 1) {
      if (lastDuplicate !== point.instant) line.push([point.time, null, point.observedAt])
      if (value !== null && value !== undefined) simultaneous.push([point.time, value, point.observedAt])
      previous = null
      lastDuplicate = point.instant
      continue
    }
    lastDuplicate = null
    if (previous !== null && Number.isFinite(intervalSeconds) && intervalSeconds > 0 &&
        point.instant - previous > BigInt(Math.round(intervalSeconds * 1000000))) line.push([point.time, null, point.observedAt])
    line.push([point.time, value ?? null, point.observedAt])
    previous = value === null || value === undefined ? null : point.instant
  }
  return { line, simultaneous, precisionLimited }
}
