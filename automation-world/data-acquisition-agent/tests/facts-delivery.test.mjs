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
test('only the nine named IPC surfaces and original decimal string windows', async () => {
  const settings = { sources: [{ sequenceFrom: '9007199254740993', sequenceThrough: '9223372036854775806' }] }
  await api.getDeliverySettings(); await api.saveDeliverySettings(settings, 'revision'); await api.getDeliverySnapshot(); await api.setDelivery('pause'); await api.listDeliveries(null); await api.getDelivery('batch'); await api.previewDelivery('cycle'); await api.testFactsEndpoint('plc'); await api.getFactsSourceMaterial()
  assert.deepEqual(calls.map(c => c.command), ['daa_get_delivery_settings','daa_save_delivery_settings','daa_get_delivery_snapshot','daa_set_delivery','daa_list_deliveries','daa_get_delivery','daa_preview_delivery','daa_test_facts_endpoint','daa_get_facts_source_material'])
  assert.equal(calls[1].request.settings.sources[0].sequenceFrom, '9007199254740993'); assert.equal(calls[4].request.limit, 20)
  assert.doesNotMatch(source, /fetch\(|XMLHttpRequest|localStorage/)
})
test('real two-page controls, read-only material, stable column preferences and paired locale keys', () => {
  for (const page of ['../src/app/collection/views/storage/index.vue','../src/app/runtime/views/overview/index.vue']) assert.match(text(page), /FactsDeliveryPanel/)
  const panel = text('../src/components/console/FactsDeliveryPanel.vue'), dialog = text('../src/components/console/FactsDeliveryDialog.vue')
  assert.match(panel, /local\.bootstrap\.uploadAvailable/); assert.match(panel, /header-dragend/); assert.match(panel, /widthKey\('com\.aiis\.aw\.dataacquisitionagent', 'storage\.delivery-queue'\)/); assert.match(panel, /\[10,20,50\]/)
  assert.doesNotMatch(dialog, /textarea|contenteditable|v-html|JSON\.parse\(.*origin/); assert.match(dialog, /CONTRACT_PINS/)
  const zh = JSON.parse(text('../src/locales/zh-CN/common.json')).delivery, en = JSON.parse(text('../src/locales/en-US/common.json')).delivery
  function keys(o, p = '') { return Object.entries(o).flatMap(([k,v]) => typeof v === 'object' ? keys(v,p+k+'.') : [p+k]).sort() }
  assert.deepEqual(keys(zh),keys(en)); assert.match(zh.readOnly,/ACK/); assert.match(en.states.unknown,/reconciliation/)
})
