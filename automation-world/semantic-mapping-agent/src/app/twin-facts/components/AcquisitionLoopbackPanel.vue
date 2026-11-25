<!-- 采集最新值只读检查。 -->
<script setup lang="ts">
import { computed, onMounted } from "vue";
import { ConsoleActionButton, ConsoleCard } from "@aw-ui";
import { externalIoEnabled, formatBackendBaseUrl } from "../../connection/api";
import { localConfiguration } from "../api/localConfiguration";
import type { LocaleMessages } from "../../../locales";
import { useAcquisitionLatest } from "../store/acquisitionLoopback";
import AcquisitionPointsTable from "./AcquisitionPointsTable.vue";

const props = defineProps<{ labels: LocaleMessages; enabled: boolean }>();
const emit = defineEmits<{ navigate: [id: string] }>();
const online = computed(() => props.enabled && externalIoEnabled());
const text = computed(() => props.labels.acquisition);
const { config, ready, busy, error, errorAt, sources, choices, latest, missing, allPoints, materials, databases, materialReady, pointsReady, restoreSaved, loadSources, sourceChanged, dbChanged, testLatest, changeAllPoints } = useAcquisitionLatest();
const connection = computed(() => {
  const profile = localConfiguration.value?.document.connection;
  return profile?.host ? formatBackendBaseUrl(profile) : "";
});
const sourceOptions = computed(() => sources.value?.map(item => item.plcId) ?? []);
const sourceBlocker = computed(() => {
  if (!online.value) return text.value.httpDisabled;
  if (!connection.value) return text.value.connectionRequired;
  if (!materialReady.value) return text.value.materialNeeded;
  if (!config.value.plcId) return text.value.plcRequired;
  if (!config.value.dbNumber) return text.value.dbRequired;
  return "";
});
const errorLabel = computed(() => {
  const code = error.value;
  if (code.includes("RESULT_UNKNOWN")) return text.value.unknown;
  if (code.includes("SEQUENCE_INVALID")) return text.value.sequenceHelp;
  if (code.includes("TARGET_EQUALS_SOURCE")) return text.value.targetEqualsSource;
  if (code.includes("MATERIAL_MISSING")) return text.value.materialNeeded;
  if (code.includes("RESPONSE_INVALID")) return text.value.invalidResponse;
  if (code.includes("TIMEOUT")) return text.value.timeout;
  if (code.includes("TRANSPORT")) return text.value.connectionFailure;
  if (code.includes("EXTERNAL_IO_DISABLED")) return text.value.httpDisabled;
  if (code.toUpperCase().includes("CONFLICT") || code.includes("(409)")) return text.value.conflict;
  if (code.includes("HTTP") || code.includes("plc_facts")) return text.value.httpFailure;
  if (code.includes("POINTS_MISSING")) return text.value.missing;
  if (code.includes("SELECTION_REQUIRED")) return text.value.selectPoint;
  return text.value.failure;
});
onMounted(() => { void restoreSaved(); });
</script>

<template>
  <ConsoleCard :title="text.latestTitle" class="acquisition-card">
    <template #actions>
      <ConsoleActionButton tone="secondary" :disabled="Boolean(busy)" @click="restoreSaved">{{ text.reload }}</ConsoleActionButton>
      <ConsoleActionButton :disabled="!ready || !online || !connection || Boolean(busy)" @click="loadSources">{{ text.loadSources }}</ConsoleActionButton>
    </template>
    <p tabindex="-1" role="status" class="acquisition-feedback">
      {{ labels.backendConnection }} · <code>{{ connection || '—' }}</code> · {{ online ? labels.httpEnabled : text.httpDisabled }}
    </p>
    <p v-if="!connection || !online" class="warning" role="status">
      {{ !online ? text.httpDisabled : text.connectionRequired }}
      <ConsoleActionButton tone="secondary" @click="emit('navigate', 'connection')">{{ labels.navBackendConnection }}</ConsoleActionButton>
    </p>
    <p v-if="error && ['load', 'options', 'latest'].includes(errorAt)" class="warning acquisition-feedback" role="alert">{{ errorLabel }}<br><code>{{ error }}</code></p>
    <fieldset class="acquisition-fieldset" :disabled="Boolean(busy)">
    <div class="acquisition-fields">
      <label class="field">
        <span>{{ text.material }}</span>
        <select v-model="config.materialKey" :disabled="!ready">
          <option value="">{{ text.select }}</option>
          <option v-for="item in materials" :key="item.materialKey" :value="item.materialKey">{{ item.name }} · {{ item.path }}</option>
        </select>
      </label>
      <label class="field">
        <span>{{ text.sourcePlc }}</span>
        <select v-model="config.plcId" @change="sourceChanged">
          <option value="">{{ text.select }}</option>
          <option v-if="config.plcId && !sourceOptions.includes(config.plcId)" :value="config.plcId">{{ config.plcId }}</option>
          <option v-for="plc in sourceOptions" :key="plc" :value="plc">{{ plc }}</option>
        </select>
      </label>
      <label class="field">
        <span>{{ text.sourceDb }}</span>
        <select v-model.number="config.dbNumber" @change="dbChanged">
          <option :value="0">{{ text.select }}</option>
          <option v-if="config.dbNumber && !databases.includes(config.dbNumber)" :value="config.dbNumber">{{ config.dbNumber }}</option>
          <option v-for="item in databases" :key="item" :value="item">{{ item }}</option>
        </select>
      </label>
    </div>
    <p v-if="ready && !materialReady" class="warning" role="status">
      {{ text.materialNeeded }} <ConsoleActionButton tone="secondary" @click="emit('navigate', 'api-materials')">{{ labels.apiMaterialsTitle }}</ConsoleActionButton>
    </p>
    <p v-if="sources === null && connection && online" role="status">{{ text.loadSourcesHint }}</p>
    <p v-if="sources?.length === 0" role="status">{{ text.noData }}</p>
    <div class="acquisition-actions">
      <ConsoleActionButton tone="secondary" :disabled="Boolean(sourceBlocker || busy)" @click="testLatest(true)">{{ text.loadPoints }}</ConsoleActionButton>
      <ConsoleActionButton tone="secondary" :disabled="Boolean(sourceBlocker || busy || !pointsReady)" @click="testLatest()">{{ text.testGet }}</ConsoleActionButton>
    </div>
    <fieldset class="acquisition-selection">
      <legend>{{ text.points }}</legend>
      <label><input type="checkbox" :checked="allPoints" @change="changeAllPoints(($event.target as HTMLInputElement).checked)">{{ text.allPoints }}</label>
      <div v-if="!allPoints" class="acquisition-checks">
        <label v-for="item in choices" :key="item.pointId">
          <input v-model="config.pointIds" type="checkbox" :value="item.pointId">{{ item.pointId }}
        </label>
      </div>
    </fieldset>
    </fieldset>
    <p v-if="busy" role="status">{{ labels.loading }}</p>
    <p v-if="missing.length" class="warning" role="status">{{ text.missing }} {{ missing.join(", ") }}</p>
    <AcquisitionPointsTable v-if="latest" :labels="labels" :points="latest"
      table-id="acquisition.latest" />
    <template #footer>
      <div class="acquisition-step-footer">
        <p v-if="sourceBlocker || !pointsReady" role="status">{{ sourceBlocker || text.selectPoint }}</p>
      </div>
    </template>
  </ConsoleCard>

</template>

<style scoped>
.acquisition-card { display: grid; min-width: 0; }
.acquisition-fieldset { border: 0; padding: 0; margin: 0; min-width: 0; }
.acquisition-fields { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 13rem), 1fr)); gap: 0.75rem; margin-block: 0.7rem; }
.acquisition-fields input, .acquisition-fields select { min-width: 0; }
.acquisition-actions, .acquisition-checks { display: flex; flex-wrap: wrap; align-items: center; gap: .65rem; margin-block: .75rem; }
.acquisition-selection { border: 0; padding: 0; min-width: 0; margin-block: 1rem; }
.acquisition-selection label { display: inline-flex; align-items: center; gap: 0.35rem; }
.acquisition-feedback { overflow-wrap: anywhere; }
.acquisition-step-footer { display: flex; align-items: center; flex-wrap: wrap; gap: .75rem; }
.acquisition-step-footer p { margin: 0; }
.acquisition-step-footer > :last-child { margin-inline-start: auto; }
</style>
