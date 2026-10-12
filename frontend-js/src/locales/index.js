/**
 * 文件路径: /frontend-js/src/locales/index.js
 * 功能描述: 使用 Registry 已筛选的全局与活动模块文案创建 Vue I18n，并接入双语系统名称与可选登录描述。
 */
import { createI18n } from 'vue-i18n'
import { messages } from '@/app/moduleRegistry'
import { withSystemNames } from '@/config/systemName'

export const availableLocales = [
  { code: 'zh-CN', name: '中文' },
  { code: 'en-US', name: 'English' }
]

const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('locale') || 'zh-CN',
  fallbackLocale: 'zh-CN',
  messages: withSystemNames(messages, import.meta.env)
})

export default i18n
