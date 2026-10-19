/** 纯壳层：四叶导航与既有主题/语言偏好；无IPC、运行快照或刷新副作用。 */
import { ref } from 'vue'
import type { ConsoleSectionId } from '../types'
import { useAgentLocale } from './useAgentLocale'
import { useAgentTheme } from './useAgentTheme'
export function useAgentConsoleShell() {
  const activeSection = ref<ConsoleSectionId>('workbench')
  return { activeSection, ...useAgentLocale(), ...useAgentTheme() }
}
