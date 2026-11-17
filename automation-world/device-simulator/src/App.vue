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
        <el-alert v-if="local.saveOutcome" :title="t('simulator.closeRecovery.'+local.saveOutcome)" :closable="false" type="info" data-testid="save-known-outcome" />
        <el-alert v-if="local.saveFailure && local.error !== local.saveFailure" :title="t('simulator.closeRecovery.rejected',{code:local.saveFailure})" :closable="false" type="error" />
        <el-alert v-if="local.unknown" :title="t('simulator.unknownReceipt')" :closable="false" type="warning" />
        <el-alert v-if="local.snapshot?.stale" :title="t('simulator.staleHint')" :closable="false" type="warning" />
        <component :is="activeComponent" />
      </div>
    </AgentLayout>
    <el-dialog class="aw-ui" :data-aw-theme="agentTheme" v-model="closeOpen" :title="t('simulator.unsavedTitle')" :append-to-body="false" :close-on-click-modal="false" :close-on-press-escape="!closeEmitting" :show-close="!closeEmitting" width="min(600px, calc(100vw - 32px))" data-testid="dirty-close-dialog" @close="cancelWindowClose">
      <p>{{ t('simulator.unsavedHint') }}</p>
      <p v-if="local.saveOutcome">{{ t('simulator.closeRecovery.'+local.saveOutcome) }}</p>
      <p v-if="local.saveFailure">{{ t('simulator.closeRecovery.rejected', {code:local.saveFailure}) }}</p>
      <p v-if="local.uncertainSave">{{ t(local.uncertainSave.reason === 'known_readback' ? 'simulator.closeRecovery.readback' : local.uncertainSave.reason === 'known_cleanup' ? 'simulator.closeRecovery.cleanup' : 'simulator.closeRecovery.saveUnknown') }}</p>
      <p v-if="local.uncertainControls.length">{{ t('simulator.closeRecovery.controls', {count:local.uncertainControls.length}) }}</p>
      <ul v-if="local.uncertainControls.length"><li v-for="item in local.uncertainControls" :key="item.id">{{ t('simulator.'+item.command) }} · {{ item.instanceId }} · {{ item.code }}</li></ul>
      <p v-if="local.previewReleases.length">{{ t('simulator.closeRecovery.releases', {count:local.previewReleases.length}) }}</p>
      <ul v-if="local.previewReleases.length"><li v-for="item in local.previewReleases" :key="item.id">{{ item.preview.kind || '—' }} · {{ t('simulator.closeRecovery.'+item.state) }}</li></ul>
      <p v-if="local.previewUnknowns.length">{{ t('simulator.closeRecovery.previewUnknown', {count:local.previewUnknowns.length}) }}</p>
      <ul v-if="local.previewUnknowns.length"><li v-for="item in local.previewUnknowns" :key="item.id">{{ item.kind || '—' }} · {{ item.code }}</li></ul>
      <p v-if="local.unknown && !local.uncertainSave && !local.uncertainControls.length && !local.previewUnknowns.length">{{ t('simulator.closeRecovery.otherUnknown', {code:local.error}) }}</p>
      <p v-if="closeChanged">{{ t('simulator.closeRecovery.changed') }}</p>
      <template #footer>
        <ConsoleActionButton label-key="simulator.cancel" data-testid="dirty-close-cancel" :disabled="local.busy || closeEmitting" @click="cancelWindowClose" />
        <ConsoleActionButton label-key="simulator.discardClose" tone="warning" data-testid="dirty-close-discard" :disabled="local.busy || closeEmitting" @click="discardClose" />
        <ConsoleActionButton label-key="simulator.saveClose" tone="primary" data-testid="dirty-close-save" :disabled="local.busy || closeEmitting" @click="saveClose" />
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
import { ipcStatusKey } from './console/ipcStatus';
import type { ConsoleSectionId } from './console/types';
import { consoleSections } from './console/sections';
import AgentLayout from './layouts/AgentLayout.vue';
import ConsoleActionButton from './components/console/ConsoleActionButton.vue';
const { t, te } = useI18n(), { activeSection, appLocale, elementLocale, localeSwitchLabel, toggleLocale, agentTheme, isDarkTheme, themeSwitchLabel, toggleTheme } = useAgentConsoleShell();
const local = reactive(useDeviceSimulator());
provide(simulatorKey, local);
const activeComponent = computed(() => consoleSections.find(s => s.id === activeSection.value)!.component);
const ipcStatusText = computed(() => t(ipcStatusKey(local.available, !!local.bootstrap, local.error)));
const runtimeStatusText = computed(() => t(local.snapshot?.instances.some(i => i.state === 'running') ? 'simulator.running' : local.snapshot?.instances.some(i => i.state === 'paused') ? 'simulator.paused' : 'simulator.stopped'));
const identityDetail = computed(() => `${local.bootstrap?.version || '—'} · ${runtimeStatusText.value}`);
const errorLabel = computed(() => { const key = 'simulator.errors.' + local.error; return te(key) ? t(key) : t('simulator.operationFailedWithCode', { code: local.error }); });
const closeOpen = ref(false), closeEmitting = ref(false), closeChanged = ref(false);
let closeReviewed = '';
let unlisten: UnlistenFn | undefined, timer: ReturnType<typeof setInterval> | undefined;
function cancelWindowClose() { if (closeEmitting.value) return; closeOpen.value = false; local.cancelClose(); }
function showClose() { closeOpen.value = true; closeChanged.value = false; closeReviewed = local.closeFingerprint(); }
async function sendClose() {
    closeEmitting.value = true;
    try { await emit('ds-close-decision', 'close'); }
    catch { local.cancelClose(); closeOpen.value = true; local.error = 'close_failed'; closeChanged.value = true; closeReviewed = local.closeFingerprint(); }
    finally { closeEmitting.value = false; }
}
async function requestClose() { if (local.busy) {
    if (!local.dirty && !local.unknown) local.error = 'operation_in_progress';
    return;
} if (local.closeGate) { closeOpen.value = true; return; }
local.beginClose();
if (local.dirty || local.editing || local.unknown)
    showClose();
else
    await sendClose(); }
async function saveClose() { if (local.editing && local.finishEditor && !local.finishEditor())
    return; if (!local.closeGate) local.beginClose();
    if (await local.save()) {
        if (local.dirty || local.editing || local.unknown) { closeChanged.value = true; closeReviewed = local.closeFingerprint(); return; }
        await sendClose();
    } }
async function discardClose() {
    if (!local.closeGate) local.beginClose();
    const current = local.closeFingerprint();
    if (current !== closeReviewed) { closeReviewed = current; closeChanged.value = true; return; }
    local.discardEditor?.(); await sendClose();
}
function navigate(event: Event) { const id = (event as CustomEvent).detail; if (consoleSections.some(s => s.id === id))
    activeSection.value = id as ConsoleSectionId; }
function visible() { if (!document.hidden)
    void local.refresh(); }
onMounted(async () => { document.addEventListener('ds-navigate', navigate); document.addEventListener('visibilitychange', visible); if (local.available)
    unlisten = await listen('ds-close-request', requestClose); await local.refresh(); timer = setInterval(() => void local.refresh(), 1000); });
onBeforeUnmount(() => { if (timer)
    clearInterval(timer); unlisten?.(); document.removeEventListener('ds-navigate', navigate); document.removeEventListener('visibilitychange', visible); });
</script>
