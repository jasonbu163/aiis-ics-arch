/** 文件路径: /frontend-js/tests/module-registry/acquisition-data.test.mjs
 * 功能描述: 采集模块装配、授权、上海时间与本机列宽偏好的回归。 */
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { parse, compileScript } from 'vue/compiler-sfc'
import * as vue from 'vue'
import { loadRegistry } from '../../scripts/check-module-manifests.mjs'
import { acquisitionDataModule } from '../../src/app/acquisition-data/manifest.js'
import { createModuleRegistry, accessibleNavigation, canAccessRoute, defaultAuthenticatedPath, resolveMessage } from '../../src/app/moduleManifest.js'
import { parseRolePageAccess } from '../../src/config/pageAccess.js'
import { formatShanghaiDateTime, shanghaiInputToRfc3339 } from '../../src/utils/date.js'
import { useTableColumnWidths } from '../../src/utils/tableColumnWidths.js'

const root = fileURLToPath(new URL('../../', import.meta.url))
const registry = await loadRegistry(root)
const pageIds = ['acquisition-data.realtime', 'acquisition-data.history']
const env = (supervisor = [], operator = []) => ({
  VITE_SUPERVISOR_PAGE_ACCESS_JSON: JSON.stringify(supervisor),
  VITE_OPERATOR_PAGE_ACCESS_JSON: JSON.stringify(operator)
})
const access = ids => ({ isAdmin: false, isLoggedIn: true, hasPageAccess: id => ids.includes(id) })

test('assembly, ordering, bilingual titles, single grants and original default', () => {
  const module = registry.activeModules.find(item => item.name === 'acquisition-data')
  assert.equal(module.order, 100)
  assert.deepEqual(module.routeRecords.map(route => [route.name, route.path, route.meta.pageId, route.meta.navigation.order]), [
    ['AcquisitionDataRealtime', '/acquisition-data/realtime', pageIds[0], 10],
    ['AcquisitionDataHistory', '/acquisition-data/history', pageIds[1], 20]
  ])
  const admin = { isAdmin: true, isLoggedIn: true }
  assert.equal(defaultAuthenticatedPath(registry, admin), '/plan/list')
  assert.equal(defaultAuthenticatedPath(registry, access(['plan.list', ...pageIds])), '/plan/list')
  for (const id of pageIds) {
    const grants = parseRolePageAccess(env([id], [id]), registry)
    const provider = access(grants.operator)
    assert.deepEqual(accessibleNavigation(registry, provider).flatMap(group => group.children.map(leaf => leaf.route.meta.pageId)), [id])
    assert.equal(defaultAuthenticatedPath(registry, provider), `/${id.replace('.', '/')}`)
    assert.equal(canAccessRoute(module.routeRecords.find(route => route.meta.pageId === id), provider), true)
  }
  assert.equal(accessibleNavigation(registry, access(['plan.list'])).some(group => group.name === 'acquisition-data'), false)
  assert.equal(canAccessRoute(module.routeRecords[0], { ...admin, isLoggedIn: false }), false)
  for (const locale of ['en-US', 'zh-CN']) {
    for (const key of ['acquisition-data.title', ...pageIds, 'acquisition-data.forbidden', 'acquisition-data.unavailable']) {
      assert.equal(typeof resolveMessage(registry.messages[locale], key), 'string', `${locale}:${key}`)
    }
  }
})

test('disabling removes routes, navigation and locales and rejects residual grants', async () => {
  const languages = Object.fromEntries(await Promise.all(['en-US', 'zh-CN'].map(async locale => [
    `/app/acquisition-data/locales/${locale}.json`, JSON.parse(await readFile(`${root}/src/app/acquisition-data/locales/${locale}.json`, 'utf8'))
  ])))
  const disabled = createModuleRegistry(
    { '/app/acquisition-data/manifest.js': { acquisitionDataModule: { ...acquisitionDataModule, enabled: false } } },
    languages, { 'en-US': {}, 'zh-CN': {} }, { requiredModules: [] }
  )
  assert.deepEqual(disabled.activeModuleNames, [])
  assert.deepEqual(disabled.routes, [])
  assert.deepEqual(disabled.navigation, [])
  assert.equal(disabled.messages['en-US']['acquisition-data'], undefined)
  assert.equal(defaultAuthenticatedPath(disabled, { isAdmin: true }), '/login')
  assert.throws(() => parseRolePageAccess(env(pageIds), disabled), /disabled pageId/)
})

test('Shanghai timestamps and strict wall-clock validation are independent of machine time zone', () => {
  assert.equal(shanghaiInputToRfc3339('2026-03-08 02:30:00'), '2026-03-08T02:30:00+08:00')
  for (const invalid of ['', '2026-02-30 00:00:00', '2026-01-01 24:00:00', '2026-01-01T00:00:00', null]) assert.equal(shanghaiInputToRfc3339(invalid), '')
  assert.equal(formatShanghaiDateTime('2026-11-10T21:56:44.313915+08:00'), '2026-11-10 21:56:44')
  assert.equal(formatShanghaiDateTime('2026-11-10T13:56:44Z'), '2026-11-10 21:56:44')
  for (const invalid of [null, '', 'not-a-time', '2026-11-10T21:56:44']) assert.equal(formatShanghaiDateTime(invalid), '')
  const code = `import {formatShanghaiDateTime,shanghaiInputToRfc3339} from './src/utils/date.js'; console.log(JSON.stringify([formatShanghaiDateTime('2026-03-08T02:30:00+08:00'),shanghaiInputToRfc3339('2026-03-08 02:30:00')]))`
  for (const TZ of ['Asia/Shanghai', 'America/Los_Angeles']) {
    const result = spawnSync(process.execPath, ['--input-type=module', '-e', code], { cwd: root, env: { ...process.env, TZ }, encoding: 'utf8' })
    assert.equal(result.status, 0, result.stderr)
    assert.deepEqual(JSON.parse(result.stdout), ['2026-03-08 02:30:00', '2026-03-08T02:30:00+08:00'])
  }
})

test('column widths isolate tables, restore valid fields and ignore stale or invalid preferences', () => {
  const store = new Map()
  globalThis.localStorage = { getItem: key => store.get(key) ?? null, setItem: (key, value) => store.set(key, value), removeItem: key => store.delete(key) }
  try {
    const definitions = { pointId: { width: 160, minWidth: 100 }, value: { width: 130, minWidth: 90 } }
    const one = useTableColumnWidths('test.one', definitions)
    one.onHeaderDragEnd(230, 160, { property: 'pointId' })
    const dragged = { property: 'value', width: 50, realWidth: 50 }
    one.onHeaderDragEnd(50, 130, dragged)
    assert.equal(one.widths.value, 90)
    assert.equal(dragged.width, 90)
    assert.equal(dragged.realWidth, 90)
    assert.equal(useTableColumnWidths('test.one', definitions).widths.pointId, 230)
    assert.equal(useTableColumnWidths('test.two', definitions).widths.pointId, 160)
    store.set('aiis-ics-architecture:table-widths:test.one', JSON.stringify({ pointId: -1, value: 'bad', retired: 400 }))
    const invalid = useTableColumnWidths('test.one', definitions)
    assert.deepEqual({ ...invalid.widths }, { pointId: 160, value: 130 })
    one.reset()
    assert.equal(one.widths.pointId, 160)
    assert.equal(store.has('aiis-ics-architecture:table-widths:test.one'), false)
    assert.equal(one.version.value, 1)
  } finally { delete globalThis.localStorage }
})

// 执行实际的 SFC setup 和 scope composable，替换网络与生命周期；不复制页面业务逻辑。
const scopeSource = await readFile(`${root}/src/app/acquisition-data/composables/useAcquisitionScope.js`, 'utf8')
const sfcSources = Object.fromEntries(await Promise.all(['realtime', 'history'].map(async name => [name,
  await readFile(`${root}/src/app/acquisition-data/views/${name}/index.vue`, 'utf8')
])))
const importsToDeps = source => source.replace(/^import\s+(.+?)\s+from\s+['"](.+?)['"];?$/gm, (_line, binding, module) => {
  if (binding.startsWith('{')) binding = binding.replace(/\bas\b/g, ':')
  return `const ${binding} = deps[${JSON.stringify(module)}]`
})
const makeScope = new Function('deps', `${importsToDeps(scopeSource).replace(/^export /gm, '')}\nreturn { useAcquisitionScope, requestStatus, rawValue, qualityKey, sourceKey }`)
const makePage = name => {
  const { descriptor } = parse(sfcSources[name])
  const executable = importsToDeps(compileScript(descriptor, { id: `acquisition-${name}` }).content).replace('export default', 'return')
  return { component: new Function('deps', executable), template: descriptor.template.content }
}
const deferred = () => {
  let resolve, reject
  const promise = new Promise((yes, no) => { resolve = yes; reject = no })
  return { promise, resolve, reject }
}
const options = [{ plcId: 'PLC-A', dbNumbers: [1, 21] }, { plcId: 'PLC-B', dbNumbers: [2, 21] }]
const tick = async () => { await vue.nextTick(); await Promise.resolve(); await vue.nextTick() }
function acquisitionPage(name, handlers = {}) {
  const hooks = [], unmounts = [], calls = []
  const customVue = { ...vue, onMounted: hook => hooks.push(hook), onBeforeUnmount: hook => unmounts.push(hook) }
  const api = {
    getOptions: () => handlers.options ? handlers.options() : Promise.resolve({ items: options }),
    browseLatest: params => { calls.push(params); return handlers.list ? handlers.list(params) : Promise.resolve({ items: [], total: 0 }) },
    getHistory: params => { calls.push(params); return handlers.list ? handlers.list(params) : Promise.resolve({ items: [], total: 0 }) },
    getHistoryDetail: id => handlers.detail ? handlers.detail(id) : Promise.resolve({ id, points: [] })
  }
  const scope = makeScope({ vue: customVue, '../api/index': api })
  const { component, template } = makePage(name)
  const deps = {
    vue: customVue, '@element-plus/icons-vue': { QuestionFilled: {} },
    '@/components/common/ActionButton.vue': {}, '@/components/common/BaseCard.vue': {},
    '@/utils/date': { formatShanghaiDateTime, shanghaiInputToRfc3339 },
    '@/utils/tableColumnWidths': { useTableColumnWidths }, '../../api/index': api,
    '../../composables/useAcquisitionScope': scope, './HistoryDetailDialog.vue': {}
  }
  const effect = vue.effectScope()
  const state = effect.run(() => component(deps).setup({}, { expose() {} }))
  return { state, calls, template, mount: async () => { hooks.forEach(fn => fn()); await tick() },
    unmount: () => { unmounts.forEach(fn => fn()); effect.stop() } }
}

test('actual realtime setup queries all first, preserves compatible DB and makes one request per selection', async () => {
  const p = acquisitionPage('realtime')
  await p.mount()
  assert.deepEqual(p.calls, [{ page: 1, pageSize: 50 }])
  assert.deepEqual(p.state.dbNumbers.value, [1, 2, 21])
  p.state.dbNumber.value = 21; await tick()
  assert.deepEqual(p.calls.at(-1), { dbNumber: 21, page: 1, pageSize: 50 })
  p.state.plcId.value = 'PLC-A'; await tick()
  assert.equal(p.state.dbNumber.value, 21)
  assert.deepEqual(p.calls.at(-1), { plcId: 'PLC-A', dbNumber: 21, page: 1, pageSize: 50 })
  p.state.dbNumber.value = 1; await tick()
  const before = p.calls.length
  p.state.plcId.value = 'PLC-B'; await tick()
  assert.equal(p.state.dbNumber.value, null)
  assert.equal(p.calls.length, before + 1)
  assert.deepEqual(p.calls.at(-1), { plcId: 'PLC-B', page: 1, pageSize: 50 })
  p.state.dbNumber.value = 21; await tick()
  p.state.plcId.value = ''; await tick()
  assert.equal(p.state.dbNumber.value, 21)
  assert.deepEqual(p.calls.at(-1), { dbNumber: 21, page: 1, pageSize: 50 })
  p.state.changeSize(20); await tick()
  assert.deepEqual(p.calls.at(-1), { dbNumber: 21, page: 1, pageSize: 20 })
  p.state.changePage(2); await tick()
  assert.deepEqual(p.calls.at(-1), { dbNumber: 21, page: 2, pageSize: 20 })
  for (const field of ['plcId', 'dbNumber', 'sourceType']) assert.match(p.template, new RegExp(`prop="${field}"`))
  p.unmount()
})

test('actual realtime debounce sends a literal server search, clears old state and ignores late responses', async () => {
  const old = deferred(), recent = deferred()
  let n = 0
  const p = acquisitionPage('realtime', { list: () => ++n === 1 ? old.promise : recent.promise })
  await p.mount()
  p.state.rows.value = [{ pointId: 'old' }]; p.state.total.value = 4
  p.state.search.value = '  %_\\ X  '
  assert.deepEqual(p.state.rows.value, [])
  assert.equal(p.state.total.value, 0)
  assert.equal(p.calls.length, 1)
  await new Promise(resolve => setTimeout(resolve, 350))
  assert.deepEqual(p.calls.at(-1), { pointSearch: '%_\\ X', page: 1, pageSize: 50 })
  recent.resolve({ items: [{ pointId: 'new' }], total: 1 }); await tick()
  old.resolve({ items: [{ pointId: 'late' }], total: 99 }); await tick()
  assert.deepEqual(p.state.rows.value, [{ pointId: 'new' }])
  assert.equal(p.state.total.value, 1)
  p.unmount()
})

test('empty authorized scope still makes the default list request and exposes failures separately', async () => {
  for (const name of ['realtime', 'history']) {
    const p = acquisitionPage(name, { options: async () => ({ items: [] }) })
    await p.mount()
    assert.equal(p.state.optionsState.value, 'ready')
    assert.equal(p.calls.length, 1)
    assert.equal(p.state.state.value, 'ready')
    assert.deepEqual(p.state.options.value, [])
    p.unmount()
    const q = acquisitionPage(name, { options: async () => ({ items: [] }), list: async () => { throw Error('offline') } })
    await q.mount()
    assert.equal(q.calls.length, 1)
    assert.equal(q.state.state.value, 'error')
    q.unmount()
  }
})

test('actual history setup queries 24h, filters independently and only submits valid edited times', async () => {
  const p = acquisitionPage('history')
  await p.mount()
  assert.equal(p.calls.length, 1)
  assert.equal(p.calls[0].page, 1)
  assert.equal(p.calls[0].pageSize, 50)
  assert.equal(Date.parse(p.calls[0].to) - Date.parse(p.calls[0].from), 24 * 60 * 60 * 1000)
  assert.equal('plcId' in p.calls[0], false)
  assert.equal('dbNumber' in p.calls[0], false)
  p.state.from.value = '2026-11-01 10:00:00'; p.state.to.value = '2026-11-08 10:00:00'
  await tick(); assert.equal(p.calls.length, 1)
  p.state.submit(); await tick()
  assert.equal(p.calls.length, 2)
  assert.equal(p.calls.at(-1).from, '2026-11-01T10:00:00+08:00')
  p.state.dbNumber.value = 2; await tick()
  assert.equal(p.calls.length, 3)
  assert.equal(p.calls.at(-1).dbNumber, 2)
  p.state.plcId.value = 'PLC-A'; await tick()
  assert.equal(p.state.dbNumber.value, null)
  assert.equal(p.calls.length, 4)
  assert.equal(p.calls.at(-1).plcId, 'PLC-A')
  p.state.to.value = '2026-11-08 10:00:01'; p.state.submit(); await tick()
  assert.equal(p.calls.length, 4)
  assert.equal(p.state.state.value, 'invalid')
  for (const field of ['plcId', 'dbNumber', 'sourceType']) assert.match(p.template, new RegExp(`prop="${field}"`))
  p.unmount()
})

test('history input change invalidates in-flight list and detail; missing source has a bilingual label', async () => {
  const oldList = deferred(), oldDetail = deferred()
  let count = 0
  const p = acquisitionPage('history', { list: () => ++count === 1 ? oldList.promise : Promise.resolve({ items: [{ id: '7' }], total: 1 }), detail: () => oldDetail.promise })
  await p.mount()
  p.state.plcId.value = 'PLC-A'; await tick()
  assert.deepEqual(p.state.rows.value, [{ id: '7' }])
  const pending = p.state.openDetail('7')
  p.state.from.value = '2026-11-01 10:00:00'
  assert.equal(p.state.detailVisible.value, false)
  assert.deepEqual(p.state.rows.value, [])
  oldDetail.resolve({ id: '7', points: [] }); oldList.resolve({ items: [{ id: '2' }], total: 2 })
  await pending; await tick()
  assert.equal(p.state.detail.value, null)
  assert.deepEqual(p.state.rows.value, [])
  assert.equal(p.state.total.value, 0)
  for (const locale of ['en-US', 'zh-CN']) {
    for (const type of ['daa', 'external', 'unrecorded']) assert.equal(typeof resolveMessage(registry.messages[locale], `acquisition-data.source.${type}`), 'string')
  }
  p.unmount()
})
