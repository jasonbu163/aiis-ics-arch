<!--
  File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/components/MappingConfigurationsPanel.vue
  Description: Saved Mapping table, Target API-derived local drafts, binding dialog, and confirmed manual-run result display.
  Main Features:
    - Loads enabled Target APIs into removable page-memory Mapping drafts
    - Selects a source and fact for each fact binding, or a fixed constant instead
    - Keeps local previews side-effect free while a saved row can emit one explicit manual-run confirmation
-->
<script setup lang="ts">
import { ElDialog } from "element-plus";
import { useTableWidths, vTableWidths } from "../../../console/tableWidths";
import { ConsoleCard, ConsoleActionButton, StatusCapsule } from "@aw-ui";
import { computed, ref, watch } from "vue";

import type { LocaleMessages } from "../../../locales";
import { saveCollectionFactFile } from "../api";
import type {
  BackendCollectionFactRecord,
  ConfigurationImportPreview,
  MappingConfiguration,
  MappingConfigurationBinding,
  MappingManualRunSummary,
  MappingValueRuleConfiguration,
  TargetApiConfiguration,
} from "../types";
import type { LocalMappingConfigurationDraft, MappingConfigurationDraft, MappingRequestPreview } from "../store/mappingConfigurations";
import {
  createMappingConfigurationExportFile,
  createMappingConfigurationTemplateFile,
  parseMappingConfigurationFile,
  type MappingConfigurationFileFormat,
} from "../utils/mappingConfigurationFiles";
import MappingBatchOperationsDialog from "./MappingBatchOperationsDialog.vue";

const props = defineProps<{
  labels: LocaleMessages;
  savedPreview?: Record<string, unknown> | null;
  configurations: MappingConfiguration[];
  localDrafts: LocalMappingConfigurationDraft[];
  targetApis: TargetApiConfiguration[];
  valueRules: MappingValueRuleConfiguration[];
  sourceFacts: BackendCollectionFactRecord[];
  draft: MappingConfigurationDraft;
  selectedId: string | null;
  selectedDraftId: string | null;
  selectedTargetApi: TargetApiConfiguration | null;
  selectedTargetApiLocked: boolean;
  requestPreview: MappingRequestPreview;
  manualRuns: Record<string, MappingManualRunSummary>;
  manualRunBusyIds: string[];
  busy: boolean;
  factsBusy: boolean;
  status: "idle" | "saved" | "deleted";
  error: string;
  importPreview: ConfigurationImportPreview | null;
  enabled: boolean;
}>();

const emit = defineEmits<{
  load: [];
  "load-target-apis": [];
  "start-create": [];
  open: [mappingId: string];
  "open-draft": [localId: string];
  "remove-draft": [localId: string];
  "load-source-facts": [];
  "preview-saved": [id: string];
  "update-draft": [patch: Partial<MappingConfigurationDraft>];
  "initialize-bindings": [targetApiKey: string];
  "update-binding": [jsonPath: string, patch: Partial<MappingConfigurationBinding>];
  save: [];
  remove: [mappingId: string];
  "run-manual": [mappingId: string];
  "preview-import": [items: unknown[]];
  "apply-import": [];
  "clear-import": [];
}>();

const editorOpen = ref(false);
const batchOpen = ref(false);
const savingFile = ref(false);
const fileError = ref("");
const constantErrors = ref<Record<string, boolean>>({});

watch(() => props.status, (status) => {
  if (status === "saved") editorOpen.value = false;
});

function startCreate() {
  emit("start-create");
  editorOpen.value = true;
}

function openEditor(mappingId: string) {
  emit("open", mappingId);
  editorOpen.value = true;
}

function openDraft(localId: string) {
  emit("open-draft", localId);
  editorOpen.value = true;
}

function closeBatch() {
  fileError.value = "";
  emit("clear-import");
  batchOpen.value = false;
}

function updateTargetApi(event: Event) {
  const targetApiKey = (event.target as HTMLSelectElement).value;
  emit("update-draft", { targetApiKey });
  emit("initialize-bindings", targetApiKey);
}

function updateBindingFixed(path: string, event: Event) {
  const fixed = (event.target as HTMLInputElement).checked;
  constantErrors.value = { ...constantErrors.value, [path]: false };
  emit("update-binding", path, {
    kind: fixed ? "constant" : "fact",
    value: fixed ? "" : null,
    sourceKey: null,
    factName: null,
  });
}

function constantValue(raw: string, dataType: string): { value: unknown; valid: boolean } {
  if (dataType === "string" || dataType === "datetime") return { value: raw, valid: true };
  if (dataType === "boolean") {
    if (raw === "true") return { value: true, valid: true };
    if (raw === "false") return { value: false, valid: true };
    return { value: raw, valid: false };
  }
  const value = Number(raw);
  const valid = raw.trim() !== "" && Number.isFinite(value)
    && (dataType !== "integer" || Number.isInteger(value));
  return { value: valid ? value : raw, valid };
}

function constantInputValue(value: unknown): string {
  return value === null || value === undefined ? "" : String(value);
}

function updateConstant(path: string, dataType: string, event: Event) {
  const parsed = constantValue((event.target as HTMLInputElement).value, dataType);
  constantErrors.value = { ...constantErrors.value, [path]: !parsed.valid };
  emit("update-binding", path, {
    kind: "constant",
    value: parsed.value,
    sourceKey: null,
    factName: null,
  });
}

function valueRuleOptions(dataType: string) {
  return props.valueRules.filter((rule) => rule.enabled && rule.values.length > 0 && rule.dataType === dataType);
}

function bindingValidation(parameter: TargetApiConfiguration["parameterSchema"][number]) {
  const binding = props.draft.bindings[parameter.parameterKey];
  if (!binding) return parameter.required ? props.labels.mappingConfigurationBindingRequired : props.labels.mappingConfigurationNoRule;
  if (binding.kind === "fact") {
    if (!props.sourceFacts.some((fact) => fact.sourceKey === binding.sourceKey && fact.name === binding.factName)) return props.labels.mappingConfigurationFactMissing;
    return binding.valueRuleKey ? props.labels.mappingConfigurationRuleDeferred : props.labels.mappingConfigurationNoRule;
  }
  if (constantErrors.value[parameter.parameterKey]) return props.labels.mappingConfigurationValueInvalid;
  const rule = props.valueRules.find((item) => item.valueRuleKey === binding.valueRuleKey) ?? null;
  if (!rule) return props.labels.mappingConfigurationNoRule;
  return rule.values.some((value) => JSON.stringify(value) === JSON.stringify(binding.value))
    ? props.labels.mappingConfigurationRuleAllowed
    : props.labels.mappingConfigurationRuleRejected;
}


function bindingSummary(bindings: Record<string, MappingConfigurationBinding>) {
  const entries = Object.values(bindings);
  const facts = entries.filter((item) => item.kind === "fact").length;
  return `${entries.length - facts} / ${facts}`;
}

async function saveFile(file: ReturnType<typeof createMappingConfigurationExportFile>) {
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
  void saveFile(createMappingConfigurationTemplateFile("mappings", format));
}

function exportMappings(format: MappingConfigurationFileFormat) {
  void saveFile(createMappingConfigurationExportFile(format, props.configurations));
}

async function importFile(file: File) {
  try {
    fileError.value = "";
    emit("preview-import", await parseMappingConfigurationFile("mappings", file));
  } catch (error) {
    fileError.value = String(error);
  }
}

function remove(mapping: MappingConfiguration) {
  if (globalThis.confirm(props.labels.mappingConfigurationDeleteConfirm.replace("{name}", mapping.name))) emit("remove", mapping.id);
}

function manualRunFor(mapping: MappingConfiguration): MappingManualRunSummary | null {
  return props.manualRuns[mapping.id] ?? null;
}

function canRunManual(mapping: MappingConfiguration) {
  const target = props.targetApis.find((item) => item.id === mapping.targetApiId) ?? null;
  return Boolean(mapping.enabled && mapping.rowVersion && target?.enabled);
}

function manualRunIsStale(mapping: MappingConfiguration, run: MappingManualRunSummary | null) {
  return Boolean(run && run.mappingRowVersion !== mapping.rowVersion);
}

function manualRunStatus(mapping: MappingConfiguration) {
  const run = manualRunFor(mapping);
  if (!run) return props.labels.mappingManualRunNone;
  if (manualRunIsStale(mapping, run)) return props.labels.mappingManualRunStale;
  if (run.status === "in_progress") return props.labels.mappingManualRunInProgress;
  if (run.status === "preflight_rejected") return props.labels.mappingManualRunPreflightRejected;
  if (run.status === "succeeded") return props.labels.mappingManualRunSucceeded;
  if (run.status === "request_failed") return props.labels.mappingManualRunFailed;
  return props.labels.mappingManualRunAmbiguous;
}

function manualRunUnresolved(mapping: MappingConfiguration) {
  const run = manualRunFor(mapping);
  if (!run || manualRunIsStale(mapping, run) || !run.unresolvedParameterKeys.length) return "";
  return props.labels.mappingManualRunUnresolved.replace(
    "{parameters}",
    run.unresolvedParameterKeys.join(", "),
  );
}

function requestManualRun(mapping: MappingConfiguration) {
  const target = props.targetApis.find((item) => item.id === mapping.targetApiId) ?? null;
  if (!target || !mapping.rowVersion || props.manualRunBusyIds.includes(mapping.id)) return;
  const confirmation = props.labels.mappingManualRunConfirm
    .replace("{mappingName}", mapping.name)
    .replace("{mappingKey}", mapping.mappingKey)
    .replace("{targetName}", target.name)
    .replace("{targetApiKey}", target.apiKey)
    .replace("{method}", target.httpMethod)
    .replace("{path}", target.path);
  if (globalThis.confirm(confirmation)) emit("run-manual", mapping.id);
}


const mappingsTable = useTableWidths("mappings", [{ id: "state", width: 140 }, { id: "key", width: 200 }, { id: "name", width: 220 }, { id: "targetApi", width: 220 }, { id: "bindings", width: 180 }, { id: "enabled", width: 140 }, { id: "manualRun", width: 220 }, { id: "actions", width: 380, min: 380, fixed: true }]);
const bindingsTable = useTableWidths("mapping-bindings", [{ id: "parameter", width: 220 }, { id: "mode", width: 180 }, { id: "value", width: 400 }, { id: "rule", width: 240 }, { id: "validation", width: 230 }]);
</script>

<template>
  <div class="mapping-page-stack mapping-configurations-stack">
    <p class="hint">{{ labels.localConfigurationOnly }}</p>
    <section v-if="savedPreview"><h3>{{ labels.localSavedPreview }}</h3><pre>{{ JSON.stringify(savedPreview, null, 2) }}</pre></section>
    <ConsoleCard :title="labels.mappingConfigurationsTitle">
    <p v-if="busy" class="hint" role="status">{{ labels.loading }}</p>
<template #actions><StatusCapsule label="HTTP" /></template>
      <p>{{ labels.mappingConfigurationsHint }}</p>
      <div class="action-row"><ConsoleActionButton tone="secondary" native-type="button" :disabled="!enabled || busy" @click="emit('load-target-apis')">{{ labels.mappingConfigurationsLoadTargetApis }}</ConsoleActionButton><ConsoleActionButton tone="secondary" native-type="button" :disabled="!enabled || busy" @click="batchOpen = true">{{ labels.mappingBatchOperations }}</ConsoleActionButton><ConsoleActionButton tone="primary" native-type="button" :disabled="!enabled || busy" @click="startCreate">{{ labels.mappingConfigurationNew }}</ConsoleActionButton></div>
      <p v-if="error" class="warning" role="alert">{{ labels.mappingConfigurationOperationFailed }} {{ /CONFLICT|PREVIEW_CHANGED/.test(error) ? labels.localConfigurationConflict : error }}</p>
      <p v-if="status === 'saved'" class="notice">{{ labels.mappingConfigurationSaved }}</p>
    </ConsoleCard>

    <ConsoleCard :title="labels.mappingConfigurationsListTitle">
      <div class="table-scroll mapping-list-scroll" tabindex="0"><ConsoleActionButton size="small" @click="mappingsTable.reset">{{ labels.resetTableWidths }}</ConsoleActionButton>
<table v-table-widths="[mappingsTable, labels.resizeTableColumn]" class="mapping-list-table mapping-configurations-table"><thead><tr><th>{{ labels.mappingConfigurationState }}</th><th>{{ labels.mappingConfigurationKey }}</th><th>{{ labels.targetApiName }}</th><th>{{ labels.mappingConfigurationTargetApi }}</th><th>{{ labels.mappingConfigurationBindingSummary }}</th><th>{{ labels.targetApiState }}</th><th>{{ labels.mappingManualRunResult }}</th><th>{{ labels.targetApiActions }}</th></tr></thead>
        <tbody>
          <tr v-for="pending in localDrafts" :key="pending.localId"><td>{{ labels.mappingConfigurationDraft }}</td><td><code>{{ pending.draft.mappingKey }}</code></td><td>{{ pending.draft.name }}</td><td><code>{{ pending.draft.targetApiKey }}</code></td><td>{{ bindingSummary(pending.draft.bindings) }}</td><td>{{ pending.draft.enabled ? labels.targetApiEnabled : labels.targetApiDisabled }}</td><td>{{ labels.mappingManualRunSavedOnly }}</td><td><div class="mapping-list-row-actions"><ConsoleActionButton size="small" tone="secondary" native-type="button" :disabled="!enabled || busy" @click="openDraft(pending.localId)">{{ labels.mappingValueRuleConfigure }}</ConsoleActionButton><ConsoleActionButton size="small" tone="danger" native-type="button" :disabled="!enabled || busy" @click="emit('remove-draft', pending.localId)">{{ labels.mappingConfigurationRemoveDraft }}</ConsoleActionButton></div></td></tr>
          <tr v-for="mapping in configurations" :key="mapping.id"><td>{{ labels.mappingConfigurationSavedState }}</td><td><code>{{ mapping.mappingKey }}</code></td><td>{{ mapping.name }}</td><td><code>{{ mapping.targetApiKey }}</code></td><td>{{ bindingSummary(mapping.bindings) }}</td><td>{{ mapping.enabled ? labels.targetApiEnabled : labels.targetApiDisabled }}</td><td><div class="mapping-manual-run-result"><span>{{ manualRunStatus(mapping) }}</span><small v-if="manualRunUnresolved(mapping)">{{ manualRunUnresolved(mapping) }}</small></div></td><td><div class="mapping-list-row-actions"><ConsoleActionButton size="small" tone="secondary" :disabled="!enabled || busy" @click="emit('preview-saved', mapping.id)">{{ labels.localSavedPreview }}</ConsoleActionButton><ConsoleActionButton size="small" tone="primary" native-type="button" :disabled="!enabled || busy || !canRunManual(mapping) || manualRunBusyIds.includes(mapping.id) || manualRunFor(mapping)?.status === 'in_progress'" @click="requestManualRun(mapping)">{{ labels.mappingManualRunOnce }}</ConsoleActionButton><ConsoleActionButton size="small" tone="secondary" native-type="button" :disabled="!enabled || busy" @click="openEditor(mapping.id)">{{ labels.targetApiEdit }}</ConsoleActionButton><ConsoleActionButton size="small" tone="danger" native-type="button" :disabled="!enabled || busy" @click="remove(mapping)">{{ labels.targetApiDelete }}</ConsoleActionButton></div></td></tr>
        </tbody>
      </table></div>
      <p v-if="!configurations.length && !localDrafts.length" class="empty-state">{{ labels.mappingConfigurationsEmpty }}</p>
    </ConsoleCard>

    <Teleport to="#sma-overlays"><ElDialog :model-value="Boolean(editorOpen)" :append-to-body="false" :title="selectedId || selectedDraftId ? labels.mappingConfigurationEdit : labels.mappingConfigurationNew" class="sma-dialog mapping-configuration-dialog" @close="editorOpen = false">
<template #header><div class="panel-header facts-dialog-header">
          <div>
            <p class="panel-kicker">{{ labels.mappingLocalPreviewOnly }}</p>
            <h2>{{ selectedId || selectedDraftId ? labels.mappingConfigurationEdit : labels.mappingConfigurationNew }}</h2>
          </div>
          <label class="mapping-configuration-enabled">
            <input :checked="draft.enabled" type="checkbox" :disabled="!enabled || busy" @change="emit('update-draft', { enabled: ($event.target as HTMLInputElement).checked })" />
            <span>{{ labels.targetApiEnabled }}</span>
          </label>
        </div></template>
        <form class="mapping-configuration-form" @submit.prevent="emit('save')">
          <div class="mapping-configuration-form-grid">
            <label class="field"><span>{{ labels.mappingConfigurationKey }}</span><input :value="draft.mappingKey" :readonly="Boolean(selectedId)" :disabled="!enabled || busy" @input="emit('update-draft', { mappingKey: ($event.target as HTMLInputElement).value })" /></label>
            <label class="field"><span>{{ labels.targetApiName }}</span><input :value="draft.name" :disabled="!enabled || busy" @input="emit('update-draft', { name: ($event.target as HTMLInputElement).value })" /></label>
            <label class="field"><span>{{ labels.mappingConfigurationTargetApi }}</span><select :value="draft.targetApiKey" :disabled="!enabled || busy || selectedTargetApiLocked" @change="updateTargetApi"><option value="">—</option><option v-for="target in targetApis.filter((item) => item.enabled)" :key="target.apiKey" :value="target.apiKey">{{ target.name }} · {{ target.apiKey }}</option></select></label>
            <label class="field"><span>{{ labels.mappingProcessingInterval }}</span><input :value="draft.intervalMs" type="number" min="1" :disabled="!enabled || busy" @input="emit('update-draft', { intervalMs: Number(($event.target as HTMLInputElement).value) })" /></label>
          </div>
          <p class="hint">{{ labels.localSourceUnverified }}</p>
          <p v-if="factsBusy" class="hint">{{ labels.loading }}</p>
          <section v-if="selectedTargetApi" class="mapping-bindings">
            <h3>{{ labels.mappingConfigurationBindings }}</h3>
            <div class="table-scroll" tabindex="0">
              <ConsoleActionButton size="small" @click="bindingsTable.reset">{{ labels.resetTableWidths }}</ConsoleActionButton>
<table v-table-widths="[bindingsTable, labels.resizeTableColumn]" class="mapping-bindings-table">

                <thead><tr><th>{{ labels.mappingConfigurationParameterIdentity }}</th><th>{{ labels.mappingConfigurationUseFixedValue }}</th><th>{{ labels.mappingConfigurationValue }}</th><th>{{ labels.mappingConfigurationValueRule }}</th><th>{{ labels.mappingConfigurationValidation }}</th></tr></thead>
                <tbody>
                  <tr v-for="parameter in selectedTargetApi.parameterSchema" :key="parameter.parameterKey">
                    <td class="mapping-binding-parameter">
                      <StatusCapsule :label="parameter.location" />
                      <code>{{ parameter.jsonPath ?? parameter.name }}</code>
                      <small>{{ parameter.dataType }} · {{ parameter.required ? labels.targetApiRequired : '—' }}</small>
                    </td>
                    <td class="mapping-binding-mode">
                      <label class="mapping-binding-mode-toggle">
                        <input type="checkbox" :checked="draft.bindings[parameter.parameterKey]?.kind === 'constant'" :disabled="!enabled || busy" @change="updateBindingFixed(parameter.parameterKey, $event)" />
                        <span>{{ labels.mappingConfigurationConstant }}</span>
                      </label>
                    </td>
                    <td class="mapping-binding-value">
                      <div v-if="draft.bindings[parameter.parameterKey]?.kind === 'fact'" class="mapping-fact-selects">
                        <label>
                          <span>{{ labels.twinSourceKey }}</span>
                          <input type="text" :value="draft.bindings[parameter.parameterKey]?.sourceKey ?? ''" :disabled="!enabled || busy" @change="emit('update-binding', parameter.parameterKey, { sourceKey: ($event.target as HTMLInputElement).value || null, factName: null, value: null })" />
                        </label>
                        <label>
                          <span>{{ labels.mappingConfigurationFact }}</span>
                          <input type="text" :value="draft.bindings[parameter.parameterKey]?.factName ?? ''" :disabled="!enabled || busy" @change="emit('update-binding', parameter.parameterKey, { factName: ($event.target as HTMLInputElement).value || null, value: null })" />
                        </label>
                      </div>
                      <input v-else :value="constantInputValue(draft.bindings[parameter.parameterKey]?.value)" :class="{ invalid: constantErrors[parameter.parameterKey] }" :disabled="!enabled || busy" @input="updateConstant(parameter.parameterKey, parameter.dataType, $event)" />
                    </td>
                    <td><select :value="draft.bindings[parameter.parameterKey]?.valueRuleKey ?? ''" :disabled="!enabled || busy" @change="emit('update-binding', parameter.parameterKey, { valueRuleKey: ($event.target as HTMLSelectElement).value || null })"><option value="">—</option><option v-for="rule in valueRuleOptions(parameter.dataType)" :key="rule.id" :value="rule.valueRuleKey ?? ''">{{ rule.name }} · {{ rule.valueRuleKey }}</option></select></td>
                    <td class="mapping-binding-validation">{{ bindingValidation(parameter) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
          <details v-if="selectedTargetApi" class="mapping-local-preview" :open="Boolean(requestPreview.unresolved.length)">
            <summary>{{ labels.mappingConfigurationPreview }}</summary>
            <div class="mapping-local-preview-content">
              <div class="mapping-preview-grid"><div><strong>{{ labels.mappingPreviewResolvedPath }}</strong><pre>{{ requestPreview.resolvedPath }}</pre></div><div><strong>{{ labels.mappingPreviewQuery }}</strong><pre>{{ JSON.stringify(requestPreview.query, null, 2) }}</pre></div><div><strong>{{ labels.mappingPreviewHeaders }}</strong><pre>{{ JSON.stringify(requestPreview.headers, null, 2) }}</pre></div><div><strong>{{ labels.mappingPreviewBody }}</strong><pre>{{ JSON.stringify(requestPreview.body, null, 2) }}</pre></div></div>
              <p v-if="requestPreview.unresolved.length" class="warning" role="alert">{{ labels.mappingPreviewUnresolved.replace('{parameters}', requestPreview.unresolved.join(', ')) }}</p>
              <p>{{ labels.mappingConfigurationPreviewHint }}</p>
            </div>
          </details>
          <div class="action-row facts-editor-actions"><ConsoleActionButton tone="secondary" native-type="button" :disabled="busy" @click="editorOpen = false">{{ labels.collectionFactsCancel }}</ConsoleActionButton><ConsoleActionButton tone="primary" native-type="submit" :disabled="!enabled || busy">{{ labels.targetApiSave }}</ConsoleActionButton></div>
        </form>

</ElDialog></Teleport>

    <MappingBatchOperationsDialog v-if="batchOpen" :labels="labels" :title="labels.mappingConfigurationsBatchTitle" :busy="busy" :saving-file="savingFile" :preview="importPreview" :error="fileError || error" :enabled="enabled" @close="closeBatch" @download-template="downloadTemplate" @export="exportMappings" @import="importFile" @apply="emit('apply-import')" />
  </div>
</template>

<style scoped>
.mapping-configurations-table { min-width: 1240px; }
.mapping-configurations-table th:first-child,
.mapping-configurations-table td:first-child { width: 76px; min-width: 76px; white-space: nowrap; }
.mapping-configurations-table th:last-child,
.mapping-configurations-table td:last-child { width: 224px; min-width: 224px; }
.mapping-configurations-table .mapping-list-row-actions > button { flex: 0 0 auto; white-space: nowrap; }
.mapping-configurations-table td, .mapping-bindings-table td { vertical-align: top; white-space: normal; }
.mapping-configurations-table td:first-child { white-space: nowrap; }

.mapping-configuration-dialog { width: min(1440px, calc(100vw - 48px)); max-width: none; max-height: calc(100vh - 48px); overflow: auto; box-shadow: var(--agent-shadow); }
.mapping-configuration-form { display: grid; gap: 18px; }
.mapping-configuration-form-grid { display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr) minmax(280px, 1.45fr) minmax(130px, 0.5fr); gap: 14px; }
.mapping-configuration-enabled, .mapping-binding-mode-toggle { display: inline-flex; align-items: center; gap: 8px; color: var(--agent-text-muted); font-size: 13px; white-space: nowrap; }
.mapping-bindings h3 { margin: 0 0 10px; font-size: 15px; }
.mapping-bindings-table { min-width: 1040px; table-layout: fixed; }
.mapping-binding-parameter-column { width: 18%; }
.mapping-binding-mode-column { width: 13%; }
.mapping-binding-value-column { width: 33%; }
.mapping-binding-rule-column { width: 20%; }
.mapping-binding-validation-column { width: 16%; }
.mapping-bindings-table select, .mapping-bindings-table input:not([type="checkbox"]) { width: 100%; min-width: 0; }
.mapping-binding-parameter { display: grid; gap: 6px; }
.mapping-binding-parameter small, .mapping-fact-selects span { color: var(--agent-text-muted); font-size: 12px; }
.mapping-binding-mode { vertical-align: middle !important; }
.mapping-fact-selects { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
.mapping-fact-selects label { display: grid; min-width: 0; gap: 4px; }
.mapping-binding-validation { color: var(--agent-text-muted); line-height: 1.45; }
.mapping-local-preview { border-top: 1px solid var(--agent-border); padding-top: 16px; }
.mapping-local-preview summary { cursor: pointer; color: var(--agent-text); font-size: 15px; font-weight: 650; }
.mapping-local-preview[open] summary { margin-bottom: 12px; }
.mapping-local-preview-content { display: grid; gap: 12px; }
.mapping-local-preview pre { max-height: 240px; margin: 0; padding: 12px; overflow: auto; background: var(--agent-surface-muted); border: 1px solid var(--agent-border); border-radius: 4px; }
.mapping-preview-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.mapping-preview-grid strong { display: block; margin-bottom: 6px; font-size: 12px; }
.mapping-configuration-dialog .facts-editor-actions { position: sticky; bottom: -18px; z-index: 1; margin: 0 -18px -18px; padding: 14px 18px; background: var(--agent-surface); border-top: 1px solid var(--agent-border); }
.mapping-manual-run-result { display: grid; gap: 4px; min-width: 180px; }
.mapping-manual-run-result small { color: var(--agent-warning); }
.invalid { border-color: var(--agent-danger); }
@media (max-width: 1180px) { .mapping-configuration-form-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 800px) {  .mapping-configuration-dialog { width: calc(100vw - 24px); max-height: calc(100vh - 24px); } .mapping-configuration-form-grid, .mapping-preview-grid { grid-template-columns: 1fr; } }
</style>
