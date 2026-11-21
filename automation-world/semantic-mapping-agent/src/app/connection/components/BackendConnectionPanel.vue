<!--
File Path: /automation-world/semantic-mapping-agent/src/app/connection/components/BackendConnectionPanel.vue
Description: Local API-first Backend connection bootstrap form.
Main Features:
  - Edits the protocol, backend host, and port without database credentials
  - Shows connection status and derived addresses, and emits explicit save and test intentions
-->
<script setup lang="ts">
import { ConsoleCard, ConsoleActionButton, type CardHeaderStatus } from "@aw-ui";
import { computed } from "vue";

import type { LocaleMessages } from "../../../locales";
import { formatBackendOpenApiBaseUrl } from "../api";
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

const openApiAddress = computed(() => {
  if (props.testTarget) return props.testTarget;
  try {
    return `${formatBackendOpenApiBaseUrl(profile.value)}/openapi.json`;
  } catch {
    return "—";
  }
});

const headerStatuses = computed<CardHeaderStatus[]>(() => {
  const { labels, saveMessage, saveStatus, testMessage, testStatus } = props;
  const test: CardHeaderStatus = {
    id: "test",
    label: testStatus === "failed" ? labels.openApiTestFailed : testMessage,
    tone: testStatus === "failed" ? "danger" : testStatus === "connected" ? "success" : "neutral",
  };
  if (!saveMessage) return [test];

  const save: CardHeaderStatus = {
    id: "save",
    label: saveStatus === "failed" ? labels.backendConnectionSaveFailed : saveMessage,
    tone: saveStatus === "failed" ? "danger" : saveStatus === "saved" ? "success" : "warning",
  };
  return testStatus === "failed" && saveStatus !== "failed" ? [test, save] : [save, test];
});
</script>

<template>
  <ConsoleCard class="connection-panel" :title="props.labels.backendConnection" :header-statuses="headerStatuses" :status-overflow-label="props.labels.moreCardStatuses" :help="props.labels.backendConnectionHint" :help-label="props.labels.backendConnectionHelp" help-append-to="#sma-overlays">
    <template #actions>
      <div class="action-row">
        <ConsoleActionButton tone="secondary" native-type="button" :disabled="saving" @click="$emit('save')">
          {{ props.labels.saveBackendConnection }}
        </ConsoleActionButton>
        <ConsoleActionButton tone="primary" native-type="button" :disabled="saving || testing" @click="$emit('testOpenApi')">
          {{ testing ? props.labels.testingOpenApi : props.labels.testOpenApi }}
        </ConsoleActionButton>
      </div>
    </template>

    <p v-if="saveStatus === 'failed' && saveMessage" class="warning" role="alert">{{ saveMessage }}</p>
    <p v-if="testStatus === 'failed'" class="warning" role="alert">{{ testMessage }}</p>

    <div class="form-grid connection-form">
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
      <label class="field test-address">
        <span>{{ props.labels.openApiTestAddress }}</span>
        <input :value="openApiAddress" type="text" readonly />
      </label>
    </div>
  </ConsoleCard>
</template>
