/** URL来源与请求代次的行为边界；不调用真实API。 */
import test from 'node:test'
import assert from 'node:assert/strict'
import { parseBusinessDataSource, businessDataSourceQuery, requireBusinessSource, createRequestGeneration } from './businessDataSource.mjs'
test('default legacy, explicit HTTP equipment and invalid source remain distinct', () => {
  assert.equal(parseBusinessDataSource({}).dataSource, 'legacy')
  assert.equal(parseBusinessDataSource({dataSource:'http'}).ready, false)
  assert.equal(parseBusinessDataSource({dataSource:'unexpected'}).valid, false)
  assert.throws(() => requireBusinessSource({dataSource:'http'}))
  assert.throws(() => requireBusinessSource({dataSource:'unexpected',equipmentId:'A'}))
  assert.deepEqual(businessDataSourceQuery({date:'2026-10-16'}, {dataSource:'http',equipmentId:'Line-A'}), {date:'2026-10-16',dataSource:'http',equipmentId:'Line-A'})
})
test('late requests cannot overwrite a newer selection or refresh', async () => {
  const gate=createRequestGeneration()
  const old=gate.begin();gate.invalidate();const next=gate.begin()
  assert.equal(gate.isCurrent(old),false)
  assert.equal(gate.isCurrent(next),true)
})
