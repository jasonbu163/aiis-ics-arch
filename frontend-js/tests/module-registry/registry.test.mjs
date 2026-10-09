/** 文件路径: /frontend-js/tests/module-registry/registry.test.mjs
 * 功能描述: Registry 纯合同矩阵与当前源码接入回归；无网络、真实账号或外部 I/O。 */
import test from 'node:test'
import assert from 'node:assert/strict'
import { fileURLToPath } from 'node:url'
import { readFile } from 'node:fs/promises'
import {
  createModuleRegistry, canAccessRoute, accessibleNavigation, defaultAuthenticatedPath,
  resolveNavigationIcon, resolveMessage
} from '../../src/app/moduleManifest.js'
import { loadRegistry } from '../../scripts/check-module-manifests.mjs'
import { createMemoryHistory, createRouter } from 'vue-router'

const admin = { isAdmin: true }
const access = (...ids) => ({ isAdmin: false, hasPageAccess: id => ids.includes(id) })
const component = () => Promise.resolve({ default: {} })
const globals = {
  'en-US': { breadcrumb: { legacy: 'Legacy page' } },
  'zh-CN': { breadcrumb: { legacy: '旧页面' } }
}
function fixture(name = 'example', options = {}) {
  return {
    name, enabled: true, order: 100,
    navigation: { titleKey: `${name}.title` },
    routes: [{ path: `${name}/list`, name: `${name}List`, component,
      meta: { pageId: `${name}.list`, titleKey: `${name}.title`, navigation: { visible: true } }
    }], ...options
  }
}
function build(modules, change = () => {}, options = { requiredModules: [] }) {
  const manifests = Object.fromEntries(modules.map(module => [`/app/${module.name}/manifest.js`, { default: module }]))
  const locales = Object.fromEntries(modules.flatMap(module => ['en-US', 'zh-CN'].map(locale => [
    `/app/${module.name}/locales/${locale}.json`, { title: locale === 'en-US' ? 'Example' : '示例' }
  ])))
  change(manifests, locales)
  return createModuleRegistry(manifests, locales, globals, options)
}
const four = (registry, provider) => ({
  routes: registry.routes.map(route => route.name),
  menus: accessibleNavigation(registry, provider).flatMap(group => group.children.map(leaf => leaf.name)),
  locales: Object.keys(registry.messages['en-US']),
  redirect: defaultAuthenticatedPath(registry, provider)
})

test('add/remove and enabled gate affect all four consumers; orphan grants never create entries', () => {
  const module = fixture()
  const enabled = four(build([module]), access('example.list'))
  assert.deepEqual(enabled, { routes: ['exampleList'], menus: ['exampleList'], locales: ['breadcrumb', 'example'], redirect: '/example/list' })
  const removed = four(build([]), access('example.list'))
  const disabled = four(build([fixture('example', { enabled: false })]), admin)
  assert.deepEqual(removed, { routes: [], menus: [], locales: ['breadcrumb'], redirect: '/login' })
  assert.deepEqual(disabled, removed)
})

test('required system must exist and explicitly remain enabled, never exempt from access', () => {
  assert.throws(() => build([], undefined, {}), /Missing required module/)
  assert.throws(() => build([fixture('system', { enabled: false })], undefined, {}), /Required module/)
  const system = fixture('system')
  delete system.enabled
  assert.throws(() => build([system], undefined, {}), /Required module/)
  assert.equal(accessibleNavigation(build([fixture('system')], undefined, {}), access()).length, 0)
})

test('legacy named export and global keys retain route/locale behavior and array default order', () => {
  const module = fixture('legacy')
  delete module.enabled
  delete module.navigation
  module.routes = ['ZFirst', 'ASecond'].map(name => ({ path: `legacy/${name}`, name, component,
    meta: { pageId: `legacy.${name}`, titleKey: 'breadcrumb.legacy' }
  }))
  const registry = build([module], manifests => {
    manifests['/app/legacy/manifest.js'] = { legacyModule: module }
  })
  assert.equal(registry.activeModules[0].modern, false)
  assert.equal(registry.navigation.length, 0)
  assert.equal(registry.messages['en-US'].legacy.title, 'Example')
  assert.equal(defaultAuthenticatedPath(registry, admin), '/legacy/ZFirst')
  assert.deepEqual(registry.routes.map(route => route.name), ['ZFirst', 'ASecond'])
})

test('new-field detection enforces owned titles; missing nav produces no group', () => {
  for (const field of ['enabled', 'navigation', 'routeNavigation']) {
    const module = fixture()
    delete module.enabled
    delete module.navigation
    delete module.routes[0].meta.navigation
    module.routes[0].meta.titleKey = 'breadcrumb.legacy'
    if (field === 'enabled') module.enabled = true
    if (field === 'navigation') module.navigation = { titleKey: 'example.title' }
    if (field === 'routeNavigation') module.routes[0].meta.navigation = { visible: false }
    assert.throws(() => build([module]), /module namespace/)
  }
  const registry = build([fixture('example', { navigation: undefined })])
  assert.equal(registry.routes.length, 1)
  assert.equal(registry.navigation.length, 0)
})

test('legacy title cannot resolve only through a disabled module', () => {
  const legacy = { name: 'legacy', routes: [{ path: 'legacy/list', name: 'Legacy', component,
    meta: { pageId: 'legacy.list', titleKey: 'other.title' }
  }] }
  assert.throws(() => build([legacy, fixture('other', { enabled: false })]), /Inactive title namespace/)
})

test('legacy redirect parents, nested children, aliases and inherited access metadata remain compatible', async () => {
  const module = { name: 'legacy', routes: [{
    path: 'legacy', redirect: '/legacy/list', meta: { requiresAdmin: true },
    children: [{ path: 'list', alias: 'shortcut', name: 'LegacyList', component,
      meta: { pageId: 'legacy.list', titleKey: 'breadcrumb.legacy' } }]
  }] }
  const registry = build([module])
  assert.equal(registry.routes[0].redirect, '/legacy/list')
  assert.equal(registry.routes[0].children[0].alias, 'shortcut')
  assert.equal(registry.routes[0].component, undefined)
  const leaf = registry.routeRecords.find(route => route.name === 'LegacyList')
  assert.equal(leaf.path, '/legacy/list')
  assert.equal(canAccessRoute(leaf, access('legacy.list')), false)
  assert.equal(defaultAuthenticatedPath(registry, access('legacy.list')), '/login')
  assert.equal(defaultAuthenticatedPath(registry, admin), '/legacy/list')
  const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/', children: registry.routes }] })
  assert.equal(router.resolve('/legacy/shortcut').name, 'LegacyList')
  await router.push('/legacy')
  assert.equal(router.currentRoute.value.path, '/legacy/list')
  assert.equal(router.currentRoute.value.meta.requiresAdmin, true)
  const minimal = build([{ name: 'legacy', routes: [{ path: 'legacy/redirect', redirect: '/login' }] }])
  assert.equal(minimal.routes[0].redirect, '/login')
  assert.equal(defaultAuthenticatedPath(minimal, admin), '/login')
})

test('QA-001: legacy optional parameters remain routable and absent from default/menu', () => {
  const route = { path: 'legacy/:id?', name: 'Optional', component,
    meta: { pageId: 'legacy.detail' } }
  const registry = build([{ name: 'legacy', routes: [route] }])
  const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/', children: registry.routes }] })
  assert.equal(router.resolve('/legacy').name, 'Optional')
  assert.equal(router.resolve('/legacy/42').name, 'Optional')
  assert.equal(canAccessRoute(registry.routeRecords[0], access('legacy.detail')), true)
  assert.equal(defaultAuthenticatedPath(registry, admin), '/login')
  assert.deepEqual(accessibleNavigation(registry, admin), [])
  for (const path of ['legacy/list?query=1', 'legacy/list#hash']) {
    assert.throws(() => build([{ name: 'legacy', routes: [{ ...route, path }] }]), /Invalid route path/)
  }
})

test('QA-002: preserve one empty default child but reject duplicate sibling defaults', () => {
  const first = { path: '', name: 'First', component, meta: { pageId: 'legacy.first' } }
  const parent = { path: 'legacy', component: {}, children: [first] }
  const registry = build([{ name: 'legacy', routes: [parent] }])
  const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/', children: registry.routes }] })
  assert.equal(router.resolve('/legacy').name, 'First')
  assert.equal(defaultAuthenticatedPath(registry, admin), '/legacy')
  parent.children.push({ ...first, name: 'Second', meta: { pageId: 'legacy.second' } })
  const conflicting = createRouter({ history: createMemoryHistory(), routes: [{ path: '/', children: [parent] }] })
  assert.equal(conflicting.resolve({ name: 'First' }).fullPath, conflicting.resolve({ name: 'Second' }).fullPath)
  assert.throws(() => build([{ name: 'legacy', routes: [parent] }]), /Duplicate route path/)
})

test('QA-003: parent aliases propagate to nested child collision checks across modules', () => {
  const parent = { path: 'base', alias: ['/shortcut', '/alternate'], component: {}, children: [{
    path: 'list', name: 'Aliased', component, meta: { pageId: 'legacy.list' }
  }] }
  const valid = build([{ name: 'legacy', routes: [parent] }])
  const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/', children: valid.routes }] })
  for (const path of ['/base/list', '/shortcut/list', '/alternate/list']) assert.equal(router.resolve(path).name, 'Aliased')
  for (const path of ['shortcut/list', 'alternate/list']) {
    const direct = { path, name: 'Direct', component, meta: { pageId: 'other.list' } }
    const ambiguous = createRouter({ history: createMemoryHistory(), routes: [{ path: '/', children: [parent, direct] }] })
    assert.equal(ambiguous.resolve(`/${path}`).name, 'Aliased')
    assert.equal(ambiguous.resolve({ name: 'Direct' }).fullPath, `/${path}`)
    assert.throws(() => build([{ name: 'legacy', routes: [parent] }, { name: 'other', routes: [direct] }]), /Duplicate route path/)
  }
})

test('admin, granted, unknown and malformed providers share route/menu/default decisions', () => {
  const module = fixture()
  module.routes[0].meta.requiresAdmin = true
  const registry = build([module])
  const route = registry.routes[0]
  for (const provider of [undefined, {}, access(), access('example.list'), { isAdmin: 'true' }, { hasPageAccess: () => true }]) {
    assert.equal(canAccessRoute(route, provider), false)
    assert.deepEqual(accessibleNavigation(registry, provider), [])
    assert.equal(defaultAuthenticatedPath(registry, provider), '/login')
  }
  assert.equal(canAccessRoute(route, admin), true)
  assert.equal(defaultAuthenticatedPath(registry, admin), '/example/list')
  const ordinary = build([fixture()])
  for (const provider of [{ hasPageAccess: () => { throw Error('broken') } }, { hasPageAccess: () => 'yes' }, { isAdmin: true, isLoggedIn: false }]) {
    assert.equal(canAccessRoute(ordinary.routes[0], provider), false)
  }
  assert.equal(canAccessRoute(ordinary.routes[0], access('example.list')), true)
})

test('stable module/route sorting, two levels, invisible detail and empty group filtering', () => {
  const module = fixture('alpha', { order: 1 })
  module.routes.push({ path: 'alpha/detail/:id', name: 'Detail', component,
    meta: { pageId: 'alpha.detail', titleKey: 'alpha.title', navigation: { visible: false } } })
  const registry = build([fixture('zeta', { order: 1 }), module, fixture('first', { order: 0 })])
  assert.deepEqual(registry.activeModuleNames, ['first', 'alpha', 'zeta'])
  const menu = accessibleNavigation(registry, access('alpha.list', 'alpha.detail'))
  assert.deepEqual(menu.map(group => group.name), ['alpha'])
  assert.deepEqual(menu[0].children.map(leaf => leaf.name), ['alphaList'])
  assert.equal(defaultAuthenticatedPath(registry, access('alpha.detail')), '/login')
  assert.equal(resolveNavigationIcon('Known', { Known: 'icon' }, 'fallback'), 'icon')
  for (const hint of [undefined, 'unknown', '__proto__']) assert.equal(resolveNavigationIcon(hint, {}, 'fallback'), 'fallback')
})

test('duplicate module, route name, normalized path, pageId and namespaces fail explicitly', () => {
  assert.throws(() => build([fixture()], manifests => {
    manifests['other/app/example/manifest.js'] = { default: fixture() }
  }), /Duplicate module name/)
  for (const property of ['name', 'path']) {
    const second = fixture('other')
    second.routes[0][property] = fixture().routes[0][property]
    assert.throws(() => build([fixture(), second]), /Duplicate route/)
  }
  const second = fixture('other')
  second.routes[0].path = '/EXAMPLE/list/'
  assert.throws(() => build([fixture(), second]), /Duplicate route path/)
  second.routes[0].path = 'other/list'
  second.routes[0].meta.pageId = 'example.list'
  assert.throws(() => build([fixture(), second]), /Duplicate pageId/)
  assert.throws(() => build([fixture(), fixture('other')], (manifests, locales) => {
    locales['/app/other/locales/example.en-US.json'] = { title: 'Collision' }
  }), /Duplicate locale namespace/)
  assert.throws(() => build([fixture()], (manifests, locales) => {
    locales['/app/example/locales/breadcrumb.en-US.json'] = { title: 'Collision' }
  }), /Duplicate locale namespace/)
})

test('invalid schema, dynamic visible route and incomplete bilingual title fail', () => {
  const edits = [
    module => { module.enabled = 'false' },
    module => { module.order = NaN },
    module => { module.navigation = false },
    module => { module.navigation = {} },
    module => { module.navigation.children = [] },
    module => { module.routes[0].meta.navigation.visible = 'true' },
    module => { module.routes[0].meta.navigation.order = '1' },
    module => { module.routes[0].meta.requiresAdmin = 'false' },
    module => { module.routes[0].path += '/:id' },
    module => { module.navigation.titleKey = 'example.missing' },
    module => { module.routes[0].meta.titleKey = 'example.missing' }
  ]
  for (const edit of edits) { const module = fixture(); edit(module); assert.throws(() => build([module]), /module-registry/) }
  assert.throws(() => build([fixture()], (manifests, locales) => { delete locales['/app/example/locales/zh-CN.json'] }), /Missing bilingual locale/)
  assert.throws(() => build([fixture()], (manifests, locales) => { locales['/app/example/locales/zh-CN.json'] = {} }), /Bilingual key mismatch/)
})

test('actual source preserves Core route identity, shell locales and default-disabled demo', async () => {
  const root = fileURLToPath(new URL('../../', import.meta.url))
  const registry = await loadRegistry(root)
  assert.deepEqual(registry.activeModuleNames, ['dashboard', 'plan', 'system'])
  assert.deepEqual(registry.routes.map(route => [route.name, route.path, route.meta.pageId]), [
    ['Dashboard', 'dashboard/home', 'dashboard.home'],
    [undefined, 'dashboard', undefined],
    ['PlanList', 'plan/list', 'plan.list'],
    ['SystemUser', 'system/user', 'system.user'],
    ['SystemProjectionMapping', 'system/dict', 'system.projection-mapping']
  ])
  assert.equal(registry.modules.find(module => module.name === 'aiis_demo').enabled, false)
  for (const locale of ['en-US', 'zh-CN']) {
    for (const key of ['system.title', 'system.user', 'system.roles.admin', 'user.profile', 'user.logout']) {
      assert.equal(typeof resolveMessage(registry.messages[locale], key), 'string', `${locale}:${key}`)
    }
    assert.equal(registry.messages[locale].aiis_demo, undefined)
  }
  assert.equal(defaultAuthenticatedPath(registry, access('system.projection-mapping')), '/login')
  const demo = await readFile(new URL('../../src/app/aiis_demo/views/example/index.vue', import.meta.url), 'utf8')
  assert.doesNotMatch(demo, /fetch\(|axios|setInterval|WebSocket|https?:\/\//)
  for (const relative of ['src/layouts/MainLayout.vue', 'src/components/navigation/ModuleNavigation.vue']) {
    const source = await readFile(`${root}/${relative}`, 'utf8')
    for (const match of source.matchAll(/\b(?:\$t|t)\(['"]([^'"]+)['"]/g)) {
      for (const locale of ['en-US', 'zh-CN']) {
        assert.equal(typeof resolveMessage(registry.messages[locale], match[1]), 'string', `${relative}:${locale}:${match[1]}`)
      }
    }
  }
})
