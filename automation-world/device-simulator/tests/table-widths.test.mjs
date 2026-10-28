/** DIRECT列宽偏好自检：模拟本机Storage，不写浏览器真实偏好、业务库或运行值。 */
import assert from 'node:assert/strict';
import test from 'node:test';
import fs from 'node:fs';
import ts from 'typescript';
const code=ts.transpileModule(fs.readFileSync(new URL('../src/console/tableWidths.ts',import.meta.url),'utf8'),{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2022}}).outputText;
const {tableWidthKey,readTableWidths,validTableWidths,resizedTableWidths,saveTableWidths,resetTableWidths}=await import('data:text/javascript;base64,'+Buffer.from(code).toString('base64'));
function store(){const values=new Map();return {getItem:key=>values.get(key)??null,setItem:(key,value)=>values.set(key,value),removeItem:key=>values.delete(key)};}
const columns=[{key:'name',minWidth:140,resizable:true},{key:'value',minWidth:100,resizable:true},{key:'actions',minWidth:200,resizable:false}];
test('drag widths survive reopening and isolate table identities',()=>{
 const local=store(),get=()=>local;
 const widths=resizedTableWidths({},columns,'name',280);
 assert.ok(saveTableWidths(get,'configuration.points',widths));
 assert.deepEqual(readTableWidths(get,'configuration.points').widths,{name:280});
 assert.deepEqual(readTableWidths(get,'runtime.values').widths,{});
 assert.ok(tableWidthKey('configuration.points').startsWith('aiis.device-simulator.'));
 // 同一稳定字段不使用中文/英文标题、筛选条件、页码或PLC身份作为偏好键。
 assert.deepEqual(validTableWidths(readTableWidths(get,'configuration.points').widths,[{...columns[0],label:'名称'},columns[1]]),{name:280});
});
test('minimum width is enforced and stale columns/fixed columns/invalid values fall back',()=>{
 const resized=resizedTableWidths({},columns,'name',30);
 assert.deepEqual(resized,{name:140});
 assert.deepEqual(resizedTableWidths(resized,columns,'actions',500),{name:140});
 assert.deepEqual(validTableWidths({name:280,value:-1,actions:500,removed:300},columns),{name:280});
 assert.deepEqual(validTableWidths({name:280},[{key:'name',minWidth:320,resizable:true}]),{});
 for(const invalid of [NaN,Infinity,'280',null,100000]) assert.deepEqual(validTableWidths({name:invalid},columns),{});
});
test('reset removes only this table; unknown/corrupt format returns defaults',()=>{
 const local=store(),get=()=>local;
 saveTableWidths(get,'one',{name:280});saveTableWidths(get,'two',{name:320});
 assert.ok(resetTableWidths(get,'one'));
 assert.deepEqual(readTableWidths(get,'one').widths,{});
 assert.deepEqual(readTableWidths(get,'two').widths,{name:320});
 for(const raw of ['broken','null','{"version":2,"widths":{"name":280}}','{"version":1,"widths":[]}']){
  local.setItem(tableWidthKey('one'),raw);assert.deepEqual(readTableWidths(get,'one'),{widths:{},available:true});
 }
});
test('unavailable storage does not throw or prevent session width changes',()=>{
 const unavailable=()=>{throw new Error('storage blocked');};
 assert.deepEqual(readTableWidths(unavailable,'one'),{widths:{},available:false});
 assert.equal(saveTableWidths(unavailable,'one',{name:280}),false);
 assert.equal(resetTableWidths(unavailable,'one'),false);
 assert.deepEqual(resizedTableWidths({},columns,'name',280),{name:280});
});
