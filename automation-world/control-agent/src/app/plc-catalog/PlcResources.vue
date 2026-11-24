<!-- 查看原始 PLC 点表、确认导入及单独填写目标绑定。 -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ConsoleCard, ConsoleActionButton } from '@aw-ui'
import {bindResource,commitCatalog,previewCatalog,type CatalogPreview,type Plc,type PlcTarget} from '../../services/caResources'
const props=defineProps<{plcs:Plc[]}>()
const emit=defineEmits<{changed:[]}>()
const {t}=useI18n()
function blockState(db:{source_enabled:boolean|null}|null){
  return t('flow-editor.'+(!db?'catalogDbAbsent':db.source_enabled===null?'catalogDbUnspecified':db.source_enabled?'enabled':'disabled'))
}
const preview=ref<CatalogPreview>()
const selected=ref('')
const alias=ref('')
const pointAlias=ref('')
const pointId=ref('')
const error=ref('')
const busy=ref(false)
const binding=ref<PlcTarget>()
const item=computed(()=>props.plcs.find(p=>p.id===selected.value))
const show=computed(()=>preview.value?.catalog??item.value?.catalog)
const supported=computed(()=>{
  const c=show.value?.plc.connection
  return !!c&&(c.local_tsap===undefined||c.local_tsap===256)&&(c.remote_tsap===undefined||c.remote_tsap===256+c.rack*32+c.slot)
})
async function choose(){
  error.value='';busy.value=true
  try{preview.value=await previewCatalog();alias.value=''}
  catch(e){if(String(e)!=='user_cancelled')error.value=String(e)}finally{busy.value=false}
}
async function commit(){
  if(!preview.value)return
  error.value='';busy.value=true
  try{
    const result=await commitCatalog(preview.value.token,alias.value)
    selected.value=result.id;preview.value=undefined;binding.value=undefined
    emit('changed')
  }catch(e){error.value=String(e)}finally{busy.value=false}
}
function open(plc:Plc){preview.value=undefined;selected.value=plc.id;binding.value=undefined;pointId.value='';pointAlias.value=''}
function editBinding(){
  const base=item.value?.binding??item.value?.catalog.plc.connection
  if(base)binding.value={host:base.host,port:base.port,rack:base.rack,slot:base.slot}
}
async function saveAlias(){
  error.value='';busy.value=true
  try{
    await bindResource({kind:'point',id:selected.value,point_id:pointId.value,alias:pointAlias.value})
    pointId.value='';pointAlias.value='';emit('changed')
  }catch(e){error.value=String(e)}finally{busy.value=false}
}
async function save(){
  if(!binding.value||!selected.value)return
  error.value='';busy.value=true
  try{await bindResource({kind:'plc',id:selected.value,target:binding.value});binding.value=undefined;emit('changed')}
  catch(e){error.value=String(e)}finally{busy.value=false}
}
</script>
<template>
  <ConsoleCard :title="t('flow-editor.plcs')" compact>
    <template #actions><ConsoleActionButton size="small" tone="primary" :disabled="busy" :label="t('flow-editor.importCatalog')" @click="choose" /></template>
    <div class="ca-fields">
    <p v-if="error" class="ca-error" role="alert">{{error}}</p>
    <div v-if="plcs.length" class="ca-actions">
      <button v-for="plc in plcs" :key="plc.id" :aria-pressed="!preview&&selected===plc.id" @click="open(plc)">{{plc.id}} · {{plc.catalog.plc.name}}</button>
    </div>
    <p v-else>{{t('flow-editor.noPlcs')}}</p>
    <template v-if="show">
      <div class="ca-bar">
        <h3>{{ show.plc.name }} · {{ show.export.producer }}</h3>
        <span>{{show.dbs.reduce((n,db)=>n+db.points.length,0)}} {{t('flow-editor.points')}}</span>
      </div>
      <p v-if="!supported" class="ca-error">{{t('flow-editor.tsapUnsupported')}}</p>
      <details><summary>{{t('flow-editor.sourceMetadata')}}</summary><pre>{{JSON.stringify({origin:show.origin,export:show.export,connection:show.plc.connection,file_sha256:preview?.file_sha256??item?.file_sha256},null,2)}}</pre></details>
      <template v-if="preview">
        <p>{{t('flow-editor.catalog_'+preview.status)}}</p>
        <template v-if="preview.status==='changed' && preview.diff">
          <div v-if="preview.diff.db_changes.length" class="ca-table-wrap">
            <table>
              <thead><tr><th>DB</th><th>{{t('flow-editor.catalogBefore')}}</th><th>{{t('flow-editor.catalogAfter')}}</th></tr></thead>
              <tbody>
                <tr v-for="change in preview.diff.db_changes" :key="change.id">
                  <td>DB{{(change.after ?? change.before)?.number}} · {{(change.after ?? change.before)?.name}}</td>
                  <td>{{blockState(change.before)}}</td><td>{{blockState(change.after)}}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <pre>{{JSON.stringify(preview.diff,null,2)}}</pre>
        </template>
        <label v-if="preview.status!=='identical'">{{t('flow-editor.logicalId')}}<input v-model.trim="alias" placeholder="plc_line_a"></label>
        <div class="ca-actions">
          <button class="ca-primary" :disabled="busy||(!alias&&preview.status!=='identical')" @click="commit">{{t(preview.status==='identical'?'flow-editor.open':'flow-editor.importCatalog')}}</button>
          <button @click="preview=undefined">{{t('flow-editor.cancel')}}</button>
        </div>
      </template>
      <template v-else-if="item">
        <div class="ca-bar"><p>{{item.binding?`${item.binding.host}:${item.binding.port} · ${item.binding.rack}/${item.binding.slot}`:t('flow-editor.unbound')}}</p>
          <button :disabled="!supported" @click="editBinding">{{t('flow-editor.bindPlc')}}</button></div>
        <form v-if="binding" class="ca-fields" @submit.prevent="save">
          <label>{{t('flow-editor.host')}}<input v-model="binding.host" required></label>
          <label>{{t('flow-editor.portNumber')}}<input v-model.number="binding.port" type="number" min="1" max="65535" required></label>
          <label>{{t('flow-editor.rack')}}<input v-model.number="binding.rack" type="number" min="0" max="7" required></label>
          <label>{{t('flow-editor.slot')}}<input v-model.number="binding.slot" type="number" min="0" max="31" required></label>
          <div class="ca-actions"><button class="ca-primary" :disabled="busy">{{t('flow-editor.confirmBinding')}}</button><button type="button" @click="binding=undefined">{{t('flow-editor.cancel')}}</button></div>
        </form>
      </template>
      <form v-if="item&&!preview" class="ca-fields" @submit.prevent="saveAlias">
        <div class="ca-actions">
          <label>{{t('flow-editor.point')}}
            <select v-model="pointId" required>
              <option value="">{{t('flow-editor.select')}}</option>
              <option v-for="p in item.catalog.dbs.flatMap(db=>db.points)" :key="p.id" :value="p.id">{{p.name}}</option>
            </select>
          </label>
          <label>{{t('flow-editor.pointAlias')}}<input v-model.trim="pointAlias" placeholder="task_status" required></label>
          <button :disabled="busy">{{t('flow-editor.confirmBinding')}}</button>
        </div>
      </form>
      <details v-for="db in show.dbs" :key="db.id" open>
        <summary>DB{{db.number}} · {{db.name}} · {{db.size_bytes}} B · {{db.points.length}} {{t('flow-editor.points')}} · {{db.source_enabled===undefined?'—':t(db.source_enabled?'flow-editor.enabled':'flow-editor.disabled')}}</summary>
        <div class="ca-table-wrap">
          <table><thead><tr><th>{{t('flow-editor.point')}}</th><th>{{t('flow-editor.address')}}</th><th>{{t('flow-editor.dataType')}}</th><th>{{t('flow-editor.sourceState')}}</th><th>{{t('flow-editor.sourceMetadata')}}</th></tr></thead>
          <tbody><tr v-for="p in db.points" :key="p.id"><td>{{p.name}}<br><small>{{item&&!preview?Object.entries(item.point_aliases).filter(([,id])=>id===p.id).map(([alias])=>alias).join(", "):""}}</small></td><td>{{p.byte_offset}}{{p.bit===undefined?'':'.'+p.bit}}</td><td>{{p.data_type}}</td><td>{{t(p.source_enabled?'flow-editor.enabled':'flow-editor.disabled')}}</td><td><details><summary>{{t('flow-editor.details')}}</summary><pre>{{JSON.stringify({db_id:db.id,...p},null,2)}}</pre></details></td></tr></tbody></table>
        </div>
      </details>
    </template>
    </div>
  </ConsoleCard>
</template>
