/** 曲线facade来源/日期原样传递，无HTTP mock/fallback。 */
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { requireBusinessSource } from '../../../utils/businessDataSource.mjs'
const source=await readFile(new URL('./index.js',import.meta.url),'utf8')
const body=source.replace(/^import .*$/gm,'').replace(/export async function/g,'async function')
const calls=[]
const request={get:async(path,options)=>{calls.push({path,options});return {trends:[],latest:{}}}}
const api=Function('request','callApi','mockApi','requireBusinessSource',body+';return {getTemperatureData}') (request,async(_m,r)=>r(),{},requireBusinessSource)
test('HTTP curve request keeps equipment/date and never falls back',async()=>{
  await api.getTemperatureData({dataSource:'http',equipmentId:'A',date:'2026-10-16'})
  assert.equal(calls[0].path,'/monitor/process-curve-samples')
  assert.equal(calls[0].options.params.date,'2026-10-16')
  assert.equal(calls[0].options.params.equipmentId,'A')
  await assert.rejects(api.getTemperatureData({dataSource:'invalid'}))
  assert.equal(calls.length,1)
})
