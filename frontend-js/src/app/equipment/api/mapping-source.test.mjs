/** 实际facade经最小import注入测试来源分派；HTTP不走mock。 */
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { requireBusinessSource } from '../../../utils/businessDataSource.mjs'
const source=await readFile(new URL('./index.js',import.meta.url),'utf8')
const body=source.replace(/^import .*$/gm,'').replace(/export async function/g,'async function')
const calls=[]
const request={get:async(path,options)=>{calls.push({path,options});return {dashboard:{recordId:7},recordId:8}}}
const callApi=async(_mock,real)=>real()
const api=Function('request','callApi','mockApi','requireBusinessSource',body+';return {getDriveData,getTemperatureControlData,getProductionParametersData}')(request,callApi,{},requireBusinessSource)
test('HTTP equipment facades select exact adapters, unwrap dashboard only',async()=>{
  calls.length=0
  assert.equal((await api.getDriveData({dataSource:'http',equipmentId:'A'})).recordId,7)
  assert.equal((await api.getTemperatureControlData({dataSource:'http',equipmentId:'A'})).recordId,8)
  await api.getProductionParametersData({dataSource:'http',equipmentId:'A'})
  assert.deepEqual(calls.map(c=>c.path),['/equipment/drive-samples','/equipment/temperature-sample-dashboard','/equipment/production-parameter-samples'])
  assert.ok(calls.every(c=>c.options.params.equipmentId==='A'))
  await assert.rejects(api.getDriveData({dataSource:'http'}))
})

test('actual drive SFC clears source rows and rejects an old equipment response',async()=>{
  const {parseBusinessDataSource,businessDataSourceQuery,createRequestGeneration}=await import('../../../utils/businessDataSource.mjs')
  const file=await readFile(new URL('../views/drive/index.vue',import.meta.url),'utf8')
  const script=file.match(/<script setup>([\s\S]*?)<\/script>/)[1].replace(/^import .*$/gm,'')
  const route={query:{dataSource:'http',equipmentId:'A'}}
  const watchers=[];const pending=[]
  const ref=value=>({value})
  const computed=options=>({get value(){return typeof options==='function'?options():options.get()}})
  const getDriveData=params=>new Promise(resolve=>pending.push({params,resolve}))
  const page=Function('ref','computed','watch','onMounted','onBeforeUnmount','useRoute','useRouter','useI18n','getDriveData','ElMessage','parseBusinessDataSource','businessDataSourceQuery','createRequestGeneration',script+';return {loadData,processParams,tensionParams}')(ref,computed,(_getter,callback)=>watchers.push(callback),()=>{},()=>{},()=>route,()=>({replace:()=>{}}),()=>({t:key=>key}),getDriveData,{error:()=>{}},parseBusinessDataSource,businessDataSourceQuery,createRequestGeneration)
  assert.ok(page.processParams.value.every(row=>row.value==null&&row.actual==null))
  const old=page.loadData()
  route.query={dataSource:'http',equipmentId:'B'}
  watchers[0]()
  assert.deepEqual(pending.map(item=>item.params.equipmentId),['A','B'])
  pending[0].resolve({processItems:[{id:'tv',value:111}]})
  await old
  assert.equal(page.processParams.value[0].value,null)
  pending[1].resolve({processItems:[{id:'tv',value:0}]})
  await new Promise(resolve=>setImmediate(resolve))
  assert.equal(page.processParams.value[0].value,0)
  route.query={dataSource:'http',equipmentId:''};watchers[0]()
  assert.equal(pending.length,2)
  assert.equal(page.processParams.value[0].value,null)
})
