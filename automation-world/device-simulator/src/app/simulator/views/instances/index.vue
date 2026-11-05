<!-- 实例CRUD与工作区版本列表：停机加载、当前页批量删除及回退保留确认；预览离页释放。 -->
<template>
  <section class="console-stack" data-testid="page-instances">
    <ConfigRevisionBar />
    <ConsoleCard title-key="simulator.instances">
      <template #actions>
        <ConsoleActionButton label-key="simulator.createInstance" data-testid="instance-add" :disabled="local.busy||!local.draft||local.draft.instances.length>=8" @click="create" />
      </template>
      <el-empty :image-size="64" v-if="!local.draft?.instances.length" :description="t('simulator.emptyInstances')" />
      <ConsoleDataTable table-id="configuration.instances" v-else :data="local.draft.instances" row-key="id">
        <el-table-column column-key="name" min-width="180" prop="name" :label="t('simulator.name')" />
        <el-table-column column-key="endpoint" min-width="200" :label="t('simulator.endpoint')">
          <template #default="{row}">{{ row.host }}:{{ row.port }}</template>
        </el-table-column>
        <el-table-column column-key="connectionLimits" min-width="150" :label="t('simulator.maxConnections')">
          <template #default="{row}">{{ row.maxConnections }}/{{ row.maxHandshakes }}</template>
        </el-table-column>
        <el-table-column column-key="actions" width="220" :resizable="false" :show-overflow-tooltip="false" fixed="right" :label="t('simulator.action')">
          <template #default="{row}">
            <div class="ds-actions">
              <ConsoleActionButton size="small" label-key="simulator.edit" data-testid="instance-edit" @click="edit(row)" />
              <ConsoleActionButton size="small" label-key="simulator.select" @click="local.instanceId=row.id" />
              <ConsoleActionButton size="small" label-key="simulator.remove" tone="danger" @click="deleting=row" />
            </div>
          </template>
        </el-table-column>
      </ConsoleDataTable>
    </ConsoleCard>
    <ConsoleCard title-key="simulator.loadRevision">
      <template #actions>
        <span>{{ t('simulator.versions.selectedCount', { count: checked.length }) }}</span>
        <ConsoleActionButton label-key="simulator.versions.refreshList" :disabled="local.busy" @click="local.pageRevisions(local.revisionOffset)" />
        <ConsoleActionButton label-key="simulator.versions.bulkDelete" tone="danger" :disabled="blocked || !checked.length" @click="previewDelete(checked.map(r => r.revisionId))" />
      </template>
      <div class="ds-selection-toolbar">
        <div class="ds-field">
          <span>{{ t('simulator.instance') }}</span>
          <el-select v-model="local.instanceId" :disabled="local.busy" :placeholder="t('simulator.instance')" data-testid="instance-selection">
            <el-option v-for="i in local.draft?.instances" :key="i.id" :value="i.id" :label="i.name" />
          </el-select>
        </div>
        <ConsoleFieldHelp :label="t('simulator.versionDisplay.title')" :text="t('simulator.savedSelectedLoaded')+'\n'+t('simulator.calendarTimeHint')" />
      </div>
      <p>{{ t('simulator.versions.workspaceHint') }} {{ t('simulator.versions.retentionHint') }}</p>
      <ConsoleTableShell :current-page="Math.floor(local.revisionOffset / 100) + 1" :page-size="100" :total="local.configuration?.revisionTotal || 0" layout="total, prev, pager, next" @update:current-page="local.pageRevisions(($event - 1) * 100)">
        <ConsoleDataTable table-id="configuration.revisions" :data="local.configuration?.revisions || []" row-key="revisionId" data-testid="configuration-versions" @selection-change="selectRevisions">
          <el-table-column column-key="selection" type="selection" width="48" :resizable="false" :selectable="deletable" :reserve-selection="false" :show-overflow-tooltip="false" />
          <el-table-column column-key="version" min-width="130" :label="t('simulator.versionDisplay.title')"><template #default="{row}">v{{ row.savedSeq }}</template></el-table-column>
          <el-table-column column-key="savedTime" min-width="210" :label="t('simulator.versions.savedTime')"><template #default="{row}">{{ formatShanghaiTime(row.createdUtc) || '—' }}</template></el-table-column>
          <el-table-column column-key="usage" min-width="270" :label="t('simulator.versions.usage')"><template #default="{row}">{{ usage(row) }}</template></el-table-column>
          <el-table-column column-key="actions" width="240" :resizable="false" :show-overflow-tooltip="false" fixed="right" :label="t('simulator.action')">
            <template #default="{row}"><div class="ds-actions">
              <ConsoleActionButton size="small" label-key="simulator.versions.previewLoad" data-testid="apply-open" :disabled="blocked || !local.instanceId || !stopped" @click="previewApply(row.revisionId)" />
              <span :title="usage(row)"><ConsoleActionButton size="small" label-key="simulator.remove" tone="danger" :disabled="blocked || !row.canDelete" @click="previewDelete([row.revisionId])" /></span>
            </div></template>
          </el-table-column>
        </ConsoleDataTable>
      </ConsoleTableShell>
      <p v-if="!stopped">{{ t('simulator.versions.stopRequired') }}</p>
    </ConsoleCard>
    <InstanceEditor v-model="editorOpen" :instance="editor" @confirm="keep" />
    <el-dialog :model-value="!!deleting" :title="t('simulator.remove')" :append-to-body="false" width="min(540px, calc(100vw - 32px))" @close="deleting=null">
      <p>{{ t('simulator.deleteInstanceHint') }}</p>
      <template #footer>
        <ConsoleActionButton label-key="simulator.cancel" @click="deleting=null" />
        <ConsoleActionButton label-key="simulator.confirm" tone="danger" data-testid="instance-delete-confirm" @click="remove" />
      </template>
    </el-dialog>
    <ApplyPreviewDialog :preview="candidate" :busy="local.busy" @cancel="cancelApply" @confirm="apply" @retention="previewApply(revision, $event)" />
    <RevisionOperationDialog :preview="deletePreview" :busy="local.busy" :blocked="blocked" :unknown="local.unknown" :instances="local.draft?.instances" @cancel="cancelDelete" @confirm="deleteRevision" />
  </section>
</template>
<script setup lang="ts">
import ConsoleDataTable from '../../../../components/console/ConsoleDataTable.vue';
import { computed, inject, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { simulatorKey } from '../../../../console/composables/useDeviceSimulator';
import { formatShanghaiTime } from '../../../../console/time';
import ConsoleFieldHelp from '../../../../components/console/ConsoleFieldHelp.vue';
import ConsoleTableShell from '../../../../components/console/ConsoleTableShell.vue';
import * as ipc from '../../../../services/deviceSimulator';
import ConsoleCard from '../../../../components/console/ConsoleCard.vue';
import ConsoleActionButton from '../../../../components/console/ConsoleActionButton.vue';
import ConfigRevisionBar from '../../../../components/console/ConfigRevisionBar.vue';
import InstanceEditor from '../../components/InstanceEditor.vue';
import ApplyPreviewDialog from '../../components/ApplyPreviewDialog.vue';
import RevisionOperationDialog from '../../components/RevisionOperationDialog.vue';
const local = inject(simulatorKey)!, { t } = useI18n(), editorOpen = ref(false), editor = ref<ipc.Instance | null>(null), deleting = ref<ipc.Instance | null>(null), candidate = ref<ipc.Preview | null>(null);
const revision = ref(''), deletePreview = ref<ipc.Preview | null>(null);
const checked = ref<ipc.Revision[]>([]);
let disposed = false;
onMounted(() => { void local.pageRevisions(local.revisionOffset); });
onBeforeUnmount(() => {
    disposed = true;
    if (candidate.value) void local.releasePreview(candidate.value);
    if (deletePreview.value) void local.releasePreview(deletePreview.value);
});
const blocked = computed(() => local.busy || local.dirty || local.editing || local.unknown);
const stopped = computed(() => !local.runtime || ['stopped', 'load_failed'].includes(local.runtime.state));
function usage(row: ipc.Revision) { return row.protection.length ? row.protection.map(p => t('simulator.versions.protection.' + p.reason) + (p.instanceId ? ' · ' + (local.draft?.instances.find(i => i.id === p.instanceId)?.name || p.instanceId) : '')).join(' / ') : t('simulator.versions.unused'); }
function deletable(row: ipc.Revision) { return row.canDelete && !blocked.value; }
function selectRevisions(rows: ipc.Revision[]) { checked.value = rows.filter(r => r.canDelete); }
watch(() => local.configuration?.revisions, () => { checked.value = []; });
watch(() => local.instanceId, () => { const p = candidate.value; candidate.value = null; if (p) void local.releasePreview(p); });
function create() { const instance = local.newInstance(); if (instance) {
    editor.value = instance;
    editorOpen.value = true;
} }
function edit(instance: ipc.Instance) { editor.value = instance; editorOpen.value = true; }
function keep(instance: ipc.Instance) { if (!local.draft)
    return; const at = local.draft.instances.findIndex(i => i.id === instance.id); if (at < 0)
    local.draft.instances.push(instance);
else
    local.draft.instances[at] = instance; local.instanceId = instance.id; }
function remove() { if (!local.draft || !deleting.value)
    return; local.draft.instances = local.draft.instances.filter(i => i.id !== deleting.value!.id); deleting.value = null; }
async function previewApply(revisionId: string, retention = 'preserve_compatible_hold') { if (candidate.value) await cancelApply(); revision.value = revisionId; const instanceId = local.instanceId; const p = await local.action(() => ipc.previewApply({ expectedEtag: local.configuration!.etag, instanceId, revisionId, retention })); if (p) {
    if (disposed || instanceId !== local.instanceId) { await local.releasePreview(p); return; }
    candidate.value = p;
    await local.pageRevisions(local.revisionOffset);
} }
async function cancelApply() { if (!candidate.value || local.busy) return; const p = candidate.value; candidate.value = null; await local.releasePreview(p); }
async function apply() { const p = candidate.value, instanceId = local.instanceId; if (!p)
    return; const result = await local.action(() => ipc.applyRevision(instanceId, p), true); if (result !== undefined)
    candidate.value = null; }
async function previewDelete(ids: string[]) { const p = await local.action(() => ipc.previewDeleteRevisions(local.configuration!.etag, ids)); if (p) { if (disposed) await local.releasePreview(p); else deletePreview.value = p; } }
async function cancelDelete() { if (!deletePreview.value || local.busy) return; const p = deletePreview.value; deletePreview.value = null; await local.releasePreview(p); }
async function deleteRevision(releaseRollback: boolean) { if (!deletePreview.value) return; const p = deletePreview.value; const result = await local.action(async () => { const saved = await ipc.commitVersion(p, releaseRollback); local.revisionOffset = 0; return saved; }, true); if (result) deletePreview.value = null; }
</script>
