/** 能耗曲线工作区、双语文案及与后端一致的序列校验。 */
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { curveIssue, curveTitle } from '../../src/app/energy/components/energyCurveGroups.js'

const source = file => readFile(new URL('../../src/app/energy/' + file, import.meta.url), 'utf8')
const metric = (metricKey, quantityKey, unit, enabled = true) => ({ metricKey, quantityKey, unit, enabled, valueType: 'number' })
const line = (metricKey, enabled = true) => ({ metricKey, enabled })

test('energy curve ordering and validation ignore the metric write flag', () => {
  const definitions = [metric('zero', 'power', undefined), metric('spare', 'power', '', false),
    metric('other', 'energy', ''), metric('watt', 'power', 'W')]
  assert.equal(curveIssue([line('spare'), line('zero')], definitions), '')
  assert.equal(curveIssue([line('other', false), line('zero')], definitions), '')
  assert.equal(curveIssue([line('zero'), line('zero', false)], definitions), 'duplicateMetric')
  assert.equal(curveIssue([line('zero'), line('other')], definitions), 'mixedUnits')
  assert.equal(curveIssue([line('zero'), line('watt')], definitions), 'mixedUnits')
  assert.equal(curveIssue([line('spare', false)], definitions), 'requiresEnabled')
  assert.equal(curveIssue([line('missing', false), line('spare')], definitions), 'invalidMetrics')
  const config = { titleZh: '功率', titleEn: '', curveGroupKey: 'power' }
  assert.equal(curveTitle(config, 'en-US'), '功率')
  assert.equal(curveTitle({ ...config, titleZh: '', titleEn: 'Power' }, 'zh-CN'), 'Power')
})

test('curve settings are in the energy admin workspace with matching locale keys', async () => {
  const [admin, dialog, en, zh] = await Promise.all([
    source('views/admin.vue'), source('components/EnergyCurveGroups.vue'),
    source('locales/en-US.json').then(JSON.parse), source('locales/zh-CN.json').then(JSON.parse)
  ])
  assert.match(admin, /value="curves"[^\n]*energy\.curves\.title/)
  assert.match(admin, /<EnergyCurveGroups v-else-if="active === 'curves'/)
  assert.match(dialog, /useTableColumnWidths\('energy\.curve-groups'/)
  assert.match(dialog, /:close-on-click-modal="true"/)
  assert.deepEqual(Object.keys(en.curves).sort(), Object.keys(zh.curves).sort())
})
