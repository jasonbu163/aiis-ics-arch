import type { Edge, Node } from '@vue-flow/core'
import type { CsvRow, ImportedFiles, StudioNodeData, TableSchemaTable } from '../types'

type StudioNode = Node<StudioNodeData>

export function buildGraph(data: ImportedFiles): { nodes: StudioNode[]; edges: Edge[] } {
  const nodes = new Map<string, StudioNode>()
  const edges = new Map<string, Edge>()
  const i18nValues = collectI18nValues(data.frontendI18nRefs)

  const addNode = (id: string, kind: string, title: string, subtitle = '', evidence = '') => {
    if (nodes.has(id)) {
      return
    }
    nodes.set(id, {
      id,
      type: 'lineage',
      position: { x: 0, y: 0 },
      class: `node-${kind}`,
      data: { title, label: title, subtitle, kind, evidence }
    })
  }

  const addEdge = (source: string, target: string, label: string, evidence = '', animated = false) => {
    const id = `${source}->${target}:${label}`
    if (edges.has(id)) {
      return
    }
    edges.set(id, {
      id,
      source,
      target,
      label,
      animated,
      data: { evidence }
    })
  }

  for (const row of data.frontendI18nRefs) {
    if (row.record_kind === 'definition' && row.locale_file) {
      addNode(nodeId('locale', row.locale_file), 'locale', fileLabel(row.locale_file), row.locale, row.row_id)
    }
    if (row.i18n_key) {
      addNode(nodeId('i18n', row.i18n_key), 'i18n', row.i18n_key, (i18nSubtitle(i18nValues.get(row.i18n_key)) || row.value || row.source_file || '').slice(0, 160), row.row_id)
    }
  }

  for (const row of data.frontendComponentRefs) {
    const componentId = row.component_id || row.source_file
    if (!componentId) {
      continue
    }
    addNode(nodeId('component', componentId), 'component', fileLabel(componentId), row.route_path || row.source_kind, row.row_id)
  }

  for (const row of data.frontendApiRefs) {
    const apiId = row.api_id || apiName(row)
    if (!apiId) {
      continue
    }
    addNode(nodeId('api', apiId), 'api', apiId, row.frontend_api_path, row.row_id)
  }

  for (const row of data.backendRoutes) {
    const currentRouteLabel = row.route_id || routeLabel(row)
    if (!currentRouteLabel) {
      continue
    }
    addNode(nodeId('route', currentRouteLabel), 'route', currentRouteLabel, row.backend_function, row.row_id)
  }

  for (const row of data.backendModels) {
    if (!row.model_class) {
      continue
    }
    const modelId = nodeId('model', row.model_class)
    addNode(modelId, 'model', row.model_class, row.backend_module || row.model_file, row.row_id)
    if (row.table_name) {
      const tableId = nodeId('table', row.table_name)
      addNode(tableId, 'table', row.table_name, row.model_file || row.backend_module, row.row_id)
      addEdge(modelId, tableId, 'maps_to_table', row.row_id)
    }
  }

  for (const row of data.frontendLinks) {
    const sourceKind = linkKind(row.from_kind)
    const targetKind = linkKind(row.to_kind)
    if (!sourceKind || !targetKind || !row.from_id || !row.to_id) {
      continue
    }
    addEdge(nodeId(sourceKind, row.from_id), nodeId(targetKind, row.to_id), row.edge_type || 'link', row.row_id)
  }

  const routesByUriKey = new Map<string, CsvRow[]>()
  for (const row of data.backendRouteUriRefs) {
    if (!row.uri_key || !row.route_id) {
      continue
    }
    routesByUriKey.set(row.uri_key, [...(routesByUriKey.get(row.uri_key) ?? []), row])
  }

  for (const row of data.frontendApiUriRefs) {
    if (!row.uri_key || !row.api_id) {
      continue
    }
    for (const route of routesByUriKey.get(row.uri_key) ?? []) {
      if (!route.route_id) {
        continue
      }
      const evidence = [row.row_id, route.row_id].filter(Boolean).join('|') || row.uri_key
      addEdge(nodeId('api', row.api_id), nodeId('route', route.route_id), 'matches_route', evidence)
    }
  }

  for (const row of data.backendRouteModelLinks) {
    const currentRouteLabel = row.route_id || routeLabel(row)
    if (!currentRouteLabel || !row.model_class) {
      continue
    }
    const routeId = nodeId('route', currentRouteLabel)
    const modelId = nodeId('model', row.model_class)
    addNode(modelId, 'model', row.model_class, row.evidence_type, row.row_id)
    addEdge(routeId, modelId, 'uses_model', row.row_id)
    if (row.table_name) {
      const tableId = nodeId('table', row.table_name)
      addNode(tableId, 'table', row.table_name, row.model_file || row.backend_module, row.row_id)
      addEdge(modelId, tableId, 'maps_to_table', row.row_id)
    }
  }

  for (const table of data.tableSchema?.tables ?? []) {
    const tableName = getTableName(table)
    if (!tableName) {
      continue
    }
    const tableId = nodeId('table', tableName)
    addNode(tableId, 'table', tableName, 'business table')
    for (const column of table.columns ?? []) {
      const fieldName = column.field_name || column.name
      if (!fieldName) {
        continue
      }
      const fieldId = nodeId('field', `${tableName}.${fieldName}`)
      addNode(fieldId, 'field', fieldName, column.field_type || column.data_type || '', tableName)
      addEdge(tableId, fieldId, 'field')
    }
  }

  return layoutGraph([...nodes.values()], [...edges.values()])
}

function layoutGraph(nodes: StudioNode[], edges: Edge[]): { nodes: StudioNode[]; edges: Edge[] } {
  const order = ['locale', 'i18n', 'component', 'api', 'route', 'model', 'table', 'field', 'plc']
  const grouped = new Map<string, StudioNode[]>()
  for (const node of nodes) {
    const kind = node.data?.kind ?? 'unknown'
    grouped.set(kind, [...(grouped.get(kind) ?? []), node])
  }
  const positioned: StudioNode[] = []
  const nodeColumnWidth = 340
  const nodeRowHeight = 104

  for (const [laneIndex, kind] of order.entries()) {
    const group = grouped.get(kind) ?? []
    group.forEach((node, index) => {
      const data = node.data ?? {
        title: '',
        label: '',
        subtitle: '',
        kind,
        evidence: ''
      }
      positioned.push({
        ...node,
        data: {
          title: data.title,
          label: data.label,
          subtitle: data.subtitle,
          kind: data.kind,
          evidence: data.evidence,
          ordinal: index + 1
        },
        position: {
          x: laneIndex * nodeColumnWidth,
          y: 52 + index * nodeRowHeight
        }
      })
    })
  }
  return { nodes: positioned, edges }
}

function nodeId(kind: string, value: string): string {
  return `${kind}:${value || 'unknown'}`
}

function fileLabel(value: string): string {
  return value.split('/').slice(-2).join('/')
}

function splitList(value: string): string[] {
  return value
    .split(';')
    .map((item) => item.trim())
    .filter(Boolean)
}

function getTableName(table: TableSchemaTable): string {
  return table.table_name || table.table || ''
}

function apiName(row: CsvRow): string {
  return `${row.api_module || ''}.${row.api_function || ''}`.replace(/^\./, '').replace(/\.$/, '')
}

function routeLabel(row: CsvRow): string {
  const method = row.method || ''
  const path = row.backend_route || row.frontend_api_path || ''
  return `${method} ${path}`.trim()
}

function linkKind(value: string): string {
  const map: Record<string, string> = {
    LocaleFile: 'locale',
    I18nKey: 'i18n',
    Component: 'component',
    API: 'api'
  }
  return map[value] || ''
}

function collectI18nValues(rows: CsvRow[]): Map<string, Record<string, string>> {
  const result = new Map<string, Record<string, string>>()
  for (const row of rows) {
    if (row.record_kind !== 'definition' || !row.i18n_key || !row.locale || !row.value) {
      continue
    }
    result.set(row.i18n_key, {
      ...(result.get(row.i18n_key) ?? {}),
      [row.locale]: row.value
    })
  }
  return result
}

function i18nSubtitle(values?: Record<string, string>): string {
  if (!values) {
    return ''
  }
  const parts: string[] = []
  const zh = values['zh-CN'] || values.zh
  const en = values['en-US'] || values.en
  if (zh) {
    parts.push(`中: ${zh}`)
  }
  if (en) {
    parts.push(`EN: ${en}`)
  }
  if (!parts.length) {
    for (const [locale, text] of Object.entries(values).slice(0, 2)) {
      parts.push(`${locale}: ${text}`)
    }
  }
  return parts.join(' / ')
}
