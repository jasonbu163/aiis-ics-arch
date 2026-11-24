<!-- 节点参数面板，参数随草稿更新。 -->
<script setup lang="ts">
import { computed } from 'vue'
import {useI18n} from 'vue-i18n'
import type {ConfigMap,FlowNode,Kind,Operand,Literal} from '../../services/caFlow'
import type {Resources} from '../../services/caResources'
import {clone,literal,type Output} from './model'
import OperandField from './OperandField.vue'
import LiteralField from './LiteralField.vue'
const props=defineProps<{node:FlowNode; resources:Resources; options:Output[]}>()
const emit=defineEmits<{'change':[node:FlowNode]}>()
const {t}=useI18n()
const points=computed(()=>{
  const n=props.node
  if(n.type!=='plc.read'&&n.type!=='plc.write') return []
  const plc=props.resources.plcs.find(p=>p.id===n.config.plc_ref)
  return plc?.catalog.dbs.flatMap(db=>db.points.flatMap(p=>[
    {...p,db:db.number,reference:p.name},
    ...Object.entries(plc.point_aliases).filter(([,id])=>id===p.id).map(([reference])=>({...p,db:db.number,reference}))
  ]))??[]
})
const pointKind=(type:string):Kind|null=>type==='INT'?'int16':type==='BOOL'?'boolean':type==='REAL'?'real':type.startsWith('STRING[')?'string':null
const text=(e:Event)=>(e.target as HTMLInputElement).value
function change(f:(node:FlowNode)=>void){const n=clone(props.node);f(n);emit('change',n)}
function plc(e:Event){change(n=>{if(n.type==='plc.read'||n.type==='plc.write'){n.config.plc_ref=text(e); n.config.point_ref=''}})}
function point(e:Event){change(n=>{
  if(n.type!=='plc.read'&&n.type!=='plc.write') return
  const p=points.value.find(p=>p.reference===text(e))
  const kind=p&&pointKind(p.data_type)
  if(!p||!kind)return
  n.config.point_ref=p.reference; n.config.value_type=kind
  if(n.type==='plc.write') n.config.value=literal(kind)
})}
function left(operand:Operand){change(n=>{
  if(n.type!=='condition.compare') return
  n.config.left=operand
  const kind='type' in operand?operand.type:props.options.find(x=>x.id===operand.node_id&&x.field===operand.field)?.type
  if(kind&&kind!==n.config.right.type)n.config.right=literal(kind)
})}
function right(value:Literal){change(n=>{if(n.type==='condition.compare')n.config.right=value})}
function http(e:Event,key:'endpoint_ref'|'path'){change(n=>{if(n.type==='http.request')n.config[key]=text(e)})}
function row(section:'query'|'body',key:string,operand?:Operand,nextKey?:string){
  change(n=>{
    if(n.type!=='http.request')return
    const map:ConfigMap={...n.config[section]}
    if(nextKey!==undefined){
      if(!nextKey||!(/^[A-Za-z_][A-Za-z0-9_-]*$/).test(nextKey)||(nextKey!==key&&nextKey in map))return
      map[nextKey]=map[key]
      if(nextKey!==key) delete map[key]
    }else if(operand)map[key]=operand
    else delete map[key]
    n.config[section]=map
  })
}
function add(section:'query'|'body'){const n=props.node;if(n.type!=='http.request')return;let i=1;while(n.config[section]?.['field_'+i])i++;row(section,'field_'+i,literal('int16'))}
</script>
<template>
  <div class="ca-fields">
    <template v-if="node.type==='plc.read'||node.type==='plc.write'">
      <label>{{t('flow-editor.plc')}}
        <select :value="node.config.plc_ref" @change="plc">
          <option value="">{{t('flow-editor.select')}}</option>
          <option v-for="resource in resources.plcs" :key="resource.id">{{resource.id}}</option>
        </select>
      </label>
      <label>{{t('flow-editor.point')}}
        <select :value="node.config.point_ref" @change="point">
          <option value="">{{t('flow-editor.select')}}</option>
          <option v-for="p in points" :key="p.reference" :value="p.reference" :disabled="!pointKind(p.data_type)">
            DB{{p.db}} · {{p.reference}} · {{p.data_type}}
          </option>
        </select>
      </label>
      <small>{{ t('flow-editor.pointCoverage') }}</small>
      <OperandField v-if="node.type==='plc.write'" :options="options" :type="node.config.value_type" :model-value="node.config.value"
        @update:model-value="value=>change(n=>{if(n.type==='plc.write') n.config.value=value})" />
    </template>
    <template v-else-if="node.type==='condition.compare'">
      <OperandField :options="options" :model-value="node.config.left" @update:model-value="left" />
      <LiteralField :model-value="node.config.right" :label="t('flow-editor.equals')" @update:model-value="right" />
    </template>
    <template v-else-if="node.type==='http.request'">
      <label>{{t('flow-editor.http')}}
        <select :value="node.config.endpoint_ref" @change="http($event,'endpoint_ref')">
          <option value="">{{t('flow-editor.select')}}</option>
          <option v-for="resource in resources.http" :key="resource.id">{{resource.id}}</option>
        </select>
      </label>
      <label>{{t('flow-editor.path')}}<input :value="node.config.path" placeholder="/status" @change="http($event,'path')"></label>
      <fieldset v-for="section in (node.config.method==='POST'?(['query','body'] as const):(['query'] as const))" :key="section">
        <legend>{{t('flow-editor.'+section)}}</legend>
        <div v-for="(value,key) in node.config[section]" :key="key" class="ca-fields">
          <label>{{t('flow-editor.fieldName')}}<input :value="key" @change="row(section,String(key),undefined,text($event))"></label>
          <OperandField :options="options" :model-value="value" @update:model-value="row(section,String(key),$event)" />
          <button type="button" @click="row(section,String(key))">{{t('flow-editor.removeField')}}</button>
        </div>
        <button type="button" @click="add(section)">{{t('flow-editor.addField')}}</button>
      </fieldset>
    </template>
    <label v-else>{{t('flow-editor.endResult')}}
      <select :value="node.config.result" @change="change(n=>{if(n.type==='end')n.config.result=text($event) as 'matched'|'not_matched'})">
        <option value="matched">{{t('flow-editor.matched')}}</option>
        <option value="not_matched">{{t('flow-editor.notMatched')}}</option>
      </select>
    </label>
  </div>
</template>
