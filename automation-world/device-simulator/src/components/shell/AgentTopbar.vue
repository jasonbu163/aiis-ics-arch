<!-- DS 顶栏薄适配：所有状态/偏好仍归宿主，通过 CU 公共控件组合。 -->
<template>
  <CuTopbar
    :title="t(activeSection.titleKey)"
    :subtitle="t('common.app.subtitle')"
    :sidebar-label="t('common.actions.toggleSidebar')"
    :sidebar-hidden="isSidebarHidden"
    @toggle-sidebar="emit('toggle-sidebar')"
  >
    <template #actions>
      <RuntimeStatusCapsule :status-text="modeStatusText" />
      <StatusCapsule :label="ipcStatusText" tone="neutral" />
      <ThemeToggle
        :theme="isDarkTheme?'dark':'light'"
        :label="themeSwitchLabel"
        @toggle="emit('toggle-theme')"
      />
      <LanguageSwitch
        :locale="appLocale"
        :zh-label="t('common.actions.switchToChineseShort')"
        :en-label="t('common.actions.switchToEnglishShort')"
        :label="localeSwitchLabel"
        @toggle="emit('toggle-locale')"
      />
      <CuAction
        :label="t('common.actions.refresh')"
        :icon="Refresh"
        :loading="refreshBusy"
        :disabled="refreshBusy"
        @click="emit('refresh-runtime')"
      />
    </template>
  </CuTopbar>
</template>
<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Refresh } from '@element-plus/icons-vue'
import { AgentTopbar as CuTopbar, ThemeToggle, LanguageSwitch, StatusCapsule, ConsoleActionButton as CuAction } from '@aw-ui'
import type { ConsoleSectionManifest } from '../../console/types'
import RuntimeStatusCapsule from './RuntimeStatusCapsule.vue'
defineProps<{
  activeSection: ConsoleSectionManifest
  ipcStatusText: string
  isDarkTheme: boolean
  isSidebarHidden: boolean
  localeSwitchLabel: string
  appLocale: 'zh-CN' | 'en-US'
  modeStatusText: string
  themeSwitchLabel: string
  refreshBusy: boolean
}>()
const emit = defineEmits<{
  'refresh-runtime': []
  'toggle-locale': []
  'toggle-sidebar': []
  'toggle-theme': []
}>()
const { t } = useI18n()
</script>
