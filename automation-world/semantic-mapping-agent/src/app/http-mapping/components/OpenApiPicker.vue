<!-- 显式读取保存连接或本地文档，在新增来源和目标前选定单条 OpenAPI 操作。 -->
<script setup lang="ts">
import { ConsoleActionButton } from "@aw-ui";
import { computed, ref, watch } from "vue";
import { formatBackendOpenApiBaseUrl, loadBackendConnectionProfile, normalizeBackendOpenApiDocument, testBackendDraftOpenApi } from "../../connection/api";
import type { BackendOpenApiOperation } from "../../connection/types";
import { localConfiguration } from "../../twin-facts/api/localConfiguration";
import { useHttpMessages } from "../messages";
import { describeError, matchesFilter } from "../ui";
import SmaDialog from "./SmaDialog.vue";

const props = defineProps<{ method: "GET" | "POST"; ioEnabled: boolean }>();
const emit = defineEmits<{ select: [operation: BackendOpenApiOperation, baseUrl: string] }>();
const open = defineModel<boolean>({ required: true });
const ui = useHttpMessages();
const input = ref<HTMLInputElement>();
const operations = ref<BackendOpenApiOperation[] | null>(null);
const selected = ref("");
const search = ref("");
const busy = ref(false);
const error = ref("");
const baseUrl = ref("");
const candidates = computed(() => (operations.value ?? localConfiguration.value?.document.catalog ?? [])
  .filter(operation => operation.method === props.method && matchesFilter(search.value, operation.path, operation.summary, operation.operationId)));
const selection = computed(() => candidates.value.find(op => identity(op) === selected.value));
const configuredAddress = computed(() => {
  try { return formatBackendOpenApiBaseUrl(loadBackendConnectionProfile()); } catch { return ""; }
});
watch(open, (shown) => {
  if (shown) {
    selected.value = "";
    search.value = "";
    error.value = "";
  }
});

function identity(operation: BackendOpenApiOperation) {
  return `${operation.path}:${operation.contentHash}`;
}

async function fromConnection() {
  busy.value = true;
  error.value = "";
  selected.value = "";
  try {
    const result = await testBackendDraftOpenApi(loadBackendConnectionProfile());
    if (result.baseUrl !== configuredAddress.value) throw new Error("SMA_CONFIGURATION_CONFLICT");
    operations.value = result.operations;
    baseUrl.value = result.baseUrl;
  } catch (caught) {
    error.value = describeError(caught);
  } finally {
    busy.value = false;
  }
}

async function fromFile(event: Event) {
  const element = event.target as HTMLInputElement;
  const file = element.files?.[0];
  element.value = "";
  if (!file) return;
  busy.value = true;
  error.value = "";
  selected.value = "";
  try {
    if (file.size > 10 * 1024 * 1024) throw new Error("SMA_CONFIGURATION_LIMIT_EXCEEDED");
    operations.value = await normalizeBackendOpenApiDocument(JSON.parse(await file.text()));
    baseUrl.value = "";
  } catch (caught) {
    error.value = describeError(caught);
  } finally {
    busy.value = false;
  }
}

function select() {
  if (!selection.value) return;
  emit("select", selection.value, baseUrl.value || configuredAddress.value);
  open.value = false;
}
</script>

<template>
  <SmaDialog v-model="open" :title="ui.openApiTitle" :error="error">
    <div class="http-main-actions">
      <ConsoleActionButton :loading="busy" :disabled="!ioEnabled || !configuredAddress" @click="fromConnection">{{ ui.openApiConnection }}</ConsoleActionButton>
      <ConsoleActionButton :disabled="busy" @click="input?.click()">{{ ui.openApiFile }}</ConsoleActionButton>
      <input ref="input" type="file" accept=".json,application/json" class="facts-file-input" @change="fromFile">
    </div>
    <div class="http-dialog-section http-form-grid">
      <label class="field"><span>{{ ui.search }}</span><input v-model="search" type="search"></label>
      <label class="field"><span>{{ ui.openApiTitle }}</span>
        <select v-model="selected" :disabled="busy || !candidates.length">
          <option value="" disabled>{{ ui.openApiTitle }}</option>
          <option v-for="operation in candidates" :key="identity(operation)" :value="identity(operation)">
            {{ operation.method }} {{ operation.path }}{{ operation.summary ? ' · ' + operation.summary : '' }}
          </option>
        </select>
      </label>
      <p v-if="!candidates.length" class="http-wide http-muted">{{ operations ? ui.empty : ui.openApiEmpty }}</p>
      <p v-if="selection?.normalizationStatus === 'unsupported'" class="http-wide warning">{{ ui.openApiUnsupported }} {{ selection.normalizationErrorCode }}</p>
    </div>
    <template #footer>
      <ConsoleActionButton @click="open = false">{{ ui.cancel }}</ConsoleActionButton>
      <ConsoleActionButton tone="primary" :disabled="!selection || busy" @click="select">{{ ui.openApiSelect }}</ConsoleActionButton>
    </template>
  </SmaDialog>
</template>
