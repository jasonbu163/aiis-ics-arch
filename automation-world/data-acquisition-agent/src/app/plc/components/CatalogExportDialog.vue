<!-- 按已保存版本预览并导出完整 PLC；目录仅由原生选择器授予。 -->
<template>
  <Teleport to="#daa-feedback">
    <ElDialog :model-value="true" :title="t('plc.catalogExport.title')" :append-to-body="false" :close-on-click-modal="false" :close-on-press-escape="!working" :show-close="!working" width="min(1000px, calc(100vw - 32px))" class="daa-import-dialog" @update:model-value="$event || close()">
      <template #header>
        <div class="daa-export-header">
          <span class="el-dialog__title">{{ t('plc.catalogExport.title') }}</span>
          <ElAlert v-if="results" :title="t('plc.catalogExport.summary.' + summaryKind)" :type="summaryKind === 'success' ? 'success' : summaryKind === 'failed' ? 'error' : 'warning'" :closable="false" show-icon>
            <p>{{ t('plc.catalogExport.summaryCounts', counts) }}</p>
            <p v-for="row in results.rows" :key="row.plcId">{{ row.name }} · {{ row.filename }} · {{ t('plc.catalogExport.result.' + row.result) }}<template v-if="row.errorCode"> · {{ local.label(row.errorCode) }}</template><template v-for="(problem, i) in row.issues ?? []" :key="i"> · {{ local.label(problem.code) }} {{ problem.dbId ?? '' }} {{ problem.pointId ?? '' }}</template><template v-if="row.fileSha256"> · SHA-256 {{ row.fileSha256 }}</template><template v-if="row.cleanupPending"> · {{ t('plc.catalogExport.cleanupPending', { name: row.cleanupPending }) }}</template></p>
            <p v-if="unknown">{{ t('plc.catalogExport.unknown') }}</p>
          </ElAlert>
        </div>
      </template>
      <div class="console-stack">
        <p class="daa-capability-note">{{ t('plc.catalogExport.savedOnly') }}</p>
        <ElAlert v-if="error" :title="local.label(error)" type="error" :closable="false" show-icon />
        <ElAlert v-if="unknown" :title="t('plc.catalogExport.unknown')" type="warning" :closable="false" show-icon />
        <ElRadioGroup v-model="state" :disabled="working || !!results" @change="load">
          <ElRadio value="saved_draft">{{ t('plc.catalogExport.savedDraft') }}</ElRadio>
          <ElRadio value="active_revision">{{ t('plc.catalogExport.activeRevision') }}</ElRadio>
        </ElRadioGroup>
        <template v-if="snapshot">
          <p>{{ t('plc.catalogExport.version') }}: <code>{{ snapshot.revision }}</code> · SHA-256 <code>{{ snapshot.payloadSha256 }}</code></p>
          <p class="daa-capability-note">{{ t('plc.catalogExport.versionFacts', { active: snapshot.active ?? '—', loaded: snapshot.loaded ?? '—', used: snapshot.used ?? '—' }) }}</p>
          <ElCheckboxGroup v-model="selected" :disabled="working || !!results" @change="clearPreview"><div v-for="plc in snapshot.plcs" :key="plc.id"><ElCheckbox :value="plc.id">{{ plc.name }} · {{ plc.host }}:{{ plc.port }} · {{ plc.rack }}/{{ plc.slot }} · {{ plc.dbCount }} DB / {{ plc.pointCount }} {{ t('plc.catalogExport.points') }}</ElCheckbox></div></ElCheckboxGroup>
          <div v-for="plc in snapshot.plcs.filter(p => selected.includes(p.id))" :key="plc.id" class="daa-export-filename">
            <label>{{ plc.name }} · {{ t('plc.catalogExport.filename') }} <ElInput v-model="filenames[plc.id]" :disabled="working || !!results" @input="clearPreview" /></label>
            <p v-for="(problem, i) in filenameErrors.filter(e => e.plcId === plc.id)" :key="i" class="daa-export-error">{{ local.label(problem.code) }}</p>
          </div>
          <ConsoleActionButton label-key="plc.catalogExport.preview" :disabled="working || !selected.length || !!results" @click="preview" />
        </template>
        <template v-if="prepared">
          <details v-for="row in prepared.rows" :key="row.plcId" class="daa-details" open>
            <summary>{{ row.name }} · {{ row.filename }} · {{ row.document?.plc.connection.host }}:{{ row.document?.plc.connection.port }}</summary>
            <p v-for="(problem, i) in row.issues" :key="i">{{ local.label(problem.code) }} · {{ problem.dbId ?? '' }} {{ problem.pointId ?? '' }}</p>
            <template v-if="row.document"><p>{{ t('plc.catalog.origin') }}: {{ row.document.origin.kind }} · {{ row.document.origin.profile_id }} · {{ row.document.origin.plc_id }}</p><details v-for="db in row.document.dbs" :key="db.id" class="daa-details"><summary>{{ db.name }} · DB{{ db.number }} · {{ db.size_bytes }} B</summary><p v-for="point in db.points" :key="point.id">{{ point.name }} · {{ point.data_type }} · {{ point.byte_offset }}<template v-if="point.bit !== undefined">.{{ point.bit }}</template> · {{ local.label(String(point.source_enabled)) }}<br />{{ t('plc.catalog.sourcePath') }}: {{ point.source_path ?? t('plc.catalog.notProvided') }} · {{ t('plc.naming.displayNameZh') }}: {{ point.display_names?.['zh-CN'] ?? '' }} · {{ t('plc.naming.displayNameEn') }}: {{ point.display_names?.['en-US'] ?? '' }}<br />{{ t('plc.catalog.legacy') }}: {{ point.display_name ?? t('plc.catalog.notProvided') }} · {{ t('plc.catalog.description') }}: {{ point.description ?? '' }}</p></details></template>
          </details>
          <ElCheckbox v-model="targetsConfirmed" :disabled="working || !!results">{{ t('plc.catalogExport.confirmTargets') }}</ElCheckbox>
          <div class="console-action-group"><ConsoleActionButton label-key="plc.catalogExport.chooseDirectory" :disabled="working || !!results" @click="chooseDirectory" /><span v-if="directory">{{ t('plc.catalogExport.directoryReady') }}</span></div>
          <p v-for="row in directory?.rows ?? []" :key="row.plcId">{{ row.name }} · {{ row.filename }} · {{ t(row.conflict ? 'plc.catalogExport.exists' : row.valid ? 'plc.catalogExport.ready' : 'plc.catalogExport.invalid') }}</p>
        </template>
      </div>
      <template #footer><div class="console-action-group"><ConsoleActionButton label-key="plc.diagnosis.close" :disabled="working" @click="close" /><ConsoleActionButton label-key="plc.catalogExport.write" tone="primary" :disabled="working || unknown || !!results || !prepared || !directory || !targetsConfirmed" @click="commit" /></div></template>
    </ElDialog>
  </Teleport>
</template>
<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { ElAlert, ElCheckbox, ElCheckboxGroup, ElDialog, ElInput, ElRadio, ElRadioGroup } from 'element-plus';
import { useI18n } from 'vue-i18n';
import { localCall, LocalCommandError, type Catalog } from '../../../services/localAcquisition';
import type { LocalConsole } from '../../../console/composables/useLocalAcquisitionConsole';
import ConsoleActionButton from '../../../components/console/ConsoleActionButton.vue';
const props = defineProps<{ local: LocalConsole }>();
const emit = defineEmits<{ close: [] }>();
const { t } = useI18n();
type State = 'saved_draft' | 'active_revision';
interface Snapshot { revision: string; payloadSha256: string; active: string | null; loaded: string | null; used: string | null; plcs: Array<{id:string;name:string;host:string;port:number;rack:number;slot:number;dbCount:number;pointCount:number}> }
interface Preview { token: string; rows: Array<{plcId:string;name:string;filename:string;document:Catalog | null;issues:Array<{code:string;dbId:string|null;pointId:string|null}>}> }
interface FilenameError { plcId:string; code:string }
interface Directory { rows: Array<{plcId:string;name:string;filename:string;conflict:boolean;valid:boolean}> }
interface Results { rows: Array<{plcId:string;name:string;filename:string;result:'written'|'failed'|'unknown';errorCode:string|null;fileSha256:string|null;cleanupPending:string|null;issues?:Array<{code:string;dbId:string|null;pointId:string|null}>}> }
const state = ref<State>('saved_draft'), snapshot = ref<Snapshot | null>(null), selected = ref<string[]>([]), prepared = ref<Preview | null>(null), directory = ref<Directory | null>(null), results = ref<Results | null>(null);
const working = ref(false), error = ref(''), unknown = ref(false), targetsConfirmed = ref(false);
const filenames = ref<Record<string,string>>({}), filenameErrors = ref<FilenameError[]>([]);
const counts = computed(() => ({ written:results.value?.rows.filter(r => r.result === 'written').length ?? 0, failed:results.value?.rows.filter(r => r.result === 'failed').length ?? 0, unknown:results.value?.rows.filter(r => r.result === 'unknown').length ?? 0 }));
const summaryKind = computed(() => counts.value.unknown ? 'unknown' : counts.value.failed ? (counts.value.written ? 'partial' : 'failed') : 'success');
async function run(fn: () => Promise<void>) { if (working.value) return; working.value = true; error.value = ''; try { await fn(); } catch (e) { error.value = e instanceof Error ? e.message : String(e); } finally { working.value = false; } }
function clearPreview() { const token = prepared.value?.token; prepared.value = null; directory.value = null; targetsConfirmed.value = false; filenameErrors.value = []; if (token) void localCall('daa_catalog_export_cancel', { token }).catch(() => undefined); }
async function load() { clearPreview(); selected.value = []; snapshot.value = null; await run(async () => { snapshot.value = await localCall<Snapshot>('daa_catalog_export_inspect', { state: state.value }); filenames.value = Object.fromEntries(snapshot.value.plcs.map(p => [p.id, /\.json$/i.test(p.name) ? p.name : p.name + '.json'])); }); }
async function preview() { clearPreview(); await run(async () => { const response = await localCall<Preview | {filenameErrors:FilenameError[]}>('daa_catalog_export_preview', { state: state.value, plcIds: selected.value, filenames: Object.fromEntries(selected.value.map(id => [id, filenames.value[id] ?? ''])) }); if ('filenameErrors' in response) filenameErrors.value = response.filenameErrors; else prepared.value = response; }); }
async function chooseDirectory() { const token = prepared.value?.token; if (!token) return; directory.value = null; await run(async () => { const result = await localCall<Directory | {result:'cancelled'}>('daa_catalog_export_directory', { token }); if ('rows' in result) directory.value = result; else clearPreview(); }); }
async function commit() {
    const token = prepared.value?.token; if (!token || !targetsConfirmed.value || !directory.value || unknown.value || results.value || working.value) return;
    const targets = directory.value.rows.map(({plcId, name, filename}) => ({plcId, name, filename}));
    const unconfirmed = (target:typeof targets[number]) => ({...target, result:'unknown' as const, errorCode:null, fileSha256:null, cleanupPending:null});
    await run(async () => {
        try {
            const response = await localCall<Results>('daa_catalog_export_commit', { token, confirmTargets: true });
            const receipts = Array.isArray(response?.rows) ? response.rows : [];
            results.value = { rows: targets.map(target => {
                const matches = receipts.filter(row => row.plcId === target.plcId);
                const row = matches[0];
                return matches.length === 1 && row.filename === target.filename && ['written','failed','unknown'].includes(row.result)
                    ? {...row, ...target} : unconfirmed(target);
            }) };
            unknown.value = results.value.rows.some(row => row.result === 'unknown');
        } catch (e) {
            const uncertain = !(e instanceof LocalCommandError) || !!e.commitUnknown || e.message === 'local_operation_failed';
            unknown.value = uncertain;
            results.value = { rows: targets.map(target => uncertain ? unconfirmed(target) : {...target, result:'failed', errorCode:e instanceof Error ? e.message : 'operation_failed', fileSha256:null, cleanupPending:null}) };
            throw e;
        }
    });
}
function close() { if (working.value) return; clearPreview(); emit('close'); }
onMounted(load);
onUnmounted(clearPreview);
</script>
