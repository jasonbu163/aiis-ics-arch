/**
 * File Path: /control-agent/src/console/composables/useAgentTheme.ts
 * Description: Local theme preference state for the Control Agent console shell
 * Main Features:
 *   - Resolves the initial light/dark theme
 *   - Applies CA theme attributes and color-scheme values
 *   - Exposes localized theme toggle labels
 */
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

export type AgentTheme = 'light' | 'dark'

const THEME_STORAGE_KEY = 'control-agent.theme'

function resolveInitialTheme(): AgentTheme {
  if (typeof window === 'undefined') {
    return 'light'
  }

  const storedTheme = window.localStorage.getItem(THEME_STORAGE_KEY)

  if (storedTheme === 'light' || storedTheme === 'dark') {
    return storedTheme
  }

  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function applyAgentTheme(theme: AgentTheme) {
  if (typeof document === 'undefined') {
    return
  }

  document.documentElement.setAttribute('data-agent-theme', theme)
  document.documentElement.style.colorScheme = theme
  window.localStorage.setItem(THEME_STORAGE_KEY, theme)
}

export function useAgentTheme() {
  const { t } = useI18n()
  const agentTheme = ref<AgentTheme>(resolveInitialTheme())

  applyAgentTheme(agentTheme.value)

  const isDarkTheme = computed(() => {
    return agentTheme.value === 'dark'
  })

  const themeSwitchLabel = computed(() => {
    return isDarkTheme.value ? t('common.actions.switchToLight') : t('common.actions.switchToDark')
  })

  const toggleTheme = () => {
    agentTheme.value = isDarkTheme.value ? 'light' : 'dark'
    applyAgentTheme(agentTheme.value)
  }

  return {
    agentTheme,
    isDarkTheme,
    themeSwitchLabel,
    toggleTheme
  }
}
