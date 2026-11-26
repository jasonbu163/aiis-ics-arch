/** 能耗来源登记仅通过管理员配置页和独立登录 API 装配。 */
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import manifest from '../../src/app/energy/manifest.js'

const source = filepath => readFile(new URL('../../src/app/energy/' + filepath, import.meta.url), 'utf8')

test('energy admin opens meter metrics by default and keeps the existing workspaces in order alongside pricing and curves', async () => {
  const [view, metrics, meters, en, zh] = await Promise.all([
    source('views/admin.vue'), source('components/EnergyAdmin.vue'), source('components/EnergyMeters.vue'),
    source('locales/en-US.json').then(JSON.parse), source('locales/zh-CN.json').then(JSON.parse)
  ])
  const workspaces = [...view.matchAll(/<el-radio-button value="(\w+)"/g)].map(match => match[1])
  assert.deepEqual(workspaces, ['meters', 'metrics', 'sources', 'prices', 'curves'])
  assert.match(view, /const active = ref\('metrics'\)/)
  assert.match(view, /<EnergyMeters v-if="active === 'meters'" \/>/)
  assert.match(view, /<EnergyAdmin v-else-if="active === 'metrics'" kind="config" \/>/)
  assert.doesNotMatch(metrics, /manage-meters/)
  assert.doesNotMatch(meters, /meter\('back'\)/)
  assert.deepEqual(Object.keys(en.meters).sort(), Object.keys(zh.meters).sort())
  assert.equal(en.meters.title, 'Meter management')
  assert.equal(zh.meters.title, '表计管理')
})

test('write registration remains in the energy admin configuration route and keeps bilingual strings', async () => {
  const admin = manifest.routes.find(route => route.name === 'EnergyObservationAdmin')
  assert.equal(admin.meta.requiresAdmin, true)
  assert.equal(admin.path, 'energy/observations/admin')
  const [view, panel, en, zh] = await Promise.all([
    source('views/admin.vue'), source('components/EnergyWriteSources.vue'),
    source('locales/en-US.json').then(JSON.parse), source('locales/zh-CN.json').then(JSON.parse)
  ])
  assert.match(view, /value="metrics"[^\n]*energy\.observation\.energyConfig/)
  assert.match(view, /value="sources"[^\n]*energy\.writeSources\.title/)
  assert.match(view, /<EnergyWriteSources v-else/)
  assert.deepEqual(Object.keys(en.writeSources).sort(), Object.keys(zh.writeSources).sort())
  for (const language of [en, zh]) {
    assert.ok(Object.values(language.writeSources).every(value => value.trim()))
  }
  assert.equal((panel.match(/:close-on-click-modal="true"/g) || []).length, 2)
  assert.match(panel, /useTableColumnWidths\('energy\.writeSources'/)
})

test('registry actions use only the energy JWT request client and encode literal dot path segments', async () => {
  const api = (await source('api/observations.js')).replace("import request from '@/utils/request'", 'const request = globalThis.__energyWriteSourcesFixture')
  const calls = []
  globalThis.__energyWriteSourcesFixture = Object.fromEntries(['get', 'post', 'patch', 'delete'].map(method =>
    [method, (...args) => calls.push([method, ...args])]
  ))
  try {
    const endpoints = await import('data:text/javascript;base64,' + Buffer.from(api).toString('base64'))
    endpoints.energyWriteSources()
    endpoints.createEnergyWriteSource({ sourceKey: '.' })
    endpoints.updateEnergyWriteSource('..', { enabled: false })
    endpoints.deleteEnergyWriteSource('A-01')
  } finally {
    delete globalThis.__energyWriteSourcesFixture
  }
  assert.deepEqual(calls.map(([method, path]) => [method, path]), [
    ['get', '/energy/write-sources'], ['post', '/energy/write-sources'],
    ['patch', '/energy/write-sources/%252E%252E'], ['delete', '/energy/write-sources/A-01']
  ])
})
