<!--
File Path: /automation-world/semantic-mapping-agent/src/app/connection/components/BackendConnectionPanel.vue
Description: Local API-first Backend connection bootstrap form.
Main Features:
  - Edits the protocol, backend host, and port without database credentials
  - Shows the derived base URL and emits explicit save and OpenAPI test intentions
-->
<script setup lang="ts">
import { computed } from "vue";

import type { LocaleMessages } from "../../../locales";
import type { BackendConnectionProfile } from "../types";

const profile = defineModel<BackendConnectionProfile>("profile", { required: true });
const props = defineProps<{
  labels: LocaleMessages;
  testing: boolean;
  connectionStatus: "idle" | "saved" | "connected" | "failed";
  connectionMessage: string;
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
  <section class="panel connection-panel">
    <header class="panel-header">
      <div>
        <p class="panel-kicker">{{ props.labels.backendConnectionKicker }}</p>
        <h2>{{ props.labels.backendConnection }}</h2>
      </div>
      <div class="action-row">
        <button class="secondary-action" type="button" :disabled="testing" @click="$emit('save')">
          {{ props.labels.saveBackendConnection }}
        </button>
        <button class="primary-action" type="button" :disabled="testing" @click="$emit('testOpenApi')">
          {{ testing ? props.labels.testingOpenApi : props.labels.testOpenApi }}
        </button>
      </div>
    </header>

    <div class="connection-status" :class="connectionStatus">
      <span class="status-dot" />
      <span>{{ connectionMessage || props.labels.openApiUntested }}</span>
    </div>

    <div class="form-grid">
      <label class="field">
        <span>{{ props.labels.backendScheme }}</span>
        <select v-model="profile.scheme">
          <option value="http">HTTP</option>
          <option value="https">HTTPS</option>
        </select>
      </label>
      <label class="field">
        <span>{{ props.labels.backendHost }}</span>
        <input v-model="profile.host" type="text" autocomplete="off" />
      </label>
      <label class="field">
        <span>{{ props.labels.port }}</span>
        <input v-model.number="profile.port" type="number" min="1" max="65535" />
      </label>
      <label class="field">
        <span>{{ props.labels.backendBaseUrl }}</span>
        <input :value="baseUrl" type="text" readonly />
      </label>
    </div>

    <p class="hint">{{ props.labels.backendConnectionHint }}</p>
  </section>
</template>
