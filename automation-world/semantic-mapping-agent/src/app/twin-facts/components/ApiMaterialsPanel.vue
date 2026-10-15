<!--
  File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/components/ApiMaterialsPanel.vue
  Description: Persistent all-method OpenAPI API Material selection page.
  Main Features:
    - Shows every standard OpenAPI operation and whether its parameters are ready for direct mapping
    - Filters visible operations by method, keyword, and current selection state
    - Keeps checkbox edits as drafts until Save selection is pressed
    - Shows Backend row existence as the authoritative selected state
-->
<script setup lang="ts">
import { computed, ref } from "vue";
import type { LocaleMessages } from "../../../locales";
import type { BackendOpenApiOperation } from "../../connection/types";
import { apiMaterialIdentity } from "../store/apiMaterials";
import { apiMaterialNormalizationReasonKey, type ApiMaterialConfiguration, type ApiMaterialSelectionResult } from "../types";

const props = defineProps<{
  labels: LocaleMessages;
  operations: BackendOpenApiOperation[];
  savedMaterials: ApiMaterialConfiguration[];
  selectedIdentities: string[];
  missingSavedCount: number;
  busy: boolean;
  canSave: boolean;
  result: ApiMaterialSelectionResult | null;
  error: string;
  enabled: boolean;
}>();

const emit = defineEmits<{
  reload: [];
  save: [];
  toggle: [method: string, path: string, selected: boolean];
}>();

const methodFilter = ref("all");
const keywordFilter = ref("");
const statusFilter = ref("all");
const methodOrder = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "TRACE"];

const availableMethods = computed(() => [...new Set(props.operations.map((operation) => operation.method))]
  .sort((left, right) => methodOrder.indexOf(left) - methodOrder.indexOf(right)));

const filteredOperations = computed(() => {
  const keyword = keywordFilter.value.trim().toLowerCase();
  return props.operations.filter((operation) => {
    if (methodFilter.value !== "all" && operation.method !== methodFilter.value) return false;
    if (statusFilter.value === "selected" && !isSelected(operation)) return false;
    if (statusFilter.value === "notSelected" && isSelected(operation)) return false;
    if (statusFilter.value === "unsupported" && operation.normalizationStatus === "ready") return false;
    if (!keyword) return true;
    const name = operation.summary ?? operation.operationId ?? `${operation.method} ${operation.path}`;
    return [name, operation.path, operation.operationId ?? ""].some((value) => value.toLowerCase().includes(keyword));
  });
});

function isSaved(operation: BackendOpenApiOperation) {
  const identity = apiMaterialIdentity(operation.method, operation.path);
  return props.savedMaterials.some(
    (item) => apiMaterialIdentity(item.httpMethod, item.path) === identity,
  );
}

function isSelected(operation: BackendOpenApiOperation) {
  return props.selectedIdentities.includes(apiMaterialIdentity(operation.method, operation.path));
}

function parameterSummary(operation: BackendOpenApiOperation) {
  if (!operation.requestContract) {
    const parameters = operation.operationSnapshot.parameters;
    return Array.isArray(parameters)
      ? parameters.filter((item) => item && typeof item === "object" && item.in === "path")
        .map((item) => `path:${item.name}`).join(" · ") || "—"
      : "—";
  }
  const counts = Object.fromEntries(["body", "query", "path", "header"].map((location) => [
    location,
    operation.requestContract?.filter((item) => item.location === location).length ?? 0,
  ]));
  return `B ${counts.body} · Q ${counts.query} · P ${counts.path} · H ${counts.header}`;
}

function normalizationReason(errorCode: string | null) {
  return props.labels[apiMaterialNormalizationReasonKey(errorCode)];
}
</script>

<template>
  <div class="mapping-page-stack api-materials-stack">
    <p>{{ labels.targetApiPartUnionHint }}</p>
    <section class="panel">
      <header class="panel-header">
        <div><p class="panel-kicker">OpenAPI</p><h2>{{ labels.apiMaterialsTitle }}</h2></div>
        <span class="status-pill">OpenAPI · HTTP</span>
      </header>
      <p>{{ labels.apiMaterialsHint }}</p>
      <div class="action-row api-materials-actions">
        <button class="secondary-action" type="button" :disabled="!enabled || busy" @click="emit('reload')">{{ labels.apiMaterialsReload }}</button>
        <button class="primary-action" type="button" :disabled="!enabled || busy || !canSave" @click="emit('save')">{{ labels.apiMaterialsSaveSelection }}</button>
      </div>
      <p v-if="missingSavedCount" class="warning">{{ labels.apiMaterialsMissingWarning.replace('{count}', String(missingSavedCount)) }}</p>
      <p v-if="result" class="notice">{{ labels.apiMaterialsSaveResult.replace('{created}', String(result.created)).replace('{updated}', String(result.updated)).replace('{unchanged}', String(result.unchanged)).replace('{removed}', String(result.removed)) }}</p>
      <p v-if="error" class="warning">{{ labels.apiMaterialsOperationFailed }}</p>
    </section>

    <section class="panel">
      <header class="panel-header"><div><p class="panel-kicker">{{ labels.apiMaterialsSourceOpenApi }}</p><h2>{{ labels.apiMaterialsCandidatesTitle }}</h2></div></header>
      <div v-if="operations.length" class="api-materials-filters">
        <label>
          <span>{{ labels.apiMaterialsFilterMethod }}</span>
          <select v-model="methodFilter">
            <option value="all">{{ labels.apiMaterialsFilterAllMethods }}</option>
            <option v-for="method in availableMethods" :key="method" :value="method">{{ method }}</option>
          </select>
        </label>
        <label class="api-materials-keyword-filter">
          <span>{{ labels.apiMaterialsFilterKeyword }}</span>
          <input v-model="keywordFilter" type="search" :placeholder="labels.apiMaterialsFilterKeywordPlaceholder" />
        </label>
        <label>
          <span>{{ labels.apiMaterialsFilterStatus }}</span>
          <select v-model="statusFilter">
            <option value="all">{{ labels.apiMaterialsFilterAllStatuses }}</option>
            <option value="selected">{{ labels.apiMaterialsSelected }}</option>
            <option value="notSelected">{{ labels.apiMaterialsNotSelected }}</option>
            <option value="unsupported">{{ labels.apiMaterialsFilterUnsupported }}</option>
          </select>
        </label>
        <p class="api-materials-filter-count">{{ labels.apiMaterialsFilterResult.replace('{count}', String(filteredOperations.length)) }}</p>
      </div>
      <div v-if="filteredOperations.length" class="table-scroll mapping-list-scroll" tabindex="0">
        <table class="api-materials-table">
          <thead><tr><th>{{ labels.apiMaterialsUse }}</th><th>{{ labels.apiMaterialsMethod }}</th><th>{{ labels.targetApiName }}</th><th>{{ labels.targetApiPath }}</th><th>{{ labels.targetApiOperationId }}</th><th>{{ labels.apiMaterialsParameters }}</th><th>{{ labels.apiMaterialsSource }}</th><th>{{ labels.apiMaterialsLoadability }}</th><th>{{ labels.apiMaterialsSelectionState }}</th></tr></thead>
          <tbody>
            <tr v-for="operation in filteredOperations" :key="apiMaterialIdentity(operation.method, operation.path)">
              <td><input type="checkbox" :checked="isSelected(operation)" :disabled="!enabled || busy" @change="emit('toggle', operation.method, operation.path, ($event.target as HTMLInputElement).checked)" /></td>
              <td><span class="status-pill">{{ operation.method }}</span></td>
              <td>{{ operation.summary ?? operation.operationId ?? `${operation.method} ${operation.path}` }}</td>
              <td><code>{{ operation.path }}</code></td>
              <td><code>{{ operation.operationId ?? "—" }}</code></td>
              <td>{{ parameterSummary(operation) }}</td>
              <td>{{ labels.apiMaterialsSourceOpenApi }}</td>
              <td>{{ operation.normalizationStatus === 'ready' ? labels.apiMaterialsReady : labels.apiMaterialsUnsupported.replace('{reason}', normalizationReason(operation.normalizationErrorCode)) }}</td>
              <td>{{ isSaved(operation) ? labels.apiMaterialsSelected : labels.apiMaterialsNotSelected }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else-if="operations.length" class="empty-state">{{ labels.apiMaterialsFilterNoMatches }}</p>
      <p v-else class="empty-state">{{ labels.apiMaterialsEmpty }}</p>
    </section>
  </div>
</template>

<style scoped>
.api-materials-actions { margin-top: 16px; }
.api-materials-filters { display: grid; grid-template-columns: auto minmax(220px, 1fr) auto auto; align-items: end; gap: 12px; margin: 16px 0; }
.api-materials-filters label { display: grid; gap: 6px; color: #3d535b; font-size: 12px; font-weight: 650; }
.api-materials-filters select, .api-materials-filters input { min-width: 0; }
.api-materials-filter-count { margin: 0 0 7px; color: #52707a; font-size: 12px; white-space: nowrap; }
.api-materials-table { min-width: 1440px; }
.api-materials-table td { vertical-align: top; white-space: normal; }
.api-materials-table code { overflow-wrap: anywhere; }
@media (max-width: 760px) {
  .api-materials-filters { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .api-materials-keyword-filter { grid-column: 1 / -1; }
  .api-materials-filter-count { grid-column: 1 / -1; margin-bottom: 0; }
}
</style>
