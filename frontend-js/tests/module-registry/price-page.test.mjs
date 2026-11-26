/** 编译实际单价页并替换网络依赖，验证日期筛选、部分写入、上海小时及请求竞态。 */
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { parse, compileScript } from 'vue/compiler-sfc'
import * as vue from 'vue'
import { createI18n } from 'vue-i18n'
import { useTableColumnWidths } from '../../src/utils/tableColumnWidths.js'
import * as priceHelpers from '../../src/app/energy/components/energyPricing.js'
import { loadRegistry } from '../../scripts/check-module-manifests.mjs'

const source = await readFile(new URL('../../src/app/energy/views/price.vue', import.meta.url), 'utf8')
const { descriptor } = parse(source)
const script = compileScript(descriptor, { id: 'price-page-test' }).content
const executable = script.replace(/^import\s+(.+?)\s+from\s+['"](.+?)['"];?$/gm, (_line, binding, module) => {
  return `const ${binding.replace(/\bas\b/g, ':')} = deps[${JSON.stringify(module)}]`
}).replace('export default', 'return')
const makeComponent = new Function('deps', executable)
const registry = await loadRegistry(new URL('../../', import.meta.url).pathname)
const water = { itemKey: 'water_feed', nameZh: '工业用水', nameEn: 'Water', unit: '元/m³' }
const electric = { itemKey: 'electric', nameZh: '电能单价', nameEn: 'Electricity Price', unit: 'CNY/kWh' }
const definitions = [{ ...water, enabled: true }, { ...electric, enabled: true }]
const current = [{ ...water, price: null }, { ...electric, price: 0 }]
const observedAt = '2026-10-13T10:59:00+08:00'
const history = { columns: definitions, items: [] }
const deferred = () => {
  let resolve, reject
  const promise = new Promise((yes, no) => { resolve = yes; reject = no })
  return { promise, resolve, reject }
}
function page(api = {}, locale = 'en-US') {
  const messages = []
  const calls = { current: 0, history: [], post: [] }
  const hooks = [], unmounts = []
  const i18n = createI18n({ legacy: false, locale, messages: registry.messages })
  const component = makeComponent({
    vue: { ...vue, onMounted: hook => hooks.push(hook), onBeforeUnmount: hook => unmounts.push(hook) },
    'vue-i18n': { useI18n: () => i18n.global },
    'element-plus': { ElMessage: Object.fromEntries(['error', 'success', 'warning'].map(
      type => [type, value => messages.push([type, value])]
    )) },
    '@/components/common/ActionButton.vue': {}, '@/components/common/BaseCard.vue': {},
    '@/utils/tableColumnWidths': { useTableColumnWidths },
    '../components/energyPricing': priceHelpers,
    '../api/pricing': {
      currentPrices: () => { calls.current++; return api.current ? api.current() : Promise.resolve(current) },
      hourlyPrices: params => { calls.history.push(params); return api.history ? api.history(params) : Promise.resolve(history) },
      pricingItems: () => Promise.resolve(definitions),
      saveHourlyPrices: input => {
        calls.post.push(input)
        return api.post ? api.post(input) : Promise.resolve({ values: { water_feed: { observedAt } } })
      }
    }
  })
  const state = component.setup({}, { expose() {} })
  return { state, calls, messages, mount: () => hooks[0](), unmount: () => unmounts[0](), t: i18n.global.t }
}

test('actual SFC loads latest history by default, filters by day, and restores latest on clear', async () => {
  const latest = { hourStart: '2026-10-13T10:00:00+08:00', values: {} }
  const p = page({ history: async ({ date }) => date ? history : { ...history, items: [latest] } })
  assert.equal(p.state.selectedDate.value, null)
  await p.mount()
  assert.deepEqual(p.state.current.value, current)
  assert.deepEqual(p.state.history.value, [latest])

  p.state.selectedDate.value = '2026-11-25'
  await p.state.loadHistory()
  assert.deepEqual(p.state.historyColumns.value, definitions)
  assert.deepEqual(p.state.history.value, [])

  p.state.selectedDate.value = null
  await p.state.loadHistory()
  assert.deepEqual(p.state.history.value, [latest])
  assert.deepEqual(p.calls.history, [
    { page: 1, pageSize: 1 },
    { date: '2026-11-25', page: 1, pageSize: 24 },
    { page: 1, pageSize: 1 },
  ])
  assert.equal(p.state.displayPrice(null), '—')
  assert.equal(p.state.displayPrice(0), '0')
  assert.match(descriptor.template.content, /v-for="item in historyColumns"/)
  assert.match(descriptor.template.content, /valueFor\(row, item.itemKey\)/)
  assert.match(descriptor.template.content, /:close-on-click-modal="true"/)
})

test('history columns and details hide a disabled project with saved prices', async () => {
  const [waterColumn, electricColumn] = definitions
  const saved = { hourStart: observedAt, values: { water_feed: { price: 0 }, electric: { price: 8 } } }
  let enabled = false
  const p = page({ history: async () => ({
    columns: [waterColumn, { ...electricColumn, enabled }],
    items: [saved],
  }) })
  await p.mount()
  p.state.details.value = saved
  assert.deepEqual(p.state.historyColumns.value, [waterColumn])
  assert.deepEqual(p.state.detailItems.value.map(item => item.itemKey), ['water_feed'])
  assert.equal(p.state.history.value[0].values.electric.price, 8)

  enabled = true
  await p.state.loadHistory()
  assert.deepEqual(p.state.historyColumns.value, definitions)
  assert.deepEqual(p.state.detailItems.value.map(item => item.itemKey), ['water_feed', 'electric'])
})

test('only entered prices are submitted and unset remarks and server clock remain distinguishable', async () => {
  const p = page()
  await p.mount()
  p.state.openAdd()
  assert.equal(p.state.observedAt.value, null)
  const [input, peer] = p.state.formItems.value
  input.price = '0'
  input.remarkTouched = true
  assert.equal(peer.price, '')
  await p.state.save()
  assert.deepEqual(p.calls.post, [{ observedAt: null, items: { water_feed: { price: '0', remark: '' } } }])
  assert.equal(p.state.dialogVisible.value, false)
  assert.equal(p.state.selectedDate.value, '2026-10-13')
  assert.equal(p.calls.current, 2)
  assert.deepEqual(p.calls.history.at(-1), { date: '2026-10-13', page: 1, pageSize: 24 })
})

test('invalid inputs never POST, future failures preserve form and unlock', async () => {
  const p = page({ post: async () => { throw Error('post') } })
  await p.mount()
  p.state.openAdd()
  await p.state.save()
  assert.deepEqual(p.calls.post, [])
  const [input] = p.state.formItems.value
  for (const value of ['-1', '1000000', '0.00001', '1.2345000000000001']) {
    input.price = value
    await p.state.save()
    assert.deepEqual(p.calls.post, [])
  }
  input.price = '1.2345000000000'
  p.state.observedAt.value = '2026-10-10T10:59:00'
  p.state.remarkTouched.value = true
  await p.state.save()
  assert.equal(p.state.dialogVisible.value, true)
  assert.equal(p.state.saving.value, false)
  assert.equal(input.price, '1.2345000000000')
  assert.deepEqual(p.calls.post[0], { observedAt: '2026-10-10T02:59:00.000Z',
    items: { water_feed: { price: '1.2345000000000' } }, remark: '' })
})

test('modal cancel sends no request and concurrent saving locks submit and close', async () => {
  const pending = deferred()
  const p = page({ post: () => pending.promise })
  await p.mount()
  p.state.openAdd()
  let closed = false
  p.state.beforeClose(() => { closed = true })
  assert.equal(closed, true)
  assert.equal(p.calls.post.length, 0)
  p.state.formItems.value[0].price = '0'
  const saving = p.state.save()
  closed = false
  p.state.beforeClose(() => { closed = true })
  await p.state.save()
  assert.equal(closed, false)
  assert.equal(p.calls.post.length, 1)
  pending.resolve({ values: { water_feed: { observedAt } } })
  await saving
  assert.equal(p.state.dialogVisible.value, false)
})

test('failed refresh after a write remains successful and leaves current and historical errors independent', async () => {
  let fail = false
  const p = page({
    current: async () => { if (fail) throw Error('current'); return current },
    history: async () => { if (fail) throw Error('history'); return history }
  })
  await p.mount()
  fail = true
  p.state.openAdd()
  p.state.formItems.value[0].price = '1'
  await p.state.save()
  assert.equal(p.state.dialogVisible.value, false)
  assert.equal(p.state.currentError.value && p.state.historyError.value, true)
  assert.deepEqual(p.state.current.value, current)
  assert.deepEqual(p.messages.map(([level]) => level), ['success', 'error', 'error'])
})

test('late history and current requests cannot replace newer responses or update unmounted state', async () => {
  const previous = deferred(), recent = deferred()
  let n = 0
  const p = page({ history: params => params.date === '2026-10-11' ? previous.promise : recent.promise,
    current: () => ++n === 1 ? previous.promise : Promise.resolve(current) })
  p.state.selectedDate.value = '2026-10-11'
  const stale = p.state.loadHistory(), staleCurrent = p.state.loadCurrent()
  p.state.selectedDate.value = '2026-10-12'
  const active = p.state.loadHistory()
  await p.state.loadCurrent()
  previous.resolve({ items: [{ hourStart: 'stale' }], columns: [] })
  await stale
  await staleCurrent
  assert.deepEqual(p.state.current.value, current)
  assert.equal(p.state.historyLoading.value, true)
  recent.resolve({ columns: definitions, items: [{ hourStart: 'active' }] })
  await active
  assert.deepEqual(p.state.history.value, [{ hourStart: 'active' }])
  const late = deferred()
  const q = page({ current: () => late.promise })
  const result = q.state.loadCurrent()
  q.unmount()
  late.resolve(current)
  await result
  assert.deepEqual(q.state.current.value, [])
})

test('language fallback, original localized units, and static locale key symmetry', () => {
  const zh = page({}, 'zh-CN')
  const en = page({}, 'en-US')
  assert.equal(zh.state.name({ ...water, nameZh: null }), 'Water')
  assert.equal(en.state.name({ ...water, nameEn: null }), '工业用水')
  assert.equal(zh.state.unit(electric), '元/kWh')
  assert.equal(en.state.unit(electric), 'CNY/kWh')
  assert.equal(zh.state.unit({ ...electric, unit: 'custom unit' }), 'custom unit')
  assert.equal(zh.t('energy.price.historyLatest'), '最近一条记录')
  assert.equal(en.t('energy.price.historyLatest'), 'Latest record')
  const keys = (locale, namespace) => Object.keys(registry.messages[locale].energy[namespace]).sort()
  for (const namespace of ['price', 'pricing']) {
    assert.deepEqual(keys('en-US', namespace), keys('zh-CN', namespace))
  }
})

test('Shanghai historical picker resolves repeated hours and rejects gaps in any host timezone', () => {
  const { encodeObservedAt, businessDate, businessDateTime } = priceHelpers
  assert.equal(encodeObservedAt('1991-08-01T10:00:00'), '1991-08-01T01:00:00.000Z')
  assert.equal(encodeObservedAt('1991-09-15T01:30:00'), '1991-09-14T16:30:00.000Z')
  assert.equal(encodeObservedAt('1000-01-01T10:00:00'), '1000-01-01T01:54:17.000Z')
  assert.throws(() => encodeObservedAt('1991-04-14T02:30:00'))
  assert.equal(businessDate('2026-10-12T16:00:00Z'), '2026-10-13')
  assert.equal(businessDateTime('2026-10-13T02:59:00Z'), '2026-10-13 10:59:00')
})
