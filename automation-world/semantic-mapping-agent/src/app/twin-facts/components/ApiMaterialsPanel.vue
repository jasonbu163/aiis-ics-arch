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
import { useTableWidths, vTableWidths } from "../../../console/tableWidths";
import { ConsoleCard, ConsoleActionButton, StatusCapsule, type CardHeaderStatus } from "@aw-ui";
import { Refresh } from "@element-plus/icons-vue";
import { computed, ref } from "vue";
import type { LocalImportPreview } from "../api/localConfiguration";
import type { LocaleMessages } from "../../../locales";
import type { BackendOpenApiOperation } from "../../connection/types";
import { apiMaterialIdentity } from "../store/apiMaterials";
import { apiMaterialNormalizationReasonKey, type ApiMaterialConfiguration, type ApiMaterialSelectionResult } from "../types";

const props = defineProps<{
  labels: LocaleMessages;
  catalogPreview?: LocalImportPreview | null;
  catalogCandidates?: BackendOpenApiOperation[];
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
  "import-open-api": [file: File];
  "apply-catalog": [];
  save: [];
  toggle: [method: string, path: string, selected: boolean];
}>();

const openApiFileInput = ref<HTMLInputElement | null>(null);
const openApiFileName = ref("");
function chooseOpenApiFile() { openApiFileInput.value?.click(); }
function importOpenApiFile(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0]; input.value = "";
  openApiFileName.value = file?.name ?? "";
  if (file) emit("import-open-api", file);
}
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

const materialsTable = useTableWidths("api-materials", [{ id: "select", width: 64, min: 64, fixed: true }, { id: "method", width: 100 }, { id: "name", width: 220 }, { id: "path", width: 250 }, { id: "operationId", width: 180 }, { id: "parameters", width: 180 }, { id: "source", width: 180 }, { id: "loadability", width: 220 }, { id: "selected", width: 180 }]);

const headerStatuses = computed<CardHeaderStatus[]>(() => {
  const { labels, selectedIdentities, savedMaterials } = props;
  const saved = new Set(savedMaterials.map(item => apiMaterialIdentity(item.httpMethod, item.path)));
  const dirty = selectedIdentities.length !== saved.size || selectedIdentities.some(id => !saved.has(id));
  const entries: CardHeaderStatus[] = [];
  if (props.busy) entries.push({ id: "working", label: labels.loading });
  if (props.catalogPreview) entries.push({ id: "preview", label: labels.catalogPreviewPending, tone: "warning" });
  entries.push(dirty
    ? { id: "selection", label: labels.selectionPending, tone: "warning" }
    : { id: "selection", label: labels.savedItemCount.replace("{count}", String(saved.size)), tone: "success" });
  entries.push({ id: "catalog", label: labels.localCatalogCount.replace("{count}", String(props.operations.length)) });
  return entries;
});
</script>

<template>
  <div class="mapping-page-stack api-materials-stack">
    <ConsoleCard :title="labels.apiMaterialsTitle" :header-statuses="headerStatuses" :status-overflow-label="labels.moreCardStatuses" :help="labels.apiMaterialsHint + '\n' + labels.targetApiPartUnionHint" :help-label="labels.apiMaterialsTitle + labels.cardHelpSuffix" help-append-to="#sma-overlays">
      <template #actions>
        <ConsoleActionButton tone="secondary" :disabled="!enabled || busy" @click="chooseOpenApiFile">{{ labels.localOpenApiImport }}</ConsoleActionButton>
        <ConsoleActionButton tone="primary" native-type="button" :disabled="!enabled || busy || !canSave" @click="emit('save')">{{ labels.apiMaterialsSaveSelection }}</ConsoleActionButton>
      </template>
      <template #refresh>
        <ConsoleActionButton tone="secondary" native-type="button" :icon="Refresh" :title="labels.apiMaterialsReload" :aria-label="labels.apiMaterialsReload" :disabled="!enabled || busy" @click="emit('reload')">{{ labels.refresh }}</ConsoleActionButton>
      </template>
      <p class="configuration-file-name" role="status">{{ openApiFileName || labels.localConfigurationNoFileSelected }}</p>
      <input ref="openApiFileInput" class="facts-file-input" type="file" accept=".json,application/json" :disabled="!enabled || busy" @change="importOpenApiFile" />
      <p v-if="result" class="notice" role="status">{{ labels.apiMaterialsSaveResult.replace('{created}', String(result.created)).replace('{updated}', String(result.updated)).replace('{unchanged}', String(result.unchanged)).replace('{removed}', String(result.removed)) }}</p>
      <section v-if="catalogPreview">
        <p>{{ labels.localOpenApiPreview }} · {{ labels.mappingBatchErrors }}: {{ catalogPreview.errors.length }}</p>
        <ul><li v-for="operation in catalogCandidates" :key="`${operation.method} ${operation.path}`"><code>{{ operation.method }} {{ operation.path }}</code> · {{ operation.summary }} · {{ operation.normalizationStatus === "ready" ? labels.apiMaterialsReady : labels.apiMaterialsUnsupported.replace("{reason}", normalizationReason(operation.normalizationErrorCode)) }}</li></ul>
        <p v-for="item in catalogPreview.errors" :key="item.errorCode" class="warning">{{ item.errorCode }}</p>
        <ConsoleActionButton :disabled="busy || catalogPreview.errors.length > 0" @click="emit('apply-catalog')">{{ labels.mappingBatchApply }}</ConsoleActionButton>
      </section>
      <p v-if="missingSavedCount" class="warning" role="alert">{{ labels.apiMaterialsMissingWarning.replace('{count}', String(missingSavedCount)) }}</p>
      <p v-if="error" class="warning" role="alert">{{ labels.apiMaterialsOperationFailed }} {{ /CONFLICT|PREVIEW_CHANGED/.test(error) ? labels.localConfigurationConflict : error }}</p>
    </ConsoleCard>

    <ConsoleCard :title="labels.apiMaterialsCandidatesTitle" :help="labels.apiMaterialsListHelp" :help-label="labels.apiMaterialsCandidatesTitle + labels.cardHelpSuffix" help-append-to="#sma-overlays">
      <template #actions>
        <ConsoleActionButton size="small" @click="materialsTable.reset" :title="labels.resetTableWidthsHelp">{{ labels.resetTableWidths }}</ConsoleActionButton>
      </template>
      <template v-if="operations.length" #tools>
        <div class="api-materials-filters">
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
      </template>
      <div v-if="filteredOperations.length" class="table-scroll mapping-list-scroll" tabindex="0">
        <table v-table-widths="[materialsTable, labels.resizeTableColumn]" class="api-materials-table">
          <thead><tr><th>{{ labels.apiMaterialsUse }}</th><th>{{ labels.apiMaterialsMethod }}</th><th>{{ labels.targetApiName }}</th><th>{{ labels.targetApiPath }}</th><th>{{ labels.targetApiOperationId }}</th><th>{{ labels.apiMaterialsParameters }}</th><th>{{ labels.apiMaterialsSource }}</th><th>{{ labels.apiMaterialsLoadability }}</th><th>{{ labels.apiMaterialsSelectionState }}</th></tr></thead>
          <tbody>
            <tr v-for="operation in filteredOperations" :key="apiMaterialIdentity(operation.method, operation.path)">
              <td><input type="checkbox" :aria-label="`${labels.apiMaterialsUse}: ${operation.summary ?? operation.operationId ?? operation.path}`" :checked="isSelected(operation)" :disabled="!enabled || busy" @change="emit('toggle', operation.method, operation.path, ($event.target as HTMLInputElement).checked)" /></td>
              <td><StatusCapsule :label="operation.method" /></td>
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
    </ConsoleCard>
  </div>
</template>

<style scoped>
.configuration-file-name { min-width: 0; overflow-wrap: anywhere; }
.api-materials-filters { display: grid; grid-template-columns: auto minmax(220px, 1fr) auto auto; align-items: end; gap: 12px; }
.api-materials-filters label { display: grid; gap: 6px; color: var(--agent-text-muted); font-size: 12px; font-weight: 650; }
.api-materials-filters select, .api-materials-filters input { min-width: 0; }
.api-materials-filter-count { margin: 0 0 7px; color: var(--agent-text-muted); font-size: 12px; white-space: nowrap; }
.api-materials-table { min-width: 1440px; }
.api-materials-table td { vertical-align: top; white-space: normal; }
.api-materials-table code { overflow-wrap: anywhere; }
@media (max-width: 760px) {
  .api-materials-filters { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .api-materials-keyword-filter { grid-column: 1 / -1; }
  .api-materials-filter-count { grid-column: 1 / -1; margin-bottom: 0; }
}
</style>
