<!--
  File Path: /control-agent/src/layouts/AgentLayout.vue
  Description: Shell layout for the Control Agent operations console
  Main Features:
    - Owns the sidebar, topbar and main content slots
    - Delegates only global actions to the composition root
    - Keeps business section content out of the shell
-->
<template>
  <el-container :class="['agent-layout', { 'agent-layout--sidebar-hidden': isSidebarHidden }]">
    <el-aside
      :class="[
        'agent-sidebar',
        {
          'agent-sidebar--hidden': isSidebarHidden,
          'agent-sidebar--floating-open': isSidebarHidden && isFloatingSidebarOpen
        }
      ]"
      :width="isSidebarHidden ? '0' : 'var(--agent-sidebar-width)'"
      @mouseenter="openFloatingSidebar"
      @mouseleave="scheduleFloatingSidebarClose"
    >
      <AgentSidebar
        :active-section="activeSection"
        :runtime-snapshot="runtimeSnapshot"
        :sections="sections"
        :show-footer-brand="!isSidebarHidden"
        @select-section="handleSelectSection"
      />
    </el-aside>

    <el-container>
      <el-header class="agent-topbar" height="var(--agent-topbar-height)">
        <AgentTopbar
          :active-section="activeSectionManifest"
          :backend-status-text="backendStatusText"
          :is-dark-theme="isDarkTheme"
          :is-sidebar-hidden="isSidebarHidden"
          :locale-switch-label="localeSwitchLabel"
          :mode-status-text="modeStatusText"
          :theme-switch-label="themeSwitchLabel"
          @open-floating-sidebar="openFloatingSidebar"
          @refresh-runtime="emit('refresh-runtime')"
          @schedule-floating-sidebar-close="scheduleFloatingSidebarClose"
          @toggle-locale="emit('toggle-locale')"
          @toggle-sidebar="toggleSidebar"
          @toggle-theme="emit('toggle-theme')"
        />
      </el-header>

      <el-main class="agent-main">
        <slot />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue'
import type { ConsoleSectionId, ConsoleSectionManifest } from '../console/types'
import type { RuntimeSnapshot } from '../services/runtimeSnapshot'
import AgentSidebar from '../components/shell/AgentSidebar.vue'
import AgentTopbar from '../components/shell/AgentTopbar.vue'

const props = defineProps<{
  activeSection: ConsoleSectionId
  backendStatusText: string
  isDarkTheme: boolean
  localeSwitchLabel: string
  modeStatusText: string
  runtimeSnapshot: RuntimeSnapshot
  sections: ConsoleSectionManifest[]
  themeSwitchLabel: string
}>()

const emit = defineEmits<{
  'refresh-runtime': []
  'select-section': [section: ConsoleSectionId]
  'toggle-locale': []
  'toggle-theme': []
}>()

const activeSectionManifest = computed(() => {
  return props.sections.find((section) => section.id === props.activeSection) ?? props.sections[0]
})

const isSidebarHidden = ref(false)
const isFloatingSidebarOpen = ref(false)
let floatingSidebarTimer: number | undefined

function clearFloatingSidebarTimer() {
  if (floatingSidebarTimer) {
    window.clearTimeout(floatingSidebarTimer)
    floatingSidebarTimer = undefined
  }
}

function openFloatingSidebar() {
  if (!isSidebarHidden.value) {
    return
  }

  clearFloatingSidebarTimer()
  isFloatingSidebarOpen.value = true
}

function scheduleFloatingSidebarClose() {
  if (!isSidebarHidden.value) {
    return
  }

  clearFloatingSidebarTimer()
  floatingSidebarTimer = window.setTimeout(() => {
    isFloatingSidebarOpen.value = false
  }, 180)
}

function toggleSidebar() {
  clearFloatingSidebarTimer()
  isFloatingSidebarOpen.value = false
  isSidebarHidden.value = !isSidebarHidden.value
}

function handleSelectSection(section: ConsoleSectionId) {
  emit('select-section', section)

  if (isSidebarHidden.value) {
    isFloatingSidebarOpen.value = false
  }
}

onBeforeUnmount(() => {
  clearFloatingSidebarTimer()
})
</script>
