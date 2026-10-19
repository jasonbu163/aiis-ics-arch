<!-- DAA 唯一local owner与纯壳；无桥/启动失败不伪造SQLite状态。 -->
<template>
  <el-config-provider :locale="elementLocale">
    <Teleport to="body"><div class="aw-ui aw-sample-overlays" :data-aw-theme="agentTheme"><div id="daa-feedback"></div></div></Teleport>
    <AgentLayout :active-section="activeSection" :app-locale="appLocale" :refresh-busy="local.busy"
      :backend-status-text="t('common.local.uploadPending')" :is-dark-theme="isDarkTheme"
      :locale-switch-label="localeSwitchLabel" :mode-status-text="t('common.local.mode')"
      :identity-detail="identityDetail" :sections="consoleSections" :theme-switch-label="themeSwitchLabel"
      @refresh-runtime="local.refresh()" @select-section="selectConsoleSection" @toggle-locale="toggleLocale" @toggle-theme="toggleTheme">
      <div class="console-stack">
        <el-alert v-if="!local.available" :title="t(bootstrapError ? 'common.local.bootstrapFailed' : 'common.local.desktopPreview')"
          :description="bootstrapError ? local.label(bootstrapError) : t('common.local.desktopPreviewHelp')" :closable="false" :type="bootstrapError ? 'error' : 'info'" show-icon />
        <el-alert v-if="bootstrap.ignoredKeys.length" :title="t('common.local.retiredKeys')" :description="bootstrap.ignoredKeys.join(', ')" type="info" :closable="false" />
        <template v-if="local.available">
          <ConfigRevisionBar />
          <template v-if="activeSection === 'workbench'"><RuntimeOverviewView /><CollectionStatusView /></template>
          <PlcDiagnosticsView v-else-if="activeSection === 'plc-config'" @open-points="selectConsoleSection('points-groups')" />
          <PlcPointsView v-else-if="activeSection === 'points-groups'" />
          <StorageView v-else-if="activeSection === 'reporting-storage'" />
        </template>
      </div>
    </AgentLayout>
  </el-config-provider>
</template>
<script setup lang="ts">
import { computed, provide } from 'vue'
import { useI18n } from 'vue-i18n'
import { bootstrap, bootstrapError } from './services/localAcquisition'
import { useAgentConsoleShell } from './console/composables/useAgentConsoleShell'
import { localConsoleKey, useLocalAcquisitionConsole } from './console/composables/useLocalAcquisitionConsole'
import type { ConsoleSectionId } from './console/types'
import { consoleSections } from './console/sections'
import AgentLayout from './layouts/AgentLayout.vue'
import ConfigRevisionBar from './components/console/ConfigRevisionBar.vue'
import RuntimeOverviewView from './app/runtime/views/overview/index.vue'
import CollectionStatusView from './app/collection/views/status/index.vue'
import PlcDiagnosticsView from './app/plc/views/diagnostics/index.vue'
import PlcPointsView from './app/plc/views/points/index.vue'
import StorageView from './app/collection/views/storage/index.vue'
const { t } = useI18n()
const { activeSection, appLocale, elementLocale, localeSwitchLabel, toggleLocale, agentTheme, isDarkTheme, themeSwitchLabel, toggleTheme } = useAgentConsoleShell()
const local = useLocalAcquisitionConsole()
provide(localConsoleKey, local)
const identityDetail = computed(() => `${bootstrap.version ?? '—'} · ${t('common.local.mode')}`)
async function selectConsoleSection(section: ConsoleSectionId) {
  if (section === activeSection.value) return
  if (local.editing && !(await local.confirmAction('common.local.discardEditorConfirm'))) return
  activeSection.value = section
}
</script>
