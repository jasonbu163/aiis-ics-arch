<!--
File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/components/ApiFirstMappingRuntimePanel.vue
Description: Control surface for the continuous API-first Mapping Runtime.
Main Features: Shows independent lifecycle, local app-open preference and per-Mapping interval semantics, safe counters, bounded logs, and full workspace-width layout without exposing target payloads.
-->
<script setup lang="ts">
import { computed } from "vue";

import type { LocaleMessages } from "../../../locales";
import type { TwinRuntimeSnapshot } from "../types";

const props = defineProps<{
  labels: LocaleMessages;
  runtime: TwinRuntimeSnapshot;
  busy: boolean;
  error: string;
  enabled: boolean;
  autoStartEnabled: boolean;
  runtimeStartupBusy: boolean;
}>();

const emit = defineEmits<{
  action: [value: "start" | "pause" | "resume" | "stop"];
  "update:autoStart": [value: boolean];
}>();

const active = computed(() => ["starting", "running", "paused", "stopping"].includes(props.runtime.status));
function statusText(status: TwinRuntimeSnapshot["status"]) {
  return props.labels.runtimeStatuses[status];
}

</script>

<template>
  <article class="panel api-first-mapping-runtime-panel">
    <header class="panel-header">
      <div><p class="panel-kicker">{{ labels.apiFirstMappingRuntimeKicker }}</p><h2>{{ labels.apiFirstMappingRuntimeTitle }}</h2></div>
      <span class="status-pill">{{ statusText(runtime.status) }}</span>
    </header>
    <p>{{ labels.apiFirstMappingRuntimeHint }}</p>
    <p class="warning">{{ labels.apiFirstMappingRuntimeSafety }}</p>
    <label class="runtime-auto-start">
      <input
        type="checkbox"
        :checked="autoStartEnabled"
        :disabled="runtimeStartupBusy"
        @change="$emit('update:autoStart', ($event.target as HTMLInputElement).checked)"
      />
      <span>{{ labels.runtimeAutoStartOnOpen }}</span>
    </label>
    <p class="runtime-auto-start-hint">{{ labels.mappingRuntimeAutoStartHint }}</p>
    <div class="runtime-metrics twin-runtime-metrics">
      <div><small>{{ labels.twinProcessed }}</small><strong>{{ runtime.processedItems }}</strong></div>
      <div><small>{{ labels.successfulTransactions }}</small><strong>{{ runtime.successfulTransactions }}</strong></div>
      <div><small>{{ labels.failedTransactions }}</small><strong>{{ runtime.failedTransactions }}</strong></div>
    </div>
    <div class="action-row runtime-actions">
      <button v-if="!active" class="primary-action" type="button" :disabled="!enabled || busy" @click="$emit('action', 'start')">{{ labels.startRuntime }}</button>
      <button v-if="runtime.status === 'running'" class="secondary-action" type="button" :disabled="busy" @click="$emit('action', 'pause')">{{ labels.pauseRuntime }}</button>
      <button v-if="runtime.status === 'paused'" class="secondary-action" type="button" :disabled="busy" @click="$emit('action', 'resume')">{{ labels.resumeRuntime }}</button>
      <button v-if="active" class="danger-action" type="button" :disabled="busy" @click="$emit('action', 'stop')">{{ labels.stopRuntime }}</button>
    </div>
    <p v-if="runtime.cursor"><strong>{{ labels.twinCursor }}</strong> <code>{{ runtime.cursor }}</code></p>
    <p v-if="runtime.lastErrorCode" class="warning"><code>{{ runtime.lastErrorCode }}</code></p>
    <p v-if="error" class="warning">{{ error }}</p>
    <ol class="runtime-event-list"><li v-for="entry in runtime.logs.slice(-8).reverse()" :key="entry.sequence"><code>{{ entry.timestamp }}</code><span>{{ entry.event }}</span><small>{{ entry.message }}</small></li></ol>
  </article>
</template>

<style scoped>
.api-first-mapping-runtime-panel { display: grid; min-width: 0; max-width: none; gap: 12px; }
.api-first-mapping-runtime-panel code { overflow-wrap: anywhere; white-space: normal; }
.runtime-auto-start { display: flex; align-items: center; gap: 8px; color: #315f5d; font-size: 13px; font-weight: 650; }
.runtime-auto-start-hint { margin: -6px 0 0; color: #52707a; font-size: 12px; }
.runtime-actions { flex-wrap: wrap; gap: 12px; }
</style>
