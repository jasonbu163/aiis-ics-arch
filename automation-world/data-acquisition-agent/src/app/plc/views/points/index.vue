<!-- DAA本地SQLite视图：唯一local owner提供状态/动作，导航不驱动PLC或health。 -->
<template>
  <template v-if="local">

    <ConsoleCard title-key="common.local.pointsGroups" body-class="console-card__body--table">
      <template #tools>
        <ElForm label-position="top" class="daa-local-filters" @submit.prevent>
          <ElFormItem :label="t('common.local.plc')"><ElSelect v-model="local.selectedPlc" :disabled="!!pointEditor" append-to="#daa-feedback" @change="changePointScope"><ElOption v-for="p in local.plcs" :key="p.id" :label="p.name" :value="p.id" /></ElSelect></ElFormItem>
          <ElFormItem :label="t('common.local.db')"><ElSelect v-model="local.selectedDb" :disabled="!!pointEditor" append-to="#daa-feedback" @change="local.pointPage = 1; local.offsets = []"><ElOption :label="t('common.local.all')" value="" /><ElOption v-for="d in local.dbs" :key="d.id" :label="d.name + ' · DB' + d.number" :value="d.id" /></ElSelect></ElFormItem>
          <ElFormItem :label="t('common.local.filter')"><ElInput v-model="local.query" clearable @input="local.pointPage = 1" /></ElFormItem>
        </ElForm>
      </template>
      <ConsoleTableShell v-model:current-page="local.pointPage" :page-size="20" :total="local.points.length" layout="total, prev, pager, next">
        <el-table :data="local.pagedPoints" row-key="id" :empty-text="t(local.draft ? 'common.local.emptyPoints' : 'common.feedback.notLoaded')" :tooltip-options="{ appendTo: '#daa-feedback' }">
          <el-table-column :label="t('common.local.point')" min-width="170"><template #default="{ row }"><strong>{{ row.name }}</strong><small class="muted-cell">{{ row.sourcePath }}</small></template></el-table-column>
          <el-table-column prop="dataType" :label="t('common.local.type')" min-width="90" />
          <el-table-column :label="t('common.local.addressSummary')" min-width="145"><template #default="{ row }"><span v-if="row.address?.confirmed">DB{{ local.draft?.dbs.find(d => d.id === row.dbId)?.number }} / {{ row.address.offset }}<template v-if="row.address.bit !== null">.{{ row.address.bit }}</template></span><el-tag v-else type="warning" effect="plain">{{ t('common.local.addressUnconfirmed') }}</el-tag><small v-if="row.address?.origin === 'manual'" class="muted-cell">{{ t('common.local.protected') }}</small></template></el-table-column>
          <el-table-column :label="t('common.local.group')" min-width="135"><template #default="{ row }">{{ local.draft?.groups.find(g => g.id === row.groupId)?.name ?? t('common.local.unassigned') }}</template></el-table-column>
          <el-table-column :label="t('common.local.enabled')" width="90"><template #default="{ row }"><el-tag :type="row.enabled ? 'success' : 'info'" effect="plain">{{ local.label(String(row.enabled)) }}</el-tag></template></el-table-column>
          <el-table-column :label="t('common.local.actions')" width="195"><template #default="{ row }"><div class="row-actions"><ConsoleActionButton size="small" label-key="common.local.edit" :disabled="local.busy || !!pointEditor" @click="editLocalPoint(row)" /><ConsoleActionButton size="small" label-key="common.local.diagnose" :disabled="local.busy || !local.view?.active" @click="local.control('daa_diagnose_point', [row.plcId], false, row.id)" /></div></template></el-table-column>
        </el-table>
      </ConsoleTableShell>
      <Teleport to="#daa-feedback">
        <ElDialog :model-value="!!pointEditor" :title="t('common.local.editPoint') + ' · ' + (pointEditor?.sourcePath ?? '')" :append-to-body="false" :close-on-click-modal="false" :close-on-press-escape="!local.busy" :show-close="!local.busy" width="min(780px, calc(100vw - 32px))" @update:model-value="$event || cancelLocalPoint()">
          <div v-if="pointEditor && pointEditor.address" class="console-stack">
            <el-alert v-if="local.error" :title="local.label(local.error)" type="error" :closable="false" show-icon />
            <p class="daa-capability-note">{{ t('common.local.editHint') }}</p>
        <ElForm :disabled="local.busy" label-position="top" class="daa-local-form-grid" @submit.prevent>
          <ElFormItem :label="t('common.local.name')"><ElInput v-model="pointEditor.name" /></ElFormItem>
          <ElFormItem :label="t('common.local.group')"><ElSelect :model-value="pointEditor.groupId ?? ''" @update:model-value="pointEditor.groupId = String($event) || null" append-to="#daa-feedback"><ElOption :label="t('common.local.unassigned')" value="" /><ElOption v-for="g in local.groups" :key="g.id" :label="g.name" :value="g.id" /></ElSelect></ElFormItem>
          <ElFormItem :label="t('common.local.enabled')"><ElSwitch v-model="pointEditor.enabled" /></ElFormItem>
          <ElFormItem :label="t('common.local.offset')"><ElInputNumber v-model="pointEditor.address.offset" :min="0" :max="65535" :precision="0" controls-position="right" @change="manualPointAddress" /></ElFormItem>
          <ElFormItem v-if="pointEditor.dataType === 'BOOL'" :label="t('common.local.bit')"><ElInputNumber :model-value="pointEditor.address.bit ?? 0" @update:model-value="pointEditor.address.bit = Number($event)" :min="0" :max="7" :precision="0" controls-position="right" @change="manualPointAddress" /></ElFormItem>
          <ElFormItem :label="t('common.local.reason')"><ElInput v-model="pointEditor.address.reason" @input="manualPointAddress" /></ElFormItem>
          <ElFormItem :label="t('common.local.confirmed')"><ElSwitch v-model="pointEditor.address.confirmed" /></ElFormItem>
          <ElFormItem :label="t('common.local.comment')" class="daa-local-form-wide"><ElInput v-model="pointEditor.comment" type="textarea" :rows="2" /></ElFormItem>
        </ElForm>
        <div class="console-action-group"><ConsoleActionButton label-key="common.local.cancelEdit" :disabled="local.busy" @click="cancelLocalPoint" /><ConsoleActionButton label-key="common.local.save" :disabled="local.busy" tone="primary" @click="applyLocalPoint" /></div>
        <details class="daa-details"><summary>{{ t('common.local.identityDetails') }}</summary><code>{{ pointEditor.id }}</code><p>{{ pointEditor.dataType }} · {{ t(pointEditor.address.origin === 'manual' ? 'common.local.manualOrigin' : 'common.local.inferredOrigin') }}</p></details>
          </div>
        </ElDialog>
      </Teleport>
      <ElCollapse>
        <ElCollapseItem name="sources" :title="t('common.local.sourceTools')">
          <SourceImportPanel :local="local" />
        </ElCollapseItem>
        <ElCollapseItem name="offsets" :title="t('common.local.offsetTools')">
          <p class="daa-capability-note">{{ t('common.local.pointLimits') }}</p><p v-if="local.offsets.length" class="daa-capability-note">{{ t('plc.sourceImport.layoutProfile', { profile: local.offsets[0]?.profile }) }}</p><el-alert v-if="local.dirty || local.editing" :title="t('common.local.saveBeforeTools')" type="warning" :closable="false" />
          <div class="console-action-group"><ConsoleActionButton label-key="common.local.previewOffsets" :disabled="local.busy || local.dirty || local.editing || !local.selectedDb" @click="local.infer(false)" /></div>
          <Teleport to="#daa-feedback"><ElDialog v-model="local.offsetPreviewOpen" :title="t('common.local.previewOffsets')" :append-to-body="false" :close-on-click-modal="false" :show-close="!local.busy" :close-on-press-escape="!local.busy" width="min(1000px, calc(100vw - 32px))" class="daa-import-dialog">
            <p class="daa-capability-note">{{ t('plc.sourceImport.layoutProfile', { profile: local.offsets[0]?.profile ?? '' }) }}</p>
            <p>{{ t('plc.sourceImport.lengths', { current: local.dbs.find(d => d.id === local?.selectedDb)?.length ?? 0, calculated: local.offsets[0]?.dbLength ?? 0 }) }}</p>
            <el-table :data="local.offsets" row-key="pointId" size="small"><el-table-column :label="t('common.local.point')" min-width="140"><template #default="{ row }">{{ local.draft?.points.find(p => p.id === row.pointId)?.sourcePath }}</template></el-table-column><el-table-column :label="t('common.local.addressSummary')" min-width="160"><template #default="{ row }">{{ row.old?.offset ?? '—' }}.{{ row.old?.bit ?? '—' }} → {{ row.proposed.offset }}.{{ row.proposed.bit ?? '—' }}</template></el-table-column><el-table-column :label="t('common.local.dbLength')" prop="dbLength" /><el-table-column :label="t('common.local.confirmState')"><template #default="{ row }">{{ row.protectedManual ? t('common.local.protected') : '—' }}<small v-if="row.manualConflict" class="muted-cell">{{ t('plc.sourceImport.manualConflict') }}</small></template></el-table-column></el-table>
            <template #footer><div class="console-action-group"><ConsoleActionButton label-key="plc.sourceImport.closePreview" :disabled="local.busy" @click="local.offsetPreviewOpen = false" /><ConsoleActionButton label-key="common.local.confirmOffsets" tone="primary" :disabled="local.busy || local.dirty || local.editing || !local.offsets.some(o => !o.protectedManual)" @click="local.infer(true)" /></div></template>
          </ElDialog></Teleport>
        </ElCollapseItem>
        <ElCollapseItem name="groups" :title="t('common.local.groupTools')">
          <div class="console-action-group"><ConsoleActionButton label-key="common.local.disableFiltered" :disabled="local.busy" @click="local.bulk(null, false)" /><ConsoleActionButton label-key="common.local.addGroup" :disabled="local.busy || !local.selectedPlc || local.groups.length >= 8" @click="local.addGroup" /></div>
          <p class="daa-capability-note">{{ t('common.local.filtered', { count: local.points.length }) }}</p>
          <section v-for="g in local.groups" :key="g.id" class="daa-local-edit-section"><ElForm inline label-position="top" @submit.prevent><ElFormItem :label="t('common.local.name')"><ElInput v-model="g.name" /></ElFormItem><ElFormItem :label="t('common.local.period')"><ElInputNumber v-model="g.intervalMs" :min="500" :max="3600000" :precision="0" controls-position="right" /></ElFormItem><ElFormItem :label="t('common.local.enabled')"><ElSwitch v-model="g.enabled" /></ElFormItem></ElForm><div class="console-action-group"><ConsoleActionButton size="small" label-key="common.local.assignFiltered" @click="local.bulk(g.id, true)" /><ConsoleActionButton size="small" label-key="common.local.remove" tone="danger" @click="removeLocalGroup(g.id)" /></div></section>
        </ElCollapseItem>
      </ElCollapse>
    </ConsoleCard>
  </template>
</template>

<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue';
import { ElDialog, ElForm, ElFormItem, ElInput, ElInputNumber, ElSelect, ElOption, ElSwitch, ElCollapse, ElCollapseItem, ElTree } from 'element-plus';
import SourceImportPanel from '../../components/SourceImportPanel.vue';
import type { Point } from '../../../../services/localAcquisition';

import { inject } from 'vue';
import { localConsoleKey } from '../../../../console/composables/useLocalAcquisitionConsole';
const local = inject(localConsoleKey);
import { computed } from 'vue';
import { Refresh } from '@element-plus/icons-vue';
import { useI18n } from 'vue-i18n';
import ConsoleActionButton from '../../../../components/console/ConsoleActionButton.vue';
import ConsoleCard from '../../../../components/console/ConsoleCard.vue';
import ConsoleTableShell from '../../../../components/console/ConsoleTableShell.vue';
const { t } = useI18n();
async function removeLocalGroup(id: string) {
    if (await local?.confirmAction('common.local.removeConfirm')) local?.removeGroup(id);
}

const pointEditor = ref<Point | null>(null);
function changePointScope() { if (local) { local.selectedDb = ''; local.pointPage = 1; local.sources = []; local.identification = null; local.mappings = []; local.preview = null; local.offsets = []; } pointEditor.value = null; }
function editLocalPoint(p: Point) { const copy: Point = JSON.parse(JSON.stringify(p)); if (!copy.address) copy.address = { offset: 0, bit: p.dataType === 'BOOL' ? 0 : null, confirmed: false, origin: 'manual', reason: '' }; pointEditor.value = copy; }
function manualPointAddress() { if (pointEditor.value?.address) { pointEditor.value.address.origin = 'manual'; pointEditor.value.address.confirmed = false; } }
function cancelLocalPoint() { pointEditor.value = null; }
async function applyLocalPoint() {
    const owner = local, edit = pointEditor.value;
    if (!owner?.draft || !edit) return;
    const candidate = JSON.parse(JSON.stringify(owner.draft));
    const point = candidate.points.find((p: Point) => p.id === edit.id);
    if (!point) return;
    Object.assign(point, { name: edit.name, comment: edit.comment, enabled: edit.enabled, groupId: edit.groupId, address: JSON.parse(JSON.stringify(edit.address)) });
    if (await owner.saveCandidate(candidate)) pointEditor.value = null;
}

watch(() => [local?.view, local?.selectedPlc, local?.selectedDb], () => { pointEditor.value = null; });

watch(pointEditor, v => { if (local) local.editing = !!v; });
onUnmounted(() => { if (local) local.editing = false; });
</script>
