<!-- DAA点位：支持选点命名与分组、保存草稿后编辑，并显示本次只读诊断结果。 -->
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
      <div class="console-action-group daa-name-tools"><span>{{ t('plc.naming.selected', { count: local.selectedPoints.length }) }}</span><ConsoleActionButton label-key="plc.naming.preview" :disabled="local.busy || local.dirty || local.editing || !local.selectedPoints.length" @click="local.previewNames" /></div>
      <PointNamePreviewDialog :local="local" />
      <ConsoleTableShell v-model:current-page="local.pointPage" v-model:page-size="local.pointPageSize" :page-sizes="[10,20,50]" :total="local.points.length" layout="total, sizes, prev, pager, next">
        <el-table :data="local.pagedPoints" row-key="id" :empty-text="t(local.draft ? 'common.local.emptyPoints' : 'common.feedback.notLoaded')" :tooltip-options="{ appendTo: '#daa-feedback' }">
          <el-table-column :label="t('plc.naming.select')" width="92">
            <template #header><ElCheckbox :model-value="pageSelection.checked" :indeterminate="pageSelection.indeterminate" :disabled="local.busy || local.editing || !local.pagedPoints.length" :aria-label="t('plc.naming.selectPage')" :title="t('plc.naming.selectPage')" @change="selectPageNames(!!$event)" /></template>
            <template #default="{ row }"><ElCheckbox :model-value="local.selectedNameIds.includes(row.id)" :disabled="local.busy || local.editing" :aria-label="t('plc.naming.selectPoint', { path: row.sourcePath })" @change="local.toggleNamePoint(row.id, !!$event)" /></template>
          </el-table-column>
          <el-table-column :label="t('plc.naming.technicalName')" min-width="210"><template #default="{ row }"><strong>{{ row.name || t('plc.naming.modes.pending') }}</strong><small class="muted-cell">{{ row.sourcePath }}</small><el-tag size="small" effect="plain" :type="row.nameMode === 'pending' ? 'warning' : 'info'">{{ t('plc.naming.modes.' + (row.nameMode ?? 'legacy')) }}</el-tag></template></el-table-column>
          <el-table-column prop="dataType" :label="t('common.local.type')" min-width="90" />
          <el-table-column :label="t('common.local.addressSummary')" min-width="145"><template #default="{ row }"><span v-if="row.address?.confirmed">DB{{ local.draft?.dbs.find(d => d.id === row.dbId)?.number }} / {{ row.address.offset }}<template v-if="row.address.bit !== null">.{{ row.address.bit }}</template></span><el-tag v-else type="warning" effect="plain">{{ t('common.local.addressUnconfirmed') }}</el-tag><small v-if="row.address?.origin === 'manual'" class="muted-cell">{{ t('common.local.protected') }}</small></template></el-table-column>
          <el-table-column :label="t('common.local.group')" min-width="135"><template #default="{ row }">{{ local.draft?.groups.find(g => g.id === row.groupId)?.name ?? t('common.local.unassigned') }}</template></el-table-column>
          <el-table-column :label="t('common.local.enabled')" width="90"><template #default="{ row }"><el-tag :type="row.enabled ? 'success' : 'info'" effect="plain">{{ local.label(String(row.enabled)) }}</el-tag></template></el-table-column>
          <el-table-column :label="t('common.local.actions')" width="260">
            <template #default="{ row }">
              <div class="row-actions">
                <ConsoleActionButton size="small" :label-key="local.dirty ? 'common.local.saveAndEdit' : 'common.local.edit'" :disabled="local.busy || local.editing || !!pointEditor" @click="editLocalPoint(row)" />
                <ConsoleActionButton size="small" label-key="common.local.diagnose" :disabled="local.busy || local.editing || !!pointDiagnosis || !local.view?.active" @click="startPointDiagnosis(row)" />
              </div>
            </template>
          </el-table-column>
        </el-table>
      </ConsoleTableShell>
      <Teleport to="#daa-feedback">
        <ElDialog :model-value="!!pointDiagnosis" :title="t('common.local.diagnose')" :append-to-body="false" :close-on-click-modal="false" width="min(520px, calc(100vw - 32px))" class="daa-name-dialog" @update:model-value="$event || closePointDiagnosis()">
          <div v-if="pointDiagnosis" class="console-stack">
            <strong class="daa-confirm-message">{{ pointDiagnosis.target }}</strong>
            <p class="daa-capability-note">{{ t('plc.diagnosis.hint') }}</p>
            <ElAlert
              :title="t('plc.diagnosis.' + pointDiagnosis.status, { seconds: diagnosticWaitSeconds })"
              :type="diagnosticTone[pointDiagnosis.status]"
              :description="pointDiagnosis.reason ? local.label(pointDiagnosis.reason) : undefined"
              :closable="false"
              show-icon
            />
            <dl v-if="pointDiagnosis.reading" class="daa-local-facts">
              <dt>{{ t('plc.value') }}</dt><dd><code>{{ pointDiagnosis.reading.value }}</code></dd>
              <dt>{{ t('common.local.addressSummary') }}</dt><dd>{{ pointDiagnosis.reading.address }}</dd>
              <dt>{{ t('common.local.type') }}</dt><dd>{{ pointDiagnosis.reading.dataType }}</dd>
              <dt>{{ t('common.local.quality') }}</dt><dd>{{ local.label(pointDiagnosis.reading.quality) }}</dd>
              <dt>{{ t('plc.diagnosis.observedAt') }}</dt><dd>{{ formatBusinessTime(pointDiagnosis.reading.observedAt) }}</dd>
            </dl>
          </div>
          <template #footer><div class="console-action-group"><ConsoleActionButton label-key="plc.diagnosis.close" @click="closePointDiagnosis" /></div></template>
        </ElDialog>
        <ElDialog :model-value="!!pointEditor" :title="t('common.local.editPoint') + ' · ' + (pointEditor?.sourcePath ?? '')" :append-to-body="false" :close-on-click-modal="false" :close-on-press-escape="!local.busy" :show-close="!local.busy" width="min(780px, calc(100vw - 32px))" class="daa-name-dialog" @update:model-value="$event || cancelLocalPoint()">
          <div v-if="pointEditor && pointEditor.address" class="console-stack">
            <el-alert v-if="local.error" :title="local.label(local.error)" type="error" :closable="false" show-icon />
            <p class="daa-capability-note">{{ t('common.local.editHint') }}</p>
        <ElForm :disabled="local.busy" label-position="top" class="daa-local-form-grid" @submit.prevent>
          <ElFormItem :label="t('plc.naming.technicalName')"><ElInput v-model="pointEditor.name" /></ElFormItem>
          <ElFormItem :label="t('common.local.group')"><ElSelect :model-value="pointEditor.groupId ?? ''" @update:model-value="pointEditor.groupId = String($event) || null" append-to="#daa-feedback"><ElOption :label="t('common.local.unassigned')" value="" /><ElOption v-for="g in local.groups" :key="g.id" :label="g.name" :value="g.id" /></ElSelect></ElFormItem>
          <ElFormItem :label="t('common.local.enabled')"><ElSwitch v-model="pointEditor.enabled" /></ElFormItem>
          <ElFormItem :label="t('common.local.offset')"><ElInputNumber v-model="pointEditor.address.offset" :min="0" :max="65535" :precision="0" controls-position="right" @change="manualPointAddress" /></ElFormItem>
          <ElFormItem v-if="pointEditor.dataType === 'BOOL'" :label="t('common.local.bit')"><ElInputNumber :model-value="pointEditor.address.bit ?? 0" @update:model-value="pointEditor.address.bit = Number($event)" :min="0" :max="7" :precision="0" controls-position="right" @change="manualPointAddress" /></ElFormItem>
          <ElFormItem :label="t('common.local.reason')"><ElInput v-model="pointEditor.address.reason" @input="manualPointAddress" /></ElFormItem>
          <ElFormItem :label="t('common.local.confirmed')"><ElSwitch v-model="pointEditor.address.confirmed" /></ElFormItem>
          <ElFormItem :label="t('common.local.comment')" class="daa-local-form-wide"><ElInput v-model="pointEditor.comment" type="textarea" :rows="2" /></ElFormItem>
        </ElForm>
        <p class="daa-capability-note">{{ t('plc.naming.editHint') }}</p>
        <p v-if="local.namePreviewBusy">{{ t('plc.naming.previewing') }}</p>
        <p v-for="row in local.namePreview?.rows ?? []" :key="row.pointId" class="daa-name-diff">{{ row.oldName || '—' }} → <strong>{{ row.proposedName || t('plc.naming.modes.pending') }}</strong> · {{ t('plc.naming.modes.' + (row.proposedMode ?? 'legacy')) }}</p>
        <p v-for="(issue, i) in local.namePreview?.readiness ?? []" :key="i">{{ local.label(issue.code) }} · {{ issue.path }}</p>
        <details class="daa-details"><summary>{{ t('common.local.identityDetails') }}</summary><code>{{ pointEditor.id }}</code><p>{{ pointEditor.dataType }} · {{ t(pointEditor.address.origin === 'manual' ? 'common.local.manualOrigin' : 'common.local.inferredOrigin') }}</p></details>
          </div>
          <template #footer><div class="console-action-group"><ConsoleActionButton label-key="common.local.cancelEdit" :disabled="local.busy" @click="cancelLocalPoint" /><ConsoleActionButton label-key="common.local.save" :disabled="local.busy || local.namePreviewBusy || !local.namePreview?.canConfirm" tone="primary" @click="applyLocalPoint" /></div></template>
        </ElDialog>
      </Teleport>
      <ElCollapse>
        <ElCollapseItem name="sources" :title="t('common.local.sourceTools')">
          <SourceImportPanel :local="local" />
        </ElCollapseItem>
        <ElCollapseItem name="offsets" :title="t('common.local.offsetTools')">
          <div class="console-stack">
          <p class="daa-capability-note">{{ t('common.local.pointLimits') }}</p><p v-if="local.offsets.length" class="daa-capability-note">{{ t('plc.sourceImport.layoutProfile', { profile: local.offsets[0]?.profile }) }}</p><el-alert v-if="local.dirty || local.editing" :title="t('common.local.saveBeforeTools')" type="warning" :closable="false" />
          <div class="console-action-group"><ConsoleActionButton label-key="common.local.previewOffsets" :disabled="local.busy || local.dirty || local.editing || !local.selectedDb" @click="local.infer(false)" /></div>
          </div>
          <Teleport to="#daa-feedback"><ElDialog v-model="local.offsetPreviewOpen" :title="t('common.local.previewOffsets')" :append-to-body="false" :close-on-click-modal="false" :show-close="!local.busy" :close-on-press-escape="!local.busy" width="min(1000px, calc(100vw - 32px))" class="daa-import-dialog">
            <p class="daa-capability-note">{{ t('plc.sourceImport.layoutProfile', { profile: local.offsets[0]?.profile ?? '' }) }}</p>
            <p>{{ t('plc.sourceImport.lengths', { current: local.dbs.find(d => d.id === local?.selectedDb)?.length ?? 0, calculated: local.offsets[0]?.dbLength ?? 0 }) }}</p>
            <el-table :data="local.offsets" row-key="pointId" size="small"><el-table-column :label="t('common.local.point')" min-width="140"><template #default="{ row }">{{ local.draft?.points.find(p => p.id === row.pointId)?.sourcePath }}</template></el-table-column><el-table-column :label="t('common.local.addressSummary')" min-width="160"><template #default="{ row }">{{ row.old?.offset ?? '—' }}.{{ row.old?.bit ?? '—' }} → {{ row.proposed.offset }}.{{ row.proposed.bit ?? '—' }}</template></el-table-column><el-table-column :label="t('plc.naming.newName')" min-width="210"><template #default="{ row }">{{ row.proposedName ?? local.draft?.points.find(p => p.id === row.pointId)?.name ?? '—' }}<small v-if="row.proposedNameMode" class="muted-cell">{{ t('plc.naming.modes.' + row.proposedNameMode) }}</small></template></el-table-column><el-table-column :label="t('common.local.dbLength')" prop="dbLength" /><el-table-column :label="t('common.local.confirmState')"><template #default="{ row }">{{ row.protectedManual ? t('common.local.protected') : '—' }}<small v-if="row.manualConflict" class="muted-cell">{{ t('plc.sourceImport.manualConflict') }}</small></template></el-table-column></el-table>
            <template #footer><div class="console-action-group"><ConsoleActionButton label-key="plc.sourceImport.closePreview" :disabled="local.busy" @click="local.offsetPreviewOpen = false" /><ConsoleActionButton label-key="common.local.confirmOffsets" tone="primary" :disabled="local.busy || local.dirty || local.editing || !local.offsets.some(o => !o.protectedManual)" @click="local.infer(true)" /></div></template>
          </ElDialog></Teleport>
        </ElCollapseItem>
        <ElCollapseItem name="groups" :title="t('common.local.groupTools')">
          <div class="console-action-group"><ConsoleActionButton label-key="common.local.disableSelected" :disabled="local.busy || local.editing || !local.selectedPoints.length" @click="local.bulk(null, false)" /><ConsoleActionButton label-key="common.local.addGroup" :disabled="local.busy || local.editing || !local.selectedPlc || local.groups.length >= 8" @click="local.addGroup" /></div>
          <p class="daa-capability-note">{{ t('common.local.selectedGroupHint', { count: local.selectedPoints.length }) }}</p>
          <section v-for="g in local.groups" :key="g.id" class="daa-local-edit-section"><ElForm inline label-position="top" :disabled="local.busy || local.editing" @submit.prevent><ElFormItem :label="t('common.local.name')"><ElInput v-model="g.name" /></ElFormItem><ElFormItem :label="t('common.local.period')"><ElInputNumber v-model="g.intervalMs" :min="500" :max="3600000" :precision="0" controls-position="right" /></ElFormItem><ElFormItem :label="t('common.local.enabled')"><ElSwitch v-model="g.enabled" /></ElFormItem></ElForm><div class="console-action-group"><ConsoleActionButton size="small" label-key="common.local.assignSelected" :disabled="local.busy || local.editing || !local.selectedPoints.length" @click="local.bulk(g.id, true)" /><ConsoleActionButton size="small" label-key="common.local.remove" tone="danger" :disabled="local.busy || local.editing" @click="removeLocalGroup(g.id)" /></div></section>
        </ElCollapseItem>
      </ElCollapse>
    </ConsoleCard>
  </template>
</template>

<script setup lang="ts">
import { ref, watch, onUnmounted, nextTick } from 'vue';
import { ElAlert, ElCheckbox, ElDialog, ElForm, ElFormItem, ElInput, ElInputNumber, ElSelect, ElOption, ElSwitch, ElCollapse, ElCollapseItem, ElTree } from 'element-plus';
import SourceImportPanel from '../../components/SourceImportPanel.vue';
import PointNamePreviewDialog from '../../components/PointNamePreviewDialog.vue';
import type { Point } from '../../../../services/localAcquisition';
import { sampleValue } from '../../../../console/sampleDetails';
import { formatBusinessTime } from '../../../../console/time';

import { inject } from 'vue';
import { diagnosticTone, diagnosticWaitSeconds, localConsoleKey } from '../../../../console/composables/useLocalAcquisitionConsole';
const local = inject(localConsoleKey);
import { computed } from 'vue';
import { Refresh } from '@element-plus/icons-vue';
import { useI18n } from 'vue-i18n';
import ConsoleActionButton from '../../../../components/console/ConsoleActionButton.vue';
import ConsoleCard from '../../../../components/console/ConsoleCard.vue';
import ConsoleTableShell from '../../../../components/console/ConsoleTableShell.vue';
const { t } = useI18n();
const pageSelection = computed(() => {
    const points = local?.pagedPoints ?? [];
    const count = points.filter(p => local?.selectedNameIds.includes(p.id)).length;
    return { checked: points.length > 0 && count === points.length, indeterminate: count > 0 && count < points.length };
});
function selectPageNames(selected: boolean) {
    if (!local || local.busy || local.editing) return;
    for (const point of local.pagedPoints) local.toggleNamePoint(point.id, selected);
}
async function removeLocalGroup(id: string) {
    if (await local?.confirmAction('common.local.removeConfirm')) local?.removeGroup(id);
}

const pointEditor = ref<Point | null>(null);
interface DiagnosisFact {
    definition: Pick<Point, 'id' | 'plcId' | 'address' | 'dataType'>;
    value: unknown;
    quality: string;
    reason: string | null;
    observedAt: string;
}
interface PointDiagnosis {
    target: string;
    operationId: string | null;
    status: keyof typeof diagnosticTone;
    reason: string | null;
    reading: { value: string; address: string; dataType: string; quality: string; observedAt: string } | null;
}
const pointDiagnosis = computed<PointDiagnosis | null>(() => {
    const current = local?.plcDiagnostic;
    if (current?.action !== 'diagnose') return null;
    const view = { target: current.target, operationId: current.operationId, reason: current.reason, reading: null };
    if (current.status !== 'applied') return { ...view, status: current.status };
    // applied 只表示操作完成，实际读数是否成功由点位质量决定。
    const result = current.result as { diagnosticId: string; revision: string; points: Record<string, Record<string, DiagnosisFact>> } | null;
    if (current.pointId && result?.diagnosticId === current.operationId && result.revision === current.revision) {
        for (const [dbNumber, points] of Object.entries(result.points ?? {})) {
            const fact: DiagnosisFact | undefined = points?.[current.pointId];
            if (fact?.definition?.id !== current.pointId || fact.definition.plcId !== current.plcId || !fact.quality) continue;
            const address = fact.definition.address;
            const good = fact.quality === 'good';
            return {
                ...view,
                status: good ? (fact.value == null ? 'unavailable' : 'success') : 'failed',
                reason: good ? null : fact.reason ?? fact.quality,
                reading: {
                    value: good ? sampleValue(fact.value) : '—',
                    address: address?.confirmed ? `DB${dbNumber} / ${address.offset}${address.bit == null ? '' : '.' + address.bit}` : '—',
                    dataType: fact.definition.dataType,
                    quality: fact.quality,
                    observedAt: fact.observedAt,
                },
            };
        }
    }
    return { ...view, status: 'unavailable' };
});
function closePointDiagnosis() {
    if (pointDiagnosis.value) local?.closeDiagnostic();
}
function startPointDiagnosis(point: Point) {
    if (!local) return;
    const plcName = local.plcs.find(plc => plc.id === point.plcId)?.name ?? point.plcId;
    return local.startDiagnostic('diagnose', point.plcId, `${plcName} · ${point.name || point.sourcePath || point.id}`, point.id);
}

function changePointScope() { if (local) { local.selectedDb = ''; local.pointPage = 1; local.sources = []; local.identification = null; local.mappings = []; local.preview = null; local.offsets = []; } pointEditor.value = null; }
async function editLocalPoint(p: Point) {
    const copy = await local?.preparePointEdit(p.id);
    if (!copy) return;
    // 新保存回执的scope watcher先完成，避免其关闭随后打开的弹窗。
    await nextTick();
    if (!copy.address) copy.address = { offset: 0, bit: copy.dataType === 'BOOL' ? 0 : null, confirmed: false, origin: 'manual', reason: '' };
    pointEditor.value = copy;
}
function manualPointAddress() { if (pointEditor.value?.address) { pointEditor.value.address.origin = 'manual'; pointEditor.value.address.confirmed = false; } }
function cancelLocalPoint() { pointEditor.value = null; local?.finishPointEdit(); }
async function applyLocalPoint() {
    if (await local?.confirmNames()) pointEditor.value = null;
}

watch(() => [local?.view, local?.selectedPlc, local?.selectedDb], cancelLocalPoint, { flush: 'sync' });

watch(pointEditor, v => { if (local) { local.editing = !!v; local.stagePointEdit(v); } }, { deep: true, flush: 'sync' });
onUnmounted(() => {
    closePointDiagnosis();
    cancelLocalPoint();
});
</script>
