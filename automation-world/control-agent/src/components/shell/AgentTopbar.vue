<!--
  File Path: /control-agent/src/components/shell/AgentTopbar.vue
  Description: Topbar shell for the Control Agent operations console
  Main Features:
    - Renders title, subtitle, backend status and global actions
    - Keeps refresh and language switch available across sections
    - Avoids business session UI
-->
<template>
  <div class="agent-topbar-shell">
    <div class="topbar-left">
      <button
        :aria-pressed="isSidebarHidden"
        :class="['sidebar-toggle-button', { 'sidebar-toggle-button--active': isSidebarHidden }]"
        type="button"
        @blur="emit('schedule-floating-sidebar-close')"
        @click="emit('toggle-sidebar')"
        @focus="emit('open-floating-sidebar')"
        @mouseenter="emit('open-floating-sidebar')"
        @mouseleave="emit('schedule-floating-sidebar-close')"
      >
        <el-icon>
          <Expand v-if="isSidebarHidden" />
          <Fold v-else />
        </el-icon>
      </button>
      <div class="topbar-title">
        <h1>{{ t(activeSection.titleKey) }}</h1>
        <p>{{ t('common.app.subtitle') }}</p>
      </div>
    </div>
    <div class="topbar-actions">
      <RuntimeStatusCapsule :status-text="modeStatusText" />
      <span class="topbar-status-chip">{{ backendStatusText }}</span>
      <button
        :aria-label="themeSwitchLabel"
        :class="['topbar-capsule-button', 'theme-toggle-button', { 'theme-toggle-button--dark': isDarkTheme }]"
        :title="themeSwitchLabel"
        type="button"
        @click="emit('toggle-theme')"
      >
        <el-icon>
          <Sunny v-if="isDarkTheme" />
          <Moon v-else />
        </el-icon>
      </button>
      <button
        :aria-label="t('common.actions.switchLanguage')"
        class="topbar-capsule-button language-switch-button"
        type="button"
        @click="emit('toggle-locale')"
      >
        <el-icon>
          <SwitchButton />
        </el-icon>
        <span>{{ localeSwitchLabel }}</span>
      </button>
      <button
        :aria-label="t('common.actions.refresh')"
        :title="t('common.actions.refresh')"
        class="topbar-capsule-button topbar-refresh-button"
        type="button"
        @click="emit('refresh-runtime')"
      >
        <el-icon>
          <Refresh />
        </el-icon>
        <span>{{ t('common.actions.refresh') }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Expand, Fold, Moon, Refresh, Sunny, SwitchButton } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import type { ConsoleSectionManifest } from '../../console/types'
import RuntimeStatusCapsule from './RuntimeStatusCapsule.vue'

defineProps<{
  activeSection: ConsoleSectionManifest
  backendStatusText: string
  isDarkTheme: boolean
  isSidebarHidden: boolean
  localeSwitchLabel: string
  modeStatusText: string
  themeSwitchLabel: string
}>()

const emit = defineEmits<{
  'open-floating-sidebar': []
  'refresh-runtime': []
  'schedule-floating-sidebar-close': []
  'toggle-locale': []
  'toggle-sidebar': []
  'toggle-theme': []
}>()

const { t } = useI18n()
</script>
