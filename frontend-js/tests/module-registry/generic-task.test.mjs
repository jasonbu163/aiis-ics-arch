/** 验证计划/实绩页面和字段设置的实际 Vue setup。 */
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { parse, compileScript } from 'vue/compiler-sfc'
import * as vue from 'vue'
import { accessibleNavigation, canAccessRoute, createModuleRegistry, defaultAuthenticatedPath } from '../../src/app/moduleManifest.js'
import { parseRolePageAccess } from '../../src/config/pageAccess.js'
import { planModule } from '../../src/app/plan/manifest.js'
import { performanceModule } from '../../src/app/performance/manifest.js'
import { useTableColumnWidths } from '../../src/utils/tableColumnWidths.js'
import * as fieldSettings from '../../src/app/plan/components/fieldSettings.js'

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
const localPage = await setupComponent('../../src/app/plan/views/local-fields/index.vue')
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
  const hooks = [], unmountHooks = [], leaveHooks = [], calls = [], notices = [], local = options.local ?? new Map(), locale = vue.ref(options.locale ?? 'en-US')
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
  const deps = { vue: { ...vue, onMounted: hook => hooks.push(hook), onBeforeUnmount: hook => unmountHooks.push(hook), useModel: () => open },
    'vue-i18n': { useI18n: () => ({ t: options.t ?? (key => key), te: options.te ?? (() => true), locale }) },
    'vue-router': { onBeforeRouteLeave: hook => leaveHooks.push(hook), useRouter: () => ({ push: path => calls.push(['navigate', path]) }) },
    'element-plus': { ElMessage: { error: message => notices.push(message), success: message => notices.push(message), warning() {}, info: message => notices.push(message) } },
    '@element-plus/icons-vue': { Setting: {}, QuestionFilled: {} },
    '@/store/user': { useUserStore: () => ({ role, isAdmin: role === 'admin', hasPageAccess: () => options.planAccess ?? true, username: 'fixture' }) },
    '@/utils/tableColumnWidths': { useTableColumnWidths },
    './useTaskPagePadding': { useTaskPagePadding: () => ({ pageRoot: vue.ref(null), pagePadding: vue.ref(0) }) },
    '../../components/useTaskPagePadding': { useTaskPagePadding: () => ({ pageRoot: vue.ref(null), pagePadding: vue.ref(0) }) },
    '../../api': api, '../../components/TaskFieldEditor.vue': {}, './SharedFieldForm.vue': {},
    '../../components/fieldSettings': fieldSettings, './fieldSettings': fieldSettings,
    '@/components/common/BaseCard.vue': {}, '@/components/common/ActionButton.vue': {}
  }
  const effect = vue.effectScope()
  const state = effect.run(() => component.make(deps).setup({ kind, module: options.module ?? kind, scope: options.scope, api },
    { expose() {}, emit: event => events.push(event) }))
  return { state, api, open, calls, notices, local, locale, events, start: async () => { for (const hook of hooks) await hook() },
    leave: () => leaveHooks.forEach(hook => hook()),
    close: () => { unmountHooks.forEach(hook => hook()); effect.stop(); delete globalThis.localStorage } }
}

test('plans use current columns, distinct fields and a fixed production state', async () => {
  const p = mount(page, 'plan')
  try {
    await p.start()
    assert.ok(p.state.fixedColumns.value.includes('productionStatus'))
    assert.ok(!p.state.fixedColumns.value.includes('dispatchStatus'))
    assert.doesNotMatch(page.template, /sharedFieldSettings|sharedConfigOpen/)
    assert.doesNotMatch(page.template, /fieldSettings|local-fields/)
    assert.doesNotMatch(page.template, /TaskConfigDialog/)
    assert.match(localPage.template, /<FieldManagement/)
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
    await p.state.openDetail(details, 'edit')
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
    await p.state.openDetail(details, 'edit')
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
    const declaredKeys = [...(page.template + editor.template + sharedPage.template).matchAll(/tr\('([a-zA-Z.]*[a-zA-Z])'(?=[,)])/g)].map(match => match[1])
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
  const admin = { isAdmin: true, isLoggedIn: true }
  assert.equal(defaultAuthenticatedPath(registry, admin), '/plan/list')
  const perModule = module => registry.routeRecords.find(route => route.meta.pageId === `${module}.shared-fields`)
  assert.equal(perModule('plan').component.toString(), perModule('performance').component.toString())
  assert.match(sharedPage.template, /:kind="settingsKind" :module="module" :draft-rows="draftRows"/)
  assert.match(sharedPage.template, /el-dialog/)
  for (const module of ['plan', 'performance']) {
    const route = perModule(module)
    assert.equal(route.path, `/${module}/shared-fields`)
    assert.equal(route.props.module, module)
    assert.equal(route.meta.titleKey, `${module}.workflow.sharedFieldSettings`)
    assert.equal(route.meta.requiresAdmin, true)
    const localRoute = registry.routeRecords.find(route => route.meta.pageId === `${module}.local-fields`)
    assert.equal(localRoute.path, `/${module}/local-fields`)
    assert.equal(localRoute.props.module, module)
    assert.equal(localRoute.meta.titleKey, `${module}.workflow.fieldSettings`)
    assert.deepEqual(localRoute.meta.navigation, { visible: true, order: 15, icon: 'Setting' })
    assert.equal(localRoute.meta.requiresAdmin, true)
    assert.equal(canAccessRoute(localRoute, admin), true)
    assert.equal(canAccessRoute(localRoute, { isAdmin: true, isLoggedIn: false }), false)
    assert.equal(canAccessRoute(localRoute, { isAdmin: false }), false)
    const navigation = accessibleNavigation(registry, admin)
    assert.deepEqual(navigation.find(group => group.name === module).children.map(entry => entry.path), [
      `/${module}/list`, localRoute.path, route.path
    ])
    assert.equal(canAccessRoute(route, { isAdmin: true, isLoggedIn: false }), false)
    for (const role of ['supervisor', 'operator', 'unknown']) {
      const access = { isAdmin: false, isLoggedIn: true, role, hasPageAccess: () => true }
      assert.equal(canAccessRoute(route, access), false)
      assert.equal(canAccessRoute(localRoute, access), false)
      assert.deepEqual(accessibleNavigation(registry, access).find(group => group.name === module).children.map(entry => entry.path), [
        `/${module}/list`
      ])
      if (role !== 'unknown') {
        const env = { VITE_SUPERVISOR_PAGE_ACCESS_JSON: '[]', VITE_OPERATOR_PAGE_ACCESS_JSON: '[]' }
        env[`VITE_${role.toUpperCase()}_PAGE_ACCESS_JSON`] = JSON.stringify([route.meta.pageId])
        assert.throws(() => parseRolePageAccess(env, registry), /admin-only pageId/)
      }
    }
    const only = register({ [`/app/${module}/manifest.js`]: { default: module === 'plan' ? planModule : performanceModule },
      [`/app/${module === 'plan' ? 'performance' : 'plan'}/manifest.js`]: {
        default: { ...(module === 'plan' ? performanceModule : planModule), enabled: false } } })
    assert.equal(only.messages['zh-CN'][module].workflow.sharedFieldSettings, '共享字段管理')
    assert.equal(defaultAuthenticatedPath(only, admin), `/${module}/list`)
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

const sharedFixture = Array.from({ length: 25 }, (_, index) => {
  const slot = index + 1
  return field('shared_sync', slot, 'field' + slot, { labels: { 'zh-CN': '字段' + slot, 'en-US': 'Field ' + slot },
    unit: null, planOrder: slot === 1 ? 1 : null, performanceOrder: null, performanceEditable: false, enabled: slot !== 22 })
})

test('shared field filtering, pagination, selection and refresh use the current revision', async () => {
  let response = { configVersion: 7, configRevision: '12', fields: [...sharedFixture.toReversed(), savedFields[2]] }
  let fail = false
  const p = mount(sharedPage, 'performance', { api: { getConfig: async module => {
    assert.equal(module, 'performance')
    if (fail) throw new Error('unavailable')
    return response
  } } })
  try {
    await p.start()
    assert.equal(p.state.pageSize.value, 20)
    assert.equal(p.state.pageRows.value.length, 20)
    assert.equal(p.state.pageRows.value[0].slotNo, 1)
    p.state.selectPage(true)
    p.state.page.value = 2
    p.state.selectRow(p.state.pageRows.value[0], true)
    assert.equal(p.state.selections.value.size, 21)
    p.state.pageSize.value = 50
    await vue.nextTick()
    assert.equal(p.state.page.value, 1)
    assert.equal(p.state.selections.value.size, 21)
    await p.state.load()
    assert.equal(p.state.selections.value.size, 21)
    fail = true
    await p.state.load()
    assert.equal(p.state.loadError.value, true)
    assert.equal(p.state.selections.value.size, 21)
    fail = false
    response = { ...response, configRevision: '13' }
    await p.state.load()
    assert.equal(p.state.selections.value.size, 0)
    assert.equal(p.state.loadError.value, false)
    p.state.filters.keyword = 'FIELD 22'
    p.state.filters.enabled = 'disabled'
    p.state.filters.owner = 'automated'
    p.state.search()
    assert.deepEqual(p.state.pageRows.value.map(row => row.slotNo), [22])
    p.state.selectPage(true)
    p.state.resetFilters()
    assert.equal(p.state.filtered.value.length, 25)
    assert.equal(p.state.selections.value.size, 0)
  } finally { p.close() }
})

test('shared edit submits actual changes only, preserves null and never overwrites an uncertain draft', async () => {
  let authoritative = { configVersion: 7, configRevision: '12', fields: sharedFixture }
  const payloads = []
  const p = mount(sharedPage, 'plan', { api: {
    getConfig: async () => authoritative,
    saveConfig: async body => {
      payloads.push(body)
      if (payloads.length === 1) throw { response: { data: { errorCode: 'task.config_revision_conflict' } } }
      if (payloads.length === 2) {
        authoritative = { ...authoritative, configRevision: '13', fields: [
          { ...sharedFixture[0], planOrder: null }, ...sharedFixture.slice(1)
        ] }
        throw { response: { data: { errorCode: 'task.commit_unknown' } } }
      }
      return authoritative
    }
  } })
  try {
    await p.start()
    p.state.openEdit('batch', [p.state.fields.value[0], p.state.fields.value[24]])
    p.state.draftRows.value[0].planOrder = null
    await p.state.save()
    assert.deepEqual(payloads[0], { module:'shared', configRevision:'12', changes:[{scope:'shared_sync',slotNo:1,planOrder:null}] })
    assert.equal(p.state.editOpen.value, true)
    assert.equal(p.state.draftRows.value[0].planOrder, null)
    await p.state.save()
    assert.equal(payloads.length, 1)
    p.state.openEdit('single', [p.state.fields.value[0]])
    p.state.draftRows.value[0].planOrder = null
    await p.state.save()
    assert.equal(p.state.reconciliation.value[0].status, 'shared.matches')
    assert.equal(p.state.editOpen.value, true)
    assert.equal(p.state.config.value.configRevision, '13')
    await p.state.save()
    assert.equal(payloads.length, 2)
    p.state.addField()
    assert.equal(p.state.draftRows.value[0].slotNo, 26)
    p.state.draftRows.value[0].name = 'newField'
    p.state.draftRows.value[0].labels = { 'zh-CN': '新字段', 'en-US': 'New field' }
    await p.state.save()
    assert.equal(payloads[2].changes[0].name, 'newField')
    assert.equal(p.state.editOpen.value, false)
  } finally { p.close() }
})

test('shared deletion requires confirmation, localizes the first obstruction, and reconciles unknown results', async () => {
  let authoritative = { configVersion: 7, configRevision: '12', fields: sharedFixture }
  const submissions = []
  const p = mount(sharedPage, 'performance', { api: {
    getConfig: async () => authoritative,
    deleteSharedFields: async body => {
      submissions.push(['batch', body])
      if (submissions.length === 1) throw { response: { data: { errorCode: 'task.field_in_use',
        details: { field:'fields.1.name', reason:'referenced_by_task_or_dispatch' } } } }
      authoritative = { configVersion: 8, configRevision: '13', fields: sharedFixture.filter(row => row.slotNo !== 1 && row.slotNo !== 25) }
      throw new Error('dropped response')
    },
    deleteField: async body => {
      submissions.push(['single', body])
      return { ...body, configVersion: 9, configRevision: '14' }
    }
  } })
  try {
    await p.start()
    p.state.selectRow(p.state.fields.value[0], true)
    p.state.selectRow(p.state.fields.value[24], true)
    p.state.openDelete('batch', p.state.selectedRows.value)
    assert.equal(submissions.length, 0)
    await p.state.confirmDelete()
    assert.equal(p.state.selections.value.size, 2)
    assert.match(p.state.message.value, /referenced_by_task_or_dispatch/)
    assert.equal(p.state.deleteOpen.value, true)
    await p.state.confirmDelete()
    assert.equal(submissions.length, 1)
    p.state.openDelete('batch', p.state.selectedRows.value)
    await p.state.confirmDelete()
    assert.deepEqual(submissions[1][1].fields.map(row => row.slotNo), [1,25])
    assert.deepEqual(p.state.reconciliation.value.map(row => row.status), ['shared.absent','shared.absent'])
    await p.state.confirmDelete()
    assert.equal(submissions.length, 2)
    p.state.openDelete('single', [p.state.fields.value[0]])
    await p.state.confirmDelete()
    assert.equal(submissions[2][0], 'single')
    assert.equal(submissions[2][1].configRevision, '13')
    assert.equal(p.state.fields.value[0].slotNo, 3)
  } finally { p.close() }
})

test('new shared field rejects any occupied shared slot before PUT, without blocking valid additions or edits', async () => {
  for (const module of ['plan', 'performance']) {
    const existing = sharedFixture[21]
    const configBefore = { configVersion: 7, configRevision: '12', fields: [existing, savedFields[2], savedFields[3]] }
    const payloads = []
    const p = mount(sharedPage, module, { te: key => key.endsWith('.errors.config_revision_conflict'), api: {
      getConfig: async () => configBefore,
      saveConfig: async body => {
        payloads.push(body)
        if (body.changes[0].slotNo === 3) throw { response: { data: { errorCode: 'task.config_revision_conflict' } } }
        return { ...configBefore, configVersion: 8, configRevision: '13',
          fields: [...configBefore.fields, ...body.changes.filter(row => row.slotNo !== existing.slotNo)] }
      }
    } })
    try {
      await p.start()
      const state = p.state
      state.addField()
      const draft = state.draftRows.value[0]
      draft.slotNo = existing.slotNo
      draft.type = existing.type
      draft.unit = existing.unit
      draft.labels = { 'zh-CN': '新的名称', 'en-US': 'New names' }
      for (const name of [existing.name, 'differentKey']) {
        draft.name = name
        await state.save()
        assert.equal(payloads.length, 0)
        assert.equal(state.message.value, module + '.workflow.shared.slotOccupied')
        assert.equal(state.editOpen.value, true)
        assert.deepEqual(state.draftRows.value[0].labels, { 'zh-CN': '新的名称', 'en-US': 'New names' })
        assert.deepEqual(state.config.value, configBefore)
      }

      draft.slotNo = 2 // This slot is occupied only in the independent local groups.
      await state.save()
      assert.equal(payloads.length, 1)
      assert.equal(payloads[0].changes[0].slotNo, 2)
      assert.equal(payloads[0].changes[0].name, 'differentKey')
      assert.equal(state.editOpen.value, false)

      state.openEdit('single', [state.fields.value.find(row => row.slotNo === existing.slotNo)])
      state.draftRows.value[0].labels['en-US'] = 'Edited name'
      await state.save()
      assert.deepEqual(payloads[1], { module: 'shared', configRevision: '13',
        changes: [{ scope: 'shared_sync', slotNo: existing.slotNo, labels: { ...existing.labels, 'en-US': 'Edited name' } }] })

      state.addField()
      Object.assign(state.draftRows.value[0], { slotNo: 3, name: 'concurrentField', labels: { 'zh-CN': '并发字段', 'en-US': 'Concurrent field' } })
      await state.save()
      assert.equal(payloads.length, 3)
      assert.equal(payloads[2].configRevision, '13')
      assert.equal(state.blocked.value, true)
      assert.equal(state.editOpen.value, true)
      assert.equal(state.draftRows.value[0].name, 'concurrentField')
      assert.equal(state.message.value, module + '.workflow.errors.config_revision_conflict')
    } finally { p.close() }
  }
})

test('local management isolates lists, drafts, versioned actions and column widths by module', async () => {
  const storage = new Map()
  for (const module of ['plan', 'performance']) {
    const scope = module + '_local'
    const localFields = Array.from({ length: 25 }, (_, index) =>
      field(scope, index + 1, 'local' + (index + 1), { enabled: index !== 23 }))
    const otherScope = module === 'plan' ? 'performance_local' : 'plan_local'
    const allFields = [...localFields, field(otherScope, 26, 'sameSlot'), ...savedFields.slice(0, 2)]
    let revision = '12'
    let failRead = false
    const writes = []
    const p = mount(sharedPage, module, { scope, local: storage, api: {
      getConfig: async requested => {
        assert.equal(requested, module)
        if (failRead) throw Error('read failed')
        return { ...config, configRevision: revision, fields: allFields }
      },
      saveConfig: async body => {
        writes.push(['save', body])
        if (revision === '13') throw { response: { data: { errorCode: 'task.commit_unknown' } } }
        for (const row of body.changes) {
          const existing = allFields.find(item => item.scope === row.scope && item.slotNo === row.slotNo)
          if (existing) Object.assign(existing, row)
          else allFields.push(row)
        }
        revision = '13'
        return { ...config, configRevision: revision, fields: allFields }
      },
      deleteLocalFields: async body => {
        writes.push(['delete', body])
        if (revision === '13') { failRead = true; throw Error('response lost') }
        return { configVersion: 8, configRevision: '15', deleted: body.fields }
      }
    } })
    try {
      await p.start()
      const state = p.state
      assert.deepEqual(state.settings.owners, module === 'plan' ? [] : ['automated', 'manual'])
      assert.equal(state.settings.switches.includes('syncEnabled'), false)
      assert.equal(state.fields.value.length, 25)
      assert.equal(state.pageRows.value.length, 20)
      state.selectRow(state.pageRows.value[0], true)
      state.page.value = 2
      state.selectRow(state.pageRows.value[0], true)
      assert.deepEqual(state.selectedRows.value.map(row => row.slotNo), [1, 21])
      state.filters.keyword = 'LoCaL1'
      state.search()
      assert.equal(state.page.value, 1)
      assert.equal(state.selectedRows.value.length, 0)
      assert.ok(!state.filtered.value.some(row => row.slotNo === 24))
      assert.equal(state.columns.widths.name, 190)
      state.columns.onHeaderDragEnd(201, 190, { property: 'name' })
      state.addField()
      const draft = state.draftRows.value[0]
      draft.slotNo = 24
      draft.labels = { 'zh-CN': '名称', 'en-US': 'Label' }
      for (const name of ['local24', 'newField']) {
        draft.name = name
        await state.save()
        assert.equal(writes.length, 0)
        assert.equal(state.editOpen.value, true)
        assert.match(state.message.value, /slotOccupied/)
      }
      draft.slotNo = 26
      await state.save()
      const [saveAction, saveBody] = writes[0]
      assert.equal(saveAction, 'save')
      assert.equal(saveBody.module, module)
      assert.equal(saveBody.changes[0].scope, scope)
      assert.ok(!('syncEnabled' in saveBody.changes[0]))
      assert.ok(!((module === 'plan' ? 'performanceVisible' : 'planVisible') in saveBody.changes[0]))
      assert.equal(state.editOpen.value, false)
      state.openEdit('batch', [state.fields.value[1], state.fields.value[20]])
      state.draftRows.value[1].labels['en-US'] = 'Changed'
      await state.save()
      assert.equal(writes[1][1].changes.length, 1)
      assert.equal(writes[1][1].changes[0].scope, scope)
      assert.equal(state.reconciliation.value[0].status, 'shared.differs')
      assert.equal(state.draftRows.value[1].labels['en-US'], 'Changed')
      state.openDelete('batch', [state.fields.value[0], state.fields.value[20]])
      await state.confirmDelete()
      assert.deepEqual(writes[2], ['delete', { module, configRevision: '13',
        fields: [{scope, slotNo: 1, name: 'local1'}, {scope, slotNo: 21, name: 'local21'}] }])
      assert.match(state.message.value, /unknownRefreshFailed/)
      assert.equal(state.blocked.value, true)
      failRead = false
      await state.retryReconciliation()
      assert.equal(writes.length, 3)
      assert.deepEqual(state.reconciliation.value.map(item => item.status), ['shared.present', 'shared.present'])
    } finally { p.close() }
  }
  assert.ok([...storage.keys()].some(key => key.endsWith('generic-task.local-fields.plan')))
  assert.ok([...storage.keys()].some(key => key.endsWith('generic-task.local-fields.performance')))
})

test('local field saves explain duplicate and reserved keys in each locale and retain the draft', async () => {
  for (const module of ['plan', 'performance']) {
    for (const locale of ['zh-CN', 'en-US']) {
      const catalogs = { [module]: JSON.parse(await readFile(
        new URL(`../../src/app/${module}/locales/${locale}.json`, import.meta.url), 'utf8')) }
      const lookup = key => key.split('.').reduce((part, name) => part?.[name], catalogs)
      const payloads = []
      const p = mount(sharedPage, module, { scope: module + '_local', locale, t: lookup,
        te: key => typeof lookup(key) === 'string', api: {
          saveConfig: async payload => {
            payloads.push(payload)
            const key = payload.changes[0].name
            if (key === 'correctedKey') return { ...config, configRevision: '13' }
            throw { response: { status: 422, data: { errorCode: 'task.invalid_request',
              details: { field: 'changes.name', reason: key === 'productionStatus' ? 'invalid_field_name' : 'duplicate_field_name' } } } }
          }
        } })
      try {
        await p.start()
        const state = p.state
        state.addField()
        const draft = state.draftRows.value[0]
        const labels = { 'zh-CN': '保留草稿', 'en-US': 'Keep the draft' }
        draft.labels = { ...labels }
        for (const [name, pattern] of [
          ['feedback', locale === 'zh-CN' ? /本地字段和共享字段都不重名/ : /does not match a local or shared field/],
          ['productionStatus', locale === 'zh-CN' ? /系统保留键或格式无效/ : /reserved or invalid/]
        ]) {
          draft.name = name
          await state.save()
          assert.match(state.message.value, pattern)
          assert.equal(state.editOpen.value, true)
          assert.equal(state.blocked.value, false)
          assert.equal(state.draftRows.value[0].name, name)
          assert.deepEqual(state.draftRows.value[0].labels, labels)
          assert.equal(state.config.value.configRevision, '12')
        }
        draft.name = 'correctedKey'
        await state.save()
        assert.equal(payloads.length, 3)
        assert.equal(payloads[2].configRevision, '12')
        assert.equal(state.editOpen.value, false)
        assert.equal(state.config.value.configRevision, '13')
      } finally { p.close() }
    }
  }
})

function deferred() {
  let resolve, reject
  const promise = new Promise((ok, fail) => { resolve = ok; reject = fail })
  return { promise, resolve, reject }
}

const older = { ...details, id: 'A', taskNo: 'PLAN-A' }
const newer = { ...details, id: 'B', taskNo: 'PLAN-B', hasPlan: true }
const olderConfig = { ...config, fields: [field('shared_sync', 1, 'aOnly')] }
const newerConfig = { ...config, fields: [field('shared_sync', 2, 'bOnly')] }
const missingTask = { response: { data: { errorCode: 'task.not_found' } } }

test('detail and edit own their record and config across switches, and retry in the same mode', async () => {
  for (const kind of ['plan', 'performance']) {
    for (const slow of ['record', 'config']) {
      for (const fail of [false, true]) {
        const stale = deferred(), current = deferred()
        let configCount = 0, detailCount = 0
        const p = mount(page, kind, { api: {
          detail: id => id === 'A' ? slow === 'record' ? stale.promise : older
            : ++detailCount === 1 ? current.promise : newer,
          getConfig: () => ++configCount === 1 ? slow === 'config' ? stale.promise : olderConfig : newerConfig
        } })
        try {
          const first = p.state.openDetail(older, fail ? 'view' : 'edit')
          const activeMode = fail ? 'edit' : 'view'
          const second = p.state.openDetail(newer, activeMode)
          assert.equal(p.state.detailTarget.value.taskNo, newer.taskNo)
          assert.equal(p.state.detailOpen.value, true)
          assert.equal(p.state.record.value, null)
          assert.equal(p.state.canEditRemark.value, false)
          assert.equal(p.state.detailLoading.value, true)
          current.resolve(newer)
          await second
          if (fail) stale.reject(missingTask)
          else stale.resolve(slow === 'record' ? older : olderConfig)
          await first
          assert.equal(p.state.record.value.taskNo, newer.taskNo)
          assert.equal(p.state.mode.value, activeMode)
          assert.deepEqual(p.state.formFields.value.map(row => row.name), ['bOnly'])
          assert.equal(p.state.detailLoading.value, false)
          assert.equal(p.state.detailError.value, '')
          assert.deepEqual(p.notices, [])
        } finally { p.close() }
      }
      const failure = deferred()
      let request = 0
      const p = mount(page, kind, { api: {
        detail: id => id === 'A' ? { ...older, hasPlan: true } : slow === 'record' && request++ === 0 ? failure.promise : newer,
        getConfig: () => slow === 'config' && request++ === 1 ? failure.promise : newerConfig
      } })
      try {
        await p.state.openDetail({ ...older, hasPlan: true })
        const activeMode = slow === 'record' ? 'edit' : 'view'
        const second = p.state.openDetail(newer, activeMode)
        failure.reject(missingTask)
        await second
        assert.equal(p.state.detailOpen.value, true)
        assert.equal(p.state.detailLoading.value, false)
        assert.equal(p.state.record.value, null)
        assert.ok(p.state.detailError.value)
        assert.equal(p.state.canEditRemark.value, false)
        await p.state.openDetail(p.state.detailTarget.value, p.state.mode.value)
        assert.equal(p.state.record.value.taskNo, newer.taskNo)
        assert.equal(p.state.mode.value, activeMode)
        assert.equal(p.state.detailError.value, '')
      } finally { p.close() }
    }
  }
})

test('optional supplement config follows the active performance and access permissions', async () => {
  for (const failStale of [false, true]) {
    for (const currentState of ['has-plan', 'ready', 'failed']) {
      const stale = deferred(), current = deferred()
      const active = { ...newer, hasPlan: currentState === 'has-plan' }
      let supplementRequests = 0
      const p = mount(page, 'performance', { api: {
        detail: id => id === 'A' ? older : active,
        getConfig: kind => kind === 'plan' ? (++supplementRequests === 1 ? stale.promise : current.promise) : config
      } })
      try {
        const first = p.state.openDetail(older)
        await Promise.resolve()
        await Promise.resolve()
        assert.equal(p.state.record.value.taskNo, older.taskNo)
        assert.equal(Boolean(p.state.canSupplement.value), false)
        const second = p.state.openDetail(active)
        await Promise.resolve()
        await Promise.resolve()
        assert.equal(p.state.record.value.taskNo, newer.taskNo)
        assert.equal(Boolean(p.state.canSupplement.value), false)
        if (currentState === 'ready') current.resolve(newerConfig)
        if (currentState === 'failed') current.reject(missingTask)
        await second
        if (failStale) stale.reject(missingTask)
        else stale.resolve(olderConfig)
        await first
        assert.equal(Boolean(p.state.canSupplement.value), currentState === 'ready')
        assert.equal(p.state.detailError.value, '')
        if (currentState === 'ready') {
          p.state.startSupplement()
          assert.deepEqual(p.state.formFields.value.map(row => row.name), ['bOnly'])
          assert.equal(p.state.form.value.backfillExisting, false)
          p.state.cancelEdit()
          assert.equal(p.state.mode.value, 'view')
          assert.equal(p.state.record.value.taskNo, newer.taskNo)
        }
      } finally { p.close() }
    }
  }
  for (const permissions of [{ role: 'operator' }, { role: 'supervisor', planAccess: false }, { role: 'viewer' }]) {
    const p = mount(page, 'performance', { ...permissions, api: { getConfig: async kind => {
      assert.equal(kind, 'performance')
      return config
    } } })
    try {
      await p.state.openDetail(older)
      assert.equal(Boolean(p.state.canSupplement.value), false)
      assert.equal(p.state.canEditRemark.value, permissions.role !== 'viewer')
    } finally { p.close() }
  }
})

test('close, route leave, unmount and switching new plan invalidate earlier dialog work', async () => {
  assert.doesNotMatch(page.template, /@closed=|v-model="detailOpen"|@update:model-value=/)
  assert.match(page.template, /:before-close="closeDetail"/)
  for (const next of ['close', 'leave', 'unmount', 'reopen', 'new', 'detail']) {
    for (const fail of [false, true]) {
      const previous = deferred()
      let configCount = 0
      const p = mount(page, 'plan', { api: {
        getConfig: () => next === 'detail' && ++configCount === 1 ? previous.promise : config,
        detail: id => id === 'A' ? previous.promise : newer
      } })
      try {
        const first = next === 'detail' ? p.state.newPlan() : p.state.openDetail(older)
        if (next === 'close') p.state.closeDetail()
        if (next === 'leave') p.leave()
        if (next === 'unmount') p.close()
        if (next === 'reopen') { p.state.closeDetail(); await p.state.openDetail(newer) }
        if (next === 'new') await p.state.newPlan()
        if (next === 'detail') await p.state.openDetail(newer)
        if (fail) previous.reject(missingTask)
        else previous.resolve(next === 'detail' ? olderConfig : older)
        await first
        assert.equal(p.state.detailOpen.value, ['reopen', 'new', 'detail'].includes(next))
        assert.equal(p.state.record.value?.taskNo, ['reopen', 'detail'].includes(next) ? newer.taskNo : undefined)
        assert.equal(p.state.mode.value, next === 'new' ? 'new' : 'view')
        assert.deepEqual(p.notices, [])
        assert.equal(p.state.detailError.value, '')
      } finally { p.close() }
    }
  }
})

test('save owns its draft, pending flag, errors and refresh in both modules', async () => {
  for (const kind of ['plan', 'performance']) {
    for (const result of ['stale-success', 'stale-failure', 'left-success', 'left-failure', 'current-failure', 'current-success']) {
      const saving = deferred(), current = deferred()
      const writes = []
      const p = mount(page, kind, { api: {
        detail: id => id === 'A' ? { ...older, hasPlan: true } : current.promise,
        upsert: body => { writes.push(body); return saving.promise }
      } })
      try {
        await p.state.openDetail(older, 'edit')
        p.state.form.value.remark = 'canceled'
        p.state.cancelEdit()
        assert.deepEqual(writes, [])
        assert.equal(p.state.detailOpen.value, false)
        await p.state.openDetail(older, 'edit')
        assert.equal(p.state.form.value.remark, null)
        p.state.form.value.remark = 'owned edit'
        const save = p.state.save()
        await p.state.save()
        assert.deepEqual(writes, [{ taskNo: older.taskNo, remark: 'owned edit' }])
        assert.equal(p.state.saving.value, true)
        const next = result.startsWith('stale') ? p.state.openDetail(newer) : null
        if (result.startsWith('left')) p.leave()
        if (result.endsWith('failure')) saving.reject(missingTask)
        else saving.resolve({})
        await save
        assert.equal(p.state.saving.value, false)
        if (next) {
          assert.equal(p.state.detailLoading.value, true)
          current.resolve(newer)
          await next
          assert.equal(p.state.record.value.taskNo, newer.taskNo)
          assert.equal(p.state.saveError.value, '')
        }
        const success = result === 'current-success'
        const retained = result === 'current-failure'
        assert.equal(p.state.detailOpen.value, Boolean(next) || retained)
        assert.equal(p.calls.filter(([key]) => key === 'list').length, Number(success))
        assert.deepEqual(p.notices, success ? [kind + '.workflow.saved'] : [])
        if (retained) {
          assert.equal(p.state.form.value.remark, 'owned edit')
          assert.ok(p.state.saveError.value)
        }
      } finally { p.close() }
    }
  }
})

test('detail edit keeps existing target locks, roles and authorized nullable or falsy values', async () => {
  for (const kind of ['plan', 'performance']) {
    for (const role of ['admin', 'supervisor', 'operator', 'viewer']) {
      for (const targetKey of ['locked-target', null]) {
        const businessFields = [
          field('shared_sync', 1, 'manual', { performanceOwner: 'manual', performanceEditable: true, isNullable: false }),
          field('shared_sync', 2, 'flag', { performanceOwner: 'manual', performanceEditable: true, type: 'boolean' }),
          field('shared_sync', 3, 'auto', { performanceOwner: 'automated', performanceEditable: true }),
          field('shared_sync', 4, 'readOnly', { planEditable: false, performanceEditable: false })
        ]
        const row = { ...newer, targetKey, items: { manual: 2, flag: true, auto: 1, readOnly: 1 } }
        const p = mount(page, kind, { role, api: {
          detail: async () => row,
          getConfig: async () => ({ ...config, fields: businessFields })
        } })
        try {
          await p.state.openDetail(row, 'edit')
          const canEdit = role !== 'viewer' && (kind === 'performance' || role !== 'operator')
          assert.equal(p.state.canEditRecord.value, canEdit)
          assert.equal(p.state.detailOpen.value, canEdit)
          assert.equal(p.state.mode.value, canEdit ? 'edit' : 'view')
          assert.equal(p.state.canEditTarget.value, canEdit && kind === 'plan' && !targetKey)
          if (canEdit) {
            p.state.form.value.targetKey = 'candidate'
            Object.assign(p.state.form.value.items, { manual: null, flag: false, auto: 0, readOnly: 0 })
          }
          await p.state.save()
          const write = p.calls.find(([key]) => key === 'upsert')
          if (!canEdit) assert.equal(write, undefined)
          else assert.deepEqual(write[1], { taskNo: newer.taskNo,
            ...(kind === 'plan' && !targetKey ? { targetKey: 'candidate' } : {}),
            items: { flag: false, ...(kind === 'plan' ? { auto: 0 } : {}) }
          })
        } finally { p.close() }
      }
    }
  }
})

test('settling a stale save never ends a newer draft save already in progress', async () => {
  for (const kind of ['plan', 'performance']) {
    for (const staleFails of [false, true]) {
      const stale = deferred(), current = deferred()
      const writes = []
      const p = mount(page, kind, { api: {
        detail: async id => id === 'A' ? { ...older, hasPlan: true } : newer,
        upsert: body => {
          writes.push(body)
          return body.taskNo === older.taskNo ? stale.promise : current.promise
        }
      } })
      try {
        await p.state.openDetail(older, 'edit')
        p.state.form.value.remark = 'A'
        const saveA = p.state.save()
        await p.state.openDetail(newer, 'edit')
        p.state.form.value.remark = 'B'
        const saveB = p.state.save()
        if (staleFails) stale.reject(missingTask)
        else stale.resolve({})
        await saveA
        assert.equal(p.state.saving.value, true)
        assert.equal(p.state.form.value.remark, 'B')
        assert.equal(p.state.detailOpen.value, true)
        assert.equal(p.state.saveError.value, '')
        assert.deepEqual(p.notices, [])
        current.resolve({})
        await saveB
        assert.deepEqual(writes, [{ taskNo: older.taskNo, remark: 'A' }, { taskNo: newer.taskNo, remark: 'B' }])
        assert.equal(p.state.detailOpen.value, false)
        assert.deepEqual(p.notices, [kind + '.workflow.saved'])
      } finally { p.close() }
    }
  }
})

test('localized dialog copy has paired keys across both modules', async () => {
  const keys = await Promise.all(['plan', 'performance'].flatMap(module => ['zh-CN', 'en-US'].map(async locale => {
    const messages = JSON.parse(await readFile(new URL(
      `../../src/app/${module}/locales/${locale}.json`, import.meta.url), 'utf8'))
    const dialog = messages.workflow.dialog
    for (const name of ['viewTitle', 'editTitle', 'supplementTitle']) assert.match(dialog[name], /\{taskNo\}/)
    for (const value of Object.values(dialog)) assert.ok(value.trim())
    return Object.keys(dialog).sort()
  })))
  for (const result of keys) assert.deepEqual(result, keys[0])
})
