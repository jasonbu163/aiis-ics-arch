/** DS-003 对话框行为：固定来源版本、原生目录取消、逐文件结果和未知回执。 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';
import ts from 'typescript';
import * as Vue from 'vue';
import {parse, compileScript} from 'vue/compiler-sfc';
const source=fs.readFileSync(new URL('../src/app/simulator/components/CatalogExportDialog.vue',import.meta.url),'utf8');
const script=compileScript(parse(source,{filename:'CatalogExportDialog.vue'}).descriptor,{id:'ds003'}).content;
const code=ts.transpileModule(script,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022,esModuleInterop:true}}).outputText;
const tick=async()=>{await Promise.resolve();await Vue.nextTick();await Promise.resolve();};
class Failure extends Error { constructor(code,unknown=false) { super(code);this.code=code;this.unknown=unknown; } }
function host(overrides={}) {
    const calls=[];
    const instance={instanceId:'instance',name:'Saved',host:'127.0.0.1',port:32194,rack:0,slot:1,localTsap:256,remoteTsap:257,selectedRevision:null,loadedRevision:null,dbCount:1,pointCount:1};
    const revision={revisionId:'revision',savedSeq:'1',createdUtc:'2026-11-16T00:00:00Z',sha256:'hash'};
    const ipc={IpcFailure:Failure,catalogRevision:async id=>{calls.push(['revision',id]);return {revision,instances:[instance]};},
        catalogPreview:async (id,targets)=>{calls.push(['preview',id,targets]);return {token:'ticket',revision,rows:[]};},
        catalogChooseDirectory:async token=>{calls.push(['directory',token]);return {rows:[{instanceId:'instance',filename:'instance.json',conflict:false,valid:true}]};},
        catalogCommit:async token=>{calls.push(['commit',token]);return {rows:[{instanceId:'instance',filename:'instance.json',result:'written',errorCode:null,fileSha256:'filehash'}]};},
        catalogCancel:async token=>{calls.push(['cancel',token]);return {};},...overrides};
    const modules={vue:Vue,'vue-i18n':{useI18n:()=>({t:(key)=>key,te:()=>false})},
        '../../../services/deviceSimulator':ipc,'../../../console/time':{formatShanghaiTime:()=>''},
        '../../../components/console/ConsoleActionButton.vue':{__esModule:true,default:{}},
        '../../../components/console/ConsoleDataTable.vue':{__esModule:true,default:{}}};
    const mod={exports:{}}; new Function('require','module','exports',code)(name=>{if(!(name in modules))throw Error(name);return modules[name];},mod,mod.exports);
    mod.exports.default.render=()=>Vue.createCommentVNode('test');
    const make=type=>({type,children:[],parent:null,text:''});
    const renderer=Vue.createRenderer({createElement:make,createText:text=>({...make('#text'),text}),createComment:text=>({...make('#comment'),text}),setText:(n,v)=>{n.text=v;},setElementText:(n,v)=>{n.text=v;},parentNode:n=>n.parent,nextSibling:()=>null,insert:(n,p)=>{n.parent=p;p.children.push(n);},remove:n=>{if(n.parent)n.parent.children.splice(n.parent.children.indexOf(n),1);},patchProp(){}});
    const visible=Vue.ref(true), root=make('root');
    const app=renderer.createApp({setup(){return()=>Vue.h(mod.exports.default,{modelValue:visible.value,revisions:[],offset:0,total:0,'onUpdate:modelValue':v=>{visible.value=v;}});}});
    const mounted=app.mount(root); const child=mounted.$.subTree.component; return {state:child.setupState,calls,visible,unmount:()=>app.unmount()};
}
test('saved revision and explicit connection confirmations reach the preview and native selection',async()=>{
    const h=host(); h.state.revisionId='revision'; await tick();
    assert.equal(h.state.source.instances[0].name,'Saved');
    h.state.selected=['instance']; h.state.targets.instance.connectionConfirmed=true; h.state.targets.instance.loadedDifferenceConfirmed=true;
    await h.state.prepare(); assert.equal(h.state.preview.token,'ticket');
    assert.equal(h.calls[1][1],'revision'); assert.equal(h.calls[1][2][0].connectionConfirmed,true); assert.equal(h.calls[1][2][0].loadedDifferenceConfirmed,true);
    await h.state.choose(); assert.equal(h.state.directory.rows[0].filename,'instance.json');
    await h.state.commit(); assert.equal(h.state.results.rows[0].fileSha256,'filehash');
    assert.equal(h.calls.filter(c=>c[0]==='commit').length,1); h.unmount();
});
test('native directory cancellation cannot submit and releasing a preview cancels its ticket',async()=>{
    const h=host({catalogChooseDirectory:async()=> 'cancelled'}); h.state.revisionId='revision'; await tick(); h.state.selected=['instance'];
    await h.state.prepare(); await h.state.choose(); await h.state.commit();
    assert.equal(h.state.directory,null); assert.equal(h.calls.filter(c=>c[0]==='commit').length,0);
    await h.state.release(); assert.deepEqual(h.calls.at(-1),['cancel','ticket']); h.unmount();
});
test('unknown commit blocks another preview until the operator acknowledges checking',async()=>{
    const h=host({catalogCommit:async()=>{throw new Failure('ipc_transport_unknown',true);}}); h.state.revisionId='revision'; await tick(); h.state.selected=['instance'];
    await h.state.prepare(); await h.state.choose(); await h.state.commit(); assert.equal(h.state.unknown,true);
    await h.state.prepare(); assert.equal(h.calls.filter(c=>c[0]==='preview').length,1);
    h.state.unknownChecked=true; await h.state.prepare(); assert.equal(h.calls.filter(c=>c[0]==='preview').length,2); h.unmount();
});
test('locale keys remain symmetric and preview uses the shared table sizing component',()=>{
    const en=JSON.parse(fs.readFileSync(new URL('../src/app/simulator/locales/en-US.json',import.meta.url)));
    const zh=JSON.parse(fs.readFileSync(new URL('../src/app/simulator/locales/zh-CN.json',import.meta.url)));
    const keys=v=>Object.entries(v).flatMap(([key,item])=>item && typeof item==='object' && !Array.isArray(item)?keys(item).map(sub=>key+'.'+sub):[key]).sort();
    assert.deepEqual(keys(en),keys(zh)); assert.match(source,/table-id="catalog\.export\.points"/);
    assert.match(source,/selectedRevision/); assert.match(source,/loadedRevision/); assert.match(source,/nonDefaultTsap/);
});
