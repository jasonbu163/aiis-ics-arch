import assert from 'node:assert/strict'
import test from 'node:test'

import {
  displayParentCoilNo,
  displayText,
  durationSourceKey,
  formatBackendDuration,
  formatNullableNumber,
  isRootPerformance,
  normalizeNullableDateTime,
  normalizeNullableNumber,
  observationStatusKey
} from './performance-presentation.mjs'

test('real API performance rows render root and child parent coils without null truthiness', () => {
  const root = { coilNo: 'ROOT-001', parentCoilNo: 'ROOT-001' }
  const child = { coilNo: 'ROOT-001-1', parentCoilNo: 'ROOT-001' }

  assert.equal(isRootPerformance(root), true)
  assert.equal(displayParentCoilNo(root), 'ROOT-001')
  assert.equal(isRootPerformance(child), false)
  assert.equal(displayParentCoilNo(child), 'ROOT-001')
})

test('nullable numeric performance fields preserve empty values and display zero', () => {
  assert.equal(formatNullableNumber(null, 2), '-')
  assert.equal(formatNullableNumber('', 2), '-')
  assert.equal(formatNullableNumber(0, 2), '0.00')
  assert.equal(formatNullableNumber('12.3', 2), '12.30')

  assert.equal(normalizeNullableNumber(null), null)
  assert.equal(normalizeNullableNumber(''), null)
  assert.equal(normalizeNullableNumber(0), 0)
  assert.equal(normalizeNullableNumber('12.3'), 12.3)
})

test('performance duration uses backend seconds only', () => {
  const translate = (key) => ({
    'common.unit.hour': 'h',
    'common.unit.min': 'm',
    'performance.durationUnits.second': 's'
  })[key]

  assert.equal(formatBackendDuration(null, translate), '-')
  assert.equal(formatBackendDuration(0, translate), '0s')
  assert.equal(formatBackendDuration(65, translate), '1m5s')
  assert.equal(formatBackendDuration(3661, translate), '1h1m1s')
})

test('status and optional datetime display use stable fallback keys', () => {
  assert.equal(observationStatusKey(null), 'manual_historical')
  assert.equal(observationStatusKey('in_production'), 'in_production')
  assert.equal(durationSourceKey(null), 'unavailable')
  assert.equal(durationSourceKey('manual_time'), 'manual_time')
  assert.equal(normalizeNullableDateTime(''), null)
  assert.equal(normalizeNullableDateTime('2026-07-23 12:00:00'), '2026-07-23 12:00:00')
  assert.equal(displayText(''), '-')
  assert.equal(displayText('S-01'), 'S-01')
})
