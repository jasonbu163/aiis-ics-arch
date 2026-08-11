export type CsvRow = Record<string, string>

export interface ImportedFiles {
  lineageGraph?: LineageGraph
  frontendSources: CsvRow[]
  frontendI18nRefs: CsvRow[]
  frontendComponentRefs: CsvRow[]
  frontendApiRefs: CsvRow[]
  frontendApiUriRefs: CsvRow[]
  frontendLinks: CsvRow[]
  backendRoutes: CsvRow[]
  backendRouteUriRefs: CsvRow[]
  backendModels: CsvRow[]
  backendRouteModelLinks: CsvRow[]
  tableSchema?: TableSchema
}

export interface TableSchema {
  tables?: TableSchemaTable[]
}

export interface TableSchemaTable {
  table_name?: string
  table?: string
  columns?: TableSchemaColumn[]
}

export interface TableSchemaColumn {
  name?: string
  field_name?: string
  field_type?: string
  data_type?: string
  nullable?: boolean
  comment?: string
}

export interface PlcPoint {
  plcKey: string
  groupName: string
  dbNumber: string
  pointName: string
  sourceName: string
  dataType: string
  offset: string
  description: string
}

export interface LineageGraph {
  version: number
  generated_at?: string
  stats?: Record<string, number>
  nodes: LineageGraphNode[]
  edges: LineageGraphEdge[]
}

export interface LineageGraphNode {
  id: string
  kind: string
  title: string
  subtitle?: string
  evidence?: string
  ordinal?: number
  position?: {
    x: number
    y: number
  }
}

export interface LineageGraphEdge {
  id: string
  source: string
  target: string
  label: string
  evidence?: string
}

export interface StudioNodeData {
  title: string
  label?: string
  subtitle: string
  kind: string
  evidence?: string
  ordinal?: number
}

export interface MappingDraftEdge {
  id: string
  source: string
  target: string
  sourceHandle?: string | null
  targetHandle?: string | null
}
