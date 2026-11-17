<!-- DS-003：只从保存版本预览；目录由原生选择，逐 PLC 报告结果。 -->
<template>
  <el-dialog :model-value="modelValue" :title="t('simulator.catalog.title')" width="min(1200px, calc(100vw - 32px))" :close-on-click-modal="false" :close-on-press-escape="!busy" :show-close="!busy" @close="close">
    <p>{{ t('simulator.catalog.readOnly') }}</p>
    <div class="ds-selection-toolbar">
      <el-select v-model="revisionId" :disabled="busy || !!preview" :placeholder="t('simulator.catalog.selectRevision')" data-testid="catalog-revision">
        <el-option v-for="r in revisions" :key="r.revisionId" :value="r.revisionId" :label="`v${r.savedSeq} · ${r.revisionId} · ${formatShanghaiTime(r.createdUtc) || '—'}`" />
      </el-select>
      <ConsoleActionButton size="small" label-key="simulator.catalog.previous" :disabled="busy || !!preview || offset === 0" @click="emit('page', Math.max(0, offset - 100))" />
      <ConsoleActionButton size="small" label-key="simulator.catalog.next" :disabled="busy || !!preview || offset + 100 >= total" @click="emit('page', offset + 100)" />
    </div>
    <p v-if="source">{{ t('simulator.catalog.source', { revision: source.revision.revisionId, sha: source.revision.sha256 }) }}</p>
    <div v-if="source && !preview && !results" class="ds-catalog-instances">
      <section v-for="i in source.instances" :key="i.instanceId" class="ds-catalog-instance">
        <el-checkbox v-model="selected" :value="i.instanceId">{{ i.name }} · {{ i.instanceId }}</el-checkbox>
        <p>{{ t('simulator.catalog.counts', { dbs: i.dbCount, points: i.pointCount }) }} · {{ t('simulator.catalog.selectedVersion') }}: {{ i.selectedRevision || '—' }} · {{ t('simulator.catalog.loadedVersion') }}: {{ i.loadedRevision || '—' }}</p>
        <div v-if="selected.includes(i.instanceId)" class="ds-catalog-fields">
          <label>{{ t('simulator.catalog.clientHost') }} <el-input v-model="targets[i.instanceId].host" /></label>
          <label>{{ t('simulator.port') }} <el-input-number v-model="targets[i.instanceId].port" :min="1" :max="65535" /></label>
          <label>{{ t('simulator.rack') }} <el-input-number v-model="targets[i.instanceId].rack" :min="0" :max="7" /></label>
          <label>{{ t('simulator.slot') }} <el-input-number v-model="targets[i.instanceId].slot" :min="0" :max="31" /></label>
          <span>{{ t('simulator.catalog.tsap', { local: hex(i.localTsap), remote: hex(i.remoteTsap) }) }}</span>
          <el-checkbox v-model="targets[i.instanceId].connectionConfirmed">{{ t('simulator.catalog.confirmConnection') }}</el-checkbox>
          <el-checkbox v-if="i.loadedRevision !== revisionId" v-model="targets[i.instanceId].loadedDifferenceConfirmed">{{ t('simulator.catalog.confirmDifference') }}</el-checkbox>
        </div>
      </section>
    </div>
    <template v-if="preview">
      <section v-for="row in preview.rows" :key="row.instanceId" class="ds-catalog-instance">
        <h3>{{ row.name }} · {{ row.instanceId }}</h3>
        <p>{{ t('simulator.catalog.counts', { dbs: row.dbCount, points: row.pointCount }) }} · {{ t('simulator.catalog.selectedVersion') }}: {{ row.selectedRevision || '—' }} · {{ t('simulator.catalog.loadedVersion') }}: {{ row.loadedRevision || '—' }}</p>
        <p>{{ t('simulator.catalog.tsap', { local: hex(row.localTsap), remote: hex(row.remoteTsap) }) }}</p>
        <el-alert v-if="row.loopback" :closable="false" type="warning" :title="t('simulator.catalog.loopback')" />
        <el-alert v-if="row.nonDefaultTsap" :closable="false" type="warning" :title="t('simulator.catalog.nonDefaultTsap')" />
        <p v-for="(issue, index) in row.issues" :key="index" class="ds-catalog-error">{{ issueText(issue.code) }} · {{ issue.dbId || '—' }} · {{ issue.pointId || '—' }}</p>
        <p>{{ t('simulator.catalog.fileEvidence', { bytes: row.byteCount ?? '—', sha: row.fileSha256 || '—' }) }}</p>
        <ConsoleDataTable table-id="catalog.export.points" :data="pointRows(row)" row-key="id">
          <el-table-column column-key="db" min-width="200" :label="t('simulator.catalog.db')"><template #default="{row: point}">{{ point.dbName }} ({{ point.dbNumber }}, {{ point.dbLength }} B) · {{ enabled(point.dbEnabled) }}</template></el-table-column>
          <el-table-column column-key="name" min-width="170" prop="name" :label="t('simulator.name')" />
          <el-table-column column-key="type" min-width="110" prop="dataType" :label="t('simulator.catalog.type')" />
          <el-table-column column-key="address" min-width="110" :label="t('simulator.catalog.address')"><template #default="{row: point}">{{ point.byte ?? '—' }}{{ point.bit === null ? '' : '.' + point.bit }}</template></el-table-column>
          <el-table-column column-key="enabled" min-width="110" :label="t('simulator.enabled')"><template #default="{row: point}">{{ enabled(point.enabled) }}</template></el-table-column>
          <el-table-column column-key="zh" min-width="150" :label="t('simulator.catalog.zh')"><template #default="{row: point}">{{ point.displayNames?.['zh-CN'] || '—' }}</template></el-table-column>
          <el-table-column column-key="en" min-width="150" :label="t('simulator.catalog.en')"><template #default="{row: point}">{{ point.displayNames?.['en-US'] || '—' }}</template></el-table-column>
          <el-table-column column-key="legacy" min-width="150" prop="displayName" :label="t('simulator.catalog.legacy')" />
          <el-table-column column-key="description" min-width="150" prop="description" :label="t('simulator.catalog.description')" />
          <el-table-column column-key="source" min-width="150" prop="sourcePath" :label="t('simulator.catalog.path')" />
        </ConsoleDataTable>
      </section>
      <p v-if="directory" v-for="row in directory.rows" :key="row.instanceId">{{ row.filename }} · {{ row.conflict ? t('simulator.catalog.exists') : row.valid ? t('simulator.catalog.ready') : t('simulator.catalog.invalid') }}</p>
    </template>
    <template v-if="results">
      <p v-for="row in results.rows" :key="row.instanceId">{{ row.filename }} · {{ row.result === 'written' ? t('simulator.catalog.written') : issueText(row.errorCode || 'catalog_validation') }} · {{ row.fileSha256 || '—' }}</p>
      <p v-for="row in results.rows.filter(r => r.cleanupPending)" :key="row.instanceId + '-cleanup'">{{ t('simulator.catalog.cleanupPending', {name: row.cleanupPending}) }}</p>
    </template>
    <el-alert v-if="error" :closable="false" type="error" :title="issueText(error)" />
    <el-alert v-if="unknown" :closable="false" type="warning" :title="t('simulator.catalog.unknown')" />
    <el-checkbox v-if="unknown" v-model="unknownChecked">{{ t('simulator.catalog.checkedUnknown') }}</el-checkbox>
    <template #footer>
      <ConsoleActionButton label-key="simulator.cancel" :disabled="busy" @click="close" />
      <ConsoleActionButton v-if="preview && !results" label-key="simulator.catalog.change" :disabled="busy" @click="change" />
      <ConsoleActionButton v-if="source && !preview && !results" label-key="simulator.catalog.preview" :disabled="busy || !selected.length || (unknown && !unknownChecked)" @click="prepare" />
      <ConsoleActionButton v-if="preview && !results" label-key="simulator.catalog.chooseDirectory" :disabled="busy" @click="choose" />
      <ConsoleActionButton v-if="preview && !results" label-key="simulator.catalog.export" :disabled="busy || !directory || !directory.rows.some(r => r.valid && !r.conflict)" @click="commit" />
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, onBeforeUnmount } from 'vue';
import { useI18n } from 'vue-i18n';
import ConsoleActionButton from '../../../components/console/ConsoleActionButton.vue';
import ConsoleDataTable from '../../../components/console/ConsoleDataTable.vue';
import { formatShanghaiTime } from '../../../console/time';
import * as ipc from '../../../services/deviceSimulator';
const props = defineProps<{modelValue: boolean; revisions: ipc.Revision[]; offset: number; total: number}>();
const emit = defineEmits<{(e:'update:modelValue', value:boolean):void; (e:'page', offset:number):void}>();
const {t, te} = useI18n();
const revisionId = ref(''), source = ref<Awaited<ReturnType<typeof ipc.catalogRevision>> | null>(null);
const selected = ref<string[]>([]), targets = ref<Record<string, ipc.CatalogTarget>>({});
const preview = ref<ipc.CatalogPreview | null>(null), directory = ref<ipc.CatalogDirectory | null>(null), results = ref<ipc.CatalogResult | null>(null);
const error = ref<string | null>(null), unknown = ref(false), unknownChecked = ref(false), busy = ref(false);
let generation = 0;
const hex = (value:number) => `0x${value.toString(16).padStart(4, '0').toUpperCase()}`;
const enabled = (value:boolean) => t(value ? 'simulator.catalog.enabled' : 'simulator.catalog.disabled');
const issueText = (code:string) => te('simulator.catalog.errors.' + code) ? t('simulator.catalog.errors.' + code) : t('simulator.catalog.error', {code});
const pointRows = (row:ipc.CatalogRow) => row.dbs.flatMap(db => db.points.map(point => ({...point, dbName:db.name, dbNumber:db.number, dbLength:db.length, dbEnabled:db.enabled})));
function reset() { source.value = null; selected.value = []; targets.value = {}; directory.value = null; results.value = null; error.value = null; }
async function release() { const old = preview.value; preview.value = null; directory.value = null; if (old) { try { await ipc.catalogCancel(old.token); } catch { /* bounded server ticket expires */ } } }
function close() { if (busy.value) return; generation++; void release(); emit('update:modelValue', false); }
function change() { void release(); error.value = null; }
onBeforeUnmount(() => { generation++; void release(); });
watch(() => props.modelValue, visible => { if (visible) { reset(); revisionId.value = ''; } else { generation++; void release(); } });
watch(revisionId, async id => {
    const current = ++generation; reset(); if (!id || !props.modelValue) return;
    busy.value = true;
    try {
        const value = await ipc.catalogRevision(id); if (generation !== current) return;
        source.value = value; targets.value = Object.fromEntries(value.instances.map(i => [i.instanceId, {instanceId:i.instanceId, host:i.host, port:i.port, rack:i.rack, slot:i.slot, connectionConfirmed:false, loadedDifferenceConfirmed:false}]));
    } catch (e) { if (generation === current) error.value = e instanceof ipc.IpcFailure ? e.code : 'operation_failed'; }
    finally { if (generation === current) busy.value = false; }
});
async function prepare() {
    if (!source.value || busy.value || (unknown.value && !unknownChecked.value)) return; busy.value = true; error.value = null;
    unknown.value = false; unknownChecked.value = false;
    try { preview.value = await ipc.catalogPreview(revisionId.value, selected.value.map(id => ({...targets.value[id]}))); }
    catch (e) { error.value = e instanceof ipc.IpcFailure ? e.code : 'operation_failed'; }
    finally { busy.value = false; }
}
async function choose() {
    if (!preview.value || busy.value) return; busy.value = true; error.value = null; directory.value = null;
    try { const result = await ipc.catalogChooseDirectory(preview.value.token); if (result !== 'cancelled') directory.value = result; }
    catch (e) { error.value = e instanceof ipc.IpcFailure ? e.code : 'operation_failed'; }
    finally { busy.value = false; }
}
async function commit() {
    if (!preview.value || busy.value || !directory.value) return; busy.value = true; error.value = null;
    const token = preview.value.token;
    try { results.value = await ipc.catalogCommit(token); unknown.value = results.value.rows.some(row => row.result === 'unknown'); preview.value = null; directory.value = null; }
    catch (e) { const failure = e instanceof ipc.IpcFailure ? e : new ipc.IpcFailure('operation_failed'); error.value = failure.code; unknown.value = failure.unknown; preview.value = null; directory.value = null; }
    finally { busy.value = false; }
}
</script>
