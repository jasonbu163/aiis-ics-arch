/**
 * 文件路径: /frontend-js/src/locales/index.js
 * 功能描述: Vue I18n 国际化配置
 * 主要功能:
 *   - 加载语言文件
 *   - 配置 i18n 实例
 *   - 导出 i18n 供全局使用
 */
import { createI18n } from 'vue-i18n'

// 英文翻译文件
import enCommon from './en-US/common.json'
import enNav from './en-US/nav.json'
import enLogin from './en-US/login.json'
import enLanguage from './en-US/language.json'
import enBreadcrumb from './en-US/breadcrumb.json'

// 中文翻译文件
import zhCommon from './zh-CN/common.json'
import zhNav from './zh-CN/nav.json'
import zhLogin from './zh-CN/login.json'
import zhLanguage from './zh-CN/language.json'
import zhBreadcrumb from './zh-CN/breadcrumb.json'

export const availableLocales = [
  { code: 'zh-CN', name: '中文' },
  { code: 'en-US', name: 'English' }
]

const availableLocaleCodes = availableLocales.map(locale => locale.code)

const moduleLocaleFiles = import.meta.glob('../app/*/locales/*.json', {
  eager: true,
  import: 'default'
})

const globalMessages = {
  'en-US': {
    common: enCommon,
    nav: enNav,
    login: enLogin,
    language: enLanguage,
    breadcrumb: enBreadcrumb
  },
  'zh-CN': {
    common: zhCommon,
    nav: zhNav,
    login: zhLogin,
    language: zhLanguage,
    breadcrumb: zhBreadcrumb
  }
}

const getLocaleFileInfo = (path) => {
  const match = path.match(/\/app\/([^/]+)\/locales\/(.+)\.json$/)

  if (!match) {
    throw new Error(`[i18n] Invalid module locale path: ${path}`)
  }

  const [, moduleName, fileName] = match
  const localeCode = availableLocaleCodes.find(locale => {
    return fileName === locale || fileName.endsWith(`.${locale}`)
  })

  if (!localeCode) {
    throw new Error(`[i18n] Unsupported module locale file: ${path}`)
  }

  const namespace = fileName === localeCode
    ? moduleName
    : fileName.slice(0, -`.${localeCode}`.length)

  return {
    localeCode,
    namespace,
    path
  }
}

const buildMessages = (localeCode) => {
  const messagesForLocale = { ...globalMessages[localeCode] }

  Object.entries(moduleLocaleFiles)
    .map(([path, messages]) => ({
      ...getLocaleFileInfo(path),
      messages
    }))
    .filter(localeFile => localeFile.localeCode === localeCode)
    .sort((current, next) => current.namespace.localeCompare(next.namespace) || current.path.localeCompare(next.path))
    .forEach(localeFile => {
      messagesForLocale[localeFile.namespace] = {
        ...(messagesForLocale[localeFile.namespace] || {}),
        ...localeFile.messages
      }
    })

  return messagesForLocale
}

const messages = {
  'zh-CN': buildMessages('zh-CN'),
  'en-US': buildMessages('en-US')
}

const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('locale') || 'zh-CN',
  fallbackLocale: 'zh-CN',
  messages
})

export default i18n
