/** 验证质量结果和本地字段管理的实际 Vue setup、链接和配置冲突行为。 */
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import * as vue from 'vue'
import { compileScript, parse } from 'vue/compiler-sfc'
import { useTableColumnWidths } from '../../src/utils/tableColumnWidths.js'

const root = '../../src/app/quality/'
const source = file => readFile(new URL(root + file, import.meta.url), 'utf8')

async function mount(file, api, role = 'admin') {
  const { descriptor } = parse(await source(file))
  const executable = compileScript(descriptor, { id: file }).content
    .replace(/^import\s+(.+?)\s+from\s+['"](.+?)['"];?$/gm, (_line, binding, key) =>
      `const ${binding.replace(/\bas\b/g, ':')} = deps[${JSON.stringify(key)}]`)
    .replace('export default', 'return')
  const hooks = []
  const deps = {
    vue: { ...vue, onMounted: hook => hooks.push(hook) },
    '@element-plus/icons-vue': { QuestionFilled: {} },
    'vue-i18n': { useI18n: () => ({ t: key => key, locale: vue.ref('en-US') }) },
    '@/store/user': { useUserStore: () => ({ role }) },
    '@/utils/tableColumnWidths': { useTableColumnWidths },
    '@/components/common/ActionButton.vue': {},
    '@/components/common/BaseCard.vue': {},
    '../../api': api,
    '../../components/QualityFieldForm.vue': {}
  }
  const effect = vue.effectScope()
  const state = effect.run(() => new Function('deps', executable)(deps).setup({}, {
    expose() {},
    emit() {}
  }))
  const start = async () => { for (const hook of hooks) await hook() }
  return { state, start, close: () => effect.stop(), template: descriptor.template.content }
}

const fields = [
  { name: 'reportUrl', type: 'link', labels: { 'en-US': 'Report', 'zh-CN': '报告' }, linkText: '下载', visible: true, editable: true },
  { name: 'defect_count', type: 'number', labels: { 'en-US': 'Defects', 'zh-CN': '缺陷数' }, visible: true, editable: true },
  { name: 'hidden', type: 'boolean', labels: { 'en-US': 'Hidden', 'zh-CN': '隐藏' }, visible: false, editable: false },
]
const row = { taskNo: 'FIXTURE-1', items: { reportUrl: 'https://example.com/a', defect_count: 2, hidden: false } }

test('quality uses enabled visible columns, validates links and sends only edited fields', async () => {
  const calls = []
  const component = await mount('views/results/QualityList.vue', {
    listQualityResults: async () => ({ items: [row], total: 1, fields }),
    getQualityResult: async () => row,
    saveQualityResult: async body => calls.push(body)
  }, 'operator')
  try {
    await component.start()
    const { state, template } = component
    assert.deepEqual(state.visibleFields.value.map(field => state.fieldKey(field)), ['item.reportUrl', 'item.defect_count'])
    assert.equal(state.displayValue(fields[1], 0), 0)
    assert.equal(state.displayValue(fields[2], false), 'quality.results.no')
    assert.equal(state.linkUrl(row.items.reportUrl), row.items.reportUrl)
    for (const value of ['javascript:alert(1)', '/report', 'https:///report', 'https://name@example.com/a',
      'https://@example.com', 'https://example.com/a b', 'https://example.com/a\u0001']) assert.equal(state.linkUrl(value), '')
    assert.match(template, /linkText \|\|/)
    assert.match(template, /target="_blank" rel="noopener noreferrer"/)
    await state.open(row.taskNo, true)
    state.draft.value.defect_count = '0'
    await state.submit()
    assert.deepEqual(calls, [{ taskNo: 'FIXTURE-1', items: { defect_count: 0 } }])
  } finally { component.close() }
})

test('fixed columns preserve date-looking identifiers and format only both timestamps', async () => {
  const component = await mount('views/results/QualityList.vue', {})
  try {
    const { state, template } = component
    const taskNo = '2026-11-23TASK-QUALITY-ALPHA'
    const targetKey = '2026-11-23TARGET-QUALITY-ALPHA'
    assert.equal(state.formatFixed('taskNo', taskNo), taskNo)
    assert.equal(state.formatFixed('targetKey', targetKey), targetKey)
    assert.equal(state.formatFixed('createdAt', '2026-11-23T09:00:00.123456+08:00'), '2026-11-23 09:00:00')
    assert.equal(state.formatFixed('updatedAt', '2026-11-23T09:30:05+08:00'), '2026-11-23 09:30:05')
    assert.equal(state.formatFixed('targetKey', null), 'quality.results.emptyValue')
    assert.match(template, /formatFixed\(key, row\[key\]\)/)
    assert.match(template, /formatFixed\(key, record\[key\]\)/)
  } finally { component.close() }
})

test('stale field configuration retains the draft and requires current revision review', async () => {
  const calls = []
  const component = await mount('views/local-fields/index.vue', {
    getQualityFieldConfig: async () => ({ revision: calls.length ? 3 : 2, definitions: fields.map(field => ({ ...field, enabled: true, order: 0 })) }),
    saveQualityFieldConfig: async body => {
      calls.push(body)
      if (calls.length === 1) throw { response: { data: { errorCode: 'quality.config_revision_conflict' } } }
      return { revision: 4, definitions: body.definitions }
    }
  })
  try {
    const { state } = component
    await component.start()
    state.open('edit', state.config.value.definitions[0])
    state.draft.value.linkText = 'Open report'
    await state.submit()
    assert.equal(state.conflicted.value, true)
    assert.equal(state.dialog.value, true)
    await state.submit()
    assert.equal(calls.length, 1)
    await state.reloadForConflict()
    assert.equal(state.draft.value.linkText, 'Open report')
    await state.submit()
    assert.equal(calls[1].revision, 3)
    assert.equal(calls[1].definitions[0].linkText, 'Open report')
    assert.equal(state.dialog.value, false)
  } finally { component.close() }
})

test('manual creation submits only touched writable fields and retains a conflicting draft', async () => {
  const calls = []
  const requests = []
  const definitions = [
    ...fields,
    { name: 'secretNote', type: 'string', editable: true, visible: false, enabled: true },
    { name: 'approved', type: 'boolean', editable: true, visible: true, enabled: true },
    { name: 'disabled', type: 'string', editable: true, visible: false, enabled: false },
  ]
  let finish
  const component = await mount('views/results/QualityList.vue', {
    listQualityResults: async params => {
      requests.push(params)
      return { items: [], total: 0, totalPages: 0, fields: definitions }
    },
    createQualityResult: body => {
      calls.push(body)
      if (calls.length === 1) {
        return new Promise((resolve, reject) => {
          finish = () => reject({ response: { status: 409, data: { errorCode: 'quality.task_no_conflict' } } })
        })
      }
      if (body.taskNo === 'UNCONFIRMED') {
        throw { response: { status: 503, data: { errorCode: 'quality.commit_unknown' } } }
      }
      if (body.taskNo === 'EXPIRED') {
        throw { response: { status: 401, data: { errorCode: 'quality.unauthenticated' } } }
      }
      return { outcome: 'created' }
    }
  }, 'supervisor')
  try {
    await component.start()
    const { state, template } = component
    assert.equal(state.canWrite.value, true)
    assert.deepEqual(state.editableFields.value.map(field => field.name),
      ['reportUrl', 'defect_count', 'secretNote', 'approved'])
    assert.match(template, /:close-on-click-modal="true"/)
    state.filters.targetKey = 'KeepCase'
    state.search()
    state.openCreate()
    assert.deepEqual(Object.keys(state.draft.value), [])
    state.identity.taskNo = ' duplicate '
    state.identity.targetKey = 'KeepCase'
    state.draft.value.defect_count = '0'
    state.draft.value.secretNote = ''
    state.draft.value.approved = false
    const pending = state.submit()
    assert.equal(state.saving.value, true)
    await state.submit()
    let closed = false
    state.beforeClose(() => { closed = true })
    assert.equal(closed, false)
    assert.deepEqual(calls, [{
      taskNo: 'duplicate', targetKey: 'KeepCase', items: { defect_count: 0, secretNote: '', approved: false },
    }])
    finish()
    await pending
    assert.equal(state.detailError.value, 'quality.results.taskNoConflict')
    assert.equal(state.dialogOpen.value, true)
    assert.equal(state.identity.taskNo, ' duplicate ')
    assert.equal(state.draft.value.approved, false)
    state.identity.taskNo = 'UNCONFIRMED'
    await state.submit()
    assert.equal(state.detailError.value, 'quality.results.createUnknown')
    assert.equal(state.dialogOpen.value, true)
    assert.equal(state.draft.value.approved, false)
    assert.equal(calls.length, 2)
    state.identity.taskNo = 'EXPIRED'
    await state.submit()
    assert.equal(state.detailError.value, 'quality.results.createUnauthenticated')
    assert.equal(state.dialogOpen.value, true)
    assert.equal(state.draft.value.approved, false)
    assert.equal(calls.length, 3)
    state.identity.taskNo = 'NEW'
    await state.submit()
    assert.equal(state.dialogOpen.value, false)
    assert.equal(requests.at(-1).targetKey, 'KeepCase')
    state.fields.value = []
    state.openCreate()
    state.identity.taskNo = 'EMPTY'
    await state.submit()
    assert.deepEqual(calls.at(-1), { taskNo: 'EMPTY', items: {} })
  } finally { component.close() }
})

test('field labels remain bilingual and legacy pages carry no inspection controls', async () => {
  const chinese = JSON.parse(await source('locales/zh-CN.json'))
  const english = JSON.parse(await source('locales/en-US.json'))
  const keys = value => Object.entries(value).flatMap(([key, item]) => typeof item === 'object'
    ? keys(item).map(child => `${key}.${child}`) : [key]).sort()
  assert.deepEqual(keys(chinese), keys(english))
  assert.doesNotMatch(await source('views/results/index.vue'), /LegacyQualityList|view:\s*['"]legacy['"]/)
  assert.match(await source('views/control/index.vue'), /router\.replace\(\{ name: 'QualityList' \}\)/)
})
