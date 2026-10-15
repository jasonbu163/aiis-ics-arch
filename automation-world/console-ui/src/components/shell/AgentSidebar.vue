<!--
  File Path: /control-agent/src/components/shell/AgentSidebar.vue
  Description: Sidebar shell for the Control Agent operations console
  Main Features:
    - Renders CA-local section manifests
    - Displays runtime identity only in the resident sidebar footer
    - Avoids business frontend shell dependencies
-->
<template>
  <div class="agent-sidebar-shell">
    <el-menu :default-active="activeSection" class="agent-menu" @select="handleSelect">
      <el-menu-item v-for="section in sections" :key="section.id" :index="section.id">
        <el-icon>
          <component :is="section.icon" />
        </el-icon>
        <span>{{ t(section.titleKey) }}</span>
      </el-menu-item>
    </el-menu>

    <div v-if="showFooterBrand" class="sidebar-footer-brand">
      <strong>{{ t('common.app.title') }}</strong>
      <small>{{ runtimeSnapshot.version }} · {{ runtimeSnapshot.accessMode }}</small>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { ConsoleSectionId, ConsoleSectionManifest } from '../../console/types'
import type { RuntimeSnapshot } from '../../services/runtimeSnapshot'

const props = defineProps<{
  activeSection: ConsoleSectionId
  runtimeSnapshot: RuntimeSnapshot
  sections: ConsoleSectionManifest[]
  showFooterBrand: boolean
}>()

const emit = defineEmits<{
  'select-section': [section: ConsoleSectionId]
}>()

const { t } = useI18n()

function handleSelect(index: string) {
  const target = props.sections.find((section) => section.id === index)

  if (target) {
    emit('select-section', target.id)
  }
}
</script>
