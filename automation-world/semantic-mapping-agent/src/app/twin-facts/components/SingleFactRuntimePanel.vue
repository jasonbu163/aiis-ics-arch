<!--
File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/components/SingleFactRuntimePanel.vue
Description: Per-point Simulation controls and sealed legacy Service Projection notice.
Main Features: Saves backend-owned simulation rules, persists Simulation app-open preference, and identifies deferred legacy cleanup.
-->
<script setup lang="ts">
import { computed, ref, watch } from "vue";

import PaginationBar from "../../../components/PaginationBar.vue";
import { usePagination } from "../../../components/usePagination";
import type { LocaleMessages } from "../../../locales";
import type {
  CollectionSimulationPointEditor,
  SimulationCurrentTimeMode,
  TwinRuntimeSnapshot,
} from "../types";

const props = defineProps<{
  labels: LocaleMessages;
  sourceKey: string;
  points: CollectionSimulationPointEditor[];
  enabledPointCount: number;
  pointsValid: boolean;
  pointsBusy: boolean;
  simulation: TwinRuntimeSnapshot;
  simulationBusy: boolean;
  simulationSettingsBusy: boolean;
  simulationSettingsDirty: boolean;
  simulationAutoStartEnabled: boolean;
  runtimeStartupBusy: boolean;
  enabled: boolean;
  view: string;
}>();

const emit = defineEmits<{
  "update:pointValues": [factName: string, valuesJson: string];
  "update:pointInterval": [factName: string, intervalMs: number];
  "update:pointCurrentTime": [
    factName: string,
    writeCurrentTime: boolean,
    currentTimeMode?: SimulationCurrentTimeMode,
    currentTimeZone?: string | null,
  ];
  saveSimulationSettings: [];
  "update:simulationAutoStart": [value: boolean];
  simulationAction: [value: "start" | "pause" | "resume" | "stop"];
}>();

const simulationActive = computed(() => isActive(props.simulation.status));
const pointSearch = ref("");
const filteredPoints = computed(() => {
  const keyword = pointSearch.value.trim().toLowerCase();
  return keyword ? props.points.filter((point) => point.factName.toLowerCase().includes(keyword)) : props.points;
});
const pointPagination = usePagination(() => filteredPoints.value, 20);
watch(pointSearch, () => pointPagination.setPage(1));

function isActive(status: string) {
  return ["starting", "running", "paused", "stopping"].includes(status);
}

function statusText(status: TwinRuntimeSnapshot["status"]) {
  return props.labels.runtimeStatuses[status];
}

function updateCurrentTimeMode(point: CollectionSimulationPointEditor, event: Event) {
  const value = (event.target as HTMLSelectElement).value;
  const currentTimeMode: SimulationCurrentTimeMode = value === "system" || value === "custom" ? value : "utc";
  emit(
    "update:pointCurrentTime",
    point.factName,
    true,
    currentTimeMode,
    currentTimeMode === "custom" ? point.currentTimeZone : null,
  );
}

function updateCurrentTimeZone(point: CollectionSimulationPointEditor, event: Event) {
  emit(
    "update:pointCurrentTime",
    point.factName,
    true,
    "custom",
    (event.target as HTMLInputElement).value || null,
  );
}
</script>

<template>
  <section class="single-fact-runtime-stack">
    <article v-show="view === 'simulation'" class="panel twin-runtime-panel">
      <header class="panel-header">
        <div><p class="panel-kicker">{{ labels.collectionSimulationKicker }}</p><h2>{{ labels.collectionSimulationTitle }}</h2></div>
        <span class="status-pill">{{ statusText(simulation.status) }}</span>
      </header>
      <p>{{ labels.collectionSimulationHint }}</p>
      <p class="warning">{{ labels.singleFactProducerWarning }}</p>
      <p><strong>{{ labels.twinSourceKey }}</strong> <code>{{ sourceKey || "—" }}</code></p>
      <label class="runtime-auto-start">
        <input
          type="checkbox"
          :checked="simulationAutoStartEnabled"
          :disabled="!sourceKey || runtimeStartupBusy"
          @change="$emit('update:simulationAutoStart', ($event.target as HTMLInputElement).checked)"
        />
        <span>{{ labels.runtimeAutoStartOnOpen }}</span>
      </label>
      <p class="runtime-auto-start-hint">{{ labels.simulationAutoStartHint }}</p>
      <label class="simulation-point-search">
        <span>{{ labels.simulationSearchPoint }}</span>
        <input v-model="pointSearch" type="search" autocomplete="off" />
      </label>

      <div class="table-scroll simulation-point-scroll" tabindex="0">
        <table class="simulation-point-table">
          <thead>
            <tr>
              <th>{{ labels.simulationPoint }}</th>
              <th>{{ labels.simulationValuesJson }}</th>
              <th>{{ labels.simulationPointInterval }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="point in pointPagination.pagedItems.value" :key="point.factName">
              <td><code>{{ point.factName }}</code><small>{{ point.dataType }}</small></td>
              <td>
                <label v-if="point.dataType === 'datetime'" class="simulation-current-time">
                  <input
                    type="checkbox"
                    :checked="point.writeCurrentTime"
                    :disabled="simulationBusy || simulationSettingsBusy || simulationActive"
                    @change="$emit('update:pointCurrentTime', point.factName, ($event.target as HTMLInputElement).checked)"
                  />
                  <span>{{ labels.simulationWriteCurrentTime }}</span>
                </label>
                <div v-if="point.writeCurrentTime" class="simulation-current-time-settings">
                  <label>
                    <span>{{ labels.simulationCurrentTimeMode }}</span>
                    <select
                      :value="point.currentTimeMode"
                      :disabled="simulationBusy || simulationSettingsBusy || simulationActive"
                      @change="updateCurrentTimeMode(point, $event)"
                    >
                      <option value="utc">{{ labels.simulationCurrentTimeModeUtc }}</option>
                      <option value="system">{{ labels.simulationCurrentTimeModeSystem }}</option>
                      <option value="custom">{{ labels.simulationCurrentTimeModeCustom }}</option>
                    </select>
                  </label>
                  <label v-if="point.currentTimeMode === 'custom'">
                    <span>{{ labels.simulationCurrentTimeZone }}</span>
                    <input
                      type="text"
                      :value="point.currentTimeZone ?? ''"
                      placeholder="Asia/Shanghai"
                      :disabled="simulationBusy || simulationSettingsBusy || simulationActive"
                      @input="updateCurrentTimeZone(point, $event)"
                    />
                  </label>
                  <p class="simulation-current-time-hint">{{ labels.simulationWriteCurrentTimeHint }}</p>
                </div>
                <textarea
                  v-if="!point.writeCurrentTime"
                  :value="point.valuesJson"
                  rows="2"
                  spellcheck="false"
                  :disabled="simulationBusy || simulationSettingsBusy || simulationActive"
                  :aria-label="`${labels.simulationValuesJson}: ${point.factName}`"
                  @input="$emit('update:pointValues', point.factName, ($event.target as HTMLTextAreaElement).value)"
                />
                <small v-if="point.validationError" class="field-error">{{ labels.simulationValidation[point.validationError] }}</small>
              </td>
              <td>
                <input
                  type="number"
                  min="20"
                  max="86400000"
                  :value="point.intervalMs"
                  :disabled="simulationBusy || simulationSettingsBusy || simulationActive"
                  :aria-label="`${labels.simulationPointInterval}: ${point.factName}`"
                  @input="$emit('update:pointInterval', point.factName, Number(($event.target as HTMLInputElement).value))"
                />
              </td>
            </tr>
            <tr v-if="!pointsBusy && points.length === 0"><td colspan="3">{{ labels.simulationNoPoints }}</td></tr>
            <tr v-else-if="!pointsBusy && filteredPoints.length === 0"><td colspan="3">{{ labels.simulationNoMatches }}</td></tr>
            <tr v-if="pointsBusy"><td colspan="3">{{ labels.loading }}</td></tr>
          </tbody>
        </table>
      </div>
      <PaginationBar :labels="labels" :page="pointPagination.page.value" :page-size="pointPagination.pageSize.value" :total="pointPagination.total.value" :busy="pointsBusy" :page-size-options="[10, 20, 50]" @update:page="pointPagination.setPage" @update:page-size="pointPagination.setPageSize" />
      <p class="runtime-config-summary">{{ labels.simulationEnabledPoints }}: {{ enabledPointCount }} · {{ labels.simulationDisabledHint }}</p>
      <p v-if="simulationSettingsDirty" class="warning">{{ labels.simulationSettingsUnsaved }}</p>
      <div class="runtime-metrics twin-runtime-metrics">
        <div><small>{{ labels.twinProcessed }}</small><strong>{{ simulation.processedItems }}</strong></div>
        <div><small>{{ labels.successfulTransactions }}</small><strong>{{ simulation.successfulTransactions }}</strong></div>
        <div><small>{{ labels.failedTransactions }}</small><strong>{{ simulation.failedTransactions }}</strong></div>
      </div>
      <div class="action-row runtime-actions">
        <button v-if="!simulationActive" class="secondary-action" type="button" :disabled="!enabled || simulationBusy || simulationSettingsBusy || pointsBusy || !pointsValid || !sourceKey" @click="$emit('saveSimulationSettings')">{{ labels.saveSimulationSettings }}</button>
        <button v-if="!simulationActive" class="primary-action" type="button" :disabled="!enabled || simulationBusy || simulationSettingsBusy || pointsBusy || !pointsValid || enabledPointCount === 0 || !sourceKey || simulationSettingsDirty" @click="$emit('simulationAction', 'start')">{{ labels.startRuntime }}</button>
        <button v-if="simulation.status === 'running'" class="secondary-action" type="button" :disabled="simulationBusy" @click="$emit('simulationAction', 'pause')">{{ labels.pauseRuntime }}</button>
        <button v-if="simulation.status === 'paused'" class="secondary-action" type="button" :disabled="simulationBusy" @click="$emit('simulationAction', 'resume')">{{ labels.resumeRuntime }}</button>
        <button v-if="simulationActive" class="danger-action" type="button" :disabled="simulationBusy" @click="$emit('simulationAction', 'stop')">{{ labels.stopRuntime }}</button>
      </div>
      <ol class="runtime-event-list"><li v-for="entry in simulation.logs.slice(-8).reverse()" :key="entry.sequence"><code>{{ entry.timestamp }}</code><span>{{ entry.event }}</span><small>{{ entry.message }}</small></li></ol>
    </article>


  </section>
</template>

<style scoped>
.single-fact-runtime-stack { display: grid; gap: 16px; }
.single-fact-runtime-stack code { overflow-wrap: anywhere; white-space: normal; }
.simulation-point-scroll { max-width: 100%; margin-top: 16px; overflow-x: auto; }
.simulation-point-table { width: 100%; min-width: 720px; border-collapse: collapse; }
.simulation-point-table th, .simulation-point-table td { padding: 10px; text-align: left; vertical-align: top; border-bottom: 1px solid #dce6e8; }
.simulation-point-table td:first-child { min-width: 260px; }
.simulation-point-table td:first-child small { display: block; margin-top: 4px; color: #6b7d85; }
.simulation-point-table textarea { width: 100%; min-width: 280px; resize: vertical; }
.simulation-point-table input { width: 150px; }
.simulation-point-table select { min-width: 170px; }
.simulation-point-table .simulation-current-time { display: flex; width: auto; align-items: center; gap: 8px; margin-bottom: 8px; color: #315f5d; font-size: 13px; }
.simulation-point-table .simulation-current-time input { width: auto; }
.simulation-current-time-settings { display: grid; gap: 8px; }
.simulation-current-time-settings label { display: grid; gap: 4px; color: #52707a; font-size: 12px; font-weight: 650; }
.simulation-current-time-hint { margin: 0; color: #52707a; font-size: 13px; }
.field-error { display: block; margin-top: 5px; color: #a33d35; }
.runtime-config-summary { margin-top: 10px; color: #52707a; }
.runtime-auto-start { display: flex; align-items: center; gap: 8px; margin-top: 12px; color: #315f5d; font-size: 13px; font-weight: 650; }
.runtime-auto-start-hint { margin: 4px 0 0; color: #52707a; font-size: 12px; }
.runtime-actions { flex-wrap: wrap; gap: 12px; }
.simulation-point-search { display: grid; max-width: 420px; gap: 6px; margin-top: 14px; color: #52707a; font-size: 12px; font-weight: 650; }
</style>
