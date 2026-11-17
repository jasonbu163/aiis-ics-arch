<!--
File Path: /automation-world/semantic-mapping-agent/src/app/connection/components/BackendConnectionPanel.vue
Description: Local API-first Backend connection bootstrap form.
Main Features:
  - Edits the protocol, backend host, and port without database credentials
  - Shows the derived base URL and emits explicit save and OpenAPI test intentions
-->
<script setup lang="ts">
import { ConsoleCard, ConsoleActionButton, StatusCapsule } from "@aw-ui";
import { computed } from "vue";

import type { LocaleMessages } from "../../../locales";
import type { BackendConnectionProfile } from "../types";

const profile = defineModel<BackendConnectionProfile>("profile", { required: true });
const props = defineProps<{
  labels: LocaleMessages;
  saving: boolean;
  testing: boolean;
  saveStatus: "idle" | "saved" | "failed";
  saveMessage: string;
  testStatus: "idle" | "testing" | "connected" | "failed";
  testMessage: string;
  testTarget: string;
}>();

defineEmits<{
  save: [];
  testOpenApi: [];
}>();

const baseUrl = computed(() => {
  const host = profile.value.host.trim();
  const port = Number(profile.value.port);
  return host && Number.isInteger(port) && port >= 1 && port <= 65535
    ? `${profile.value.scheme}://${host}:${port}`
    : "—";
});
</script>

<template>
  <ConsoleCard class="connection-panel" :title="props.labels.backendConnection">
<template #actions><div class="action-row">
        <ConsoleActionButton tone="secondary" native-type="button" :disabled="saving" @click="$emit('save')">
          {{ props.labels.saveBackendConnection }}
        </ConsoleActionButton>
        <ConsoleActionButton tone="primary" native-type="button" :disabled="saving || testing" @click="$emit('testOpenApi')">
          {{ testing ? props.labels.testingOpenApi : props.labels.testOpenApi }}
        </ConsoleActionButton>
      </div></template>

    <p v-if="saveMessage" class="connection-status" role="status"><StatusCapsule :label="saveMessage" :tone="saveStatus === 'failed' ? 'danger' : saveStatus === 'saved' ? 'success' : 'neutral'" /></p>
    <p class="connection-status" role="status"><StatusCapsule :label="testMessage" :tone="testStatus === 'failed' ? 'danger' : testStatus === 'connected' ? 'success' : 'neutral'" /></p>
    <p v-if="testTarget" class="hint test-address">{{ props.labels.openApiTestAddress }} <code>{{ testTarget }}</code></p>

    <div class="form-grid">
      <label class="field">
        <span>{{ props.labels.backendScheme }}</span>
        <select v-model="profile.scheme" :disabled="saving">
          <option value="http">HTTP</option>
          <option value="https">HTTPS</option>
        </select>
      </label>
      <label class="field">
        <span>{{ props.labels.backendHost }}</span>
        <input v-model="profile.host" type="text" autocomplete="off" :disabled="saving" />
      </label>
      <label class="field">
        <span>{{ props.labels.port }}</span>
        <input v-model.number="profile.port" type="number" min="1" max="65535" :disabled="saving" />
      </label>
      <label class="field">
        <span>{{ props.labels.backendBaseUrl }}</span>
        <input :value="baseUrl" type="text" readonly />
      </label>
    </div>

    <p class="hint">{{ props.labels.backendConnectionHint }}</p>
  </ConsoleCard>
</template>

<style scoped>
.test-address { overflow-wrap: anywhere; }
</style>
