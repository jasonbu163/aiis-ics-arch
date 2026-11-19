/** 验证计划/实绩页面和字段设置的实际 Vue setup。 */
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { parse, compileScript } from 'vue/compiler-sfc'
import * as vue from 'vue'
import { accessibleNavigation, canAccessRoute, createModuleRegistry } from '../../src/app/moduleManifest.js'
import { parseRolePageAccess } from '../../src/config/pageAccess.js'
import { planModule } from '../../src/app/plan/manifest.js'
import { performanceModule } from '../../src/app/performance/manifest.js'
import { useTableColumnWidths } from '../../src/utils/tableColumnWidths.js'

async function setupComponent(url) {
  const source = await readFile(new URL(url, import.meta.url), 'utf8')
  const { descriptor } = parse(source)
  const executable = compileScript(descriptor, { id: url }).content
    .replace(/^import\s+(.+?)\s+from\s+['"](.+?)['"];?$/gm, (_line, binding, module) => {
      if (binding.startsWith('{')) binding = binding.replace(/\bas\b/g, ':')
      return `const ${binding} = deps[${JSON.stringify(module)}]`
    }).replace('export default', 'return')
  return { make: new Function('deps', executable), template: descriptor.template.content }
}

const page = await setupComponent('../../src/app/plan/components/TaskPage.vue')
const localDialog = await setupComponent('../../src/app/plan/components/TaskConfigDialog.vue')
const editor = await setupComponent('../../src/app/plan/components/TaskFieldEditor.vue')
const sharedPage = await setupComponent('../../src/app/plan/views/shared-fields/index.vue')
const field = (scope, slotNo, name, extra = {}) => ({ scope, slotNo, name, type: 'number',
  labels: { 'zh-CN': name, 'en-US': name }, enabled: true, isNullable: true, planEditable: true,
  planVisible: true, performanceVisible: true, performanceOwner: 'automated', syncEnabled: true, ...extra })
const savedFields = [field('shared_sync', 3, 'feedback'), field('shared_sync', 4, 'hidden', { enabled: false }),
  field('performance_local', 2, 'manual', { performanceOwner: 'manual', performanceEditable: true }),
  field('plan_local', 2, 'planned')]
const details = { id: '1', taskNo: 'FIXTURE-1', productionStatus: 'running', targetKey: null, hasPlan: false,
  items: { feedback: 2, manual: null, planned: 0 } }
const config = { configVersion: 7, configRevision: '12', fields: savedFields }

function mount(component, kind, options = {}) {
  const hooks = [], calls = [], notices = [], local = new Map(), locale = vue.ref('en-US')
  const open = vue.ref(true)
  const events = []
  const api = {
    getConfig: async (...args) => { calls.push(['config', ...args]); return config },
    list: async params => { calls.push(['list', params]); return { items: [details], total: 1 } },
    detail: async () => details,
    upsert: async body => calls.push(['upsert', body]),
    upsertPlan: async body => calls.push(['upsertPlan', body]),
    saveConfig: async body => { calls.push(['saveConfig', body]); return config },
    deleteField: async body => { calls.push(['deleteField', body]); return { configVersion: 8, configRevision: '13' } },
    ...options.api
  }
  const role = options.role || 'admin'
  globalThis.localStorage = {
    getItem: key => local.get(key) ?? null,
    setItem: (key, value) => local.set(key, value),
    removeItem: key => local.delete(key)
  }
  const deps = { vue: { ...vue, onMounted: hook => hooks.push(hook), onBeforeUnmount() {}, useModel: () => open },
    'vue-i18n': { useI18n: () => ({ t: key => key, te: () => true, locale }) },
    'element-plus': { ElMessage: { error: message => notices.push(message), success() {} } },
    '@element-plus/icons-vue': { Setting: {}, QuestionFilled: {} },
    '@/store/user': { useUserStore: () => ({ role, isAdmin: role === 'admin', hasPageAccess: () => true, username: 'fixture' }) },
    '@/utils/tableColumnWidths': { useTableColumnWidths },
    './useTaskPagePadding': { useTaskPagePadding: () => ({ pageRoot: vue.ref(null), pagePadding: vue.ref(0) }) },
    '@/components/common/BaseCard.vue': {}, '@/components/common/ActionButton.vue': {}, './TaskConfigDialog.vue': {}
  }
  const effect = vue.effectScope()
  const state = effect.run(() => component.make(deps).setup({ kind, module: options.module ?? kind, api }, { expose() {}, emit: event => events.push(event) }))
  return { state, api, open, calls, notices, local, locale, events, start: async () => { for (const hook of hooks) await hook() },
    close: () => { effect.stop(); delete globalThis.localStorage } }
}

test('plans use current columns, distinct fields and a fixed production state', async () => {
  const p = mount(page, 'plan')
  try {
    await p.start()
    assert.ok(p.state.fixedColumns.value.includes('productionStatus'))
    assert.ok(!p.state.fixedColumns.value.includes('dispatchStatus'))
    assert.doesNotMatch(page.template, /sharedFieldSettings|sharedConfigOpen/)
    assert.match(page.template, /tr\('fieldSettings'\)/)
    assert.match(localDialog.template, /destroy-on-close/)
    assert.match(localDialog.template, /:kind="kind" :module="kind"/)
    assert.equal(p.state.fieldKey(savedFields[0]), 'shared_sync.feedback')
    assert.ok(!p.state.visibleFields.value.some(item => item.name === 'hidden'))
    assert.deepEqual(p.calls.filter(([key]) => key === 'config'), [['config', 'plan']])
    assert.equal(p.state.displayValue(0), '0')
    assert.equal(p.state.displayValue(false), 'plan.workflow.no')
    assert.equal(p.state.displayValue(null), '—')
    const firstWidths = p.state.columns.value
    firstWidths.onHeaderDragEnd(201, 150, { property: 'shared_sync.feedback' })
    await p.state.load()
    assert.equal(p.state.columns.value.widths['shared_sync.feedback'], 201)
    p.state.columns.value.reset()
    assert.equal(p.state.columns.value.widths['shared_sync.feedback'], 150)
  } finally { p.close() }
})

test('both pages preserve canonical +08:00 wall time from historical and current API records', () => {
  for (const kind of ['plan', 'performance']) {
    const p = mount(page, kind)
    try {
      const record = { createdAt: '1990-07-01T08:00:00.123456+08:00',
        updatedAt: '2026-11-18T10:01:02+08:00', lastObservedAt: '1990-01-01T08:00:00+08:00' }
      assert.equal(p.state.displayFixed(record, 'createdAt'), '1990-07-01 08:00:00')
      assert.equal(p.state.displayFixed(record, 'updatedAt'), '2026-11-18 10:01:02')
      assert.equal(p.state.displayFixed(record, 'lastObservedAt'), '1990-01-01 08:00:00')
      assert.equal(p.state.displayFixed({ createdAt: null }, 'createdAt'), '—')
    } finally { p.close() }
  }
})

test('plan edits submit only changed allowed values, including a shared feedback field', async () => {
  const p = mount(page, 'plan')
  try {
    await p.state.openDetail(details)
    assert.equal(p.state.fieldEditable(savedFields[0]), true)
    p.state.form.value.items.feedback = 0
    p.state.form.value.productionStatus = 'error'
    await p.state.save()
    assert.deepEqual(p.calls.find(([key]) => key === 'upsert')[1],
      { taskNo: 'FIXTURE-1', productionStatus: 'error', items: { feedback: 0 } })
    await p.state.newPlan()
    p.state.form.value.taskNo = 'NEW'
    assert.deepEqual(p.state.changedValues(), { taskNo: 'NEW' })
    assert.doesNotMatch(page.template, /runAction|dispatchStatus/)
  } finally { p.close() }
})

test('performance manual editing and optional backfill use the correct entry points', async () => {
  const p = mount(page, 'performance', { role: 'supervisor' })
  try {
    await p.state.openDetail(details)
    assert.equal(p.state.fieldEditable(savedFields[0]), false)
    p.state.form.value.items.manual = 0
    await p.state.save()
    assert.deepEqual(p.calls.find(([key]) => key === 'upsert')[1], { taskNo: 'FIXTURE-1', items: { manual: 0 } })
    await p.state.openDetail(details)
    p.state.startSupplement()
    p.state.form.value.backfillExisting = true
    await p.state.save()
    assert.deepEqual(p.calls.find(([key]) => key === 'upsertPlan')[1], { taskNo: 'FIXTURE-1', backfillExisting: true })
  } finally { p.close() }
})

test('each settings editor loads only its own group and the shared dialog has a single width preference scope', async () => {
  for (const [kind, scope] of [['plan','plan_local'], ['performance','performance_local'], ['shared','shared_sync']]) {
    const p = mount(editor, kind, { module: kind === 'shared' ? 'plan' : kind })
    try {
      await p.state.load()
      assert.ok(p.state.rows.value.length)
      assert.ok(p.state.rows.value.every(row => row.scope === scope))
      assert.deepEqual(p.calls[0], ['config', kind === 'shared' ? 'plan' : kind])
      const row = p.state.rows.value[0]
      await p.state.deleteSaved(row)
      assert.equal(p.calls.at(-1)[1].configRevision, '12')
      assert.equal(p.state.config.value.configRevision, '13')
      p.state.addRow()
      assert.equal(p.state.rows.value.at(-1).scope, scope)
      p.state.columns.onHeaderDragEnd(220, 150, { property: 'name' })
      assert.ok([...p.local.keys()].some(key => key.endsWith(`field-settings.${kind}`)))
    } finally { p.close() }
  }
})

test('resetting column widths and a stale revision preserve open edits until cancel', async () => {
  const p = mount(editor, 'shared', { module: 'plan', api: { saveConfig: async () => {
    throw { response: { data: { errorCode: 'task.config_revision_conflict' } } }
  } } })
  try {
    await p.state.load()
    p.state.rows.value[0].labels['en-US'] = 'unsaved'
    p.state.columns.reset()
    await p.state.save()
    assert.equal(p.state.conflict.value, true)
    assert.equal(p.state.rows.value[0].labels['en-US'], 'unsaved')
    assert.deepEqual(p.events, [])
    await p.state.cancel()
    assert.equal(p.state.conflict.value, false)
    assert.deepEqual(p.events, ['cancel'])
    assert.notEqual(p.state.rows.value[0].labels['en-US'], 'unsaved')
  } finally { p.close() }
})

test('current status and field setup texts resolve in both languages', async () => {
  for (const module of ['plan', 'performance']) {
    const locales = await Promise.all(['zh-CN', 'en-US'].map(async locale =>
      JSON.parse(await readFile(new URL(`../../src/app/${module}/locales/${locale}.json`, import.meta.url), 'utf8')).workflow))
    const leaves = (object, prefix = '') => Object.entries(object)
      .flatMap(([key, value]) => typeof value === 'string' ? [`${prefix}${key}`] : leaves(value, `${prefix}${key}.`)).sort()
    const [zh, en] = locales
    assert.deepEqual(leaves(zh), leaves(en))
    assert.deepEqual(Object.keys(en.statuses), ['new', 'running', 'completed', 'error'])
    const declaredKeys = [...(page.template + editor.template).matchAll(/tr\('([a-zA-Z.]+)'\)/g)].map(match => match[1])
    for (const key of declaredKeys) assert.ok(leaves(en).includes(key), `${module}.${key}`)
    assert.equal(zh.fieldSettings, '本地字段管理')
    assert.equal(zh.sharedFieldSettings, '共享字段管理')
    assert.equal(en.fieldSettings, 'Local Field Management')
    assert.equal(en.sharedFieldSettings, 'Shared Field Management')
  }
})

test('both module routes use a common administrator page and cannot be granted to other roles', async () => {
  const manifests = { '/app/plan/manifest.js': { planModule }, '/app/performance/manifest.js': { performanceModule } }
  const locales = {}
  for (const module of ['plan', 'performance']) {
    for (const locale of ['zh-CN', 'en-US']) {
      locales[`/app/${module}/locales/${locale}.json`] = JSON.parse(await readFile(
        new URL(`../../src/app/${module}/locales/${locale}.json`, import.meta.url), 'utf8'))
    }
  }
  const register = modules => createModuleRegistry(modules, locales, {}, { requiredModules: [] })
  const registry = register(manifests)
  const perModule = module => registry.routeRecords.find(route => route.meta.pageId === `${module}.shared-fields`)
  assert.equal(perModule('plan').component.toString(), perModule('performance').component.toString())
  assert.match(sharedPage.template, /:key="module" kind="shared" :module="module"/)
  assert.doesNotMatch(sharedPage.template, /el-dialog/)
  for (const module of ['plan', 'performance']) {
    const route = perModule(module)
    assert.equal(route.path, `/${module}/shared-fields`)
    assert.equal(route.props.module, module)
    assert.equal(route.meta.titleKey, `${module}.workflow.sharedFieldSettings`)
    assert.equal(route.meta.requiresAdmin, true)
    const navigation = accessibleNavigation(registry, { isAdmin: true, isLoggedIn: true })
    assert.ok(navigation.find(group => group.name === module).children.some(entry => entry.name === route.name))
    assert.equal(canAccessRoute(route, { isAdmin: true, isLoggedIn: false }), false)
    for (const role of ['supervisor', 'operator']) {
      const access = { isAdmin: false, isLoggedIn: true, role, hasPageAccess: () => true }
      assert.equal(canAccessRoute(route, access), false)
      assert.ok(!accessibleNavigation(registry, access).some(group => group.children.some(entry => entry.name === route.name)))
      const env = { VITE_SUPERVISOR_PAGE_ACCESS_JSON: '[]', VITE_OPERATOR_PAGE_ACCESS_JSON: '[]' }
      env[`VITE_${role.toUpperCase()}_PAGE_ACCESS_JSON`] = JSON.stringify([route.meta.pageId])
      assert.throws(() => parseRolePageAccess(env, registry), /admin-only pageId/)
    }
    const only = register({ [`/app/${module}/manifest.js`]: { default: module === 'plan' ? planModule : performanceModule },
      [`/app/${module === 'plan' ? 'performance' : 'plan'}/manifest.js`]: {
        default: { ...(module === 'plan' ? performanceModule : planModule), enabled: false } } })
    assert.equal(only.messages['zh-CN'][module].workflow.sharedFieldSettings, '共享字段管理')
    assert.equal(only.messages['zh-CN'][module === 'plan' ? 'performance' : 'plan'], undefined)
  }
})

test('switching shared route namespaces reads one saved definition and discards prior drafts', async () => {
  let saved = config
  const api = { getConfig: async () => saved, saveConfig: async body => {
    assert.equal(body.module, 'shared')
    assert.equal(body.configRevision, '12')
    assert.deepEqual(body.changes, [{ scope: 'shared_sync', slotNo: 3,
      labels: { 'zh-CN': 'feedback', 'en-US': 'Persisted' } }])
    saved = { ...config, configRevision: '13',
      fields: savedFields.map(row => row.name === 'feedback' ? { ...row, labels: body.changes[0].labels } : row) }
    return saved
  } }
  const plan = mount(editor, 'shared', { module: 'plan', api })
  try {
    await plan.state.load()
    assert.equal(plan.state.tr('owner'), 'plan.workflow.owner')
    plan.state.rows.value[0].labels['en-US'] = 'Persisted'
    await plan.state.save()
    assert.equal(plan.state.config.value.configRevision, '13')
    plan.state.rows.value[0].labels['en-US'] = 'Uncommitted'
  } finally { plan.close() }
  const performance = mount(editor, 'shared', { module: 'performance', api })
  try {
    await performance.state.load()
    assert.equal(performance.state.tr('owner'), 'performance.workflow.owner')
    assert.equal(performance.state.rows.value[0].labels['en-US'], 'Persisted')
    assert.equal(performance.state.config.value.configRevision, '13')
    assert.ok(performance.state.rows.value.every(field => field.scope === 'shared_sync'))
  } finally { performance.close() }
})
