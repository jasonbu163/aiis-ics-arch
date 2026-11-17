<!--
File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/components/ApiFirstMappingRuntimePanel.vue
Description: Diagnostic surface for the API-first Mapping Runtime.
Main Features: Shows delivery availability, lifecycle, safe counters, bounded logs, and applicable pause and stop controls.
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
}>();

defineEmits<{
  action: [value: "pause" | "stop"];
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
    <p class="hint">{{ labels.mappingDeliveryUnavailable }}</p>
    <div class="runtime-metrics twin-runtime-metrics">
      <div><small>{{ labels.twinProcessed }}</small><strong>{{ runtime.processedItems }}</strong></div>
      <div><small>{{ labels.successfulTransactions }}</small><strong>{{ runtime.successfulTransactions }}</strong></div>
      <div><small>{{ labels.failedTransactions }}</small><strong>{{ runtime.failedTransactions }}</strong></div>
    </div>
    <div class="action-row runtime-actions">
      <ConsoleActionButton tone="secondary" v-if="runtime.status === 'running'" native-type="button" :disabled="busy" @click="$emit('action', 'pause')">{{ labels.pauseRuntime }}</ConsoleActionButton>
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
.runtime-actions { flex-wrap: wrap; gap: 12px; }
</style>
