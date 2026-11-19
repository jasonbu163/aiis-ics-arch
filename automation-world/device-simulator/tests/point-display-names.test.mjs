/** DS-004 组件自检：真实 Vue 组件逻辑运行在内存 renderer，不接触配置库或设备。 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';
import {createRequire} from 'node:module';
import ts from 'typescript';
import * as Vue from 'vue';
import { parse, compileScript } from 'vue/compiler-sfc';

const source = fs.readFileSync(new URL('../src/app/simulator/components/PointEditor.vue', import.meta.url), 'utf8');
const { descriptor } = parse(source, { filename: 'PointEditor.vue' });
const script = compileScript(descriptor, { id: 'ds4-test', inlineTemplate: true }).content;
const code = ts.transpileModule(script, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, esModuleInterop: true } }).outputText;
const key = Symbol('simulator');
const Button = Vue.defineComponent({ inheritAttrs: false, setup(_, {attrs}) { return () => Vue.h('button', attrs); } });
const mocks = { vue: Vue, 'vue-i18n': { useI18n: () => ({t: value => value}) },
    '../../../console/composables/useDeviceSimulator': { simulatorKey: key },
    '../../../components/console/ConsoleActionButton.vue': { default: Button, __esModule: true } };
const mod = { exports: {} };
new Function('require', 'module', 'exports', code)(name => { if (!(name in mocks)) throw Error(name); return mocks[name]; }, mod, mod.exports);
const PointEditor = mod.exports.default;

function host(changes = {}) {
    const make = type => ({type, props: {}, children: [], parent: null, text: ''});
    const renderer = Vue.createRenderer({
        createElement: make, createText: text => ({...make('#text'), text}), createComment: text => ({...make('#comment'), text}),
        setText: (node, text) => { node.text = text; }, setElementText: (node, text) => { node.text = text; node.children = []; },
        parentNode: node => node.parent, nextSibling: node => node.parent?.children[node.parent.children.indexOf(node) + 1] ?? null,
        insert: (node, parent, anchor) => { if (node.parent) node.parent.children.splice(node.parent.children.indexOf(node), 1); node.parent = parent; const at = anchor ? parent.children.indexOf(anchor) : -1; parent.children.splice(at < 0 ? parent.children.length : at, 0, node); },
        remove: node => { if (node.parent) node.parent.children.splice(node.parent.children.indexOf(node), 1); node.parent = null; },
        patchProp: (node, prop, _old, value) => { node.props[prop] = value; },
    });
    const wrapper = Vue.defineComponent({ inheritAttrs: false, setup(_, {slots, attrs}) { return () => Vue.h('section', attrs, [...(slots.default?.() || []), ...(slots.footer?.() || [])]); } });
    const input = Vue.defineComponent({ inheritAttrs: false, props: ['modelValue'], emits: ['update:modelValue'], setup(props, {attrs, emit}) { return () => Vue.h('input', {...attrs, value: props.modelValue, onInput: event => emit('update:modelValue', event.target.value)}); } });
    const root = make('root'), visible = Vue.ref(false), emitted = [], local = Vue.reactive({editing:false, finishEditor:null, discardEditor:null});
    const original = {id:'id',name:'',displayName:'source comment',dataType:'BOOL',enabled:true,sourcePath:'Flag',segments:[],byte:null,bit:null,manualReason:'',manual:false,policy:{},confirmations:{initial:null,policy:null}, ...changes};
    const app = renderer.createApp({setup() { return () => Vue.h(PointEditor, {modelValue:visible.value, point:original, 'onUpdate:modelValue': value => {visible.value = value;}, onConfirm: point => emitted.push(point)}); }});
    app.provide(key, local);
    for (const name of ['el-dialog','el-form','el-form-item','el-select','el-option','el-alert','el-switch','el-input-number']) app.component(name, wrapper);
    app.component('el-input', input);
    app.mount(root);
    const find = (node, id) => node.props['data-testid'] === id ? node : node.children.map(child => find(child, id)).find(Boolean);
    const set = async (id, value) => { const node = find(root, id); assert.ok(node, id); node.props.onInput({target:{value}}); await Vue.nextTick(); };
    const click = async id => { const node = find(root, id); assert.ok(node, id); node.props.onClick(); await Vue.nextTick(); };
    const open = async () => { visible.value = true; await Vue.nextTick(); };
    return {root, visible, emitted, local, original, find: id => find(root, id), set, click, open, close: () => app.unmount()};
}

test('cancel preserves an unconfirmed imported point and all original fields', async () => {
    const view = host(); await view.open();
    await view.set('point-display-name-zh', '本地'); await view.set('point-description', 'discarded');
    await view.click('point-cancel');
    assert.equal(view.emitted.length, 0); assert.equal(view.local.editing, false);
    assert.equal(view.original.displayName, 'source comment'); assert.equal(view.original.bit, null);
    await view.open();
    assert.equal(view.find('point-display-name-zh').props.value, '');
    assert.equal(view.find('point-description').props.value, '');
    view.close();
});

test('byte limits reject instead of truncating; confirm keeps independent metadata and address', async () => {
    const view = host(); await view.open();
    await view.set('point-display-name-zh', '界'.repeat(86));
    await view.click('point-confirm');
    assert.equal(view.emitted.length, 0); assert.equal(view.visible.value, true);
    await view.set('point-display-name-zh', ' 温度 '); await view.set('point-display-name-en', '');
    await view.set('point-description', '字'.repeat(167)); await view.click('point-confirm');
    assert.equal(view.emitted.length, 0);
    await view.set('point-description', ' explicit '); await view.click('point-confirm');
    assert.equal(view.emitted.length, 1);
    assert.deepEqual(view.emitted[0].displayNames, {'zh-CN':' 温度 ', 'en-US':''});
    assert.equal(view.emitted[0].description, ' explicit ');
    assert.equal(view.emitted[0].displayName, 'source comment');
    assert.equal(view.emitted[0].name, ''); assert.equal(view.emitted[0].byte, null); assert.equal(view.emitted[0].bit, null);
    view.close();
});

test('editing only metadata leaves an incomplete manual point and its existing address untouched', async () => {
    const view = host({name:'Manual', manual:true, dataType:'INT', byte:0, bit:1, manualReason:'', displayNames:{'zh-CN':'中文', 'en-US':'English'}, description:'old'});
    await view.open(); await view.set('point-display-name-zh', ''); await view.set('point-description', ''); await view.click('point-confirm');
    assert.equal(view.emitted.length, 1);
    assert.deepEqual(view.emitted[0].displayNames, {'zh-CN':'', 'en-US':'English'});
    assert.equal(view.emitted[0].description, undefined);
    assert.equal(view.emitted[0].dataType, 'INT'); assert.equal(view.emitted[0].byte, 0); assert.equal(view.emitted[0].bit, 1);
    assert.equal(view.emitted[0].manualReason, ''); assert.equal(view.emitted[0].name, 'Manual');
    view.close();
});

test('locale files remain symmetric and table uses the shared column sizing wrapper', () => {
    const en = JSON.parse(fs.readFileSync(new URL('../src/app/simulator/locales/en-US.json', import.meta.url)));
    const zh = JSON.parse(fs.readFileSync(new URL('../src/app/simulator/locales/zh-CN.json', import.meta.url)));
    const keys = value => Object.entries(value).flatMap(([key, item]) => item && typeof item === 'object' && !Array.isArray(item) ? keys(item).map(sub => key + '.' + sub) : [key]).sort();
    assert.deepEqual(keys(en), keys(zh));
    const page = fs.readFileSync(new URL('../src/app/simulator/views/points/index.vue', import.meta.url), 'utf8');
    assert.match(page, /table-id="configuration\.points"/); assert.match(page, /column-key="displayName" min-width="200"/);
    assert.match(page, /row\.displayNames\?\.\[locale === 'zh-CN' \? 'zh-CN' : 'en-US'\] \?\? ''/);
});

test('real point-page render switches language without editing or saving the draft', async () => {
    const pageSource = fs.readFileSync(new URL('../src/app/simulator/views/points/index.vue', import.meta.url), 'utf8');
    const pageScript = compileScript(parse(pageSource, {filename:'points.vue'}).descriptor, {id:'ds4-page', inlineTemplate:true}).content;
    const compiled = ts.transpileModule(pageScript, {compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022,esModuleInterop:true}}).outputText;
    const locale = Vue.ref('zh-CN'), rowsKey = Symbol('rows');
    const wrapper = Vue.defineComponent({inheritAttrs:false, setup(_, {slots,attrs}) { return () => Vue.h('section', attrs, slots.default?.()); }});
    const table = Vue.defineComponent({inheritAttrs:false, props:['data'], setup(props, {slots,attrs}) { Vue.provide(rowsKey, Vue.computed(() => props.data)); return () => Vue.h('table', attrs, slots.default?.()); }});
    const column = Vue.defineComponent({inheritAttrs:false, props:['prop'], setup(props, {slots,attrs}) { const rows = Vue.inject(rowsKey); return () => Vue.h('column', {field:attrs['column-key']}, (rows.value || []).map(row => Vue.h('cell', slots.default ? slots.default({row}) : String(row[props.prop] ?? '')))); }});
    const point = (id, names) => ({id,name:'tech-'+id,displayName:'legacy-'+id,displayNames:names,dataType:'INT',sourcePath:'',byte:0,bit:null,manual:true,manualReason:'fixture',enabled:true,policy:{},confirmations:{initial:null,policy:null}});
    const db = {id:'db',name:'db',number:71,length:4,manual:true,enabled:true,points:[point('a', {'zh-CN':'中文甲','en-US':''}), point('b', {'zh-CN':'','en-US':'English B'})]};
    const instance = {id:'i',name:'fixture',dbs:[db]}, draft = {schemaVersion:1,instances:[instance],sourceVersions:[]};
    let saves = 0;
    let compared=0;
    const local = Vue.reactive({selectedDb:db,selected:instance,draft,instanceId:'i',dbId:'db',dirty:false,busy:false,saveCanResolve:true,configuration:{etag:'unchanged'},save:()=>{saves++;},noteSaveDifferences:()=>{compared++;}});
    const modules = {vue:Vue,'vue-i18n':{useI18n:()=>({t:value=>value,locale})},
        '../../../../console/composables/useDeviceSimulator':{simulatorKey:key}, '../../../../services/deviceSimulator':{}};
    for (const name of ['ConsoleCard','ConsoleActionButton','ConsoleTableShell','ConsoleOperationDialog','ConfigRevisionBar']) modules['../../../../components/console/'+name+'.vue'] = {default:wrapper,__esModule:true};
    modules['../../../../components/console/ConsoleDataTable.vue'] = {default:table,__esModule:true};
    for (const name of ['SourceImportPanel','PointEditor','PointNamePreviewDialog']) modules['../../components/'+name+'.vue'] = {default:wrapper,__esModule:true};
    const page = {exports:{}};
    new Function('require','module','exports',compiled)(name => {if (!(name in modules)) throw Error(name); return modules[name];}, page, page.exports);
    const make = type => ({type,props:{},children:[],parent:null,text:''});
    const renderer = Vue.createRenderer({createElement:make,createText:text=>({...make('#text'),text}),createComment:text=>({...make('#comment'),text}),setText:(n,v)=>{n.text=v;},setElementText:(n,v)=>{n.text=v;n.children=[];},parentNode:n=>n.parent,nextSibling:n=>n.parent?.children[n.parent.children.indexOf(n)+1]??null,insert:(n,p,a)=>{if(n.parent)n.parent.children.splice(n.parent.children.indexOf(n),1);n.parent=p;const i=a?p.children.indexOf(a):-1;p.children.splice(i<0?p.children.length:i,0,n);},remove:n=>{if(n.parent)n.parent.children.splice(n.parent.children.indexOf(n),1);n.parent=null;},patchProp:(n,k,_old,v)=>{n.props[k]=v;}});
    const root=make('root'), app=renderer.createApp(page.exports.default); app.provide(key,local);
    for(const name of ['el-select','el-option','el-form','el-form-item','el-input','el-input-number','el-switch','el-checkbox','el-empty','el-dialog','el-alert','el-pagination']) app.component(name,wrapper);
    app.component('el-table-column',column); app.mount(root); await Vue.nextTick();
    const walk = n => [n,...n.children.flatMap(walk)], textOf = n => n.text + n.children.map(textOf).join('');
    const cells = () => walk(root).find(n=>n.type==='column' && n.props.field==='displayName').children.map(textOf);
    const before = JSON.stringify(local.draft);
    assert.deepEqual(cells(), ['中文甲','']);
    locale.value='en-US'; await Vue.nextTick(); assert.deepEqual(cells(), ['', 'English B']);
    locale.value='zh-CN'; await Vue.nextTick(); assert.deepEqual(cells(), ['中文甲','']);
    assert.equal(JSON.stringify(local.draft),before); assert.equal(local.configuration.etag,'unchanged'); assert.equal(saves,0);
    local.uncertainSave = {expectedEtag:'before-save',submitted:draft,confirmPoints:[],reason:'save_receipt_unknown',cleanupUnproven:false};
    const saved=structuredClone(draft); saved.instances[0].dbs[0].points[0].description='saved description'; saved.instances[0].dbs[0].points[0].confirmations.initial='saved-confirmation';
    local.saveReview = {configuration:{etag:'readback',latestRevision:'revision-1',selections:[],workspace:saved},matchesSubmitted:false};
    await Vue.nextTick();
    assert.ok(walk(root).find(n=>n.props['data-testid']==='save-unknown-inspect'));
    assert.ok(textOf(walk(root).find(n=>n.props['data-testid']==='save-unknown-saved-points')).includes('中文甲'));
    const compare=walk(root).find(n=>n.props['data-testid']==='save-unknown-compare'); assert.ok(compare); compare.props.onClick(); await Vue.nextTick();
    const differences=textOf(walk(root).find(n=>n.props['data-testid']==='save-unknown-differences'));
    assert.ok(differences.includes('saved description')); assert.ok(differences.includes('saved-confirmation')); assert.equal(compared,1);
    local.uncertainControls = [{id:1,instanceId:'i',command:'stop',code:'runtime_task_receipt_unknown',epoch:'7',loadedRevision:'r1'}];
    local.controlReview = {facts:[{instanceId:'i',name:'fixture',state:'stopped',epoch:'7',loadedRevision:'r1'}],generation:1};
    await Vue.nextTick();
    assert.ok(walk(root).find(n=>n.props['data-testid']==='control-unknown-inspect'));
    assert.ok(walk(root).find(n=>n.props['data-testid']==='control-unknown-accept'));
    assert.ok(textOf(walk(root).find(n=>n.props['data-testid']==='control-unknown-list')).includes('runtime_task_receipt_unknown'));
    assert.ok(textOf(walk(root).find(n=>n.props['data-testid']==='control-unknown-current')).includes('stopped'));
    app.unmount();
});

const require = createRequire(import.meta.url);
const stateSource = fs.readFileSync(new URL('../src/console/composables/useDeviceSimulator.ts', import.meta.url), 'utf8');
const stateCode = ts.transpileModule(stateSource, {compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
class StateFailure extends Error { constructor(code, currentEtag=null, unknown=false) { super(code); this.code=code; this.currentEtag=currentEtag; this.unknown=unknown; } }
function stateHost(methods) {
    let tick=0;
    const ipc={IpcFailure:StateFailure,desktopAvailable:true,getBootstrap:async()=>({version:'test'}),getSnapshot:async()=>({instances:[],stale:false}),...methods};
    const context={exports:{},require:name=>name==='vue'?require('vue'):ipc,structuredClone,performance:{now:()=>tick+=2000},document:{hidden:false}};
    vm.runInNewContext(stateCode,context,{filename:'useDeviceSimulator.js'});
    return context.exports.useDeviceSimulator();
}
function facts(etag='etag-before') {
    return {etag,latestRevision:'revision-before',revisions:[],revisionTotal:0,selections:[],issues:[],draftMatchesLatest:false,workspace:{schemaVersion:1,instances:[{id:'i',name:'Local',dbs:[{id:'db',name:'DB',points:[{id:'p',name:'Point',displayName:'legacy',displayNames:{'zh-CN':'旧','en-US':''},description:'old'}]}]}],sourceVersions:[]}};
}
const clone = value => structuredClone(value);
async function pendingState() {
    let server=facts(), saveCalls=0, reads=0, controls=[];
    const state=stateHost({getConfiguration:async()=>{reads++;return clone(server);},saveConfiguration:async(_etag,workspace)=>{saveCalls++;server={...clone(server),etag:'etag-saved',workspace:clone(workspace)};throw new StateFailure('save_receipt_unknown',null,true);},controlInstance:async intent=>{controls.push(intent.command);return {ok:true};}});
    await state.reload();
    state.draft.value.instances[0].dbs[0].points[0].displayNames['zh-CN']='新值';
    assert.equal(await state.save(),false);
    return {state,get server(){return server;},set server(v){server=v;},get saves(){return saveCalls;},get reads(){return reads;},controls};
}

test('unknown save from any page freezes resubmission and checks saved facts without overwriting local edits', async () => {
    const ctx=await pendingState(), state=ctx.state;
    assert.equal(state.error.value,'save_receipt_unknown'); assert.equal(state.unknown.value,true); assert.equal(state.dirty.value,true);
    const local=JSON.stringify(state.draft.value), oldEtag=state.configuration.value.etag;
    assert.equal(await state.save(),false); await state.action(async()=>{throw Error('must not run');});
    assert.equal(ctx.saves,1); assert.equal(state.configuration.value.etag,oldEtag); assert.equal(JSON.stringify(state.draft.value),local);
    const readsBeforeRefresh=ctx.reads; await state.refresh();
    assert.equal(ctx.reads,readsBeforeRefresh); assert.ok(state.uncertainSave.value); assert.equal(state.unknown.value,true);
    const row={instanceId:'i',loadedRevision:'r',epoch:'1'};
    await state.control(row,'start'); await state.control(row,'stop'); assert.deepEqual(ctx.controls,['stop']);
    assert.equal(await state.reviewUncertainSave(),true);
    assert.equal(state.saveReview.value.configuration.etag,'etag-saved'); assert.equal(state.saveReview.value.matchesSubmitted,true);
    assert.equal(JSON.stringify(state.draft.value),local); assert.equal(state.configuration.value.etag,oldEtag);
    const readsBefore=ctx.reads;
    assert.equal(await state.acceptReviewedSave(),true); assert.equal(ctx.reads,readsBefore+1);
    assert.equal(state.uncertainSave.value,null); assert.equal(state.unknown.value,false); assert.equal(state.configuration.value.etag,'etag-saved');
    assert.equal(JSON.stringify(state.draft.value),local); assert.equal(state.dirty.value,false); assert.equal(ctx.saves,1);
    for (const lang of ['en-US','zh-CN']) {
        const labels=JSON.parse(fs.readFileSync(new URL(`../src/app/simulator/locales/${lang}.json`,import.meta.url)));
        assert.ok(labels.errors.save_receipt_unknown.includes('DB')); assert.ok(labels.unknownReceipt.includes('DB'));
    }
});

test('remote ETag change and later local edits prevent confirmation; only explicit reload discards local draft', async () => {
    const ctx=await pendingState(), state=ctx.state, local=JSON.stringify(state.draft.value);
    await state.reviewUncertainSave();
    ctx.server={...clone(ctx.server),etag:'etag-concurrent'};
    assert.equal(await state.acceptReviewedSave(),false);
    assert.equal(state.saveReviewError.value,'changed'); assert.ok(state.uncertainSave.value);
    assert.equal(state.configuration.value.etag,'etag-before'); assert.equal(JSON.stringify(state.draft.value),local);
    ctx.server.workspace.instances[0].dbs[0].points[0].description='another writer';
    ctx.server.etag='etag-different';
    assert.equal(await state.reviewUncertainSave(),true); assert.equal(state.saveReview.value.matchesSubmitted,false);
    assert.equal(await state.acceptReviewedSave(),false); assert.equal(await state.save(),false); assert.equal(ctx.saves,1);
    assert.equal(JSON.stringify(state.draft.value),local);
    // Simulates the existing explicitly confirmed Reload draft action.
    state.noteSaveDifferences(); await state.action(state.reload);
    assert.equal(state.uncertainSave.value,null); assert.equal(state.configuration.value.etag,'etag-different');
    assert.equal(state.draft.value.instances[0].dbs[0].points[0].description,'another writer');
});

test('a changed ETag after comparison blocks explicit reload without overwriting local inputs', async () => {
    const ctx=await pendingState(), state=ctx.state, local=JSON.stringify(state.draft.value);
    ctx.server.workspace.instances[0].name='another writer'; ctx.server.etag='read-etag';
    await state.reviewUncertainSave(); state.noteSaveDifferences();
    ctx.server.etag='later-etag'; await state.action(state.reload);
    assert.equal(state.saveReviewError.value,'changed'); assert.ok(state.uncertainSave.value); assert.equal(JSON.stringify(state.draft.value),local); assert.equal(ctx.saves,1);
});

test('local edits during readback or confirmed reload remain intact and never unlock silently', async () => {
    let server=facts(), hold=null, holdRead=false, saves=0;
    const state=stateHost({getConfiguration:()=>holdRead?new Promise(resolve=>{hold=resolve;}):Promise.resolve(clone(server)),saveConfiguration:async(_etag,workspace)=>{saves++;server={...server,etag:'saved',workspace:clone(workspace)};throw new StateFailure('save_receipt_unknown',null,true);}});
    await state.reload(); state.draft.value.instances[0].name='submitted'; await state.save();
    await state.reviewUncertainSave();
    holdRead=true; const confirming=state.acceptReviewedSave();
    state.draft.value.instances[0].name='later local edit'; hold(clone(server));
    assert.equal(await confirming,false); assert.equal(state.saveReviewError.value,'local'); assert.ok(state.uncertainSave.value);
    state.noteSaveDifferences(); const reloading=state.action(state.reload); state.draft.value.instances[0].name='even later edit'; hold(clone(server)); await reloading;
    assert.equal(state.draft.value.instances[0].name,'even later edit'); assert.ok(state.uncertainSave.value); assert.equal(saves,1);
});

test('a known save followed by failed draft readback also pauses further saves', async () => {
    let server=facts(), failRead=false, saves=0;
    const state=stateHost({getConfiguration:async()=>{if(failRead) throw new StateFailure('storage_query_timeout');return clone(server);},saveConfiguration:async(_etag,workspace)=>{saves++;server={...server,etag:'saved',workspace:clone(workspace)};failRead=true;return {result:'saved'};}});
    await state.reload(); state.draft.value.instances[0].name='saved local';
    assert.equal(await state.save(),false); assert.ok(state.uncertainSave.value); assert.equal(state.unknown.value,false); assert.equal(state.saveOutcome.value,'saved'); assert.equal(state.error.value,'saved_readback_unavailable');
    assert.equal(await state.reviewUncertainSave(),false); assert.equal(state.saveReviewError.value,'read');
    assert.equal(await state.save(),false); assert.equal(saves,1); assert.equal(state.draft.value.instances[0].name,'saved local');
    failRead=false; await state.reviewUncertainSave(); assert.equal(await state.acceptReviewedSave(),true);
});

test('a local edit during a successful save readback is not replaced', async () => {
    let server=facts(), saved=false, releaseRead=null;
    let signalRead; const readStarted=new Promise(resolve=>{signalRead=resolve;});
    const state=stateHost({getConfiguration:()=>saved?new Promise(resolve=>{releaseRead=resolve;signalRead();}):Promise.resolve(clone(server)),saveConfiguration:async(_etag,workspace)=>{server={...server,etag:'saved',workspace:clone(workspace)};saved=true;return {result:'saved'};}});
    await state.reload(); state.draft.value.instances[0].name='submitted';
    const saving=state.save(); await readStarted;
    state.draft.value.instances[0].name='edited while saving'; releaseRead(clone(server));
    assert.equal(await saving,false); assert.ok(state.uncertainSave.value);
    assert.equal(state.draft.value.instances[0].name,'edited while saving'); assert.equal(state.configuration.value.etag,'etag-before');
});

test('a separate unknown stop receipt survives draft reconciliation and read-only refresh', async () => {
    let server=facts(), saves=0, stops=0;
    const state=stateHost({getConfiguration:async()=>clone(server),getSnapshot:async()=>{throw new StateFailure('snapshot_format');},saveConfiguration:async(_etag,workspace)=>{saves++;server={...server,etag:'saved',workspace:clone(workspace)};throw new StateFailure('save_receipt_unknown',null,true);},controlInstance:async()=>{stops++;throw new StateFailure('runtime_task_receipt_unknown',null,true);}});
    await state.reload(); state.draft.value.instances[0].name='submitted'; await state.save();
    await state.control({instanceId:'i',loadedRevision:'r',epoch:'1'},'stop');
    assert.equal(stops,1); assert.ok(state.uncertainSave.value);
    await state.reviewUncertainSave(); assert.equal(await state.acceptReviewedSave(),true);
    assert.equal(state.uncertainSave.value,null); assert.equal(state.unknown.value,true); assert.equal(state.error.value,'runtime_controls_unknown');
    await state.refresh(); assert.equal(state.unknown.value,true); assert.equal(state.error.value,'runtime_controls_unknown');
    assert.equal(await state.save(),false); assert.equal(saves,1);
});

test('all unknown safety controls survive known rejection, background refresh and saved-draft review', async () => {
    let server=facts(), saves=0, calls=[];
    const current=()=>({stale:false,instances:[{instanceId:'i',name:'one',state:'stopped',epoch:'2',loadedRevision:'r1'},{instanceId:'j',name:'two',state:'paused',epoch:'4',loadedRevision:'r2'}]});
    const state=stateHost({getConfiguration:async()=>clone(server),getSnapshot:async()=>current(),saveConfiguration:async(_etag,workspace)=>{saves++;server={...server,etag:'saved',workspace:clone(workspace)};throw new StateFailure('save_receipt_unknown',null,true);},controlInstance:async intent=>{calls.push(intent.command);if(intent.command==='pause'&&intent.instanceId==='i')throw new StateFailure('control_rejected');throw new StateFailure('runtime_task_receipt_unknown',null,true);}});
    await state.reload(); state.draft.value.instances[0].name='submitted'; await state.save();
    const local=JSON.stringify(state.draft.value), i={instanceId:'i',loadedRevision:'r1',epoch:'1'}, j={instanceId:'j',loadedRevision:'r2',epoch:'3'};
    await state.control(i,'stop'); await state.control(i,'pause'); await state.control(j,'stop');
    assert.deepEqual(calls,['stop','pause','stop']);
    assert.deepEqual(Array.from(state.uncertainControls.value,x=>[x.instanceId,x.command,x.epoch]),[['i','stop','1'],['j','stop','3']]);
    await state.refresh(); assert.equal(state.unknown.value,true);
    await state.reviewUncertainSave(); assert.equal(await state.acceptReviewedSave(),true);
    assert.equal(state.error.value,'runtime_controls_unknown'); assert.equal(state.unknown.value,true); assert.equal(state.dirty.value,true);
    assert.equal(JSON.stringify(state.draft.value),local); assert.equal(await state.save(),false); assert.equal(saves,1);
    assert.equal(await state.acceptReviewedControls(),false);
    assert.equal(await state.reviewUncertainControls(),true); assert.equal(state.uncertainControls.value.length,2);
    await state.refresh(); assert.equal(state.uncertainControls.value.length,2);
    assert.equal(await state.acceptReviewedControls(),true); assert.equal(state.uncertainControls.value.length,0); assert.equal(state.unknown.value,false);
});

test('control confirmation during an unknown save requires consistent valid current facts and explicit acknowledgement', async () => {
    let rows=[{instanceId:'i',name:'one',state:'stopped',epoch:'2',loadedRevision:'r1'}], stale=false, fail=false;
    const state=stateHost({getConfiguration:async()=>facts(),getSnapshot:async()=>{if(fail)throw new StateFailure('snapshot_format');return {stale,instances:clone(rows)};},saveConfiguration:async()=>{throw new StateFailure('save_receipt_unknown',null,true);},controlInstance:async()=>{throw new StateFailure('runtime_task_receipt_unknown',null,true);}});
    await state.reload(); await state.save(); await state.control({instanceId:'i',loadedRevision:'r1',epoch:'1'},'stop');
    assert.equal(state.uncertainControls.value.length,1); assert.equal(state.unknown.value,true);
    for (const bad of [[],[{...rows[0]},{...rows[0]}],[{...rows[0],epoch:'invalid'}],[{...rows[0],state:'running',loadedRevision:null}]]) {
        const original=rows; rows=bad; assert.equal(await state.reviewUncertainControls(),false); assert.equal(state.controlReviewError.value,'read'); assert.equal(state.uncertainControls.value.length,1); rows=original;
    }
    stale=true; assert.equal(await state.reviewUncertainControls(),false); stale=false;
    fail=true; assert.equal(await state.reviewUncertainControls(),false); fail=false;
    assert.equal(await state.reviewUncertainControls(),true); rows[0].epoch='3';
    assert.equal(await state.acceptReviewedControls(),false); assert.equal(state.controlReviewError.value,'changed'); assert.equal(state.uncertainControls.value.length,1);
    rows[0]={...rows[0],state:'load_failed',loadedRevision:null};
    assert.equal(await state.reviewUncertainControls(),true); assert.equal(state.controlReview.value.facts[0].loadedRevision,null);
    assert.equal(await state.acceptReviewedControls(),true); assert.equal(state.unknown.value,true); assert.ok(state.uncertainSave.value);
});

test('a safety command during current-state review invalidates confirmation even if the command is rejected', async () => {
    let hold=null, defer=false, calls=0;
    const row={instanceId:'i',name:'one',state:'stopped',epoch:'2',loadedRevision:'r1'};
    const state=stateHost({getConfiguration:async()=>facts(),saveConfiguration:async()=>{throw new StateFailure('save_receipt_unknown',null,true);},getSnapshot:()=>defer?new Promise(resolve=>{hold=resolve;}):Promise.resolve({stale:false,instances:[clone(row)]}),controlInstance:async()=>{calls++;if(calls===1)throw new StateFailure('runtime_task_receipt_unknown',null,true);throw new StateFailure('control_rejected');}});
    await state.reload(); await state.save(); await state.control(row,'stop'); assert.equal(await state.reviewUncertainControls(),true);
    defer=true; const confirming=state.acceptReviewedControls(); await state.control(row,'pause'); hold({stale:false,instances:[clone(row)]});
    assert.equal(await confirming,false); assert.equal(state.controlReviewError.value,'changed'); assert.equal(state.uncertainControls.value.length,1); assert.equal(state.unknown.value,true);
    defer=false; assert.equal(await state.reviewUncertainControls(),true); assert.equal(await state.acceptReviewedControls(),true); assert.equal(state.error.value,'save_receipt_unknown'); assert.equal(state.unknown.value,true);
});

test('save and other unknowns survive a separate explicit runtime control review', async () => {
    let server=facts(), cancels=0;
    const state=stateHost({getConfiguration:async()=>clone(server),getSnapshot:async()=>({stale:false,instances:[{instanceId:'i',name:'one',state:'running',epoch:'1',loadedRevision:'r1'}]}),queryLogs:async()=>({rows:[]}),saveConfiguration:async(_etag,workspace)=>{server={...server,etag:'saved',workspace:clone(workspace)};throw new StateFailure('save_receipt_unknown',null,true);},controlInstance:async()=>{throw new StateFailure('runtime_task_receipt_unknown',null,true);},cancelPreview:async()=>{cancels++;throw new StateFailure('ipc_transport_unknown',null,true);}});
    await state.reload(); state.draft.value.instances[0].name='submitted'; await state.save();
    await state.control({instanceId:'i',loadedRevision:'r1',epoch:'1'},'stop'); await state.releasePreview({});
    assert.equal(cancels,1); assert.equal(await state.reviewUncertainControls(),true); assert.equal(await state.acceptReviewedControls(),true);
    assert.ok(state.uncertainSave.value); assert.equal(state.error.value,'save_receipt_unknown'); assert.equal(state.unknown.value,true);
    await state.reviewUncertainSave(); assert.equal(await state.acceptReviewedSave(),true);
    assert.equal(state.error.value,'preview_release_unknown'); assert.equal(state.unknown.value,true); assert.equal(await state.save(),false);
    await state.pageRevisions(0); assert.equal(state.error.value,'preview_release_unknown'); assert.equal(state.unknown.value,true);
    await state.loadLogs(); assert.equal(state.error.value,'preview_release_unknown'); assert.equal(state.unknown.value,true);
    const separate=stateHost({getConfiguration:async()=>facts(),getSnapshot:async()=>({stale:false,instances:[{instanceId:'i',name:'one',state:'stopped',epoch:'2',loadedRevision:'r1'}]}),controlInstance:async()=>{throw new StateFailure('runtime_task_receipt_unknown',null,true);}});
    await separate.reload(); await separate.action(async()=>{throw new StateFailure('apply_receipt_unknown',null,true);});
    await separate.control({instanceId:'i',loadedRevision:'r1',epoch:'1'},'stop');
    assert.equal(separate.uncertainControls.value.length,0); assert.equal(await separate.reviewUncertainControls(),false);
});

test('an existing unknown apply or point-write result is not cleared by save recovery actions', async () => {
    for (const code of ['apply_receipt_unknown','runtime_task_receipt_unknown']) {
        let saves=0;
        const state=stateHost({getConfiguration:async()=>facts(),saveConfiguration:async()=>{saves++;return {result:'saved'};},getSnapshot:async()=>{throw new StateFailure('snapshot_format');}});
        await state.reload(); state.error.value=code; state.unknown.value=true;
        assert.equal(await state.save(),false); assert.equal(await state.reviewUncertainSave(),false); assert.equal(await state.acceptReviewedSave(),false);
        await state.refresh(); assert.equal(state.error.value,code); assert.equal(state.unknown.value,true); assert.equal(saves,0);
    }
});

test('transport and task unknown cannot be resolved by matching reads before a late save', async () => {
    for (const code of ['ipc_transport_unknown','runtime_task_receipt_unknown']) {
        let server=facts(), saves=0, finishLate;
        const late=new Promise(resolve=>{finishLate=resolve;});
        const state=stateHost({getConfiguration:async()=>clone(server),saveConfiguration:async(_etag,workspace,ids)=>{
            saves++; void late.then(()=>{server={...server,etag:'late',workspace:clone(workspace)};server.workspace.instances[0].dbs[0].points[0].confirmations={initial:'late-initial',policy:'late-policy'};});
            assert.deepEqual(Array.from(ids),['p']); throw new StateFailure(code,null,true);
        }});
        await state.reload(); const local=JSON.stringify(state.draft.value);
        assert.equal(await state.save(['p']),false); assert.deepEqual(Array.from(state.uncertainSave.value.confirmPoints),['p']);
        assert.equal(await state.reviewUncertainSave(),true); assert.equal(await state.acceptReviewedSave(),false);
        assert.equal(await state.reviewUncertainSave(),true); state.noteSaveDifferences(); await state.action(state.reload);
        assert.ok(state.uncertainSave.value); assert.equal(state.unknown.value,true); assert.equal(state.configuration.value.etag,'etag-before');
        assert.equal(JSON.stringify(state.draft.value),local); assert.equal(await state.save(),false); assert.equal(saves,1);
        finishLate(); await late; assert.equal(server.etag,'late'); assert.equal(server.workspace.instances[0].dbs[0].points[0].confirmations.initial,'late-initial');
        assert.ok(state.uncertainSave.value); assert.equal(state.unknown.value,true);
    }
});

test('submitted confirmation IDs remain the original request even if caller selection changes in flight', async () => {
    let rejectSave, sent;
    const state=stateHost({getConfiguration:async()=>facts(),saveConfiguration:async(_etag,_workspace,ids)=>{sent=ids;return new Promise((_resolve,reject)=>{rejectSave=reject;});}});
    await state.reload(); const ids=['p']; const saving=state.save(ids); ids.push('other');
    rejectSave(new StateFailure('ipc_transport_unknown',null,true)); await saving;
    assert.deepEqual(Array.from(sent),['p']); assert.deepEqual(Array.from(state.uncertainSave.value.confirmPoints),['p']);
});

test('service receipt readback shows changed confirmations without replacing local inputs', async () => {
    for (const code of ['save_receipt_unknown','save_commit_unknown']) {
        let server=facts(), saves=0;
        const state=stateHost({getConfiguration:async()=>clone(server),saveConfiguration:async(_etag,workspace,ids)=>{
            saves++; assert.deepEqual(Array.from(ids),['p']); server={...server,etag:'server-after',workspace:clone(workspace)};
            server.workspace.instances[0].namesConfirmation='server-name-confirmation';
            server.workspace.instances[0].dbs[0].addressConfirmation={method:'manual'};
            server.workspace.instances[0].dbs[0].points[0].confirmations={initial:'server-initial',policy:'server-policy'};
            throw new StateFailure(code,null,true);
        }});
        await state.reload(); state.draft.value.instances[0].dbs[0].points[0].displayNames['en-US']='local name';
        const local=JSON.stringify(state.draft.value); assert.equal(await state.save(['p']),false);
        assert.equal(state.uncertainSave.value.reason,code); assert.equal(await state.reviewUncertainSave(),true);
        assert.equal(state.saveReview.value.matchesSubmitted,false); assert.equal(state.saveReview.value.configuration.workspace.instances[0].dbs[0].points[0].confirmations.initial,'server-initial');
        await state.action(state.reload); assert.equal(JSON.stringify(state.draft.value),local); assert.ok(state.uncertainSave.value);
        state.noteSaveDifferences(); await state.action(state.reload);
        assert.equal(state.uncertainSave.value,null); assert.equal(state.draft.value.instances[0].dbs[0].points[0].displayNames['en-US'],'local name');
        assert.equal(state.draft.value.instances[0].dbs[0].points[0].confirmations.policy,'server-policy'); assert.equal(saves,1);
    }
});

test('unknown save with removed instance cannot use a draft read as runtime cleanup proof', async () => {
    let server=facts();
    const state=stateHost({getConfiguration:async()=>clone(server),saveConfiguration:async(_etag,workspace)=>{server={...server,etag:'changed',workspace:clone(workspace)};throw new StateFailure('save_receipt_unknown',null,true);}});
    await state.reload(); state.draft.value.instances=[]; await state.save();
    assert.equal(state.uncertainSave.value.cleanupUnproven,true); assert.equal(await state.reviewUncertainSave(),true);
    assert.equal(await state.acceptReviewedSave(),false); state.noteSaveDifferences(); await state.action(state.reload);
    assert.ok(state.uncertainSave.value); assert.equal(state.unknown.value,true);
});

test('known save and unchanged replies remain distinct from failed post-save readback', async () => {
    for (const result of ['saved','unchanged']) {
        let failing=false, saves=0;
        const state=stateHost({getConfiguration:async()=>{if(failing)throw new StateFailure('storage_query_timeout');return facts();},saveConfiguration:async()=>{saves++;failing=true;return {result,etag:'etag-before',revisionId:null,cleanupPending:[]};}});
        await state.reload(); assert.equal(await state.save(),false);
        assert.equal(state.saveOutcome.value,result); assert.equal(state.uncertainSave.value.reason,'known_readback'); assert.equal(state.unknown.value,false); assert.equal(state.error.value,'saved_readback_unavailable');
        assert.equal(await state.save(),false); assert.equal(saves,1);
    }
});

test('a concurrent ETag after a known save does not replace the submitted local draft', async () => {
    let server=facts();
    const state=stateHost({getConfiguration:async()=>clone(server),saveConfiguration:async(_etag,workspace)=>{
        server={...server,etag:'newer',workspace:clone(workspace)}; server.workspace.instances[0].name='another writer';
        return {result:'saved',etag:'saved-before-concurrent',revisionId:null,cleanupPending:[]};
    }});
    await state.reload(); state.draft.value.instances[0].name='local submission';
    assert.equal(await state.save(),false); assert.equal(state.saveOutcome.value,'saved'); assert.equal(state.uncertainSave.value.reason,'known_readback');
    assert.equal(state.draft.value.instances[0].name,'local submission'); assert.equal(state.configuration.value.etag,'etag-before');
    await state.reviewUncertainSave(); assert.equal(state.saveReview.value.configuration.etag,'newer'); assert.equal(state.saveReview.value.matchesSubmitted,false);
});

test('known saved removal with pending cleanup is not presented as a failed save or released by readback', async () => {
    let server=facts(), saves=0;
    const state=stateHost({getConfiguration:async()=>clone(server),saveConfiguration:async(_etag,workspace)=>{saves++;server={...server,etag:'saved',workspace:clone(workspace)};return {result:'saved',etag:'saved',revisionId:null,cleanupPending:['i']};}});
    await state.reload(); state.draft.value.instances=[];
    assert.equal(await state.save(),false); assert.equal(state.saveOutcome.value,'saved'); assert.equal(state.uncertainSave.value.reason,'known_cleanup');
    assert.equal(state.error.value,'saved_cleanup_pending'); assert.equal(state.unknown.value,false);
    assert.equal(await state.reviewUncertainSave(),true); assert.equal(await state.acceptReviewedSave(),false); assert.equal(await state.save(),false); assert.equal(saves,1);
});

test('related preview release unknowns remain separate and an unsent close-gated release is not called', async () => {
    let releases=[], resolveSave, rejectFirst;
    const state=stateHost({getConfiguration:async()=>facts(),saveConfiguration:()=>new Promise(resolve=>{resolveSave=resolve;}),cancelPreview:p=>{releases.push(p.token); if(p.token==='first')return new Promise((_resolve,reject)=>{rejectFirst=reject;}); throw new StateFailure('ipc_transport_unknown',null,true);}});
    await state.reload(); const first=state.releasePreview({kind:'apply',token:'first'}); const save=state.save();
    rejectFirst(new StateFailure('ipc_transport_unknown',null,true)); await first;
    resolveSave({result:'saved',etag:'etag-before',revisionId:null,cleanupPending:[]});
    assert.equal(await save,false); assert.equal(state.saveOutcome.value,'saved'); assert.equal(state.previewUnknowns.value.length,1); assert.equal(state.unknown.value,true);
    await state.releasePreview({kind:'publish_revision',token:'second'}); assert.equal(state.previewUnknowns.value.length,2);
    state.beginClose(); await state.releasePreview({kind:'apply',token:'deferred'});
    assert.deepEqual(releases,['first','second']); assert.equal(state.previewReleases.value[0].state,'deferred'); assert.equal(state.dirty.value,true);
    state.cancelClose(); await Promise.resolve(); await Promise.resolve();
    assert.deepEqual(releases,['first','second','deferred']); assert.equal(state.previewUnknowns.value.length,3);
    assert.equal(await state.save(),false);
});

test('a known rejected save and an overlapping preview unknown remain distinct', async () => {
    let rejectSave, rejectRelease;
    const state=stateHost({getConfiguration:async()=>facts(),saveConfiguration:()=>new Promise((_resolve,reject)=>{rejectSave=reject;}),cancelPreview:()=>new Promise((_resolve,reject)=>{rejectRelease=reject;})});
    await state.reload(); const release=state.releasePreview({kind:'apply',token:'one'}); const save=state.save();
    rejectRelease(new StateFailure('ipc_transport_unknown',null,true)); await release;
    rejectSave(new StateFailure('point_selection')); assert.equal(await save,false);
    assert.equal(state.saveFailure.value,'point_selection'); assert.equal(state.saveOutcome.value,null); assert.equal(state.previewUnknowns.value.length,1); assert.equal(state.unknown.value,true);
});

test('standalone controls keep their pre-r2 behavior without the save recovery UI', async () => {
    const state=stateHost({getConfiguration:async()=>facts(),controlInstance:async()=>{throw new StateFailure('runtime_task_receipt_unknown',null,true);}});
    await state.reload(); await state.control({instanceId:'i',loadedRevision:'r',epoch:'1'},'stop');
    assert.equal(state.unknown.value,true); assert.equal(state.error.value,'runtime_task_receipt_unknown'); assert.equal(state.uncertainControls.value.length,0);
});

function appHost(state, emit) {
    const appSource=fs.readFileSync(new URL('../src/App.vue',import.meta.url),'utf8');
    const script=compileScript(parse(appSource,{filename:'App.vue'}).descriptor,{id:'ds4-r2-app'}).content;
    const code=ts.transpileModule(script,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022,esModuleInterop:true}}).outputText;
    const empty=Vue.defineComponent({render:()=>Vue.createCommentVNode('stub')});
    const modules={vue:Vue,'vue-i18n':{useI18n:()=>({t:value=>value,te:()=>true})},
        '@tauri-apps/api/event':{listen:async()=>()=>{},emit},
        './console/composables/useAgentConsoleShell':{useAgentConsoleShell:()=>({activeSection:Vue.ref('overview'),appLocale:Vue.ref('en-US'),elementLocale:Vue.ref(null),localeSwitchLabel:Vue.ref(''),toggleLocale(){},agentTheme:Vue.ref('light'),isDarkTheme:Vue.ref(false),themeSwitchLabel:Vue.ref(''),toggleTheme(){}})},
        './console/composables/useDeviceSimulator':{useDeviceSimulator:()=>state,simulatorKey:key},'./console/ipcStatus':{ipcStatusKey:()=>''},
        './console/sections':{consoleSections:[{id:'overview',component:empty}]},'./layouts/AgentLayout.vue':{default:empty,__esModule:true},'./components/console/ConsoleActionButton.vue':{default:empty,__esModule:true}};
    const context={exports:{},require:name=>{if(!(name in modules))throw Error(name);return modules[name];},document:{hidden:false,addEventListener(){},removeEventListener(){}},setInterval:()=>1,clearInterval(){}};
    vm.runInNewContext(code,context,{filename:'App.js'});
    context.exports.default.render=()=>Vue.createCommentVNode('host');
    const make=type=>({type,children:[],parent:null,text:''});
    const renderer=Vue.createRenderer({createElement:make,createText:text=>({...make('#text'),text}),createComment:text=>({...make('#comment'),text}),setText:(n,v)=>{n.text=v;},setElementText:(n,v)=>{n.text=v;},parentNode:n=>n.parent,nextSibling:()=>null,insert:(n,p)=>{n.parent=p;p.children.push(n);},remove:n=>{if(n.parent)n.parent.children.splice(n.parent.children.indexOf(n),1);},patchProp(){}});
    const app=renderer.createApp(context.exports.default), mounted=app.mount(make('root'));
    return {view:mounted.$.setupState,unmount:()=>app.unmount()};
}

test('App close keeps a known save and concurrent unknown release visible until explicit discard', async () => {
    let server=facts(), finishSave, rejectRelease, emissions=0;
    const state=stateHost({getConfiguration:async()=>clone(server),saveConfiguration:(_etag,workspace)=>new Promise(resolve=>{finishSave=()=>{server={...server,etag:'saved',workspace:clone(workspace)};resolve({result:'saved',etag:'saved',revisionId:null,cleanupPending:[]});};}),cancelPreview:()=>new Promise((_resolve,reject)=>{rejectRelease=reject;})});
    await state.reload(); state.draft.value.instances[0].name='edited';
    const app=appHost(state,async()=>{emissions++;}); await Vue.nextTick();
    const releasing=state.releasePreview({kind:'apply',token:'one'});
    await app.view.requestClose(); assert.equal(app.view.closeOpen,true); assert.equal(state.closeGate.value,true);
    const saving=app.view.saveClose(); rejectRelease(new StateFailure('ipc_transport_unknown',null,true)); await releasing; finishSave(); await saving;
    assert.equal(emissions,0); assert.equal(state.saveOutcome.value,'saved'); assert.equal(state.previewUnknowns.value.length,1); assert.equal(state.unknown.value,true);
    app.view.cancelWindowClose(); assert.equal(state.closeGate.value,false); assert.equal(state.previewUnknowns.value.length,1);
    await app.view.requestClose(); await app.view.discardClose(); assert.equal(emissions,1); app.unmount();
});

test('App close gate defers new releases through emit and requires renewed consent when facts change', async () => {
    let rejectEmit, emitted=0, released=[];
    const state=stateHost({getConfiguration:async()=>facts(),cancelPreview:async p=>{released.push(p.token);return {result:'cancelled'};}});
    await state.reload();
    const app=appHost(state,()=>{emitted++;return new Promise((_resolve,reject)=>{rejectEmit=reject;});}); await Vue.nextTick();
    const closing=app.view.requestClose(); assert.equal(emitted,1); assert.equal(state.closeGate.value,true);
    await state.releasePreview({kind:'apply',token:'deferred'}); assert.deepEqual(released,[]); assert.equal(state.previewReleases.value[0].state,'deferred');
    rejectEmit(Error('synthetic emit failure')); await closing; await Promise.resolve(); await Promise.resolve();
    assert.equal(state.closeGate.value,false); assert.deepEqual(released,['deferred']); assert.equal(app.view.closeOpen,true); app.unmount();

    let discards=0;
    const second=stateHost({getConfiguration:async()=>facts(),cancelPreview:async()=>({result:'cancelled'})}); await second.reload(); second.draft.value.instances[0].name='edited';
    const dialog=appHost(second,async()=>{discards++;}); await Vue.nextTick(); await dialog.view.requestClose();
    await second.releasePreview({kind:'apply',token:'not-sent'}); await dialog.view.discardClose();
    assert.equal(discards,0); assert.equal(dialog.view.closeChanged,true); assert.equal(second.previewReleases.value[0].state,'deferred');
    await dialog.view.discardClose(); assert.equal(discards,1); dialog.unmount();
});

test('fault-injected Rust receipt and persisted draft drive the real Vue state recovery', {skip:!process.env.DS4_FAULT_LOG}, async () => {
    const line=fs.readFileSync(process.env.DS4_FAULT_LOG,'utf8').split('\n').find(value=>value.startsWith('DS4_F1_FAULT_EVIDENCE:'));
    assert.ok(line,'missing explicit Rust fault evidence');
    const evidence=JSON.parse(line.slice('DS4_F1_FAULT_EVIDENCE:'.length));
    assert.equal(evidence.response.result,'unknown'); assert.equal(evidence.response.errorCode,'save_receipt_unknown');
    let current=clone(evidence.before), saves=0, controls=[];
    const facadeSource=fs.readFileSync(new URL('../src/services/deviceSimulator.ts',import.meta.url),'utf8');
    const facadeCode=ts.transpileModule(facadeSource,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
    const core={isTauri:()=>true,invoke:async(command,args)=>{
        if(command==='ds_get_configuration') return {result:'ok',data:clone(current)};
        if(command==='ds_save_configuration') {saves++;assert.deepEqual(JSON.parse(JSON.stringify(args.request.payload.workspace)),evidence.saved.workspace);current=clone(evidence.saved);return clone(evidence.response);}
        if(command==='ds_get_bootstrap') return {result:'ok',data:{version:'test'}};
        if(command==='ds_get_runtime_snapshot') return {result:'ok',data:{instances:[{instanceId:'i',name:'synthetic',state:'stopped',epoch:'2',loadedRevision:'r1'}],stale:false}};
        if(command==='ds_control_instance') { const commandName=args.request.payload.command; controls.push(commandName); return {result:'error',data:null,errorCode:commandName==='stop'?'runtime_task_receipt_unknown':'control_rejected',receiptState:commandName==='stop'?'unknown':'known',currentEtag:null}; }
        throw Error(command);
    }};
    const facade={exports:{},require:name=>{assert.equal(name,'@tauri-apps/api/core');return core;},crypto:globalThis.crypto};
    vm.runInNewContext(facadeCode,facade,{filename:'deviceSimulator.js'});
    const state=stateHost(facade.exports);
    await state.reload(); state.draft.value=clone(evidence.saved.workspace);
    assert.equal(await state.save(),false); assert.equal(saves,1); assert.equal(state.error.value,'save_receipt_unknown');
    const local=JSON.stringify(state.draft.value), row={instanceId:'i',loadedRevision:'r1',epoch:'1'};
    await state.control(row,'stop'); await state.control(row,'pause');
    await state.reviewUncertainSave(); assert.equal(state.saveReview.value.matchesSubmitted,true);
    assert.equal(await state.acceptReviewedSave(),true); assert.equal(state.configuration.value.etag,evidence.saved.etag); assert.equal(saves,1);
    assert.deepEqual(controls,['stop','pause']); assert.equal(state.unknown.value,true); assert.equal(state.error.value,'runtime_controls_unknown');
    assert.equal(state.uncertainControls.value.length,1); assert.equal(state.uncertainControls.value[0].command,'stop'); assert.equal(JSON.stringify(state.draft.value),local);
    assert.equal(await state.save(),false); assert.equal(saves,1); await state.refresh(); assert.equal(state.unknown.value,true);
    assert.equal(await state.reviewUncertainControls(),true); assert.equal(await state.acceptReviewedControls(),true); assert.equal(state.unknown.value,false);
});

test('legacy display name preserves 256 UTF-8 bytes and blocks the next byte', async () => {
    const view = host({name:'Manual', manual:true, dataType:'INT', byte:0, bit:null, manualReason:'fixture', displayName:'x'.repeat(256)});
    await view.open(); await view.click('point-confirm');
    assert.equal(view.emitted.length,1); assert.equal(view.emitted[0].displayName,'x'.repeat(256));
    await view.open(); await view.set('point-legacy-display-name','x'.repeat(257)); await view.click('point-confirm');
    assert.equal(view.emitted.length,1); view.close();
});

test('catalog import unknown receipt freezes retries and reconciles the exact candidate', async () => {
    let server=facts(), calls=0;
    const state=stateHost({getConfiguration:async()=>clone(server),confirmCatalogImport:async(_file,preview)=>{calls++;server={...server,etag:'catalog-saved',workspace:clone(preview.workspace)};throw new StateFailure('save_receipt_unknown',null,true);}});
    await state.reload(); const workspace=JSON.parse(JSON.stringify(state.draft.value));workspace.instances.push({id:'catalog',name:'Catalog',dbs:[]});
    const preview={workspace,expectedEtag:'etag-before',token:'ticket',candidateSha256:'sha'};
    assert.equal(await state.commitCatalogImport('file',preview),false);assert.equal(state.uncertainSave.value.reason,'save_receipt_unknown');assert.equal(state.draft.value.instances[1].id,'catalog');assert.equal(state.unknown.value,true);
    assert.equal(await state.commitCatalogImport('file',preview),false);assert.equal(calls,1);assert.equal(await state.reviewUncertainSave(),true);assert.equal(state.saveReview.value.matchesSubmitted,true);
    assert.equal(await state.acceptReviewedSave(),true);assert.equal(state.configuration.value.etag,'catalog-saved');assert.equal(state.uncertainSave.value,null);assert.equal(calls,1);
});

test('catalog import readback never replaces a concurrent local edit', async () => {
    let server=facts(), committed=false, releaseRead, started; const readStarted=new Promise(resolve=>{started=resolve;});
    const state=stateHost({getConfiguration:()=>committed?new Promise(resolve=>{releaseRead=resolve;started();}):Promise.resolve(clone(server)),confirmCatalogImport:async(_file,preview)=>{server={...server,etag:'catalog-saved',workspace:clone(preview.workspace)};committed=true;return {result:'saved',etag:'catalog-saved'};}});
    await state.reload();const workspace=JSON.parse(JSON.stringify(state.draft.value));workspace.instances.push({id:'catalog',name:'Catalog',dbs:[]});const preview={workspace,expectedEtag:'etag-before',token:'ticket',candidateSha256:'sha'};
    const saving=state.commitCatalogImport('file',preview);await readStarted;state.draft.value.instances[0].name='later local edit';releaseRead(clone(server));
    assert.equal(await saving,false);assert.equal(state.draft.value.instances[0].name,'later local edit');assert.equal(state.draft.value.instances.length,1);assert.equal(state.uncertainSave.value.reason,'known_readback');
});
