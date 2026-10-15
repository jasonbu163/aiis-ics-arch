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
const current = { observedAt: '2026-10-13T10:59:00+08:00', electricPrice: 0, hydrogenPrice: '15.2500', argonPrice: 3.5, electricRemark: 'existing' }
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
    'element-plus': { ElMessage: {
      error: value => messages.push(['error', value]), success: value => messages.push(['success', value])
    } },
    '@/components/common/ActionButton.vue': {}, '@/components/common/BaseCard.vue': {},
    '@/utils/date': { formatDateTime: value => value },
    '@/app/auxiliary/api': {
      getCurrentPrice: () => { calls.current++; return api.current ? api.current() : Promise.resolve(current) },
      getPriceList: params => { calls.history.push(params); return api.history ? api.history(params) : Promise.resolve({ items: [] }) },
      createPrice: data => { calls.post.push(data); return api.post ? api.post(data) : Promise.resolve({ observedAt: data.observedAt || "2026-10-13T12:00:00+08:00" }) }
    }
  })
  const state = component.setup({}, { expose() {} })
  state.formRef.value = { validate: async () => true }
  return { state, calls, messages, mount: () => hooks[0](), unmount: () => unmounts[0](), t: i18n.global.t, i18n }
}

const fill = p => Object.assign(p.state.form, { electricPrice: '0', hydrogenPrice: '2.1234', argonPrice: '3', electricRemark: 'E', hydrogenRemark: 'H', argonRemark: 'A', remark: 'whole snapshot' })

test('actual SFC: readonly current, Shanghai today, day history request and distinct event/modification columns', async () => {
  const p = page()
  assert.equal(p.state.selectedDate.value, p.state.businessDate(Date.now()))
  await p.mount()
  assert.equal(p.state.currentPrice.value.electricPrice,0)
  assert.equal(p.state.form.electricPrice,'')
  assert.deepEqual(p.calls.history,[{date:p.state.selectedDate.value,page:1,pageSize:24}])
  assert.equal(p.state.businessDate('2026-10-12T16:00:00Z'),'2026-10-13')
  assert.equal(p.state.businessDateTime('2026-10-13T02:59:00Z'),'2026-10-13 10:59:00')
  // Inspect the real template structure, in addition to executing its compiled setup.
  const beforeDialog=descriptor.template.content.split('<el-dialog')[0]
  assert.equal(beforeDialog.includes('<el-form'),false)
  assert.equal(beforeDialog.includes("@click=\"handleSave\""),false)
  assert.equal(descriptor.template.content.includes('el-pagination'),false)
  assert.match(descriptor.template.content,/prop="observedAt"/)
  assert.match(descriptor.template.content,/prop="updatedAt"/)
  assert.match(descriptor.template.content,/:editable="false" clearable/)
})

test('null current and bad price failures preserve recognizable previous values; histories never touch dialog', async () => {
  const empty=page({current:async()=>null});await empty.mount();assert.equal(empty.state.currentPrice.value,null)
  for(const bad of [null,undefined,'',' ','no',Infinity,NaN,-1,false,{}]) {
    const p=page({current:async()=>({...current,electricPrice:bad}),history:async()=>{throw Error('history')}})
    p.state.currentPrice.value=current;p.state.openAdd();fill(p)
    await p.mount()
    assert.equal(p.state.currentPrice.value.electricPrice,0)
    assert.equal(p.state.form.electricRemark,'E')
    assert.equal(p.state.currentError.value,true)
    assert.equal(p.state.historyError.value,true)
    assert.equal(p.state.currentLoading.value,false)
    assert.equal(p.state.historyLoading.value,false)
  }
})

test('new form is blank, cancel has no POST, clear picker encodes null, explicit picker encodes Shanghai offset',async()=>{
  const p=page();p.state.openAdd();assert.equal(p.state.form.observedAt,null)
  fill(p);p.state.cancelAdd();assert.equal(p.calls.post.length,0)
  p.state.openAdd();assert.equal(p.state.form.electricPrice,'');fill(p)
  await p.state.handleSave()
  assert.equal(p.calls.post[0].observedAt,null)
  assert.equal(p.calls.post[0].remark,'whole snapshot')
  p.state.openAdd();fill(p);p.state.form.observedAt='2026-10-10T10:59:00'
  await p.state.handleSave()
  assert.equal(p.calls.post[1].observedAt,'2026-10-10T02:59:00.000Z')
})

test('POST snapshot locks validation, duplicate submit, cancel and close; success closes, switches response day and reads current',async()=>{
  const validation=deferred(),post=deferred()
  const p=page({post:()=>post.promise});p.state.openAdd();fill(p)
  p.state.form.observedAt='2026-10-10T10:59:00'
  p.state.formRef.value.validate=()=>validation.promise
  const saving=p.state.handleSave()
  await p.state.handleSave();p.state.cancelAdd();let closed=false;p.state.beforeClose(()=>closed=true)
  assert.equal(closed,false);assert.equal(p.state.dialogVisible.value,true)
  p.state.form.electricPrice='99'
  validation.resolve(true);await Promise.resolve();await Promise.resolve()
  assert.equal(p.calls.post.length,1);assert.equal(p.calls.post[0].electricPrice,'0')
  post.resolve({observedAt:'2026-10-10T02:59:00Z',electricPrice:888})
  await saving
  assert.equal(p.state.dialogVisible.value,false)
  assert.equal(p.state.selectedDate.value,'2026-10-10')
  assert.equal(p.state.currentPrice.value.electricPrice,0)
  assert.equal(p.calls.current,1)
  assert.deepEqual(p.calls.history,[{date:'2026-10-10',page:1,pageSize:24}])
  assert.deepEqual(p.messages,[['success',p.t('common.success')]])
})

test('validation failure never POSTs; POST failure preserves every input and unlocks; no rounding',async()=>{
  for(const invalid of ['',null,-1,'1000000','0.00001','1.2345000000000001']) {
    const p=page();p.state.openAdd();fill(p);p.state.form.electricPrice=invalid
    await p.state.handleSave();assert.equal(p.calls.post.length,0);assert.equal(p.state.saveLoading.value,false)
  }
  const p=page({post:async()=>{throw Error('post')}});p.state.openAdd();fill(p)
  p.state.form.observedAt='2026-10-10T12:00:00'
  const input={...p.state.form};await p.state.handleSave()
  assert.deepEqual({...p.state.form},input);assert.equal(p.state.dialogVisible.value,true)
  assert.equal(p.calls.current,0);assert.equal(p.calls.history.length,0)
  assert.equal(p.state.saveLoading.value,false)
  for(const result of [false,Error('invalid')]) {
    const q=page();q.state.openAdd();fill(q);q.state.formRef.value.validate=async()=>{if(result instanceof Error)throw result;return result}
    await q.state.handleSave();assert.equal(q.calls.post.length,0)
  }
})

test('successful POST then failed GETs remains successful and never reopens/replays',async()=>{
  const p=page({current:async()=>{throw Error('get')},history:async()=>{throw Error('get')}})
  p.state.openAdd();fill(p);await p.state.handleSave()
  assert.equal(p.state.dialogVisible.value,false);assert.equal(p.calls.post.length,1)
  assert.deepEqual(p.messages,[['success',p.t('common.success')],['error',p.t('auxiliary.price.currentLoadError')],['error',p.t('auxiliary.price.historyLoadError')]])
})

test('history A/B late result/error/finally cannot replace B, current requests and unmount have same guard',async()=>{
  for(const rejectOld of [false,true]) {
    const a=deferred(),b=deferred();const p=page({history:params=>params.date==='2026-10-10'?a.promise:b.promise})
    p.state.selectedDate.value='2026-10-10';p.state.priceHistory.value=[{id:0}];const first=p.state.loadHistory()
    assert.deepEqual(p.state.priceHistory.value,[])
    p.state.selectedDate.value='2026-10-11';const second=p.state.loadHistory()
    if(rejectOld)a.reject(Error('old'));else a.resolve({items:[{id:1}]})
    await first;assert.equal(p.state.historyLoading.value,true);assert.deepEqual(p.messages,[])
    b.resolve({items:[{id:2}]});await second;assert.deepEqual(p.state.priceHistory.value,[{id:2}])
  }
  const a=deferred(),b=deferred();let n=0;const p=page({current:()=>++n===1?a.promise:b.promise})
  const first=p.state.loadCurrent(),second=p.state.loadCurrent();b.resolve({...current,electricPrice:2});await second
  a.resolve({...current,electricPrice:1});await first;assert.equal(p.state.currentPrice.value.electricPrice,2)
  const late=deferred();const q=page({current:()=>late.promise});const pending=q.state.loadCurrent();q.unmount();late.resolve(current);await pending
  assert.equal(q.state.currentPrice.value,null)
})

test('save auto day and subsequent manual day use latest request; pending old current cannot undo refreshed current',async()=>{
  const old=deferred(),saved=deferred(),manual=deferred(),oldCurrent=deferred();let n=0
  const p=page({current:()=>++n===1?oldCurrent.promise:Promise.resolve({...current,electricPrice:4}),history:params=>params.date==='2026-10-09'?old.promise:params.date==='2026-10-13'?saved.promise:manual.promise})
  p.state.selectedDate.value='2026-10-09';const starting=p.state.handleRefresh()
  p.state.openAdd();fill(p);const saving=p.state.handleSave();await Promise.resolve();await Promise.resolve();await Promise.resolve()
  assert.equal(p.state.selectedDate.value,'2026-10-13')
  p.state.selectedDate.value='2026-10-14';const latest=p.state.loadHistory()
  saved.resolve({items:[{id:1}]});old.resolve({items:[{id:0}]});oldCurrent.resolve({...current,electricPrice:9})
  await starting;await saving
  assert.equal(p.state.currentPrice.value.electricPrice,4);assert.equal(p.state.historyLoading.value,true)
  manual.resolve({items:[{id:2}]});await latest
  assert.deepEqual(p.state.priceHistory.value,[{id:2}])
})

test('both languages expose identical price keys and translated labels; facade/mock remain paired',()=>{
  const en=registry.messages['en-US'].auxiliary.price,zh=registry.messages['zh-CN'].auxiliary.price
  assert.deepEqual(Object.keys(en).sort(),Object.keys(zh).sort())
  for(const locale of ['en-US','zh-CN']) {
    const p=page({},locale)
    for(const key of ['add','observedAt','lastModified','serverTimeHint','overwriteHint','historyEmpty']) assert.notEqual(p.t('auxiliary.price.'+key),'auxiliary.price.'+key)
  }
})


test('Shanghai historical DST picker uses IANA offset, repeated hour fold=0, gap rejects and LMT remains representable',async()=>{
  const p=page()
  assert.equal(p.state.encodeObservedAt('1991-08-01T10:00:00'),'1991-08-01T01:00:00.000Z')
  assert.equal(p.state.encodeObservedAt('1991-09-15T01:30:00'),'1991-09-14T16:30:00.000Z')
  assert.equal(p.state.encodeObservedAt('1000-01-01T10:00:00'),'1000-01-01T01:54:17.000Z')
  assert.throws(()=>p.state.encodeObservedAt('1991-04-14T02:30:00'))
  p.state.openAdd();fill(p);p.state.form.observedAt='1991-04-14T02:30:00'
  await p.state.handleSave();assert.equal(p.calls.post.length,0);assert.equal(p.state.dialogVisible.value,true)
  assert.deepEqual(p.messages,[['error',p.t('auxiliary.price.invalidObservedAt')]])
})
