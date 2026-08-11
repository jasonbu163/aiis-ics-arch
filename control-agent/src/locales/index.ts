/**
 * File Path: /control-agent/src/locales/index.ts
 * Description: Control Agent i18n setup
 * Main Features:
 *   - Assembles global and module-owned English and Chinese translations
 *   - Auto-discovers locale files from vertical app modules
 *   - Uses browser language as the initial locale
 *   - Keeps user-visible text out of Vue templates
 */
import { createI18n } from 'vue-i18n'
import enCommon from './en-US/common.json'
import enNavigation from './en-US/navigation.json'
import zhCommon from './zh-CN/common.json'
import zhNavigation from './zh-CN/navigation.json'

type LocaleKey = 'en-US' | 'zh-CN'
interface LocaleMessages {
  [key: string]: string | LocaleMessages
}

const STORAGE_KEY = 'aiis-ics-control-agent-locale'
const localeCodes: readonly LocaleKey[] = ['en-US', 'zh-CN']

const moduleLocaleFiles = import.meta.glob<LocaleMessages>('../app/*/locales/*.json', {
  eager: true,
  import: 'default'
})

const globalMessages: Record<LocaleKey, LocaleMessages> = {
  'en-US': {
    common: enCommon,
    navigation: enNavigation
  },
  'zh-CN': {
    common: zhCommon,
    navigation: zhNavigation
  }
}

const getModuleLocaleInfo = (filePath: string) => {
  const match = filePath.match(/\/app\/([^/]+)\/locales\/(en-US|zh-CN)\.json$/)

  if (!match) {
    throw new Error(`[i18n] Invalid module locale path: ${filePath}`)
  }

  const [, moduleName, localeCode] = match

  if (!localeCodes.includes(localeCode as LocaleKey)) {
    throw new Error(`[i18n] Unsupported module locale file: ${filePath}`)
  }

  return {
    moduleName,
    localeCode: localeCode as LocaleKey,
    filePath
  }
}

const buildMessages = (localeCode: LocaleKey): LocaleMessages => {
  const messagesForLocale: LocaleMessages = { ...globalMessages[localeCode] }

  Object.entries(moduleLocaleFiles)
    .map(([filePath, messages]) => ({
      ...getModuleLocaleInfo(filePath),
      messages
    }))
    .filter((localeFile) => localeFile.localeCode === localeCode)
    .sort(
      (current, next) =>
        current.moduleName.localeCompare(next.moduleName) ||
        current.filePath.localeCompare(next.filePath)
    )
    .forEach((localeFile) => {
      messagesForLocale[localeFile.moduleName] = localeFile.messages
    })

  return messagesForLocale
}

export const localeMessages: Record<LocaleKey, LocaleMessages> = {
  'en-US': buildMessages('en-US'),
  'zh-CN': buildMessages('zh-CN')
}

const pickLocale = (): LocaleKey => {
  const storedLocale = localStorage.getItem(STORAGE_KEY)
  if (storedLocale === 'en-US' || storedLocale === 'zh-CN') {
    return storedLocale
  }

  return navigator.language.toLowerCase().startsWith('zh') ? 'zh-CN' : 'en-US'
}

export const persistLocale = (locale: LocaleKey) => {
  localStorage.setItem(STORAGE_KEY, locale)
}

export const i18n = createI18n({
  legacy: false,
  locale: pickLocale(),
  fallbackLocale: 'en-US',
  messages: localeMessages
})
