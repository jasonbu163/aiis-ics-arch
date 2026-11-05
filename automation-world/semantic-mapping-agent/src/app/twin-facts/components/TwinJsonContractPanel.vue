<!--
File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/components/TwinJsonContractPanel.vue
Description: Data Workspace composition for read-only source facts, API-first Mapping configuration, and HTTP runtime.
Main Features: Coordinates app-open runtime preferences after defaults/profile readiness while keeping facts and saved configuration backend-first.
-->
<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import type { LocaleMessages } from "../../../locales";
import type { AppPage } from "../../navigation";
import type { CollectionFactFileFormat } from "../types";
import { useCollectionFactsStore } from "../store/collectionFacts";
import { useApiMaterialsStore } from "../store/apiMaterials";
import { useMappingConfigurationsStore } from "../store/mappingConfigurations";
import { useMappingValueRulesStore } from "../store/mappingValueRules";
import { useApiFirstMappingRuntimeStore } from "../store/apiFirstMappingRuntime";
import { useMappingStartupStore } from "../store/mappingStartup";
import { useTargetApiConfigurationStore } from "../store/targetApiConfiguration";
import { ConsoleCard, ConsoleActionButton } from "@aw-ui";
import { localConfiguration, previewConfiguration, applyConfiguration, exportConfiguration, type LocalImportPreview, type ChangeIntent } from "../api/localConfiguration";
import { formatBusinessTime } from "../../../console/time";
import { saveCollectionFactFile } from "../api";
import ApiMaterialsPanel from "./ApiMaterialsPanel.vue";
import ApiFirstMappingRuntimePanel from "./ApiFirstMappingRuntimePanel.vue";
import FactsTablePanel from "./FactsTablePanel.vue";
import MappingConfigurationsPanel from "./MappingConfigurationsPanel.vue";
import MappingValueRulesPanel from "./MappingValueRulesPanel.vue";
import TargetApiConfigurationPanel from "./TargetApiConfigurationPanel.vue";
import { createValueExportFile } from "../utils/collectionFactFiles";

const props = defineProps<{ labels: LocaleMessages; enabled: boolean; page: AppPage; view: string }>();
const collection = useCollectionFactsStore();
const apiMaterials = useApiMaterialsStore();
const mappingConfigurations = useMappingConfigurationsStore();
const mappingValueRules = useMappingValueRulesStore();
const runtime = useMappingStartupStore();
const apiFirstMappingRuntime = useApiFirstMappingRuntimeStore();
const targetApis = useTargetApiConfigurationStore();

async function run(operation: () => Promise<void>) {
  try {
    await operation();
  } catch {
    // Each store retains its stable backend or Rust error without replacing editor text.
  }
}

async function loadSource(sourceKey: string) {
  collection.setSourceKey(sourceKey);
  await collection.load();
}

async function exportValues(format: CollectionFactFileFormat, complete: (failed: boolean) => void) {
  try {
    const facts = await collection.listAllFacts();
    await saveCollectionFactFile(createValueExportFile(format, collection.sourceKey.value, facts));
    complete(false);
  } catch {
    complete(true);
  }
}

watch(
  () => [props.enabled, props.page, props.view] as const,
  ([enabled, page, view]) => {
    if (!enabled || page !== "mappingIdentity" || view !== "mappings") return;
    void run(mappingConfigurations.load);
  },
  { immediate: true },
);

const backupError = ref("");
const backupBusy = ref(false);
const restorePreview = ref<LocalImportPreview | null>(null);
const restoreFileInput = ref<HTMLInputElement | null>(null);
const restoreFileName = ref("");
const restoreConfirmed = ref(false);
let restoreIntent: ChangeIntent | null = null;
const configurationTime = computed(() => formatBusinessTime(localConfiguration.value?.updatedAt));
async function exportBackup() {
  backupBusy.value = true; backupError.value = "";
  try { const json = await exportConfiguration(); await saveCollectionFactFile({ fileName: "sma-configuration.json", mimeType: "application/json;charset=utf-8", contents: new TextEncoder().encode(json) }); }
  catch (error) { backupError.value = String(error); } finally { backupBusy.value = false; }
}
function chooseRestoreFile() { restoreFileInput.value?.click(); }
async function previewRestore(event: Event) {
  const input = event.target as HTMLInputElement; const file = input.files?.[0]; input.value = "";
  restorePreview.value = null; restoreIntent = null; restoreConfirmed.value = false;
  restoreFileName.value = file?.name ?? "";
  if (!file) return;
  backupBusy.value = true; backupError.value = "";
  try { if (file.size > 10 * 1024 * 1024) throw new Error("SMA_CONFIGURATION_LIMIT_EXCEEDED"); restoreIntent = { kind: "restore", resource: "configuration", id: null, payload: JSON.parse(await file.text()) }; restorePreview.value = await previewConfiguration(restoreIntent); }
  catch (error) { backupError.value = String(error); } finally { backupBusy.value = false; }
}
async function applyRestore() {
  if (!restoreIntent || !restorePreview.value || !restoreConfirmed.value) return;
  backupBusy.value = true; backupError.value = "";
  try { await applyConfiguration(restoreIntent, restorePreview.value, restoreConfirmed.value); restorePreview.value = null; restoreIntent = null; restoreConfirmed.value = false; await Promise.all([apiMaterials.load(), targetApis.load(), mappingValueRules.load(), mappingConfigurations.load()]); }
  catch (error) { backupError.value = String(error); } finally { backupBusy.value = false; }
}
watch(() => [props.enabled, props.page, props.view] as const, ([enabled, page, view]) => {
  if (!enabled || page !== "mappingIdentity") return;
  if (view === "apiMaterials") void run(apiMaterials.load);
  if (view === "targetApis") void run(targetApis.load);
  if (view === "valueRules") void run(mappingValueRules.load);
}, { immediate: true });
onMounted(() => {
  if (!props.enabled) return;
  apiFirstMappingRuntime.startPolling();
  void run(async () => { await runtime.loadStartupPreferences(); await apiFirstMappingRuntime.autoStartIfEnabled(runtime.runtimeStartupPreferences.value.runtimeAutoStart.apiMappingRuntime.enabled); });
});

</script>

<template>
  <div v-show="page === 'twinFacts'" class="single-fact-workspace-stack">
    <FactsTablePanel
      v-show="view === 'contract'"
      :labels="labels"
      :source-key="collection.sourceKey.value"
      :contract="collection.contract.value"
      :query="collection.query.value"
      :result="collection.factPage.value"
      :contract-busy="collection.contractBusy.value"
      :table-busy="collection.inspectorBusy.value"
      :error="collection.error.value"
      :enabled="enabled"
      @load-source="run(() => loadSource($event))"
      @query="run(() => collection.updateQuery($event))"
      @export-values="exportValues"
    />
  </div>

  <div v-show="page === 'mappingIdentity'">
    <ConsoleCard :title="labels.localConfigurationTitle">
      <p>{{ labels.localConfigurationOnly }}</p>
      <p>{{ labels.localConfigurationRevision }} {{ localConfiguration?.revision ?? "—" }} · {{ labels.localConfigurationUpdatedAt }} {{ configurationTime }}</p>
      <div class="action-row"><ConsoleActionButton :disabled="!enabled || backupBusy" @click="exportBackup">{{ labels.localConfigurationBackup }}</ConsoleActionButton><ConsoleActionButton tone="secondary" :disabled="!enabled || backupBusy" @click="chooseRestoreFile">{{ labels.localConfigurationRestore }}</ConsoleActionButton><span class="configuration-file-name" role="status">{{ restoreFileName || labels.localConfigurationNoFileSelected }}</span><input ref="restoreFileInput" class="facts-file-input" type="file" accept=".json,application/json" :disabled="!enabled || backupBusy" @change="previewRestore" /></div>
      <p v-if="backupError" class="warning" role="alert">{{ labels.localConfigurationFailed }} {{ /CONFLICT|PREVIEW_CHANGED/.test(backupError) ? labels.localConfigurationConflict : backupError }}</p>
      <section v-if="restorePreview">
        <p>{{ labels.localConfigurationReplaceWarning }}</p>
        <p>{{ labels.mappingBatchCreated }}: {{ restorePreview.createdKeys.join(', ') || '—' }}</p>
        <p>{{ labels.mappingBatchUpdated }}: {{ restorePreview.updatedKeys.join(', ') || '—' }}</p>
        <p>{{ labels.localConfigurationDeleted }}: {{ restorePreview.deletedKeys.join(', ') || '—' }}</p>
        <p v-for="item in restorePreview.errors" :key="item.errorCode" class="warning">{{ item.key }}: {{ item.errorCode }}</p>
        <label><input v-model="restoreConfirmed" type="checkbox" />{{ labels.localConfigurationRestoreConfirm }}</label>
        <ConsoleActionButton :disabled="!restoreConfirmed || backupBusy || restorePreview.errors.length > 0" @click="applyRestore">{{ labels.mappingBatchApply }}</ConsoleActionButton>
        <ConsoleActionButton tone="secondary" @click="restorePreview = null; restoreConfirmed = false">{{ labels.collectionFactsCancel }}</ConsoleActionButton>
      </section>
    </ConsoleCard>
    <div v-show="view === 'apiMaterials'">
    <ApiMaterialsPanel
      :labels="labels"
      :operations="apiMaterials.operations.value"
      :saved-materials="apiMaterials.savedMaterials.value"
      :selected-identities="apiMaterials.selectedIdentities.value"
      :missing-saved-count="apiMaterials.missingSavedMaterials.value.length"
      :busy="apiMaterials.busy.value || apiMaterials.saving.value"
      :can-save="apiMaterials.canSave.value"
      :result="apiMaterials.result.value"
      :error="apiMaterials.error.value"
      :enabled="enabled"
      @reload="run(() => apiMaterials.previewCatalog())"
      :catalog-preview="apiMaterials.catalogPreview.value"
      :catalog-candidates="apiMaterials.catalogCandidates.value"
      @import-open-api="file => run(() => apiMaterials.previewCatalog(file))"
      @apply-catalog="run(apiMaterials.applyCatalog)"
      @save="run(apiMaterials.save)"
      @toggle="apiMaterials.toggle"
    />
    </div>
    <div v-show="view === 'targetApis'">
    <TargetApiConfigurationPanel
      :labels="labels"
      :configurations="targetApis.configurations.value"
      :draft="targetApis.draft.value"
      :selected-id="targetApis.selectedId.value"
      :api-materials="targetApis.apiMaterials.value"
      :selected-material-keys="targetApis.selectedMaterialKeys.value"
      :loaded-material-keys="targetApis.loadedMaterialKeys.value"
      :material-load-result="targetApis.materialLoadResult.value"
      :busy="targetApis.busy.value"
      :status="targetApis.status.value"
      :error="targetApis.error.value"
      :import-preview="targetApis.importPreview.value"
      :enabled="enabled"
      @load="run(targetApis.load)"
      @start-manual="targetApis.startManual"
      @load-api-materials="run(targetApis.loadApiMaterials)"
      @toggle-material="targetApis.toggleMaterial"
      @import-materials="run(targetApis.loadSelectedMaterials)"
      @open="run(() => targetApis.open($event))"
      @update-draft="targetApis.updateDraft"
      @update-parameter="targetApis.updateParameter"
      @add-parameter="targetApis.addParameter"
      @remove-parameter="targetApis.removeParameter"
      @save="run(targetApis.save)"
      @remove="run(() => targetApis.remove($event))"
      @remove-many="run(() => targetApis.removeMany($event))"
      @preview-import="run(() => targetApis.previewImport($event))"
      @apply-import="run(targetApis.applyImport)"
      @clear-import="targetApis.clearImport"
    />
    </div>
    <div v-show="view === 'valueRules'">
    <MappingValueRulesPanel
      :labels="labels"
      :configurations="mappingValueRules.configurations.value"
      :fact-origin-drafts="mappingValueRules.factOriginDrafts.value"
      :draft="mappingValueRules.draft.value"
      :selected-id="mappingValueRules.selectedId.value"
      :selected-origin-key="mappingValueRules.selectedOriginKey.value"
      :busy="mappingValueRules.busy.value"
      :status="mappingValueRules.status.value"
      :error="mappingValueRules.error.value"
      :import-preview="mappingValueRules.importPreview.value"
      :enabled="enabled"
      @load="run(mappingValueRules.load)"
      @load-saved-facts="run(mappingValueRules.loadSavedFacts)"
      @start-create="mappingValueRules.startCreate"
      @open="mappingValueRules.open($event)"
      @open-fact-origin-draft="(sourceKey, factName) => mappingValueRules.openFactOriginDraft(sourceKey, factName)"
      @remove-fact-origin-draft="(sourceKey, factName) => mappingValueRules.removeFactOriginDraft(sourceKey, factName)"
      @remove-fact-origin-drafts="mappingValueRules.removeFactOriginDrafts($event)"
      @update-draft="mappingValueRules.updateDraft"
      @save="run(mappingValueRules.save)"
      @remove="run(() => mappingValueRules.remove($event))"
      @preview-import="run(() => mappingValueRules.previewImport($event))"
      @apply-import="run(mappingValueRules.applyImport)"
      @clear-import="mappingValueRules.clearImport"
    />
    </div>
    <div v-show="view === 'mappings'">
    <MappingConfigurationsPanel
      :labels="labels"
      :configurations="mappingConfigurations.configurations.value"
      :local-drafts="mappingConfigurations.localDrafts.value"
      :target-apis="mappingConfigurations.targetApis.value"
      :value-rules="mappingConfigurations.valueRules.value"
      :source-facts="mappingConfigurations.sourceFacts.value"
      :draft="mappingConfigurations.draft.value"
      :selected-id="mappingConfigurations.selectedId.value"
      :selected-draft-id="mappingConfigurations.selectedDraftId.value"
      :selected-target-api="mappingConfigurations.selectedTargetApi.value"
      :selected-target-api-locked="mappingConfigurations.selectedTargetApiLocked.value"
      :request-preview="mappingConfigurations.requestPreview.value"
      :saved-preview="mappingConfigurations.savedPreview.value"
      @preview-saved="id => run(() => mappingConfigurations.previewSaved(id))"
      :manual-runs="mappingConfigurations.manualRuns.value"
      :manual-run-busy-ids="mappingConfigurations.manualRunBusyIds.value"
      :busy="mappingConfigurations.busy.value"
      :facts-busy="mappingConfigurations.factsBusy.value"
      :status="mappingConfigurations.status.value"
      :error="mappingConfigurations.error.value"
      :import-preview="mappingConfigurations.importPreview.value"
      :enabled="enabled"
      @load="run(mappingConfigurations.load)"
      @load-target-apis="run(mappingConfigurations.loadTargetApiDrafts)"
      @start-create="mappingConfigurations.startCreate"
      @open="run(() => mappingConfigurations.open($event))"
      @open-draft="run(() => mappingConfigurations.openDraft($event))"
      @remove-draft="mappingConfigurations.removeDraft"
      @load-source-facts="run(mappingConfigurations.loadSourceFacts)"
      @update-draft="mappingConfigurations.updateDraft"
      @initialize-bindings="mappingConfigurations.initializeBindings"
      @update-binding="mappingConfigurations.updateBinding"
      @save="run(mappingConfigurations.save)"
      @remove="run(() => mappingConfigurations.remove($event))"
      @run-manual="run(() => mappingConfigurations.runManual($event))"
      @preview-import="run(() => mappingConfigurations.previewImport($event))"
      @apply-import="run(mappingConfigurations.applyImport)"
      @clear-import="mappingConfigurations.clearImport"
    />
    </div>
  </div>

  <div v-show="page === 'mappingRuntime'">
    <ApiFirstMappingRuntimePanel
      :labels="labels"
      :runtime="apiFirstMappingRuntime.runtime.value"
      :busy="apiFirstMappingRuntime.busy.value"
      :error="apiFirstMappingRuntime.error.value || runtime.runtimeStartupError.value"
      :enabled="enabled"
      :auto-start-enabled="runtime.runtimeStartupPreferences.value.runtimeAutoStart.apiMappingRuntime.enabled"
      :runtime-startup-busy="runtime.runtimeStartupBusy.value"
      @action="run(() => apiFirstMappingRuntime.action($event))"
      @update:auto-start="run(() => runtime.setApiMappingRuntimeAutoStart($event))"
    />

  </div>
</template>

<style scoped>
.configuration-file-name { min-width: 0; overflow-wrap: anywhere; }
.single-fact-workspace-stack { display: grid; gap: 16px; }
</style>
