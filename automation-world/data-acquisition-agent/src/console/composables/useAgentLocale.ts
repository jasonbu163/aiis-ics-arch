/**
 * File Path: /automation-world/data-acquisition-agent/src/console/composables/useAgentLocale.ts
 * Description: Local locale preference state for the Data Acquisition Agent console shell
 * Main Features:
 *   - Maps vue-i18n locale to Element Plus locale packs
 *   - Persists the CA console locale preference
 *   - Exposes localized language toggle labels
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import en from 'element-plus/es/locale/lang/en'
import { persistLocale } from '../../locales'

export function useAgentLocale() {
  const { t, locale } = useI18n()

  const elementLocale = computed(() => {
    return locale.value === 'zh-CN' ? zhCn : en
  })

  const localeSwitchLabel = computed(() => {
    return locale.value === 'zh-CN'
      ? t('common.actions.switchToEnglish')
      : t('common.actions.switchToChinese')
  })

  const toggleLocale = () => {
    const nextLocale = locale.value === 'zh-CN' ? 'en-US' : 'zh-CN'
    locale.value = nextLocale
    persistLocale(nextLocale)
  }

  return {
    appLocale: computed(() => locale.value as 'zh-CN' | 'en-US'),
    elementLocale,
    localeSwitchLabel,
    toggleLocale
  }
}
