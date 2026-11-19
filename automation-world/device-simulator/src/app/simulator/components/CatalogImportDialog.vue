<!-- DS-005：原生选择完整目录，明确模拟监听后只新建草稿。 -->
<template>
  <el-dialog :model-value="modelValue" :title="t('simulator.catalogImport.open')" width="min(1200px, calc(100vw - 32px))" :close-on-click-modal="false" :close-on-press-escape="!busy && !local.busy" :show-close="!busy && !local.busy" @close="close">
    <p>{{ t('simulator.catalogImport.hint') }}</p>
    <ConsoleActionButton label-key="simulator.catalogImport.choose" :disabled="busy || local.busy || !!preview" @click="choose" />
    <template v-if="file">
      <p>{{ t('simulator.catalogImport.file', {name:file.fileName, bytes:file.byteCount, sha:file.fileSha256}) }}</p>
      <p>{{ t('simulator.catalogImport.origin', {kind:file.document.origin.kind, profile:file.document.origin.profile_id, plc:file.document.origin.plc_id}) }}</p>
      <p>{{ t('simulator.catalogImport.version', {producer:file.document.export.producer, state:file.document.export.config_state, id:file.document.export.revision_id, sha:file.document.export.payload_sha256, time:file.document.export.exported_at}) }}</p>
      <p>{{ t('simulator.catalogImport.sourceTarget', {name:file.document.plc.name, host:file.document.plc.connection.host, port:file.document.plc.connection.port, rack:file.document.plc.connection.rack, slot:file.document.plc.connection.slot}) }}</p>
      <p>{{ t('simulator.catalogImport.tsap', {calling:hex(sourceCalling), called:hex(sourceCalled)}) }}</p>
      <div class="ds-catalog-fields">
        <label>{{ t('simulator.catalogImport.listenHost') }} <el-input v-model="host" :disabled="!!preview" data-testid="catalog-import-host" /></label>
        <label>{{ t('simulator.port') }} <el-input-number v-model="port" :min="1" :max="65535" :disabled="!!preview" data-testid="catalog-import-port" /></label>
        <label>{{ t('simulator.rack') }} <el-input-number v-model="rack" :min="0" :max="7" :disabled="!!preview" data-testid="catalog-import-rack" /></label>
        <label>{{ t('simulator.slot') }} <el-input-number v-model="slot" :min="0" :max="31" :disabled="!!preview" data-testid="catalog-import-slot" /></label>
        <el-checkbox v-model="confirmed" :disabled="!!preview">{{ t('simulator.catalogImport.confirmListener') }}</el-checkbox>
      </div>
      <p v-if="preview">{{ t('simulator.catalogImport.listenTsap', {calling:hex(sourceCalling), called:hex(0x100 | ((rack || 0) << 5) | (slot || 0))}) }}</p>
      <ConsoleDataTable table-id="catalog.import.points" :data="rows" row-key="id" max-height="420">
        <el-table-column column-key="db" min-width="200" :label="t('simulator.catalog.db')"><template #default="{row}">{{ row.dbName }} · DB{{ row.dbNumber }} · {{ row.dbSize }} B · {{ row.dbId }} · {{ sourceEnabled(row.dbEnabled) }}</template></el-table-column>
        <el-table-column column-key="id" min-width="280" prop="id" :label="t('simulator.pointId')" />
        <el-table-column column-key="name" min-width="170" prop="name" :label="t('simulator.name')" />
        <el-table-column column-key="type" min-width="110" prop="data_type" :label="t('simulator.catalog.type')" />
        <el-table-column column-key="address" min-width="110" :label="t('simulator.catalog.address')"><template #default="{row}">{{ row.byte_offset }}{{ row.bit === undefined ? '' : '.' + row.bit }}</template></el-table-column>
        <el-table-column column-key="enabled" min-width="110" :label="t('simulator.enabled')"><template #default="{row}">{{ sourceEnabled(row.source_enabled) }}</template></el-table-column>
        <el-table-column column-key="zh" min-width="150" :label="t('simulator.catalog.zh')"><template #default="{row}">{{ row.display_names?.['zh-CN'] || '—' }}</template></el-table-column>
        <el-table-column column-key="en" min-width="150" :label="t('simulator.catalog.en')"><template #default="{row}">{{ row.display_names?.['en-US'] || '—' }}</template></el-table-column>
        <el-table-column column-key="legacy" min-width="150" prop="display_name" :label="t('simulator.catalog.legacy')" />
        <el-table-column column-key="description" min-width="150" prop="description" :label="t('simulator.catalog.description')" />
        <el-table-column column-key="path" min-width="150" prop="source_path" :label="t('simulator.catalog.path')" />
      </ConsoleDataTable>
    </template>
    <el-alert v-if="error" :title="issueText(error)" type="error" :closable="false" />
    <el-alert v-if="local.uncertainSave" :title="t('simulator.catalogImport.unknown')" type="warning" :closable="false" />
    <template #footer>
      <ConsoleActionButton label-key="simulator.cancel" :disabled="busy || local.busy" @click="close" />
      <ConsoleActionButton v-if="preview" label-key="simulator.catalog.change" :disabled="busy || local.busy || !!local.uncertainSave" @click="preview=null" />
      <ConsoleActionButton v-if="file && !preview" label-key="simulator.catalog.preview" :disabled="busy || local.busy || local.dirty || !confirmed || port === undefined || rack === undefined || slot === undefined" @click="prepare" />
      <ConsoleActionButton v-if="preview" label-key="simulator.catalogImport.create" tone="primary" :disabled="busy || local.busy || local.dirty" @click="commit" />
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { computed, inject, onBeforeUnmount, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import ConsoleActionButton from '../../../components/console/ConsoleActionButton.vue';
import ConsoleDataTable from '../../../components/console/ConsoleDataTable.vue';
import { simulatorKey } from '../../../console/composables/useDeviceSimulator';
import * as ipc from '../../../services/deviceSimulator';
const props = defineProps<{modelValue:boolean}>();
const emit = defineEmits<{(e:'update:modelValue', value:boolean):void}>();
const local = inject(simulatorKey)!, {t, te} = useI18n();
const file = ref<ipc.ImportCatalogFile | null>(null), preview = ref<ipc.Preview | null>(null), busy = ref(false), error = ref<string | null>(null);
const host = ref(''), port = ref<number>(), rack = ref<number>(), slot = ref<number>(), confirmed = ref(false);
const sourceCalling = computed(() => file.value?.document.plc.connection.local_tsap ?? 0x100);
const sourceCalled = computed(() => { const c = file.value?.document.plc.connection; return c?.remote_tsap ?? (0x100 + (c?.rack ?? 0) * 32 + (c?.slot ?? 0)); });
const rows = computed(() => file.value?.document.dbs.flatMap(db => db.points.map(point => ({...point, dbId:db.id, dbName:db.name, dbNumber:db.number, dbSize:db.size_bytes, dbEnabled:db.source_enabled}))) ?? []);
const hex = (n:number) => `0x${n.toString(16).padStart(4, '0').toUpperCase()}`;
const sourceEnabled = (v:boolean | undefined) => v === undefined ? t('simulator.catalogImport.notProvided') : t(v ? 'simulator.catalog.enabled' : 'simulator.catalog.disabled');
const issueText = (code:string) => te('simulator.catalogImport.errors.' + code) ? t('simulator.catalogImport.errors.' + code) : t('simulator.catalog.error', {code});
async function release() { const old = file.value; file.value = null; preview.value = null; if (old) { try { await ipc.cancelCatalogImport(old.fileToken); } catch { /* ticket expires; no configuration mutation */ } } }
function close() { if (busy.value || local.busy) return; void release(); emit('update:modelValue', false); }
onBeforeUnmount(() => { void release(); });
watch(() => props.modelValue, open => { if (open) { host.value=''; port.value=undefined; rack.value=undefined; slot.value=undefined; confirmed.value=false; error.value=null; } else void release(); });
async function choose() {
    if (busy.value) return; busy.value=true; error.value=null;
    try { await release(); const result = await ipc.chooseCatalogImport(); if (result !== 'cancelled') file.value=result; }
    catch (e) { error.value=e instanceof ipc.IpcFailure ? e.code : 'operation_failed'; }
    finally { busy.value=false; }
}
async function prepare() {
    if (!file.value || !local.configuration || local.dirty || port.value === undefined || rack.value === undefined || slot.value === undefined) return;
    busy.value=true; error.value=null;
    try { preview.value=await ipc.previewCatalogImport({fileToken:file.value.fileToken, expectedEtag:local.configuration.etag, host:host.value, port:port.value, rack:rack.value, slot:slot.value, connectionConfirmed:confirmed.value}); }
    catch (e) { error.value=e instanceof ipc.IpcFailure ? e.code : 'operation_failed'; }
    finally { busy.value=false; }
}
async function commit() {
    if (!file.value || !preview.value || busy.value) return;
    busy.value=true; error.value=null;
    try { if (await local.commitCatalogImport(file.value.fileToken, preview.value)) { file.value=null; preview.value=null; emit('update:modelValue', false); } else error.value=local.error; }
    finally { busy.value=false; }
}
</script>
