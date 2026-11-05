<!--
File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/components/ApiFirstMappingRuntimePanel.vue
Description: Control surface for the continuous API-first Mapping Runtime.
Main Features: Shows independent lifecycle, local app-open preference and per-Mapping interval semantics, safe counters, bounded logs, and full workspace-width layout without exposing target payloads.
-->
<script setup lang="ts">
import { ConsoleCard, ConsoleActionButton, StatusCapsule } from "@aw-ui";
import { computed } from "vue";
import { formatBusinessTime } from "../../../console/time";

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
  <ConsoleCard class="api-first-mapping-runtime-panel" :title="labels.apiFirstMappingRuntimeTitle">
    <p v-if="busy" class="hint" role="status">{{ labels.loading }}</p>
<template #actions><StatusCapsule :label="statusText(runtime.status)" :tone="runtime.status === 'failed' ? 'danger' : runtime.status === 'paused' ? 'warning' : active ? 'success' : 'neutral'" /></template>
    <p>{{ labels.apiFirstMappingRuntimeHint }}</p>
    <p class="warning" role="alert">{{ labels.apiFirstMappingRuntimeSafety }}</p>
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
      <ConsoleActionButton tone="primary" v-if="!active" native-type="button" :disabled="!enabled || busy" @click="$emit('action', 'start')">{{ labels.startRuntime }}</ConsoleActionButton>
      <ConsoleActionButton tone="secondary" v-if="runtime.status === 'running'" native-type="button" :disabled="busy" @click="$emit('action', 'pause')">{{ labels.pauseRuntime }}</ConsoleActionButton>
      <ConsoleActionButton tone="secondary" v-if="runtime.status === 'paused'" native-type="button" :disabled="busy" @click="$emit('action', 'resume')">{{ labels.resumeRuntime }}</ConsoleActionButton>
      <ConsoleActionButton tone="danger" v-if="active" native-type="button" :disabled="busy" @click="$emit('action', 'stop')">{{ labels.stopRuntime }}</ConsoleActionButton>
    </div>
    <p v-if="runtime.cursor"><strong>{{ labels.twinCursor }}</strong> <code>{{ runtime.cursor }}</code></p>
    <p v-if="runtime.lastErrorCode" class="warning" role="alert"><code>{{ runtime.lastErrorCode }}</code></p>
    <p v-if="error" class="warning" role="alert">{{ error }}</p>
    <p class="hint">{{ labels.businessTimeHint }}</p>
    <ol class="runtime-event-list"><li v-for="entry in runtime.logs.slice(-8).reverse()" :key="entry.sequence"><code :title="entry.timestamp">{{ formatBusinessTime(entry.timestamp, labels.timeMissing) }}</code><span>{{ entry.event }}</span><small>{{ entry.message }}</small></li></ol>
  </ConsoleCard>
</template>

<style scoped>
.api-first-mapping-runtime-panel { display: grid; min-width: 0; max-width: none; gap: 12px; }
.api-first-mapping-runtime-panel code { overflow-wrap: anywhere; white-space: normal; }
.runtime-auto-start { display: flex; align-items: center; gap: 8px; color: var(--agent-text-muted); font-size: 13px; font-weight: 650; }
.runtime-auto-start-hint { margin: -6px 0 0; color: var(--agent-text-muted); font-size: 12px; }
.runtime-actions { flex-wrap: wrap; gap: 12px; }
</style>
