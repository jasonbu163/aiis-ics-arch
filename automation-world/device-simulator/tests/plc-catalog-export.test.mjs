/** 对话框行为：保存来源、逐实例命名、目录取消和逐文件回执。 */
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
    const second={...instance,instanceId:'second',name:'车间.JSON',port:32195};
    const revision={revisionId:'revision',savedSeq:'1',createdUtc:'2026-11-16T00:00:00Z',sha256:'hash'};
    let files=[];
    const ipc={IpcFailure:Failure,catalogRevision:async id=>{calls.push(['revision',id]);return {revision,instances:[instance,second]};},
        catalogPreview:async (id,targets,filenames)=>{
            calls.push(['preview',id,targets,filenames]);
            files=targets.map(({instanceId})=>({instanceId,name:[instance,second].find(i=>i.instanceId===instanceId).name,filename:filenames[instanceId]}));
            return {token:'ticket',revision,rows:files};
        },
        catalogChooseDirectory:async token=>{calls.push(['directory',token]);return {rows:files.map(file=>({...file,conflict:false,valid:true}))};},
        catalogCommit:async token=>{calls.push(['commit',token]);return {rows:files.map(file=>({...file,result:'written',errorCode:null,fileSha256:'filehash'}))};},
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
    assert.deepEqual({...h.state.filenames},{instance:'Saved.json',second:'车间.JSON'});
    h.state.selected=['instance']; h.state.targets.instance.connectionConfirmed=true; h.state.targets.instance.loadedDifferenceConfirmed=true;
    h.state.rename('instance','实测名称.JSON');
    await h.state.prepare(); assert.equal(h.state.preview.token,'ticket');
    assert.equal(h.calls[1][1],'revision'); assert.equal(h.calls[1][2][0].connectionConfirmed,true); assert.equal(h.calls[1][2][0].loadedDifferenceConfirmed,true);
    assert.deepEqual(h.calls[1][3],{instance:'实测名称.JSON'});
    await h.state.choose(); assert.equal(h.state.directory.rows[0].filename,'实测名称.JSON');
    await h.state.commit(); assert.equal(h.state.results.rows[0].fileSha256,'filehash');
    assert.equal(h.state.summary.key,'success');
    assert.deepEqual(h.state.summary.counts,{written:1,failed:0,unknown:0});
    assert.equal(h.calls.filter(c=>c[0]==='commit').length,1); h.unmount();
});
test('native directory cancellation cannot submit and releasing a preview cancels its ticket',async()=>{
    const h=host({catalogChooseDirectory:async()=> 'cancelled'}); h.state.revisionId='revision'; await tick(); h.state.selected=['instance'];
    await h.state.prepare(); await h.state.choose(); await h.state.commit();
    assert.equal(h.state.preview,null);
    assert.equal(h.state.directory,null); assert.equal(h.calls.filter(c=>c[0]==='commit').length,0);
    await h.state.release(); assert.deepEqual(h.calls.at(-1),['cancel','ticket']); h.unmount();
});
test('unknown commit blocks another preview until the operator acknowledges checking',async()=>{
    let attempts=0;
    const h=host({catalogCommit:async()=>{attempts++; throw new Failure('ipc_transport_unknown',true);}}); h.state.revisionId='revision'; await tick(); h.state.selected=['instance','second'];
    await h.state.prepare(); await h.state.choose(); await h.state.commit(); await h.state.commit();
    assert.equal(attempts,1);
    assert.equal(h.state.summary.key,'unknown');
    assert.deepEqual(h.state.summary.counts,{written:0,failed:0,unknown:2});
    assert.deepEqual(h.state.results.rows.map(row=>[row.name,row.filename,row.result,row.fileSha256]),[
        ['Saved','Saved.json','unknown',null],['车间.JSON','车间.JSON','unknown',null],
    ]);
    h.state.change(); assert.equal(h.state.summary.key,'unknown');
    await h.state.prepare(); assert.equal(h.calls.filter(c=>c[0]==='preview').length,1);
    h.state.unknownChecked=true; h.state.change(); await h.state.prepare(); assert.equal(h.calls.filter(c=>c[0]==='preview').length,2); h.unmount();
});
test('each selected instance has its own filename, inline validation and a fresh ticket after changes',async()=>{
    const h=host(); h.state.revisionId='revision'; await tick();
    h.state.selected=['second','instance'];
    h.state.rename('instance','../collision.json');
    assert.equal(h.state.filenameErrors.instance,'catalog_filename_characters');
    h.state.rename('instance','车间.json');
    assert.deepEqual({...h.state.filenameErrors},{instance:'catalog_filename_duplicate',second:'catalog_filename_duplicate'});
    await h.state.prepare();
    assert.equal(h.calls.filter(c=>c[0]==='preview').length,0);
    h.state.rename('instance','正品.JSON');
    h.state.rename('second','rejects.json');
    await h.state.prepare(); await h.state.choose();
    assert.deepEqual(h.state.directory.rows.map(row=>[row.instanceId,row.filename]),[['second','rejects.json'],['instance','正品.JSON']]);
    h.state.change();
    assert.equal(h.state.directory,null);
    assert.deepEqual(h.calls.at(-1),['cancel','ticket']);
    h.state.rename('second','退料.json');
    await h.state.prepare(); await h.state.choose();
    assert.equal(h.state.directory.rows[0].filename,'退料.json');
    h.state.selected=['instance'];
    assert.equal(h.state.preview,null);
    assert.equal(h.state.directory,null);
    assert.deepEqual(h.calls.at(-1),['cancel','ticket']);
    h.unmount();
});
test('partial, entirely failed and incomplete receipts keep separate file statuses',async()=>{
    const first={instanceId:'instance',name:'Saved',filename:'Saved.json',result:'written',errorCode:null,fileSha256:'sha',cleanupPending:'.left.tmp'};
    const second={instanceId:'second',name:'车间.JSON',filename:'车间.JSON',result:'failed',errorCode:'catalog_target_changed',fileSha256:null,cleanupPending:null};
    for (const [response, key, counts] of [
        [[second,first],'partial',{written:1,failed:1,unknown:0}],
        [[first],'unknown',{written:1,failed:0,unknown:1}],
        [[{...first,result:'failed',errorCode:'catalog_write',fileSha256:null},second],'failed',{written:0,failed:2,unknown:0}],
    ]) {
        const h=host({catalogCommit:async()=>({rows:response})});
        h.state.revisionId='revision'; await tick(); h.state.selected=['instance','second'];
        await h.state.prepare(); await h.state.choose(); await h.state.commit();
        assert.equal(h.state.summary.key,key);
        assert.deepEqual(h.state.summary.counts,counts);
        assert.deepEqual(h.state.results.rows.map(row=>row.instanceId),['instance','second']);
        assert.equal(h.state.results.rows[0].fileSha256,counts.written?'sha':null);
        assert.equal(h.state.results.rows[1].errorCode,counts.unknown?'catalog_write_result_unknown':'catalog_target_changed');
        h.unmount();
    }
});
test('wrong filenames, duplicate instance receipts and invalid statuses leave only that file unknown',async()=>{
    const first={instanceId:'instance',name:'Saved',filename:'Saved.json',result:'written',errorCode:null,fileSha256:'sha',cleanupPending:null};
    const second={instanceId:'second',name:'车间.JSON',filename:'车间.JSON',result:'failed',errorCode:'catalog_target_changed',fileSha256:null,cleanupPending:null};
    for (const suspicious of [
        [{...first,filename:'other.json'}],
        [first,{...first,result:'failed',fileSha256:null}],
        [{...first,result:'invalid'}],
    ]) {
        let attempts=0;
        const h=host({catalogCommit:async()=>{attempts++;return {rows:[...suspicious,second]};}});
        h.state.revisionId='revision'; await tick(); h.state.selected=['instance','second'];
        await h.state.prepare(); await h.state.choose(); await h.state.commit(); await h.state.commit();
        assert.deepEqual(h.state.summary.counts,{written:0,failed:1,unknown:1});
        assert.equal(h.state.summary.key,'unknown');
        assert.deepEqual({...h.state.results.rows[0]},{
            ...first,result:'unknown',errorCode:'catalog_write_result_unknown',fileSha256:null,
        });
        assert.deepEqual({...h.state.results.rows[1]},second);
        assert.equal(attempts,1);
        h.unmount();
    }
});
test('a successful multi-file receipt keeps every output and its digest',async()=>{
    const h=host(); h.state.revisionId='revision'; await tick();
    h.state.selected=['instance','second'];
    h.state.rename('instance','good.json');
    h.state.rename('second','备用.json');
    await h.state.prepare(); await h.state.choose(); await h.state.commit();
    assert.equal(h.state.summary.key,'success');
    assert.deepEqual(h.state.summary.counts,{written:2,failed:0,unknown:0});
    assert.deepEqual(h.state.results.rows.map(row=>[row.filename,row.result,row.fileSha256]),[
        ['good.json','written','filehash'],['备用.json','written','filehash'],
    ]);
    h.unmount();
});
test('locale keys remain symmetric and preview uses the shared table sizing component',()=>{
    const en=JSON.parse(fs.readFileSync(new URL('../src/app/simulator/locales/en-US.json',import.meta.url)));
    const zh=JSON.parse(fs.readFileSync(new URL('../src/app/simulator/locales/zh-CN.json',import.meta.url)));
    const keys=v=>Object.entries(v).flatMap(([key,item])=>item && typeof item==='object' && !Array.isArray(item)?keys(item).map(sub=>key+'.'+sub):[key]).sort();
    assert.deepEqual(keys(en),keys(zh)); assert.match(source,/table-id="catalog\.export\.points"/);
    assert.match(source,/selectedRevision/); assert.match(source,/loadedRevision/); assert.match(source,/nonDefaultTsap/);
});
