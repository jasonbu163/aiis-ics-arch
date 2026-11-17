/** r7 设备页面装配和过程缺样曲线回归。 */
import test from 'node:test'
import assert from 'node:assert/strict'
import { fileURLToPath } from 'node:url'
import { loadRegistry } from '../../scripts/check-module-manifests.mjs'
import { splitObservedPoints } from '../../src/app/monitor/components/observations/curveSeries.js'

const root = fileURLToPath(new URL('../../', import.meta.url))

test('four equipment and three history pages use configured views with restricted admin routes', async () => {
  const registry = await loadRegistry(root)
  const routes = registry.routes
  const page = id => routes.find(route => route.meta?.pageId === id)
  for (const id of ['equipment.production-parameters', 'equipment.cleaning', 'equipment.temperature', 'equipment.drive',
    'monitor.temperature', 'monitor.drive', 'monitor.cleaning']) {
    assert.ok(page(id), id)
  }
  assert.equal(page('monitor.realtime'), undefined)
  assert.ok(page('monitor.energy'))
  assert.ok(page('acquisition-data.realtime'))
  assert.equal(page('equipment.observations.admin').meta.requiresAdmin, true)
  assert.equal(page('monitor.observations.admin').meta.requiresAdmin, true)
})

test('history preserves observed times and breaks missing intervals', () => {
  const points = [
    { observedAt: '2026-11-11T10:00:00+08:00', value: 0 },
    { observedAt: '2026-11-11T10:00:10+08:00', value: 1 },
    { observedAt: '2026-11-11T10:00:30+08:00', value: 2 }
  ]
  const output = splitObservedPoints(points, 10).line
  assert.deepEqual(output.map(point => point[1]), [0, 1, null, 2])
  assert.equal(output[0][0], Date.parse(points[0].observedAt))
  assert.equal(output[2][0], Date.parse(points[2].observedAt))
  assert.equal(output[3][0], Date.parse(points[2].observedAt))
  assert.equal(points.length, 3)
})

test('same-time samples stay visible without a guessed line order and true missing values break lines', () => {
  const t = '2026-11-11T10:00:00+08:00'
  const result = splitObservedPoints([{ observedAt: t, value: 1 }, { observedAt: t, value: 2 },
    { observedAt: '2026-11-11T10:00:01+08:00', present: false, value: null }])
  assert.deepEqual(result.simultaneous.map(point => point[1]), [1, 2])
  assert.equal(result.line.every(point => point[1] === null), true)
})

test('different microseconds remain in chronological order while equivalent instants are simultaneous', () => {
  const points = [
    { observedAt: '2026-11-17T10:00:00.123001+08:00', value: 10 },
    { observedAt: '2026-11-17T10:00:00.123999+08:00', value: 20 },
    { observedAt: '2026-11-17T02:00:00.124001Z', value: 30 },
    { observedAt: '2026-11-17T10:00:00.124001+08:00', value: 40 }
  ]
  const result = splitObservedPoints(points, null)
  assert.deepEqual(result.line.map(point => point[1]), [10, 20, null])
  assert.ok(result.line[0][0] < result.line[1][0])
  assert.deepEqual(result.simultaneous.map(point => point[1]), [30, 40])
  assert.equal(result.simultaneous[0][0], result.simultaneous[1][0])
})

test('gap threshold compares exact microseconds, not rounded chart coordinates', () => {
  const result = splitObservedPoints([
    { observedAt: '2026-11-17T10:00:00.000001+08:00', value: 1 },
    { observedAt: '2026-11-17T10:00:01.000001+08:00', value: 2 },
    { observedAt: '2026-11-17T10:00:02.000002+08:00', value: 3 }
  ], 1)
  assert.deepEqual(result.line.map(point => point[1]), [1, 2, null, 3])
})

test('extremely wide ranges report coordinate collisions without merging distinct observed events', () => {
  const points = [
    { observedAt: '2600-01-01T00:00:00.123001Z', value: 1 },
    { observedAt: '2600-01-01T00:00:00.123002Z', value: 2 }
  ]
  const result = splitObservedPoints(points, null, Date.parse('2300-01-01T00:00:00Z'))
  assert.equal(result.precisionLimited, true)
  assert.deepEqual(result.line.map(point => point[1]), [1, 2])
  assert.deepEqual(result.line.map(point => point[2]), points.map(point => point.observedAt))
  assert.deepEqual(result.simultaneous, [])
})
