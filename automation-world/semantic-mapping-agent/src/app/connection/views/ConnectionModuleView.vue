<!-- SMA connection settings keep draft tests separate from explicit local saves. -->
<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { presentUserError } from "../../errors";
import type { LocaleMessages } from "../../../locales";
import { formatBackendOpenApiBaseUrl, loadBackendConnectionProfile, saveBackendConnectionProfile, testBackendDraftOpenApi } from "../api";
import BackendConnectionPanel from "../components/BackendConnectionPanel.vue";
import OpenApiOperationCatalog from "../components/OpenApiOperationCatalog.vue";
import type { BackendOpenApiResult } from "../types";
import { currentRevision, localConfiguration } from "../../twin-facts/api/localConfiguration";

const props = defineProps<{ labels: LocaleMessages }>();
const labels = computed(() => props.labels);
let observedRevision = localConfiguration.value?.revision ?? 0;
const backendProfile = ref(loadBackendConnectionProfile());
const previousSaved = ref(JSON.stringify(backendProfile.value));
watch(localConfiguration, snapshot => {
  if (!snapshot) return;
  if (JSON.stringify(backendProfile.value) === previousSaved.value) {
    backendProfile.value = { ...snapshot.document.connection };
    observedRevision = snapshot.revision;
  }
  previousSaved.value = JSON.stringify(snapshot.document.connection);
});

const saving = ref(false);
const saveStatus = ref<"idle" | "saved" | "failed">("idle");
const saveError = ref("");
const dirty = computed(() => JSON.stringify(backendProfile.value) !== previousSaved.value);
const saveMessage = computed(() => {
  if (saveStatus.value === "failed") {
    if (/CONFLICT/.test(saveError.value)) return labels.value.localConfigurationConflict;
    return `${presentUserError(labels.value, saveError.value).primaryMessage} (${saveError.value})`;
  }
  if (dirty.value) return labels.value.backendConnectionUnsaved;
  return saveStatus.value === "saved" ? labels.value.backendConnectionSaved : "";
});

const testStatus = ref<"idle" | "testing" | "connected" | "failed">("idle");
const testError = ref("");
const testTarget = ref("");
const backendOpenApiResult = ref<BackendOpenApiResult | null>(null);
let testGeneration = 0;
watch(() => [backendProfile.value.scheme, backendProfile.value.host, backendProfile.value.port], () => {
  testGeneration += 1;
  testStatus.value = "idle";
  testTarget.value = "";
  testError.value = "";
  backendOpenApiResult.value = null;
  saveStatus.value = "idle";
}, { flush: "sync" });

const testMessage = computed(() => {
  if (testStatus.value === "testing") return labels.value.testingOpenApi;
  if (testStatus.value === "connected") return `${labels.value.openApiLoaded}: ${backendOpenApiResult.value?.openApiVersion}`;
  if (testStatus.value === "idle") return labels.value.openApiUntested;
  const error = testError.value;
  if (/SMA_EXTERNAL_IO_DISABLED/.test(error)) return labels.value.externalIoDisabled;
  if (/BACKEND_(HOST_REQUIRED|PORT_INVALID|ADDRESS_INVALID)/.test(error)) return labels.value.openApiAddressInvalid;
  if (/OPENAPI_REQUEST_TIMEOUT/.test(error)) return labels.value.openApiTimeout;
  if (/OPENAPI_(RESPONSE|DOCUMENT)_INVALID/.test(error)) return labels.value.openApiInvalidResponse;
  const status = error.match(/OPENAPI_REQUEST_FAILED:(\d+)/)?.[1];
  if (status) return `${labels.value.openApiHttpFailed} (${status})`;
  return labels.value.openApiUnreachable;
});

async function saveBackendConnection() {
  saving.value = true;
  saveError.value = "";
  try {
    backendProfile.value = await saveBackendConnectionProfile({ ...backendProfile.value }, observedRevision);
    observedRevision = currentRevision();
    saveStatus.value = "saved";
  } catch (error) {
    saveStatus.value = "failed";
    saveError.value = error instanceof Error ? error.message : String(error);
  } finally {
    saving.value = false;
  }
}

async function testBackendConnectionOpenApi() {
  const generation = ++testGeneration;
  const draft = { ...backendProfile.value };
  testStatus.value = "testing";
  backendOpenApiResult.value = null;
  testTarget.value = `${draft.scheme}://${String(draft.host).trim()}:${draft.port}/openapi.json`;
  try {
    testTarget.value = `${formatBackendOpenApiBaseUrl(draft)}/openapi.json`;
    const result = await testBackendDraftOpenApi(draft);
    if (generation !== testGeneration) return;
    backendOpenApiResult.value = result;
    testStatus.value = "connected";
  } catch (error) {
    if (generation !== testGeneration) return;
    testError.value = error instanceof Error ? error.message : String(error);
    testStatus.value = "failed";
  }
}
</script>

<template>
  <BackendConnectionPanel v-model:profile="backendProfile" :labels="labels" :saving="saving" :testing="testStatus === 'testing'" :save-status="saveStatus" :save-message="saveMessage" :test-status="testStatus" :test-message="testMessage" :test-target="testTarget" @save="saveBackendConnection" @test-open-api="testBackendConnectionOpenApi" />
  <OpenApiOperationCatalog v-if="backendOpenApiResult" :labels="labels" :result="backendOpenApiResult" />
</template>
