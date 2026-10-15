<!--
File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/components/TwinJsonContractPanel.vue
Description: Data Workspace composition for Fact Table, Simulation, API-first Mapping configuration, and three runtime surfaces.
Main Features: Coordinates app-open runtime preferences after defaults/profile readiness while keeping facts and saved configuration backend-first.
-->
<script setup lang="ts">
import { onMounted, watch } from "vue";

import type { LocaleMessages } from "../../../locales";
import type { AppPage } from "../../navigation";
import type { CollectionFactFileFormat, CollectionFactValueInput } from "../types";
import { useCollectionFactsStore } from "../store/collectionFacts";
import { useApiMaterialsStore } from "../store/apiMaterials";
import { useMappingConfigurationsStore } from "../store/mappingConfigurations";
import { useMappingValueRulesStore } from "../store/mappingValueRules";
import { useApiFirstMappingRuntimeStore } from "../store/apiFirstMappingRuntime";
import { useSingleFactRuntimeStore } from "../store/singleFactRuntime";
import { useTargetApiConfigurationStore } from "../store/targetApiConfiguration";
import { externalIoEnabled } from "../../connection/api";
import { saveCollectionFactFile } from "../api";
import ApiMaterialsPanel from "./ApiMaterialsPanel.vue";
import ApiFirstMappingRuntimePanel from "./ApiFirstMappingRuntimePanel.vue";
import FactsTablePanel from "./FactsTablePanel.vue";
import MappingConfigurationsPanel from "./MappingConfigurationsPanel.vue";
import MappingValueRulesPanel from "./MappingValueRulesPanel.vue";
import SingleFactRuntimePanel from "./SingleFactRuntimePanel.vue";
import TargetApiConfigurationPanel from "./TargetApiConfigurationPanel.vue";
import { createValueExportFile } from "../utils/collectionFactFiles";

const props = defineProps<{ labels: LocaleMessages; enabled: boolean; page: AppPage; view: string }>();
const collection = useCollectionFactsStore();
const apiMaterials = useApiMaterialsStore();
const mappingConfigurations = useMappingConfigurationsStore();
const mappingValueRules = useMappingValueRulesStore();
const runtime = useSingleFactRuntimeStore(() => collection.sourceKey.value);
const apiFirstMappingRuntime = useApiFirstMappingRuntimeStore();
const targetApis = useTargetApiConfigurationStore();

async function run(operation: () => Promise<void>) {
  try {
    await operation();
  } catch {
    // Each store retains its stable backend or Rust error without replacing editor text.
  }
}

async function refreshSimulationPoints() {
  await runtime.loadSimulationPoints();
}

async function loadSource(sourceKey: string) {
  collection.setSourceKey(sourceKey);
  await collection.load();
  await refreshSimulationPoints();
}

async function applyContract() {
  await collection.applyPendingContract();
  await refreshSimulationPoints();
}

async function updateValues(values: CollectionFactValueInput[]) {
  await collection.updateValues(values);
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

onMounted(() => {
  if (!props.enabled) return;
  if (!externalIoEnabled()) {
    runtime.startPolling();
    apiFirstMappingRuntime.startPolling();
    void runtime.loadStartupPreferences().catch(() => {});
    return;
  }
  void run(async () => {
    await Promise.all([
      collection.load(),
      targetApis.load(),
      mappingValueRules.load(),
    ]);
    await refreshSimulationPoints();
    runtime.startPolling();
    apiFirstMappingRuntime.startPolling();
    try {
      await runtime.loadStartupPreferences();
    } catch {
      // Preference failure remains visible without preventing independent manual runtimes.
    }
    const simulationSourceKey = runtime.autoStartSimulationSourceKey();
    if (simulationSourceKey && simulationSourceKey !== collection.sourceKey.value) {
      try {
        await loadSource(simulationSourceKey);
      } catch {
        // Simulation start will show its own source/configuration error below.
      }
    }
    await Promise.allSettled([
      runtime.autoStartSimulationIfEnabled(),
      apiFirstMappingRuntime.autoStartIfEnabled(
        runtime.runtimeStartupPreferences.value.runtimeAutoStart.apiMappingRuntime.enabled,
      ),
    ]);
  });
});
</script>

<template>
  <div v-show="page === 'twinFacts'" class="single-fact-workspace-stack">
    <!-- TSS-012 replaces CollectionFactsContractEditor and CollectionFactInspector with the table-first workspace. -->
    <FactsTablePanel
      v-show="view === 'contract'"
      :labels="labels"
      :source-key="collection.sourceKey.value"
      :contract="collection.contract.value"
      :pending-preview="collection.pendingPreview.value"
      :preview-needs-confirmation="collection.previewNeedsConfirmation.value"
      :query="collection.query.value"
      :result="collection.factPage.value"
      :contract-busy="collection.contractBusy.value"
      :table-busy="collection.inspectorBusy.value"
      :values-busy="collection.valuesBusy.value"
      :status="collection.status.value"
      :error="collection.error.value"
      :enabled="enabled"
      @load-source="run(() => loadSource($event))"
      @query="run(() => collection.updateQuery($event))"
      @preview-contract="run(() => collection.previewContract($event))"
      @apply-contract="run(applyContract)"
      @discard-preview="collection.discardPendingContract"
      @update-values="run(() => updateValues($event))"
      @export-values="exportValues"
    />
    <SingleFactRuntimePanel
      v-show="view === 'inspector'"
      :labels="labels"
      :source-key="collection.sourceKey.value"
      :points="runtime.simulationPoints.value"
      :enabled-point-count="runtime.enabledPointCount.value"
      :points-valid="runtime.pointsValid.value"
      :points-busy="runtime.pointsBusy.value"
      :simulation="runtime.simulation.value"
      :simulation-busy="runtime.simulationBusy.value"
      :simulation-settings-busy="runtime.simulationSettingsBusy.value"
      :simulation-settings-dirty="runtime.simulationSettingsDirty.value"
      :simulation-auto-start-enabled="runtime.runtimeStartupPreferences.value.runtimeAutoStart.collectionFactSimulation.enabled"
      :runtime-startup-busy="runtime.runtimeStartupBusy.value"
      :enabled="enabled"
      view="simulation"
      @update:point-values="runtime.updatePointValues"
      @update:point-interval="runtime.updatePointInterval"
      @update:point-current-time="runtime.updatePointCurrentTime"
      @save-simulation-settings="run(runtime.saveSimulationSettings)"
      @update:simulation-auto-start="run(() => runtime.setSimulationAutoStart($event))"
      @simulation-action="run(() => runtime.simulationAction($event))"
    />
    <p v-if="view === 'inspector' && runtime.simulationError.value" class="warning">{{ runtime.simulationError.value }}</p>
    <p v-if="view === 'inspector' && runtime.runtimeStartupError.value" class="warning">{{ runtime.runtimeStartupError.value }}</p>
  </div>

  <div v-show="page === 'mappingIdentity'">
    <ApiMaterialsPanel
      v-show="view === 'apiMaterials'"
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
      @reload="run(apiMaterials.load)"
      @save="run(apiMaterials.save)"
      @toggle="apiMaterials.toggle"
    />
    <TargetApiConfigurationPanel
      v-show="view === 'targetApis'"
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
    <MappingValueRulesPanel
      v-show="view === 'valueRules'"
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
    <MappingConfigurationsPanel
      v-show="view === 'mappings'"
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

  <div v-show="page === 'simulationRuntime'">
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
.single-fact-workspace-stack { display: grid; gap: 16px; }
</style>
