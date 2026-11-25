<!-- 可复用合法值规则保留稳定类型、来源身份和严格的标量值。 -->
<script setup lang="ts">
import { ConsoleActionButton, ConsoleCard, StatusCapsule } from "@aw-ui";
import { computed, ref, watch } from "vue";
import { usePagination } from "../../../components/usePagination";
import type { CollectionFactDataType, MappingValueRuleConfiguration, MappingValueRuleConfigurationInput } from "../../twin-facts/types";
import { useHttpMessages } from "../messages";
import { inputText, jsonText, matchesFilter, readScalar, scalarTypes, typeLabel } from "../ui";
import { useConfigPage } from "../useConfigPage";
import DeleteConfigurationDialog from "./DeleteConfigurationDialog.vue";
import HttpTable from "./HttpTable.vue";
import SmaDialog from "./SmaDialog.vue";

const ui = useHttpMessages();
const config = useConfigPage("mappingValueRules");
const { ready, working, notice, errorMessage, deleteOpen, deleteName } = config;
const search = ref("");
const rules = computed(() => (config.document.value?.mappingValueRules ?? [])
  .filter(rule => matchesFilter(search.value, rule.name, rule.valueRuleKey, rule.originSourceKey, rule.originFactName)));
const sources = computed(() => config.document.value?.httpSources ?? []);
const { page, pageSize, total, pagedItems } = usePagination(() => rules.value);
watch(search, () => { page.value = 1; });
const columns = computed(() => [
  { id: "name", title: ui.value.name, width: 170 },
  { id: "key", title: ui.value.key, width: 146 },
  { id: "type", title: ui.value.kind, width: 142 },
  { id: "origin", title: ui.value.source, width: 181 },
  { id: "values", title: ui.value.allowedValues, width: 215 },
  { id: "status", title: ui.value.status, width: 114 },
  { id: "actions", title: ui.value.actions, width: 140, fixed: true },
]);

function buildDraft(rule?: MappingValueRuleConfiguration) {
  return {
    valueRuleKey: rule?.valueRuleKey ?? "",
    name: rule?.name ?? "",
    originSourceKey: rule?.originSourceKey ?? "",
    originFactName: rule?.originFactName ?? "",
    dataType: (rule?.dataType ?? "string") as CollectionFactDataType,
    enabled: rule?.enabled ?? true,
    values: rule?.values.map(inputText) ?? [],
  };
}

const draft = ref(buildDraft());
const editor = ref(false);
const form = ref<HTMLFormElement>();
const editingId = ref<string | null>(null);
const sourcePoints = computed(() => sources.value.find(source => source.sourceKey === draft.value.originSourceKey)?.points ?? []);
let editorRevision = 0;

function edit(rule?: MappingValueRuleConfiguration) {
  draft.value = buildDraft(rule);
  editorRevision = config.revision();
  editingId.value = rule?.id ?? null;
  config.error.value = "";
  editor.value = true;
}

function updatePoint() {
  const point = sourcePoints.value.find(point => point.pointKey === draft.value.originFactName);
  if (point) draft.value.dataType = point.dataType;
}

async function save() {
  if (!editor.value) return;
  try {
    const row = draft.value;
    const payload: MappingValueRuleConfigurationInput = {
      valueRuleKey: row.valueRuleKey.trim(), name: row.name.trim(), enabled: row.enabled, dataType: row.dataType,
      originSourceKey: row.originSourceKey || null, originFactName: row.originFactName || null,
      values: row.values.map((value, index) => {
        try { return readScalar(value, row.dataType); }
        catch { throw new Error(`SMA_INPUT_SCALAR_INVALID:${index + 1}`); }
      }),
    };
    if (await config.save(editingId.value, payload, editorRevision)) editor.value = false;
  } catch (caught) {
    config.report(caught);
  }
}
</script>

<template>
  <ConsoleCard :title="ui.valueRules" :help="ui.ruleRulesHelp" :help-label="ui.ruleRulesHelp" help-append-to="#sma-overlays">
    <template #actions><ConsoleActionButton tone="primary" :disabled="!ready || working" @click="edit()">{{ ui.add }}</ConsoleActionButton></template>
    <template #refresh><ConsoleActionButton v-if="ready" :loading="working" @click="config.reload">{{ ui.reload }}</ConsoleActionButton></template>
    <p v-if="notice" class="notice" role="status">{{ ui[notice] }}</p>
    <p v-if="errorMessage && !editor && !deleteOpen" class="warning" role="alert">{{ errorMessage }}</p>
    <HttpTable v-model:page="page" v-model:page-size="pageSize" table-id="http-value-rules" :columns="columns" :total="total" :busy="working" :caption="ui.valueRules">
      <template #filters><input v-model="search" type="search" :aria-label="ui.search" :placeholder="ui.search"></template>
      <tr v-for="rule in pagedItems" :key="rule.id">
        <td><strong>{{ rule.name }}</strong></td><td>{{ rule.valueRuleKey }}</td><td>{{ typeLabel(ui, rule.dataType) }}</td>
        <td>{{ rule.originSourceKey ? rule.originSourceKey + ' / ' + rule.originFactName : ui.standalone }}</td>
        <td><code v-if="rule.values.length">{{ rule.values.slice(0, 4).map(jsonText).join(', ') }}</code><span v-if="rule.values.length > 4"> +{{ rule.values.length - 4 }}</span><span v-if="!rule.values.length">{{ ui.missing }}</span></td>
        <td><StatusCapsule :label="!rule.enabled ? ui.inactive : rule.values.length ? ui.active : ui.rulePending" :tone="!rule.enabled ? 'neutral' : rule.values.length ? 'success' : 'warning'" /></td>
        <td><div class="console-row-actions">
          <ConsoleActionButton tone="primary" variant="row" :disabled="working" @click="edit(rule)">{{ ui.edit }}</ConsoleActionButton>
          <ConsoleActionButton tone="danger" variant="row" :disabled="working" @click="config.askDelete(rule)">{{ ui.remove }}</ConsoleActionButton>
        </div></td>
      </tr>
    </HttpTable>
  </ConsoleCard>

  <DeleteConfigurationDialog v-model="deleteOpen" :name="deleteName" :busy="working" :error="errorMessage" @confirm="config.remove" />
  <SmaDialog v-model="editor" :title="editingId ? ui.editRule : ui.newRule" :error="errorMessage">
    <form ref="form" class="http-stack" @submit.prevent="save">
      <div class="http-form-grid">
        <label class="field"><span>{{ ui.key }}</span><input v-model.trim="draft.valueRuleKey" :readonly="!!editingId" required></label>
        <label class="field"><span>{{ ui.name }}</span><input v-model.trim="draft.name" required></label>
        <label class="field">
          <span>{{ ui.ruleOrigin }}</span>
          <input v-if="editingId" :value="draft.originSourceKey ? draft.originSourceKey + ' / ' + draft.originFactName : ui.standalone" readonly>
          <select v-else v-model="draft.originSourceKey" @change="draft.originFactName = ''">
            <option value="">{{ ui.standalone }}</option>
            <option v-for="source in sources" :key="source.id" :value="source.sourceKey" :disabled="!source.points.length">{{ source.name }}</option>
          </select>
        </label>
        <label v-if="draft.originSourceKey && !editingId" class="field"><span>{{ ui.point }}</span><select v-model="draft.originFactName" required @change="updatePoint">
          <option value="" disabled>{{ ui.selectPoint }}</option>
          <option v-for="point in sourcePoints" :key="point.pointKey" :value="point.pointKey">{{ point.name }} · {{ point.pointKey }}</option>
        </select></label>
        <label class="field"><span>{{ ui.kind }}</span><select v-model="draft.dataType" :disabled="!!draft.originSourceKey">
          <option v-for="type in scalarTypes" :key="type" :value="type">{{ typeLabel(ui, type) }}</option>
        </select></label>
        <label class="http-checkbox"><input v-model="draft.enabled" type="checkbox"><span>{{ ui.enabled }}</span></label>
      </div>
      <section class="http-dialog-section">
        <div class="http-section-header"><h3>{{ ui.allowedValues }}</h3><ConsoleActionButton size="small" @click="draft.values.push(draft.dataType === 'boolean' ? 'false' : '')">{{ ui.addValue }}</ConsoleActionButton></div>
        <p v-if="!draft.values.length" class="hint">{{ ui.rulePending }}</p>
        <div v-for="(_, index) in draft.values" :key="index" class="http-row-fields">
          <label class="field"><span>{{ ui.value }} {{ index + 1 }}</span>
            <select v-if="draft.dataType === 'boolean'" v-model="draft.values[index]">
              <option value="true">true</option><option value="false">false</option>
            </select>
            <input v-else v-model="draft.values[index]">
          </label>
          <ConsoleActionButton tone="danger" size="small" @click="draft.values.splice(index, 1)">{{ ui.remove }}</ConsoleActionButton>
        </div>
      </section>
    </form>
    <template #footer><ConsoleActionButton @click="editor = false">{{ ui.cancel }}</ConsoleActionButton><ConsoleActionButton tone="primary" :loading="working" @click="form?.requestSubmit()">{{ ui.save }}</ConsoleActionButton></template>
  </SmaDialog>
</template>
