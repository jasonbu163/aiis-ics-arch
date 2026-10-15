<!--
  File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/components/MappingValueRulesPanel.vue
  Description: Legal Value Preset table, select-all fact-origin drafts, and single-record dialog.
  Main Features:
    - Loads saved Collection Facts as local, individually or collectively removable preset drafts
    - Keeps legal values independent from fact current values and definitions
    - Retains r1 batch exchange and protected deletion for saved records only
-->
<script setup lang="ts">
import { computed, ref, watch } from "vue";

import type { LocaleMessages } from "../../../locales";
import { saveCollectionFactFile } from "../api";
import type { ConfigurationImportPreview, MappingValueRuleConfiguration } from "../types";
import type { FactOriginDraftIdentity, MappingValueRuleDraft } from "../store/mappingValueRules";
import {
  createMappingConfigurationTemplateFile,
  createMappingValueRuleExportFile,
  parseMappingConfigurationFile,
  type MappingConfigurationFileFormat,
} from "../utils/mappingConfigurationFiles";
import MappingBatchOperationsDialog from "./MappingBatchOperationsDialog.vue";

const props = defineProps<{
  labels: LocaleMessages;
  configurations: MappingValueRuleConfiguration[];
  factOriginDrafts: MappingValueRuleDraft[];
  draft: MappingValueRuleDraft;
  selectedId: string | null;
  selectedOriginKey: string | null;
  busy: boolean;
  status: "idle" | "saved" | "deleted";
  error: string;
  importPreview: ConfigurationImportPreview | null;
  enabled: boolean;
}>();

const emit = defineEmits<{
  load: [];
  "load-saved-facts": [];
  "start-create": [];
  open: [valueRuleId: string];
  "open-fact-origin-draft": [sourceKey: string, factName: string];
  "remove-fact-origin-draft": [sourceKey: string, factName: string];
  "remove-fact-origin-drafts": [drafts: FactOriginDraftIdentity[]];
  "update-draft": [patch: Partial<MappingValueRuleDraft>];
  save: [];
  remove: [valueRuleId: string];
  "preview-import": [items: unknown[]];
  "apply-import": [];
  "clear-import": [];
}>();

const editorOpen = ref(false);
const batchOpen = ref(false);
const selectedDraftKeys = ref<string[]>([]);
const pendingDraftRemovals = ref<FactOriginDraftIdentity[]>([]);
const savingFile = ref(false);
const fileError = ref("");
const displayedError = computed(() => {
  if (!props.error) return "";
  if (props.error.includes("tss_mapping_value_rule_in_use")) return props.labels.mappingValueRuleInUse;
  return props.labels.mappingValueRuleOperationFailed;
});
const isOriginDraft = computed(() => props.selectedOriginKey !== null);

watch(() => props.status, (status) => {
  if (status === "saved") editorOpen.value = false;
});
watch(() => props.factOriginDrafts, (drafts) => {
  const available = new Set(drafts.map((draft) => draftKey(draft.originSourceKey, draft.originFactName)));
  selectedDraftKeys.value = selectedDraftKeys.value.filter((key) => available.has(key));
});

const selectableDraftKeys = computed(() => props.factOriginDrafts.flatMap((draft) => {
  const key = draftKey(draft.originSourceKey, draft.originFactName);
  return key ? [key] : [];
}));
const allDraftsSelected = computed(() => (
  selectableDraftKeys.value.length > 0
  && selectableDraftKeys.value.every((key) => selectedDraftKeys.value.includes(key))
));
const draftSelectionIndeterminate = computed(() => (
  selectedDraftKeys.value.length > 0 && !allDraftsSelected.value
));

function startCreate() {
  emit("start-create");
  editorOpen.value = true;
}

function openEditor(valueRuleId: string) {
  emit("open", valueRuleId);
  editorOpen.value = true;
}

function openOriginDraft(draft: MappingValueRuleDraft) {
  if (!draft.originSourceKey || !draft.originFactName) return;
  emit("open-fact-origin-draft", draft.originSourceKey, draft.originFactName);
  editorOpen.value = true;
}

function closeBatch() {
  fileError.value = "";
  emit("clear-import");
  batchOpen.value = false;
}

function updateDataType(event: Event) {
  emit("update-draft", { dataType: (event.target as HTMLSelectElement).value as MappingValueRuleDraft["dataType"] });
}

async function saveFile(file: ReturnType<typeof createMappingValueRuleExportFile>) {
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
  void saveFile(createMappingConfigurationTemplateFile("mappingValueRules", format));
}

function exportRules(format: MappingConfigurationFileFormat) {
  void saveFile(createMappingValueRuleExportFile(format, props.configurations));
}

async function importFile(file: File) {
  try {
    fileError.value = "";
    emit("preview-import", await parseMappingConfigurationFile("mappingValueRules", file));
  } catch (error) {
    fileError.value = String(error);
  }
}

function remove(rule: MappingValueRuleConfiguration) {
  if (globalThis.confirm(props.labels.mappingValueRuleDeleteConfirm.replace("{name}", rule.name))) emit("remove", rule.id);
}

function draftKey(sourceKey: string | null, factName: string | null) {
  return sourceKey && factName ? `${sourceKey}\u0000${factName}` : "";
}

function isDraftSelected(draft: MappingValueRuleDraft) {
  return selectedDraftKeys.value.includes(draftKey(draft.originSourceKey, draft.originFactName));
}

function toggleDraft(draft: MappingValueRuleDraft, selected: boolean) {
  const key = draftKey(draft.originSourceKey, draft.originFactName);
  if (!key) return;
  const selectedKeys = new Set(selectedDraftKeys.value);
  if (selected) selectedKeys.add(key);
  else selectedKeys.delete(key);
  selectedDraftKeys.value = [...selectedKeys];
}

function toggleAllDrafts(selected: boolean) {
  selectedDraftKeys.value = selected ? [...selectableDraftKeys.value] : [];
}

function requestDraftRemoval(drafts: FactOriginDraftIdentity[]) {
  if (!drafts.length) return;
  pendingDraftRemovals.value = drafts;
}

function requestSingleDraftRemoval(draft: MappingValueRuleDraft) {
  if (!draft.originSourceKey || !draft.originFactName) return;
  requestDraftRemoval([{ sourceKey: draft.originSourceKey, factName: draft.originFactName }]);
}

function requestSelectedDraftRemoval() {
  requestDraftRemoval(props.factOriginDrafts.flatMap((draft) => (
    isDraftSelected(draft) && draft.originSourceKey && draft.originFactName
      ? [{ sourceKey: draft.originSourceKey, factName: draft.originFactName }]
      : []
  )));
}

function confirmDraftRemoval() {
  if (!pendingDraftRemovals.value.length) return;
  const drafts = [...pendingDraftRemovals.value];
  pendingDraftRemovals.value = [];
  selectedDraftKeys.value = selectedDraftKeys.value.filter((key) => !drafts.some((draft) => key === draftKey(draft.sourceKey, draft.factName)));
  if (drafts.length === 1) emit("remove-fact-origin-draft", drafts[0].sourceKey, drafts[0].factName);
  else emit("remove-fact-origin-drafts", drafts);
}

function originLabel(rule: MappingValueRuleDraft | MappingValueRuleConfiguration) {
  return rule.originSourceKey && rule.originFactName
    ? `${rule.originSourceKey} / ${rule.originFactName}`
    : "—";
}

function presetState(rule: MappingValueRuleDraft | MappingValueRuleConfiguration) {
  const values = "values" in rule ? rule.values : JSON.parse(rule.valuesJson) as unknown[];
  return values.length === 0 ? props.labels.mappingValueRulePending : props.labels.mappingValueRuleSavedState;
}

function draftState() {
  return props.labels.mappingValueRuleDraft;
}
</script>

<template>
  <div class="mapping-page-stack mapping-value-rules-stack">
    <section class="panel">
      <header class="panel-header"><div><p class="panel-kicker">{{ labels.mappingBackendConfiguration }}</p><h2>{{ labels.mappingValueRulesTitle }}</h2></div><span class="status-pill">{{ labels.mappingValueRulePreset }}</span></header>
      <p>{{ labels.mappingValueRulesHint }}</p>
      <div class="action-row">
        <button class="secondary-action" type="button" :disabled="!enabled || busy" @click="emit('load-saved-facts')">{{ labels.mappingValueRulesLoadSavedFacts }}</button>
        <button class="danger-action" type="button" :disabled="!enabled || busy || !selectedDraftKeys.length" @click="requestSelectedDraftRemoval">{{ labels.mappingValueRuleRemoveSelectedDrafts.replace('{count}', String(selectedDraftKeys.length)) }}</button>
        <button class="secondary-action" type="button" :disabled="!enabled || busy" @click="batchOpen = true">{{ labels.mappingBatchOperations }}</button>
        <button class="primary-action" type="button" :disabled="!enabled || busy" @click="startCreate">{{ labels.mappingValueRuleNewGeneric }}</button>
      </div>
      <p v-if="displayedError" class="warning">{{ displayedError }}</p>
      <p v-if="status === 'saved'" class="notice">{{ labels.mappingValueRuleSaved }}</p>
    </section>

    <section class="panel">
      <header class="panel-header"><div><p class="panel-kicker">{{ labels.mappingBackendConfiguration }}</p><h2>{{ labels.mappingValueRulesListTitle }}</h2></div></header>
      <div class="table-scroll mapping-list-scroll" tabindex="0"><table class="mapping-list-table mapping-value-rules-table"><thead><tr><th><input :aria-label="labels.mappingValueRuleSelectAll" :checked="allDraftsSelected" :disabled="!enabled || busy || !factOriginDrafts.length" :indeterminate="draftSelectionIndeterminate" type="checkbox" @change="toggleAllDrafts(($event.target as HTMLInputElement).checked)" /></th><th>{{ labels.mappingValueRuleState }}</th><th>{{ labels.mappingValueRuleKey }}</th><th>{{ labels.targetApiName }}</th><th>{{ labels.mappingValueRuleOrigin }}</th><th>{{ labels.collectionFactsDataType }}</th><th>{{ labels.mappingValueRuleValues }}</th><th>{{ labels.targetApiState }}</th><th>{{ labels.targetApiActions }}</th></tr></thead>
        <tbody>
          <tr v-for="pending in factOriginDrafts" :key="`${pending.originSourceKey}/${pending.originFactName}`"><td><input type="checkbox" :checked="isDraftSelected(pending)" :disabled="!enabled || busy" @change="toggleDraft(pending, ($event.target as HTMLInputElement).checked)" /></td><td>{{ draftState() }}</td><td>—</td><td>{{ pending.name }}</td><td><code>{{ originLabel(pending) }}</code></td><td>{{ pending.dataType }}</td><td><code>{{ pending.valuesJson }}</code></td><td>{{ presetState(pending) }}</td><td><div class="mapping-list-row-actions"><button class="secondary-action" type="button" :disabled="!enabled || busy" @click="openOriginDraft(pending)">{{ labels.mappingValueRuleConfigure }}</button><button class="danger-action" type="button" :disabled="!enabled || busy" @click="requestSingleDraftRemoval(pending)">{{ labels.mappingValueRuleRemoveDraft }}</button></div></td></tr>
          <tr v-for="rule in configurations" :key="rule.id"><td>—</td><td>{{ presetState(rule) }}</td><td><code>{{ rule.valueRuleKey }}</code></td><td>{{ rule.name }}</td><td><code>{{ originLabel(rule) }}</code></td><td>{{ rule.dataType }}</td><td><code>{{ JSON.stringify(rule.values) }}</code></td><td>{{ rule.enabled ? labels.targetApiEnabled : labels.targetApiDisabled }}</td><td><div class="mapping-list-row-actions"><button class="secondary-action" type="button" :disabled="!enabled || busy" @click="openEditor(rule.id)">{{ labels.targetApiEdit }}</button><button class="danger-action" type="button" :disabled="!enabled || busy" @click="remove(rule)">{{ labels.targetApiDelete }}</button></div></td></tr>
        </tbody>
      </table></div>
      <p v-if="!configurations.length && !factOriginDrafts.length" class="empty-state">{{ labels.mappingValueRulesEmpty }}</p>
    </section>

    <div v-if="pendingDraftRemovals.length" class="facts-dialog-backdrop" @click.self="pendingDraftRemovals = []">
      <section class="panel facts-dialog mapping-value-rule-delete-dialog" role="alertdialog" aria-modal="true" aria-labelledby="mapping-value-rule-draft-remove-confirm-title">
        <header class="panel-header facts-dialog-header"><div><p class="panel-kicker">{{ labels.mappingValueRulePreset }}</p><h2 id="mapping-value-rule-draft-remove-confirm-title">{{ labels.mappingValueRuleRemoveDraftConfirmTitle }}</h2></div></header>
        <p>{{ labels.mappingValueRuleRemoveDraftConfirm.replace('{count}', String(pendingDraftRemovals.length)) }}</p>
        <div class="action-row facts-editor-actions"><button class="secondary-action" type="button" :disabled="busy" @click="pendingDraftRemovals = []">{{ labels.collectionFactsCancel }}</button><button class="danger-action" type="button" :disabled="!enabled || busy" @click="confirmDraftRemoval">{{ labels.mappingValueRuleRemoveDraft }}</button></div>
      </section>
    </div>

    <div v-if="editorOpen" class="facts-dialog-backdrop" @click.self="editorOpen = false">
      <section class="panel facts-dialog mapping-value-rule-dialog" role="dialog" aria-modal="true">
        <header class="panel-header facts-dialog-header"><div><p class="panel-kicker">{{ labels.mappingValueRulePreset }}</p><h2>{{ selectedId || isOriginDraft ? labels.mappingValueRuleEdit : labels.mappingValueRuleNewGeneric }}</h2></div></header>
        <form class="mapping-value-rule-form" @submit.prevent="emit('save')">
          <div class="form-grid">
            <label class="field"><span>{{ labels.mappingValueRuleKey }}</span><input :value="draft.valueRuleKey ?? labels.mappingValueRuleGeneratedKey" :readonly="Boolean(selectedId) || isOriginDraft" :disabled="!enabled || busy || isOriginDraft" @input="emit('update-draft', { valueRuleKey: ($event.target as HTMLInputElement).value })" /></label>
            <label class="field"><span>{{ labels.targetApiName }}</span><input :value="draft.name" :disabled="!enabled || busy" @input="emit('update-draft', { name: ($event.target as HTMLInputElement).value })" /></label>
            <label class="field"><span>{{ labels.collectionFactsDataType }}</span><select :value="draft.dataType" :disabled="!enabled || busy || Boolean(draft.originSourceKey)" @change="updateDataType"><option v-for="dataType in ['string', 'integer', 'number', 'boolean', 'datetime']" :key="dataType" :value="dataType">{{ dataType }}</option></select></label>
            <label class="check-field"><input :checked="draft.enabled" type="checkbox" :disabled="!enabled || busy" @change="emit('update-draft', { enabled: ($event.target as HTMLInputElement).checked })" /><span>{{ labels.targetApiEnabled }}</span></label>
          </div>
          <p v-if="draft.originSourceKey && draft.originFactName" class="hint">{{ labels.mappingValueRuleOrigin }}: <code>{{ draft.originSourceKey }} / {{ draft.originFactName }}</code></p>
          <label class="field"><span>{{ labels.mappingValueRuleValues }}</span><textarea :value="draft.valuesJson" rows="8" spellcheck="false" :disabled="!enabled || busy" @input="emit('update-draft', { valuesJson: ($event.target as HTMLTextAreaElement).value })" /></label>
          <p class="hint">{{ labels.mappingValueRuleEmptyValuesHint }}</p>
          <div class="action-row facts-editor-actions"><button class="secondary-action" type="button" :disabled="busy" @click="editorOpen = false">{{ labels.collectionFactsCancel }}</button><button class="primary-action" type="submit" :disabled="!enabled || busy">{{ labels.targetApiSave }}</button></div>
        </form>
      </section>
    </div>

    <MappingBatchOperationsDialog v-if="batchOpen" :labels="labels" :title="labels.mappingValueRulesBatchTitle" :busy="busy" :saving-file="savingFile" :preview="importPreview" :error="fileError || error" :enabled="enabled" @close="closeBatch" @download-template="downloadTemplate" @export="exportRules" @import="importFile" @apply="emit('apply-import')" />
  </div>
</template>

<style scoped>
.mapping-value-rules-table { min-width: 1180px; }
.mapping-value-rules-table td { vertical-align: top; white-space: normal; }
.mapping-value-rules-table td code { white-space: normal; overflow-wrap: anywhere; }
.mapping-value-rule-dialog { max-width: min(900px, calc(100vw - 32px)); }
.mapping-value-rule-delete-dialog { max-width: min(480px, calc(100vw - 32px)); }
.mapping-value-rule-form { display: grid; gap: 16px; }
.mapping-value-rule-form textarea { width: 100%; font: 12px/1.5 "SFMono-Regular", Consolas, monospace; }
</style>
