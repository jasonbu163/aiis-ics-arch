/** 导出对话框：已保存版本、预览、取消目录及逐实例结果的无 DOM 检查。 */
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url), vue = require('vue'), ts = require('typescript');
const sfc = require('vue/compiler-sfc');
const text = readFileSync(new URL('../src/app/plc/components/CatalogExportDialog.vue', import.meta.url), 'utf8');
const script = sfc.compileScript(sfc.parse(text).descriptor, { id:'catalog-export' }).content;
const compiled = ts.transpileModule(script, { compilerOptions:{ module:ts.ModuleKind.CommonJS, target:ts.ScriptTarget.ES2020 } }).outputText;
class LocalCommandError extends Error { constructor(code, unknown=false){super(code);this.commitUnknown=unknown;} }
async function fixture(t) {
  const calls=[], server={cancelFolder:false, unknown:false, invalid:false, partial:false, reject:'', targets:[]};
  const localCall=async(command,request)=>{
    calls.push({command,request:JSON.parse(JSON.stringify(request))});
    if(command==='daa_catalog_export_inspect') return {revision:'etag',payloadSha256:'abc',active:null,loaded:null,used:null,plcs:[{id:'A',name:'A',host:'127.0.0.1',port:102,rack:0,slot:1,dbCount:1,pointCount:2},{id:'B',name:'B',host:'127.0.0.2',port:102,rack:0,slot:1,dbCount:1,pointCount:1}]};
    if(command==='daa_catalog_export_preview') { server.targets=request.plcIds.map(plcId=>({plcId,name:plcId,filename:request.filenames[plcId]})); return server.invalid ? {filenameErrors:[{plcId:'A',code:'catalog_filename_characters'}]} : {token:'token',rows:server.targets.map(row=>({...row,document:null,issues:[]}))}; }
    if(command==='daa_catalog_export_directory') return server.cancelFolder ? {result:'cancelled'} : {rows:server.targets.map(row=>({...row,conflict:row.plcId==='B',valid:true}))};
    if(command==='daa_catalog_export_commit') { if(server.unknown) throw new LocalCommandError('transport_lost',true); if(server.reject) throw new LocalCommandError(server.reject); const rows=server.targets.map(row=>({...row,result:row.plcId==='B'?'failed':'written',errorCode:row.plcId==='B'?'catalog_target_exists':null,fileSha256:row.plcId==='B'?null:'sha',cleanupPending:null})); return {rows:server.partial?rows.slice(0,1):rows}; }
    if(command==='daa_catalog_export_cancel') return {result:'cancelled'};
    throw new Error(command);
  };
  const module={exports:{}};
  new Function('require','module','exports',compiled)(id=>{
    if(id==='vue')return vue; if(id==='vue-i18n')return {useI18n:()=>({t:key=>key})};
    if(id.endsWith('/services/localAcquisition'))return {localCall,LocalCommandError};
    return {default:{}};
  },module,module.exports);
  const node=type=>({type,children:[],parent:null});
  const renderer=vue.createRenderer({createElement:node,createText:node,createComment:node,setText(){},setElementText(){},patchProp(){},insert(c,p){c.parent=p;p.children.push(c);},remove(){},parentNode:c=>c.parent,nextSibling:()=>null});
  let state; const component=module.exports.default;
  const app=renderer.createApp({...component,setup(props,context){state=component.setup(props,context);return ()=>vue.h('div');}},{local:{label:v=>v}});
  app.mount(node('root'));t.after(()=>app.unmount());await new Promise(resolve=>setImmediate(resolve));
  return {state,calls,server};
}
test('directory cancellation invalidates preview; successful result remains per PLC',async t=>{
  const {state,calls,server}=await fixture(t);
  assert.equal(state.snapshot.value.revision,'etag');
  state.selected.value=['A','B'];await state.preview();server.cancelFolder=true;await state.chooseDirectory();
  assert.equal(state.prepared.value,null);assert.equal(calls.at(-1).command,'daa_catalog_export_cancel');
  server.cancelFolder=false;await state.preview();await state.chooseDirectory();state.targetsConfirmed.value=true;await state.commit();
  assert.equal(calls.find(c=>c.command==='daa_catalog_export_commit').request.confirmTargets,true);
  assert.deepEqual(state.results.value.rows.map(row=>row.result),['written','failed']);
  assert.equal(state.summaryKind.value,'partial');
});
test('unknown commit blocks repeat and page owns exactly one import dialog',async t=>{
  const {state,calls,server}=await fixture(t);state.selected.value=['A'];await state.preview();await state.chooseDirectory();state.targetsConfirmed.value=true;server.unknown=true;await state.commit();
  assert.equal(state.unknown.value,true);
  assert.equal(state.summaryKind.value,'unknown');
  assert.equal(state.results.value.rows[0].result,'unknown');
  await state.commit();
  const page=readFileSync(new URL('../src/app/plc/views/diagnostics/index.vue',import.meta.url),'utf8');
  const source=readFileSync(new URL('../src/app/plc/components/SourceImportPanel.vue',import.meta.url),'utf8');
  assert.equal((page.match(/<CatalogImportDialog/g)||[]).length,1);assert.doesNotMatch(source,/<CatalogImportDialog/);
  assert.match(page,/plc\.catalog\.open/);assert.match(page,/plc\.catalogExport\.open/);
  assert.equal(calls.filter(c=>c.command==='daa_catalog_export_commit').length,1);
});

test('filenames bind to PLC ids and edits invalidate the previous preview',async t=>{
  const {state,calls,server}=await fixture(t);
  assert.equal(state.filenames.value.A,'A.json');
  state.selected.value=['A','B'];state.filenames.value.A='温度.json';
  await state.preview();
  assert.deepEqual(calls.find(c=>c.command==='daa_catalog_export_preview').request.filenames,{A:'温度.json',B:'B.json'});
  state.filenames.value.A='new.json';state.clearPreview();
  assert.equal(state.prepared.value,null);assert.equal(calls.at(-1).command,'daa_catalog_export_cancel');
  server.invalid=true;await state.preview();assert.equal(state.prepared.value,null);
  assert.equal(state.filenameErrors.value[0].code,'catalog_filename_characters');
  assert.match(text,/#header/);assert.match(text,/@input="clearPreview"/);
});

test('missing receipts and worker loss stay unknown; explicit rejection is failed',async t=>{
  const {state,server}=await fixture(t);
  state.selected.value=['A','B'];await state.preview();await state.chooseDirectory();state.targetsConfirmed.value=true;
  server.partial=true;await state.commit();
  assert.deepEqual(state.results.value.rows.map(r=>r.result),['written','unknown']);assert.equal(state.summaryKind.value,'unknown');
  state.results.value=null;state.unknown.value=false;server.partial=false;await state.preview();await state.chooseDirectory();state.targetsConfirmed.value=true;
  server.reject='local_operation_failed';await state.commit();assert.equal(state.summaryKind.value,'unknown');
  state.results.value=null;state.unknown.value=false;server.reject='';await state.preview();await state.chooseDirectory();state.targetsConfirmed.value=true;
  server.reject='catalog_preview_stale';await state.commit();assert.equal(state.summaryKind.value,'failed');assert(state.results.value.rows.every(r=>r.errorCode==='catalog_preview_stale'));
});

test('native folder picker revokes old directory before opening',()=>{
  const bridge=readFileSync(new URL('../src-tauri/src/commands/catalog_export.rs',import.meta.url),'utf8');
  const revoke=bridge.indexOf('.catalog_export_release_directory(&request.token)');
  const picker=bridge.indexOf('.blocking_pick_folder()');
  assert(revoke>=0 && picker>revoke);
});
