import type { CsvRow, LineageGraph, PlcPoint, TableSchema } from '../types'

export function parseCsv(text: string): CsvRow[] {
  const rows = parseCsvRows(text.trim())
  if (rows.length < 2) {
    return []
  }
  const headers = rows[0].map((header) => header.trim())
  return rows.slice(1).map((row) => {
    const item: CsvRow = {}
    headers.forEach((header, index) => {
      item[header] = row[index] ?? ''
    })
    return item
  })
}

function parseCsvRows(text: string): string[][] {
  const rows: string[][] = []
  let current = ''
  let row: string[] = []
  let inQuotes = false

  for (let index = 0; index < text.length; index += 1) {
    const char = text[index]
    const next = text[index + 1]
    if (char === '"' && inQuotes && next === '"') {
      current += '"'
      index += 1
      continue
    }
    if (char === '"') {
      inQuotes = !inQuotes
      continue
    }
    if (char === ',' && !inQuotes) {
      row.push(current)
      current = ''
      continue
    }
    if ((char === '\n' || char === '\r') && !inQuotes) {
      if (char === '\r' && next === '\n') {
        index += 1
      }
      row.push(current)
      rows.push(row)
      row = []
      current = ''
      continue
    }
    current += char
  }
  row.push(current)
  rows.push(row)
  return rows.filter((item) => item.some((cell) => cell.trim().length > 0))
}

export function parseTableSchema(text: string): TableSchema {
  return JSON.parse(text) as TableSchema
}

export function parseLineageGraph(text: string): LineageGraph {
  return JSON.parse(text) as LineageGraph
}

export function parsePlcPointsYaml(text: string): PlcPoint[] {
  const points: PlcPoint[] = []
  let plcKey = ''
  let groupName = ''
  let dbNumber = ''
  let current: Partial<PlcPoint> | null = null

  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.trim()
    if (!line || line.startsWith('#')) {
      continue
    }
    const plcMatch = rawLine.match(/^([A-Za-z0-9_-]+):\s*$/)
    if (plcMatch && !rawLine.startsWith(' ')) {
      plcKey = plcMatch[1]
      continue
    }
    const groupMatch = rawLine.match(/^  - name:\s*(.+)$/)
    if (groupMatch) {
      if (current?.pointName) {
        points.push(normalizePoint(current, plcKey, groupName, dbNumber))
        current = null
      }
      groupName = groupMatch[1].trim()
      continue
    }
    const nestedGroupMatch = rawLine.match(/^  groups:\s*$/)
    if (nestedGroupMatch) {
      continue
    }
    const dbMatch = line.match(/^db_number:\s*(.+)$/)
    if (dbMatch) {
      dbNumber = dbMatch[1].trim()
      continue
    }
    const pointMatch = rawLine.match(/^    - name:\s*(.+)$/)
    if (pointMatch) {
      if (current?.pointName) {
        points.push(normalizePoint(current, plcKey, groupName, dbNumber))
      }
      current = {
        pointName: pointMatch[1].trim(),
        plcKey,
        groupName,
        dbNumber
      }
      continue
    }
    if (!current) {
      continue
    }
    const typeMatch = line.match(/^type:\s*(.+)$/)
    if (typeMatch) {
      current.dataType = typeMatch[1].trim()
    }
    const sourceNameMatch = line.match(/^source_name:\s*(.+)$/)
    if (sourceNameMatch) {
      current.sourceName = sourceNameMatch[1].trim()
    }
    const offsetMatch = line.match(/^offset:\s*(.+)$/)
    if (offsetMatch) {
      current.offset = offsetMatch[1].trim()
    }
    const descMatch = line.match(/^desc:\s*(.+)$/)
    if (descMatch) {
      current.description = descMatch[1].trim()
    }
  }
  if (current?.pointName) {
    points.push(normalizePoint(current, plcKey, groupName, dbNumber))
  }
  return points
}

function normalizePoint(
  point: Partial<PlcPoint>,
  plcKey: string,
  groupName: string,
  dbNumber: string
): PlcPoint {
  return {
    plcKey: point.plcKey || plcKey,
    groupName: point.groupName || groupName,
    dbNumber: point.dbNumber || dbNumber,
    pointName: point.pointName || '',
    sourceName: point.sourceName || '',
    dataType: point.dataType || '',
    offset: point.offset || '',
    description: point.description || ''
  }
}
