<!-- 实例CRUD与不可变revision选择/apply；保存不start，版本加载始终停机。 -->
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
      <div class="ds-selection-toolbar">
        <div class="ds-field">
          <span>{{ t('simulator.instance') }}</span>
          <el-select v-model="local.instanceId" :placeholder="t('simulator.instance')" data-testid="instance-selection">
            <el-option v-for="i in local.draft?.instances" :key="i.id" :value="i.id" :label="i.name" />
          </el-select>
        </div>
        <div class="ds-field">
          <span>{{ t('simulator.versionDisplay.title') }} <ConsoleFieldHelp :label="t('simulator.versionDisplay.title')" :text="t('simulator.savedSelectedLoaded')+'\n'+t('simulator.calendarTimeHint')" /></span>
          <el-select v-model="revision" :placeholder="t('simulator.revision')" data-testid="revision-selection">
            <el-option v-for="r in local.configuration?.revisions" :key="r.revisionId" :value="r.revisionId" :label="'v'+r.savedSeq+' · '+(formatShanghaiTime(r.createdUtc)||'—')" />
          </el-select>
        </div>
        <ConsoleActionButton label-key="simulator.editing.chooseLatest" :disabled="!local.configuration?.latestRevision" @click="chooseLatest" />
        <ConsoleActionButton label-key="simulator.previewApply" data-testid="apply-open" :disabled="local.busy||local.dirty||!local.instanceId||!revision" @click="previewApply()" />
      </div>
      <p>{{ t('simulator.editing.chosenVersion',{revision:revisionLabel(revision,local.configuration?.revisions)}) }}</p>
      <el-alert v-if="revision&&revision!==local.configuration?.latestRevision" :title="t('simulator.editing.historicalVersion')" type="warning" :closable="false" />
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
import ConsoleDataTable from '../../../../components/console/ConsoleDataTable.vue';
import { computed, inject, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { simulatorKey } from '../../../../console/composables/useDeviceSimulator';
import { formatShanghaiTime } from '../../../../console/time';
import { revisionLabel } from '../../../../console/revisions';
import ConsoleFieldHelp from '../../../../components/console/ConsoleFieldHelp.vue';
import * as ipc from '../../../../services/deviceSimulator';
import ConsoleCard from '../../../../components/console/ConsoleCard.vue';
import ConsoleActionButton from '../../../../components/console/ConsoleActionButton.vue';
import ConfigRevisionBar from '../../../../components/console/ConfigRevisionBar.vue';
import InstanceEditor from '../../components/InstanceEditor.vue';
import ApplyPreviewDialog from '../../components/ApplyPreviewDialog.vue';
const local = inject(simulatorKey)!, { t } = useI18n(), editorOpen = ref(false), editor = ref<ipc.Instance | null>(null), deleting = ref<ipc.Instance | null>(null), candidate = ref<ipc.Preview | null>(null);
const choices = ref<Record<string,string>>({});
const revision = computed({get:()=>choices.value[local.instanceId]||local.configuration?.latestRevision||'',set:value=>{choices.value[local.instanceId]=value;candidate.value=null;}});
function chooseLatest(){delete choices.value[local.instanceId];candidate.value=null;}
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
