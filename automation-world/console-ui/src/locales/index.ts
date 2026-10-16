/** CU 私有 i18n 实例：只读取 cu.locale，不迁移其他 Agent 偏好。 */
import { createI18n } from 'vue-i18n'
import en from './en-US/workbench.json'
import zh from './zh-CN/workbench.json'
const stored = localStorage.getItem('cu.locale')
const locale = stored === 'zh-CN' || stored === 'en-US' ? stored : navigator.language.startsWith('zh') ? 'zh-CN' : 'en-US'
export const i18n = createI18n({ legacy: false, locale, fallbackLocale: 'en-US', messages: { 'en-US': { workbench: en }, 'zh-CN': { workbench: zh } } })
