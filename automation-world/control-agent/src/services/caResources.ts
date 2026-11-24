/** 本机逻辑资源、来源点表和绑定 IPC。 */
import { invoke } from '@tauri-apps/api/core'
export interface PlcTarget {host:string; port:number; rack:number; slot:number; local_tsap?:number; remote_tsap?:number}
export interface Point {id:string; name:string; data_type:string; byte_offset:number; bit?:number; source_enabled:boolean; source_path?:string; display_name?:string; display_names?:Record<string,string>; description?:string}
export interface Catalog {
  origin:{kind:string; profile_id:string; plc_id:string}
  export:{producer:string; profile_id:string; config_state:string; revision_id:string; exported_at:string; payload_sha256:string}
  plc:{name:string; connection:PlcTarget}
  dbs:{id:string; name:string; number:number; size_bytes:number; source_enabled?:boolean; points:Point[]}[]
}
export interface Plc {id:string; catalog:Catalog; file_sha256:string; binding:PlcTarget|null; point_aliases:Record<string,string>}
export interface Resources { plcs:Plc[]; http:{id:string; base_url:string; header_names:string[]}[]; fake:boolean }
interface BlockSnapshot {number:number; name:string; size_bytes:number; source_enabled:boolean|null}
interface CatalogDiff {
  added:string[];
  removed:string[];
  changed:string[];
  connection_changed:boolean;
  db_changes:{id:string; before:BlockSnapshot|null; after:BlockSnapshot|null}[];
}
export interface CatalogPreview {catalog:Catalog; file_sha256:string; status:'new'|'identical'|'changed'; existing:string|null; diff:CatalogDiff|null; token:string}
export const listResources = () => invoke<Resources>('ca_resource_list')
export const previewCatalog = () => invoke<CatalogPreview>('ca_plc_catalog_preview')
export const commitCatalog = (token:string,alias:string) => invoke<{id:string}>('ca_plc_catalog_commit',{token,alias})
export const bindResource = (binding:{kind:'http'; id:string; target:{base_url:string;headers:Record<string,string>}}|{kind:'plc'; id:string;target:PlcTarget}|{kind:'point'; id:string;point_id:string;alias:string}) => invoke<void>('ca_resource_save_binding',{binding})
