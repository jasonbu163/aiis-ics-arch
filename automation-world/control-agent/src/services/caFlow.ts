/** 新版 CA 流程 JSON 与本地 IPC。 */
import { invoke } from '@tauri-apps/api/core'

export type Kind = 'int16' | 'boolean' | 'string' | 'real'
export interface Literal { type: Kind; value: string | number | boolean }
export interface Reference { node_id: string; field: string }
export type Operand = Literal | Reference
export type ConfigMap = Record<string, Operand>
interface PlcConfig { plc_ref: string; point_ref: string; value_type: Kind }
interface NodeBase { id: string; version: number }
export type FlowNode = NodeBase & (
  { type: 'plc.read'; config: PlcConfig } |
  { type: 'plc.write'; config: PlcConfig & { value: Operand } } |
  { type: 'condition.compare'; config: {left: Operand; op: 'eq'; right: Literal} } |
  { type: 'http.request'; config: {endpoint_ref: string; method: 'GET' | 'POST'; path: string; query?: ConfigMap; body?: ConfigMap} } |
  { type: 'end'; config: { result: 'matched' | 'not_matched' } }
)
export interface Edge {from_node_id: string; from_port: string; to_node_id: string}
export interface Position {x: number; y: number}
export interface Document {
  format: 'aiis.flow'
  schema_version: number
  flow: {flow_id: string; revision: number; trigger: {type: 'interval'; interval_ms: number}; entry_node_id: string; nodes: FlowNode[]; edges: Edge[]}
  layout?: {nodes: Record<string, Position>}
}
export interface Saved {document: Document; semantic_sha256: string; file_sha256: string}
export interface Issue {code: string; node_id: string | null}
export interface FlowPreview {document: Document; issues: Issue[]; status: 'new'|'identical'|'conflict'; token: string; file_sha256: string}
export const validateFlow = (document: Document) => invoke<Issue[]>('ca_flow_validate', {document})
export const listFlows = () => invoke<Saved[]>('ca_flow_list')
export const getFlow = (id: string, revision: number) => invoke<Saved>('ca_flow_get', {id, revision})
export const saveFlow = (document: Document, expected: number) => invoke<Saved>('ca_flow_save', {document, expected})
export const previewFlow = () => invoke<FlowPreview>('ca_flow_import', {token:null, copyId:null})
export const importFlow = (token: string, copyId: string | null) => invoke<Saved>('ca_flow_import', {token, copyId})
export const exportFlow = (id: string, revision: number) => invoke<Omit<Saved,'document'>>('ca_flow_export', {id, revision})
