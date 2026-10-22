<!-- 多文件导入沿DAA预览/显式选择范式；文件原字节与声明/UDT闭包均送真实DS服务。 -->
<template>
  <ConsoleCard title-key="simulator.importSources">
    <div class="console-stack" data-testid="source-import">
      <el-alert :title="t('simulator.tiaInitializersIgnored')" type="warning" :closable="false" />
      <input type="file" accept=".db,.udt" multiple data-testid="source-files" :disabled="local.busy||local.dirty||!local.selected" @change="filesChanged" />
      <p>{{ t('simulator.sourceBounds') }}</p>
      <div v-for="file in files" :key="file.inputId" class="ds-inline" data-testid="source-file-row" :data-input-id="file.inputId">
        <span data-testid="source-file-label">{{ fileLabel(file) }}</span>
        <el-select v-model="file.lineageId" :placeholder="t('simulator.sourceLineage')" clearable>
          <el-option :value="''" :label="t('simulator.newSource')" />
          <el-option v-for="source in lineages" :key="source.lineageId" :value="source.lineageId" :label="source.logicalName+' · '+source.lineageId.slice(0,8)" />
        </el-select>
      </div>
      <ConsoleActionButton label-key="simulator.scan" data-testid="source-scan" :disabled="local.dirty||!files.length||local.busy" @click="scan" />
      <el-table v-if="declarations.length" :data="dbDeclarations">
        <el-table-column :label="t('simulator.select')">
          <template #default="{row}">
            <el-checkbox v-model="row.selected" :data-testid="'import-select-'+row.name" />
          </template>
        </el-table-column>
        <el-table-column :label="t('simulator.declaration')">
          <template #default="{row}">{{ declarationLabel(row) }}</template>
        </el-table-column>
        <el-table-column :label="t('simulator.targetDb')">
          <template #default="{row}">
            <el-select v-model="row.dbId" clearable @change="chooseDb(row)">
              <el-option :value="''" :label="t('simulator.newDb')" />
              <el-option v-for="db in local.selected?.dbs" :key="db.id" :value="db.id" :label="db.name" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column :label="t('simulator.dbNumber')">
          <template #default="{row}">
            <el-input-number v-model="row.number" :min="1" :max="65535" data-testid="import-db-number" />
          </template>
        </el-table-column>
        <el-table-column :label="t('simulator.udtClosure')">
          <template #default="{row}">
            <el-select v-model="row.closure" multiple :data-testid="'import-closure-'+row.name">
              <el-option v-for="udt in udtDeclarations" :key="key(udt)" :value="key(udt)" :label="declarationLabel(udt)" />
            </el-select>
          </template>
        </el-table-column>
      </el-table>
      <ConsoleActionButton v-if="declarations.length" label-key="simulator.previewImport" data-testid="source-preview" :disabled="local.busy||!dbDeclarations.some(d=>d.selected)" @click="preview" />
      <el-dialog :model-value="!!candidate" :title="t('simulator.importPreview')" :append-to-body="false" width="min(1000px, calc(100vw - 32px))" @close="candidate=null">
        <div v-if="candidate" class="console-stack">
          <el-alert :title="t('simulator.tiaInitializersIgnored')" type="warning" :closable="false" />
          <div v-for="db in candidate.workspace.instances.find(i=>i.id===local.instanceId)?.dbs" :key="db.id">
            <strong>{{ db.name }} · DB{{ db.number }}</strong>
            <el-tree v-if="db.binding" :data="tree(db.binding)" :props="{label:'name',children:'children'}" />
          </div>
          <el-table :data="changes" max-height="260">
            <el-table-column prop="path" :label="t('simulator.sourcePath')" />
            <el-table-column :label="t('simulator.action')">
              <template #default="{row}">{{ t('simulator.changes.'+row.result) }}</template>
            </el-table-column>
            <el-table-column :label="t('simulator.dbNumber')">
              <template #default="{row}">{{ row.dbNumberBefore??'—' }} → {{ row.dbNumberAfter??'—' }}</template>
            </el-table-column>
            <el-table-column :label="t('simulator.dataType')">
              <template #default="{row}">{{ row.typeBefore??'—' }} → {{ row.typeAfter??'—' }}</template>
            </el-table-column>
            <el-table-column :label="t('simulator.address')">
              <template #default="{row}">{{ row.byteBefore??'—' }}.{{ row.bitBefore??'—' }} → {{ row.byteAfter??'—' }}.{{ row.bitAfter??'—' }}</template>
            </el-table-column>
          </el-table>
        </div>
        <template #footer>
          <ConsoleActionButton label-key="simulator.cancel" data-testid="import-cancel" @click="candidate=null" />
          <ConsoleActionButton label-key="simulator.confirmImport" data-testid="import-confirm" tone="primary" :loading="local.busy" :disabled="local.busy" @click="confirm" />
        </template>
      </el-dialog>
    </div>
  </ConsoleCard>
</template>
<script setup lang="ts">
import { computed, inject, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import * as ipc from '../../../services/deviceSimulator';
import { simulatorKey } from '../../../console/composables/useDeviceSimulator';
import ConsoleCard from '../../../components/console/ConsoleCard.vue';
import ConsoleActionButton from '../../../components/console/ConsoleActionButton.vue';
const local = inject(simulatorKey)!, { t } = useI18n();
interface FileInput {
    inputId: string;
    name: string;
    bytes: number[];
    lineageId: string;
}
interface Declaration {
    inputId: string;
    declarationIndex: number;
    name: string;
    db: boolean;
    selected: boolean;
    dbId: string;
    number: number;
    closure: string[];
}
const files = ref<FileInput[]>([]), declarations = ref<Declaration[]>([]), candidate = ref<ipc.Preview | null>(null);
const dbDeclarations = computed(() => declarations.value.filter(d => d.db)), udtDeclarations = computed(() => declarations.value.filter(d => !d.db)), changes = computed(() => Array.isArray(candidate.value?.details.changes) ? candidate.value!.details.changes as Record<string, ipc.Json>[] : []);
const lineages = computed(() => Array.from(new Map((local.draft?.sourceVersions || []).map(s => [s.lineageId, s])).values()));
function fileLabel(file: FileInput) {
    return file.name + ' · [' + (files.value.findIndex(f => f.inputId === file.inputId) + 1) + ':' + file.inputId.slice(0, 8) + ']';
}
function declarationLabel(d: Declaration) {
    const file = files.value.find(f => f.inputId === d.inputId);
    return d.name + ' · ' + (file ? fileLabel(file) : d.inputId) + ' · #' + (d.declarationIndex + 1);
}
function chooseDb(row: Declaration) { const db = local.selected?.dbs.find(d => d.id === row.dbId); if (db)
    row.number = db.number; }
function key(d: {
    inputId: string;
    declarationIndex: number;
}) { return d.inputId + ':' + d.declarationIndex; }
function tree(binding: ipc.Json) { return binding && typeof binding === 'object' && !Array.isArray(binding) && Array.isArray(binding.tree) ? binding.tree : []; }
async function filesChanged(event: Event) { const chosen = Array.from((event.target as HTMLInputElement).files || []); if (chosen.length > 128 || chosen.some(f => f.size > 1048576) || chosen.reduce((n, f) => n + f.size, 0) > 4194304) {
    local.error = 'source_limits';
    return;
} files.value = await Promise.all(chosen.map(async (f) => ({ inputId: crypto.randomUUID(), name: f.name, bytes: Array.from(new Uint8Array(await f.arrayBuffer())), lineageId: '' }))); declarations.value = []; candidate.value = null; }
function intent(bindings: unknown[]) { return { expectedEtag: local.configuration!.etag, instanceId: local.instanceId, files: files.value.map(f => ({ ...f, lineageId: f.lineageId || null })), bindings }; }
async function scan() { const result = await local.action(() => ipc.previewImport(intent([]))); if (result)
    declarations.value = result.declarations.map(d => ({ ...d, selected: false, dbId: '', number: 1, closure: [] })); }
async function preview() { const bindings = dbDeclarations.value.filter(d => d.selected).map(d => ({ dbId: d.dbId || null, number: d.number, declaration: { inputId: d.inputId, declarationIndex: d.declarationIndex }, udtClosure: d.closure.map(id => { const u = udtDeclarations.value.find(u => key(u) === id)!; return { inputId: u.inputId, declarationIndex: u.declarationIndex }; }) })); const result = await local.action(() => ipc.previewImport(intent(bindings))); if (result?.preview)
    candidate.value = result.preview; }
async function confirm() { if (!candidate.value)
    return; const result = await local.action(() => ipc.confirmPreview('import', candidate.value!), true); if (result !== undefined) {
    candidate.value = null;
    files.value = [];
    declarations.value = [];
} }
</script>
