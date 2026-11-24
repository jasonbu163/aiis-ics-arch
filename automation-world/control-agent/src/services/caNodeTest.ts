/** 单节点测试预览、一次性确认及审计记录 IPC。 */
import { invoke } from '@tauri-apps/api/core'
import type { Document, FlowNode, Literal } from './caFlow'
export interface Intent {flow_id:string; revision:number; node:FlowNode; document:Document; real:boolean; timeout_ms:number; inputs:Record<string,Literal>; sample:Literal|null; fake_outcome:string|null}
export interface TestResult {
  id:string; status:string; mode:'simulate'|'fake'|'real'; node_id:string; flow_id:string;
  started_at:string; elapsed_ms?:number; output?:Record<string,unknown>; target?:unknown; actual_io:boolean;
}
export interface Preview {token:string; mode:string; target?:unknown; side_effect:boolean; confirmation_required:boolean; inputs:unknown; timeout_ms:number}
export const previewTest = (intent:Intent) => invoke<Preview>('ca_node_test_preview',{intent})
export const runTest = (token:string,confirmed:boolean) => invoke<TestResult>('ca_node_test_run',{token,confirmed})
export const listTests = () => invoke<TestResult[]>('ca_node_test_list')
