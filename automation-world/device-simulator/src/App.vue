<!-- DAA/CU公共壳的DS正式装配：一个宿主状态owner、六页、dirty确认与正常关闭。 -->
<template>
  <el-config-provider :locale="elementLocale">
    <Teleport to="body">
      <div class="aw-ui aw-sample-overlays" :data-aw-theme="agentTheme">
        <div id="ds-feedback"></div>
      </div>
    </Teleport>
    <AgentLayout :active-section="activeSection" :app-locale="appLocale" :refresh-busy="local.refreshing" :ipc-status-text="ipcStatusText" :is-dark-theme="isDarkTheme" :locale-switch-label="localeSwitchLabel" :mode-status-text="runtimeStatusText" :identity-detail="identityDetail" :sections="consoleSections" :theme-switch-label="themeSwitchLabel" @refresh-runtime="local.refresh()" @select-section="activeSection=$event" @toggle-locale="toggleLocale" @toggle-theme="toggleTheme">
      <div class="console-stack" data-testid="ds-ready" :data-ready="!!local.bootstrap">
        <el-alert v-if="!local.available" :title="t('common.local.desktopPreview')" :closable="false" type="info" />
        <el-alert v-if="local.error" :title="errorLabel" :closable="false" type="error" data-testid="ipc-error" :data-error-code="local.error" />
        <el-alert v-if="local.unknown" :title="t('simulator.unknownReceipt')" :closable="false" type="warning" />
        <el-alert v-if="local.snapshot?.stale" :title="t('simulator.staleHint')" :closable="false" type="warning" />
        <component :is="activeComponent" />
      </div>
    </AgentLayout>
    <el-dialog class="aw-ui" :data-aw-theme="agentTheme" v-model="closeOpen" :title="t('simulator.unsavedTitle')" :append-to-body="false" :close-on-click-modal="false" width="min(600px, calc(100vw - 32px))" data-testid="dirty-close-dialog">
      <p>{{ t('simulator.unsavedHint') }}</p>
      <template #footer>
        <ConsoleActionButton label-key="simulator.cancel" data-testid="dirty-close-cancel" :disabled="local.busy" @click="closeOpen=false" />
        <ConsoleActionButton label-key="simulator.discardClose" tone="warning" data-testid="dirty-close-discard" :disabled="local.busy" @click="discardClose" />
        <ConsoleActionButton label-key="simulator.saveClose" tone="primary" data-testid="dirty-close-save" :disabled="local.busy" @click="saveClose" />
      </template>
    </el-dialog>
  </el-config-provider>
</template>
<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, provide, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { listen, emit, type UnlistenFn } from '@tauri-apps/api/event';
import { useAgentConsoleShell } from './console/composables/useAgentConsoleShell';
import { useDeviceSimulator, simulatorKey } from './console/composables/useDeviceSimulator';
import type { ConsoleSectionId } from './console/types';
import { consoleSections } from './console/sections';
import AgentLayout from './layouts/AgentLayout.vue';
import ConsoleActionButton from './components/console/ConsoleActionButton.vue';
const { t, te } = useI18n(), { activeSection, appLocale, elementLocale, localeSwitchLabel, toggleLocale, agentTheme, isDarkTheme, themeSwitchLabel, toggleTheme } = useAgentConsoleShell();
const local = reactive(useDeviceSimulator());
provide(simulatorKey, local);
const activeComponent = computed(() => consoleSections.find(s => s.id === activeSection.value)!.component);
const ipcStatusText = computed(() => t(!local.available ? 'common.local.desktopPreview' : local.error ? 'common.local.bootstrapFailed' : local.bootstrap ? 'simulator.ipcReady' : 'common.local.loading'));
const runtimeStatusText = computed(() => t(local.snapshot?.instances.some(i => i.state === 'running') ? 'simulator.running' : local.snapshot?.instances.some(i => i.state === 'paused') ? 'simulator.paused' : 'simulator.stopped'));
const identityDetail = computed(() => `${local.bootstrap?.version || '—'} · ${runtimeStatusText.value}`);
const errorLabel = computed(() => { const key = 'simulator.errors.' + local.error; return te(key) ? t(key) : t('simulator.operationFailed'); });
const closeOpen = ref(false);
let unlisten: UnlistenFn | undefined, timer: ReturnType<typeof setInterval> | undefined;
async function requestClose() { if (local.busy) {
    local.error = 'operation_in_progress';
    return;
} if (local.dirty || local.editing)
    closeOpen.value = true;
else
    await emit('ds-close-decision', 'close'); }
async function saveClose() { if (local.editing && local.finishEditor && !local.finishEditor())
    return; if (await local.save()) {
    closeOpen.value = false;
    await emit('ds-close-decision', 'close');
} }
async function discardClose() { local.discardEditor?.(); closeOpen.value = false; await emit('ds-close-decision', 'close'); }
function navigate(event: Event) { const id = (event as CustomEvent).detail; if (consoleSections.some(s => s.id === id))
    activeSection.value = id as ConsoleSectionId; }
function visible() { if (!document.hidden)
    void local.refresh(); }
onMounted(async () => { document.addEventListener('ds-navigate', navigate); document.addEventListener('visibilitychange', visible); if (local.available)
    unlisten = await listen('ds-close-request', requestClose); await local.refresh(); timer = setInterval(() => void local.refresh(), 1000); });
onBeforeUnmount(() => { if (timer)
    clearInterval(timer); unlisten?.(); document.removeEventListener('ds-navigate', navigate); document.removeEventListener('visibilitychange', visible); });
</script>
