/** 文件路径: /frontend-js/tests/module-registry/price-page.test.mjs
 * 功能描述: 编译实际价格页 SFC，注入 API stub 验证局部状态、提交及刷新语义；不发送网络请求。 */
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { parse, compileScript } from 'vue/compiler-sfc'
import * as vue from 'vue'
import { createI18n } from 'vue-i18n'
import { loadRegistry } from '../../scripts/check-module-manifests.mjs'

const source = await readFile(new URL('../../src/app/auxiliary/views/price/index.vue', import.meta.url), 'utf8')
const { descriptor } = parse(source)
const script = compileScript(descriptor, { id: 'price-page-test' }).content
// 只替换模块导入；所有状态与 handler 均来自编译后的实际页面，未复制业务实现。
const executable = script.replace(/^import\s+(.+?)\s+from\s+['"](.+?)['"];?$/gm, (_line, binding, module) => {
  if (binding.startsWith('{')) binding = binding.replace(/\bas\b/g, ':')
  return `const ${binding} = deps[${JSON.stringify(module)}]`
}).replace('export default', 'return')
const makeComponent = new Function('deps', executable)
const registry = await loadRegistry(new URL('../../', import.meta.url).pathname)
const current = { electricPrice: 0, hydrogenPrice: '15.2500', argonPrice: 3.5, electricRemark: 'existing' }
const deferred = () => {
  let resolve, reject
  const promise = new Promise((yes, no) => { resolve = yes; reject = no })
  return { promise, resolve, reject }
}
function page(api = {}, locale = 'en-US') {
  const messages = []
  const calls = { current: 0, history: [], post: [] }
  const hooks = []
  const i18n = createI18n({ legacy: false, locale, messages: registry.messages })
  const component = makeComponent({
    vue: { ...vue, onMounted: hook => hooks.push(hook) },
    'vue-i18n': { useI18n: () => i18n.global },
    'element-plus': { ElMessage: {
      error: value => messages.push(['error', value]), success: value => messages.push(['success', value])
    } },
    '@/components/common/ActionButton.vue': {}, '@/components/common/BaseCard.vue': {},
    '@/utils/date': { formatDateTime: value => value },
    '@/app/auxiliary/api': {
      getCurrentPrice: () => { calls.current++; return api.current ? api.current() : Promise.resolve(current) },
      getPriceList: params => { calls.history.push(params); return api.history ? api.history(params) : Promise.resolve({ items: [] }) },
      createPrice: data => { calls.post.push(data); return api.post ? api.post(data) : Promise.resolve({}) }
    }
  })
  const state = component.setup({}, { expose() {} })
  state.formRef.value = { validate: async () => true }
  return { state, calls, messages, mount: () => hooks[0](), t: i18n.global.t, i18n }
}

test('actual SFC starts empty; mount reads facade and preserves zero/numeric strings and remarks', async () => {
  const p = page()
  assert.equal(p.state.form.electricPrice, undefined)
  assert.equal(p.state.form.hydrogenRemark, '')
  await p.mount()
  assert.equal(p.state.form.electricPrice, 0)
  assert.equal(p.state.form.hydrogenPrice, 15.25)
  assert.equal(p.state.form.electricRemark, 'existing')
  assert.deepEqual(p.calls.history, [{ page: 1, pageSize: 10 }])
  assert.deepEqual(p.state.priceHistory.value, [])
  assert.equal(p.state.currentEmpty.value, false)
})

test('null current record is unconfigured; malformed prices report errors without zero/default fallback', async () => {
  const empty = page({ current: async () => null })
  await empty.mount()
  assert.equal(empty.state.currentEmpty.value, true)
  assert.equal(empty.state.form.electricPrice, undefined)
  for (const bad of [null, undefined, '', '  ', 'no', Infinity, NaN, -1, '-2', false, {}]) {
    const p = page({ current: async () => ({ ...current, electricPrice: bad }) })
    await p.mount()
    assert.equal(p.state.form.electricPrice, undefined)
    assert.deepEqual(p.messages, [['error', p.t('auxiliary.price.currentLoadError')]])
    assert.equal(p.state.currentLoading.value, false)
    let validationError
    p.state.rules.electricPrice[0].validator({}, bad, error => { validationError = error })
    assert.equal(validationError.message, p.t('auxiliary.price.invalidPrice'))
  }
  for (const valid of [0, '0', '1.25']) {
    let error = 'not called'
    empty.state.rules.electricPrice[0].validator({}, valid, value => { error = value })
    assert.equal(error, undefined)
  }
})

test('current/history failures preserve previous input/data and finally restore independent loading', async () => {
  const get = deferred(), history = deferred()
  const p = page({ current: () => get.promise, history: () => history.promise })
  Object.assign(p.state.form, current)
  p.state.priceHistory.value = [{ id: 4 }]
  const pending = p.mount()
  assert.equal(p.state.currentLoading.value, true)
  assert.equal(p.state.historyLoading.value, true)
  assert.equal(p.state.formBusy.value, true)
  await p.state.handleSave()
  await p.state.handleRefresh()
  assert.equal(p.calls.current, 1)
  assert.equal(p.calls.post.length, 0)
  get.reject(new Error('current unavailable')); history.reject(new Error('history unavailable'))
  await pending
  assert.deepEqual(p.state.form.electricPrice, 0)
  assert.deepEqual(p.state.priceHistory.value, [{ id: 4 }])
  assert.equal(p.state.currentLoading.value, false)
  assert.equal(p.state.historyLoading.value, false)
  assert.equal(p.state.formBusy.value, false)
  assert.deepEqual(p.messages.map(item => item[1]).sort(), [p.t('auxiliary.price.currentLoadError'), p.t('auxiliary.price.historyLoadError')].sort())
})

test('POST uses snapshot, prevents duplicate validation/submission, keeps saved values and awaits history', async () => {
  const validation = deferred(), post = deferred(), history = deferred()
  const p = page({ post: () => post.promise, history: () => history.promise })
  Object.assign(p.state.form, { electricPrice: '0', hydrogenPrice: 2.1234, argonPrice: 3, electricRemark: 'E', hydrogenRemark: 'H', argonRemark: 'A' })
  p.state.formRef.value.validate = () => validation.promise
  const saving = p.state.handleSave()
  assert.equal(p.state.saveLoading.value, true)
  await p.state.handleSave()
  validation.resolve(true)
  await Promise.resolve(); await Promise.resolve()
  assert.deepEqual(p.calls.post, [{ electricPrice: 0, hydrogenPrice: 2.1234, argonPrice: 3, electricRemark: 'E', hydrogenRemark: 'H', argonRemark: 'A', remark: `${p.t('auxiliary.price.electric')}: E; ${p.t('auxiliary.price.hydrogen')}: H; ${p.t('auxiliary.price.argon')}: A` }])
  // 即使外部修改 reactive 对象，POST 完成后仍同步本次提交快照。
  p.state.form.electricPrice = 99
  await p.state.handleSave(); await p.state.handleRefresh()
  post.resolve({ electricPrice: 999 })
  await Promise.resolve(); await Promise.resolve()
  assert.equal(p.state.form.electricPrice, 0)
  assert.equal(p.calls.current, 0)
  assert.equal(p.calls.post.length, 1)
  assert.equal(p.state.saveLoading.value, true)
  history.resolve({ items: [{ id: 8 }] })
  await saving
  assert.deepEqual(p.state.priceHistory.value, [{ id: 8 }])
  assert.equal(p.state.saveLoading.value, false)
  assert.deepEqual(p.messages, [['success', p.t('common.success')]])
})

test('failed POST preserves input; history failure remains separate after successful POST', async () => {
  const failed = page({ post: async () => { throw new Error('POST failed') } })
  Object.assign(failed.state.form, current)
  await failed.state.handleSave()
  assert.equal(failed.state.form.hydrogenPrice, '15.2500')
  assert.equal(failed.calls.history.length, 0)
  assert.equal(failed.state.saveLoading.value, false)
  assert.deepEqual(failed.messages, [['error', failed.t('common.error')]])
  const p = page({ history: async () => { throw new Error('history failed') } })
  Object.assign(p.state.form, { electricPrice: 0, hydrogenPrice: 1, argonPrice: 2 })
  await p.state.handleSave()
  assert.equal(p.calls.post[0].remark, p.t('auxiliary.price.priceAdjustment'))
  assert.equal(p.calls.post.length, 1)
  assert.equal(p.state.form.electricPrice, 0)
  assert.equal(p.state.saveLoading.value, false)
  assert.deepEqual(p.messages, [['success', p.t('common.success')], ['error', p.t('auxiliary.price.historyLoadError')]])
  await p.state.handleRefresh()
  assert.equal(p.calls.current, 1)
  assert.equal(p.state.form.hydrogenPrice, 15.25)
})

test('invalid input and rejected/false form validation never POST and release submission guard', async () => {
  for (const validate of [async () => false, async () => { throw new Error('invalid') }, async () => true]) {
    const p = page()
    p.state.formRef.value.validate = validate
    await p.state.handleSave()
    assert.equal(p.calls.post.length, 0)
    assert.equal(p.state.saveLoading.value, false)
  }
})

test('new feedback keys resolve through actual Registry in both languages; switching translates validator', async () => {
  const p = page()
  for (const locale of ['en-US', 'zh-CN']) {
    p.i18n.global.locale.value = locale
    for (const key of ['currentEmpty', 'currentLoadError', 'historyLoadError', 'invalidPrice']) {
      const full = `auxiliary.price.${key}`
      assert.notEqual(p.t(full), full)
      assert.equal(typeof p.t(full), 'string')
    }
    let error
    p.state.rules.electricPrice[0].validator({}, null, value => { error = value })
    assert.equal(error.message, p.t('auxiliary.price.invalidPrice'))
  }
})

test('existing diagnostic mock integrates without implying persistence or overwriting saved snapshot', async () => {
  const mockSource = await readFile(new URL('../../src/app/auxiliary/api/mock.js', import.meta.url), 'utf8')
  const diagnosticUrl = new URL('../../src/api/mock/_diagnostic.js', import.meta.url).href
  const mock = await import(`data:text/javascript;base64,${Buffer.from(mockSource.replace("@/api/mock/_diagnostic", diagnosticUrl)).toString('base64')}`)
  const p = page({ current: mock.getCurrentPrice, history: mock.getPriceList, post: mock.createPrice })
  await p.mount()
  assert.ok(p.state.priceHistory.value.length > 0)
  const fixedPrice = p.state.form.electricPrice
  p.state.form.electricPrice = 0
  await p.state.handleSave()
  assert.equal(p.state.form.electricPrice, 0)
  assert.equal(p.calls.current, 1)
  assert.equal(p.calls.history.length, 2)
  assert.equal(p.calls.post.length, 1)
  await p.state.handleRefresh()
  assert.equal(p.state.form.electricPrice, fixedPrice)
})
