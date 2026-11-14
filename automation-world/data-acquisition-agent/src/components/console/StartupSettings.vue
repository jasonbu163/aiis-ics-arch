<!-- 应用启动偏好独立保存；仅下次原生启动触发采集或上报。 -->
<template>
  <section v-if="local" class="console-card console-card--compact daa-startup">
    <header class="console-card__header">
      <div class="daa-startup-heading">
        <h2><button type="button" class="daa-startup-title" :aria-expanded="expanded" aria-controls="daa-startup-body" @click="toggleExpanded">{{ t('common.startup.title') }}</button></h2>
        <div v-if="expanded" class="daa-delivery-help" @mouseenter="hoverHelp = true" @mouseleave="hoverHelp = false">
          <button type="button" class="daa-help-button" :aria-label="t('common.startup.helpLabel')" :aria-expanded="helpVisible" aria-describedby="daa-startup-help" @focus="focusHelp = true" @blur="focusHelp = false; touchHelp = false" @click="touchHelp = !touchHelp">?</button>
          <div v-show="helpVisible" id="daa-startup-help" role="tooltip" class="daa-help-text">{{ t('common.startup.help') }}</div>
        </div>
      </div>
      <button type="button" class="daa-startup-collapse" :aria-label="t(expanded ? 'common.startup.collapse' : 'common.startup.expand')" :aria-expanded="expanded" aria-controls="daa-startup-body" @click="toggleExpanded"><el-icon><ArrowDown v-if="expanded" /><ArrowRight v-else /></el-icon></button>
    </header>
    <div v-if="expanded" id="daa-startup-body" class="console-card__body">
      <div class="daa-startup-options">
        <div class="daa-startup-option"><span>{{ t('common.startup.autoCollect') }}</span><ElSwitch :model-value="local.startup?.settings.autoCollect ?? false" :aria-label="t('common.startup.autoCollect')" :disabled="!local.startup || local.startupBusy" @change="value => local?.saveStartup('autoCollect', value === true)" /></div>
        <div class="daa-startup-option"><span>{{ t('common.startup.autoReport') }}</span><ElSwitch :model-value="local.startup?.settings.autoReport ?? false" :aria-label="t('common.startup.autoReport')" :disabled="!local.startup || local.startupBusy || !local.bootstrap.uploadAvailable" @change="value => local?.saveStartup('autoReport', value === true)" /></div>
      </div>
      <p v-if="local.startupSaved" class="daa-capability-note" role="status">{{ t('common.startup.saved') }}</p>
      <el-alert v-if="local.startupError" :title="t('common.startup.settingsError')" :description="local.label(local.startupError)" type="error" :closable="false" show-icon />
      <el-button v-if="local.startupError" :disabled="local.startupBusy" @click="local.loadStartup">{{ t('common.startup.reload') }}</el-button>
      <el-alert v-for="(reason, kind) in local.startup?.errors" :key="kind" :title="t('common.startup.startFailed')" :description="local.label(reason)" type="warning" :closable="false" show-icon />
    </div>
  </section>
</template>
<script setup lang="ts">
import { computed, inject, ref } from 'vue'
import { ElSwitch } from 'element-plus'
import { ArrowDown, ArrowRight } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import { localConsoleKey } from '../../console/composables/useLocalAcquisitionConsole'
const local = inject(localConsoleKey)
const { t } = useI18n()
const expanded = ref(true), hoverHelp = ref(false), focusHelp = ref(false), touchHelp = ref(false)
const helpVisible = computed(() => hoverHelp.value || focusHelp.value || touchHelp.value)
function toggleExpanded() {
  expanded.value = !expanded.value
  if (!expanded.value) hoverHelp.value = focusHelp.value = touchHelp.value = false
}
</script>
