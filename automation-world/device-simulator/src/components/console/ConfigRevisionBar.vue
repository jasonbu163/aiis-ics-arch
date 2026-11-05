<!-- 沿DAA保存/版本事实条，适配DS草稿；校验问题定位到实例、DB和点。 -->
<template>
  <ConsoleCard title-key="simulator.configuration" compact>
    <template #actions>
      <el-tag :type="local.dirty ? 'warning' : 'info'">{{ t(local.dirty ? 'simulator.dirty' : 'simulator.saved') }}</el-tag>
      <el-tag v-if="!local.dirty && local.configuration && !local.configuration.draftMatchesLatest" type="warning">{{ t('simulator.versions.unpublished') }}</el-tag>
      <ConsoleActionButton label-key="simulator.save" data-testid="configuration-save" :disabled="local.busy || local.editing || !local.draft" :loading="local.busy" :tone="local.dirty ? 'primary' : 'secondary'" @click="local.save()" />
      <ConsoleActionButton label-key="simulator.versions.publish" data-testid="configuration-publish" :disabled="local.busy || local.editing || local.dirty || local.unknown || !local.configuration" @click="previewPublish" />
      <ConsoleActionButton label-key="simulator.reload" :disabled="local.busy" @click="reloadOpen = true" />
    </template>
    <RevisionStatus :saved="local.configuration?.latestRevision" :selected="selection" :loaded="local.runtime?.loadedRevision" :etag="local.configuration?.etag" :hint="t('simulator.saveApplyHint')" />
    <ul v-if="local.configuration?.issues.length" class="ds-issues">
      <li v-for="(issue, index) in local.configuration.issues.slice(0, 100)" :key="index">
        {{ issueLabel(issue.code) }} · {{ issueLocation(issue) }}
      </li>
    </ul>
    <ConsoleOperationDialog v-model="reloadOpen" title-key="simulator.reload" message-key="simulator.reloadHint" cancel-label-key="simulator.cancel" confirm-label-key="simulator.confirm" @confirm="reload" />
    <RevisionOperationDialog :preview="publishPreview" :busy="local.busy" :blocked="local.dirty || local.editing || local.unknown" :unknown="local.unknown" @cancel="cancelPublish" @confirm="publish" />
  </ConsoleCard>
</template>
<script setup lang="ts">
import { computed, inject, onBeforeUnmount, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import type { Issue } from '../../services/deviceSimulator';
import * as ipc from '../../services/deviceSimulator';
import RevisionOperationDialog from '../../app/simulator/components/RevisionOperationDialog.vue';
import { simulatorKey } from '../../console/composables/useDeviceSimulator';
import RevisionStatus from './RevisionStatus.vue';
import ConsoleCard from './ConsoleCard.vue';
import ConsoleActionButton from './ConsoleActionButton.vue';
import ConsoleOperationDialog from './ConsoleOperationDialog.vue';
const local = inject(simulatorKey)!;
const { t, te } = useI18n();
const reloadOpen = ref(false);
const publishPreview = ref<ipc.Preview | null>(null);
let disposed = false;
onBeforeUnmount(() => { disposed = true; if (publishPreview.value) void local.releasePreview(publishPreview.value); });
const selection=computed(()=>local.configuration?.selections.find(s=>s.instanceId===local.instanceId)?.revisionId||local.runtime?.selectedRevision);
function issueLabel(code: string) {
    const key = 'simulator.errors.' + code;
    return te(key) ? t(key) : t('simulator.configurationBlocked');
}
function issueLocation(issue: Issue) {
    const instance = local.draft?.instances.find(item => item.id === issue.instanceId);
    const db = instance?.dbs.find(item => item.id === issue.dbId);
    const point = db?.points.find(item => item.id === issue.pointId);
    return [
        instance ? `${t('simulator.instance')}: ${instance.name}` : t('simulator.configuration'),
        db ? `DB${db.number} · ${db.name}` : null,
        point ? `${t('simulator.levels.point')}: ${point.name || point.sourcePath}` : null,
    ].filter(Boolean).join(' / ');
}
async function reload() {
    await local.action(local.reload);
    if (!local.error)
        reloadOpen.value = false;
}
async function previewPublish() {
    if (!local.configuration) return;
    const preview = await local.action(() => ipc.previewPublishRevision(local.configuration!.etag));
    if (preview) { if (disposed) await local.releasePreview(preview); else publishPreview.value = preview; }
}
async function cancelPublish() {
    if (!publishPreview.value || local.busy) return;
    const preview = publishPreview.value;
    publishPreview.value = null;
    await local.releasePreview(preview);
}
async function publish() {
    if (!publishPreview.value) return;
    const preview = publishPreview.value;
    const result = await local.action(async () => {
        const result = await ipc.commitVersion(preview);
        local.revisionOffset = 0;
        return result;
    }, true);
    if (result) { local.lastSavedRevision = result.revisionId; publishPreview.value = null; }
}
</script>
