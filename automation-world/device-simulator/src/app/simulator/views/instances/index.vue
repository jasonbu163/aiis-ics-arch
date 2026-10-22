<!-- 实例CRUD与不可变revision选择/apply；保存不start，版本加载始终停机。 -->
<template>
  <section class="console-stack" data-testid="page-instances">
    <ConfigRevisionBar />
    <ConsoleCard title-key="simulator.instances">
      <template #actions>
        <ConsoleActionButton label-key="simulator.createInstance" data-testid="instance-add" :disabled="local.busy||!local.draft||local.draft.instances.length>=8" @click="create" />
      </template>
      <el-empty :image-size="64" v-if="!local.draft?.instances.length" :description="t('simulator.emptyInstances')" />
      <el-table v-else :data="local.draft.instances" row-key="id">
        <el-table-column prop="name" :label="t('simulator.name')" />
        <el-table-column :label="t('simulator.endpoint')">
          <template #default="{row}">{{ row.host }}:{{ row.port }}</template>
        </el-table-column>
        <el-table-column :label="t('simulator.maxConnections')">
          <template #default="{row}">{{ row.maxConnections }}/{{ row.maxHandshakes }}</template>
        </el-table-column>
        <el-table-column :label="t('simulator.action')">
          <template #default="{row}">
            <div class="ds-actions">
              <ConsoleActionButton size="small" label-key="simulator.edit" data-testid="instance-edit" @click="edit(row)" />
              <ConsoleActionButton size="small" label-key="simulator.select" @click="local.instanceId=row.id" />
              <ConsoleActionButton size="small" label-key="simulator.remove" tone="danger" @click="deleting=row" />
            </div>
          </template>
        </el-table-column>
      </el-table>
    </ConsoleCard>
    <ConsoleCard title-key="simulator.loadRevision">
      <div class="ds-selection-toolbar">
        <el-select v-model="local.instanceId" :placeholder="t('simulator.instance')" data-testid="instance-selection">
          <el-option v-for="i in local.draft?.instances" :key="i.id" :value="i.id" :label="i.name" />
        </el-select>
        <el-select v-model="revision" :placeholder="t('simulator.revision')" data-testid="revision-selection">
          <el-option v-for="r in local.configuration?.revisions" :key="r.revisionId" :value="r.revisionId" :label="r.savedSeq+' · '+r.createdUtc" />
        </el-select>
        <ConsoleActionButton label-key="simulator.previewApply" data-testid="apply-open" :disabled="local.busy||local.dirty||!local.instanceId||!revision" @click="previewApply()" />
      </div>
      <p>{{ t('simulator.savedSelectedLoaded') }}</p>
    </ConsoleCard>
    <InstanceEditor v-model="editorOpen" :instance="editor" @confirm="keep" />
    <el-dialog :model-value="!!deleting" :title="t('simulator.remove')" :append-to-body="false" width="min(540px, calc(100vw - 32px))" @close="deleting=null">
      <p>{{ t('simulator.deleteInstanceHint') }}</p>
      <template #footer>
        <ConsoleActionButton label-key="simulator.cancel" @click="deleting=null" />
        <ConsoleActionButton label-key="simulator.confirm" tone="danger" data-testid="instance-delete-confirm" @click="remove" />
      </template>
    </el-dialog>
    <ApplyPreviewDialog :preview="candidate" :busy="local.busy" @cancel="candidate=null" @confirm="apply" @retention="previewApply" />
  </section>
</template>
<script setup lang="ts">
import { inject, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { simulatorKey } from '../../../../console/composables/useDeviceSimulator';
import * as ipc from '../../../../services/deviceSimulator';
import ConsoleCard from '../../../../components/console/ConsoleCard.vue';
import ConsoleActionButton from '../../../../components/console/ConsoleActionButton.vue';
import ConfigRevisionBar from '../../../../components/console/ConfigRevisionBar.vue';
import InstanceEditor from '../../components/InstanceEditor.vue';
import ApplyPreviewDialog from '../../components/ApplyPreviewDialog.vue';
const local = inject(simulatorKey)!, { t } = useI18n(), editorOpen = ref(false), editor = ref<ipc.Instance | null>(null), deleting = ref<ipc.Instance | null>(null), revision = ref(''), candidate = ref<ipc.Preview | null>(null);
watch(() => local.configuration?.latestRevision, v => { if (!revision.value && v)
    revision.value = v; }, { immediate: true });
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
async function previewApply(retention = 'preserve_compatible_hold') { const p = await local.action(() => ipc.previewApply({ expectedEtag: local.configuration!.etag, instanceId: local.instanceId, revisionId: revision.value, retention })); if (p)
    candidate.value = p; }
async function apply() { if (!candidate.value)
    return; const result = await local.action(() => ipc.applyRevision(local.instanceId, candidate.value!), true); if (result !== undefined)
    candidate.value = null; }
</script>
