<!--
  File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/components/TargetApiConfigurationPanel.vue
  Description: Backend-owned multi-method Target API table, material loader, and editor.
  Main Features:
    - Loads every persisted API Material through a multi-select Dialog without overwriting existing targets
    - Maintains manual location-aware current-backend definitions and compatible batch exchange
    - Supports all-or-partial selection before confirmed Target API deletion in an application dialog
    - Does not render OpenAPI candidates or execute a target request
-->
<script setup lang="ts">
import { computed, ref, watch } from "vue";

import type { LocaleMessages } from "../../../locales";
import { saveCollectionFactFile } from "../api";
import { apiMaterialNormalizationReasonKey, type ApiMaterialConfiguration, type ConfigurationImportPreview, type TargetApiConfiguration, type TargetApiDraft, type TargetApiMaterialLoadResult, type TargetApiParameter } from "../types";
import {
  createMappingConfigurationTemplateFile,
  createTargetApiExportFile,
  parseMappingConfigurationFile,
  type MappingConfigurationFileFormat,
} from "../utils/mappingConfigurationFiles";
import MappingBatchOperationsDialog from "./MappingBatchOperationsDialog.vue";

const props = defineProps<{
  labels: LocaleMessages;
  configurations: TargetApiConfiguration[];
  draft: TargetApiDraft;
  selectedId: string | null;
  apiMaterials: ApiMaterialConfiguration[];
  selectedMaterialKeys: string[];
  loadedMaterialKeys: Set<string>;
  materialLoadResult: TargetApiMaterialLoadResult | null;
  busy: boolean;
  status: "idle" | "saved" | "deleted";
  error: string;
  importPreview: ConfigurationImportPreview | null;
  enabled: boolean;
}>();

const emit = defineEmits<{
  load: [];
  "load-api-materials": [];
  "toggle-material": [materialKey: string, selected: boolean];
  "import-materials": [];
  "start-manual": [];
  open: [targetApiId: string];
  "update-draft": [patch: Partial<TargetApiDraft>];
  "update-parameter": [index: number, patch: Partial<TargetApiParameter>];
  "add-parameter": [];
  "remove-parameter": [index: number];
  save: [];
  remove: [targetApiId: string];
  "remove-many": [targetApiIds: string[]];
  "preview-import": [items: unknown[]];
  "apply-import": [];
  "clear-import": [];
}>();

const editorOpen = ref(false);
const batchOpen = ref(false);
const materialDialogOpen = ref(false);
const selectedTargetApiIds = ref<string[]>([]);
const pendingDeleteIds = ref<string[]>([]);
const savingFile = ref(false);
const fileError = ref("");
const displayedError = computed(() => {
  if (!props.error) return "";
  if (props.error.includes("tss_target_api_in_use")) return props.labels.targetApiInUse;
  return props.labels.targetApiOperationFailed;
});

watch(() => props.status, (status) => {
  if (status === "saved") editorOpen.value = false;
});
watch(() => props.materialLoadResult, (result) => {
  if (result) materialDialogOpen.value = false;
});
watch(() => props.configurations, (configurations) => {
  const available = new Set(configurations.map((configuration) => configuration.id));
  selectedTargetApiIds.value = selectedTargetApiIds.value.filter((targetApiId) => available.has(targetApiId));
});

const allTargetApisSelected = computed(() => (
  props.configurations.length > 0
  && props.configurations.every((configuration) => selectedTargetApiIds.value.includes(configuration.id))
));
const targetApiSelectionIndeterminate = computed(() => (
  selectedTargetApiIds.value.length > 0 && !allTargetApisSelected.value
));
const pendingSingleDelete = computed(() => pendingDeleteIds.value.length === 1
  ? props.configurations.find((configuration) => configuration.id === pendingDeleteIds.value[0]) ?? null
  : null);

function sourceLabel(origin: TargetApiConfiguration["originType"]) {
  return origin === "api_material" ? props.labels.targetApiSourceApiMaterial : props.labels.targetApiSourceManual;
}

function normalizationReason(errorCode: string | null) {
  return props.labels[apiMaterialNormalizationReasonKey(errorCode)];
}

function startManual() {
  emit("start-manual");
  editorOpen.value = true;
}

function openEditor(targetApiId: string) {
  emit("open", targetApiId);
  editorOpen.value = true;
}

function closeBatch() {
  fileError.value = "";
  emit("clear-import");
  batchOpen.value = false;
}

function textPatch(field: "apiKey" | "name" | "path" | "operationId", event: Event) {
  emit("update-draft", { [field]: (event.target as HTMLInputElement).value });
}

function parameterPatch(index: number, field: "location" | "name" | "jsonPath" | "dataType" | "required", event: Event) {
  const target = event.target as HTMLInputElement | HTMLSelectElement;
  emit("update-parameter", index, {
    [field]: field === "required" ? (target as HTMLInputElement).checked : target.value,
  } as Partial<TargetApiParameter>);
}

function openMaterialDialog() {
  materialDialogOpen.value = true;
  emit("load-api-materials");
}

function materialParameterSummary(material: ApiMaterialConfiguration) {
  if (!material.requestContract) return "—";
  const counts = ["body", "query", "path", "header"].map(
    (location) => material.requestContract?.filter((item) => item.location === location).length ?? 0,
  );
  return `B ${counts[0]} · Q ${counts[1]} · P ${counts[2]} · H ${counts[3]}`;
}

async function saveFile(file: ReturnType<typeof createTargetApiExportFile>) {
  savingFile.value = true;
  fileError.value = "";
  try {
    await saveCollectionFactFile(file);
  } catch (error) {
    fileError.value = String(error);
  } finally {
    savingFile.value = false;
  }
}

function downloadTemplate(format: MappingConfigurationFileFormat) {
  void saveFile(createMappingConfigurationTemplateFile("targetApis", format));
}

function exportConfigurations(format: MappingConfigurationFileFormat) {
  void saveFile(createTargetApiExportFile(format, props.configurations));
}

async function importFile(file: File) {
  try {
    fileError.value = "";
    emit("preview-import", await parseMappingConfigurationFile("targetApis", file));
  } catch (error) {
    fileError.value = String(error);
  }
}

function requestDelete(configuration: TargetApiConfiguration) {
  pendingDeleteIds.value = [configuration.id];
}

function toggleTargetApi(targetApiId: string, selected: boolean) {
  const selectedIds = new Set(selectedTargetApiIds.value);
  if (selected) selectedIds.add(targetApiId);
  else selectedIds.delete(targetApiId);
  selectedTargetApiIds.value = [...selectedIds];
}

function toggleAllTargetApis(selected: boolean) {
  selectedTargetApiIds.value = selected ? props.configurations.map((configuration) => configuration.id) : [];
}

function requestSelectedDelete() {
  if (!selectedTargetApiIds.value.length) return;
  pendingDeleteIds.value = [...selectedTargetApiIds.value];
}

function confirmDelete() {
  if (!pendingDeleteIds.value.length) return;
  const targetApiIds = [...pendingDeleteIds.value];
  pendingDeleteIds.value = [];
  if (targetApiIds.length === 1) emit("remove", targetApiIds[0]);
  else emit("remove-many", targetApiIds);
}
</script>

<template>
  <p>{{ labels.targetApiPartIdentityHint }}</p>
  <div class="mapping-page-stack target-api-configuration-stack">
    <section class="panel target-api-configuration-panel">
      <header class="panel-header"><div><p class="panel-kicker">{{ labels.mappingBackendConfiguration }}</p><h2>{{ labels.targetApiConfigurationTitle }}</h2></div><span class="status-pill">HTTP</span></header>
      <p>{{ labels.targetApiConfigurationHint }}</p>
      <div class="action-row target-api-actions">
        <button class="secondary-action" type="button" :disabled="!enabled || busy" @click="openMaterialDialog">{{ labels.targetApiLoadMaterials }}</button>
        <button class="secondary-action" type="button" :disabled="!enabled || busy" @click="batchOpen = true">{{ labels.mappingBatchOperations }}</button>
        <button class="primary-action" type="button" :disabled="!enabled || busy" @click="startManual">{{ labels.targetApiNewManual }}</button>
      </div>
      <p v-if="displayedError" class="warning">{{ displayedError }}</p>
      <p v-if="status === 'saved'" class="notice">{{ labels.targetApiSaved }}</p>
      <p v-if="materialLoadResult" class="notice">{{ labels.targetApiMaterialLoadResult.replace('{created}', String(materialLoadResult.created.length)).replace('{skipped}', String(materialLoadResult.skipped.length)).replace('{requiresConfiguration}', String(materialLoadResult.requiresConfiguration.length)) }}</p>
    </section>

    <section class="panel target-api-configuration-panel">
      <header class="panel-header"><div><p class="panel-kicker">{{ labels.mappingValueRuleSavedState }}</p><h2>{{ labels.targetApiConfigured }}</h2></div><button class="danger-action" type="button" :disabled="!enabled || busy || !selectedTargetApiIds.length" @click="requestSelectedDelete">{{ labels.targetApiRemoveSelected.replace('{count}', String(selectedTargetApiIds.length)) }}</button></header>
      <div class="table-scroll mapping-list-scroll target-api-table-scroll" tabindex="0"><table class="mapping-list-table target-api-list-table"><thead><tr><th><input :aria-label="labels.targetApiSelectAll" :checked="allTargetApisSelected" :disabled="!enabled || busy || !configurations.length" :indeterminate="targetApiSelectionIndeterminate" type="checkbox" @change="toggleAllTargetApis(($event.target as HTMLInputElement).checked)" /></th><th>{{ labels.targetApiKey }}</th><th>{{ labels.targetApiName }}</th><th>{{ labels.targetApiMethod }}</th><th>{{ labels.targetApiPath }}</th><th>{{ labels.targetApiSchemaSource }}</th><th>{{ labels.targetApiParameters }}</th><th>{{ labels.targetApiDuplicateRequest }}</th><th>{{ labels.targetApiState }}</th><th>{{ labels.targetApiActions }}</th></tr></thead>
        <tbody><tr v-for="configuration in configurations" :key="configuration.id"><td><input type="checkbox" :checked="selectedTargetApiIds.includes(configuration.id)" :disabled="!enabled || busy" @change="toggleTargetApi(configuration.id, ($event.target as HTMLInputElement).checked)" /></td><td><code>{{ configuration.apiKey }}</code></td><td>{{ configuration.name }}</td><td><span class="status-pill">{{ configuration.httpMethod }}</span></td><td><code>{{ configuration.path }}</code></td><td>{{ sourceLabel(configuration.originType) }}</td><td>{{ configuration.parameterSchema.length }}</td><td>{{ configuration.idempotencySupported ? labels.yes : labels.no }}</td><td>{{ configuration.enabled ? labels.targetApiEnabled : labels.targetApiDisabled }}</td><td><div class="mapping-list-row-actions"><button class="secondary-action" type="button" :disabled="!enabled || busy" @click="openEditor(configuration.id)">{{ labels.targetApiEdit }}</button><button class="danger-action" type="button" :disabled="!enabled || busy" @click="requestDelete(configuration)">{{ labels.targetApiDelete }}</button></div></td></tr></tbody>
      </table></div>
      <p v-if="!configurations.length" class="empty-state">{{ labels.targetApiEmpty }}</p>
    </section>

    <div v-if="pendingDeleteIds.length" class="facts-dialog-backdrop" @click.self="pendingDeleteIds = []">
      <section class="panel facts-dialog target-api-delete-dialog" role="alertdialog" aria-modal="true" aria-labelledby="target-api-delete-confirm-title">
        <header class="panel-header facts-dialog-header"><div><p class="panel-kicker">HTTP</p><h2 id="target-api-delete-confirm-title">{{ pendingSingleDelete ? labels.targetApiDeleteConfirmTitle : labels.targetApiRemoveSelectedConfirmTitle }}</h2></div></header>
        <p>{{ pendingSingleDelete ? labels.targetApiDeleteConfirm.replace('{name}', pendingSingleDelete.name) : labels.targetApiRemoveSelectedConfirm.replace('{count}', String(pendingDeleteIds.length)) }}</p>
        <div class="action-row facts-editor-actions"><button class="secondary-action" type="button" :disabled="busy" @click="pendingDeleteIds = []">{{ labels.collectionFactsCancel }}</button><button class="danger-action" type="button" :disabled="!enabled || busy" @click="confirmDelete">{{ labels.targetApiDelete }}</button></div>
      </section>
    </div>

    <div v-if="editorOpen" class="facts-dialog-backdrop" @click.self="editorOpen = false">
      <section class="panel facts-dialog target-api-dialog" role="dialog" aria-modal="true">
        <header class="panel-header facts-dialog-header"><div><p class="panel-kicker">HTTP</p><h2>{{ selectedId ? labels.targetApiEditTitle : labels.targetApiNewTitle }}</h2></div></header>
        <form class="target-api-form" @submit.prevent="emit('save')">
          <div class="form-grid">
            <label class="field"><span>{{ labels.targetApiKey }}</span><input :value="draft.apiKey" :readonly="Boolean(selectedId)" :disabled="!enabled || busy" @input="textPatch('apiKey', $event)" /></label>
            <label class="field"><span>{{ labels.targetApiName }}</span><input :value="draft.name" :disabled="!enabled || busy" @input="textPatch('name', $event)" /></label>
            <label class="field"><span>{{ labels.targetApiMethod }}</span><select :value="draft.httpMethod" :disabled="!enabled || busy" @change="emit('update-draft', { httpMethod: ($event.target as HTMLSelectElement).value as TargetApiDraft['httpMethod'] })"><option v-for="method in ['GET','POST','PUT','PATCH','DELETE','HEAD','OPTIONS','TRACE']" :key="method" :value="method">{{ method }}</option></select></label>
            <label class="field"><span>{{ labels.targetApiOrigin }}</span><input :value="selectedId ? sourceLabel(configurations.find((item) => item.id === selectedId)?.originType ?? 'manual') : labels.targetApiSourceManual" readonly /></label>
            <label class="field"><span>{{ labels.targetApiPath }}</span><input :value="draft.path" :disabled="!enabled || busy" @input="textPatch('path', $event)" /></label>
            <label class="field"><span>{{ labels.targetApiOperationId }}</span><input :value="draft.operationId" :disabled="!enabled || busy" @input="textPatch('operationId', $event)" /></label>
            <label class="check-field"><input :checked="draft.enabled" type="checkbox" :disabled="!enabled || busy" @change="emit('update-draft', { enabled: ($event.target as HTMLInputElement).checked })" /><span>{{ labels.targetApiEnabled }}</span></label>
            <label class="check-field"><input :checked="draft.idempotencySupported" type="checkbox" :disabled="!enabled || busy" @change="emit('update-draft', { idempotencySupported: ($event.target as HTMLInputElement).checked })" /><span>{{ labels.targetApiIdempotencySupported }}</span></label>
          </div>
          <p class="hint">{{ labels.targetApiIdempotencyHelp }}</p>
          <label class="field target-api-body-template"><span>{{ labels.targetApiBodyTemplate }}</span><textarea :value="draft.bodyTemplateJson" rows="10" spellcheck="false" :disabled="!enabled || busy" @input="emit('update-draft', { bodyTemplateJson: ($event.target as HTMLTextAreaElement).value })" /></label>
          <div class="target-api-parameters"><div class="target-api-parameters-header"><h3>{{ labels.targetApiParameterSchema }}</h3><button class="secondary-action" type="button" :disabled="!enabled || busy" @click="emit('add-parameter')">{{ labels.targetApiAddParameter }}</button></div>
            <div class="table-scroll target-api-table-scroll" tabindex="0"><table class="target-api-parameter-table"><thead><tr><th>{{ labels.targetApiParameterLocation }}</th><th>{{ labels.targetApiParameterName }}</th><th>{{ labels.targetApiJsonPath }}</th><th>{{ labels.collectionFactsDataType }}</th><th>{{ labels.targetApiRequired }}</th><th>{{ labels.targetApiActions }}</th></tr></thead><tbody><tr v-for="(parameter, index) in draft.parameterSchema" :key="index"><td><select :value="parameter.location" :disabled="!enabled || busy" @change="parameterPatch(index, 'location', $event)"><option v-for="location in ['body','query','path','header']" :key="location" :value="location">{{ location }}</option></select></td><td><input :value="parameter.name" :disabled="!enabled || busy" @input="parameterPatch(index, 'name', $event)" /></td><td><input :value="parameter.jsonPath ?? ''" :disabled="!enabled || busy || parameter.location !== 'body'" @input="parameterPatch(index, 'jsonPath', $event)" /></td><td><select :value="parameter.dataType" :disabled="!enabled || busy" @change="parameterPatch(index, 'dataType', $event)"><option v-for="dataType in ['string', 'integer', 'number', 'boolean', 'datetime']" :key="dataType" :value="dataType">{{ dataType }}</option></select></td><td><input :checked="parameter.required" type="checkbox" :disabled="!enabled || busy || parameter.location === 'path'" @change="parameterPatch(index, 'required', $event)" /></td><td><button class="danger-action" type="button" :disabled="!enabled || busy" @click="emit('remove-parameter', index)">{{ labels.targetApiRemoveParameter }}</button></td></tr></tbody></table></div>
          </div>
          <div class="action-row facts-editor-actions"><button class="secondary-action" type="button" :disabled="busy" @click="editorOpen = false">{{ labels.collectionFactsCancel }}</button><button class="primary-action" type="submit" :disabled="!enabled || busy">{{ labels.targetApiSave }}</button></div>
        </form>
      </section>
    </div>

    <div v-if="materialDialogOpen" class="facts-dialog-backdrop" @click.self="materialDialogOpen = false">
      <section class="panel facts-dialog target-api-material-dialog" role="dialog" aria-modal="true">
        <header class="panel-header facts-dialog-header"><div><p class="panel-kicker">{{ labels.apiMaterialsSourceOpenApi }}</p><h2>{{ labels.targetApiLoadMaterials }}</h2></div></header>
        <p>{{ labels.targetApiMaterialDialogHint }}</p>
        <div class="table-scroll target-api-table-scroll" tabindex="0"><table class="target-api-material-table"><thead><tr><th>{{ labels.apiMaterialsUse }}</th><th>{{ labels.targetApiMethod }}</th><th>{{ labels.targetApiName }}</th><th>{{ labels.targetApiPath }}</th><th>{{ labels.apiMaterialsParameters }}</th><th>{{ labels.apiMaterialsSource }}</th><th>{{ labels.targetApiMaterialLoadState }}</th></tr></thead><tbody>
          <tr v-for="material in apiMaterials" :key="material.materialKey"><td><input type="checkbox" :checked="selectedMaterialKeys.includes(material.materialKey)" :disabled="busy || loadedMaterialKeys.has(material.materialKey)" @change="emit('toggle-material', material.materialKey, ($event.target as HTMLInputElement).checked)" /></td><td><span class="status-pill">{{ material.httpMethod }}</span></td><td>{{ material.name }}</td><td><code>{{ material.path }}</code></td><td>{{ materialParameterSummary(material) }}</td><td>{{ labels.apiMaterialsSourceOpenApi }}</td><td>{{ loadedMaterialKeys.has(material.materialKey) ? labels.targetApiMaterialAlreadyLoaded : material.normalizationStatus === 'ready' ? labels.apiMaterialsReady : labels.targetApiMaterialRequiresConfiguration.replace('{reason}', normalizationReason(material.normalizationErrorCode)) }}</td></tr>
        </tbody></table></div>
        <p v-if="!apiMaterials.length" class="empty-state">{{ labels.targetApiMaterialEmpty }}</p>
        <div class="action-row facts-editor-actions"><button class="secondary-action" type="button" :disabled="busy" @click="materialDialogOpen = false">{{ labels.collectionFactsCancel }}</button><button class="primary-action" type="button" :disabled="!enabled || busy || !selectedMaterialKeys.length" @click="emit('import-materials')">{{ labels.targetApiMaterialLoadAction }}</button></div>
      </section>
    </div>

    <MappingBatchOperationsDialog v-if="batchOpen" :labels="labels" :title="labels.targetApiBatchTitle" :busy="busy" :saving-file="savingFile" :preview="importPreview" :error="fileError || error" :enabled="enabled" @close="closeBatch" @download-template="downloadTemplate" @export="exportConfigurations" @import="importFile" @apply="emit('apply-import')" />
  </div>
</template>

<style scoped>
.target-api-actions, .target-api-parameters { margin-top: 16px; }
.target-api-table-scroll { overflow-x: auto; }
.target-api-list-table { min-width: 1020px; }
.target-api-parameter-table { min-width: 760px; }
.target-api-list-table td, .target-api-parameter-table td { vertical-align: top; white-space: normal; }
.target-api-dialog { max-width: min(1120px, calc(100vw - 32px)); }
.target-api-material-dialog { max-width: min(1200px, calc(100vw - 32px)); }
.target-api-delete-dialog { max-width: min(480px, calc(100vw - 32px)); }
.target-api-material-table { min-width: 1050px; }
.target-api-form { display: grid; gap: 16px; }
.target-api-body-template textarea { width: 100%; font: 12px/1.5 "SFMono-Regular", Consolas, monospace; }
.target-api-parameters-header { display: flex; justify-content: space-between; gap: 12px; margin-bottom: 10px; }
.target-api-parameters-header h3 { margin: 0; font-size: 14px; }
.target-api-parameter-table input, .target-api-parameter-table select { width: 100%; min-width: 130px; }
@media (max-width: 760px) { .target-api-parameters-header { align-items: flex-start; flex-direction: column; } }
</style>
