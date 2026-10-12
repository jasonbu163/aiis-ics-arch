/** 文件路径: /frontend-js/tests/module-registry/system-name.test.mjs
 * 功能描述: 双语独立默认、名称普通文本与实际 Vue I18n 消费合同。 */
import test from 'node:test'
import assert from 'node:assert/strict'
import { createI18n } from 'vue-i18n'
import { withSystemNames } from '../../src/config/systemName.js'

const defaults = {
  'zh-CN': { common: { systemTitle: '默认中文', save: '保存' }, login: { title: '登录' } },
  'en-US': { common: { systemTitle: 'English default', save: 'Save' }, login: { title: 'Login' } }
}
const translate = env => createI18n({ legacy: false, locale: 'zh-CN', messages: withSystemNames(defaults, env) }).global

test('missing, empty and whitespace names retain each locale default independently', () => {
  for (const value of [undefined, '', ' \t\n ']) {
    for (const env of [
      { VITE_SYSTEM_NAME_ZH_CN: value, VITE_SYSTEM_NAME_EN_US: value },
      { VITE_SYSTEM_NAME_ZH_CN: '中文配置', VITE_SYSTEM_NAME_EN_US: value },
      { VITE_SYSTEM_NAME_ZH_CN: value, VITE_SYSTEM_NAME_EN_US: 'Configured English' }
    ]) {
      const i18n = translate(env)
      assert.equal(i18n.t('common.systemTitle'), env.VITE_SYSTEM_NAME_ZH_CN?.trim() || '默认中文')
      i18n.locale.value = 'en-US'
      assert.equal(i18n.t('common.systemTitle'), env.VITE_SYSTEM_NAME_EN_US?.trim() || 'English default')
    }
  }
})

test('names trim only the edges and remain literal through i18n language switching', () => {
  const i18n = translate({ VITE_SYSTEM_NAME_ZH_CN: '  系统  A @ {name} | <b>字</b>!  ', VITE_SYSTEM_NAME_EN_US: '  System  B @ {name} | <b>Text</b>!  ' })
  assert.equal(i18n.t('common.systemTitle'), '系统  A @ {name} | <b>字</b>!')
  i18n.locale.value = 'en-US'
  assert.equal(i18n.t('common.systemTitle'), 'System  B @ {name} | <b>Text</b>!')
  assert.equal(i18n.t('common.save'), 'Save')
  assert.equal(i18n.t('login.title'), 'Login')
  assert.equal(defaults['zh-CN'].common.systemTitle, '默认中文')
  assert.equal(defaults['en-US'].common.systemTitle, 'English default')
})


test('optional descriptions remain empty per language without fallback or borrowed names', () => {
  for (const value of [undefined, '', ' \t\n ']) {
    for (const env of [
      { VITE_SYSTEM_SUBTITLE_ZH_CN: value, VITE_SYSTEM_SUBTITLE_EN_US: value },
      { VITE_SYSTEM_SUBTITLE_ZH_CN: '中文描述', VITE_SYSTEM_SUBTITLE_EN_US: value },
      { VITE_SYSTEM_SUBTITLE_ZH_CN: value, VITE_SYSTEM_SUBTITLE_EN_US: 'English description' }
    ]) {
      const i18n = translate(env)
      assert.equal(i18n.t('login.subtitle'), env.VITE_SYSTEM_SUBTITLE_ZH_CN?.trim() || '')
      assert.equal(i18n.t('common.systemTitle'), '默认中文')
      i18n.locale.value = 'en-US'
      assert.equal(i18n.t('login.subtitle'), env.VITE_SYSTEM_SUBTITLE_EN_US?.trim() || '')
      assert.equal(i18n.t('common.systemTitle'), 'English default')
    }
  }
})

test('descriptions preserve literal text independently of system names and leave source messages intact', () => {
  const i18n = translate({
    VITE_SYSTEM_NAME_ZH_CN: '系统名', VITE_SYSTEM_NAME_EN_US: 'System name',
    VITE_SYSTEM_SUBTITLE_ZH_CN: '  描述  @ {A} | <b>文本</b>  ',
    VITE_SYSTEM_SUBTITLE_EN_US: '  Description  @ {A} | <b>Text</b>  '
  })
  assert.equal(i18n.t('login.subtitle'), '描述  @ {A} | <b>文本</b>')
  assert.equal(i18n.t('common.systemTitle'), '系统名')
  i18n.locale.value = 'en-US'
  assert.equal(i18n.t('login.subtitle'), 'Description  @ {A} | <b>Text</b>')
  assert.equal(i18n.t('common.systemTitle'), 'System name')
  assert.equal(i18n.t('login.title'), 'Login')
  assert.equal(defaults['zh-CN'].login.subtitle, undefined)
  assert.equal(defaults['en-US'].login.subtitle, undefined)
})
