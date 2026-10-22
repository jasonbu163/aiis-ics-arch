<!-- 多DB完整配置/导入/地址/命名；10/20/50分页与跨页选择只影响明确点ID。 -->
<template>
  <section class="console-stack" data-testid="page-points">
    <ConfigRevisionBar />
    <ConsoleCard title-key="simulator.dbPoints">
      <div class="ds-selection-toolbar">
        <el-select v-model="local.instanceId" data-testid="points-instance" :placeholder="t('simulator.instance')">
          <el-option v-for="i in local.draft?.instances" :key="i.id" :value="i.id" :label="i.name" />
        </el-select>
        <el-select v-model="local.dbId" data-testid="points-db" :placeholder="t('simulator.db')">
          <el-option v-for="d in local.selected?.dbs" :key="d.id" :value="d.id" :label="d.name+' · DB'+d.number" />
        </el-select>
        <ConsoleActionButton label-key="simulator.newDb" data-testid="db-add" :disabled="!local.selected" @click="addDb" />
      </div>
      <div v-if="db" class="console-stack">
        <el-form label-position="top" class="ds-form-grid">
          <el-form-item :label="t('simulator.name')">
            <el-input v-model="db.name" data-testid="db-name" maxlength="100" />
          </el-form-item>
          <el-form-item :label="t('simulator.dbNumber')">
            <el-input-number v-model="db.number" data-testid="db-number" :min="1" :max="65535" />
          </el-form-item>
          <el-form-item :label="t('simulator.dbLength')">
            <el-input-number v-model="db.length" data-testid="db-length" :min="1" :max="65536" />
          </el-form-item>
          <el-form-item :label="t('simulator.enabled')">
            <el-switch v-model="db.enabled" />
          </el-form-item>
        </el-form>
        <div class="ds-actions">
          <ConsoleActionButton label-key="simulator.addPoint" data-testid="point-add" :disabled="!db.manual" @click="addPoint" />
          <ConsoleActionButton label-key="simulator.toManual" :disabled="db.manual" @click="manualOpen=true" />
          <ConsoleActionButton label-key="simulator.removeDb" tone="danger" @click="deleteDbOpen=true" />
          <ConsoleActionButton label-key="simulator.standardLayout" data-testid="standard-layout" :disabled="local.dirty||local.busy||db.manual" @click="previewLayout('standard')" />
          <ConsoleActionButton label-key="simulator.manualLayout" data-testid="layout-open" :disabled="local.dirty||local.busy" @click="layoutOpen=true" />
          <ConsoleActionButton label-key="simulator.previewNames" data-testid="names-open" :disabled="local.dirty||local.busy||!selected.size" @click="previewNames" />
          <ConsoleActionButton label-key="simulator.confirmInitialPolicy" data-testid="points-confirm-initial" :disabled="local.busy||!selected.size" @click="local.save(Array.from(selected))" />
        </div>
        <ConsoleTableShell v-model:current-page="page" v-model:page-size="pageSize" :page-sizes="[10,20,50]" :total="db.points.length">
          <el-table :data="rows" row-key="id" data-testid="points-table">
            <el-table-column width="50">
              <template #header>
                <el-checkbox data-testid="point-select-page" :model-value="rows.length>0&&rows.every(p=>selected.has(p.id))" @change="selectPage" />
              </template>
              <template #default="{row}">
                <el-checkbox :model-value="selected.has(row.id)" :data-testid="'point-select-'+row.id" @change="toggle(row.id)" />
              </template>
            </el-table-column>
            <el-table-column prop="name" :label="t('simulator.name')" />
            <el-table-column prop="sourcePath" :label="t('simulator.sourcePath')" />
            <el-table-column prop="dataType" :label="t('simulator.dataType')" />
            <el-table-column :label="t('simulator.address')">
              <template #default="{row}">{{ row.byte??'—' }}{{ row.bit===null?'':'.'+row.bit }}</template>
            </el-table-column>
            <el-table-column :label="t('simulator.confirmation')">
              <template #default="{row}">{{ t(row.confirmations.initial&&row.confirmations.policy?'simulator.confirmed':'simulator.pending') }}</template>
            </el-table-column>
            <el-table-column :label="t('simulator.action')">
              <template #default="{row}">
                <ConsoleActionButton label-key="simulator.edit" size="small" data-testid="point-edit" @click="edit(row)" />
                <ConsoleActionButton label-key="simulator.remove" size="small" tone="danger" :disabled="!db.manual" @click="deleting=row" />
              </template>
            </el-table-column>
          </el-table>
        </ConsoleTableShell>
      </div>
      <el-empty v-else :image-size="64" :description="t('simulator.selectDb')" />
    </ConsoleCard>
    <SourceImportPanel />
    <PointEditor v-model="editorOpen" :point="editor" @confirm="keep" />
    <PointNamePreviewDialog :preview="candidate" :busy="local.busy" @cancel="candidate=null" @confirm="confirmPreview" />
    <el-dialog v-model="layoutOpen" :title="t('simulator.manualLayout')" :append-to-body="false">
      <el-input v-model="reason" data-testid="layout-reason" :placeholder="t('simulator.manualReason')" maxlength="1000" />
      <template #footer>
        <ConsoleActionButton label-key="simulator.cancel" @click="layoutOpen=false" />
        <ConsoleActionButton label-key="simulator.preview" data-testid="layout-preview" :disabled="!reason.trim()" @click="previewLayout('manual')" />
      </template>
    </el-dialog>
    <ConsoleOperationDialog v-model="manualOpen" title-key="simulator.toManual" message-key="simulator.toManualHint" cancel-label-key="simulator.cancel" confirm-label-key="simulator.confirm" @confirm="convertManual" />
    <ConsoleOperationDialog v-model="deleteDbOpen" title-key="simulator.removeDb" message-key="simulator.removeDbHint" cancel-label-key="simulator.cancel" confirm-label-key="simulator.confirm" confirm-tone="danger" @confirm="removeDb" />
    <ConsoleOperationDialog :model-value="!!deleting" title-key="simulator.remove" message-key="simulator.removePointHint" cancel-label-key="simulator.cancel" confirm-label-key="simulator.confirm" confirm-tone="danger" @update:model-value="deleting=null" @confirm="removePoint" />
  </section>
</template>
<script setup lang="ts">
import { computed, inject, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { simulatorKey } from '../../../../console/composables/useDeviceSimulator';
import * as ipc from '../../../../services/deviceSimulator';
import ConsoleCard from '../../../../components/console/ConsoleCard.vue';
import ConsoleActionButton from '../../../../components/console/ConsoleActionButton.vue';
import ConsoleTableShell from '../../../../components/console/ConsoleTableShell.vue';
import ConsoleOperationDialog from '../../../../components/console/ConsoleOperationDialog.vue';
import ConfigRevisionBar from '../../../../components/console/ConfigRevisionBar.vue';
import SourceImportPanel from '../../components/SourceImportPanel.vue';
import PointEditor from '../../components/PointEditor.vue';
import PointNamePreviewDialog from '../../components/PointNamePreviewDialog.vue';
const local = inject(simulatorKey)!, { t } = useI18n(), db = computed(() => local.selectedDb), page = ref(1), pageSize = ref(10), selected = ref(new Set<string>()), editorOpen = ref(false), editor = ref<ipc.Point | null>(null), deleting = ref<ipc.Point | null>(null), candidate = ref<ipc.Preview | null>(null), layoutOpen = ref(false), reason = ref(''), manualOpen = ref(false), deleteDbOpen = ref(false);
const rows = computed(() => db.value?.points.slice((page.value - 1) * pageSize.value, page.value * pageSize.value) || []);
watch(() => local.instanceId, () => { local.dbId = local.selected?.dbs[0]?.id || ''; selected.value = new Set(); page.value = 1; });
watch(() => local.dbId, () => { selected.value = new Set(); page.value = 1; });
function toggle(id: string) { const next = new Set(selected.value); next.has(id) ? next.delete(id) : next.add(id); selected.value = next; }
function selectPage(value: unknown) { const next = new Set(selected.value); rows.value.forEach(p => value ? next.add(p.id) : next.delete(p.id)); selected.value = next; }
function addDb() { if (!local.selected)
    return; const number = Array.from({ length: 65535 }, (_, i) => i + 1).find(n => !local.selected!.dbs.some(d => d.number === n))!; const d: ipc.Db = { id: crypto.randomUUID(), name: 'DB' + number, number, length: 1, enabled: true, manual: true, binding: null, points: [], policy: {}, regions: [], addressConfirmation: null }; local.selected.dbs.push(d); local.dbId = d.id; }
function addPoint() { if (!db.value)
    return; editor.value = { id: crypto.randomUUID(), name: '', displayName: '', dataType: 'BOOL', enabled: true, sourcePath: '', segments: [], byte: 0, bit: 0, manualReason: '', manual: true, policy: {}, confirmations: { initial: null, policy: null } }; editorOpen.value = true; }
function edit(p: ipc.Point) { editor.value = p; editorOpen.value = true; }
function keep(p: ipc.Point) { if (!db.value)
    return; const at = db.value.points.findIndex(v => v.id === p.id); if (at < 0)
    db.value.points.push(p);
else
    db.value.points[at] = p; }
function removePoint() { if (db.value && deleting.value)
    db.value.points = db.value.points.filter(p => p.id !== deleting.value!.id); deleting.value = null; }
function removeDb() { if (local.selected)
    local.selected.dbs = local.selected.dbs.filter(d => d.id !== local.dbId); local.dbId = local.selected?.dbs[0]?.id || ''; deleteDbOpen.value = false; }
function convertManual() { if (db.value) {
    db.value.manual = true;
    db.value.binding = null;
    db.value.points.forEach(p => p.manual = true);
} manualOpen.value = false; }
async function previewLayout(method: string) { if (!db.value)
    return; const p = await local.action(() => ipc.previewLayout({ expectedEtag: local.configuration!.etag, instanceId: local.instanceId, dbId: db.value!.id, method, reason: reason.value })); if (p) {
    candidate.value = p;
    layoutOpen.value = false;
} }
async function previewNames() { const p = await local.action(() => ipc.previewNames({ expectedEtag: local.configuration!.etag, instanceId: local.instanceId, pointIds: Array.from(selected.value), addressOnly: false })); if (p)
    candidate.value = p; }
async function confirmPreview() { if (!candidate.value)
    return; const p = candidate.value; const result = await local.action(() => ipc.confirmPreview(p.kind as 'layout' | 'names', p), true); if (result !== undefined)
    candidate.value = null; }
</script>
