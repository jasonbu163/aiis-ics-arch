<!-- HTTP 资源绑定，已有敏感头仅列名称。 -->
<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ConsoleCard } from '@aw-ui'
import {bindResource,type Resources} from '../../services/caResources'
defineProps<{connections:Resources['http']}>()
const emit=defineEmits<{changed:[]}>()
const {t}=useI18n()
const id=ref('')
const url=ref('')
const headers=ref<{name:string; value:string}[]>([])
const error=ref('')
const busy=ref(false)
async function save(){
  error.value='';busy.value=true
  try{
    await bindResource({kind:'http',id:id.value,target:{base_url:url.value,headers:Object.fromEntries(headers.value.map(h=>[h.name,h.value]))}})
    id.value='';url.value='';headers.value=[];emit('changed')
  }catch(e){error.value=String(e)}finally{busy.value=false}
}
</script>
<template>
  <ConsoleCard :title="t('flow-editor.httpResources')" compact>
    <div class="ca-fields">
    <div v-if="connections.length" class="ca-table-wrap">
      <table><thead><tr><th>{{t('flow-editor.logicalId')}}</th><th>URL</th><th>{{t('flow-editor.headerNames')}}</th></tr></thead>
        <tbody><tr v-for="resource in connections" :key="resource.id"><td>{{resource.id}}</td><td>{{resource.base_url}}</td><td>{{resource.header_names.join(', ')||'—'}}</td></tr></tbody></table>
    </div>
    <form class="ca-fields" @submit.prevent="save">
      <h3>{{t('flow-editor.bindHttp')}}</h3>
      <label>{{t('flow-editor.logicalId')}}<input v-model.trim="id" placeholder="backend_api" required></label>
      <label>{{t('flow-editor.baseUrl')}}<input v-model.trim="url" type="url" placeholder="https://example.invalid" required></label>
      <div v-for="(row,index) in headers" :key="index" class="ca-actions">
        <label>{{t('flow-editor.headerNames')}}<input v-model.trim="row.name" required></label>
        <label>{{t('flow-editor.value')}}<input v-model="row.value" type="password" autocomplete="off" required></label>
        <button type="button" @click="headers.splice(index,1)">{{t('flow-editor.removeField')}}</button>
      </div>
      <div class="ca-actions">
        <button type="button" @click="headers.push({name:'',value:''})">{{t('flow-editor.addHeader')}}</button>
        <button class="ca-primary" :disabled="busy">{{t('flow-editor.confirmBinding')}}</button>
      </div>
      <p v-if="error" class="ca-error" role="alert">{{error}}</p>
    </form>
    </div>
  </ConsoleCard>
</template>
