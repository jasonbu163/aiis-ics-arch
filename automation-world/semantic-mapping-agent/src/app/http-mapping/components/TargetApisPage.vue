<!-- 目标 API 支持手工或 OpenAPI 定义，单次测试使用统一预览确认。 -->
<script setup lang="ts">
import { ConsoleActionButton, ConsoleCard, StatusCapsule } from "@aw-ui";
import { computed, ref, watch } from "vue";
import { usePagination } from "../../../components/usePagination";
import type { BackendOpenApiOperation } from "../../connection/types";
import type { TargetApiConfiguration, TargetApiConfigurationInput, TargetApiParameter } from "../../twin-facts/types";
import { useHttpMessages } from "../messages";
import type { PostResult } from "../types";
import {
  jsonText, matchesFilter, parameterLocation, postStatusLabel, postStatusTone, readJsonScalar,
  scalarTypes, targetAddress, targetParameter, typeLabel,
} from "../ui";
import { useConfigPage } from "../useConfigPage";
import DeleteConfigurationDialog from "./DeleteConfigurationDialog.vue";
import HttpTable from "./HttpTable.vue";
import OpenApiPicker from "./OpenApiPicker.vue";
import PostPreviewDialog from "./PostPreviewDialog.vue";
import PostResultDetails from "./PostResultDetails.vue";
import SmaDialog from "./SmaDialog.vue";

defineProps<{ ioEnabled: boolean }>();
const ui = useHttpMessages();
const config = useConfigPage("targetApis");
const { ready, working, notice, errorMessage, deleteOpen, deleteName } = config;
const search = ref("");
const rows = computed(() => (config.document.value?.targetApis ?? [])
  .filter(row => matchesFilter(search.value, row.name, row.apiKey, row.path, row.url)));
const { page, pageSize, total, pagedItems } = usePagination(() => rows.value);
watch(search, () => { page.value = 1; });
const columns = computed(() => [
  { id: "name", title: ui.value.name, width: 174 },
  { id: "key", title: ui.value.key, width: 143 },
  { id: "address", title: ui.value.address, width: 273 },
  { id: "parameters", title: ui.value.parameters, width: 113 },
  { id: "state", title: ui.value.status, width: 146 },
  { id: "result", title: ui.value.sentResult, width: 151 },
  { id: "actions", title: ui.value.actions, width: 227, fixed: true },
]);

function buildDraft(target?: TargetApiConfiguration) {
  return {
    apiKey: target?.apiKey ?? "",
    name: target?.name ?? "",
    url: target?.url ?? "",
    path: target?.path ?? "",
    enabled: target?.enabled ?? true,
    timeoutMs: target?.timeoutMs ?? 5000,
    operationId: target?.operationId ?? null,
    schemaSource: target?.schemaSource ?? "manual",
    originType: target?.originType ?? "manual",
    originMaterialKey: target?.originMaterialKey ?? null,
    idempotencySupported: target?.idempotencySupported ?? false,
    bodyTemplate: jsonText(target?.bodyTemplate ?? {}),
    parameterSchema: target?.parameterSchema.map(parameter => ({ ...parameter })) ?? [],
    receiptPath: target?.receipt?.path ?? "",
    receiptValue: jsonText(target?.receipt?.equals),
  } satisfies Omit<TargetApiConfigurationInput, "bodyTemplate" | "httpMethod"> & {
    bodyTemplate: string; receiptPath: string; receiptValue: string;
  };
}

const locations = ["body", "query", "path", "header"] as const;
const picker = ref(false);
const editor = ref(false);
const form = ref<HTMLFormElement>();
const editingId = ref<string | null>(null);
const draft = ref(buildDraft());
let editorRevision = 0;

function edit(row?: TargetApiConfiguration) {
  draft.value = buildDraft(row);
  editorRevision = config.revision();
  editingId.value = row?.id ?? null;
  config.error.value = "";
  editor.value = true;
}

function selectOperation(operation: BackendOpenApiOperation, base: string) {
  edit();
  draft.value.name = operation.summary ?? operation.operationId ?? operation.path;
  draft.value.path = operation.path;
  draft.value.url = base ? base + operation.path : "";
  draft.value.operationId = operation.operationId;
  draft.value.schemaSource = "openapi";
  draft.value.bodyTemplate = jsonText(operation.bodyTemplate);
  draft.value.parameterSchema = operation.requestContract?.map(parameter => ({ ...parameter })) ?? [];
}

function addParameter() {
  draft.value.parameterSchema.push({ parameterKey: "", name: "", jsonPath: null, location: "body", dataType: "string", required: false });
}

function fallbackPathFromUrl(url: string) {
  const route = url.match(/^https?:\/\/[^/?#]+([^?#]*)/i)?.[1];
  if (route === undefined) throw new Error("SMA_HTTP_TARGET_URL_INVALID");
  return route || "/";
}

async function save() {
  if (!editor.value) return;
  try {
    const entry = draft.value;
    let template: unknown;
    try { template = JSON.parse(entry.bodyTemplate); } catch { throw new Error("SMA_HTTP_BODY_TEMPLATE_INVALID"); }
    if (!template || typeof template !== "object" || Array.isArray(template)) throw new Error("SMA_HTTP_BODY_TEMPLATE_INVALID");
    const url = entry.url.trim();
    const parameterSchema: TargetApiParameter[] = entry.parameterSchema.map(targetParameter);
    const payload: TargetApiConfigurationInput = {
      apiKey: entry.apiKey.trim(), name: entry.name.trim(), httpMethod: "POST",
      path: url ? fallbackPathFromUrl(url) : entry.path.trim(), url: url || null,
      enabled: entry.enabled, timeoutMs: entry.timeoutMs, operationId: entry.operationId,
      schemaSource: entry.schemaSource, originType: entry.originType, originMaterialKey: entry.originMaterialKey,
      idempotencySupported: entry.idempotencySupported, bodyTemplate: template as Record<string, unknown>, parameterSchema,
      receipt: entry.receiptPath || entry.receiptValue
        ? { path: entry.receiptPath.trim(), equals: readJsonScalar(entry.receiptValue) } : null,
    };
    if (await config.save(editingId.value, payload, editorRevision)) editor.value = false;
  } catch (caught) {
    config.report(caught);
  }
}

const testOpen = ref(false);
const testTarget = ref<TargetApiConfiguration | null>(null);
const sending = ref(false);
const results = ref(new Map<string, PostResult>());
const detailsOpen = ref(false);
const selectedResult = ref<PostResult | null>(null);
function test(target: TargetApiConfiguration) { testTarget.value = target; testOpen.value = true; }
function storeResult(id: string, result: PostResult) { results.value.set(id, result); }
function showResult(result: PostResult) { selectedResult.value = result; detailsOpen.value = true; }
</script>

<template>
  <ConsoleCard :title="ui.targetApis">
    <template #actions>
      <ConsoleActionButton :disabled="!ready || working" @click="picker = true">{{ ui.openApi }}</ConsoleActionButton>
      <ConsoleActionButton tone="primary" :disabled="!ready || working" @click="edit()">{{ ui.manual }}</ConsoleActionButton>
    </template>
    <template #refresh><ConsoleActionButton v-if="ready" :loading="working" @click="config.reload">{{ ui.reload }}</ConsoleActionButton></template>
    <p v-if="notice" class="notice" role="status">{{ ui[notice] }}</p>
    <p v-if="errorMessage && !editor && !deleteOpen" class="warning" role="alert">{{ errorMessage }}</p>
    <HttpTable v-model:page="page" v-model:page-size="pageSize" table-id="http-targets" :columns="columns" :total="total" :busy="working" :caption="ui.targetApis">
      <template #filters><input v-model="search" type="search" :aria-label="ui.search" :placeholder="ui.search"></template>
      <tr v-for="row in pagedItems" :key="row.id">
        <td><strong>{{ row.name }}</strong></td><td>{{ row.apiKey }}</td>
        <td><strong>{{ row.httpMethod }}</strong> <code>{{ targetAddress(row.url, row.path, config.document.value?.connection) }}</code></td>
        <td>{{ row.parameterSchema.length }}</td>
        <td><StatusCapsule :label="row.httpMethod !== 'POST' ? ui.legacy : row.enabled ? ui.active : ui.inactive" :tone="row.httpMethod === 'POST' && row.enabled ? 'success' : 'neutral'" /></td>
        <td><template v-for="result in [results.get(row.id)]" :key="row.id"><ConsoleActionButton v-if="result" variant="row" :tone="postStatusTone(result.status) === 'danger' ? 'danger' : 'secondary'" @click="showResult(result)">{{ postStatusLabel(ui, result.status) }}</ConsoleActionButton><span v-else>{{ ui.missing }}</span></template></td>
        <td><div class="console-row-actions">
          <ConsoleActionButton variant="row" :disabled="!row.enabled || row.httpMethod !== 'POST' || working || sending"
            :title="!row.enabled ? ui.inactive : row.httpMethod !== 'POST' ? ui.legacy : ui.testPost" @click="test(row)">{{ ui.testPost }}</ConsoleActionButton>
          <ConsoleActionButton tone="primary" variant="row" :disabled="working" @click="edit(row)">{{ ui.edit }}</ConsoleActionButton>
          <ConsoleActionButton tone="danger" variant="row" :disabled="working" @click="config.askDelete(row)">{{ ui.remove }}</ConsoleActionButton>
        </div></td>
      </tr>
    </HttpTable>
  </ConsoleCard>

  <OpenApiPicker v-model="picker" method="POST" :io-enabled="ioEnabled" @select="selectOperation" />
  <DeleteConfigurationDialog v-model="deleteOpen" :name="deleteName" :busy="working" :error="errorMessage" @confirm="config.remove" />
  <SmaDialog v-model="editor" :title="editingId ? ui.editTarget : ui.newTarget" :error="errorMessage">
    <form ref="form" class="http-stack" @submit.prevent="save">
      <div class="http-form-grid">
        <label class="field"><span>{{ ui.key }}</span><input v-model.trim="draft.apiKey" :readonly="!!editingId" required></label>
        <label class="field"><span>{{ ui.name }}</span><input v-model.trim="draft.name" required></label>
        <label class="field http-wide"><span>{{ ui.fullUrl }}</span><input v-model.trim="draft.url"><small>{{ ui.targetAddressHelp }}</small></label>
        <label v-if="!draft.url" class="field http-wide"><span>{{ ui.targetPath }}</span><input v-model.trim="draft.path" required></label>
        <label class="field"><span>{{ ui.timeout }}</span><input v-model.number="draft.timeoutMs" type="number" min="1" max="60000" step="1" required></label>
        <label class="http-checkbox"><input v-model="draft.enabled" type="checkbox"><span>{{ ui.enabled }}</span></label>
      </div>

      <section class="http-dialog-section">
        <div class="http-section-header"><h3>{{ ui.parameters }}</h3><ConsoleActionButton size="small" @click="addParameter">{{ ui.addParameter }}</ConsoleActionButton></div>
        <div class="http-detail-list">
          <div v-for="(parameter, index) in draft.parameterSchema" :key="index" class="http-binding">
            <div class="http-form-grid">
              <label class="field"><span>{{ ui.parameterLocation }}</span><select v-model="parameter.location">
                <option v-for="location in locations" :key="location" :value="location">{{ parameterLocation(ui, location) }}</option>
              </select></label>
              <label class="field"><span>{{ ui.parameterName }}</span><input v-model.trim="parameter.name" required></label>
              <label v-if="parameter.location === 'body'" class="field"><span>{{ ui.jsonPath }}</span><input :value="parameter.jsonPath ?? ''" :placeholder="parameter.name" @input="parameter.jsonPath = ($event.target as HTMLInputElement).value"></label>
              <label class="field"><span>{{ ui.kind }}</span><select v-model="parameter.dataType">
                <option v-for="type in scalarTypes" :key="type" :value="type">{{ typeLabel(ui, type) }}</option>
              </select></label>
              <label class="http-checkbox"><input type="checkbox" :checked="parameter.location === 'path' || parameter.required" :disabled="parameter.location === 'path'" @change="parameter.required = ($event.target as HTMLInputElement).checked"><span>{{ ui.required }}</span></label>
            </div>
            <ConsoleActionButton size="small" tone="danger" class="http-point-remove" @click="draft.parameterSchema.splice(index, 1)">{{ ui.remove }}</ConsoleActionButton>
          </div>
        </div>
      </section>

      <label class="field http-dialog-section"><span>{{ ui.bodyTemplate }}</span>
        <textarea v-model="draft.bodyTemplate" rows="6" spellcheck="false" class="http-text-area" required></textarea>
        <small>{{ ui.templateHelp }}</small>
      </label>

      <details class="http-dialog-section" :open="Boolean(draft.receiptPath || draft.receiptValue)">
        <summary>{{ ui.receipt }}</summary>
        <p class="hint">{{ ui.receiptHelp }}</p>
        <div class="http-form-grid">
          <label class="field"><span>{{ ui.receiptPath }}</span><input v-model.trim="draft.receiptPath"></label>
          <label class="field"><span>{{ ui.receiptValue }}</span><input v-model="draft.receiptValue"><small>{{ ui.conditionJsonExample }}</small></label>
        </div>
      </details>
    </form>
    <template #footer><ConsoleActionButton @click="editor = false">{{ ui.cancel }}</ConsoleActionButton><ConsoleActionButton tone="primary" :loading="working" @click="form?.requestSubmit()">{{ ui.save }}</ConsoleActionButton></template>
  </SmaDialog>

  <PostPreviewDialog v-model="testOpen" v-model:sending="sending" :target="testTarget" :io-enabled="ioEnabled" @result="storeResult" />
  <SmaDialog v-model="detailsOpen" :title="ui.sentResult">
    <PostResultDetails v-if="selectedResult" :result="selectedResult" />
    <template #footer><ConsoleActionButton @click="detailsOpen = false">{{ ui.close }}</ConsoleActionButton></template>
  </SmaDialog>
</template>
