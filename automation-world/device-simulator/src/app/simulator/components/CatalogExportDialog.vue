<!-- 保存版本逐 PLC 导出：单独命名、原生选目录、逐文件回执。 -->
<template>
  <el-dialog :model-value="modelValue" :title="t('simulator.catalog.title')" class="ds-catalog-export-dialog" width="min(1200px, calc(100vw - 32px))" :close-on-click-modal="false" :close-on-press-escape="!busy" :show-close="!busy" @close="close">
    <template #header="{ titleId, titleClass }">
      <span :id="titleId" :class="titleClass">{{ t('simulator.catalog.title') }}</span>
      <el-alert v-if="summary" class="ds-catalog-summary" :type="summary.tone" :title="t('simulator.catalog.summary.' + summary.key)" :closable="false" show-icon>
        {{ t('simulator.catalog.summary.counts', summary.counts) }}
        <p v-if="summary.counts.unknown">{{ t('simulator.catalog.unknown') }}</p>
      </el-alert>
    </template>
    <p v-if="!results">{{ t('simulator.catalog.readOnly') }}</p>
    <div v-if="!results" class="ds-selection-toolbar">
      <el-select v-model="revisionId" :disabled="busy || !!preview" :placeholder="t('simulator.catalog.selectRevision')" data-testid="catalog-revision">
        <el-option v-for="r in revisions" :key="r.revisionId" :value="r.revisionId" :label="`v${r.savedSeq} · ${r.revisionId} · ${formatShanghaiTime(r.createdUtc) || '—'}`" />
      </el-select>
      <ConsoleActionButton size="small" label-key="simulator.catalog.previous" :disabled="busy || !!preview || offset === 0" @click="emit('page', Math.max(0, offset - 100))" />
      <ConsoleActionButton size="small" label-key="simulator.catalog.next" :disabled="busy || !!preview || offset + 100 >= total" @click="emit('page', offset + 100)" />
    </div>
    <p v-if="source && !results">{{ t('simulator.catalog.source', { revision: source.revision.revisionId, sha: source.revision.sha256 }) }}</p>
    <div v-if="source && !preview && !results" class="ds-catalog-instances">
      <section v-for="i in source.instances" :key="i.instanceId" class="ds-catalog-instance">
        <el-checkbox v-model="selected" :value="i.instanceId" :disabled="busy">{{ i.name }} · {{ i.instanceId }}</el-checkbox>
        <p>{{ t('simulator.catalog.counts', { dbs: i.dbCount, points: i.pointCount }) }} · {{ t('simulator.catalog.selectedVersion') }}: {{ i.selectedRevision || '—' }} · {{ t('simulator.catalog.loadedVersion') }}: {{ i.loadedRevision || '—' }}</p>
        <label v-if="selected.includes(i.instanceId)" class="ds-catalog-filename">
          {{ t('simulator.catalog.filename') }}
          <el-input :model-value="filenames[i.instanceId]" :disabled="busy" :aria-invalid="!!filenameErrors[i.instanceId]" :aria-describedby="filenameErrors[i.instanceId] ? 'catalog-filename-' + i.instanceId : undefined" @update:model-value="rename(i.instanceId, $event)" />
          <span v-if="filenameErrors[i.instanceId]" :id="'catalog-filename-' + i.instanceId" class="ds-catalog-error">{{ issueText(filenameErrors[i.instanceId]) }}</span>
        </label>
        <div v-if="selected.includes(i.instanceId)" class="ds-catalog-fields">
          <label>{{ t('simulator.catalog.clientHost') }} <el-input v-model="targets[i.instanceId].host" :disabled="busy" /></label>
          <label>{{ t('simulator.port') }} <el-input-number v-model="targets[i.instanceId].port" :disabled="busy" :min="1" :max="65535" /></label>
          <label>{{ t('simulator.rack') }} <el-input-number v-model="targets[i.instanceId].rack" :disabled="busy" :min="0" :max="7" /></label>
          <label>{{ t('simulator.slot') }} <el-input-number v-model="targets[i.instanceId].slot" :disabled="busy" :min="0" :max="31" /></label>
          <span>{{ t('simulator.catalog.tsap', { local: hex(i.localTsap), remote: hex(i.remoteTsap) }) }}</span>
          <el-checkbox v-model="targets[i.instanceId].connectionConfirmed" :disabled="busy">{{ t('simulator.catalog.confirmConnection') }}</el-checkbox>
          <el-checkbox v-if="i.loadedRevision !== revisionId" v-model="targets[i.instanceId].loadedDifferenceConfirmed" :disabled="busy">{{ t('simulator.catalog.confirmDifference') }}</el-checkbox>
        </div>
      </section>
    </div>
    <template v-if="preview">
      <section v-for="row in preview.rows" :key="row.instanceId" class="ds-catalog-instance">
        <h3>{{ row.name }} · {{ row.filename }}</h3>
        <p>{{ row.instanceId }}</p>
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
      <p v-for="row in directory?.rows ?? []" :key="row.instanceId">{{ row.name }} · {{ row.filename }} · {{ row.conflict ? t('simulator.catalog.exists') : row.valid ? t('simulator.catalog.ready') : t('simulator.catalog.invalid') }}</p>
    </template>
    <template v-if="results">
      <section v-for="row in results.rows" :key="row.instanceId" class="ds-catalog-instance ds-catalog-receipt">
        <strong>{{ row.name }} · {{ row.filename }} · {{ t('simulator.catalog.result.' + row.result) }}</strong>
        <p v-if="row.errorCode">{{ issueText(row.errorCode) }}</p>
        <p v-for="(issue, index) in row.issues" :key="index">{{ issueText(issue.code) }} · {{ issue.dbId || '—' }} · {{ issue.pointId || '—' }}</p>
        <p v-if="row.fileSha256">SHA-256 <code>{{ row.fileSha256 }}</code></p>
        <p v-if="row.cleanupPending">{{ t('simulator.catalog.cleanupPending', {name: row.cleanupPending}) }}</p>
      </section>
      <el-checkbox v-if="summary?.counts.unknown" v-model="unknownChecked">{{ t('simulator.catalog.checkedUnknown') }}</el-checkbox>
    </template>
    <el-alert v-if="error" :closable="false" type="error" :title="issueText(error)" />
    <template #footer>
      <ConsoleActionButton label-key="simulator.cancel" :disabled="busy" @click="close" />
      <ConsoleActionButton v-if="preview || results" label-key="simulator.catalog.change" :disabled="busy || (!!summary?.counts.unknown && !unknownChecked)" @click="change" />
      <ConsoleActionButton v-if="source && !preview && !results" label-key="simulator.catalog.preview" :disabled="busy || !selected.length || !!Object.keys(filenameErrors).length" @click="prepare" />
      <ConsoleActionButton v-if="preview && !results" label-key="simulator.catalog.chooseDirectory" :disabled="busy" @click="choose" />
      <ConsoleActionButton v-if="preview && !results" label-key="simulator.catalog.export" :disabled="busy || !directory || !directory.rows.some(r => r.valid && !r.conflict)" @click="commit" />
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { computed, ref, watch, onBeforeUnmount } from 'vue';
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
const filenames = ref<Record<string, string>>({}), serverNameErrors = ref<Record<string, string>>({});
const preview = ref<ipc.CatalogPreview | null>(null), directory = ref<ipc.CatalogDirectory | null>(null), results = ref<ipc.CatalogResult | null>(null);
const error = ref<string | null>(null), unknownChecked = ref(false), busy = ref(false);
let generation = 0;
let previewGeneration = 0;
const hex = (value:number) => `0x${value.toString(16).padStart(4, '0').toUpperCase()}`;
const enabled = (value:boolean) => t(value ? 'simulator.catalog.enabled' : 'simulator.catalog.disabled');
const issueText = (code:string) => te('simulator.catalog.errors.' + code) ? t('simulator.catalog.errors.' + code) : t('simulator.catalog.error', {code});
const pointRows = (row:ipc.CatalogRow) => row.dbs.flatMap(db => db.points.map(point => ({...point, dbName:db.name, dbNumber:db.number, dbLength:db.length, dbEnabled:db.enabled})));
const defaultFilename = (name: string) => name.toLowerCase().endsWith('.json') ? name : name + '.json';
const selectedFilenames = computed(() => Object.fromEntries(selected.value.map(id => [id, filenames.value[id] ?? ''])));
function filenameError(filename: string) {
    if (new TextEncoder().encode(filename).length > 255) return 'catalog_filename_length';
    if (/[\u0000-\u001f\u007f/\\<>:"|?*]/.test(filename)) return 'catalog_filename_characters';
    if (!filename.trim()) return 'catalog_filename_required';
    if (!/\.json$/i.test(filename)) return 'catalog_filename_extension';
    const stem = filename.slice(0, -5);
    if (!stem.trim()) return 'catalog_filename_required';
    if (/[ .]$/.test(stem)) return 'catalog_filename_ending';
    if (/^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)/i.test(stem)
        || filename.startsWith('__daa_yaml_migration_v1__')
        || filename.startsWith('__daa_startup_settings_v1__')) return 'catalog_filename_reserved';
}
const filenameErrors = computed(() => {
    const entries = Object.entries(selectedFilenames.value);
    const names = entries.map(([, name]) => name.toLowerCase());
    const issues = entries.flatMap(([id, name], index) => {
        const issue = filenameError(name) ?? (names.indexOf(names[index]) !== names.lastIndexOf(names[index]) ? 'catalog_filename_duplicate' : undefined);
        return issue ? [[id, issue]] : [];
    });
    return {...Object.fromEntries(issues), ...serverNameErrors.value} as Record<string, string>;
});
const summary = computed(() => {
    if (!results.value) return null;
    const counts = {written:0, failed:0, unknown:0};
    for (const row of results.value.rows) counts[row.result]++;
    const key = counts.unknown ? 'unknown' : !counts.failed ? 'success' : counts.written ? 'partial' : 'failed';
    return {counts, key, tone:key === 'success' ? 'success' : key === 'failed' ? 'error' : 'warning'} as const;
});
function reset() {
    source.value = null; selected.value = []; targets.value = {}; filenames.value = {}; serverNameErrors.value = {};
    directory.value = null; results.value = null; error.value = null; unknownChecked.value = false;
}
async function cancelTicket(token: string) { try { await ipc.catalogCancel(token); } catch { /* bounded server ticket expires */ } }
async function release() {
    previewGeneration++;
    const old = preview.value; preview.value = null; directory.value = null;
    if (old) await cancelTicket(old.token);
}
function rename(id: string, name: string) {
    if (busy.value || results.value) return;
    filenames.value[id] = name; serverNameErrors.value = {}; void release();
}
function close() { if (busy.value) return; generation++; void release(); emit('update:modelValue', false); }
function change() {
    if (busy.value || (summary.value?.counts.unknown && !unknownChecked.value)) return;
    void release(); results.value = null; error.value = null; unknownChecked.value = false;
}
onBeforeUnmount(() => { generation++; void release(); });
watch(() => props.modelValue, visible => { if (visible) { reset(); busy.value = false; revisionId.value = ''; } else { generation++; void release(); } });
watch(selected, () => { serverNameErrors.value = {}; void release(); }, {deep: true, flush: 'sync'});
watch(revisionId, async id => {
    const current = ++generation; void release(); reset(); if (!id || !props.modelValue) return;
    busy.value = true;
    try {
        const value = await ipc.catalogRevision(id); if (generation !== current) return;
        source.value = value; targets.value = Object.fromEntries(value.instances.map(i => [i.instanceId, {instanceId:i.instanceId, host:i.host, port:i.port, rack:i.rack, slot:i.slot, connectionConfirmed:false, loadedDifferenceConfirmed:false}]));
        filenames.value = Object.fromEntries(value.instances.map(i => [i.instanceId, defaultFilename(i.name)]));
    } catch (e) { if (generation === current) error.value = e instanceof ipc.IpcFailure ? e.code : 'operation_failed'; }
    finally { if (generation === current) busy.value = false; }
});
async function prepare() {
    if (!source.value || busy.value || results.value || preview.value || !selected.value.length || Object.keys(filenameErrors.value).length) return;
    busy.value = true; error.value = null;
    const current = previewGeneration;
    try {
        const response = await ipc.catalogPreview(revisionId.value, selected.value.map(id => ({...targets.value[id]})), selectedFilenames.value);
        if ('filenameErrors' in response) {
            if (previewGeneration === current) serverNameErrors.value = Object.fromEntries(response.filenameErrors.map(row => [row.instanceId, row.code]));
        } else if (previewGeneration === current) {
            preview.value = response;
        } else {
            await cancelTicket(response.token);
        }
    }
    catch (e) { error.value = e instanceof ipc.IpcFailure ? e.code : 'operation_failed'; }
    finally { busy.value = false; }
}
async function choose() {
    if (!preview.value || busy.value) return; busy.value = true; error.value = null; directory.value = null;
    const token = preview.value.token;
    try {
        const result = await ipc.catalogChooseDirectory(token);
        if (preview.value?.token !== token) return;
        if (result === 'cancelled') await release();
        else directory.value = result;
    }
    catch (e) { error.value = e instanceof ipc.IpcFailure ? e.code : 'operation_failed'; }
    finally { busy.value = false; }
}
async function commit() {
    if (!preview.value || busy.value || !directory.value?.rows.some(row => row.valid && !row.conflict)) return;
    busy.value = true; error.value = null;
    const token = preview.value.token;
    const expected = directory.value.rows;
    const missing = (row: ipc.CatalogFile, result: 'unknown' | 'failed', errorCode: string): ipc.CatalogResultRow => ({
        instanceId:row.instanceId, name:row.name, filename:row.filename, result, errorCode, fileSha256:null, cleanupPending:null,
    });
    try {
        const receipt = await ipc.catalogCommit(token);
        const receipts = Array.isArray(receipt?.rows) ? receipt.rows : [];
        results.value = {rows:expected.map(row => {
            const matches = receipts.filter(item => item?.instanceId === row.instanceId);
            const item = matches[0];
            if (matches.length === 1 && item.filename === row.filename
                && ['written', 'failed', 'unknown'].includes(item.result)) {
                return {...item, name:row.name};
            }
            return missing(row, 'unknown', 'catalog_write_result_unknown');
        })};
    } catch (e) {
        const known = e instanceof ipc.IpcFailure && !e.unknown;
        results.value = {rows:expected.map(row => missing(row, known ? 'failed' : 'unknown', known ? e.code : 'catalog_write_result_unknown'))};
    } finally {
        preview.value = null; directory.value = null; busy.value = false;
    }
}
</script>
