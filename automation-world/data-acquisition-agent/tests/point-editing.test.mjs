/** 点位编辑与测试反馈回归：真实 Vue 响应式 owner 配内存 IPC 替身。 */
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const ts = require('typescript'), vue = require('vue');
const clone = value => JSON.parse(JSON.stringify(value));
const source = readFileSync(new URL('../src/console/composables/useLocalAcquisitionConsole.ts', import.meta.url), 'utf8');
const compile = text => ts.transpileModule(text, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText;
const compiled = compile(source);
function loadConsoleHelper(name) {
    const text = readFileSync(new URL(`../src/console/${name}.ts`, import.meta.url), 'utf8');
    const module = { exports: {} };
    new Function('exports', compile(text))(module.exports);
    return module.exports;
}
const time = loadConsoleHelper('time');
const sampleDetails = loadConsoleHelper('sampleDetails');
class LocalCommandError extends Error {
    constructor(code, currentEtag = null) { super(code); this.currentEtag = currentEtag; }
}
function initial() {
    const points = Array.from({length:6},(_,i)=>({id:'p'+i,plcId:'A',dbId:i<2?'DB71':'DB88',name:'Point_'+i,sourcePath:'field'+i,dataType:i===0||i===2?'BOOL':'INT',comment:'',groupId:'fast',enabled:true,address:{offset:i*2,bit:i===0||i===2?0:null,confirmed:true,origin:'inferred',reason:'fixture'}}));
    points.push({...clone(points[0]),id:'other',plcId:'B',dbId:'B-DB71'});
    return {etag:'e1',issues:[],active:null,loaded:null,used:null,previous:null,phase:'loaded',draft:{schemaVersion:1,plcs:[{id:'A',name:'A'},{id:'B',name:'B'}],dbs:[{id:'DB71',plcId:'A',number:71,name:'Alpha'},{id:'DB88',plcId:'A',number:88,name:'Beta'},{id:'B-DB71',plcId:'B',number:71,name:'Other'}],groups:[{id:'fast',plcId:'A',name:'Fast_500',intervalMs:500,enabled:true},{id:'slow',plcId:'A',name:'Slow_1000',intervalMs:1000,enabled:true}],points,sources:[],storage:{}}};
}
async function fixture(t) {
    const server={view:initial(),calls:[],previews:[],failSave:null,operations:[],diagnose:null,testConnection:null,readFacts:null};
    const service={bootstrap:{localStorage:true,origin:'fixture'},LocalCommandError,
        async localCall(command,request) {
            server.calls.push({command,request:clone(request??null)});
            if(command==='daa_get_configuration') return clone(server.view);
            if(command==='daa_get_local_snapshot') return { operations: clone(server.operations) };
            if(command==='daa_diagnose_point' && server.diagnose) return server.diagnose();
            if(command==='daa_test_connection' && server.testConnection) return server.testConnection();
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
        if(id.endsWith('/services/factsDelivery')) return {
            testFactsEndpoint(plcId, query) {
                server.calls.push({ command: 'daa_test_facts_endpoint', request: { plcId, ...clone(query) } });
                assert.ok(server.readFacts, 'expected a mocked GET response');
                return server.readFacts();
            },
        };
        if(id==='../time') return time;
        throw Error('unexpected test import: '+id);
    };
    new Function('require','module','exports',compiled)(imports,module,module.exports);
    const scope=vue.effectScope();
    const local=scope.run(()=>module.exports.useLocalAcquisitionConsole());
    t.after(()=>{local.finishPointEdit();scope.stop();});
    await local.reload();await vue.nextTick();
    return {local,server,ownerModule:module.exports};
}
function mountLocalScript(t, fixture, path = 'app/plc/views/points/index.vue') {
    // 挂载真实SFC的setup/watch/lifecycle；使用无DOM宿主，不启动浏览器或原生应用。
    const sfc=require('vue/compiler-sfc');
    const text=readFileSync(new URL('../src/' + path,import.meta.url),'utf8');
    const {descriptor}=sfc.parse(text);
    const script=sfc.compileScript(descriptor,{id:path}).content;
    const code=compile(script);
    const module={exports:{}};
    new Function('require','module','exports',code)(id=>{
        if(id==='vue') return vue;
        if(id==='vue-i18n') return {useI18n:()=>({t:key=>key,te:()=>false})};
        if(id.endsWith('/composables/useLocalAcquisitionConsole')) return fixture.ownerModule;
        if(id.endsWith('/console/sampleDetails')) return sampleDetails;
        if(id.endsWith('/console/time')) return time;
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
    app.provide(fixture.ownerModule.localConsoleKey,fixture.local);app.mount(node('root'));
    let mounted = true;
    function unmount() {
        if (mounted) app.unmount();
        mounted = false;
    }
    t.after(unmount);
    return { ...state, unmount };
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
    const f=await fixture(t),script=mountLocalScript(t,f);
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
    const f=await fixture(t),script=mountLocalScript(t,f);
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

async function diagnosisFixture(t) {
    const f = await fixture(t);
    f.server.view.active = 'active-1';
    await f.local.reload();
    return { ...f, script: mountLocalScript(t, f), point: f.local.draft.points[0] };
}
function pendingDiagnosis(operationId) {
    return { operationId, plcId: 'A', action: 'diagnose', phase: 'pending', reason: null, result: null };
}
function diagnosisReply(operation) {
    return { schemaVersion: 1, items: [operation] };
}
function completedDiagnosis(operation, point, value, quality = 'good', reason = null) {
    return {
        ...operation,
        phase: 'applied',
        result: {
            diagnosticId: operation.operationId,
            revision: 'active-1',
            points: { 71: { [point.id]: {
                definition: { ...point, address: { ...point.address, offset: 12 } },
                value, quality, reason, observedAt: '2026-11-10T03:26:36.345Z'
            } } }
        }
    };
}

test('point diagnosis follows this click and renders false and zero from the active definition', async t => {
    const { local, server, script, point } = await diagnosisFixture(t);
    const op = pendingDiagnosis('op-a');
    server.diagnose = () => diagnosisReply(op);
    local.notice = 'pending';
    const started = script.startPointDiagnosis(point);
    assert.equal(script.pointDiagnosis.value.status, 'waiting');
    await script.startPointDiagnosis(point);
    await started;
    assert.equal(local.notice, '');
    assert.deepEqual(server.calls.filter(call => call.command === 'daa_diagnose_point'), [{
        command: 'daa_diagnose_point', request: { plcId: 'A', pointId: 'p0', expectedActiveRevision: 'active-1' }
    }]);

    const completed = completedDiagnosis(op, point, false);
    server.operations = [
        { ...completed, operationId: 'op-old' },
        { ...completed, plcId: 'B' },
        { ...completed, action: 'test' }
    ];
    await local.refresh();
    assert.equal(script.pointDiagnosis.value.status, 'waiting');
    server.operations = [completed];
    await local.refresh();
    const reading = script.pointDiagnosis.value.reading;
    assert.equal(script.pointDiagnosis.value.status, 'success');
    assert.deepEqual(reading, {
        value: 'false', address: 'DB71 / 12.0', dataType: 'BOOL', quality: 'good', observedAt: '2026-11-10T03:26:36.345Z'
    });
    assert.equal(time.formatBusinessTime(reading.observedAt), '2026-11-10 11:26:36');
    assert.equal(local.notice, '');

    script.closePointDiagnosis();
    const intPoint = local.draft.points[1];
    server.diagnose = () => diagnosisReply(completedDiagnosis(pendingDiagnosis('op-int'), intPoint, 0));
    await script.startPointDiagnosis(intPoint);
    assert.equal(script.pointDiagnosis.value.status, 'success');
    assert.equal(script.pointDiagnosis.value.reading.value, '0');
    assert.equal(script.pointDiagnosis.value.reading.address, 'DB71 / 12');
});

test('point diagnosis reports queue, connection, read, and missing-result failures', async t => {
    const { local, server, script, point } = await diagnosisFixture(t);
    const op = pendingDiagnosis('op-blocked');
    server.diagnose = () => diagnosisReply({ ...op, phase: 'blocked', reason: 'actor_busy_or_missing' });
    await script.startPointDiagnosis(point);
    assert.equal(script.pointDiagnosis.value.status, 'blocked');
    assert.equal(script.pointDiagnosis.value.reason, 'actor_busy_or_missing');
    script.closePointDiagnosis();

    const unconnected = pendingDiagnosis('op-unconnected');
    server.diagnose = () => diagnosisReply(unconnected);
    await script.startPointDiagnosis(point);
    server.operations = [{ ...unconnected, phase: 'failed', reason: 'connection_required' }];
    await local.refresh();
    assert.equal(script.pointDiagnosis.value.status, 'failed');
    assert.equal(script.pointDiagnosis.value.reason, 'connection_required');
    script.closePointDiagnosis();

    server.diagnose = () => diagnosisReply(completedDiagnosis(pendingDiagnosis('op-decode'), point, null, 'bad_decode', 'invalid_bool'));
    await script.startPointDiagnosis(point);
    assert.equal(script.pointDiagnosis.value.status, 'failed');
    assert.equal(script.pointDiagnosis.value.reason, 'invalid_bool');
    assert.equal(script.pointDiagnosis.value.reading.value, '—');
    script.closePointDiagnosis();

    server.diagnose = () => diagnosisReply(completedDiagnosis(pendingDiagnosis('op-other'), local.draft.points[1], 99));
    await script.startPointDiagnosis(point);
    assert.equal(script.pointDiagnosis.value.status, 'unavailable');
    assert.equal(script.pointDiagnosis.value.reading, null);
    script.closePointDiagnosis();

    server.diagnose = () => Promise.reject(new LocalCommandError('revision_conflict'));
    await script.startPointDiagnosis(point);
    assert.equal(script.pointDiagnosis.value.status, 'failed');
    assert.equal(script.pointDiagnosis.value.reason, 'revision_conflict');
});

test('point diagnosis has a deadline and drops late replies after close or unmount', async t => {
    t.mock.timers.enable({ apis: ['setTimeout'] });
    const { local, server, script, point } = await diagnosisFixture(t);
    let returnFirst;
    server.diagnose = () => new Promise(resolve => { returnFirst = resolve; });
    const first = script.startPointDiagnosis(point);
    t.mock.timers.tick(14_999);
    assert.equal(script.pointDiagnosis.value.status, 'waiting');
    t.mock.timers.tick(1);
    assert.equal(script.pointDiagnosis.value.status, 'timeout');
    assert.equal(local.busy, false);
    script.closePointDiagnosis();

    const second = pendingDiagnosis('op-current');
    server.diagnose = () => diagnosisReply(second);
    await script.startPointDiagnosis(point);
    returnFirst(diagnosisReply(completedDiagnosis(pendingDiagnosis('op-late'), point, true)));
    await first;
    assert.equal(script.pointDiagnosis.value.operationId, second.operationId);
    assert.equal(script.pointDiagnosis.value.status, 'waiting');
    t.mock.timers.tick(15_000);
    assert.equal(script.pointDiagnosis.value.status, 'timeout');
    script.closePointDiagnosis();

    let returnThird;
    server.diagnose = () => new Promise(resolve => { returnThird = resolve; });
    const third = script.startPointDiagnosis(point);
    script.unmount();
    returnThird(diagnosisReply(completedDiagnosis(pendingDiagnosis('op-after-unmount'), point, false)));
    await third;
    t.mock.timers.tick(15_000);
    assert.equal(script.pointDiagnosis.value, null);
    assert.equal(server.calls.filter(call => call.command === 'daa_diagnose_point').length, 3);
});

test('connection test tracks the selected PLC and distinguishes reuse from a temporary failure', async t => {
    const f = await fixture(t);
    const { local, server } = f;
    server.view.active = 'active-1';
    await local.reload();
    const script = mountLocalScript(t, f, 'app/plc/views/diagnostics/index.vue');
    const op = { ...pendingDiagnosis('test-current'), action: 'test' };
    const testedAt = '2026-11-10T03:26:36.345Z';
    local.notice = 'pending';
    server.testConnection = () => diagnosisReply(op);
    await script.startConnectionTest(local.plcs[0]);
    assert.equal(script.connectionStatus.value, 'waiting');
    assert.equal(local.notice, '');
    assert.deepEqual(server.calls.find(call => call.command === 'daa_test_connection').request, {
        plcId: 'A', pointId: null, expectedActiveRevision: 'active-1',
    });
    const completed = {
        ...op, phase: 'applied',
        result: { testId: op.operationId, testedAt, success: true, connected: true, restorationPhase: 'applied', reason: null },
    };
    server.operations = [{ ...completed, operationId: 'test-old' }, { ...completed, plcId: 'B' }];
    await local.refresh();
    assert.equal(script.connectionStatus.value, 'waiting');
    server.operations = [completed];
    await local.refresh();
    assert.equal(script.connectionStatus.value, 'success');
    assert.equal(script.connectionResult.value.connected, true);
    assert.equal(time.formatBusinessTime(script.connectionResult.value.testedAt), '2026-11-10 11:26:36');
    script.closeConnectionTest();

    server.testConnection = () => diagnosisReply({
        ...completed, operationId: 'test-temporary',
        result: { ...completed.result, testId: 'test-temporary', success: false, connected: false, reason: 'connection_failed' },
    });
    await script.startConnectionTest(local.plcs[0]);
    assert.equal(script.connectionStatus.value, 'failed');
    assert.equal(script.connectionResult.value.connected, false);
    assert.equal(script.connectionDescription.value, 'plc.connectionTest.connectFailed');
    assert.equal(local.notice, '');
});

test('facts read reports HTTP results and IPC failure in the open test dialog', async t => {
    const f = await fixture(t);
    const { local, server } = f;
    const script = mountLocalScript(t, f, 'components/console/FactsDeliveryDialog.vue');
    const ok = { status: 200, result: { data: [] }, responseUtf8: '{"data":[]}', hasMore: true, nextCursor: 'next-cursor' };
    local.openFactsRead();
    let resolveRead;
    server.readFacts = () => new Promise(resolve => { resolveRead = resolve; });
    const pending = local.testFacts();
    assert.equal(local.busy, true);
    assert.equal(script.readStatus.value, null);
    resolveRead(ok);
    await pending;
    assert.equal(local.busy, false);
    assert.equal(script.readStatus.value, 200);
    assert.equal(local.factsReadPage, 1);

    server.readFacts = () => Promise.reject(new Error('transport_unknown'));
    await local.testFacts(true);
    assert.equal(local.factsReadError, 'transport_unknown');
    assert.equal(local.error, '');
    assert.equal(local.factsReadPage, 1);
    assert.equal(server.calls.at(-1).request.cursor, 'next-cursor');
    assert.equal(server.calls.at(-1).request.page, 2);

    server.readFacts = () => ({ status: 403, result: { errorCode: 'plc_facts.scope_rejected' }, gap: true });
    await local.testFacts();
    assert.equal(local.factsReadError, '');
    assert.equal(script.readStatus.value, 403);
    assert.equal(script.readErrorCode.value, 'plc_facts.scope_rejected');
    local.factsReadMode = 'latest';
    await vue.nextTick();
    assert.equal(script.readStatus.value, null);

    server.readFacts = () => new Promise(resolve => { resolveRead = resolve; });
    const closing = local.testFacts();
    local.deliveryDialog = null;
    resolveRead(ok);
    await closing;
    assert.equal(local.deliveryDialog, null);
    assert.equal(local.deliveryDetail, null);
});

test('PLC test and diagnosis translations have symmetric keys and timeout placeholders', () => {
    const zh = JSON.parse(readFileSync(new URL('../src/app/plc/locales/zh-CN.json', import.meta.url), 'utf8'));
    const en = JSON.parse(readFileSync(new URL('../src/app/plc/locales/en-US.json', import.meta.url), 'utf8'));
    for (const section of ['diagnosis', 'connectionTest']) {
        assert.deepEqual(Object.keys(zh[section]), Object.keys(en[section]));
        for (const key of Object.keys(zh[section])) {
            assert.ok(zh[section][key] && en[section][key], key);
            assert.deepEqual(zh[section][key].match(/\{[^}]+\}/g), en[section][key].match(/\{[^}]+\}/g));
        }
    }
});
