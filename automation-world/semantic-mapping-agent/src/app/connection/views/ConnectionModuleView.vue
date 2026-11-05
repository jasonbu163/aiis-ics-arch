<!-- SMA retains the Backend bootstrap/OpenAPI controls without SQL/customer diagnostics. -->
<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { presentUserError } from "../../errors";
import type { LocaleMessages } from "../../../locales";
import { loadBackendConnectionProfile, saveBackendConnectionProfile, testBackendOpenApi } from "../api";
import BackendConnectionPanel from "../components/BackendConnectionPanel.vue";
import OpenApiOperationCatalog from "../components/OpenApiOperationCatalog.vue";
import type { BackendOpenApiResult } from "../types";
const props = defineProps<{ labels: LocaleMessages }>();
const labels = computed(() => props.labels);
import { currentRevision, localConfiguration } from "../../twin-facts/api/localConfiguration";
let observedRevision = localConfiguration.value?.revision ?? 0;
const backendProfile = ref(loadBackendConnectionProfile());
let previousSaved = JSON.stringify(backendProfile.value);
watch(localConfiguration, snapshot => {
  if (!snapshot) return;
  if (JSON.stringify(backendProfile.value) === previousSaved) { backendProfile.value = { ...snapshot.document.connection }; observedRevision = snapshot.revision; }
  previousSaved = JSON.stringify(snapshot.document.connection);
});
const backendConnectionStatus = ref<"idle" | "saved" | "connected" | "failed">("idle");
const backendConnectionMessage = ref("");
const backendConnectionTesting = ref(false);
const backendOpenApiResult = ref<BackendOpenApiResult | null>(null);
async function saveBackendConnection() {
  backendOpenApiResult.value = null;
  try {
    backendProfile.value = await saveBackendConnectionProfile(backendProfile.value, observedRevision);
    observedRevision = currentRevision();
    backendConnectionStatus.value = "saved";
    backendConnectionMessage.value = labels.value.backendConnectionSaved;
  } catch (error) {
    backendConnectionStatus.value = "failed";
    backendConnectionMessage.value = /CONFLICT/.test(String(error)) ? labels.value.localConfigurationConflict : presentUserError(labels.value, error).primaryMessage;
  }
}
async function testBackendConnectionOpenApi() {
  await saveBackendConnection();
  if (backendConnectionStatus.value === "failed") return;
  backendConnectionTesting.value = true;
  backendOpenApiResult.value = null;
  try {
    const result = await testBackendOpenApi(backendProfile.value);
    backendOpenApiResult.value = result;
    backendConnectionStatus.value = "connected";
    backendConnectionMessage.value = `${labels.value.openApiLoaded}: ${result.openApiVersion}`;
  } catch (error) {
    backendConnectionStatus.value = "failed";
    backendConnectionMessage.value = /CONFLICT/.test(String(error)) ? labels.value.localConfigurationConflict : presentUserError(labels.value, error).primaryMessage;
  } finally { backendConnectionTesting.value = false; }
}
</script>
<template>
  <BackendConnectionPanel v-model:profile="backendProfile" :labels="labels" :testing="backendConnectionTesting" :connection-status="backendConnectionStatus" :connection-message="backendConnectionMessage" @save="saveBackendConnection" @test-open-api="testBackendConnectionOpenApi" />
  <OpenApiOperationCatalog v-if="backendOpenApiResult" :labels="labels" :result="backendOpenApiResult" />
</template>
