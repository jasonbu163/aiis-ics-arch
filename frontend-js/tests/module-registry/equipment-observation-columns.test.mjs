/** 设备与过程列表指标标题和假值展示的回归。 */
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { parse, compileScript } from 'vue/compiler-sfc'
import { renderToString } from 'vue/server-renderer'
import * as vue from 'vue'
import * as echarts from 'echarts'
import { splitObservedPoints } from '../../src/app/monitor/components/observations/curveSeries.js'
import { metricField, metricTitle, metricValue } from '../../src/app/equipment/components/observations/columnModel.js'
import { useTableColumnWidths } from '../../src/utils/tableColumnWidths.js'
import { formatShanghaiDateTime } from '../../src/utils/date.js'

test('metric columns retain stable keys and distinguish zero, false, empty and missing', () => {
  const row = { values: [{ metricKey: 'temperature', value: 0 }, { metricKey: 'ready', value: false }, { metricKey: 'coil', value: '' }] }
  assert.equal(metricField('temperature'), 'metric:temperature')
  assert.equal(metricValue(row, 'temperature'), '0')
  assert.equal(metricValue(row, 'ready'), 'false')
  assert.equal(metricValue(row, 'coil'), '')
  assert.equal(metricValue(row, 'other'), '—')
  assert.equal(metricValue({}, 'other'), '—')
})

test('localized titles show optional unit without changing the field key', () => {
  const metric = { nameZh: '实际温度', nameEn: 'Actual temperature', unit: '°C' }
  assert.equal(metricTitle(metric, 'zh-CN'), '实际温度 (°C)')
  assert.equal(metricTitle(metric, 'en-US'), 'Actual temperature (°C)')
  assert.equal(metricTitle({ ...metric, unit: null }, 'en-US'), 'Actual temperature')
})

test('actual list setup saves independent display settings and restores stable column widths', async () => {
  const source = await readFile(new URL('../../src/app/equipment/components/observations/RecordList.vue', import.meta.url), 'utf8')
  const { descriptor } = parse(source)
  const script = compileScript(descriptor, { id: 'observation-records' }).content
    .replace(/^import\s+(.+?)\s+from\s+['"](.+?)['"];?$/gm, (_line, binding, name) => {
      if (binding.startsWith('{')) binding = binding.replace(/\bas\b/g, ':')
      return `const ${binding} = deps[${JSON.stringify(name)}]`
    }).replace('export default', 'return')
  const fields = [{ groupKey: 'temperature', slotNo: 7, metricKey: 'actual', enabled: false, listVisible: false,
    listOrder: null, nameZh: '实际温度', nameEn: 'Actual temperature', unit: '°C' }]
  fields.push(...Array.from({ length: 8 }, (_, i) => ({
    ...fields[0], slotNo: 8 + i, metricKey: 'other' + i, nameEn: 'Other ' + i
  })))
  const calls = [], hooks = [], store = new Map()
  let rejectLast = true
  globalThis.localStorage = { getItem: key => store.get(key) ?? null, setItem: (key, value) => store.set(key, value), removeItem: key => store.delete(key) }
  const api = {
    equipmentOptions: async () => [], latestList: async () => ({ items: [], total: 0 }), latestDetail: async () => ({}), updateLatest: async () => {},
    observationListColumns: async target => ({ target, items: structuredClone(fields) }),
    updateBinding: async (target, group, slot, changes) => {
      calls.push({ target, group, slot, changes })
      if (slot === 15 && rejectLast) throw new Error('temporary failure')
      Object.assign(fields.find(field => field.slotNo === slot), changes)
    }
  }
  const deps = {
    vue: { ...vue, onMounted: fn => hooks.push(fn), onBeforeUnmount: () => {} }, 'vue-i18n': { useI18n: () => ({ t: key => key, locale: vue.ref('zh-CN') }) },
    '@element-plus/icons-vue': {}, '@/components/common/BaseCard.vue': {},
    '@/components/common/ActionButton.vue': {}, '@/utils/date': { formatShanghaiDateTime: v => v, shanghaiInputToRfc3339: v => v },
    '@/utils/tableColumnWidths': { useTableColumnWidths }, '../../api/observations': api,
    '@/app/monitor/api/observations': { monitorOptions: async () => [], historyList: async () => ({ items: [], total: 0 }), historyDetail: async () => ({}), updateHistory: async () => {} },
    './columnModel': { metricField, metricTitle, metricValue }
  }
  const scope = vue.effectScope()
  try {
    const component = new Function('deps', script)(deps)
    const state = scope.run(() => component.setup({ target: 'history' }, { expose() {} }))
    await Promise.all(hooks.map(fn => fn()))
    assert.equal(state.visibleColumns.value.length, 0)
    state.openColumnSettings()
    state.columnPageRows.value[0].listVisible = true
    state.columnDialog.value = false
    state.openColumnSettings()
    assert.equal(state.columnPageRows.value[0].listVisible, false)
    Object.assign(state.columnPageRows.value[0], { listVisible: true, listOrder: 10 })
    state.columnPage.value = 2
    state.columnPageRows.value[0].listVisible = true
    state.columnFilters.keyword = 'Other 3'
    state.searchColumnSettings()
    assert.equal(state.columnPageRows.value.length, 1)
    assert.equal(calls.length, 0)
    await state.saveColumnSettings()
    assert.deepEqual(calls, [
      { target: 'history', group: 'temperature', slot: 7, changes: { listVisible: true, listOrder: 10 } },
      { target: 'history', group: 'temperature', slot: 15, changes: { listVisible: true } }
    ])
    assert.equal(state.columnDialog.value, true)
    assert.deepEqual(state.columnSaveFailures.value, ['other7'])
    rejectLast = false
    await state.saveColumnSettings()
    assert.equal(calls.length, 3)
    assert.equal(calls[2].slot, 15)
    assert.equal(state.columnDialog.value, false)
    assert.equal(fields[0].enabled, false)
    assert.equal(state.visibleColumns.value[0].metricKey, 'actual')
    state.columns.value.onHeaderDragEnd(240, 160, { property: 'metric:actual' })
    await state.loadColumns()
    assert.equal(state.columns.value.widths['metric:actual'], 240)
    state.columns.value.reset()
    assert.equal(state.columns.value.widths['metric:actual'], 160)
    assert.match(descriptor.template.content, /v-for="field in visibleColumns"/)
  } finally { scope.stop(); delete globalThis.localStorage }
})

test('energy settings save column order and the sample list respects it', async () => {
  const source = await readFile(new URL('../../src/app/monitor/components/observations/EnergyAdmin.vue', import.meta.url), 'utf8')
  const { descriptor } = parse(source)
  const script = compileScript(descriptor, { id: 'energy-admin' }).content
    .replace(/^import\s+(.+?)\s+from\s+['"](.+?)['"];?$/gm, (_line, binding, name) => {
      if (binding.startsWith('{')) binding = binding.replace(/\bas\b/g, ':')
      return `const ${binding} = deps[${JSON.stringify(name)}]`
    }).replace('export default', 'return')
  const fields = [
    { meterId: 'meter1', groupKey: 'power', metricKey: 'a', slotNo: 1, listVisible: true, listOrder: 20, rules: {}, enabled: true },
    { meterId: 'meter1', groupKey: 'power', metricKey: 'b', slotNo: 2, listVisible: true, listOrder: 10, rules: {}, enabled: true },
    { meterId: 'meter1', groupKey: 'power', metricKey: 'c', slotNo: 3, listVisible: false, listOrder: 0, rules: {}, enabled: true },
    { meterId: 'meter1', groupKey: 'power', metricKey: 'd', slotNo: 4, listVisible: true, listOrder: null, rules: {}, enabled: true }
  ]
  const calls = [], hooks = [], store = new Map()
  globalThis.localStorage = { getItem: key => store.get(key) ?? null, setItem: (key, value) => store.set(key, value), removeItem: key => store.delete(key) }
  const api = {
    energyOptions: async () => [{ meterId: 'meter1' }], energyConfigs: async () => structuredClone(fields),
    createEnergyConfig: async () => {}, energyAdminSamples: async () => ({ items: [], total: 0 }), updateEnergySample: async () => {},
    updateEnergyConfig: async (meter, group, metric, changes) => { calls.push({ meter, group, metric, changes }) }
  }
  const deps = {
    vue: { ...vue, onMounted: fn => hooks.push(fn) }, 'vue-i18n': { useI18n: () => ({ t: key => key, locale: vue.ref('zh-CN') }) },
    '@/components/common/ActionButton.vue': {}, '@/utils/date': { formatShanghaiDateTime: value => value },
    '@/utils/tableColumnWidths': { useTableColumnWidths }, '../../api/observations': api
  }
  const scope = vue.effectScope()
  try {
    const component = new Function('deps', script)(deps)
    const state = scope.run(() => component.setup({ kind: 'samples' }, { expose() {} }))
    state.meter.value = 'meter1'
    await state.load()
    assert.deepEqual(state.visibleColumns.value.map(field => field.metricKey), ['b', 'a', 'd'])
    assert.match(descriptor.template.content, /v-model="form\.listOrder"/)
    const editor = scope.run(() => component.setup({ kind: 'config', active: true }, { expose() {} }))
    await editor.loadConfig()
    editor.openConfig(editor.configs.value[0])
    editor.form.listOrder = 5
    await editor.save()
    assert.equal(calls[0].metric, 'a')
    assert.equal(calls[0].changes.listOrder, 5)
    assert.equal(calls[0].changes.listVisible, true)
    assert.equal(calls[0].changes.enabled, true)
  } finally { scope.stop(); delete globalThis.localStorage }
})

async function energyAdminFixture(kind, api) {
  const source = await readFile(new URL('../../src/app/monitor/components/observations/EnergyAdmin.vue', import.meta.url), 'utf8')
  const script = compileScript(parse(source).descriptor, { id: 'energy-admin-race' }).content
    .replace(/^import\s+(.+?)\s+from\s+['"](.+?)['"];?$/gm, (_line, binding, name) => {
      if (binding.startsWith('{')) binding = binding.replace(/\bas\b/g, ':')
      return `const ${binding} = deps[${JSON.stringify(name)}]`
    }).replace('export default', 'return')
  const store = new Map()
  globalThis.localStorage = { getItem: key => store.get(key) ?? null, setItem: (key, value) => store.set(key, value), removeItem: key => store.delete(key) }
  const deps = { vue: { ...vue, onMounted: () => {}, onBeforeUnmount: () => {} },
    'vue-i18n': { useI18n: () => ({ t: key => key, locale: vue.ref('zh-CN') }) },
    '@/components/common/ActionButton.vue': {}, '@/utils/date': { formatShanghaiDateTime: value => value },
    '@/utils/tableColumnWidths': { useTableColumnWidths }, '../../api/observations': api }
  const scope = vue.effectScope()
  const component = new Function('deps', script)(deps)
  const state = scope.run(() => component.setup({ kind, active: true }, { expose() {} }))
  return { state, close() { scope.stop(); delete globalThis.localStorage } }
}

test('energy config selection rejects out-of-order results and stale edit targets', async () => {
  const requests = { A: deferred(), B: deferred() }, counts = {}, writes = []
  const field = meterId => ({ meterId, groupKey: 'power', metricKey: 'reading', slotNo: 1, rules: {}, listVisible: true })
  const api = { energyOptions: async () => [{ meterId: 'A' }, { meterId: 'B' }], energyConfigs: ({ meterId }) => {
    if (!meterId) return Promise.resolve([field('A'), field('B')])
    counts[meterId] = (counts[meterId] || 0) + 1
    return counts[meterId] === 1 ? requests[meterId].promise : Promise.resolve([field(meterId)])
  }, createEnergyConfig: async value => writes.push(value), energyAdminSamples: async () => ({ items: [], total: 0 }),
  updateEnergySample: async () => {}, updateEnergyConfig: async (...args) => writes.push(args) }
  const { state, close } = await energyAdminFixture('config', api)
  try {
    await state.loadConfig()
    assert.deepEqual(state.configs.value.map(item => item.meterId), ['A', 'B'])
    state.openConfig()
    assert.equal(state.form.meterId, '')
    await state.save()
    assert.equal(writes.length, 0)
    state.draft.meter = 'A'; const first = state.searchConfig()
    state.draft.meter = 'B'; const second = state.searchConfig()
    requests.B.resolve([field('B')]); await second
    requests.A.resolve([field('A')]); await first
    assert.deepEqual(state.configs.value.map(item => item.meterId), ['B'])
    state.openConfig(field('A')); await state.save()
    assert.equal(writes.length, 0)
    state.openConfig(state.configs.value[0]); state.form.listOrder = 5
    state.form.meterId = 'A'; state.form.groupKey = 'other'; state.form.metricKey = 'other'
    await state.save()
    assert.deepEqual(writes[0].slice(0, 3), ['B', 'power', 'reading'])
    state.openConfig(state.configs.value[0]); state.draft.meter = 'A'
    await state.searchConfig()
    await state.save()
    assert.equal(writes.length, 1)
    await state.resetConfigFilters()
    assert.deepEqual(state.configs.value.map(item => item.meterId), ['A', 'B'])
  } finally { close() }
})

test('energy samples retain current meter, group and page across delayed results and errors', async () => {
  const pending = new Map(), writes = [], sampleCalls = []
  const field = (meterId, groupKey = 'power') => ({ meterId, groupKey, metricKey: 'reading', slotNo: 1, rules: {}, listVisible: true })
  const key = p => `${p.meterId}:${p.groupKey || 'all'}:${p.page}`
  const api = { energyOptions: async () => [], energyConfigs: async ({ meterId, groupKey }) => [field(meterId, groupKey || 'power')],
    energyAdminSamples: p => { sampleCalls.push(key(p)); const request = deferred(); pending.set(key(p), request); return request.promise },
    createEnergyConfig: async () => {}, updateEnergyConfig: async () => {}, updateEnergySample: async (...args) => { writes.push(args) } }
  const { state, close } = await energyAdminFixture('samples', api)
  const settle = async () => { await vue.nextTick(); await Promise.resolve(); await vue.nextTick() }
  const row = (meterId, id, groupKey = 'power') => ({ id, meterId, groupKey, values: [], remark: '', reviewMark: '' })
  try {
    state.meter.value = 'A'; await settle()
    state.meter.value = 'B'; await settle()
    pending.get('B:all:1').resolve({ items: [row('B', 'b')], total: 1 }); await settle()
    pending.get('A:all:1').resolve({ items: [row('A', 'a')], total: 1 }); await settle()
    assert.deepEqual(state.samples.value.map(item => item.id), ['b'])
    assert.deepEqual(state.configs.value.map(item => item.meterId), ['B'])
    state.openSample(row('A', 'a')); await state.save(); assert.equal(writes.length, 0)
    state.openSample(state.samples.value[0]); state.form.remark = 'reviewed'; state.form.id = 'a'
    const saving = state.save(); await settle()
    pending.get('B:all:1').resolve({ items: [row('B', 'b')], total: 1 }); await saving
    assert.equal(writes[0][0], 'b')
    state.openSample(state.samples.value[0]); state.group.value = 'zone1'; await state.save()
    assert.equal(writes.length, 1)
    const first = state.load(); await settle()
    state.group.value = 'zone2'; const second = state.load(); await settle()
    pending.get('B:zone2:1').resolve({ items: [row('B', 'z2', 'zone2')], total: 60 }); await second
    pending.get('B:zone1:1').reject(new Error('obsolete')); await first
    assert.equal(state.failed.value, false); assert.equal(state.samples.value[0].id, 'z2')
    state.page.value = 2; const page2 = state.load(); await settle()
    assert.equal(state.total.value, 60)
    state.page.value = 3; const page3 = state.load(); await settle()
    pending.get('B:zone2:3').resolve({ items: [row('B', 'p3', 'zone2')], total: 3 }); await page3
    pending.get('B:zone2:2').resolve({ items: [row('B', 'p2', 'zone2')], total: 3 }); await page2
    assert.equal(state.samples.value[0].id, 'p3')
    assert.ok(sampleCalls.includes('B:zone2:3'))
  } finally { close() }
})

test('energy retry and an obsolete save failure cannot alter the new selection', async () => {
  const save = deferred(), writes = [], options = { attempts: 0 }
  const field = meterId => ({ meterId, groupKey: 'power', metricKey: 'reading', slotNo: 1, rules: {} })
  const api = { energyOptions: async () => { if (++options.attempts === 1) throw new Error('unavailable'); return [{ meterId: 'A' }, { meterId: 'B' }] },
    energyConfigs: async ({ meterId }) => meterId ? [field(meterId)] : [field('A'), field('B')], energyAdminSamples: async () => ({ items: [], total: 0 }),
    createEnergyConfig: async () => {}, updateEnergyConfig: (...args) => { writes.push(args); return save.promise }, updateEnergySample: async () => {} }
  const { state, close } = await energyAdminFixture('config', api)
  try {
    await state.loadConfig(); assert.equal(state.failed.value, true)
    await state.loadConfig()
    assert.equal(state.failed.value, false)
    assert.deepEqual(state.configs.value.map(item => item.meterId), ['A', 'B'])
    state.openConfig(state.configs.value[0]); const saving = state.save()
    state.draft.meter = 'B'; await state.searchConfig()
    save.reject(new Error('old save failure')); await saving
    assert.equal(state.failed.value, false)
    assert.deepEqual(state.configs.value.map(item => item.meterId), ['B'])
    assert.equal(writes[0][0], 'A')
  } finally { close() }
})

test('superseded energy configuration request cannot start a sample request for the new meter', async () => {
  const a = deferred(), calls = []
  const api = { energyOptions: async () => [], energyConfigs: ({ meterId }) => meterId === 'A' ? a.promise : Promise.resolve([]),
    energyAdminSamples: async p => { calls.push(p.meterId); return { items: [], total: 0 } }, createEnergyConfig: async () => {},
    updateEnergyConfig: async () => {}, updateEnergySample: async () => {} }
  const { state, close } = await energyAdminFixture('samples', api)
  try {
    state.meter.value = 'A'; await vue.nextTick()
    state.meter.value = 'B'; await vue.nextTick(); await Promise.resolve(); await vue.nextTick()
    a.resolve([]); await vue.nextTick(); await Promise.resolve(); await vue.nextTick()
    assert.deepEqual(calls, ['B'])
  } finally { close() }
})

test('curve area picker uses localized labels while retaining stable group keys', async () => {
  const source = await readFile(new URL('../../src/app/monitor/components/observations/CurveChart.vue', import.meta.url), 'utf8')
  const { descriptor } = parse(source)
  const script = compileScript(descriptor, { id: 'curve-area-picker' }).content
    .replace(/^import\s+(.+?)\s+from\s+['"](.+?)['"];?$/gm, (_line, binding, name) => {
      if (binding.startsWith('{')) binding = binding.replace(/\bas\b/g, ':')
      else if (binding.includes(',')) {
        const [def, named] = binding.split(/,(.+)/)
        return `const ${def} = deps[${JSON.stringify(name)}].default; const ${named.replace(/\bas\b/g, ':')} = deps[${JSON.stringify(name)}]`
      }
      return `const ${binding} = deps[${JSON.stringify(name)}]`
    }).replace('export default', 'return')
  const group = vue.reactive({ title: '温度', series: [{ groupKey: 'heatZone1', groupLabel: '一号加热区', points: [] }] })
  const deps = {
    vue: { ...vue, onMounted: () => {}, onBeforeUnmount: () => {} },
    'vue-i18n': { useI18n: () => ({ t: key => key }) }, '@/utils/echarts': { default: {}, getEChartsTheme: () => ({}) },
    '@/utils/date': { formatShanghaiDateTime: value => value }, '@/store/theme': { useThemeStore: () => ({ theme: 'light' }) },
    '@/components/common/ActionButton.vue': {}, './curveSeries': { splitObservedPoints: () => ({ line: [], simultaneous: [] }) }
  }
  const scope = vue.effectScope()
  try {
    const component = new Function('deps', script)(deps)
    const state = scope.run(() => component.setup({ group, range: [] }, { expose() {} }))
    assert.deepEqual(state.available.value, ['heatZone1'])
    assert.equal(state.areaLabel('heatZone1'), '一号加热区')
    group.series[0].groupLabel = 'Renamed Zone One'
    assert.equal(state.areaLabel('heatZone1'), 'Renamed Zone One')
    assert.deepEqual(state.selected.value, ['heatZone1'])
    assert.match(descriptor.template.content, /:value="key"\s+:label="areaLabel\(key\)"/)
  } finally { scope.stop() }
})

test('actual ECharts time axis retains microsecond order and missing or simultaneous samples', async () => {
  const source = await readFile(new URL('../../src/app/monitor/components/observations/CurveChart.vue', import.meta.url), 'utf8')
  const { descriptor } = parse(source)
  const script = compileScript(descriptor, { id: 'curve-axis' }).content
    .replace(/^import\s+(.+?)\s+from\s+['"](.+?)['"];?$/gm, (_line, binding, name) => {
      if (binding.startsWith('{')) binding = binding.replace(/\bas\b/g, ':')
      else if (binding.includes(',')) {
        const [def, named] = binding.split(/,(.+)/)
        return `const ${def} = deps[${JSON.stringify(name)}].default; const ${named.replace(/\bas\b/g, ':')} = deps[${JSON.stringify(name)}]`
      }
      return `const ${binding} = deps[${JSON.stringify(name)}]`
    }).replace('export default', 'return')
  const time = suffix => `2500-01-01T10:00:${suffix}+08:00`
  const group = { title: 'Temperature', unit: '°C', series: [{ groupKey: 'zone', groupLabel: 'Zone', label: 'Actual', points: [
    { observedAt: time('00.123001'), value: 10 }, { observedAt: time('00.123002'), value: 20 },
    { observedAt: time('01.000000'), present: false, value: null }, { observedAt: time('02.000000'), value: 30 },
    { observedAt: time('03.000000'), value: 40 }, { observedAt: time('03.000000'), value: 50 }
  ] }] }
  let chart
  const deps = {
    vue: { ...vue, onMounted: () => {}, onBeforeUnmount: () => {} }, 'vue-i18n': { useI18n: () => ({ t: key => key }) },
    '@/utils/echarts': { default: { init: () => (chart = echarts.init(null, null, { renderer: 'svg', ssr: true, width: 1000, height: 400 })) }, getEChartsTheme: () => null },
    '@/utils/date': { formatShanghaiDateTime: value => value }, '@/store/theme': { useThemeStore: () => ({ theme: 'light' }) },
    '@/components/common/ActionButton.vue': {}, './curveSeries': { splitObservedPoints }
  }
  const scope = vue.effectScope()
  try {
    const component = new Function('deps', script)(deps)
    const state = scope.run(() => component.setup({ group, range: [time('00'), time('04')] }, { expose() {} }))
    state.element.value = {}
    state.render()
    const line = chart.getModel().getSeriesByIndex(0).getData()
    const simultaneous = chart.getModel().getSeriesByIndex(1).getData()
    assert.ok(line.get('x', 0) < line.get('x', 1))
    assert.ok(chart.convertToPixel({ xAxisIndex: 0 }, line.get('x', 0)) < chart.convertToPixel({ xAxisIndex: 0 }, line.get('x', 1)))
    assert.equal(Number.isNaN(line.get('y', 2)), true)
    assert.equal(Number.isNaN(line.get('y', 4)), true)
    assert.equal(simultaneous.get('x', 0), simultaneous.get('x', 1))
    assert.deepEqual([simultaneous.get('y', 0), simultaneous.get('y', 1)], [40, 50])
    const original = group.series[0].points[0].observedAt
    assert.equal(line.getRawDataItem(0)[2], original)
    const formatter = chart.getOption().tooltip[0].formatter
    assert.match(formatter([{ axisValue: line.get('x', 0), marker: '', seriesName: 'Actual',
      value: line.getRawDataItem(0), data: line.getRawDataItem(0) }]), new RegExp(original.replace('+', '\\+')))
    assert.equal(state.precisionLimited.value, false)
    chart.dispose()
    const wideGroup = { ...group, series: [{ ...group.series[0], points: [
      { observedAt: '2600-01-01T00:00:00.123001Z', value: 1 },
      { observedAt: '2600-01-01T00:00:00.123002Z', value: 2 }
    ] }] }
    const wide = scope.run(() => component.setup({ group: wideGroup,
      range: ['2300-01-01T00:00:00Z', '2601-01-01T00:00:00Z'] }, { expose() {} }))
    wide.element.value = {}
    wide.render()
    assert.equal(wide.precisionLimited.value, true)
    assert.equal(chart.getModel().getSeriesByIndex(0).getData().count(), 2)
    assert.match(descriptor.template.content, /v-if="precisionLimited"/)
  } finally { chart?.dispose(); scope.stop() }
})

async function energyPageFixture(api) {
  const source = await readFile(new URL('../../src/app/monitor/views/observations/energy.vue', import.meta.url), 'utf8')
  const { descriptor } = parse(source)
  const script = compileScript(descriptor, { id: 'energy-races' }).content
    .replace(/^import\s+(.+?)\s+from\s+['"](.+?)['"];?$/gm, (_line, binding, name) => {
      if (binding.startsWith('{')) binding = binding.replace(/\bas\b/g, ':')
      return `const ${binding} = deps[${JSON.stringify(name)}]`
    }).replace('export default', 'return')
  const deps = {
    vue: { ...vue, onMounted: () => {}, onBeforeUnmount: () => {} }, 'vue-i18n': { useI18n: () => ({ t: key => key, locale: vue.ref('zh-CN') }) },
    '@/components/common/ActionButton.vue': {}, '@/components/common/BaseCard.vue': {},
    '@/utils/date': { shanghaiInputToRfc3339: value => value },
    '../../components/observations/CurveChart.vue': {}, '../../components/observations/EmptyAxes.vue': {},
    '../../api/observations': api
  }
  const scope = vue.effectScope()
  const component = new Function('deps', script)(deps)
  const state = scope.run(() => component.setup({}, { expose() {} }))
  return { state, scope }
}

function deferred() {
  let resolve, reject
  const promise = new Promise((done, fail) => { resolve = done; reject = fail })
  return { promise, resolve, reject }
}

test('late meter definitions and errors cannot replace the currently selected meter', async () => {
  const requests = []
  const api = { energyOptions: async () => [], energyDefinitions: meter => {
    const waiting = deferred(); requests.push({ meter, ...waiting }); return waiting.promise
  }, energySamples: async () => ({ items: [], totalPages: 0 }), energySummary: async () => ({}) }
  const { state, scope } = await energyPageFixture(api)
  const metric = (groupKey, metricKey, nameZh) => ({ groupKey, metricKey, nameZh, nameEn: nameZh, quantityKey: 'energy', unit: 'kWh' })
  try {
    state.meter.value = 'A'; await vue.nextTick()
    state.meter.value = 'B'; await vue.nextTick()
    requests.find(request => request.meter === 'B').resolve([metric('groupB', 'readingB', 'Meter B')])
    await vue.nextTick(); await vue.nextTick()
    requests.find(request => request.meter === 'A').resolve([metric('groupA', 'readingA', 'Meter A')])
    await vue.nextTick(); await vue.nextTick()
    assert.equal(state.meter.value, 'B')
    assert.equal(state.group.value, 'groupB')
    assert.equal(state.metric.value, 'readingB')
    assert.equal(state.definitions.value[0].nameZh, 'Meter B')
    state.meter.value = 'A'; await vue.nextTick()
    state.meter.value = 'B'; await vue.nextTick()
    requests.filter(request => request.meter === 'B').at(-1).resolve([metric('groupB', 'readingB', 'Meter B')])
    await vue.nextTick(); await vue.nextTick()
    requests.filter(request => request.meter === 'A').at(-1).reject(new Error('late failure'))
    await vue.nextTick(); await vue.nextTick()
    assert.equal(state.failed.value, false)
    assert.equal(state.definitions.value[0].nameZh, 'Meter B')
  } finally { scope.stop() }
})

test('initialization and retry share an in-flight definition request for the selected meter', async () => {
  const requests=[]
  const api={ energyOptions:async () => [{ meterId:'A' }], energyDefinitions:meter => {
    const wait=deferred(); requests.push({ meter, ...wait }); return wait.promise
  }, energySamples:async () => ({ items:[], totalPages:0 }), energySummary:async () => ({}) }
  const { state, scope } = await energyPageFixture(api)
  try {
    const first=state.retry(); await vue.nextTick(); await vue.nextTick()
    assert.equal(requests.length,1)
    requests[0].reject(new Error('fixture failure')); await first
    assert.equal(state.failed.value,true)
    const second=state.retry(); await vue.nextTick(); await vue.nextTick()
    assert.equal(requests.length,2)
    requests[1].resolve([{ groupKey:'A', metricKey:'reading', nameZh:'读数', nameEn:'Reading', quantityKey:'energy', unit:'kWh' }])
    await second
    assert.equal(state.failed.value,false)
    assert.equal(state.group.value,'A')
  } finally { scope.stop() }
})

test('changing between groups with the same metric invalidates in-flight values and summaries', async () => {
  const calls = [], first = deferred(), secondSummary = deferred()
  const metrics = ['A', 'B'].map(groupKey => ({ groupKey, metricKey: 'reading', nameZh: `Group ${groupKey}`,
    nameEn: `Group ${groupKey}`, quantityKey: 'energy', unit: 'kWh' }))
  const api = { energyOptions: async () => [], energyDefinitions: async () => metrics,
    energySamples: async params => {
      calls.push(['samples', params.groupKey])
      if (params.groupKey === 'A') return first.promise
      return { items: [{ observedAt:'2026-11-17T10:00:00+08:00', values:[{ metricKey:'reading', value:0 }] }], totalPages:1 }
    },
    energySummary: async params => {
      calls.push(['summary', params.groupKey])
      return params.groupKey === 'B' ? secondSummary.promise : { source:'A', amount:111 }
    } }
  const { state, scope } = await energyPageFixture(api)
  try {
    state.meter.value = 'meter'; await state.loadDefinitions()
    state.range.value = ['2026-11-17T00:00:00+08:00','2026-11-18T00:00:00+08:00']
    await vue.nextTick()
    const oldRequest = state.load()
    state.group.value = 'B'; await vue.nextTick()
    const currentRequest = state.load()
    first.resolve({ items:[{ observedAt:'2026-11-17T10:00:00+08:00', values:[{ metricKey:'reading', value:111 }] }], totalPages:1 })
    await oldRequest
    secondSummary.resolve({ source:'B', amount:0 })
    await currentRequest
    assert.equal(state.group.value, 'B')
    assert.equal(state.summary.value.source, 'B')
    assert.equal(state.chartGroups.value[0].title, 'Group B')
    assert.equal(state.chartGroups.value[0].series[0].points[0].value, 0)
    assert.equal(calls.some(([type, group]) => type === 'summary' && group === 'A'), false)
  } finally { scope.stop() }
})

test('late summaries, page results and errors cannot replace the current group and locale', async () => {
  const staleSummary = deferred(), stalePage = deferred(), calls = []
  const metrics = ['A', 'B'].map(groupKey => ({ groupKey, metricKey:'reading', nameZh:`区域${groupKey}`,
    nameEn:`Area ${groupKey}`, quantityKey:'energy', unit:'kWh' }))
  let mode = 'summary'
  const api = { energyOptions: async () => [], energyDefinitions: async () => metrics,
    energySamples: async params => {
      calls.push(['samples', params.groupKey, params.page])
      if (mode === 'page' && params.groupKey === 'A' && params.page === 2) return stalePage.promise
      return { items:[{ observedAt:'2026-11-17T10:00:00+08:00',
        values:[{ metricKey:'reading', value:params.groupKey === 'A' ? 111 : 0 }] }],
      totalPages:mode === 'page' && params.groupKey === 'A' ? 2 : 1 }
    },
    energySummary: async params => {
      calls.push(['summary', params.groupKey])
      return params.groupKey === 'A' ? staleSummary.promise : { source:'B', amount:0 }
    } }
  const { state, scope } = await energyPageFixture(api)
  try {
    state.meter.value='meter'; await state.loadDefinitions()
    state.range.value=['2026-11-17T00:00:00+08:00','2026-11-18T00:00:00+08:00']
    const old = state.load(); await vue.nextTick(); await vue.nextTick()
    assert.ok(calls.some(([kind, group]) => kind === 'summary' && group === 'A'))
    state.group.value='B'
    await state.load()
    staleSummary.resolve({ source:'A', amount:111 }); await old
    assert.equal(state.summary.value.source, 'B')
    assert.equal(state.chartGroups.value[0].series[0].points[0].value, 0)
    state.locale.value='en-US'
    assert.equal(state.chartGroups.value[0].title, 'Area B')
    mode='page'; state.group.value='A'
    const oldPage = state.load(); await vue.nextTick(); await vue.nextTick()
    state.group.value='B'; await state.load()
    stalePage.reject(new Error('late page failure')); await oldPage
    assert.equal(state.group.value, 'B')
    assert.equal(state.summary.value.source, 'B')
    assert.equal(state.failed.value, false)
    assert.equal(state.loading.value, false)
  } finally { scope.stop() }
})

test('stale device cards render their own real observed time in both languages', async () => {
  const source = await readFile(new URL('../../src/app/equipment/views/observations/cards.vue', import.meta.url), 'utf8')
  const { descriptor } = parse(source)
  const render = vue.compile(descriptor.template.content)
  const labels = { 'zh-CN': { sampledAt:'采集时间', stale:'陈旧' }, 'en-US': { sampledAt:'Sampled at', stale:'Stale' } }
  for (const language of ['zh-CN', 'en-US']) {
    const context = { route:{ meta:{ titleKey:'test.title' } }, locale:language, equipment:'line', devices:[], tasks:[], manualTask:'',
      manualUnavailable:false, failed:false, loading:false, refresh() {},
      t:key => labels[language][key.split('.').at(-1)] || key,
      formatted:item => item.value === null ? '—' : String(item.value), formatShanghaiDateTime,
      data:{ taskNo:'task', tied:false, cards:[{ cardKey:'c', title:'Card', items:[
        { metricKey:'stale', label:'A', value:0, dataState:'stale', observedAt:'2026-11-17T02:30:45.123456Z' },
        { metricKey:'fresh', label:'B', value:1, dataState:'fresh', observedAt:'2026-11-17T03:00:00Z' },
        { metricKey:'missing', label:'C', value:null, dataState:'missing', observedAt:null },
        { metricKey:'unknown-time', label:'D', value:false, dataState:'stale', observedAt:null }
      ] }] } }
    const app = vue.createSSRApp({ setup:() => context, render })
    app.config.globalProperties.$t = context.t
    const slot = { inheritAttrs:false, render() { return vue.h('div', this.$slots.default?.()) } }
    for (const name of ['BaseCard','el-select','el-option','ActionButton','el-alert','el-empty','el-tag']) app.component(name, slot)
    app.directive('loading', { getSSRProps:() => ({}) })
    const html = await renderToString(app)
    assert.match(html, /2026-11-17 10:30:45/)
    assert.match(html, new RegExp(labels[language].sampledAt))
    assert.match(html, new RegExp(labels[language].stale))
    assert.match(html, new RegExp(`${labels[language].sampledAt}: —`))
    assert.match(html, /false/)
    assert.doesNotMatch(html, /2026-11-17 11:00:00/)
  }
})

test('same metric labels from different regions remain identifiable and individually selectable', async () => {
  const source = await readFile(new URL('../../src/app/monitor/components/observations/CurveChart.vue', import.meta.url), 'utf8')
  const { descriptor } = parse(source)
  const script = compileScript(descriptor, { id:'independent-series' }).content
    .replace(/^import\s+(.+?)\s+from\s+['"](.+?)['"];?$/gm, (_line, binding, name) => {
      if (binding.startsWith('{')) binding = binding.replace(/\bas\b/g, ':')
      else if (binding.includes(',')) {
        const [def, named] = binding.split(/,(.+)/)
        return `const ${def} = deps[${JSON.stringify(name)}].default; const ${named.replace(/\bas\b/g, ':')} = deps[${JSON.stringify(name)}]`
      }
      return `const ${binding} = deps[${JSON.stringify(name)}]`
    }).replace('export default', 'return')
  const time = '2026-11-17T10:00:00.123456+08:00'
  const group = { title:'Temperature', unit:'°C', series:[
    { groupKey:'zoneA', groupLabel:'Zone A', metricKey:'a', label:'Actual temperature', points:[{ observedAt:time,value:1 },{ observedAt:time,value:2 }] },
    { groupKey:'zoneB', groupLabel:'Zone B', metricKey:'b', label:'Actual temperature', points:[{ observedAt:time,value:3 }] }
  ] }
  let chart
  const deps = { vue:{ ...vue, onMounted:() => {}, onBeforeUnmount:() => {} },
    'vue-i18n':{ useI18n:() => ({ t:key => key }) },
    '@/utils/echarts':{ default:{ init:() => (chart=echarts.init(null,null,{ renderer:'svg', ssr:true, width:1000, height:400 })) }, getEChartsTheme:() => null },
    '@/utils/date':{ formatShanghaiDateTime:value => value }, '@/store/theme':{ useThemeStore:() => ({ theme:'light' }) },
    '@/components/common/ActionButton.vue':{}, './curveSeries':{ splitObservedPoints } }
  const scope = vue.effectScope()
  try {
    const component = new Function('deps', script)(deps)
    const state = scope.run(() => component.setup({ group, range:['2026-11-17T09:00:00+08:00','2026-11-17T11:00:00+08:00'] }, { expose() {} }))
    state.element.value = {}; state.render()
    const legend = chart.getOption().legend[0]
    assert.equal(new Set(legend.data).size, 2)
    assert.match(legend.formatter(legend.data[0]), /Zone A.*Actual temperature/)
    assert.match(legend.formatter(legend.data[1]), /Zone B.*Actual temperature/)
    const tooltip = chart.getOption().tooltip[0].formatter(legend.data.map((name, i) => ({ axisValue:1, marker:'', seriesName:name, value:[1,i], data:[1,i,time] })))
    assert.match(tooltip, /Zone A.*Actual temperature/)
    assert.match(tooltip, /Zone B.*Actual temperature/)
    const all = [0,1,2].map(i => chart.getModel().getSeriesByIndex(i))
    chart.dispatchAction({ type:'legendToggleSelect', name:legend.data[0] })
    assert.deepEqual(all.map(series => chart.getModel().isSeriesFiltered(series)), [true,true,false])
    group.series[0].groupLabel = '一区'; group.series[1].groupLabel = '二区'
    group.series.forEach(item => { item.label = '实际温度' })
    state.render()
    const localized = chart.getOption().legend[0]
    assert.match(localized.formatter(localized.data[0]), /一区.*实际温度/)
    assert.match(localized.formatter(localized.data[1]), /二区.*实际温度/)
    assert.equal(localized.selected[localized.data[0]], false)
    assert.deepEqual([0,1,2].map(i => chart.getModel().isSeriesFiltered(chart.getModel().getSeriesByIndex(i))), [true,true,false])
    chart.dispose()
    const identical = { ...group, series:group.series.map((item, index) => ({ ...item, groupLabel:'同名区域',
      groupKey:index ? 'zone' : 'zone / part', metricKey:index ? 'part / value' : 'value', label:'实际值' })) }
    const same = scope.run(() => component.setup({ group:identical, range:[] }, { expose() {} }))
    same.element.value = {}; same.render()
    const duplicate = chart.getOption().legend[0]
    assert.notEqual(duplicate.formatter(duplicate.data[0]), duplicate.formatter(duplicate.data[1]))
    chart.dispose()
    const escaped = { ...group, series:[{ ...group.series[0], groupLabel:'<区域&一>', label:'<实际值>' }] }
    const escapedState = scope.run(() => component.setup({ group:escaped, range:[] }, { expose() {} }))
    escapedState.element.value = {}; escapedState.render()
    const option = chart.getOption(), key = option.legend[0].data[0]
    const html = option.tooltip[0].formatter([{ axisValue:1, marker:'', seriesName:key, value:[1,1], data:[1,1,time] }])
    assert.match(html, /&lt;区域&amp;一&gt;.*&lt;实际值&gt;/)
    assert.doesNotMatch(html, /<区域|<实际值/)
  } finally { chart?.dispose(); scope.stop() }
})

test('slots initially load both targets, preserve submitted filters, and reject stale results', async () => {
  const source = await readFile(new URL('../../src/app/equipment/views/observations/admin.vue', import.meta.url), 'utf8')
  const script = compileScript(parse(source).descriptor, { id: 'observation-config' }).content
    .replace(/^import\s+([\s\S]+?)\s+from\s+['"](.+?)['"];?$/gm, (_line, binding, name) => {
      if (binding.startsWith('{')) binding = binding.replace(/\bas\b/g, ':')
      return `const ${binding} = deps[${JSON.stringify(name)}]`
    }).replace('export default', 'return')
  const hooks = [], requests = []
  const slot1 = { target: 'latest', groupKey: 'heatZone1', slotNo: 1, metricKey: 'actual', enabled: true }
  const slot2 = { target: 'history', groupKey: 'heatZone2', slotNo: 1, metricKey: 'set', enabled: false }
  const deps = {
    vue: { ...vue, onMounted: fn => hooks.push(fn), onBeforeUnmount: () => {} },
    'element-plus': {},
    'vue-i18n': { useI18n: () => ({ t: key => key, locale: vue.ref('zh-CN') }) },
    '@/components/common/ActionButton.vue': {}, '@/components/common/BaseCard.vue': {},
    '@/utils/date': {}, '@/utils/tableColumnWidths': { useTableColumnWidths },
    '../../api/observations': {
      metricGroups: async () => [{ groupKey: 'heatZone1' }, { groupKey: 'heatZone2' }],
      metrics: async () => [{ metricKey: 'set', nameZh: '设定值', nameEn: 'Set temperature' }],
      cards: async () => [],
      bindings: params => { const wait = deferred(); requests.push({ params, ...wait }); return wait.promise }
    }
  }
  const scope = vue.effectScope()
  const settle = () => new Promise(resolve => setImmediate(resolve))
  try {
    const component = new Function('deps', script)(deps)
    const state = scope.run(() => component.setup({}, { expose() {} }))
    await hooks[0]()
    state.selectTab('slot')
    assert.deepEqual(requests[0].params, { target: undefined, groupKey: undefined })
    requests[0].resolve({ items: [slot1, slot2] })
    await settle()
    assert.deepEqual(state.visibleRows.value, [slot1, slot2])
    state.draft.scope = 'heatZone2'; state.draft.target = 'history'; state.draft.keyword = ' SET TEMPERATURE '
    assert.deepEqual(state.visibleRows.value, [slot1, slot2])
    state.search()
    assert.deepEqual(requests[1].params, { target: 'history', groupKey: 'heatZone2' })
    requests[1].resolve({ items: [slot2] })
    await settle()
    assert.deepEqual(state.visibleRows.value, [slot2])
    state.draft.keyword = 'unsubmitted'
    state.selectTab('group')
    state.selectTab('slot')
    assert.equal(state.draft.keyword, 'SET TEMPERATURE')
    state.resetFilters()
    assert.deepEqual(requests[3].params, { target: undefined, groupKey: undefined })
    requests[3].resolve({ items: [slot1, slot2] })
    await settle()
    requests[2].reject(new Error('old lookup'))
    await settle()
    assert.deepEqual(state.visibleRows.value, [slot1, slot2])
    assert.equal(state.failed.value, false)
  } finally { scope.stop() }
})
