<!-- SMA只读源事实：查询、筛选、分页和导出，不提供事实生产入口。 -->
<script setup lang="ts">
import { ConsoleCard, ConsoleActionButton, StatusCapsule } from "@aw-ui";
import { computed, ref, watch } from "vue";
import PaginationBar from "../../../components/PaginationBar.vue";
import type { LocaleMessages } from "../../../locales";
import { useTableWidths } from "../../../console/tableWidths";
import { formatBusinessTime } from "../../../console/time";
import type { BackendCollectionFactListQuery, BackendCollectionFactPage, CollectionFactContract, CollectionFactFileFormat, CollectionFactDataType, CollectionFactKind } from "../types";
const props = defineProps<{
  labels: LocaleMessages; sourceKey: string; contract: CollectionFactContract | null;
  query: BackendCollectionFactListQuery; result: BackendCollectionFactPage;
  contractBusy: boolean; tableBusy: boolean; error: string; enabled: boolean;
}>();
const emit = defineEmits<{
  "load-source": [sourceKey: string]; query: [patch: Partial<BackendCollectionFactListQuery>];
  "export-values": [format: CollectionFactFileFormat, complete: (failed: boolean) => void];
}>();
const sourceInput = ref(props.sourceKey);
const nameInput = ref(props.query.name || "");
const savingFile = ref(false);
const exportError = ref(false);
const busy = computed(() => props.contractBusy || props.tableBusy);
watch(() => props.sourceKey, value => { sourceInput.value = value; });
watch(() => props.query.name, value => { nameInput.value = value || ""; });
const kinds: CollectionFactKind[] = ["current", "incremental"];
const types: CollectionFactDataType[] = ["string", "integer", "number", "boolean", "datetime"];
const columns = [
  { id: "name", label: "collectionFactsName", width: 220 },
  { id: "sourceKey", label: "twinSourceKey", width: 180 },
  { id: "factKind", label: "collectionFactsKind", width: 120 },
  { id: "dataType", label: "collectionFactsDataType", width: 120 },
  { id: "value", label: "collectionFactsValue", width: 200 },
  { id: "updatedAt", label: "collectionFactsUpdatedAt", width: 190, min: 160 },
  { id: "rowVersion", label: "collectionFactsRowVersion", width: 180 },
] as const;
const table = useTableWidths("source-facts", columns);
function selectQuery(field: "factKind" | "dataType", event: Event) {
  emit("query", { [field]: (event.target as HTMLSelectElement).value || undefined, page: 1 });
}
function exportValues(format: CollectionFactFileFormat) {
  savingFile.value = true;
  exportError.value = false;
  emit("export-values", format, failed => { savingFile.value = false; exportError.value = failed; });
}
</script>
<template>
  <ConsoleCard class="facts-table-panel" :title="labels.factsTableTitle">
<template #actions><StatusCapsule :label="labels.sourceFactsReadOnly" /></template>
    <p>{{ labels.factsTableHint }}</p>
    <div class="facts-source-controls">
      <label class="field"><span>{{ labels.twinSourceKey }}</span><input v-model="sourceInput" :disabled="busy" @keyup.enter="emit('load-source', sourceInput.trim())" /></label>
      <ConsoleActionButton tone="secondary" :disabled="!enabled || busy" @click="emit('load-source', sourceInput.trim())">{{ labels.collectionFactsLoad }}</ConsoleActionButton>
      <ConsoleActionButton tone="secondary" v-for="format in (['json', 'xlsx'] as const)" :key="format" :disabled="!enabled || !contract || busy || savingFile" @click="exportValues(format)">{{ labels.collectionFactsExportValues }} {{ format.toUpperCase() }}</ConsoleActionButton>
    </div>
    <p v-if="sourceKey && !contract && !busy && !error" class="notice">{{ labels.sourceFactsMissing }}</p>
    <p v-if="error" class="warning">{{ labels.collectionFactsOperationFailed }}</p>
    <p v-if="exportError" class="warning">{{ labels.collectionFactsExportFailed }}</p>
    <div class="collection-fact-filters">
      <label>{{ labels.collectionFactsName }}<input v-model="nameInput" :disabled="busy" @change="emit('query', { name: nameInput, page: 1 })" /></label>
      <label>{{ labels.collectionFactsKind }}<select :value="query.factKind || ''" :disabled="busy" @change="selectQuery('factKind', $event)"><option value="">{{ labels.collectionFactsAll }}</option><option v-for="kind in kinds" :key="kind">{{ kind }}</option></select></label>
      <label>{{ labels.collectionFactsDataType }}<select :value="query.dataType || ''" :disabled="busy" @change="selectQuery('dataType', $event)"><option value="">{{ labels.collectionFactsAll }}</option><option v-for="type in types" :key="type">{{ type }}</option></select></label>
      <ConsoleActionButton tone="secondary" :disabled="!enabled || busy" @click="emit('query', { page: query.page })">{{ labels.refresh }}</ConsoleActionButton>
      <ConsoleActionButton tone="secondary" @click="table.reset">{{ labels.resetTableWidths }}</ConsoleActionButton>
    </div>
    <p class="hint">{{ labels.businessTimeHint }}</p>
    <div class="table-scroll facts-table-scroll" tabindex="0">
      <table class="facts-table" :style="{ width: `${table.totalWidth.value}px` }">
        <colgroup><col v-for="column in columns" :key="column.id" :style="{ width: `${table.widths.value[column.id]}px` }" /></colgroup>
        <thead><tr><th v-for="column in columns" :key="column.id">{{ labels[column.label] }}<span class="sma-column-resizer" :aria-label="labels.resizeTableColumn" @pointerdown="table.startResize(column.id, $event)" /></th></tr></thead>
        <tbody>
          <tr v-for="fact in result.items" :key="`${fact.sourceKey}:${fact.name}`"><td><code>{{ fact.name }}</code></td><td><code>{{ fact.sourceKey }}</code></td><td>{{ fact.factKind }}</td><td>{{ fact.dataType }}</td><td><code>{{ fact.value ?? labels.collectionFactsNull }}</code></td><td :title="fact.updatedAt">{{ formatBusinessTime(fact.updatedAt, labels.timeMissing) }}</td><td><code>{{ fact.rowVersion }}</code></td></tr>
          <tr v-if="tableBusy"><td :colspan="columns.length">{{ labels.loading }}</td></tr>
        </tbody>
      </table>
    </div>
    <p v-if="!tableBusy && !result.items.length" class="empty-state">{{ labels.collectionFactsEmpty }}</p>
    <PaginationBar :labels="labels" :page="result.page" :page-size="result.pageSize" :total="result.total" :busy="busy" @update:page="emit('query', { page: $event })" @update:page-size="emit('query', { page: 1, pageSize: $event })" />
  </ConsoleCard>
</template>
<style>
.facts-source-controls { display: flex; flex-wrap: wrap; align-items: end; gap: 12px; margin-top: 16px; }
.facts-source-controls .field { flex: 1 1 280px; }
.collection-fact-filters { display: flex; flex-wrap: wrap; align-items: end; gap: 12px; margin: 18px 0; }
.collection-fact-filters label { display: grid; gap: 6px; }
.facts-table-scroll { overflow-x: auto; }
.facts-table { table-layout: fixed; }
.facts-table th { position: relative; }
.facts-table td { vertical-align: top; white-space: normal; }
.facts-table code { overflow-wrap: anywhere; white-space: normal; }
.sma-column-resizer { position: absolute; right: 0; top: 0; z-index: 1; width: 9px; height: 100%; cursor: col-resize; touch-action: none; }
</style>
