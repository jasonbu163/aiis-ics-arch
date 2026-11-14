/** 具名投递IPC、字符串序号、无桥与UI触达面的必要合同断言；无网络/GUI。 */
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { readFileSync } from 'node:fs'
import { createRequire } from 'node:module'
const require = createRequire(import.meta.url), ts = require('typescript')
const text = path => readFileSync(new URL(path, import.meta.url), 'utf8')
const calls = [], module = { exports: {} }
const source = ts.transpileModule(text('../src/services/factsDelivery.ts'), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText
new Function('module', 'exports', 'require', source)(module, module.exports, () => ({ localCall: (command, request = {}) => { calls.push({ command, request }); return Promise.resolve({}) } }))
const api = module.exports
test('named IPC surfaces carry the settings revision and exact locally confirmed bindings', async () => {
  const settings = { schemaVersion: 1, settingsRevision: 'revision', origin: 'http://127.0.0.1:8001', path: '/compatible/samples', intervalSeconds: 5, identityMode:'per_plc', bindings:[{localPlcId:'local',instanceId:'instance',plcId:'plc',sourceGeneration:'generation'}] }
  const sources = [{ instanceId:'instance', plcId: 'plc', dbNumber: 21, sourceGeneration: 'generation' }]
  await api.getDeliverySettings(); await api.saveDeliverySettings(settings, 'revision'); await api.getDeliverySnapshot(); await api.setDelivery('start', 'revision', sources); await api.listDeliveries(null); await api.getDelivery('batch'); await api.previewDelivery('cycle'); await api.testFactsEndpoint('plc'); await api.getFactsSourceMaterial()
  assert.deepEqual(calls.map(c => c.command), ['daa_get_delivery_settings','daa_save_delivery_settings','daa_get_delivery_snapshot','daa_set_delivery','daa_list_deliveries','daa_get_delivery','daa_preview_delivery','daa_test_facts_endpoint','daa_get_facts_source_material'])
  assert.deepEqual(calls[3].request, { action: 'start', settingsRevision: 'revision', sources }); assert.equal(calls[4].request.limit, 20)
  await api.rebindDelivery('sample', 'http://127.0.0.1:8000/old', 'revision', sources)
  assert.deepEqual(calls.at(-1).request, { action: 'rebind', sampleId: 'sample', oldUrl: 'http://127.0.0.1:8000/old', settingsRevision: 'revision', sources })
  await api.listDeliveries(null, 20, 'batches', 'unknown')
  assert.equal(calls.at(-1).request.state, 'unknown')
  assert.doesNotMatch(source, /fetch\(|XMLHttpRequest|localStorage/)
})

test('structured delivery confirmations preserve each source, cancellation and IPC', async t => {
  const vue = require('vue'), { createI18n } = require('vue-i18n'), { renderToString } = require('vue/server-renderer')
  const messages = Object.fromEntries(['zh-CN', 'en-US'].map(locale => [locale, { common: JSON.parse(text(`../src/locales/${locale}/common.json`)) }]))
  const i18n = createI18n({ legacy: false, locale: 'zh-CN', messages })
  const settings = { identityMode: 'per_plc', settingsRevision: 'revision-2', origin: 'http://127.0.0.1:8001', path: '/samples' }
  const sources = [
    { instanceId: 'inst/' + 'I'.repeat(123), plcId: 'plc/' + 'P'.repeat(124), dbNumber: 21, sourceGeneration: 'gen/' + 'G'.repeat(124) },
    { instanceId: 'instance/b', plcId: 'plc/b', dbNumber: 22, sourceGeneration: 'gen/current' },
    { instanceId: 'old/instance', plcId: 'plc/b', dbNumber: 23, sourceGeneration: 'gen/old;one' },
  ]
  for (const value of [sources[0].instanceId, sources[0].plcId, sources[0].sourceGeneration]) assert.equal(Buffer.byteLength(value), 128)
  const material = { contractVersion: 'plc-facts/v2', sources }
  const ipcCalls = [], prompts = [], apiModule = { exports: {} }
  let accept = true, rejectWrite = false
  new Function('module', 'exports', 'require', source)(apiModule, apiModule.exports, () => ({
    localCall: async (command, request = {}) => {
      ipcCalls.push({ command, request })
      if (command === 'daa_get_delivery_settings') return settings
      if (command === 'daa_get_facts_source_material') return material
      if (command === 'daa_set_delivery' && rejectWrite) throw new Error('source_confirmation_changed')
      return {}
    },
  }))
  const compiled = ts.transpileModule(text('../src/console/composables/useLocalAcquisitionConsole.ts'), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText
  const consoleModule = { exports: {} }
  new Function('require', 'module', 'exports', compiled)(id => {
    if (id === 'vue') return { ...vue, onMounted() {}, onUnmounted() {} }
    if (id === 'vue-i18n') return { useI18n: () => ({ t: i18n.global.t, te: i18n.global.te }) }
    if (id === 'element-plus') return { ElMessageBox: { confirm: async (message, title, options) => { prompts.push({ message, title, options }); if (!accept) throw new Error('cancel') } } }
    if (id.endsWith('/localAcquisition')) return { bootstrap: { localStorage: true, origin: 'fixture' }, LocalCommandError: class extends Error {} }
    if (id.endsWith('/factsDelivery')) return apiModule.exports
    if (id.endsWith('/time')) return {}
    throw new Error(`Unexpected import: ${id}`)
  }, consoleModule, consoleModule.exports)
  const previousDocument = globalThis.document
  globalThis.document = { querySelector: () => null }
  const scope = vue.effectScope(), local = scope.run(() => consoleModule.exports.useLocalAcquisitionConsole())
  // 手动启动前已有成功读取的上报快照，与实际页面的启用条件一致。
  local.delivery = { running: false, state: 'stopped' }
  t.after(() => { scope.stop(); if (previousDocument === undefined) delete globalThis.document; else globalThis.document = previousDocument })
  const walk = node => !node || typeof node !== 'object' ? [] : [node, ...(Array.isArray(node.children) ? node.children.flatMap(walk) : [])]
  const byClass = (node, cls) => walk(node).filter(item => String(item.props?.class ?? '').split(/\s+/).includes(cls))
  const valueNodes = node => walk(node).filter(item => item.type === 'dd').map(item => item.children)
  const oldUrl = 'http://127.0.0.1:8000/old', newUrl = settings.origin + settings.path
  async function invoke(action) {
    if (action === 'rebind') { local.deliveryDetail = { batchId: 'old/sample;1', origin: oldUrl, state: 'unknown' }; await local.rebindDelivery() }
    else await local.deliveryControl(action)
  }
  for (const locale of ['zh-CN', 'en-US']) {
    i18n.global.locale.value = locale
    for (const action of ['start', 'resume', 'rebind']) {
      accept = true; rejectWrite = false; ipcCalls.length = 0
      await invoke(action)
      assert.equal(local.error, '')
      const call = ipcCalls.find(entry => entry.command === 'daa_set_delivery')
      assert.deepEqual(call?.request, action === 'rebind'
        ? { action, sampleId: 'old/sample;1', oldUrl, settingsRevision: 'revision-2', sources }
        : { action, settingsRevision: 'revision-2', sources })
      const prompt = prompts.at(-1)
      assert.ok(vue.isVNode(prompt.message), `${locale} ${action} must render structured content`)
      assert.equal(prompt.options.customClass, 'daa-reporting-confirm')
      assert.equal(prompt.title, i18n.global.t(`common.delivery.confirm${action === 'rebind' ? 'Rebind' : action === 'resume' ? 'Resume' : 'Start'}Title`))
      assert.equal(prompt.options.confirmButtonText, i18n.global.t(`common.delivery.${action === 'rebind' ? 'confirmRebindAction' : action}`))
      const targets = byClass(prompt.message, 'daa-confirm-targets')
      assert.equal(targets.length, 1)
      assert.deepEqual(valueNodes(targets[0]), action === 'rebind' ? [oldUrl, newUrl, 'plc-facts/v2'] : [newUrl, 'plc-facts/v2'])
      const rows = byClass(prompt.message, 'daa-confirm-source')
      assert.equal(rows.length, sources.length)
      for (const [index, row] of rows.entries()) {
        const item = sources[index]
        assert.deepEqual(valueNodes(row), [item.instanceId, item.plcId, `DB${item.dbNumber}`, item.sourceGeneration])
      }
      const html = await renderToString(vue.createSSRApp({ render: () => prompt.message }))
      for (const key of ['sourceInstance', 'sourcePlc', 'db', 'sourceGeneration', 'confirmRegistration']) assert.ok(html.includes(i18n.global.t('common.delivery.' + key)), `${locale} ${action} ${key}`)
      assert.ok(html.includes(i18n.global.t('common.delivery.' + (action === 'rebind' ? 'confirmRetryNote' : 'confirmQueueNote'))))
      if (action === 'rebind') assert.ok(html.includes(i18n.global.t('common.delivery.confirmSameTarget')))
      assert.ok(html.includes('tabindex="0"'))
      accept = false; ipcCalls.length = 0
      await invoke(action)
      assert.ok(!ipcCalls.some(entry => entry.command === 'daa_set_delivery'), `${locale} ${action} cancellation must not write`)
    }
  }
  accept = true; rejectWrite = true; ipcCalls.length = 0
  await invoke('start')
  assert.equal(local.error, 'source_confirmation_changed')
  assert.deepEqual(ipcCalls.find(entry => entry.command === 'daa_set_delivery').request.sources, sources)
  rejectWrite = false
  await local.deliveryControl('pause') // 成功返回新快照后才能再次请求启动。
  delete settings.identityMode; ipcCalls.length = 0
  await local.deliveryControl('start')
  assert.equal(local.error, 'delivery_profile_upgrade_required')
  assert.deepEqual(ipcCalls.map(call => call.command), ['daa_get_delivery_settings', 'daa_get_facts_source_material'])
})
test('real two-page controls, editable material, stable column preferences and paired locale keys', () => {
  for (const page of ['../src/app/collection/views/storage/index.vue','../src/app/runtime/views/overview/index.vue']) assert.match(text(page), /FactsDeliveryPanel/)
  const panel = text('../src/components/console/FactsDeliveryPanel.vue'), dialog = text('../src/components/console/FactsDeliveryDialog.vue')
  assert.match(panel, /local\.bootstrap\.uploadAvailable/); assert.match(panel, /header-dragend/); assert.match(panel, /widthKey\('com\.aiis\.aw\.dataacquisitionagent', 'storage\.delivery-queue'\)/); assert.match(panel, /\[10,20,50\]/)
  assert.doesNotMatch(dialog, /contenteditable|v-html|JSON\.parse\(.*origin|sequenceFrom|sequenceThrough|adoptionReference/); assert.match(dialog, /common\.delivery\.sourceEditNote/); assert.match(dialog, /applyParameters/)
  assert.match(panel, /common\.delivery\.unknownSamples/); assert.match(panel, /common\.delivery\.historicalV1/); assert.match(panel, /aria-describedby/); assert.match(panel, /@focus/); assert.match(panel, /@click/)
  assert.match(dialog, /draft\.path/); assert.match(dialog, /previewUrl/); assert.match(dialog, /rebindDelivery/); assert.match(panel, /deliveryState/)
  assert.doesNotMatch(panel, /local\.previewFacts|local\.openFactsRead/)
  assert.match(text('../src/console/composables/useLocalAcquisitionConsole.ts'), /confirmRegistration/)
  const zh = JSON.parse(text('../src/locales/zh-CN/common.json')).delivery, en = JSON.parse(text('../src/locales/en-US/common.json')).delivery
  function keys(o, p = '') { return Object.entries(o).flatMap(([k,v]) => typeof v === 'object' ? keys(v,p+k+'.') : [p+k]).sort() }
  assert.deepEqual(keys(zh),keys(en)); assert.match(zh.readOnly,/ACK/); assert.match(en.states.unknown,/reconciliation/)
  for (const key of ['confirmRegistration', 'confirmSameTarget']) {
    const placeholders = value => [...value.matchAll(/\{(\w+)\}/g)].map(match => match[1]).sort()
    assert.deepEqual(placeholders(zh[key]), placeholders(en[key]), key)
  }
  for (const lang of ['zh-CN','en-US']) { const codes=JSON.parse(text(`../src/locales/${lang}/common.json`)).local.codes; for (const key of ['source_confirmation_changed','source_confirmation_required','source_changed','delivery_settings_conflict']) assert.ok(codes[key], `${lang}: ${key}`) }
  assert.match(zh.localPlc, /本机/); assert.match(en.localPlc, /local/i)
  assert.match(zh.sourceEditNote, /逐台.*参与上报/); assert.match(zh.sourceEditNote, /重新开启后.*补传/)
  assert.match(en.sourceEditNote, /each PLC reports/i); assert.match(en.sourceEditNote, /after re-enabling/i)
  assert.match(zh.sourceEditNote, /此前样本保留原身份/)
  assert.match(en.sourceEditNote, /samples keep their original identities/i)
  for (const key of ['reportingEnabled','reportingOn','reportingOff']) { assert.ok(zh[key]); assert.ok(en[key]) }
})

test('per-PLC settings isolate paste, validation, cancel and retained inactive rows', async t => {
  const vue = require('vue'), sfc = require('vue/compiler-sfc'), { createI18n } = require('vue-i18n')
  const descriptor = sfc.parse(text('../src/components/console/FactsDeliveryDialog.vue')).descriptor
  const compiled = ts.transpileModule(sfc.compileScript(descriptor, { id: 'source-settings-test' }).content, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText
  const injectionKey = Symbol('owner'), saved = []
  const owner = vue.reactive({ deliveryDialog:'settings',busy:false,deliverySettings:{schemaVersion:1,settingsRevision:'r',origin:null,path:'/samples',intervalSeconds:5,identityMode:'per_plc',bindings:[{localPlcId:'inactive',instanceId:'old',plcId:'old-plc',sourceGeneration:'old-gen'}]},sourceMaterial:{localSources:[{localPlcId:'local-a',name:'PLC A',dbNumbers:[21]},{localPlcId:'local-b',name:'PLC B',dbNumbers:[22]}]},saveDelivery:value=>saved.push(value) })
  const mod = { exports:{} }
  new Function('require','module','exports',compiled)(id => {
    if (id === 'vue' || id === 'vue-i18n') return require(id)
    if (id.endsWith('/useLocalAcquisitionConsole')) return { localConsoleKey:injectionKey }
    if (id.endsWith('/sampleDetails')) return {formatSampleJson: value => value}
    if (id === 'element-plus') return {}
    return {default:{}}
  },mod,mod.exports)
  const node = type => ({type,children:[],parent:null})
  const renderer = vue.createRenderer({createElement:node,createText:node,createComment:node,setText(){},setElementText(){},patchProp(){},insert(child,parent){child.parent=parent;parent.children.push(child)},remove(){},parentNode:child=>child.parent,nextSibling:()=>null})
  let state; const component=mod.exports.default
  const app=renderer.createApp({...component,setup(props,context){state=component.setup(props,context);return ()=>vue.h('div')}})
  app.use(createI18n({legacy:false,locale:'zh-CN',messages:{'zh-CN':{common:JSON.parse(text('../src/locales/zh-CN/common.json'))}}}));app.provide(injectionKey,owner);app.mount(node('root'));t.after(()=>app.unmount())
  assert.deepEqual(state.localSources.value.map(x=>x.localPlcId),['local-a','local-b','inactive'])
  assert.deepEqual(state.editing.value.map(x=>x.enabled),[false,false,true])
  Object.assign(state.editing.value[0],{instanceId:'inst-a',plcId:'plc-a',sourceGeneration:'gen-a'})
  state.openPaste('local-b');state.pasted.value=JSON.stringify({instanceId:'inst-b',plcId:'plc-b',sourceGeneration:'gen-b'});state.applyParameters()
  assert.equal(state.editing.value[1].instanceId,'inst-b')
  const before=JSON.stringify(state.editing.value)
  state.openPaste('local-b');state.pasted.value='{"instanceId":';state.applyParameters();assert.equal(state.sourceError.value,'sourceInvalid');assert.equal(JSON.stringify(state.editing.value),before)
  state.pasted.value=JSON.stringify({instanceId:'inst-b2',plcId:'plc-b2',sourceGeneration:'gen-b2',dbNumbers:[999]});state.cancelPaste();assert.equal(JSON.stringify(state.editing.value),before)
  state.openPaste('local-b');state.pasted.value=JSON.stringify({instanceId:'inst-b2',plcId:'plc-b2',sourceGeneration:'gen-b2',dbNumbers:[999]});state.applyParameters()
  assert.equal(state.editing.value[0].instanceId,'inst-a');assert.equal(state.localSources.value[1].dbNumbers[0],22)
  state.editing.value[0].enabled=true
  state.save();assert.equal(saved.length,1);assert.deepEqual(saved[0].bindings.map(b=>[b.instanceId,b.plcId]),[['inst-a','plc-a'],['inst-b2','plc-b2'],['old','old-plc']]);assert.deepEqual(saved[0].disabledLocalPlcs,['local-b']);assert.ok(saved[0].bindings.every(row=>!('enabled' in row)))
  state.editing.value[1].sourceGeneration='';state.save();assert.equal(state.sourceErrorPlc.value,'local-b');assert.equal(saved.length,1)
  state.editing.value[1].sourceGeneration='gen-b';state.editing.value[1].plcId='plc-a';state.save();assert.equal(state.sourceError.value,'sourceDuplicate');assert.equal(saved.length,1)
  state.editing.value[1].plcId='plc-b'
  const legal=['\uFEFFPLC','PLC\uFEFF','PLC\u0085middle','😀'.repeat(32)]
  const illegal=['\u0085PLC','PLC\u0085','\u00a0PLC','PLC\u2003','\uD800PLC','PLC\uDC00','😀'.repeat(33),'a\u007fb']
  for (const field of ['plcId','instanceId','sourceGeneration']) {
    for (const value of legal) {
      state.openPaste('local-b');state.pasted.value=JSON.stringify({instanceId:'inst',plcId:'plc',sourceGeneration:'gen',[field]:value});state.applyParameters()
      assert.equal(state.sourceError.value,'',`${field}: ${JSON.stringify(value)}`);assert.equal(state.editing.value[1][field],value)
    }
    for (const value of illegal) {
      const previous=JSON.stringify(state.editing.value)
      state.openPaste('local-b');state.pasted.value=JSON.stringify({instanceId:'inst',plcId:'plc',sourceGeneration:'gen',[field]:value});state.applyParameters()
      assert.equal(state.sourceError.value,'sourceInvalid');assert.equal(JSON.stringify(state.editing.value),previous)
    }
  }
})

test('reporting SFC uses live counts, saved PLC names with ID fallback, and state filters', async t => {
  const vue = require('vue'), sfc = require('vue/compiler-sfc'), { createI18n } = require('vue-i18n')
  const previous = globalThis.window
  const preferences = new Map()
  globalThis.window = { localStorage: { getItem: key => preferences.get(key) ?? null, setItem: (key, value) => preferences.set(key, value), removeItem: key => preferences.delete(key) } }
  const descriptor = sfc.parse(text('../src/components/console/FactsDeliveryPanel.vue')).descriptor
  const script = sfc.compileScript(descriptor, { id: 'delivery-test' }).content
  const compiled = ts.transpileModule(script, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText
  const injectionKey = Symbol('owner'), loaded = []
  const owner = vue.reactive({
    bootstrap: { uploadAvailable: true }, busy: false, deliveryKind: 'batches', deliveryState: '',
    delivery: { running: true, state: 'running', sampleCounts: { pending: 2, unknown: 3, needsProcessing: 4, acknowledged: 5 } },
    view: { draft: { plcs: [{ id: 'registered-id', name: 'Saved PLC' }] } },
    label: value => value || '—', loadDeliveries: async () => { loaded.push([owner.deliveryKind, owner.deliveryState]) },
    rawSampleId: '', inspect: async id => { owner.rawSampleId = id; return true },
  })
  const widthsSource = ts.transpileModule(text('../src/console/tableWidths.ts'), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText
  const widthsModule = { exports: {} }; new Function('require', 'module', 'exports', widthsSource)(require, widthsModule, widthsModule.exports)
  const module = { exports: {} }
  new Function('require', 'module', 'exports', compiled)(id => {
    if (id === 'vue' || id === 'vue-i18n') return require(id)
    if (id.endsWith('/useLocalAcquisitionConsole')) return { localConsoleKey: injectionKey }
    if (id.endsWith('/tableWidths')) return widthsModule.exports
    if (id.endsWith('/time')) return { formatBusinessTime: value => value || '—' }
    if (id === 'element-plus') return {}
    return { default: {} }
  }, module, module.exports)
  const node = type => ({ type, children: [], parent: null })
  const renderer = vue.createRenderer({
    createElement: node, createText: node, createComment: node, setText() {}, setElementText() {}, patchProp() {},
    insert(child, parent) { child.parent = parent; parent.children.push(child) },
    remove(child) { if (child.parent) child.parent.children = child.parent.children.filter(item => item !== child) },
    parentNode: child => child.parent, nextSibling: () => null,
  })
  let state
  const component = module.exports.default
  const app = renderer.createApp({ ...component, setup(props, context) { state = component.setup(props, context); return () => vue.h('div') } }, { configure: true })
  const messages = Object.fromEntries(['zh-CN', 'en-US'].map(locale => [locale, { common: JSON.parse(text(`../src/locales/${locale}/common.json`)) }]))
  const i18n = createI18n({ legacy: false, locale: 'zh-CN', fallbackLocale: 'en-US', messages })
  app.use(i18n); app.provide(injectionKey, owner); app.mount(node('root'))
  t.after(() => { app.unmount(); if (previous === undefined) delete globalThis.window; else globalThis.window = previous })
  assert.deepEqual(state.stats.value.map(item => item.value), [2, 3, 4, 5])
  loaded.length = 0
  owner.delivery.sampleCounts.acknowledged = 17
  await vue.nextTick()
  assert.deepEqual(state.stats.value.map(item => item.value), [2, 3, 4, 17])
  assert.deepEqual(loaded, [['batches', '']])
  assert.equal(state.plcName('registered-id'), 'Saved PLC'); assert.equal(state.plcName('removed-id'), 'removed-id')
  loaded.length = 0; state.selectState('unknown'); await vue.nextTick()
  assert.equal(owner.deliveryState, 'unknown'); assert.deepEqual(loaded, [['batches', 'unknown']])
  await state.openSample('sample-A'); assert.equal(state.detailsVisible.value, true); assert.equal(state.detailSampleId.value, 'sample-A')
  owner.inspect = async () => { owner.rawSampleId = 'different-sample'; return true }
  await state.openSample('sample-B'); assert.equal(state.detailsVisible.value, false)
  assert.equal(state.label('running'), '上报中')
  i18n.global.locale.value = 'en-US'; await vue.nextTick(); assert.equal(state.label('running'), 'Delivering')
  for (const locale of Object.keys(messages)) {
    assert.doesNotMatch(messages[locale].common.local.uploadPending, /尚未实现|unavailable/i)
    assert.match(messages[locale].common.delivery.recordsNote, /ID/)
  }
})

test('storage summary distinguishes active policy, draft and unavailable queue snapshots', async t => {
  const vue = require('vue'), sfc = require('vue/compiler-sfc'), { createI18n } = require('vue-i18n')
  const descriptor = sfc.parse(text('../src/app/collection/views/storage/index.vue')).descriptor
  const script = sfc.compileScript(descriptor, { id: 'storage-summary-test' }).content
  const compiled = ts.transpileModule(script, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText
  const injectionKey = Symbol('owner'), owner = vue.reactive({ snapshot: null, snapshotError: '', draft: { storage: { retentionDays: 7 } } })
  const module = { exports: {} }
  new Function('require', 'module', 'exports', compiled)(id => {
    if (id === 'vue' || id === 'vue-i18n') return require(id)
    if (id.endsWith('/useLocalAcquisitionConsole')) return { localConsoleKey: injectionKey }
    if (id.endsWith('/time')) return { formatBusinessTime: value => value || '—' }
    if (id === 'element-plus') return {}
    return { default: {} }
  }, module, module.exports)
  const node = type => ({ type, children: [], parent: null })
  const renderer = vue.createRenderer({ createElement: node, createText: node, createComment: node, setText() {}, setElementText() {}, patchProp() {}, insert(child, parent) { child.parent = parent; parent.children.push(child) }, remove() {}, parentNode: child => child.parent, nextSibling: () => null })
  let state; const component = module.exports.default
  const app = renderer.createApp({ ...component, setup(props, context) { state = component.setup(props, context); return () => vue.h('div') } })
  const messages = Object.fromEntries(['zh-CN', 'en-US'].map(locale => [locale, { common: JSON.parse(text(`../src/locales/${locale}/common.json`)) }]))
  app.use(createI18n({ legacy: false, locale: 'zh-CN', fallbackLocale: 'en-US', messages })); app.provide(injectionKey, owner); app.mount(node('root')); t.after(() => app.unmount())
  assert.equal(state.oldestPending.value, '—'); assert.equal(state.activeRetention.value, '—')
  owner.snapshot = { configuration: { active: null }, activeStorage: null, capacity: { pendingCount: 0, oldestPending: null, mainBytes: 10, journalBytes: 5, quotaBytes: 100 } }
  assert.equal(state.oldestPending.value, '暂无待上报样本'); assert.equal(state.activeRetention.value, '尚未激活')
  owner.snapshot.configuration.active = 'revision-8'; owner.snapshot.activeStorage = { revision: 'revision-8', quotaBytes: 100, retentionDays: 8 }
  assert.equal(owner.draft.storage.retentionDays, 7); assert.equal(state.activeRetention.value, '8 天'); assert.equal(state.usedBytes.value, 15); assert.equal(state.usagePercent.value, 15)
  owner.snapshot.capacity.pendingCount = 1; assert.equal(state.oldestPending.value, '—')
  owner.snapshot.capacity.oldestPending = '2026-11-12T12:00:00.000+08:00'; assert.equal(state.oldestPending.value, '2026-11-12T12:00:00.000+08:00')
  owner.snapshotError = 'read_failed'; assert.equal(state.oldestPending.value, '—'); assert.equal(state.activeRetention.value, '—'); assert.equal(state.usedBytes.value, null); assert.equal(state.usagePercent.value, null)
})

test('pending save displays the actual bilingual unknown-result alert', async () => {
  const vue = require('vue'), sfc = require('vue/compiler-sfc'), { createI18n } = require('vue-i18n')
  const { renderToString } = require('vue/server-renderer')
  const descriptor = sfc.parse(text('../src/components/console/FactsDeliveryDialog.vue')).descriptor
  const compiled = ts.transpileModule(sfc.compileScript(descriptor, { id:'pending-save-alert', inlineTemplate:true }).content, { compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020} }).outputText
  const key = Symbol('owner'), module = { exports:{} }
  const wrapper = { setup(_props, { slots }) { return () => vue.h('div', slots.default?.()) } }
  const alert = { props:['title','description'], setup(props) { return () => vue.h('p', {class:'fixture-alert'}, props.title + (props.description ?? '')) } }
  const elements = Object.fromEntries(['ElDialog','ElForm','ElFormItem','ElInput','ElInputNumber','ElSelect','ElOption','ElDatePicker'].map(name => [name,wrapper])); elements.ElAlert = alert
  new Function('require','module','exports',compiled)(id => {
    if (id === 'vue' || id === 'vue-i18n') return require(id)
    if (id === 'element-plus') return elements
    if (id.endsWith('/useLocalAcquisitionConsole')) return {localConsoleKey:key}
    if (id.endsWith('/sampleDetails')) return {formatSampleJson:value=>value}
    return {default:wrapper}
  }, module, module.exports)
  for (const locale of ['zh-CN','en-US']) {
    const common = JSON.parse(text(`../src/locales/${locale}/common.json`))
    const owner = vue.reactive({deliveryDialog:'settings',deliverySaveError:'storage_pending',busy:false,deliverySettings:{schemaVersion:1,settingsRevision:'r',origin:null,path:'/samples',intervalSeconds:5,identityMode:'per_plc',bindings:[]},sourceMaterial:{localSources:[]},label:value=>value})
    const app = vue.createSSRApp(module.exports.default)
    app.use(createI18n({legacy:false,locale,messages:{[locale]:{common}}})); app.provide(key,owner)
    const html = await renderToString(app)
    assert.ok(html.includes(common.delivery.settingsPending), locale)
    assert.ok(!html.includes(common.delivery.settingsSaveFailed), locale)
  }
})
