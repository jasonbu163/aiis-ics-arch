<!-- 多DB完整配置/导入/地址/命名；10/20/50分页与跨页选择只影响明确点ID。 -->
<template>
  <section class="console-stack" data-testid="page-points">
    <ConfigRevisionBar />
    <el-alert v-if="local.saveOutcome && (local.previewUnknowns?.length || local.previewReleases?.length)" :title="t('simulator.closeRecovery.'+local.saveOutcome)" type="info" :closable="false" />
    <el-alert v-if="local.saveFailure && local.previewUnknowns?.length" :title="t('simulator.closeRecovery.rejected', {code:local.saveFailure})" type="error" :closable="false" />
    <ConsoleCard v-if="local.previewUnknowns?.length" title-key="simulator.previewRecovery.title">
      <el-alert :title="t('simulator.previewRecovery.hint')" type="warning" :closable="false" />
      <ul data-testid="preview-unknown-list"><li v-for="item in local.previewUnknowns" :key="item.id">{{ item.kind || '—' }} · {{ item.code }}</li></ul>
    </ConsoleCard>
    <ConsoleCard v-if="local.uncertainControls?.length" title-key="simulator.controlRecovery.title">
      <el-alert :title="t('simulator.controlRecovery.hint')" type="warning" :closable="false" />
      <ul data-testid="control-unknown-list">
        <li v-for="item in local.uncertainControls" :key="item.id">
          {{ t('simulator.'+item.command) }} · {{ item.instanceId }} · {{ item.code }} · {{ t('simulator.epoch') }}: {{ item.epoch }} · {{ t('simulator.controlRecovery.requestedRevision') }}: {{ item.loadedRevision ?? '—' }}
        </li>
      </ul>
      <div class="ds-actions">
        <ConsoleActionButton label-key="simulator.controlRecovery.inspect" data-testid="control-unknown-inspect" :disabled="local.busy || local.checkingControls" :loading="local.checkingControls" @click="local.reviewUncertainControls()" />
        <ConsoleActionButton v-if="local.controlReview" label-key="simulator.controlRecovery.accept" data-testid="control-unknown-accept" :disabled="local.busy || local.checkingControls" @click="local.acceptReviewedControls()" />
      </div>
      <el-alert v-if="local.controlReviewError" :title="t('simulator.controlRecovery.'+local.controlReviewError)" type="warning" :closable="false" />
      <template v-if="local.controlReview">
        <p>{{ t('simulator.controlRecovery.currentOnly') }}</p>
        <ul data-testid="control-unknown-current">
          <li v-for="fact in local.controlReview.facts" :key="fact.instanceId">
            {{ fact.name }} · {{ fact.instanceId }} · {{ t('simulator.states.'+fact.state) }} · {{ t('simulator.epoch') }}: {{ fact.epoch }} · {{ t('simulator.controlRecovery.loadedRevision') }}: {{ fact.loadedRevision ?? '—' }}
          </li>
        </ul>
      </template>
    </ConsoleCard>
    <ConsoleCard v-if="local.uncertainSave" title-key="simulator.saveRecovery.title">
      <el-alert :title="t(local.uncertainSave.reason === 'known_readback' ? 'simulator.saveRecovery.knownReadback' : local.uncertainSave.reason === 'known_cleanup' ? 'simulator.saveRecovery.knownCleanup' : 'simulator.saveRecovery.hint')" type="warning" :closable="false" />
      <div class="ds-actions">
        <ConsoleActionButton label-key="simulator.saveRecovery.inspect" data-testid="save-unknown-inspect" :disabled="local.busy || local.checkingSave" :loading="local.checkingSave" @click="local.reviewUncertainSave()" />
        <ConsoleActionButton v-if="local.saveReview?.matchesSubmitted && local.saveCanResolve" label-key="simulator.saveRecovery.accept" data-testid="save-unknown-accept" :disabled="local.busy || local.checkingSave || local.editing" @click="local.acceptReviewedSave()" />
      </div>
      <el-alert v-if="!local.saveCanResolve" :title="t(local.uncertainSave.cleanupUnproven ? 'simulator.saveRecovery.cleanupPending' : 'simulator.saveRecovery.unsettled')" type="warning" :closable="false" />
      <el-alert v-if="local.saveReviewError" :title="t('simulator.saveRecovery.'+local.saveReviewError)" type="warning" :closable="false" />
      <template v-if="local.saveReview">
        <p>{{ t(!local.saveCanResolve ? 'simulator.saveRecovery.inspectOnly' : local.saveReview.matchesSubmitted ? (local.uncertainSave.reason === 'known_readback' ? 'simulator.saveRecovery.knownMatches' : 'simulator.saveRecovery.matches') : 'simulator.saveRecovery.differs') }}</p>
        <p>{{ t('simulator.saveRecovery.submittedEtag') }}: {{ local.uncertainSave.expectedEtag }}</p>
        <p>{{ t('simulator.saveRecovery.savedEtag') }}: {{ local.saveReview.configuration.etag }}</p>
        <p>{{ t('simulator.saveRecovery.savedRevision') }}: {{ local.saveReview.configuration.latestRevision ?? '—' }}</p>
        <p>{{ t('simulator.saveRecovery.selectedRevision') }}: {{ reviewedSelection ?? '—' }}</p>
        <p>{{ t('simulator.saveRecovery.confirmPoints') }}: {{ local.uncertainSave.confirmPoints.join(', ') || '—' }}</p>
        <p>{{ t('simulator.saveRecovery.instanceConfirmation') }}: {{ reviewedInstance?.namesConfirmation ?? '—' }}</p>
        <p>{{ t('simulator.saveRecovery.dbConfirmation') }}: {{ JSON.stringify(reviewedDb?.addressConfirmation ?? null) }}</p>
        <p>{{ t('simulator.saveRecovery.savedPoints') }}</p>
        <ul v-if="reviewedDb" data-testid="save-unknown-saved-points">
          <li v-for="point in reviewedRows" :key="point.id">
            <strong>{{ point.name || point.sourcePath }} · {{ point.id }}</strong>
            <div>{{ t('simulator.displayNameZh') }}: <span class="ds-saved-value">{{ point.displayNames?.['zh-CN'] ?? '' }}</span></div>
            <div>{{ t('simulator.displayNameEn') }}: <span class="ds-saved-value">{{ point.displayNames?.['en-US'] ?? '' }}</span></div>
            <div>{{ t('simulator.pointDescription') }}: <span class="ds-saved-value">{{ point.description ?? '' }}</span></div>
            <div>{{ t('simulator.saveRecovery.pointConfirmation') }}: {{ JSON.stringify(point.confirmations) }}</div>
          </li>
        </ul>
        <p v-else>{{ t('simulator.saveRecovery.noSavedDb') }}</p>
        <ConsoleActionButton label-key="simulator.saveRecovery.compare" data-testid="save-unknown-compare" @click="showDifferences" />
        <template v-if="diffOpen">
          <p>{{ t('simulator.saveRecovery.differenceHint') }}</p>
          <p v-if="!differences.length">{{ t('simulator.saveRecovery.noDifferences') }}</p>
          <ul data-testid="save-unknown-differences"><li v-for="item in differencePage" :key="item.path">
            <strong>{{ item.path }}</strong> · {{ t('simulator.saveRecovery.localValue') }}: <span class="ds-saved-value">{{ item.local }}</span> · {{ t('simulator.saveRecovery.persisted') }}: <span class="ds-saved-value">{{ item.persisted }}</span>
          </li></ul>
          <el-pagination v-if="differences.length > 50" :current-page="differencePageNumber" :page-size="50" :total="differences.length" layout="prev, pager, next" @current-change="differencePageNumber=$event" />
        </template>
      </template>
    </ConsoleCard>
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
          <ConsoleDataTable table-id="configuration.points" :data="rows" row-key="id" data-testid="points-table">
            <el-table-column column-key="selection" width="48" :resizable="false" :show-overflow-tooltip="false" fixed="left">
              <template #header>
                <el-checkbox data-testid="point-select-page" :model-value="rows.length>0&&rows.every(p=>selected.has(p.id))" @change="selectPage" />
              </template>
              <template #default="{row}">
                <el-checkbox :model-value="selected.has(row.id)" :data-testid="'point-select-'+row.id" @change="toggle(row.id)" />
              </template>
            </el-table-column>
            <el-table-column column-key="name" min-width="200" prop="name" :label="t('simulator.name')" />
            <el-table-column column-key="displayName" min-width="200" :label="t('simulator.currentDisplayName')">
              <template #default="{row}">{{ row.displayNames?.[locale === 'zh-CN' ? 'zh-CN' : 'en-US'] ?? '' }}</template>
            </el-table-column>
            <el-table-column column-key="sourcePath" min-width="240" prop="sourcePath" :label="t('simulator.sourcePath')" />
            <el-table-column column-key="dataType" min-width="110" prop="dataType" :label="t('simulator.dataType')" />
            <el-table-column column-key="address" min-width="110" :label="t('simulator.address')">
              <template #default="{row}">{{ row.byte??'—' }}{{ row.bit===null?'':'.'+row.bit }}</template>
            </el-table-column>
            <el-table-column column-key="confirmation" min-width="120" :label="t('simulator.confirmation')">
              <template #default="{row}">{{ t(row.confirmations.initial&&row.confirmations.policy?'simulator.confirmed':'simulator.pending') }}</template>
            </el-table-column>
            <el-table-column column-key="actions" width="200" :resizable="false" :show-overflow-tooltip="false" fixed="right" :label="t('simulator.action')">
              <template #default="{row}">
                <div class="ds-actions">
                <ConsoleActionButton label-key="simulator.edit" size="small" data-testid="point-edit" @click="edit(row)" />
                <ConsoleActionButton label-key="simulator.remove" size="small" tone="danger" :disabled="!db.manual" @click="deleting=row" />
                </div>
              </template>
            </el-table-column>
          </ConsoleDataTable>
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
import ConsoleDataTable from '../../../../components/console/ConsoleDataTable.vue';
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
const local = inject(simulatorKey)!, { t, locale } = useI18n(), db = computed(() => local.selectedDb), page = ref(1), pageSize = ref(10), selected = ref(new Set<string>()), editorOpen = ref(false), editor = ref<ipc.Point | null>(null), deleting = ref<ipc.Point | null>(null), candidate = ref<ipc.Preview | null>(null), layoutOpen = ref(false), reason = ref(''), manualOpen = ref(false), deleteDbOpen = ref(false);
const rows = computed(() => db.value?.points.slice((page.value - 1) * pageSize.value, page.value * pageSize.value) || []);
const reviewedDb = computed(() => local.saveReview?.configuration.workspace.instances.find(i => i.id === local.instanceId)?.dbs.find(d => d.id === local.dbId));
const reviewedInstance = computed(() => local.saveReview?.configuration.workspace.instances.find(i => i.id === local.instanceId));
const reviewedRows = computed(() => reviewedDb.value?.points.slice((page.value - 1) * pageSize.value, page.value * pageSize.value) || []);
const reviewedSelection = computed(() => local.saveReview?.configuration.selections.find(s => s.instanceId === local.instanceId)?.revisionId);
const diffOpen = ref(false), differencePageNumber = ref(1);
type Difference = {path: string; local: string; persisted: string};
function collectDifferences(a: unknown, b: unknown, path: string, out: Difference[]) {
    if (a === b) return;
    if (Array.isArray(a) && Array.isArray(b)) { for (let i = 0; i < Math.max(a.length, b.length); i++) collectDifferences(a[i], b[i], `${path}[${i}]`, out); return; }
    if (a && b && typeof a === 'object' && typeof b === 'object' && !Array.isArray(a) && !Array.isArray(b)) {
        const left = a as Record<string, unknown>, right = b as Record<string, unknown>;
        for (const key of new Set([...Object.keys(left), ...Object.keys(right)])) collectDifferences(left[key], right[key], path ? `${path}.${key}` : key, out);
        return;
    }
    out.push({path, local: JSON.stringify(a) ?? '—', persisted: JSON.stringify(b) ?? '—'});
}
const differences = computed(() => { const result: Difference[] = []; if (diffOpen.value && local.saveReview) collectDifferences(local.draft, local.saveReview.configuration.workspace, '', result); return result; });
const differencePage = computed(() => differences.value.slice((differencePageNumber.value - 1) * 50, differencePageNumber.value * 50));
function showDifferences() { diffOpen.value = true; differencePageNumber.value = 1; local.noteSaveDifferences(); }
watch(() => local.saveReview?.configuration.etag, () => { diffOpen.value = false; });
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
