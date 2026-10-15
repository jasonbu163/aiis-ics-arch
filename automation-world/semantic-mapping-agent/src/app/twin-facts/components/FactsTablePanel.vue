<!--
File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/components/FactsTablePanel.vue
Description: Table-first source-fact definitions, values, and file-exchange workspace.
Main Features:
  - Keeps definition Preview and explicit Apply separate from fact-value updates
  - Shows every source as a read-only paged table when the source key is empty
  - Owns Fact Table drafts while delegating each Dialog to a module-private component
  - Guards definition imports against source drift and skips stale fact values safely
  - Separates a loaded source context from definitions that have completed Apply
  - Generates definition templates and current-value exports through the module API facade
  - Preserves contract and import drafts when an API operation fails
  - Keeps value export busy until its parent finishes fetching all saved facts
-->
<script setup lang="ts">
import { computed, ref, watch } from "vue";

import PaginationBar from "../../../components/PaginationBar.vue";
import type { LocaleMessages } from "../../../locales";
import { saveCollectionFactFile } from "../api";
import type {
  BackendCollectionFactListQuery,
  BackendCollectionFactPage,
  BackendCollectionFactRecord,
  CollectionFactContract,
  CollectionFactContractPreview,
  CollectionFactDataType,
  CollectionFactDefinitionFileRow,
  CollectionFactFileFormat,
  CollectionFactKind,
  CollectionFactValueFileRow,
  CollectionFactValueInput,
} from "../types";
import {
  createDefinitionExportFile,
  createDefinitionTemplateFile,
  parseDefinitionFile,
  parseValueFile,
  type CollectionFactGeneratedFile,
} from "../utils/collectionFactFiles";
import FactBatchOperationsDialog from "./FactBatchOperationsDialog.vue";
import FactDefinitionDialog from "./FactDefinitionDialog.vue";
import FactValueDialog from "./FactValueDialog.vue";

const DEFAULT_CONTRACT_VERSION = "collection-facts.v1";
const DATA_TYPES: CollectionFactDataType[] = ["string", "integer", "number", "boolean", "datetime"];
const FACT_KINDS: CollectionFactKind[] = ["current", "incremental"];

const props = defineProps<{
  labels: LocaleMessages;
  sourceKey: string;
  contract: CollectionFactContract | null;
  pendingPreview: CollectionFactContractPreview | null;
  previewNeedsConfirmation: boolean;
  query: BackendCollectionFactListQuery;
  result: BackendCollectionFactPage;
  contractBusy: boolean;
  tableBusy: boolean;
  valuesBusy: boolean;
  status: "idle" | "previewed" | "saved" | "valuesSaved";
  error: string;
  enabled: boolean;
}>();

const emit = defineEmits<{
  "load-source": [sourceKey: string];
  query: [patch: Partial<BackendCollectionFactListQuery>];
  "preview-contract": [contract: CollectionFactContract];
  "apply-contract": [];
  "discard-preview": [];
  "update-values": [values: CollectionFactValueInput[]];
  "export-values": [format: CollectionFactFileFormat, complete: (failed: boolean) => void];
}>();

interface DefinitionDraft {
  originalName: string | null;
  name: string;
  factKind: CollectionFactKind;
  dataType: CollectionFactDataType;
}

interface ValueDraft {
  name: string;
  dataType: CollectionFactDataType;
  value: string;
  isNull: boolean;
}

interface ValueImportResult {
  updated: number;
  skipped: number;
}

const sourceInput = ref(props.sourceKey);
const nameInput = ref(props.query.name || "");

watch(() => props.query.name, (name) => {
  nameInput.value = name || "";
});

const definitionDraft = ref<DefinitionDraft | null>(null);
const definitionError = ref("");
const valueDraft = ref<ValueDraft | null>(null);
const valueError = ref("");
const batchOperationsOpen = ref(false);
const replaceDefinitions = ref(false);
const fileError = ref("");
const applyingConfirmed = ref(false);
const previewError = ref("");
const savingFile = ref(false);
const exportError = ref(false);
const pendingValueImportResult = ref<ValueImportResult | null>(null);
const valueImportResult = ref<ValueImportResult | null>(null);

const displayContractVersion = computed(() => props.contract?.contractVersion ?? DEFAULT_CONTRACT_VERSION);
const isAllSourcesView = computed(() => !props.sourceKey);
const hasLoadedContract = computed(() => Boolean(
  props.contract && props.contract.sourceKey === sourceInput.value.trim(),
));
const hasAppliedDefinitions = computed(() => Boolean(
  hasLoadedContract.value
  && props.contract
  && (Object.keys(props.contract.current).length || Object.keys(props.contract.incremental).length),
));
const operationError = computed(() => props.error ? props.labels.collectionFactsOperationFailed : "");
const valueImportResultText = computed(() => {
  const result = valueImportResult.value;
  if (!result) return "";
  return props.labels.collectionFactsValueImportResult
    .replace("{updated}", String(result.updated))
    .replace("{skipped}", String(result.skipped));
});
const fileErrorText = computed(() => {
  if (!fileError.value) return "";
  if (fileError.value.includes("SOURCE")) return props.labels.collectionFactsFileSourceInvalid;
  if (fileError.value.includes("VERSION")) return props.labels.collectionFactsFileVersionInvalid;
  if (fileError.value.includes("NO_CURRENT_NAMES")) return props.labels.collectionFactsFileNoCurrentNames;
  if (fileError.value.includes("DUPLICATE")) return props.labels.collectionFactsFileNamesInvalid;
  if (fileError.value.includes("TYPE")) return props.labels.collectionFactsValueInvalid;
  return props.labels.collectionFactsFileInvalid;
});

watch(() => props.sourceKey, (sourceKey) => {
  sourceInput.value = sourceKey;
  definitionDraft.value = null;
  valueDraft.value = null;
  definitionError.value = "";
  valueError.value = "";
  batchOperationsOpen.value = false;
  replaceDefinitions.value = false;
  fileError.value = "";
  exportError.value = false;
  pendingValueImportResult.value = null;
  valueImportResult.value = null;
});

watch(() => props.pendingPreview, (preview) => {
  applyingConfirmed.value = false;
  previewError.value = "";
  if (preview) {
    closeDefinitionDialog();
    closeBatchOperations();
  }
});

watch(() => props.valuesBusy, (busy, wasBusy) => {
  if (!busy && wasBusy) {
    if (props.status === "valuesSaved" && !props.error) {
      if (pendingValueImportResult.value) {
        valueImportResult.value = pendingValueImportResult.value;
      }
      pendingValueImportResult.value = null;
      closeValueDialog();
      closeBatchOperations();
    } else {
      pendingValueImportResult.value = null;
    }
  }
});

function loadSource() {
  emit("load-source", sourceInput.value.trim());
}

function textQuery(field: "name", event: Event) {
  emit("query", { [field]: (event.target as HTMLInputElement).value, page: 1 });
}

function selectQuery(field: "factKind" | "dataType", event: Event) {
  const value = (event.target as HTMLSelectElement).value || undefined;
  emit("query", { [field]: value, page: 1 });
}

function startDefinitionCreate() {
  definitionDraft.value = { originalName: null, name: "", factKind: "current", dataType: "string" };
  definitionError.value = "";
}

function closeDefinitionDialog() {
  definitionDraft.value = null;
  definitionError.value = "";
}

function startDefinitionEdit(fact: BackendCollectionFactRecord) {
  definitionDraft.value = {
    originalName: fact.name,
    name: fact.name,
    factKind: fact.factKind,
    dataType: fact.dataType,
  };
  definitionError.value = "";
}

function updateDefinitionDraft(patch: Partial<DefinitionDraft>) {
  if (definitionDraft.value) Object.assign(definitionDraft.value, patch);
}

function previewDefinitionDraft() {
  if (!definitionDraft.value) return;
  try {
    const draft = definitionDraft.value;
    const name = draft.name.trim();
    if (!name) throw new Error("COLLECTION_FACT_DEFINITION_NAME_REQUIRED");
    const next = baseContract(sourceInput.value.trim());
    if (draft.originalName) {
      delete next.current[draft.originalName];
      delete next.incremental[draft.originalName];
    }
    if (next.current[name] || next.incremental[name]) throw new Error("COLLECTION_FACT_DEFINITION_NAME_DUPLICATE");
    next[draft.factKind][name] = draft.dataType;
    definitionError.value = "";
    emit("preview-contract", next);
  } catch (error) {
    definitionError.value = String(error);
  }
}

function previewDefinitionDelete(fact: BackendCollectionFactRecord) {
  const next = baseContract(sourceInput.value.trim());
  delete next.current[fact.name];
  delete next.incremental[fact.name];
  emit("preview-contract", next);
}

function baseContract(sourceKey: string): CollectionFactContract {
  if (!sourceKey) throw new Error("COLLECTION_FACT_SOURCE_REQUIRED");
  const contract = props.contract;
  if (!contract || contract.sourceKey !== sourceKey) throw new Error("COLLECTION_FACT_CONTRACT_REQUIRED");
  return {
    contractVersion: contract.contractVersion,
    sourceKey,
    current: { ...contract.current },
    incremental: { ...contract.incremental },
  };
}

function startValueEdit(fact: BackendCollectionFactRecord) {
  valueImportResult.value = null;
  valueDraft.value = {
    name: fact.name,
    dataType: fact.dataType,
    value: fact.value ?? "",
    isNull: fact.value === null,
  };
  valueError.value = "";
}

function closeValueDialog() {
  valueDraft.value = null;
  valueError.value = "";
}

function updateValueDraft(patch: Partial<ValueDraft>) {
  if (valueDraft.value) Object.assign(valueDraft.value, patch);
}

function openBatchOperations() {
  batchOperationsOpen.value = true;
  replaceDefinitions.value = false;
  fileError.value = "";
  pendingValueImportResult.value = null;
  valueImportResult.value = null;
}

function closeBatchOperations() {
  batchOperationsOpen.value = false;
  replaceDefinitions.value = false;
  fileError.value = "";
  exportError.value = false;
  pendingValueImportResult.value = null;
}

function submitValue() {
  if (!valueDraft.value) return;
  const nextValue = valueDraft.value.isNull ? null : valueDraft.value.value;
  if (!matchesValue(nextValue, valueDraft.value.dataType)) {
    valueError.value = "COLLECTION_FACT_VALUE_TYPE_INVALID";
    return;
  }
  valueError.value = "";
  emit("update-values", [{ name: valueDraft.value.name, value: nextValue }]);
}

function matchesValue(value: string | null, dataType: CollectionFactDataType): boolean {
  if (value === null || dataType === "string") return true;
  if (dataType === "integer") return /^[-+]?\d+$/.test(value.trim());
  if (dataType === "number") return value.trim() !== "" && Number.isFinite(Number(value));
  if (dataType === "boolean") return value === "true" || value === "false";
  return value.trim().length > 0 && !Number.isNaN(Date.parse(value));
}

function applyPreview() {
  if (props.previewNeedsConfirmation && !applyingConfirmed.value) {
    previewError.value = props.labels.collectionFactsPreviewConfirmationRequired;
    return;
  }
  previewError.value = "";
  emit("apply-contract");
}

async function saveGeneratedFile(file: CollectionFactGeneratedFile) {
  if (savingFile.value) return;
  savingFile.value = true;
  exportError.value = false;
  try {
    await saveCollectionFactFile(file);
  } catch {
    exportError.value = true;
  } finally {
    savingFile.value = false;
  }
}

function saveDefinitionTemplate(format: CollectionFactFileFormat) {
  void saveGeneratedFile(createDefinitionTemplateFile(format));
}

function saveDefinitionExport(format: CollectionFactFileFormat) {
  if (props.contract) void saveGeneratedFile(createDefinitionExportFile(format, props.contract));
}

async function importFile(intent: "definitions" | "values", file: File) {
  try {
    if (intent === "definitions") previewImportedDefinitions(await parseDefinitionFile(file));
    else previewImportedValues(await parseValueFile(file));
    fileError.value = "";
  } catch (error) {
    fileError.value = String(error);
  }
}

function previewImportedDefinitions(rows: CollectionFactDefinitionFileRow[]) {
  const contract = props.contract;
  if (!contract) throw new Error("COLLECTION_FACT_CONTRACT_REQUIRED");
  if (!rows.length) throw new Error("COLLECTION_FACT_FILE_ROWS_REQUIRED");
  const sourceKeys = new Set(rows.map((row) => row.sourceKey));
  if (sourceKeys.size !== 1) throw new Error("COLLECTION_FACT_FILE_SOURCE_INVALID");
  const sourceKey = rows[0].sourceKey;
  if (sourceKey !== contract.sourceKey) throw new Error("COLLECTION_FACT_FILE_SOURCE_INVALID");
  const names = new Set<string>();
  for (const row of rows) {
    if (names.has(row.name)) throw new Error("COLLECTION_FACT_FILE_DUPLICATE_NAME");
    names.add(row.name);
  }
  const next = replaceDefinitions.value
    ? { contractVersion: contract.contractVersion, sourceKey: contract.sourceKey, current: {}, incremental: {} }
    : baseContract(contract.sourceKey);
  for (const row of rows) {
    delete next.current[row.name];
    delete next.incremental[row.name];
    next[row.factKind][row.name] = row.dataType;
  }
  emit("preview-contract", next);
}

function previewImportedValues(rows: CollectionFactValueFileRow[]) {
  const contract = props.contract;
  if (!contract || !rows.length) throw new Error("COLLECTION_FACT_CONTRACT_REQUIRED");
  if (rows.length > 500) throw new Error("COLLECTION_FACT_VALUE_BATCH_SIZE_INVALID");
  pendingValueImportResult.value = null;
  const definitions = new Map<string, CollectionFactDataType>([
    ...Object.entries(contract.current),
    ...Object.entries(contract.incremental),
  ]);
  const names = new Set<string>();
  const values: CollectionFactValueInput[] = [];
  let skipped = 0;
  for (const row of rows) {
    if (row.sourceKey !== contract.sourceKey) throw new Error("COLLECTION_FACT_FILE_SOURCE_INVALID");
    if (row.contractVersion !== contract.contractVersion) throw new Error("COLLECTION_FACT_FILE_VERSION_INVALID");
    if (names.has(row.name)) throw new Error("COLLECTION_FACT_FILE_DUPLICATE_NAME");
    names.add(row.name);
    const dataType = definitions.get(row.name);
    if (!dataType) {
      skipped += 1;
      continue;
    }
    if (!matchesValue(row.value, dataType)) {
      throw new Error("COLLECTION_FACT_VALUE_TYPE_INVALID");
    }
    values.push({ name: row.name, value: row.value });
  }
  if (!values.length) throw new Error("COLLECTION_FACT_FILE_NO_CURRENT_NAMES");
  pendingValueImportResult.value = { updated: values.length, skipped };
  emit("update-values", values);
}

function exportValues(format: CollectionFactFileFormat) {
  if (savingFile.value) return;
  savingFile.value = true;
  exportError.value = false;
  emit("export-values", format, (failed) => {
    savingFile.value = false;
    exportError.value = failed;
  });
}
</script>

<template>
  <div class="facts-table-stack">
    <section class="panel facts-table-panel">
      <header class="panel-header">
        <div>
          <p class="panel-kicker">collection_facts · {{ labels.collectionFactsBackendApi }}</p>
          <h2>{{ labels.factsTableTitle }}</h2>
        </div>
        <span class="status-pill">{{ isAllSourcesView ? labels.collectionFactsAllSourcesReadOnly : displayContractVersion }}</span>
      </header>
      <p>{{ labels.factsTableHint }}</p>
      <p v-if="isAllSourcesView" class="notice">{{ labels.collectionFactsAllSourcesReadOnly }}</p>
      <div class="facts-source-controls">
        <label class="field">
          <span>{{ labels.twinSourceKey }}</span>
          <input v-model="sourceInput" :disabled="contractBusy || tableBusy || valuesBusy" @keyup.enter="loadSource" />
        </label>
        <button class="secondary-action" type="button" :disabled="!enabled || contractBusy || tableBusy || valuesBusy" @click="loadSource">
          {{ contractBusy ? labels.loading : labels.collectionFactsLoad }}
        </button>
        <button class="secondary-action" type="button" :disabled="!enabled || !hasLoadedContract || contractBusy || valuesBusy" @click="openBatchOperations">
          {{ labels.collectionFactsBatchOperations }}
        </button>
        <button class="primary-action" type="button" :disabled="!enabled || !hasLoadedContract || contractBusy || valuesBusy" @click="startDefinitionCreate">
          {{ labels.collectionFactsAddDefinition }}
        </button>
      </div>
      <p v-if="operationError" class="warning">{{ operationError }}</p>
      <p v-if="status === 'saved'" class="notice">{{ labels.collectionFactsSaved }}</p>
      <p v-if="status === 'valuesSaved'" class="notice">{{ labels.collectionFactsValuesSaved }}</p>
      <p v-if="valueImportResultText" class="notice">{{ valueImportResultText }}</p>

      <div class="collection-fact-filters">
        <label>{{ labels.collectionFactsName }}<input v-model="nameInput" :disabled="tableBusy" @change="textQuery('name', $event)" /></label>
        <label>{{ labels.collectionFactsKind }}<select :value="query.factKind || ''" :disabled="tableBusy" @change="selectQuery('factKind', $event)"><option value="">{{ labels.collectionFactsAll }}</option><option v-for="kind in FACT_KINDS" :key="kind" :value="kind">{{ kind }}</option></select></label>
        <label>{{ labels.collectionFactsDataType }}<select :value="query.dataType || ''" :disabled="tableBusy" @change="selectQuery('dataType', $event)"><option value="">{{ labels.collectionFactsAll }}</option><option v-for="dataType in DATA_TYPES" :key="dataType" :value="dataType">{{ dataType }}</option></select></label>
        <div class="facts-filter-action"><button class="secondary-action" type="button" :disabled="tableBusy" @click="emit('query', { page: query.page })">{{ tableBusy ? labels.loading : labels.refresh }}</button></div>
      </div>

      <div class="table-scroll facts-table-scroll" tabindex="0">
        <table class="facts-table">
          <thead><tr><th>{{ labels.collectionFactsName }}</th><th>{{ labels.twinSourceKey }}</th><th>{{ labels.collectionFactsKind }}</th><th>{{ labels.collectionFactsDataType }}</th><th>{{ labels.collectionFactsValue }}</th><th>{{ labels.collectionFactsUpdatedAt }}</th><th>{{ labels.collectionFactsRowVersion }}</th><th>{{ labels.collectionFactsActions }}</th></tr></thead>
          <tbody>
            <tr v-for="fact in result.items" :key="`${fact.sourceKey}:${fact.name}`">
              <td><code>{{ fact.name }}</code></td><td><code>{{ fact.sourceKey }}</code></td><td>{{ fact.factKind }}</td><td>{{ fact.dataType }}</td><td><code>{{ fact.value ?? labels.collectionFactsNull }}</code></td><td>{{ fact.updatedAt }}</td><td><code>{{ fact.rowVersion }}</code></td>
              <td class="facts-row-actions"><button class="secondary-action" type="button" :disabled="!enabled || !hasLoadedContract || contractBusy || valuesBusy" @click="startDefinitionEdit(fact)">{{ labels.collectionFactsEditDefinition }}</button><button class="secondary-action" type="button" :disabled="!enabled || !hasLoadedContract || valuesBusy" @click="startValueEdit(fact)">{{ labels.collectionFactsEditValue }}</button><button class="danger-action" type="button" :disabled="!enabled || !hasLoadedContract || contractBusy" @click="previewDefinitionDelete(fact)">{{ labels.collectionFactsDeleteDefinition }}</button></td>
            </tr>
            <tr v-if="tableBusy"><td colspan="8">{{ labels.loading }}</td></tr>
          </tbody>
        </table>
      </div>
      <p v-if="!tableBusy && !result.items.length" class="empty-state">{{ labels.collectionFactsEmpty }}</p>
      <PaginationBar :labels="labels" :page="result.page" :page-size="result.pageSize" :total="result.total" :busy="tableBusy" @update:page="emit('query', { page: $event })" @update:page-size="emit('query', { page: 1, pageSize: $event })" />
    </section>

    <section v-if="pendingPreview" class="panel facts-preview-panel">
      <header class="panel-header"><div><p class="panel-kicker">{{ labels.collectionFactsBackendApi }}</p><h2>{{ labels.collectionFactsPreviewTitle }}</h2></div><span class="status-pill">{{ labels.collectionFactsValidated }}</span></header>
      <p>{{ labels.collectionFactsPreviewHint }}</p>
      <dl class="facts-preview-summary"><div><dt>{{ labels.collectionFactsAdded }}</dt><dd>{{ pendingPreview.summary.added.length }}</dd></div><div><dt>{{ labels.collectionFactsRetained }}</dt><dd>{{ pendingPreview.summary.retained.length }}</dd></div><div><dt>{{ labels.collectionFactsDeleted }}</dt><dd>{{ pendingPreview.summary.deleted.length }}</dd></div><div><dt>{{ labels.collectionFactsKindChanges }}</dt><dd>{{ pendingPreview.summary.kindChanges.length }}</dd></div><div><dt>{{ labels.collectionFactsTypeChanges }}</dt><dd>{{ pendingPreview.summary.typeChanges.length }}</dd></div></dl>
      <label v-if="previewNeedsConfirmation" class="check-field facts-confirmation"><input v-model="applyingConfirmed" type="checkbox" /><span>{{ labels.collectionFactsPreviewConfirmImpact }}</span></label>
      <p v-if="previewError" class="warning">{{ previewError }}</p>
      <div class="action-row facts-editor-actions"><button class="secondary-action" type="button" :disabled="contractBusy" @click="emit('discard-preview')">{{ labels.collectionFactsCancel }}</button><button class="primary-action" type="button" :disabled="!enabled || !hasLoadedContract || contractBusy" @click="applyPreview">{{ labels.collectionFactsApply }}</button></div>
    </section>

    <FactDefinitionDialog
      v-if="definitionDraft"
      :labels="labels"
      :contract-version="displayContractVersion"
      :draft="definitionDraft"
      :fact-kinds="FACT_KINDS"
      :data-types="DATA_TYPES"
      :busy="contractBusy"
      :enabled="enabled"
      :invalid="Boolean(definitionError)"
      @close="closeDefinitionDialog"
      @preview="previewDefinitionDraft"
      @update-draft="updateDefinitionDraft"
    />
    <FactValueDialog
      v-if="valueDraft"
      :labels="labels"
      :draft="valueDraft"
      :busy="valuesBusy"
      :enabled="enabled"
      :invalid="Boolean(valueError)"
      @close="closeValueDialog"
      @save="submitValue"
      @update-draft="updateValueDraft"
    />
    <FactBatchOperationsDialog
      v-if="batchOperationsOpen"
      :labels="labels"
      :has-contract="hasLoadedContract"
      :has-applied-definitions="hasAppliedDefinitions"
      :contract-busy="contractBusy"
      :values-busy="valuesBusy"
      :saving-file="savingFile"
      :enabled="enabled"
      :replace-definitions="replaceDefinitions"
      :file-error-text="fileErrorText"
      :export-error="exportError"
      @close="closeBatchOperations"
      @update:replace-definitions="replaceDefinitions = $event"
      @download-definition-template="saveDefinitionTemplate"
      @download-definition="saveDefinitionExport"
      @export-values="exportValues"
      @import-file="importFile"
    />
  </div>
</template>

<style>
.facts-table-stack { display: grid; width: 100%; min-width: 0; gap: 16px; }
.facts-table-stack > .panel { min-width: 0; max-width: none; }
.facts-table-scroll { min-width: 0; }
.facts-source-controls { display: flex; flex-wrap: wrap; align-items: end; gap: 12px; margin-top: 16px; }
.facts-source-controls .field { flex: 1 1 280px; }
.collection-fact-filters { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; margin: 18px 0; }
.collection-fact-filters label { display: grid; gap: 6px; color: #52707a; font-size: 12px; font-weight: 650; }
.facts-filter-action { display: flex; align-items: end; }
.facts-table-scroll { overflow-x: auto; }
.facts-table { min-width: 1120px; }
.facts-table td { vertical-align: top; white-space: normal; }
.facts-table code { overflow-wrap: anywhere; white-space: normal; }
.facts-row-actions, .facts-file-actions { display: flex; flex-wrap: wrap; gap: 8px; }
.facts-editor-actions { margin-top: 16px; }
.facts-preview-summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin: 16px 0; }
.facts-preview-summary div { padding: 10px; border: 1px solid #dce6e8; border-radius: 6px; }
.facts-preview-summary dt { color: #52707a; font-size: 12px; }
.facts-preview-summary dd { margin: 5px 0 0; font-size: 18px; }
.facts-confirmation, .facts-replace-toggle { margin-top: 10px; }
.facts-file-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; margin-top: 16px; }
.facts-file-grid article { padding: 14px; border: 1px solid #dce6e8; border-radius: 6px; }
.facts-file-grid h3 { margin: 0 0 12px; font-size: 14px; }
.facts-file-input { display: none; }
.facts-dialog-backdrop { position: fixed; inset: 0; z-index: 30; display: grid; place-items: center; padding: 24px; background: rgb(25 48 53 / 42%); }
.facts-dialog { width: min(900px, 100%); max-height: calc(100vh - 48px); overflow: auto; box-shadow: 0 18px 48px rgb(21 46 53 / 26%); }
.facts-value-dialog { width: min(640px, 100%); }
.facts-dialog-header { display: flex; align-items: start; justify-content: space-between; gap: 16px; }
@media (max-width: 640px) { .facts-dialog-backdrop { align-items: start; padding: 12px; } .facts-dialog { max-height: calc(100vh - 24px); } }
</style>
