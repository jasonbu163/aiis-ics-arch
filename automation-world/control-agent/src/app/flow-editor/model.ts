/** 编辑器的类型化参数、端口和布局辅助。 */
import type {Document, Edge, FlowNode, Kind, Literal, Position} from '../../services/caFlow'

export const palette = ['read','condition','get','post','write','end'] as const
export type Palette = typeof palette[number]
export const clone = <T>(value:T):T => JSON.parse(JSON.stringify(value))
export const fresh = ():Document => ({
  format:'aiis.flow', schema_version:1,
  flow:{flow_id:'new_flow',revision:1,trigger:{type:'interval',interval_ms:1000},entry_node_id:'',nodes:[],edges:[]},
  layout:{nodes:{}}
})
export function literal(type:Kind):Literal {
  return {type,value:type==='string'?'':type==='boolean'?false:0}
}
export function createNode(kind:Palette, id:string):FlowNode {
  const common = {id,version:1}
  if (kind==='read') return {...common,type:'plc.read',config:{plc_ref:'',point_ref:'',value_type:'int16'}}
  if (kind==='write') return {...common,type:'plc.write',config:{plc_ref:'',point_ref:'',value_type:'int16',value:literal('int16')}}
  if (kind==='condition') return {...common,type:'condition.compare',config:{left:literal('int16'),op:'eq',right:{type:'int16',value:1}}}
  if (kind==='end') return {...common,type:'end',config:{result:'matched'}}
  return {...common,type:'http.request',config:{method:kind==='post'?'POST':'GET',endpoint_ref:'',path:'/status'}}
}
export function paletteKey(node:FlowNode):Palette {
  if (node.type==='plc.read') return 'read'
  if (node.type==='plc.write') return 'write'
  if (node.type==='condition.compare') return 'condition'
  if (node.type==='end') return 'end'
  return node.config.method==='GET'?'get':'post'
}
export const ports = (node:FlowNode):string[] => node.type==='end'?[]:node.type==='condition.compare'?['true','false']:['next']
export const edgeKey = (edge:Edge) => [edge.from_node_id,edge.from_port,edge.to_node_id].join(':')
export function layoutPosition(doc:Document,id:string,index:number):Position {
  if (doc.layout?.nodes[id]) return doc.layout.nodes[id]
  let depth=0; let current=id
  while (depth<doc.flow.nodes.length) {
    const edge=doc.flow.edges.find(item=>item.to_node_id===current)
    if (!edge) break
    current=edge.from_node_id
    depth++
  }
  return {x:40+depth*205,y:70+(index%4)*100}
}
export interface Output {id:string; field:string; type:Kind; kind:Palette}
export function outputs(doc:Document,id:string):Output[] {
  const nodes = new Map(doc.flow.nodes.map(node => [node.id, node]))
  const parents = new Map<string, Set<string>>()
  const children = new Map<string, Set<string>>()
  for (const edge of doc.flow.edges) {
    const source = nodes.get(edge.from_node_id)
    if (!source || !nodes.has(edge.to_node_id) || !ports(source).includes(edge.from_port)) continue
    if (!parents.has(edge.to_node_id)) parents.set(edge.to_node_id, new Set())
    if (!children.has(edge.from_node_id)) children.set(edge.from_node_id, new Set())
    parents.get(edge.to_node_id)!.add(edge.from_node_id)
    children.get(edge.from_node_id)!.add(edge.to_node_id)
  }

  const upstream = new Map<string, Set<string>>()
  const remaining = new Map([...parents].map(([target, sources]) => [target, sources.size]))
  const ready = [...nodes.keys()].filter(node => !remaining.has(node))
  for (const node of ready) {
    let common: Set<string> | undefined
    for (const parent of parents.get(node) ?? []) {
      const path = new Set([parent, ...upstream.get(parent)!])
      common = common ? new Set([...common].filter(source => path.has(source))) : path
    }
    if (node === id) {
      const result: Output[] = []
      for (const source of common ?? []) {
        const option = nodes.get(source)!
        const label = {id: source, kind: paletteKey(option)}
        if (option.type === 'plc.read') result.push({...label, field: 'value', type: option.config.value_type})
        if (option.type === 'http.request') result.push({...label, field: 'status', type: 'int16'})
        if (option.type === 'condition.compare') result.push({...label, field: 'matched', type: 'boolean'})
      }
      return result
    }
    upstream.set(node, common ?? new Set())
    for (const child of children.get(node) ?? []) {
      const count = remaining.get(child)! - 1
      remaining.set(child, count)
      if (count === 0) ready.push(child)
    }
  }
  return []
}

/** 连线允许条件分支回到共同节点，仍限制单入口、端口复用和回环。 */
export function canConnect(doc: Document, edge: Edge): boolean {
  const {from_node_id: from, to_node_id: to, from_port: port} = edge
  const {nodes, edges, entry_node_id: entry} = doc.flow
  const source = nodes.find(node => node.id === from)
  if (!source || !nodes.some(node => node.id === to) || !ports(source).includes(port)) return false
  if (to === entry || edges.some(edge => edge.from_node_id === from && edge.from_port === port)) return false
  const seen = new Set([to])
  const pending = [to]
  for (const node of pending) {
    if (node === from) return false
    for (const edge of edges) {
      if (edge.from_node_id !== node || seen.has(edge.to_node_id)) continue
      seen.add(edge.to_node_id)
      pending.push(edge.to_node_id)
    }
  }
  return true
}
