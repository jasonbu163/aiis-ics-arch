<!-- 映射按目标参数独立绑定点位或固定值，预览使用保存的映射与快照。 -->
<script setup lang="ts">
import { ConsoleActionButton, ConsoleCard, StatusCapsule } from "@aw-ui";
import { computed, ref, watch } from "vue";
import { usePagination } from "../../../components/usePagination";
import type {
  CollectionFactDataType, MappingConfiguration, MappingConfigurationBinding, MappingConfigurationInput, TargetApiParameter,
} from "../../twin-facts/types";
import { useHttpMessages } from "../messages";
import type { PostResult } from "../types";
import { inputText, matchesFilter, parameterLocation, postStatusLabel, postStatusTone, readScalar, typeLabel } from "../ui";
import { useConfigPage } from "../useConfigPage";
import DeleteConfigurationDialog from "./DeleteConfigurationDialog.vue";
import HttpTable from "./HttpTable.vue";
import PostPreviewDialog from "./PostPreviewDialog.vue";
import PostResultDetails from "./PostResultDetails.vue";
import SmaDialog from "./SmaDialog.vue";

defineProps<{ ioEnabled: boolean }>();
const ui = useHttpMessages();
const config = useConfigPage("mappings");
const { ready, working, notice, errorMessage, deleteOpen, deleteName } = config;
const targets = computed(() => config.document.value?.targetApis ?? []);
const targetNames = computed(() => new Map(targets.value.map(target => [target.apiKey, target.name])));
const sources = computed(() => config.document.value?.httpSources ?? []);
const rules = computed(() => config.document.value?.mappingValueRules ?? []);
const search = ref("");
const rows = computed(() => (config.document.value?.mappings ?? []).filter(mapping =>
  matchesFilter(search.value, mapping.name, mapping.mappingKey, mapping.targetApiKey, targetNames.value.get(mapping.targetApiKey))));
const { page, pageSize, total, pagedItems } = usePagination(() => rows.value);
watch(search, () => { page.value = 1; });
const columns = computed(() => [
  { id: "name", title: ui.value.name, width: 160 },
  { id: "key", title: ui.value.key, width: 135 },
  { id: "target", title: ui.value.target, width: 153 },
  { id: "interval", title: ui.value.interval, width: 116 },
  { id: "age", title: ui.value.maxAge, width: 150 },
  { id: "parameters", title: ui.value.bindings, width: 113 },
  { id: "status", title: ui.value.status, width: 120 },
  { id: "result", title: ui.value.sentResult, width: 152 },
  { id: "actions", title: ui.value.actions, width: 223, fixed: true },
]);

interface BindingDraft {
  kind: "" | "constant" | "fact";
  value: string;
  sourceKey: string;
  factName: string;
  valueRuleKey: string;
}
function bindingDraft(binding?: MappingConfigurationBinding, legacySource?: string | null): BindingDraft {
  return {
    kind: binding?.kind ?? "", value: inputText(binding?.value),
    sourceKey: binding?.sourceKey ?? legacySource ?? "", factName: binding?.factName ?? "",
    valueRuleKey: binding?.valueRuleKey ?? "",
  };
}

function buildDraft(mapping?: MappingConfiguration) {
  const target = targets.value.find(item => item.apiKey === mapping?.targetApiKey);
  return {
    mappingKey: mapping?.mappingKey ?? "",
    name: mapping?.name ?? "",
    intervalMs: mapping?.intervalMs ?? 1000,
    maxAgeMs: mapping ? mapping.maxAgeMs ?? "" : 10000,
    enabled: mapping?.enabled ?? true,
    targetApiKey: mapping?.targetApiKey ?? "",
    bindings: Object.fromEntries((target?.parameterSchema ?? []).map(parameter => [
      parameter.parameterKey, bindingDraft(mapping?.bindings[parameter.parameterKey], mapping?.sourceKey),
    ])) as Record<string, BindingDraft>,
  };
}

const editor = ref(false);
const draft = ref(buildDraft());
const form = ref<HTMLFormElement>();
const editingId = ref<string | null>(null);
const editingLegacy = ref(false);
let editorRevision = 0;
const target = computed(() => targets.value.find(target => target.apiKey === draft.value.targetApiKey));
const parameters = computed(() => (target.value?.parameterSchema ?? []).flatMap(parameter => {
  const binding = draft.value.bindings[parameter.parameterKey];
  return binding ? [{ parameter, binding }] : [];
}));

function edit(row?: MappingConfiguration) {
  draft.value = buildDraft(row);
  editorRevision = config.revision();
  editingId.value = row?.id ?? null;
  editingLegacy.value = Boolean(row && row.maxAgeMs == null);
  config.error.value = "";
  editor.value = true;
}

function changeTarget() {
  draft.value.bindings = Object.fromEntries((target.value?.parameterSchema ?? []).map(parameter => [parameter.parameterKey, bindingDraft()]));
}

function changeKind(binding: BindingDraft, parameter: TargetApiParameter) {
  if (binding.kind === "constant" && parameter.dataType === "boolean" && binding.value === "") binding.value = "false";
  if (!binding.kind) binding.valueRuleKey = "";
}

function compatible(point: CollectionFactDataType, parameter: CollectionFactDataType) {
  return point === parameter || (point === "integer" && parameter === "number");
}

function pointChoices(sourceKey: string, dataType: CollectionFactDataType) {
  return (sources.value.find(source => source.sourceKey === sourceKey)?.points ?? []).filter(point => compatible(point.dataType, dataType));
}

function sourceChoices(dataType: CollectionFactDataType) {
  return sources.value.filter(source => source.points.some(point => compatible(point.dataType, dataType)));
}

function ruleChoices(dataType: CollectionFactDataType) {
  return rules.value.filter(rule => rule.enabled && rule.valueRuleKey && rule.values.length && rule.dataType === dataType);
}

async function save() {
  if (!editor.value) return;
  try {
    const row = draft.value;
    const bindings = Object.fromEntries(parameters.value.flatMap(({ parameter, binding }): [string, MappingConfigurationBinding][] => {
      if (!binding.kind) return [];
      try {
        if (binding.kind === "fact" && (!binding.sourceKey || !binding.factName)) throw new Error("MISSING");
        return [[parameter.parameterKey, {
          kind: binding.kind, sourceKey: binding.kind === "fact" ? binding.sourceKey : null,
          factName: binding.kind === "fact" ? binding.factName : null,
          valueRuleKey: binding.valueRuleKey || null,
          value: binding.kind === "constant" ? readScalar(binding.value, parameter.dataType) : null,
        }]];
      } catch {
        throw new Error(`SMA_INPUT_BINDING_INVALID:${parameter.parameterKey}`);
      }
    }));
    const payload: MappingConfigurationInput = {
      mappingKey: row.mappingKey.trim(), name: row.name.trim(), targetApiKey: row.targetApiKey,
      enabled: row.enabled, intervalMs: row.intervalMs, maxAgeMs: typeof row.maxAgeMs === "number" ? row.maxAgeMs : null,
      sourceKey: null, bindings,
    };
    if (await config.save(editingId.value, payload, editorRevision)) editor.value = false;
  } catch (caught) {
    config.report(caught);
  }
}

const testOpen = ref(false);
const testMappingId = ref<string | null>(null);
const sending = ref(false);
const results = ref(new Map<string, PostResult>());
const detailsOpen = ref(false);
const selectedResult = ref<PostResult | null>(null);
function test(row: MappingConfiguration) { testMappingId.value = row.id; testOpen.value = true; }
function storeResult(id: string, result: PostResult) { results.value.set(id, result); }
function showResult(result: PostResult) { selectedResult.value = result; detailsOpen.value = true; }
</script>

<template>
  <ConsoleCard :title="ui.mappings" :help="ui.bindingHelp" :help-label="ui.bindingHelp" help-append-to="#sma-overlays">
    <template #actions><ConsoleActionButton tone="primary" :disabled="!ready || working || !targets.some(target => target.httpMethod === 'POST')" :title="!targets.some(target => target.httpMethod === 'POST') ? ui.selectTarget : ui.add" @click="edit()">{{ ui.add }}</ConsoleActionButton></template>
    <template #refresh><ConsoleActionButton v-if="ready" :loading="working" @click="config.reload">{{ ui.reload }}</ConsoleActionButton></template>
    <p v-if="notice" class="notice" role="status">{{ ui[notice] }}</p>
    <p v-if="errorMessage && !editor && !deleteOpen" class="warning" role="alert">{{ errorMessage }}</p>
    <HttpTable v-model:page="page" v-model:page-size="pageSize" table-id="http-mappings" :columns="columns" :total="total" :busy="working" :caption="ui.mappings">
      <template #filters><input v-model="search" type="search" :aria-label="ui.search" :placeholder="ui.search"></template>
      <tr v-for="row in pagedItems" :key="row.id">
        <td><strong>{{ row.name }}</strong></td><td>{{ row.mappingKey }}</td><td>{{ targetNames.get(row.targetApiKey) ?? row.targetApiKey }}</td>
        <td>{{ row.intervalMs }}</td><td>{{ row.maxAgeMs ?? ui.missing }}</td><td>{{ Object.keys(row.bindings).length }}</td>
        <td><StatusCapsule :label="row.maxAgeMs == null ? ui.legacy : row.enabled ? ui.active : ui.inactive" :tone="row.maxAgeMs != null && row.enabled ? 'success' : 'neutral'" /></td>
        <td><template v-for="result in [results.get(row.id)]" :key="row.id"><ConsoleActionButton v-if="result" variant="row" :tone="postStatusTone(result.status) === 'danger' ? 'danger' : 'secondary'" @click="showResult(result)">{{ postStatusLabel(ui, result.status) }}</ConsoleActionButton><span v-else>{{ ui.missing }}</span></template></td>
        <td><div class="console-row-actions">
          <ConsoleActionButton variant="row" :disabled="row.maxAgeMs == null || working || sending"
            :title="row.maxAgeMs == null ? ui.legacyHelp : ui.testMapping" @click="test(row)">{{ ui.testMapping }}</ConsoleActionButton>
          <ConsoleActionButton tone="primary" variant="row" :disabled="working" @click="edit(row)">{{ ui.edit }}</ConsoleActionButton>
          <ConsoleActionButton tone="danger" variant="row" :disabled="working" @click="config.askDelete(row)">{{ ui.remove }}</ConsoleActionButton>
        </div></td>
      </tr>
    </HttpTable>
  </ConsoleCard>

  <DeleteConfigurationDialog v-model="deleteOpen" :name="deleteName" :busy="working" :error="errorMessage" @confirm="config.remove" />
  <SmaDialog v-model="editor" :title="editingId ? ui.editMapping : ui.newMapping" :error="errorMessage">
    <form ref="form" class="http-stack" @submit.prevent="save">
      <div class="http-form-grid">
        <label class="field"><span>{{ ui.key }}</span><input v-model.trim="draft.mappingKey" :readonly="!!editingId" required></label>
        <label class="field"><span>{{ ui.name }}</span><input v-model.trim="draft.name" required></label>
        <label class="field"><span>{{ ui.target }}</span>
          <select v-model="draft.targetApiKey" required @change="changeTarget">
            <option value="" disabled>{{ ui.selectTarget }}</option>
            <option v-for="choice in targets.filter(item => item.httpMethod === 'POST' || item.apiKey === draft.targetApiKey)" :key="choice.id" :value="choice.apiKey">
              {{ choice.name }} · {{ choice.apiKey }}
            </option>
          </select>
        </label>
        <label class="field"><span>{{ ui.interval }}</span><input v-model.number="draft.intervalMs" type="number" min="1" max="86400000" step="1" required></label>
        <label class="field"><span>{{ ui.maxAge }}</span><input v-model.number="draft.maxAgeMs" type="number" min="1" max="604800000" step="1" :required="!editingLegacy"></label>
        <label class="http-checkbox"><input v-model="draft.enabled" type="checkbox"><span>{{ ui.enabled }}</span></label>
        <p v-if="editingLegacy" class="hint http-wide">{{ ui.legacyHelp }}</p>
      </div>
      <section v-if="parameters.length" class="http-dialog-section">
        <div class="http-section-header"><h3>{{ ui.bindings }}</h3></div>
        <p class="hint">{{ ui.bindingHelp }}</p>
        <div class="http-stack">
          <article v-for="{ parameter, binding } in parameters" :key="parameter.parameterKey" class="http-binding">
            <div class="http-section-header"><h3>{{ parameter.name }}</h3><span class="http-muted">{{ parameterLocation(ui, parameter.location) }} · {{ typeLabel(ui, parameter.dataType) }} · {{ parameter.required ? ui.required : ui.optional }}</span></div>
            <div class="http-form-grid">
              <label class="field"><span>{{ ui.binding }}</span><select v-model="binding.kind" @change="changeKind(binding, parameter)">
                <option value="">{{ ui.unbound }}</option><option value="fact">{{ ui.pointBinding }}</option><option value="constant">{{ ui.fixedBinding }}</option>
              </select></label>
              <template v-if="binding.kind === 'fact'">
                <label class="field"><span>{{ ui.source }}</span><select v-model="binding.sourceKey" required @change="binding.factName = ''">
                  <option value="" disabled>{{ ui.selectSource }}</option>
                  <option v-if="binding.sourceKey && !sourceChoices(parameter.dataType).some(source => source.sourceKey === binding.sourceKey)" :value="binding.sourceKey">{{ binding.sourceKey }}</option>
                  <option v-for="source in sourceChoices(parameter.dataType)" :key="source.id" :value="source.sourceKey">{{ source.name }} · {{ source.sourceKey }}</option>
                </select></label>
                <label class="field"><span>{{ ui.point }}</span><select v-model="binding.factName" :disabled="!binding.sourceKey" required>
                  <option value="" disabled>{{ ui.selectPoint }}</option>
                  <option v-if="binding.factName && !pointChoices(binding.sourceKey, parameter.dataType).some(point => point.pointKey === binding.factName)" :value="binding.factName">{{ binding.factName }}</option>
                  <option v-for="point in pointChoices(binding.sourceKey, parameter.dataType)" :key="point.pointKey" :value="point.pointKey">{{ point.name }} · {{ point.pointKey }}</option>
                </select></label>
              </template>
              <label v-if="binding.kind === 'constant'" class="field"><span>{{ ui.fixedBinding }}</span>
                <select v-if="parameter.dataType === 'boolean'" v-model="binding.value"><option value="true">true</option><option value="false">false</option></select>
                <input v-else v-model="binding.value" :required="parameter.dataType !== 'string'">
              </label>
              <label v-if="binding.kind" class="field"><span>{{ ui.useRule }}</span><select v-model="binding.valueRuleKey">
                <option value="">{{ ui.noRule }}</option>
                <option v-if="binding.valueRuleKey && !ruleChoices(parameter.dataType).some(rule => rule.valueRuleKey === binding.valueRuleKey)" :value="binding.valueRuleKey">{{ binding.valueRuleKey }}</option>
                <option v-for="rule in ruleChoices(parameter.dataType)" :key="rule.id" :value="rule.valueRuleKey">{{ rule.name }}</option>
              </select></label>
            </div>
          </article>
        </div>
      </section>
    </form>
    <template #footer><ConsoleActionButton @click="editor = false">{{ ui.cancel }}</ConsoleActionButton><ConsoleActionButton tone="primary" :loading="working" @click="form?.requestSubmit()">{{ ui.save }}</ConsoleActionButton></template>
  </SmaDialog>

  <PostPreviewDialog v-model="testOpen" v-model:sending="sending" :mapping-id="testMappingId" :io-enabled="ioEnabled" @result="storeResult" />
  <SmaDialog v-model="detailsOpen" :title="ui.sentResult">
    <PostResultDetails v-if="selectedResult" :result="selectedResult" />
    <template #footer><ConsoleActionButton @click="detailsOpen = false">{{ ui.close }}</ConsoleActionButton></template>
  </SmaDialog>
</template>
