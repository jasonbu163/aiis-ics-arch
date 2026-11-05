/** DIRECT样本展示增量验证：冻结样本、真实Vue/i18n及SFC状态，不访问SQLite、PLC或原生窗口。 */
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const ts = require('typescript'), vue = require('vue'), sfc = require('vue/compiler-sfc');
const { createI18n } = require('vue-i18n');
function loadTs(path) {
    const code = ts.transpileModule(readFileSync(new URL(path, import.meta.url), 'utf8'), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText;
    const module = {exports:{}};
    new Function('require', 'module', 'exports', code)(require, module, module.exports);
    return module.exports;
}
const helpers = loadTs('../src/console/sampleDetails.ts');
const time = loadTs('../src/console/time.ts');
const tableWidths = loadTs('../src/console/tableWidths.ts');
const messages = Object.fromEntries(['zh-CN', 'en-US'].map(locale => [locale, { common: JSON.parse(readFileSync(new URL(`../src/locales/${locale}/common.json`, import.meta.url), 'utf8')) }]));
const digest = text => createHash('sha256').update(text).digest('hex');
function fixture(count = 6) {
    const points = Object.fromEntries(Array.from({length:count}, (_, i) => [`point-${i}`, {
        definition:{name:`DB88_Frozen_${i}`,sourcePath:`原始路径.field${i}`,dataType:i===0?'BOOL':'INT',address:{offset:i*2,bit:i===0?0:null}},
        value:[false,0,'',null,12.5,52][i%6],
        observedAt:'2026-10-30T11:56:59.795+08:00', quality:i===3?'bad_read':'good',reason:i===3?'read_failed':null
    }]));
    const payload = JSON.stringify({schemaVersion:2,sampleId:'owned-sample',plcId:'plc-A',groupId:'slow',dbNumber:88,origin:'s7',savedAt:'2026-10-30T11:56:59.797+08:00',points});
    const manifest = '{"schemaVersion":2,"sourceSeq":"142","samples":[{"sampleId":"owned-sample"}]}';
    const context = JSON.stringify({schemaVersion:1,plcs:[{id:'plc-A',name:'Frozen PLC'}],groups:[{id:'slow',name:'Frozen Slow_1000'}],points:[]});
    return {payload,sha256:digest(payload),manifest,manifestSha256:digest(manifest),context,contextSha256:digest(context),contextBytes:Buffer.byteLength(context),contextOffset:0,contextNextOffset:null,deliveryState:'pending'};
}
function freeze(value) { Object.freeze(value); for (const child of Object.values(value)) if (child && typeof child === 'object') freeze(child); return value; }
function mountScript(t, raw, storage = new Map()) {
    const previous = globalThis.window;
    globalThis.window = {localStorage:{getItem:key=>storage.get(key)??null,setItem:(key,value)=>storage.set(key,value),removeItem:key=>storage.delete(key)}};
    const descriptor = sfc.parse(readFileSync(new URL('../src/components/console/LocalSampleDetail.vue', import.meta.url), 'utf8')).descriptor;
    const script = sfc.compileScript(descriptor, {id:'sample-details-test'}).content;
    const code = ts.transpileModule(script, {compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText;
    const module = {exports:{}};
    new Function('require','module','exports',code)(id=>{
        if(id==='vue') return vue;
        if(id==='vue-i18n') return require(id);
        if(id.endsWith('/sampleDetails')) return helpers;
        if(id.endsWith('/time')) return time;
        if(id.endsWith('/tableWidths')) return tableWidths;
        return {default:{}};
    },module,module.exports);
    const node=type=>({type,children:[],parent:null});
    const renderer=vue.createRenderer({
        createElement:node,createText:node,createComment:node,setText(){},setElementText(){},patchProp(){},
        insert(child,parent){child.parent=parent;parent.children.push(child);},
        remove(child){if(child.parent)child.parent.children=child.parent.children.filter(item=>item!==child);},
        parentNode:child=>child.parent,nextSibling:()=>null
    });
    let state;
    const component=module.exports.default;
    const app=renderer.createApp({...component,setup(props,context){state=component.setup(props,context);return()=>vue.h('div');}},{raw,sampleId:'owned-sample'});
    const i18n=createI18n({legacy:false,locale:'zh-CN',fallbackLocale:'en-US',messages});
    app.use(i18n);app.mount(node('root'));
    t.after(()=>{app.unmount();if(previous===undefined)delete globalThis.window;else globalThis.window=previous;});
    return {state,i18n,storage,app};
}

test('summary and rows use only frozen sample facts and context, preserving falsy values',()=>{
    const raw=freeze(fixture()), before=JSON.stringify(raw);
    const view=helpers.sampleDetails(raw);
    assert.equal(view.plc,'Frozen PLC');assert.equal(view.group,'Frozen Slow_1000');
    assert.equal(view.dbNumber,'88');assert.equal(view.origin,'s7');assert.equal(view.good,5);
    assert.deepEqual(view.rows.map(row=>row.value),['false','0','""','—','12.5','52']);
    assert.equal(view.rows[0].address,'0.0');assert.equal(view.rows[1].address,'2');
    assert.equal(view.rows[3].quality,'bad_read');assert.equal(view.rows[3].reason,'read_failed');
    assert.equal(view.rows[0].name,'DB88_Frozen_0');assert.equal(view.rows[0].sourcePath,'原始路径.field0');
    for(const [body,hash] of [['payload','sha256'],['manifest','manifestSha256'],['context','contextSha256']]) {
        assert.equal(digest(raw[body]),raw[hash]);helpers.formatSampleJson(raw[body]);assert.equal(digest(raw[body]),raw[hash]);
    }
    assert.equal(JSON.stringify(raw),before);
});

test('JSON formatting preserves large integers, exponent spelling, escapes and string whitespace',()=>{
    const text = JSON.stringify('中 文 { } , : "' + String.fromCharCode(92, 10, 9));
    const source = '{"n":9007199254740993,"negative":-0,"exp":1.20e+03,"text":' + text + ',"escaped":"' + String.fromCharCode(92) + 'u4e2d","items":[true,null,{},[]]}';
    assert.doesNotThrow(()=>JSON.parse(source));
    const pretty=helpers.formatSampleJson(source);
    assert.ok(pretty.includes('\n  "n": 9007199254740993,'));
    assert.ok(pretty.includes('"negative": -0'));assert.ok(pretty.includes('"exp": 1.20e+03'));
    const tokens = text => text.match(/"(?:\\.|[^"\\])*"|[^\s]/g);
    assert.deepEqual(tokens(pretty),tokens(source));
    assert.deepEqual(JSON.parse(pretty),JSON.parse(source));
    assert.equal(helpers.formatSampleJson('{invalid'),'{invalid');
});

test('missing context or metadata never invents current names, addresses or successful quality',()=>{
    const raw=fixture();raw.context='{}';
    const payload=JSON.parse(raw.payload);payload.points={unknown:{value:null}};raw.payload=JSON.stringify(payload);
    const view=helpers.sampleDetails(raw);
    assert.equal(view.plc,'plc-A');assert.equal(view.group,'slow');assert.equal(view.good,0);
    assert.equal(view.rows[0].name,'unknown');assert.equal(view.rows[0].address,'—');assert.equal(view.rows[0].quality,'');
    assert.equal(helpers.sampleDetails({...raw,payload:'{"sampleId":"owned-sample"}'}),null);
    assert.equal(helpers.sampleDetails({...raw,payload:'null'}),null);
});

test('sample timestamps display in Shanghai at seconds without changing stored precision',()=>{
    assert.equal(time.formatBusinessTime('2026-10-30T03:56:59.795Z'),'2026-10-30 11:56:59');
    assert.equal(time.formatBusinessTime('2026-10-30T11:56:59.795+08:00'),'2026-10-30 11:56:59');
    assert.equal(time.formatBusinessTime('not-a-time'),'—');
});

test('real SFC separates upload pending from read quality and switches Chinese/English',async t=>{
    const {state,i18n}=mountScript(t,freeze(fixture()));
    assert.equal(state.deliveryLabel.value,'待上报');
    assert.equal(state.label('pending'),'处理中'); // Operation phases retain their own meaning.
    assert.equal(state.label('good'),'良好');
    assert.equal(state.t('common.local.sampleView.qualityCount',{good:5,total:6}),'良好 5 / 6 点');
    i18n.global.locale.value='en-US';await vue.nextTick();
    assert.equal(state.deliveryLabel.value,'Awaiting upload');assert.equal(state.label('good'),'Good');
    assert.equal(state.label('unrecognized_reason'),'unrecognized_reason');
});

test('real SFC keeps results paged, resets page on size changes and lazily opens JSON',async t=>{
    const {state}=mountScript(t,freeze(fixture(45)));
    assert.equal(state.pagedRows.value.length,20);assert.equal(state.page.value,1);
    state.page.value=3;assert.equal(state.pagedRows.value.length,5);
    state.pageSize.value=10;await vue.nextTick();
    assert.equal(state.page.value,1);assert.equal(state.pagedRows.value.length,10);
    assert.deepEqual({...state.jsonOpen},{payload:false,manifest:false,context:false});
    state.toggleJson('payload',{target:{open:true}});
    assert.equal(state.jsonOpen.payload,true);assert.equal(state.jsonOpen.context,false);
});

test('column preferences are isolated, survive reopening, and restore defaults without sample writes',t=>{
    const raw=freeze(fixture()), before=JSON.stringify(raw), storage=new Map();
    storage.set(tableWidths.widthKey('com.aiis.aw.dataacquisitionagent','storage.history'),'{"savedAt":350}');
    const first=mountScript(t,raw,storage).state;
    first.resizeColumn(320,240,{columnKey:'name'});first.resizeColumn(10,120,{columnKey:'value'});
    const second=mountScript(t,raw,storage).state;
    assert.equal(second.widths.value.name,320);assert.equal(second.widths.value.value,100);
    second.resetColumns();assert.equal(second.widths.value.name,240);
    assert.equal(storage.get(tableWidths.widthKey('com.aiis.aw.dataacquisitionagent','storage.history')),'{"savedAt":350}');
    assert.equal(JSON.stringify(raw),before);
});

test('new sample translations have matching keys/placeholders and template literal keys resolve',()=>{
    const zh=messages['zh-CN'].common.local.sampleView,en=messages['en-US'].common.local.sampleView;
    assert.deepEqual(Object.keys(zh).sort(),Object.keys(en).sort());
    for(const key of Object.keys(zh)) assert.deepEqual(zh[key].match(/\{\w+\}/g)??[],en[key].match(/\{\w+\}/g)??[],key);
    const component=readFileSync(new URL('../src/components/console/LocalSampleDetail.vue',import.meta.url),'utf8');
    for(const match of component.matchAll(/['"](common\.local\.[A-Za-z.]+)['"]/g)) {
        for(const locale of Object.keys(messages)) assert.ok(match[1].split('.').reduce((value,key)=>value?.[key],messages[locale]),match[1]);
    }
    assert.ok(component.includes('v-if="jsonOpen[entry.id]"'));
    assert.ok(!component.includes('v-html'));
});
