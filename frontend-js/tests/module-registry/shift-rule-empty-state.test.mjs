/** 编译实际排班SFC，验证合法null、禁止误写及已有规则/错误的双语回归。 */
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { parse, compileScript } from 'vue/compiler-sfc'
import * as vue from 'vue'
import { createI18n } from 'vue-i18n'
import { loadRegistry } from '../../scripts/check-module-manifests.mjs'
const source = await readFile(new URL('../../src/app/auxiliary/views/shift/index.vue', import.meta.url), 'utf8')
const { descriptor } = parse(source)
const script = compileScript(descriptor, { id: 'shift-rule-test' }).content
const executable = script.replace(/^import\s+([\s\S]+?)\s+from\s+['"](.+?)['"];?$/gm, (_line, binding, module) => {
  if (binding.startsWith('{')) binding = binding.replace(/\bas\b/g, ':')
  return `const ${binding} = deps[${JSON.stringify(module)}]`
}).replace('export default', 'return')
const makeComponent = new Function('deps', executable)
const registry = await loadRegistry(new URL('../../', import.meta.url).pathname)
const saved = { id: 7, name: 'existing', shiftMode: 'two_shift', cycleName: 'approved cycle', dayShiftStart: '07:00', dayShiftEnd: '19:00', nightShiftStart: '19:00', nightShiftEnd: '07:00' }
function page(value, locale, { putError = false } = {}) {
  const messages = [], puts = []
  const i18n = createI18n({ legacy: false, locale, messages: registry.messages })
  const component = makeComponent({
    vue: { ...vue, onMounted: () => {} },
    'vue-i18n': { useI18n: () => i18n.global },
    'element-plus': { ElMessage: { error: text => messages.push(['error', text]), success: text => messages.push(['success', text]) } },
    '@/store/user': { useUserStore: () => ({ role: 'admin' }) },
    '@/components/common/ActionButton.vue': {}, '@/components/common/BaseCard.vue': {},
    '@/app/auxiliary/api': {
      getShiftRule: async () => { if (value instanceof Error) throw value; return value },
      getShiftTeamList: async () => ({ items: [] }), getShiftList: async () => ({ items: [], total: 0 }),
      updateShiftRule: async (id, data) => { puts.push({ id, data }); if (putError) throw new Error("fixture PUT failure"); return { ...data, id } }
    }
  })
  return { state: component.setup({}, { expose() {} }), messages, puts, i18n }
}
for (const locale of ['en-US', 'zh-CN']) {
  test(`actual SFC ${locale}: null is unconfigured, no error/default rule/edit/PUT`, async () => {
    const p = page(null, locale)
    await p.state.loadShiftRule()
    assert.equal(p.state.shiftRule.id, null)
    assert.equal(p.state.shiftRule.dayShiftStart, '')
    assert.equal(p.state.shiftRule.cycleName, '')
    assert.deepEqual(p.messages, [])
    p.state.handleEditRule()
    assert.equal(p.state.ruleDialogVisible.value, false)
    await p.state.handleRuleSubmit()
    assert.deepEqual(p.puts, [])
    assert.notEqual(p.i18n.global.t('auxiliary.shift.ruleNotConfigured'), 'auxiliary.shift.ruleNotConfigured')
    assert.match(descriptor.template.content, /v-if="shiftRule.id" class="rule-content"/)
    assert.match(descriptor.template.content, /v-if="canManageShift && shiftRule.id"/)
  })
  test(`actual SFC ${locale}: saved rule loads and existing PUT remains intact`, async () => {
    const p = page(saved, locale)
    await p.state.loadShiftRule()
    assert.equal(p.state.shiftRule.dayShiftStart, '07:00')
    p.state.handleEditRule()
    assert.equal(p.state.ruleDialogVisible.value, true)
    p.state.ruleForm.dayShiftStart = '06:30'
    await p.state.handleRuleSubmit()
    assert.equal(p.puts[0].id, 7)
    assert.equal(p.puts[0].data.dayShiftStart, '06:30')
    assert.equal(p.state.shiftRule.dayShiftStart, '06:30')
    assert.equal(p.state.ruleDialogVisible.value, false)
    assert.equal(p.messages[0][0], 'success')
  })
  test(`actual SFC ${locale}: existing rule PUT failure keeps dialog and saved state`, async () => {
    const p = page(saved, locale, { putError: true })
    await p.state.loadShiftRule()
    p.state.handleEditRule()
    p.state.ruleForm.dayShiftStart = '06:30'
    await p.state.handleRuleSubmit()
    assert.equal(p.puts.length, 1)
    assert.equal(p.state.ruleDialogVisible.value, true)
    assert.equal(p.state.shiftRule.dayShiftStart, '07:00')
    assert.deepEqual(p.messages, [['error', p.i18n.global.t('common.error')]])
  })
  test(`actual SFC ${locale}: API failure keeps error feedback`, async () => {
    const p = page(new Error('fixture'), locale)
    await p.state.loadShiftRule()
    assert.deepEqual(p.messages, [['error', p.i18n.global.t('common.error')]])
    assert.deepEqual(p.puts, [])
  })
}
