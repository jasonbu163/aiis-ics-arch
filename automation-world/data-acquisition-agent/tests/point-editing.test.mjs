/** DIRECT点位交互回归：真实Vue响应式owner配受控IPC替身，不访问SQLite、PLC或桌面窗口。 */
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const ts = require('typescript'), vue = require('vue');
const clone = value => JSON.parse(JSON.stringify(value));
const source = readFileSync(new URL('../src/console/composables/useLocalAcquisitionConsole.ts', import.meta.url), 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText;
class LocalCommandError extends Error {
    constructor(code, currentEtag = null) { super(code); this.currentEtag = currentEtag; }
}
function initial() {
    const points = Array.from({length:6},(_,i)=>({id:'p'+i,plcId:'A',dbId:i<2?'DB71':'DB88',name:'Point_'+i,sourcePath:'field'+i,dataType:i===0||i===2?'BOOL':'INT',comment:'',groupId:'fast',enabled:true,address:{offset:i*2,bit:i===0||i===2?0:null,confirmed:true,origin:'inferred',reason:'fixture'}}));
    points.push({...clone(points[0]),id:'other',plcId:'B',dbId:'B-DB71'});
    return {etag:'e1',issues:[],active:null,loaded:null,used:null,previous:null,phase:'loaded',draft:{schemaVersion:1,plcs:[{id:'A',name:'A'},{id:'B',name:'B'}],dbs:[{id:'DB71',plcId:'A',number:71,name:'Alpha'},{id:'DB88',plcId:'A',number:88,name:'Beta'},{id:'B-DB71',plcId:'B',number:71,name:'Other'}],groups:[{id:'fast',plcId:'A',name:'Fast_500',intervalMs:500,enabled:true},{id:'slow',plcId:'A',name:'Slow_1000',intervalMs:1000,enabled:true}],points,sources:[],storage:{}}};
}
async function fixture(t) {
    const server={view:initial(),calls:[],previews:[],failSave:null};
    const service={bootstrap:{localStorage:true,origin:'fixture'},LocalCommandError,
        async localCall(command,request) {
            server.calls.push({command,request:clone(request??null)});
            if(command==='daa_get_configuration') return clone(server.view);
            if(command==='daa_save_draft') {
                if(server.failSave) { const error=server.failSave;server.failSave=null;throw error; }
                assert.equal(request.expectedEtag,server.view.etag);
                server.view.draft=clone(request.draft);server.view.etag='e'+(Number(server.view.etag.slice(1))+1);
                return clone(server.view);
            }
            throw Error('unexpected test IPC: '+command);
        },
        async previewPointNames(request) {
            server.previews.push(clone(request));assert.equal(request.expectedEtag,server.view.etag);
            return {canConfirm:true,rows:[],readiness:[],previewToken:'owned-token'};
        },
        async confirmPointNames(request) {
            assert.equal(request.expectedEtag,server.view.etag);
            Object.assign(server.view.draft.points.find(p=>p.id===request.pointIds[0]),clone(request.patch));
            server.view.etag='e'+(Number(server.view.etag.slice(1))+1);
            return clone(server.view);
        }};
    const module={exports:{}};
    const imports=id=>{
        if(id==='vue') return {...vue,onMounted(){},onUnmounted(){}};
        if(id==='element-plus') return {ElMessageBox:{confirm:async()=>{}}};
        if(id==='vue-i18n') return {useI18n:()=>({t:key=>key,te:()=>false})};
        if(id.endsWith('/services/localAcquisition')) return service;
        throw Error('unexpected test import: '+id);
    };
    new Function('require','module','exports',compiled)(imports,module,module.exports);
    const scope=vue.effectScope();
    const local=scope.run(()=>module.exports.useLocalAcquisitionConsole());
    t.after(()=>{local.finishPointEdit();scope.stop();});
    await local.reload();await vue.nextTick();
    return {local,server,key:module.exports.localConsoleKey};
}
function mountPointScript(t, fixture) {
    // 挂载真实SFC的setup/watch/lifecycle；使用无DOM宿主，不启动浏览器或原生应用。
    const sfc=require('vue/compiler-sfc');
    const text=readFileSync(new URL('../src/app/plc/views/points/index.vue',import.meta.url),'utf8');
    const {descriptor}=sfc.parse(text);
    const script=sfc.compileScript(descriptor,{id:'direct-point-editing'}).content;
    const code=ts.transpileModule(script,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText;
    const module={exports:{}};
    new Function('require','module','exports',code)(id=>{
        if(id==='vue') return vue;
        if(id==='vue-i18n') return {useI18n:()=>({t:key=>key,te:()=>false})};
        if(id.endsWith('/composables/useLocalAcquisitionConsole')) return {localConsoleKey:fixture.key};
        return {default:{}};
    },module,module.exports);
    const node=type=>({type,children:[],parent:null});
    const renderer=vue.createRenderer({
        createElement:node,createText:node,createComment:node,
        setText(){},setElementText(){},patchProp(){},
        insert(child,parent){child.parent=parent;parent.children.push(child);},
        remove(child){if(child.parent) child.parent.children=child.parent.children.filter(item=>item!==child);},
        parentNode:child=>child.parent,nextSibling:()=>null,
    });
    let state;
    const component=module.exports.default;
    const app=renderer.createApp({...component,setup(props,context){state=component.setup(props,context);return ()=>vue.h('div');}});
    app.provide(fixture.key,fixture.local);app.mount(node('root'));
    t.after(()=>app.unmount());
    return state;
}
test('batch grouping uses checked IDs across filters/pages and excludes another PLC',async t=>{
    const {local}=await fixture(t);
    local.selectedNameIds=['p0','p2','other','missing'];
    local.selectedDb='DB71';local.query='no visible rows';local.pointPage=2;
    assert.equal(local.points.length,0);assert.equal(local.selectedPoints.length,2);
    local.bulk('slow',true);
    for(const p of local.draft.points) assert.equal(p.groupId,['p0','p2'].includes(p.id)?'slow':'fast',p.id);
    local.bulk(null,false);
    for(const p of local.draft.points) assert.equal(p.enabled,!['p0','p2'].includes(p.id),p.id);
});
test('empty selection, invalid group, busy state and open editor cannot mutate groups',async t=>{
    const {local}=await fixture(t);const before=clone(local.draft);
    local.bulk('slow',true);assert.deepEqual(local.draft,before);
    local.selectedNameIds=['p0'];local.bulk('unknown',true);assert.deepEqual(local.draft,before);
    local.busy=true;local.bulk('slow',true);local.busy=false;
    local.editing=true;local.bulk('slow',true);local.editing=false;
    assert.deepEqual(local.draft,before);
});
test('save-and-edit preserves pending group edits and previews a point with the new ETag',async t=>{
    const {local,server}=await fixture(t);
    local.groups[0].intervalMs=750;local.selectedNameIds=['p0'];local.bulk('slow',true);
    const point=await local.preparePointEdit('p1');
    assert.equal(server.view.draft.groups[0].intervalMs,750);
    assert.equal(server.view.draft.points[0].groupId,'slow');
    assert.equal(local.dirty,false);assert.equal(local.editing,true);
    point.groupId='slow';local.stagePointEdit(point);
    await new Promise(resolve=>setTimeout(resolve,220));
    assert.equal(server.previews.at(-1).expectedEtag,'e2');
    assert.equal(server.previews.at(-1).patch.groupId,'slow');
    assert.equal(await local.confirmNames(),true);
    assert.equal(local.draft.points[1].groupId,'slow');
    assert.equal(local.draft.points[0].groupId,'slow');
    assert.equal(local.draft.groups[0].intervalMs,750);
    assert.equal(local.editing,false);assert.equal(local.dirty,false);
    const saves=server.calls.filter(c=>c.command==='daa_save_draft').length;
    assert.ok(await local.preparePointEdit('p2'));
    assert.equal(server.calls.filter(c=>c.command==='daa_save_draft').length,saves);
});
test('save conflict preserves pending input, clears busy and does not open an editor',async t=>{
    const {local,server}=await fixture(t);
    local.groups[0].name='Pending name';server.failSave=new LocalCommandError('draft_conflict','external-etag');
    assert.equal(await local.preparePointEdit('p0'),null);
    assert.equal(local.groups[0].name,'Pending name');assert.equal(local.dirty,true);
    assert.equal(local.busy,false);assert.equal(local.editing,false);
    assert.equal(local.conflictVersion,'external-etag');
    assert.equal(server.calls.filter(c=>c.command==='daa_get_configuration').length,1);
});
test('clean editor changes remain detached until confirmation and cancellation releases editing',async t=>{
    const {local,server}=await fixture(t);
    const before=clone(local.draft);const point=await local.preparePointEdit('p0');
    point.groupId='slow';point.enabled=false;
    assert.deepEqual(local.draft,before);
    local.finishPointEdit();assert.equal(local.editing,false);
    assert.equal(server.calls.filter(c=>c.command==='daa_save_draft').length,0);
    assert.ok(await local.preparePointEdit('p1'));
});
test('accepting reload clears stale editing and later saves retain valid checked IDs',async t=>{
    const {local}=await fixture(t);
    local.editing=true;await local.reload();await vue.nextTick();assert.equal(local.editing,false);
    local.selectedNameIds=['p0','other','missing'];local.groups[0].intervalMs=900;
    assert.equal(await local.save(),true);assert.equal(local.dirty,false);assert.equal(local.busy,false);
    assert.deepEqual(local.selectedNameIds,['p0']);
    assert.ok(await local.preparePointEdit('p0'));
});
test('saving preserves the all-DB scope and a valid single-DB filter',async t=>{
    const {local}=await fixture(t);
    assert.equal(local.selectedDb,'');
    local.selectedDb='DB88';local.groups[0].intervalMs=600;await local.save();
    assert.equal(local.selectedDb,'DB88');
    local.selectedDb='';local.groups[0].intervalMs=700;await local.save();
    assert.equal(local.selectedDb,'');
});
test('actual point dialog opens after pending draft save and can edit a group again after confirmation',async t=>{
    const f=await fixture(t),script=mountPointScript(t,f);
    f.local.groups[0].intervalMs=750;
    await script.editLocalPoint(f.local.draft.points[0]);await vue.nextTick();
    assert.equal(script.pointEditor.value.id,'p0');assert.equal(f.local.editing,true);
    script.pointEditor.value.groupId='slow';
    await new Promise(resolve=>setTimeout(resolve,220));
    await script.applyLocalPoint();await vue.nextTick();
    assert.equal(script.pointEditor.value,null);assert.equal(f.local.editing,false);assert.equal(f.local.dirty,false);
    assert.equal(f.server.view.draft.points[0].groupId,'slow');
    assert.equal(f.server.view.draft.groups[0].intervalMs,750);
    await script.editLocalPoint(f.local.draft.points[1]);await vue.nextTick();
    assert.equal(script.pointEditor.value.id,'p1');assert.equal(f.local.editing,true);
    script.cancelLocalPoint();assert.equal(f.local.editing,false);
});
test('actual point dialog stays closed on save failure and releases state on reload',async t=>{
    const f=await fixture(t),script=mountPointScript(t,f);
    f.local.groups[0].name='Unsaved group';f.server.failSave=new LocalCommandError('draft_conflict');
    await script.editLocalPoint(f.local.draft.points[0]);
    assert.equal(script.pointEditor.value,null);assert.equal(f.local.dirty,true);assert.equal(f.local.editing,false);
    assert.equal(f.local.groups[0].name,'Unsaved group');
    await f.local.reload();await vue.nextTick();
    await script.editLocalPoint(f.local.draft.points[0]);await vue.nextTick();
    assert.equal(f.local.editing,true);
    await f.local.reload();await vue.nextTick();
    assert.equal(script.pointEditor.value,null);assert.equal(f.local.editing,false);
});
test('new selection and save-and-edit translations have symmetric keys and placeholders',()=>{
    const zh=JSON.parse(readFileSync(new URL('../src/locales/zh-CN/common.json',import.meta.url),'utf8'));
    const en=JSON.parse(readFileSync(new URL('../src/locales/en-US/common.json',import.meta.url),'utf8'));
    for(const key of ['assignSelected','disableSelected','selectedGroupHint','saveAndEdit']) {
        assert.equal(typeof zh.local[key],'string');assert.equal(typeof en.local[key],'string');
        assert.deepEqual(zh.local[key].match(/\{[^}]+\}/g)||[],en.local[key].match(/\{[^}]+\}/g)||[]);
    }
});
