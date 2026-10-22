<!-- DS 壳层组合：消费 CU Layout，导航状态与运行副作用由 App 唯一 owner 持有。 -->
<template>
  <CuLayout ref="layout" :theme="isDarkTheme?'dark':'light'" :sidebar-hidden="isSidebarHidden">
    <template #sidebar>
      <AgentSidebar
        :active-section="activeSection"
        :identity-detail="identityDetail"
        :sections="sections"
        @select-section="emit('select-section',$event)"
      />
    </template>
    <template #topbar>
      <AgentTopbar
        :active-section="activeSectionManifest"
        :ipc-status-text="ipcStatusText"
        :is-dark-theme="isDarkTheme"
        :is-sidebar-hidden="isSidebarHidden"
        :locale-switch-label="localeSwitchLabel"
        :app-locale="appLocale"
        :mode-status-text="modeStatusText"
        :theme-switch-label="themeSwitchLabel"
        :refresh-busy="refreshBusy"
        @refresh-runtime="emit('refresh-runtime')"
        @toggle-locale="emit('toggle-locale')"
        @toggle-theme="emit('toggle-theme')"
        @toggle-sidebar="isSidebarHidden=!isSidebarHidden"
      />
    </template>
    <slot />
  </CuLayout>
</template>
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { AgentLayout as CuLayout } from '@aw-ui'
import type { ConsoleSectionId, ConsoleSectionManifest } from '../console/types'
import AgentSidebar from '../components/shell/AgentSidebar.vue'
import AgentTopbar from '../components/shell/AgentTopbar.vue'
const props = defineProps<{
  activeSection: ConsoleSectionId
  ipcStatusText: string
  isDarkTheme: boolean
  localeSwitchLabel: string
  appLocale: 'zh-CN' | 'en-US'
  modeStatusText: string
  identityDetail: string
  sections: ConsoleSectionManifest[]
  themeSwitchLabel: string
  refreshBusy: boolean
}>()
const emit = defineEmits<{
  'refresh-runtime': []
  'select-section': [
    section: ConsoleSectionId
  ]
  'toggle-locale': []
  'toggle-theme': []
}>()
const layout = ref<{ $el: HTMLElement } | null>(null)
const isSidebarHidden = ref(false)
watch(() => props.activeSection, () => {
  const workspace = layout.value?.$el.querySelector('.agent-workspace')
  if (workspace instanceof HTMLElement) workspace.scrollTop = 0
}, { flush: 'post' })
const activeSectionManifest = computed(() => props.sections.find(s => s.id === props.activeSection) ?? props.sections[0])
</script>

