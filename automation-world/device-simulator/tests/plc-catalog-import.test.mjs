/** DS-005 合成组件测试：原生文件选择、显式监听、草稿确认及取消。 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';
import ts from 'typescript';
import * as Vue from 'vue';
import {parse, compileScript} from 'vue/compiler-sfc';
const source=fs.readFileSync(new URL('../src/app/simulator/components/CatalogImportDialog.vue',import.meta.url),'utf8');
const script=compileScript(parse(source,{filename:'CatalogImportDialog.vue'}).descriptor,{id:'ds005'}).content;
const code=ts.transpileModule(script,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022,esModuleInterop:true}}).outputText;
class Failure extends Error { constructor(code,unknown=false) { super(code);this.code=code;this.unknown=unknown; } }
function host(overrides={}) {
 const calls=[],key=Symbol('ds');
 const selected={fileToken:'file',fileName:'source.json',byteCount:123,fileSha256:'sha',document:{origin:{kind:'data_acquisition_agent',profile_id:'profile',plc_id:'external'},export:{producer:'data_acquisition_agent',config_state:'saved_draft',revision_id:'revision',payload_sha256:'payload',exported_at:'time'},plc:{name:'PLC',connection:{host:'192.0.2.1',port:102,rack:0,slot:1,local_tsap:546,remote_tsap:258}},dbs:[{id:'db',name:'DB',number:21,size_bytes:2,points:[{id:'point',name:'Count',data_type:'INT',byte_offset:0,source_enabled:true}]}]}};
 const ipc={IpcFailure:Failure,chooseCatalogImport:async()=>{calls.push(['choose']);return selected;},previewCatalogImport:async p=>{calls.push(['preview',p]);return {token:'preview',expectedEtag:p.expectedEtag,candidateSha256:'candidate',workspace:{instances:[]}};},cancelCatalogImport:async id=>{calls.push(['cancel',id]);return {};},...overrides};
 const local=Vue.reactive({busy:false,dirty:false,configuration:{etag:'etag'},uncertainSave:null,error:null,commitCatalogImport:async (id,p)=>{calls.push(['commit',id,p]);return true;}});
 const modules={vue:Vue,'vue-i18n':{useI18n:()=>({t:key=>key,te:()=>false})},'../../../services/deviceSimulator':ipc,'../../../console/composables/useDeviceSimulator':{simulatorKey:key},'../../../components/console/ConsoleActionButton.vue':{__esModule:true,default:{}},'../../../components/console/ConsoleDataTable.vue':{__esModule:true,default:{}}};
 const mod={exports:{}};new Function('require','module','exports',code)(name=>{if(!(name in modules)) throw Error(name);return modules[name];},mod,mod.exports);mod.exports.default.render=()=>Vue.createCommentVNode('test');
 const make=type=>({type,children:[],parent:null,text:''});
 const renderer=Vue.createRenderer({createElement:make,createText:text=>({...make('#text'),text}),createComment:text=>({...make('#comment'),text}),setText:(n,v)=>{n.text=v;},setElementText:(n,v)=>{n.text=v;},parentNode:n=>n.parent,nextSibling:()=>null,insert:(n,p)=>{n.parent=p;p.children.push(n);},remove:n=>{if(n.parent)n.parent.children.splice(n.parent.children.indexOf(n),1);},patchProp(){}});
 const visible=Vue.ref(true), app=renderer.createApp({setup(){return()=>Vue.h(mod.exports.default,{modelValue:visible.value,'onUpdate:modelValue':v=>{visible.value=v;}});}});app.provide(key,local);const mounted=app.mount(make('root'));return {state:mounted.$.subTree.component.setupState,calls,local,visible,unmount:()=>app.unmount()};
}
test('selection never copies source target; preview requires explicit listener and passes file ticket and etag',async()=>{
 const h=host();await h.state.choose();assert.equal(h.state.host,'');assert.equal(h.state.port,undefined);assert.equal(h.state.sourceCalling,546);assert.equal(h.state.sourceCalled,258);
 await h.state.prepare();assert.equal(h.calls.filter(c=>c[0]==='preview').length,0);
 h.state.host='127.0.0.1';h.state.port=32194;h.state.rack=0;h.state.slot=2;h.state.confirmed=true;await h.state.prepare();
 assert.deepEqual(h.calls.find(c=>c[0]==='preview')[1],{fileToken:'file',expectedEtag:'etag',host:'127.0.0.1',port:32194,rack:0,slot:2,connectionConfirmed:true});
 await h.state.commit();assert.equal(h.calls.filter(c=>c[0]==='commit').length,1);assert.equal(h.visible.value,false);h.unmount();
});
test('cancel releases file and dirty draft prevents preview',async()=>{
 const h=host();await h.state.choose();h.state.host='127.0.0.1';h.state.port=32194;h.state.rack=0;h.state.slot=2;h.state.confirmed=true;h.local.dirty=true;await h.state.prepare();assert.equal(h.calls.filter(c=>c[0]==='preview').length,0);h.state.close();await Promise.resolve();assert.deepEqual(h.calls.at(-1),['cancel','file']);h.unmount();
});
test('changed file is surfaced and cannot submit a preview',async()=>{
 const h=host({previewCatalogImport:async()=>{throw new Failure('catalog_file_changed');}});await h.state.choose();h.state.host='127.0.0.1';h.state.port=32194;h.state.rack=0;h.state.slot=2;h.state.confirmed=true;await h.state.prepare();assert.equal(h.state.error,'catalog_file_changed');await h.state.commit();assert.equal(h.calls.filter(c=>c[0]==='commit').length,0);h.unmount();
});
test('locale keys match and full point preview uses shared table sizing',()=>{
 const en=JSON.parse(fs.readFileSync(new URL('../src/app/simulator/locales/en-US.json',import.meta.url))),zh=JSON.parse(fs.readFileSync(new URL('../src/app/simulator/locales/zh-CN.json',import.meta.url)));
 const keys=v=>Object.entries(v).flatMap(([k,x])=>x && typeof x==='object' && !Array.isArray(x)?keys(x).map(y=>k+'.'+y):[k]).sort();assert.deepEqual(keys(en),keys(zh));assert.match(source,/table-id="catalog\.import\.points"/);for(const key of ['display_name','display_names','description','source_path','source_enabled'])assert.match(source,new RegExp(key));
});
