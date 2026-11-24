<!-- 单节点模拟、目标预览、明确确认和审计结果。 -->
<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type {Document,FlowNode,Kind,Literal,Operand} from '../../services/caFlow'
import {previewTest,runTest,type Preview,type TestResult} from '../../services/caNodeTest'
import {literal,type Output} from '../flow-editor/model'
import LiteralField from '../flow-editor/LiteralField.vue'
const props=defineProps<{node:FlowNode; document:Document; options:Output[]; flowId:string; revision:number; records:TestResult[]; fake:boolean}>()
const emit=defineEmits<{done:[]}>()
const {t}=useI18n()
const allowedReal=computed(()=>props.node.type==='http.request'||props.node.type==='plc.read')
const readType=computed(()=>props.node.type==='plc.read'?props.node.config.value_type:'int16')
const real=ref(false)
const timeout=ref(3000)
const fakeOutcome=ref('success')
const sample=ref<Literal|null>(null)
const inputs=reactive<Record<string,Literal>>({})
const outcome=ref<TestResult>()
const preview=ref<Preview>()
const error=ref('')
const busy=ref(false)
const confirm=ref(false)
const needs=computed(()=>{
  const n=props.node
  const result=new Map<string,Kind>()
  const add=(o:Operand,fallback:Kind)=>{
    if(!('node_id' in o))return
    result.set(o.node_id+'.'+o.field,props.options.find(x=>x.id===o.node_id&&x.field===o.field)?.type??fallback)
  }
  if(n.type==='condition.compare') add(n.config.left,n.config.right.type)
  if(n.type==='plc.write') add(n.config.value,n.config.value_type)
  if(n.type==='http.request') for(const o of [...Object.values(n.config.body??{}),...Object.values(n.config.query??{})])add(o,'int16')
  return [...result]
})
watch([()=>props.document,real,timeout,fakeOutcome],()=>{preview.value=undefined; outcome.value=undefined;confirm.value=false;error.value=''})
watch(readType,()=>{sample.value=null})
function invalidate(){preview.value=undefined;confirm.value=false;outcome.value=undefined}
function setInput(key:string,value:Literal){inputs[key]=value;invalidate()}
function pickSaved(key:string,type:Kind,event:Event){
  const id=(event.target as HTMLSelectElement).value
  const value=props.records.find(record=>record.id===id)?.output?.[key.split('.').at(-1)!]
  if(typeof value==='string'||typeof value==='boolean'||typeof value==='number')setInput(key,{type,value})
}
function available(key:string,type:Kind){
  const [node,field]=key.split('.')
  return props.records.filter(r=>{
    const value=r.output?.[field]
    return r.mode==='simulate'&&r.flow_id===props.flowId&&r.node_id===node&&
      (typeof value===(type==='int16'||type==='real'?'number':type))
  })
}
async function prepare(){
  busy.value=true;error.value='';invalidate()
  try{
    const missing=needs.value.find(([key])=>!inputs[key])
    if(missing)throw new Error(t('flow-editor.test_input_missing')+' · '+missing[0])
    preview.value=await previewTest({flow_id:props.flowId,revision:props.revision,node:props.node,document:props.document,real:real.value,
      timeout_ms:timeout.value,inputs:Object.fromEntries(needs.value.map(([key])=>[key,inputs[key]])),sample:sample.value,
      fake_outcome:props.fake&&real.value?fakeOutcome.value:null})
  }catch(e){error.value=String(e)}finally{busy.value=false}
}
async function run(){
  if(!preview.value)return
  const runToken=preview.value.token
  const confirmed=confirm.value
  invalidate();busy.value=true;error.value=''
  try{outcome.value=await runTest(runToken,confirmed);emit('done')}
  catch(e){error.value=String(e)}finally{busy.value=false}
}
</script>
<template>
  <div class="ca-fields">
    <label>{{t('flow-editor.mode')}}
      <select v-model="real" :disabled="!allowedReal||busy">
        <option :value="false">{{t('flow-editor.simulate')}}</option><option :value="true">{{t(fake?'flow-editor.fake':'flow-editor.real')}}</option>
      </select>
    </label>
    <label>{{t('flow-editor.timeout')}}<input v-model.number="timeout" type="number" min="100" max="10000" :disabled="busy"></label>
    <label v-if="fake&&real">{{t('flow-editor.scenario')}}
      <select v-model="fakeOutcome"><option value="success">{{t('flow-editor.completed')}}</option><option value="before_send">{{t('flow-editor.failed_before_send')}}</option><option value="unknown">{{t('flow-editor.unknown')}}</option></select>
    </label>
    <template v-if="node.type==='plc.read'&&!real">
      <LiteralField :model-value="sample??literal(readType)" :label="t('flow-editor.sample')+' · '+readType" @update:model-value="value=>{sample=value;invalidate()}" />
      <button v-if="sample===null" type="button" @click="sample=literal(readType)">{{t('flow-editor.useValue')}}</button>
    </template>
    <fieldset v-for="[key,kind] in needs" :key="key">
      <legend>{{key}} · {{kind}}</legend>
      <LiteralField :model-value="inputs[key]??literal(kind)" :label="t('flow-editor.manualInput')" @update:model-value="setInput(key,$event)" />
      <button v-if="!inputs[key]" type="button" @click="setInput(key,literal(kind))">{{t('flow-editor.useValue')}}</button>
      <label v-if="available(key,kind).length">{{t('flow-editor.savedSample')}}
        <select value="" @change="pickSaved(key,kind,$event)"><option value="">{{t('flow-editor.select')}}</option><option v-for="r in available(key,kind)" :key="r.id" :value="r.id">{{r.started_at}} · {{r.output?.[key.split('.').at(-1)!]}}</option></select>
      </label>
    </fieldset>
    <button type="button" :disabled="busy" @click="prepare">{{t('flow-editor.previewTarget')}}</button>
    <p v-if="error" role="alert" class="ca-error">{{ t('flow-editor.'+error) === 'flow-editor.'+error ? error : t('flow-editor.'+error) }}</p>
    <template v-if="preview">
      <pre>{{JSON.stringify({mode:preview.mode, target:preview.target, inputs:preview.inputs, timeout_ms:preview.timeout_ms},null,2)}}</pre>
      <p v-if="preview.side_effect">{{t('flow-editor.postEffect')}}</p>
      <label v-if="preview.confirmation_required" class="ca-check"><input v-model="confirm" type="checkbox">{{t('flow-editor.confirmTarget')}}</label>
      <button type="button" class="ca-primary" :disabled="busy||preview.confirmation_required&&!confirm" @click="run">{{t('flow-editor.runNode')}}</button>
      <button type="button" @click="invalidate">{{t('flow-editor.cancel')}}</button>
    </template>
    <template v-if="outcome">
      <strong>{{t('flow-editor.'+outcome.mode)}} · {{t('flow-editor.'+outcome.status)}}</strong>
      <pre>{{JSON.stringify(outcome,null,2)}}</pre>
    </template>
  </div>
</template>
