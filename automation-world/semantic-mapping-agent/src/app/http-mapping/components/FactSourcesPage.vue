<!-- 事实来源管理 GET 地址、采集条件与稳定点位定义，手工测试只读。 -->
<script setup lang="ts">
import { ConsoleActionButton, ConsoleCard, StatusCapsule } from "@aw-ui";
import { computed, ref, watch } from "vue";
import { usePagination } from "../../../components/usePagination";
import { formatBackendBaseUrl, loadBackendConnectionProfile } from "../../connection/api";
import type { BackendOpenApiOperation } from "../../connection/types";
import type { SourceChoice } from "../../twin-facts/api/acquisition";
import { httpMapping } from "../api";
import { useHttpMessages } from "../messages";
import { pointDefinition, pointDraft } from "../sourceDraft";
import type { HttpSource, HttpSourceInput, SourceTestResult } from "../types";
import { useConfigPage } from "../useConfigPage";
import { describeError, jsonText, matchesFilter, readJsonScalar, responsePointCandidates } from "../ui";
import DeleteConfigurationDialog from "./DeleteConfigurationDialog.vue";
import HttpTable from "./HttpTable.vue";
import OpenApiPicker from "./OpenApiPicker.vue";
import PointValuesTable from "./PointValuesTable.vue";
import SmaDialog from "./SmaDialog.vue";
import SourcePointEditor from "./SourcePointEditor.vue";

defineProps<{ ioEnabled: boolean }>();
const ui = useHttpMessages();
const config = useConfigPage("httpSources");
const { ready, working, notice, errorMessage, deleteOpen, deleteName } = config;
const search = ref("");
const sources = computed(() => (config.document.value?.httpSources ?? [])
  .filter(source => matchesFilter(search.value, source.sourceKey, source.name, source.url)));
const { page, pageSize, pagedItems, total } = usePagination(() => sources.value);
watch(search, () => { page.value = 1; });
const columns = computed(() => [
  { id: "name", title: ui.value.name, width: 170 },
  { id: "sourceKey", title: ui.value.key, width: 150 },
  { id: "url", title: ui.value.address, width: 274 },
  { id: "interval", title: ui.value.interval, width: 125 },
  { id: "points", title: ui.value.countPoints, width: 110 },
  { id: "status", title: ui.value.status, width: 112 },
  { id: "actions", title: ui.value.actions, width: 216, fixed: true },
]);

function buildDraft(source?: HttpSource) {
  return {
    sourceKey: source?.sourceKey ?? "",
    name: source?.name ?? "",
    url: source?.url ?? "",
    intervalMs: source?.intervalMs ?? 1000,
    timeoutMs: source?.timeoutMs ?? 5000,
    enabled: source?.enabled ?? true,
    query: Object.entries(source?.query ?? {}).map(([key, value]) => ({ key, value })),
    responsePath: source?.responsePath ?? "",
    conditionPath: source?.responseCondition?.path ?? "",
    conditionValue: jsonText(source?.responseCondition?.equals),
    points: source?.points.map(pointDraft) ?? [],
  };
}

const draft = ref(buildDraft());
const editor = ref(false);
const form = ref<HTMLFormElement>();
const picker = ref(false);
const editingId = ref<string | null>(null);
let editorRevision = 0;
const openPoint = ref(-1);
const options = ref<SourceChoice[]>([]);
const optionsBusy = ref(false);
const optionsError = ref("");
const plc = ref("");
const db = ref<number>();
const historyId = ref("");
let editorGeneration = 0;

function edit(source?: HttpSource) {
  editorGeneration++;
  editingId.value = source?.id ?? null;
  editorRevision = config.revision();
  config.error.value = "";
  draft.value = buildDraft(source);
  options.value = [];
  optionsError.value = "";
  plc.value = "";
  db.value = undefined;
  historyId.value = "";
  openPoint.value = -1;
  editor.value = true;
}

function selectOperation(operation: BackendOpenApiOperation, base: string) {
  edit();
  draft.value.url = base + operation.path;
  draft.value.name = operation.summary ?? operation.operationId ?? operation.path;
  draft.value.query = (operation.requestContract ?? []).filter(parameter => parameter.location === "query")
    .map(parameter => ({ key: parameter.name, value: "" }));
}

async function lookup() {
  const generation = editorGeneration;
  optionsBusy.value = true;
  optionsError.value = "";
  try {
    const result = await httpMapping.acquisitionOptions();
    if (editor.value && generation === editorGeneration) options.value = result.items;
  } catch (caught) {
    if (generation === editorGeneration) optionsError.value = describeError(caught);
  } finally {
    optionsBusy.value = false;
  }
}

const databases = computed(() => options.value.find(item => item.plcId === plc.value)?.dbNumbers ?? []);
function chooseAcquisition(history: boolean) {
  try {
    const base = formatBackendBaseUrl(loadBackendConnectionProfile());
    const path = history ? `/history/${encodeURIComponent(historyId.value.trim())}` : "/latest";
    draft.value.url = `${base}/api/v1/acquisition-data${path}`;
    draft.value.conditionPath = "/code";
    draft.value.conditionValue = "200";
    draft.value.responsePath = "/data";
    draft.value.query = history ? [] : [{ key: "plcId", value: plc.value }, { key: "dbNumber", value: String(db.value) }];
    optionsError.value = "";
  } catch (caught) {
    optionsError.value = describeError(caught);
  }
}

function addPoint() {
  openPoint.value = draft.value.points.push(pointDraft()) - 1;
}

function revealInvalidField(event: Event) {
  if (!(event.target instanceof HTMLElement)) return;
  let details = event.target.closest("details");
  while (details) {
    details.open = true;
    details = details.parentElement?.closest("details") ?? null;
  }
}

async function save() {
  if (!editor.value) return;
  try {
    const entry = draft.value;
    const pairs = entry.query.map(({ key, value }) => [key.trim(), value] as const);
    if (new Set(pairs.map(([key]) => key)).size !== pairs.length) throw new Error("SMA_HTTP_QUERY_DUPLICATE");
    const payload: HttpSourceInput = {
      sourceKey: entry.sourceKey.trim(), name: entry.name.trim(), url: entry.url.trim(), enabled: entry.enabled,
      query: Object.fromEntries(pairs), intervalMs: entry.intervalMs, timeoutMs: entry.timeoutMs,
      responsePath: entry.responsePath.trim() || null,
      responseCondition: entry.conditionPath || entry.conditionValue
        ? { path: entry.conditionPath.trim(), equals: readJsonScalar(entry.conditionValue) } : null,
      points: entry.points.map(pointDefinition),
    };
    if (await config.save(editingId.value, payload, editorRevision)) editor.value = false;
  } catch (caught) {
    config.report(caught);
  }
}

const testOpen = ref(false);
const testBusy = ref(false);
const testSource = ref<HttpSource | null>(null);
const testResult = ref<SourceTestResult | null>(null);
const testError = ref("");
const candidate = ref<number>(-1);
let testGeneration = 0;
let testRevision = 0;
watch(testOpen, open => { if (!open) testGeneration++; }, { flush: "sync" });

async function runTest(source: HttpSource) {
  if (testBusy.value) return;
  const generation = ++testGeneration;
  testRevision = config.revision();
  testSource.value = source;
  testResult.value = null;
  testError.value = "";
  candidate.value = -1;
  testOpen.value = true;
  testBusy.value = true;
  try {
    const result = await httpMapping.testSource(source.sourceKey);
    if (generation === testGeneration) testResult.value = result;
  } catch (caught) {
    if (generation === testGeneration) testError.value = describeError(caught);
  } finally {
    testBusy.value = false;
  }
}

const candidates = computed(() => testResult.value && testSource.value && !testResult.value.errorCode
  ? responsePointCandidates(testResult.value.response, testSource.value.responsePath ?? "", testSource.value.url) : []);

function addCandidate() {
  const point = candidates.value[candidate.value];
  const source = config.document.value?.httpSources?.find(entry => entry.id === testSource.value?.id);
  if (!point || !source) return;
  if (testRevision !== config.revision()) {
    testError.value = ui.value.conflict;
    return;
  }
  testOpen.value = false;
  edit(source);
  let key = typeof point.selector?.value === "string" ? point.selector.value : point.name;
  if (!key || /\s|[\u0000-\u001f\u007f]/u.test(key) || new TextEncoder().encode(key).length > 256 || source.points.some(entry => entry.pointKey === key)) {
    let number = source.points.length + 1;
    while (source.points.some(entry => entry.pointKey === `point-${number}`)) number++;
    key = `point-${number}`;
  }
  openPoint.value = draft.value.points.push(pointDraft({ ...point, pointKey: key })) - 1;
}
</script>

<template>
  <ConsoleCard :title="ui.factSources" :help="ui.sourceHelp" :help-label="ui.sourceHelp" help-append-to="#sma-overlays">
    <template #actions>
      <ConsoleActionButton :disabled="!ready || working" @click="picker = true">{{ ui.openApi }}</ConsoleActionButton>
      <ConsoleActionButton tone="primary" :disabled="!ready || working" @click="edit()">{{ ui.manual }}</ConsoleActionButton>
    </template>
    <template #refresh><ConsoleActionButton v-if="ready" :loading="working" @click="config.reload">{{ ui.reload }}</ConsoleActionButton></template>
    <p v-if="notice" class="notice" role="status">{{ ui[notice] }}</p>
    <p v-if="errorMessage && !editor && !deleteOpen" class="warning" role="alert">{{ errorMessage }}</p>
    <HttpTable v-model:page="page" v-model:page-size="pageSize" table-id="http-sources" :columns="columns" :total="total" :busy="working" :caption="ui.factSources">
      <template #filters><input v-model="search" type="search" :aria-label="ui.search" :placeholder="ui.search"></template>
      <tr v-for="source in pagedItems" :key="source.id">
        <td><strong>{{ source.name }}</strong></td><td>{{ source.sourceKey }}</td><td><code>{{ source.url }}</code></td>
        <td>{{ source.intervalMs }}</td><td>{{ source.points.length }}</td>
        <td><StatusCapsule :label="source.enabled ? ui.active : ui.inactive" :tone="source.enabled ? 'success' : 'neutral'" /></td>
        <td><div class="console-row-actions">
          <ConsoleActionButton variant="row" :disabled="!ioEnabled || working || testBusy" :title="!ioEnabled ? ui.httpDisabled : ui.testGet" @click="runTest(source)">{{ ui.testGet }}</ConsoleActionButton>
          <ConsoleActionButton tone="primary" variant="row" :disabled="working" @click="edit(source)">{{ ui.edit }}</ConsoleActionButton>
          <ConsoleActionButton tone="danger" variant="row" :disabled="working" @click="config.askDelete(source)">{{ ui.remove }}</ConsoleActionButton>
        </div></td>
      </tr>
    </HttpTable>
  </ConsoleCard>

  <OpenApiPicker v-model="picker" method="GET" :io-enabled="ioEnabled" @select="selectOperation" />
  <DeleteConfigurationDialog v-model="deleteOpen" :name="deleteName" :busy="working" :error="errorMessage" @confirm="config.remove" />
  <SmaDialog v-model="editor" :title="editingId ? ui.editSource : ui.newSource" :error="errorMessage">
    <form ref="form" class="http-stack" @submit.prevent="save" @invalid.capture="revealInvalidField">
      <div class="http-form-grid">
        <label class="field"><span>{{ ui.key }}</span><input v-model.trim="draft.sourceKey" :readonly="!!editingId" required></label>
        <label class="field"><span>{{ ui.name }}</span><input v-model.trim="draft.name" required></label>
        <label class="field http-wide"><span>{{ ui.fullUrl }}</span><input v-model.trim="draft.url" required></label>
        <label class="field"><span>{{ ui.interval }}</span><input v-model.number="draft.intervalMs" type="number" min="1" max="86400000" step="1" required></label>
        <label class="field"><span>{{ ui.timeout }}</span><input v-model.number="draft.timeoutMs" type="number" min="1" max="60000" step="1" required></label>
        <label class="http-checkbox"><input v-model="draft.enabled" type="checkbox"><span>{{ ui.enabled }}</span></label>
      </div>

      <div class="http-inline">
        <ConsoleActionButton :loading="optionsBusy" :disabled="!ioEnabled" :title="!ioEnabled ? ui.httpDisabled : ui.lookupPlc" @click="lookup">{{ ui.lookupPlc }}</ConsoleActionButton>
        <p v-if="optionsError" class="warning" role="alert">{{ optionsError }}</p>
      </div>
      <div v-if="options.length" class="http-row-fields">
        <label class="field"><span>{{ ui.plc }}</span><select v-model="plc" @change="db = undefined">
          <option value="" disabled>{{ ui.selectPlc }}</option>
          <option v-for="item in options" :key="item.plcId" :value="item.plcId">{{ item.plcId }}</option>
        </select></label>
        <label class="field"><span>{{ ui.db }}</span><select v-model="db" :disabled="!plc">
          <option :value="undefined" disabled>{{ ui.selectDb }}</option>
          <option v-for="number in databases" :key="number" :value="number">{{ number }}</option>
        </select></label>
        <ConsoleActionButton :disabled="!db" @click="chooseAcquisition(false)">{{ ui.useLatest }}</ConsoleActionButton>
        <label class="field"><span>{{ ui.historyId }}</span><input v-model.trim="historyId"></label>
        <ConsoleActionButton :disabled="!db || !historyId" @click="chooseAcquisition(true)">{{ ui.useHistory }}</ConsoleActionButton>
      </div>

      <section class="http-dialog-section">
        <div class="http-section-header"><h3>{{ ui.query }}</h3><ConsoleActionButton size="small" @click="draft.query.push({ key: '', value: '' })">{{ ui.add }}</ConsoleActionButton></div>
        <div v-for="(item, index) in draft.query" :key="index" class="http-row-fields">
          <label class="field"><span>{{ ui.parameterName }}</span><input v-model.trim="item.key" required></label>
          <label class="field"><span>{{ ui.parameterValue }}</span><input v-model="item.value"></label>
          <ConsoleActionButton size="small" tone="danger" @click="draft.query.splice(index, 1)">{{ ui.remove }}</ConsoleActionButton>
        </div>
      </section>

      <div class="http-form-grid http-dialog-section">
        <label class="field"><span>{{ ui.responsePath }}</span><input v-model.trim="draft.responsePath"><small>{{ ui.responseRootHelp }}</small></label>
        <label class="field"><span>{{ ui.conditionPath }}</span><input v-model.trim="draft.conditionPath"></label>
        <label class="field"><span>{{ ui.conditionValue }}</span><input v-model="draft.conditionValue"><small>{{ ui.conditionJsonExample }}</small></label>
      </div>

      <section class="http-dialog-section">
        <div class="http-section-header"><h3>{{ ui.pointSettings }}</h3><ConsoleActionButton size="small" @click="addPoint">{{ ui.addPoint }}</ConsoleActionButton></div>
        <div class="http-detail-list">
          <SourcePointEditor v-for="(point, index) in draft.points" :key="index" :point="point" :expanded="index === openPoint" @remove="draft.points.splice(index, 1)" />
        </div>
      </section>
    </form>
    <template #footer>
      <ConsoleActionButton @click="editor = false">{{ ui.cancel }}</ConsoleActionButton>
      <ConsoleActionButton tone="primary" :loading="working" @click="form?.requestSubmit()">{{ ui.save }}</ConsoleActionButton>
    </template>
  </SmaDialog>

  <SmaDialog v-model="testOpen" :title="ui.getResult" :error="testError || testResult?.errorCode || ''">
    <p v-if="testBusy" role="status">{{ ui.loading }}</p>
    <div v-if="testResult" class="http-stack">
      <div class="http-inline"><strong>{{ testSource?.name }}</strong><code>{{ testSource?.url }}</code><StatusCapsule :label="ui.httpStatus + ' ' + (testResult.httpStatus ?? ui.missing)" /></div>
      <div v-if="!testResult.errorCode" class="http-row-fields">
        <label class="field"><span>{{ ui.selectFromResponse }}</span><select v-model="candidate" :disabled="!candidates.length">
          <option :value="-1" disabled>{{ candidates.length ? ui.selectPoint : ui.noPointCandidates }}</option>
          <option v-for="(point, index) in candidates" :key="index" :value="index">{{ point.name }} · {{ point.selector?.value ?? point.path }} · {{ jsonText(point.value) }}</option>
        </select></label>
        <ConsoleActionButton :disabled="candidate < 0" @click="addCandidate">{{ ui.addSelection }}</ConsoleActionButton>
      </div>
      <PointValuesTable :values="testResult.points" table-id="http-test-points" />
      <details class="http-dialog-section">
        <summary>{{ ui.rawResponse }}</summary>
        <pre v-if="testResult.response != null" class="http-code">{{ jsonText(testResult.response) }}</pre>
        <p v-else>{{ ui.noResponse }}</p>
      </details>
    </div>
    <template #footer><ConsoleActionButton @click="testOpen = false">{{ ui.close }}</ConsoleActionButton></template>
  </SmaDialog>
</template>
