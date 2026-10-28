/** DAA-007纯前端合同：既有TypeScript编译通道、多个宿主TZ及本机偏好，产物仅临时目录。 */
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { execFileSync } from 'node:child_process'
import { readFileSync } from 'node:fs'
import { createRequire } from 'node:module'
const require = createRequire(import.meta.url)
const ts = require('typescript')
function load(relative) {
  const source = readFileSync(new URL(relative, import.meta.url), 'utf8')
  const code = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText
  const module = { exports: {} }; new Function('module', 'exports', code)(module, module.exports); return module.exports
}
const time = load('../src/console/time.ts'), prefs = load('../src/console/tableWidths.ts')
test('Shanghai wall time, inclusive final millisecond and invalid inputs', () => {
  assert.equal(time.formatBusinessTime('2026-10-22T16:00:00.999Z'), '2026-10-23 00:00:00')
  assert.equal(time.formatBusinessTime('2026-10-22T12:00:00.123-04:00'), '2026-10-23 00:00:00')
  assert.equal(time.historyBoundary('2026-10-23T00:00:00', false), '2026-10-23T00:00:00.000+08:00')
  assert.equal(time.historyBoundary('2026-10-23T00:00:00', true), '2026-10-23T00:00:00.999+08:00')
  assert.equal(time.historyBoundary('2026-02-30T00:00:00', false), '')
  assert.equal(time.formatBusinessTime('123'), '—'); assert.equal(time.formatBusinessTime('2026-10-23T00:00:00'), '—'); assert.equal(time.formatBusinessTime(null), '—'); assert.equal(time.historyBoundary('', true), '')
})
test('the same helper result under UTC, Shanghai and Los Angeles host zones', () => {
  const source = ts.transpileModule(readFileSync(new URL('../src/console/time.ts', import.meta.url), 'utf8'), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText
  const script = `${source}\nconsole.log(JSON.stringify([exports.formatBusinessTime('2026-10-22T16:00:00.999Z'),exports.historyBoundary('2026-10-23T00:00:00',true)]))`
  const values = ['UTC', 'Asia/Shanghai', 'America/Los_Angeles'].map(TZ => execFileSync(process.execPath, ['-e', script], { env: { ...process.env, TZ }, encoding: 'utf8' }).trim())
  assert.equal(new Set(values).size, 1)
})
test('stable app/table keys, minimum, reload, invalid field and reset', () => {
  const data = new Map(), storage = { getItem: key => data.get(key) ?? null, setItem: (key,v) => data.set(key,v), removeItem: key => data.delete(key) }
  const columns = [{ id: 'savedAt', width: 210, min: 200 },{ id: 'plcId', width: 180, min: 150 }]
  const key = prefs.widthKey('daa','history'), other = prefs.widthKey('ds','history'), page = prefs.widthKey('daa','other')
  let widths=prefs.loadWidths(storage,key,columns); widths=prefs.saveWidth(storage,key,columns,widths,'savedAt',300)
  assert.equal(prefs.loadWidths(storage,key,columns).savedAt,300)
  assert.equal(prefs.loadWidths(storage,other,columns).savedAt,210); assert.equal(prefs.loadWidths(storage,page,columns).savedAt,210)
  widths=prefs.saveWidth(storage,key,columns,widths,'plcId',10); assert.equal(widths.plcId,150)
  assert.deepEqual(prefs.resetWidths(storage,key,columns),{savedAt:210,plcId:180}); assert.equal(data.has(key),false)
  storage.setItem(key,'{"removed":999,"savedAt":-2,"plcId":"bad"}'); assert.deepEqual(prefs.loadWidths(storage,key,columns),{savedAt:210,plcId:180})
  storage.setItem(key,'broken'); assert.deepEqual(prefs.loadWidths(storage,key,columns),{savedAt:210,plcId:180})
})
