/**
 * 文件路径: /frontend-js/src/locales/index.js
 * 功能描述: 使用 Registry 已筛选的全局与活动模块文案创建 Vue I18n。
 */
import { createI18n } from 'vue-i18n'
import { messages } from '@/app/moduleRegistry'

export const availableLocales = [
  { code: 'zh-CN', name: '中文' },
  { code: 'en-US', name: 'English' }
]

const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('locale') || 'zh-CN',
  fallbackLocale: 'zh-CN',
  messages
})

export default i18n
