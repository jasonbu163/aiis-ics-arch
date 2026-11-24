<!-- CA 工作台、已保存版本和流程编辑器。 -->
<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Connection, Document as DocumentIcon, Link, Monitor, RefreshRight, Tickets } from '@element-plus/icons-vue'
import { AgentLayout, AgentSidebar, AgentTopbar, ConsoleActionButton, ConsoleCard, LanguageSwitch,
  StatusCapsule, ThemeToggle, type NavigationItem } from '@aw-ui'
import '@aw-ui-styles'
import { useAgentLocale } from '../../console/composables/useAgentLocale'
import { useAgentTheme } from '../../console/composables/useAgentTheme'
import { exportFlow,getFlow,importFlow,listFlows,previewFlow,saveFlow,validateFlow,
  type Document,type Edge,type FlowNode,type FlowPreview,type Issue,type Position,type Saved } from '../../services/caFlow'
import {listResources,type Resources} from '../../services/caResources'
import {listTests,type TestResult} from '../../services/caNodeTest'
import {clone,createNode,edgeKey,fresh,layoutPosition,outputs,palette,paletteKey,type Palette} from './model'
import FlowCanvas from './FlowCanvas.vue'
import Params from './Params.vue'
import PlcResources from '../plc-catalog/PlcResources.vue'
import HttpResources from '../http-connections/HttpResources.vue'
import NodeTester from '../node-tests/NodeTester.vue'
import './workspace.css'

const props=defineProps<{offline:boolean}>()
const {t,te,locale}=useI18n()
const {toggleLocale,localeSwitchLabel,elementLocale}=useAgentLocale()
const {toggleTheme,themeSwitchLabel,isDarkTheme}=useAgentTheme()
const theme=computed(()=>isDarkTheme.value?'dark':'light')
const sidebarHidden=ref(false)
const pages=['workbench','flows','plcs','httpResources','records'] as const
type Page=typeof pages[number]|'editor'
const page=ref<Page>('workbench')
const pageIcons=[Monitor,DocumentIcon,Connection,Link,Tickets]
const navigation=computed<NavigationItem[]>(()=>pages.map((id,index)=>({id,label:t('flow-editor.'+id),icon:pageIcons[index]})))
const activePage=computed(()=>page.value==='editor'?'flows':page.value)
function navigateFromSidebar(id:string){
  if(pages.includes(id as typeof pages[number]))navigate(id as typeof pages[number])
}
const doc=ref<Document>(fresh())
const saved=ref<Saved[]>([])
const resources=ref<Resources>({plcs:[],http:[],fake:false})
const records=ref<TestResult[]>([])
const record=ref<TestResult>()
const selected=ref('')
const selectedEdge=ref('')
const panel=ref<'parameters'|'test'>('parameters')
const inspector=ref(true)
const flowCanvas=ref<InstanceType<typeof FlowCanvas>>()
const paletteDrag=ref<{kind:Palette;x:number;y:number}>()
let gesture:{kind:Palette;id:number;x:number;y:number}|undefined
let suppressPaletteClick=false
const viewJson=ref(false)
const jsonText=ref<HTMLTextAreaElement>()
const undoStack=ref<Document[]>([])
const baseline=ref('')
const current=ref<Saved>()
const issues=ref<Issue[]>([])
const checking=ref(false)
const exists=ref(false)
const busy=ref(false)
const error=ref('')
const message=ref('')
const importing=ref<FlowPreview>()
const copyId=ref('')
const duplicate=ref(false)
const selectedFlow=ref('')
const selectedVersion=ref(0)
let validation=0
let debounce:number|undefined
const node=computed(()=>doc.value.flow.nodes.find(n=>n.id===selected.value))
const upstream=computed(()=>outputs(doc.value,selected.value))
const dirty=computed(()=>baseline.value!==JSON.stringify(doc.value))
const versionChoices=computed(()=>saved.value.filter(s=>s.document.flow.flow_id===selectedFlow.value).sort((a,b)=>b.document.flow.revision-a.document.flow.revision))
const flowIds=computed(()=>Array.from(new Set(saved.value.map(s=>s.document.flow.flow_id))).sort())
const canSave=computed(()=>!props.offline&&!busy.value&&!checking.value&&!issues.value.length&&exists.value&&dirty.value)
const canExport=computed(()=>!props.offline&&!busy.value&&!checking.value&&!issues.value.length&&exists.value&&!dirty.value&&!!current.value)
const fileJson=computed(()=>JSON.stringify(doc.value,null,2))
const key=(s:string)=>'flow-editor.'+s
const local=(s:string)=>te(key(s))?t(key(s)):s
watch(selectedFlow,()=>{selectedVersion.value=versionChoices.value[0]?.document.flow.revision??0})
function edit(f:(draft:Document)=>void){
  const next=clone(doc.value)
  f(next)
  if(JSON.stringify(next)===JSON.stringify(doc.value))return
  undoStack.value=[...undoStack.value.slice(-79),clone(doc.value)]
  doc.value=next
}
function selectNode(id:string){selected.value=id;selectedEdge.value='';if(id){inspector.value=true;panel.value='parameters'}}
function selectEdge(id:string){selected.value='';selectedEdge.value=id;inspector.value=true;panel.value='parameters'}
function undo(){
  const previous=undoStack.value.pop()
  if(!previous)return
  doc.value=previous
  if(!doc.value.flow.nodes.some(n=>n.id===selected.value))selected.value=''
  if(!doc.value.flow.edges.some(e=>edgeKey(e)===selectedEdge.value))selectedEdge.value=''
}
function add(kind:Palette,position?:Position){
  let i=1;while(doc.value.flow.nodes.some(n=>n.id===kind+'_'+i))i++
  const id=kind+'_'+i
  edit(draft=>{
    const n=draft.flow.nodes.length
    draft.flow.nodes.push(createNode(kind,id))
    if(!draft.flow.entry_node_id)draft.flow.entry_node_id=id
    draft.layout??={nodes:{}}
    draft.layout.nodes[id]=position??{x:55+(n%4)*185,y:75+Math.floor(n/4)*100}
  })
  selectNode(id)
}
function move(id:string,p:Position){
  edit(draft=>{
    if(!draft.layout)draft.layout={nodes:Object.fromEntries(draft.flow.nodes.map((n,i)=>[n.id,layoutPosition(draft,n.id,i)]))}
    draft.layout.nodes[id]={x:p.x,y:p.y}
  })
}
function connect(edge:Edge){edit(d=>d.flow.edges.push(edge));error.value=''}
function remove(){
  if(!selected.value&&!selectedEdge.value)return
  const id=selected.value, link=selectedEdge.value
  edit(d=>{
    if(id){
      d.flow.nodes=d.flow.nodes.filter(n=>n.id!==id)
      d.flow.edges=d.flow.edges.filter(e=>e.from_node_id!==id&&e.to_node_id!==id)
      if(d.layout)delete d.layout.nodes[id]
      if(d.flow.entry_node_id===id)d.flow.entry_node_id=d.flow.nodes.find(n=>!d.flow.edges.some(e=>e.to_node_id===n.id))?.id??''
    }else d.flow.edges=d.flow.edges.filter(e=>edgeKey(e)!==link)
  })
  selectNode('')
}
function updateNode(updated:FlowNode){edit(d=>{const i=d.flow.nodes.findIndex(n=>n.id===updated.id);if(i>=0)d.flow.nodes[i]=updated})}
function shortcuts(event:KeyboardEvent){
  if(page.value!=='editor'||event.target instanceof HTMLInputElement||event.target instanceof HTMLSelectElement||event.target instanceof HTMLTextAreaElement)return
  if((event.key==='Delete'||event.key==='Backspace')&&(selected.value||selectedEdge.value)){event.preventDefault();remove()}
  if((event.metaKey||event.ctrlKey)&&event.key.toLowerCase()==='z'){event.preventDefault();undo()}
}
function beginDrag(event:PointerEvent,kind:Palette){
  if(event.button!==0||gesture)return
  gesture={kind,id:event.pointerId,x:event.clientX,y:event.clientY}
  suppressPaletteClick=false
  const button=event.currentTarget as HTMLElement
  button.setPointerCapture(event.pointerId)
}
function dragMove(event:PointerEvent){
  if(!gesture||gesture.id!==event.pointerId)return
  if(Math.hypot(event.clientX-gesture.x,event.clientY-gesture.y)>5||paletteDrag.value){
    paletteDrag.value={kind:gesture.kind,x:event.clientX,y:event.clientY}
  }
}
function endDrag(event:PointerEvent){
  if(!gesture||gesture.id!==event.pointerId)return
  if(paletteDrag.value){
    const position=event.type==='pointerup'?flowCanvas.value?.pointAt(event.clientX,event.clientY):undefined
    if(position)add(gesture.kind,position)
    suppressPaletteClick=true
  }
  gesture=undefined
  paletteDrag.value=undefined
}
function paletteClick(kind:Palette){
  if(!suppressPaletteClick)add(kind)
  suppressPaletteClick=false
}
async function validate(){
  const request=++validation
  if(props.offline)return
  checking.value=true
  try{
    const result=await validateFlow(doc.value)
    if(request!==validation)return
    issues.value=result;exists.value=true
  }catch(e){if(request===validation){error.value=String(e);exists.value=false}}
  finally{if(request===validation) checking.value=false}
}
function scheduleValidation(){
  validation++
  checking.value=true
  window.clearTimeout(debounce)
  debounce=window.setTimeout(()=>{void validate()},110)
}
watch(doc,scheduleValidation)
function setDoc(next:Document,stored?:Saved){
  doc.value=clone(next);current.value=stored
  baseline.value=stored?JSON.stringify(doc.value):''
  undoStack.value=[];viewJson.value=false;inspector.value=true;selectNode('')
  page.value='editor'
}
function newFlow(){const next=fresh();let i=1;while(flowIds.value.includes('flow_'+i))i++;next.flow.flow_id='flow_'+i;setDoc(next)}
async function attempt(operation:()=>Promise<void>){
  if(busy.value)return
  busy.value=true;error.value='';message.value=''
  try{await operation()}catch(e){if(String(e)!=='user_cancelled')error.value=String(e)}
  finally{busy.value=false}
}
async function refresh(){
  if(props.offline)return
  const [f,r,tests]=await Promise.all([listFlows(),listResources(),listTests()])
  saved.value=f;resources.value=r;records.value=tests
  if(page.value==='editor')scheduleValidation()
}
const refreshUI=()=>attempt(refresh)
async function open(id:string,revision:number){await attempt(async()=>{const s=await getFlow(id,revision);setDoc(s.document,s)})}
async function save(){
  if(!canSave.value)return
  await attempt(async()=>{
    const expected=current.value?.document.flow.flow_id===doc.value.flow.flow_id?
      Math.max(...saved.value.filter(s=>s.document.flow.flow_id===doc.value.flow.flow_id).map(s=>s.document.flow.revision),0):0
    const result=await saveFlow(doc.value,expected)
    current.value=result;doc.value=clone(result.document);baseline.value=JSON.stringify(doc.value);message.value='saved'
    await refresh()
  })
}
async function exportCurrent(){
  if(!current.value||!canExport.value)return
  const f=current.value.document.flow
  await attempt(async()=>{await exportFlow(f.flow_id,f.revision);message.value='exported'})
}
async function selectFile(){
  await attempt(async()=>{importing.value=await previewFlow();copyId.value='';duplicate.value=importing.value.status==='conflict'})
}
async function confirmImport(){
  const pending=importing.value
  if(!pending||pending.issues.length)return
  await attempt(async()=>{
    const result=await importFlow(pending.token,duplicate.value?copyId.value:null)
    importing.value=undefined;setDoc(result.document,result);await refresh()
  })
}
function navigate(next:Page){page.value=next;error.value='';message.value='';importing.value=undefined}
async function copyJson(){
  jsonText.value?.select()
  try{await navigator.clipboard.writeText(fileJson.value);message.value='copied'}
  catch{message.value='copySelected'}
}
onMounted(()=>{window.addEventListener('keydown',shortcuts);void refreshUI()})
onUnmounted(()=>{window.removeEventListener('keydown',shortcuts);window.clearTimeout(debounce)})
</script>
<template>
  <el-config-provider :locale="elementLocale">
    <AgentLayout class="aw-ui--dense" :theme="theme" :sidebar-hidden="sidebarHidden">
      <template #sidebar>
        <AgentSidebar :items="navigation" :active-id="activePage" :brand="t(key('appTitle'))" @select="navigateFromSidebar" />
      </template>
      <template #topbar>
        <AgentTopbar :title="t(key(activePage))" :subtitle="t(key('appTitle'))" :sidebar-hidden="sidebarHidden"
          :sidebar-label="t(key(sidebarHidden?'showSidebar':'hideSidebar'))" @toggle-sidebar="sidebarHidden=!sidebarHidden">
          <template #actions>
            <StatusCapsule v-if="resources.fake" :label="t(key('fake'))" tone="neutral" />
            <ConsoleActionButton :icon="RefreshRight" :label="t(key('refresh'))" round-icon @click="refreshUI" />
            <ThemeToggle :theme="theme" :label="themeSwitchLabel" @toggle="toggleTheme" />
            <LanguageSwitch :locale="locale==='zh-CN'?'zh-CN':'en-US'" :label="localeSwitchLabel"
              :en-label="t('common.actions.switchToEnglishShort')" :zh-label="t('common.actions.switchToChineseShort')" @toggle="toggleLocale" />
          </template>
        </AgentTopbar>
      </template>
      <div class="ca-content">
      <p v-if="offline" class="ca-note">{{t(key('offline'))}}</p>
      <p v-if="error" class="ca-error" role="alert">{{local(error)}}</p>
      <p v-if="message" class="ca-note" role="status">{{local(message)}}</p>
      <section v-if="importing" class="ca-card ca-fields" aria-labelledby="ca-import-title">
        <div class="ca-bar"><h2 id="ca-import-title">{{t(key('importPreview'))}}</h2><button @click="importing=undefined">{{t(key('cancel'))}}</button></div>
        <p>{{importing.document.flow.flow_id}} · r{{importing.document.flow.revision}} · {{t(key('import_'+importing.status))}}</p>
        <p class="ca-digest">SHA-256 · {{importing.file_sha256}}</p>
        <ul v-if="importing.issues.length" class="ca-error"><li v-for="(issue,index) in importing.issues" :key="index">{{issue.node_id||'—'}} · {{local(issue.code)}}</li></ul>
        <template v-else>
          <label v-if="importing.status==='identical'" class="ca-check"><input v-model="duplicate" type="checkbox">{{t(key('newCopy'))}}</label>
          <label v-if="duplicate">{{t(key('logicalId'))}}<input v-model.trim="copyId" placeholder="status_gate_copy"></label>
          <button class="ca-primary" :disabled="busy||duplicate&&!copyId" @click="confirmImport">{{t(key(duplicate?'newCopy':importing.status==='identical'?'open':'import'))}}</button>
        </template>
      </section>

      <ConsoleCard v-if="page==='workbench'" :title="t(key('workbench'))" compact>
        <div class="ca-fields">
        <p>{{t(key('runtimeUnavailable'))}}</p>
        <div class="ca-actions">
          <label>{{t(key('flowId'))}}<select v-model="selectedFlow"><option value="">{{t(key('select'))}}</option><option v-for="id in flowIds" :key="id">{{id}}</option></select></label>
          <label>{{t(key('revision'))}}<select v-model="selectedVersion"><option v-for="v in versionChoices" :key="v.document.flow.revision" :value="v.document.flow.revision">r{{v.document.flow.revision}}</option></select></label>
          <button class="ca-primary" :disabled="!selectedVersion" @click="open(selectedFlow,selectedVersion)">{{t(key('open'))}}</button>
        </div>
        <h2>{{t(key('recentTests'))}}</h2>
        <p v-if="!records.length">{{t(key('noRecords'))}}</p>
        <button v-for="r in records.slice(0,6)" :key="r.id" @click="record=r;navigate('records')">{{r.node_id}} · {{local(r.mode)}} · {{local(r.status)}}</button>
        </div>
      </ConsoleCard>

      <ConsoleCard v-if="page==='flows'" :title="t(key('flows'))" compact>
        <template #actions>
          <ConsoleActionButton size="small" :disabled="offline||busy" :label="t(key('import'))" @click="selectFile" />
          <ConsoleActionButton size="small" tone="primary" :label="t(key('newFlow'))" @click="newFlow" />
          <ConsoleActionButton v-if="doc.flow.nodes.length" size="small" :label="t(key('continueDraft'))" @click="navigate('editor')" />
        </template>
        <p v-if="!saved.length">{{t(key('noFlows'))}}</p>
        <div v-else class="ca-table-wrap"><table><thead><tr><th>{{t(key('flowId'))}}</th><th>{{t(key('revision'))}}</th><th>{{t(key('status'))}}</th><th></th></tr></thead>
          <tbody><tr v-for="s in [...saved].reverse()" :key="s.document.flow.flow_id+'-'+s.document.flow.revision">
            <td>{{s.document.flow.flow_id}}</td><td>r{{s.document.flow.revision}}</td><td>{{t(key('valid'))}}</td>
            <td><button @click="open(s.document.flow.flow_id,s.document.flow.revision)">{{t(key('open'))}}</button></td>
          </tr></tbody>
        </table></div>
      </ConsoleCard>

      <ConsoleCard v-if="page==='editor'" :title="doc.flow.flow_id||t(key('newFlow'))" compact class="ca-editor">
        <template #title-aside><small>{{t(key('editor'))}}</small></template>
        <template #actions>
          <ConsoleActionButton size="small" :label="t(key('back'))" @click="navigate('flows')" />
          <ConsoleActionButton size="small" :disabled="!undoStack.length" :label="t(key('undo'))" @click="undo" />
          <ConsoleActionButton size="small" :disabled="offline||busy" :label="t(key('validate'))" @click="validate" />
          <ConsoleActionButton size="small" :aria-pressed="viewJson" label="JSON" @click="viewJson=!viewJson" />
          <ConsoleActionButton size="small" :disabled="!canExport" :label="t(key('export'))" @click="exportCurrent" />
          <ConsoleActionButton size="small" tone="primary" :disabled="!canSave" :label="t(key('saveRevision'))" @click="save" />
        </template>
        <template v-if="viewJson">
          <div class="ca-json-view">
            <div class="ca-actions"><button @click="copyJson">{{t(key('copyJson'))}}</button></div>
            <textarea ref="jsonText" readonly :aria-label="t(key('jsonPreview'))" :value="fileJson" spellcheck="false"></textarea>
          </div>
        </template>
        <div v-else class="ca-editor-body" :class="{'ca-compact-editor':!inspector}">
          <aside class="ca-palette">
            <h2>{{t(key('nodeLibrary'))}}</h2>
            <button v-for="kind in palette" :key="kind" :data-palette="kind"
              @pointerdown="beginDrag($event,kind)" @pointermove="dragMove" @pointerup="endDrag" @pointercancel="endDrag" @click="paletteClick(kind)">
              {{t(key('node.'+kind))}}
            </button>
          </aside>
          <FlowCanvas ref="flowCanvas" :document="doc" :selected="selected" :edge="selectedEdge" :invalid="issues.flatMap(i=>i.node_id?[i.node_id]:[])"
            @move="move" @select="selectNode" @select-edge="selectEdge" @connect="connect" @invalid="error='invalidConnection'" />
          <aside v-if="inspector" class="ca-inspector">
            <div class="ca-bar"><h2>{{node?t(key('node.'+paletteKey(node))):selectedEdge?t(key('edge')):t(key('flowSettings'))}}</h2>
              <button :aria-label="t(key('hideInspector'))" @click="inspector=false">×</button></div>
            <template v-if="node">
              <p class="ca-node-id">{{node.id}} · v{{node.version}}</p>
              <div class="ca-actions">
                <button :aria-pressed="panel==='parameters'" @click="panel='parameters'">{{t(key('parameters'))}}</button>
                <button :aria-pressed="panel==='test'" @click="panel='test'">{{t(key('testNode'))}}</button>
                <button class="ca-danger" @click="remove">{{t(key('deleteNode'))}}</button>
              </div>
              <Params v-if="panel==='parameters'" :node="node" :options="upstream" :resources="resources" @change="updateNode" />
              <NodeTester v-else :key="node.id" :node="node" :document="doc" :options="upstream" :flow-id="doc.flow.flow_id" :revision="doc.flow.revision"
                :records="records" :fake="resources.fake" @done="refreshUI" />
            </template>
            <template v-else-if="selectedEdge">
              <p class="ca-node-id">{{selectedEdge}}</p><button class="ca-danger" @click="remove">{{t(key('deleteEdge'))}}</button>
            </template>
            <div v-else class="ca-fields">
              <label>{{t(key('flowId'))}}<input :value="doc.flow.flow_id" @change="event=>edit(d=>d.flow.flow_id=(event.target as HTMLInputElement).value.trim())"></label>
              <label>{{t(key('interval'))}}<input :value="doc.flow.trigger.interval_ms" type="number" min="1" @change="event=>edit(d=>d.flow.trigger.interval_ms=(event.target as HTMLInputElement).valueAsNumber)"></label>
              <label>{{t(key('entryNode'))}}
                <select :value="doc.flow.entry_node_id" @change="event=>edit(d=>d.flow.entry_node_id=(event.target as HTMLSelectElement).value)">
                  <option value="">{{t(key('select'))}}</option>
                  <option v-for="n in doc.flow.nodes" :key="n.id">{{n.id}}</option>
                </select>
              </label>
              <small>{{t(key('editorHelp'))}}</small>
            </div>
          </aside>
        </div>
        <template #footer><div class="ca-editor-footer">
          <details v-if="issues.length"><summary>{{t(key('issues'),{count:issues.length})}}</summary>
            <ul><li v-for="(i,index) in issues" :key="index">
              <button v-if="i.node_id" @click="viewJson=false;selectNode(i.node_id)">{{i.node_id}}</button>
              {{local(i.code)}}
            </li></ul>
          </details>
          <span v-else>{{t(key(checking?'validating':exists?'valid':'validationUnavailable'))}}</span>
          <span class="ca-digest" v-if="current&&!dirty">r{{doc.flow.revision}} · SHA-256 {{current.file_sha256.slice(0,12)}}</span>
          <span v-else>{{t(key('draft'))}}</span>
          <button v-if="!inspector&&!viewJson" @click="inspector=true">{{t(key('showInspector'))}}</button>
        </div></template>
      </ConsoleCard>

      <PlcResources v-if="page==='plcs'" :plcs="resources.plcs" @changed="refreshUI" />
      <HttpResources v-if="page==='httpResources'" :connections="resources.http" @changed="refreshUI" />
      <ConsoleCard v-if="page==='records'" :title="t(key('records'))" compact>
        <p v-if="!records.length">{{t(key('noRecords'))}}</p>
        <div v-else class="ca-table-wrap"><table><thead><tr><th>{{t(key('nodeId'))}}</th><th>{{t(key('mode'))}}</th><th>{{t(key('status'))}}</th><th>{{t(key('startedAt'))}}</th><th></th></tr></thead>
          <tbody><tr v-for="r in records" :key="r.id"><td>{{r.node_id}}</td><td>{{local(r.mode)}}</td><td>{{local(r.status)}}</td><td>{{r.started_at}}</td><td><button @click="record=r">{{t(key('details'))}}</button></td></tr></tbody>
        </table></div>
        <pre v-if="record">{{JSON.stringify(record,null,2)}}</pre>
      </ConsoleCard>
      </div>
    <div v-if="paletteDrag" class="ca-palette-ghost" :style="{left:paletteDrag.x+'px',top:paletteDrag.y+'px'}" aria-hidden="true">
      {{t(key('node.'+paletteDrag.kind))}}
    </div>
    </AgentLayout>
  </el-config-provider>
</template>
