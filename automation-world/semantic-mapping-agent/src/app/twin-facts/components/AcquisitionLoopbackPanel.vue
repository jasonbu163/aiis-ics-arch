<!-- 采集来源页的手工回环流程，使用已保存连接和选入的 GET。 -->
<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { ConsoleActionButton, ConsoleCard, useTableColumnWidths } from "@aw-ui";
import { ElDialog, ElTable, ElTableColumn } from "element-plus";
import { externalIoEnabled } from "../../connection/api";
import type { LocaleMessages } from "../../../locales";
import { formatBusinessTime } from "../../../console/time";
import { useAcquisitionLoopback } from "../store/acquisitionLoopback";
import AcquisitionPointsTable from "./AcquisitionPointsTable.vue";

const props = defineProps<{ labels: LocaleMessages; enabled: boolean }>();
const online = computed(() => props.enabled && externalIoEnabled());
const text = computed(() => props.labels.acquisition);
const {
  config, ready, busy, error, sources, choices, latest, missing, allPoints, history, detail,
  from, to, sourceSeq, preview, receipt, readback, sendState, materials, databases, sourceReady,
  mixed, canPost, canReadback, saved, restoreSaved, loadSources, sourceChanged, dbChanged, testLatest,
  applyHistory, pickSample, save, prepare, push, checkTarget, changeAllPoints, setMove,
} = useAcquisitionLoopback();
const dialog = ref(false);
const showTarget = ref(false);
const sourceOptions = computed(() => sources.value?.map(item => item.plcId) ?? []);
const mappingPoints = computed(() => (detail.value?.points ?? choices.value)
  .filter(point => allPoints.value || config.value.pointIds.includes(point.pointId)));
const historyMins = { sampledAt: 170, sampleId: 220, pointCount: 95, sourceType: 110 };
const historyWidth = useTableColumnWidths("sma", "acquisition.history", historyMins);
const errorLabel = computed(() => {
  const code = error.value;
  if (code.includes("RESULT_UNKNOWN")) return text.value.unknown;
  if (code.includes("SEQUENCE_INVALID")) return text.value.sequenceHelp;
  if (code.includes("TARGET_EQUALS_SOURCE")) return text.value.targetEqualsSource;
  if (code.includes("MATERIAL_MISSING")) return text.value.materialNeeded;
  if (code.includes("RESPONSE_INVALID")) return text.value.invalidResponse;
  if (code.includes("TIMEOUT")) return text.value.timeout;
  if (code.includes("EXTERNAL_IO_DISABLED")) return text.value.httpDisabled;
  if (code.toUpperCase().includes("CONFLICT") || code.includes("(409)")) return text.value.conflict;
  if (code.includes("HTTP") || code.includes("plc_facts")) return text.value.httpFailure;
  if (code.includes("POINTS_MISSING")) return text.value.missing;
  if (code.includes("SELECTION_REQUIRED")) return text.value.selectPoint;
  return text.value.failure;
});
async function openPreview() {
  await prepare();
  if (preview.value) dialog.value = true;
}
async function openTarget() {
  await checkTarget();
  if (readback.value) {
    dialog.value = false;
    showTarget.value = true;
  }
}
const timeLabels = (source: string | null | undefined) => source === "daa" ? text.value.daa : source === "external" ? text.value.external : "—";
onMounted(() => { void restoreSaved(); });
</script>

<template>
  <ConsoleCard :title="text.title" class="acquisition-card">
    <template #actions>
      <ConsoleActionButton tone="secondary" :disabled="Boolean(busy)" @click="restoreSaved">{{ text.reload }}</ConsoleActionButton>
      <ConsoleActionButton :disabled="!ready || !online || Boolean(busy)" @click="loadSources">{{ text.loadSources }}</ConsoleActionButton>
    </template>
    <div v-if="!online" class="warning" role="status">{{ text.httpDisabled }}</div>
    <p v-if="error && !dialog" class="warning acquisition-feedback" role="alert">{{ errorLabel }}<br><code>{{ error }}</code></p>
    <div class="acquisition-fields">
      <label class="field">
        <span>{{ text.material }}</span>
        <select v-model="config.materialKey" :disabled="!ready">
          <option value="">{{ text.select }}</option>
          <option v-for="item in materials" :key="item.materialKey" :value="item.materialKey">{{ item.name }} · {{ item.path }}</option>
        </select>
      </label>
      <label class="field">
        <span>{{ text.sourcePlc }}</span>
        <select v-model="config.plcId" @change="sourceChanged">
          <option value="">{{ text.select }}</option>
          <option v-if="config.plcId && !sourceOptions.includes(config.plcId)" :value="config.plcId">{{ config.plcId }}</option>
          <option v-for="plc in sourceOptions" :key="plc" :value="plc">{{ plc }}</option>
        </select>
      </label>
      <label class="field">
        <span>{{ text.sourceDb }}</span>
        <select v-model.number="config.dbNumber" @change="dbChanged">
          <option :value="0">{{ text.select }}</option>
          <option v-if="config.dbNumber && !databases.includes(config.dbNumber)" :value="config.dbNumber">{{ config.dbNumber }}</option>
          <option v-for="item in databases" :key="item" :value="item">{{ item }}</option>
        </select>
      </label>
    </div>
    <p v-if="ready && materials.length === 0" class="warning">{{ text.materialNeeded }}</p>
    <p v-if="sources?.length === 0" role="status">{{ text.noData }}</p>
    <div class="acquisition-actions">
      <ConsoleActionButton tone="secondary" :disabled="!online || !sourceReady || Boolean(busy)" @click="testLatest(true)">{{ text.loadPoints }}</ConsoleActionButton>
      <ConsoleActionButton :disabled="!online || !sourceReady || Boolean(busy)" @click="testLatest()">{{ text.testGet }}</ConsoleActionButton>
    </div>
    <fieldset class="acquisition-selection">
      <legend>{{ text.points }}</legend>
      <label><input type="checkbox" :checked="allPoints" @change="changeAllPoints(($event.target as HTMLInputElement).checked)">{{ text.allPoints }}</label>
      <div v-if="!allPoints" class="acquisition-checks">
        <label v-for="item in choices" :key="item.pointId">
          <input v-model="config.pointIds" type="checkbox" :value="item.pointId">{{ item.pointId }}
        </label>
      </div>
    </fieldset>
    <p v-if="busy" role="status">{{ labels.loading }}</p>
    <p v-if="missing.length" class="warning" role="status">{{ text.missing }} {{ missing.join(", ") }}</p>
    <p v-if="mixed" role="status">{{ text.mixed }}</p>
    <AcquisitionPointsTable v-if="latest" :labels="labels" :points="latest" table-id="acquisition.latest" />
  </ConsoleCard>

  <ConsoleCard :title="text.historyTitle" class="acquisition-card">
    <div class="acquisition-fields">
      <label class="field"><span>{{ text.from }}</span><input v-model="from" type="datetime-local" step="1"></label>
      <label class="field"><span>{{ text.to }}</span><input v-model="to" type="datetime-local" step="1"></label>
    </div>
    <div class="acquisition-actions">
      <ConsoleActionButton :disabled="!online || !sourceReady || !from || !to || Boolean(busy)" @click="applyHistory()">{{ text.search }}</ConsoleActionButton>
      <ConsoleActionButton v-if="history" tone="secondary" :title="text.resetWidths" @click="historyWidth.reset">{{ text.resetWidths }}</ConsoleActionButton>
    </div>
    <template v-if="history">
      <ElTable :key="historyWidth.tableVersion.value" :data="history.items" row-key="id" border :empty-text="text.noData" @header-dragend="historyWidth.resize">
        <ElTableColumn v-for="(minWidth, key) in historyMins" :key="key" :prop="key" :label="text[key]"
          :min-width="minWidth" :width="historyWidth.widths.value[key] || undefined" resizable>
          <template #default="{ row }">{{ key === 'sampledAt' ? formatBusinessTime(row.sampledAt) : key === 'sourceType' ? timeLabels(row.sourceType) : row[key] }}</template>
        </ElTableColumn>
        <ElTableColumn :label="text.actions" :width="128">
          <template #default="{ row }">
            <ConsoleActionButton tone="secondary" :disabled="Boolean(busy)" @click="pickSample(row.id)">{{ text.chooseSample }}</ConsoleActionButton>
          </template>
        </ElTableColumn>
      </ElTable>
      <div v-if="history.totalPages > 1" class="acquisition-actions">
        <ConsoleActionButton tone="secondary" :disabled="history.page <= 1 || Boolean(busy)" @click="applyHistory(history.page - 1)">{{ text.previous }}</ConsoleActionButton>
        <span>{{ history.page }} / {{ history.totalPages }}</span>
        <ConsoleActionButton tone="secondary" :disabled="history.page >= history.totalPages || Boolean(busy)" @click="applyHistory(history.page + 1)">{{ text.next }}</ConsoleActionButton>
      </div>
    </template>
    <template v-if="detail">
      <p role="status">{{ text.selectedSample }} <code>{{ detail.sampleId }}</code> · {{ formatBusinessTime(detail.sampledAt) }}</p>
      <AcquisitionPointsTable :labels="labels" :points="detail.points" table-id="acquisition.history-detail" />
    </template>
  </ConsoleCard>

  <ConsoleCard :title="text.targetTitle" class="acquisition-card">
    <p>{{ text.targetHelp }}</p>
    <div class="acquisition-fields">
      <label class="field"><span>{{ text.targetPlc }}</span><input v-model.trim="config.target.plcId" maxlength="128"></label>
      <label class="field"><span>{{ text.targetDb }}</span><input v-model.number="config.target.dbNumber" type="number" min="1" max="65535"></label>
      <label class="field"><span>{{ text.instance }}</span><input v-model.trim="config.target.instanceId" maxlength="128"></label>
      <label class="field"><span>{{ text.generation }}</span><input v-model.trim="config.target.sourceGeneration" maxlength="128"></label>
      <label class="field"><span>{{ text.groupId }}</span><input v-model.trim="config.groupId" maxlength="128"></label>
      <label class="field"><span>{{ text.configRevision }}</span><input v-model.trim="config.configRevision" maxlength="128"></label>
    </div>
    <fieldset v-if="mappingPoints.length" class="acquisition-selection">
      <legend>{{ text.mapping }}</legend>
      <p>{{ text.mappingHelp }}</p>
      <div v-for="point in mappingPoints" :key="point.pointId" class="acquisition-fields acquisition-mapping-row">
        <code>{{ point.pointId }} · {{ point.dataType }}</code>
        <label class="field"><span>{{ text.targetPointId }}</span><input :value="config.moves.find(rule => rule.from === point.pointId)?.to ?? ''" :placeholder="point.pointId" maxlength="128" @input="setMove(point.pointId, 'to', ($event.target as HTMLInputElement).value)"></label>
        <label class="field"><span>{{ text.targetPointName }}</span><input :value="config.moves.find(rule => rule.from === point.pointId)?.name ?? ''" :placeholder="point.name" maxlength="100" @input="setMove(point.pointId, 'name', ($event.target as HTMLInputElement).value)"></label>
      </div>
    </fieldset>
    <label class="field acquisition-sequence">
      <span>{{ text.sequence }}</span>
      <input v-model="sourceSeq" type="text" inputmode="numeric" aria-describedby="acquisition-sequence-help">
    </label>
    <p id="acquisition-sequence-help">{{ text.sequenceHelp }}</p>
    <div class="acquisition-actions">
      <ConsoleActionButton tone="secondary" :disabled="!sourceReady || !config.target.plcId || !config.target.dbNumber || !config.target.instanceId || !config.target.sourceGeneration || Boolean(busy)" @click="save">{{ text.save }}</ConsoleActionButton>
      <ConsoleActionButton v-if="!preview" :disabled="!online || !saved || !detail || !sourceSeq || Boolean(busy)" @click="openPreview">{{ text.preview }}</ConsoleActionButton>
      <ConsoleActionButton v-else :disabled="Boolean(busy)" @click="dialog = true">{{ text.preview }}</ConsoleActionButton>
    </div>
    <p v-if="saved" role="status">{{ text.saved }}</p>
    <p v-if="receipt" role="status">{{ text.committed }} · {{ receipt.receipt.outcome }} · {{ receipt.receipt.sampleId }}</p>
  </ConsoleCard>

  <ElDialog v-model="dialog" :title="text.preview" width="min(780px, 88vw)" append-to="#sma-overlays"
    :close-on-click-modal="false" :show-close="busy !== 'push'" :close-on-press-escape="busy !== 'push'">
    <template v-if="preview">
      <p class="acquisition-feedback"><code>POST {{ preview.url }}</code></p>
      <p>{{ text.sampleId }} <code>{{ preview.sampleId }}</code></p>
      <p>{{ text.sampledAt }} {{ formatBusinessTime(preview.sampledAt) }}</p>
      <pre class="acquisition-body" tabindex="0">{{ preview.body }}</pre>
      <p v-if="error" class="warning acquisition-feedback" role="alert">{{ errorLabel }}<br><code>{{ error }}</code></p>
      <p v-if="sendState === 'unknown'" role="status">{{ text.unknownHelp }}</p>
      <p v-if="receipt" role="status">HTTP {{ receipt.httpStatus }} · {{ receipt.receipt.status }} · {{ receipt.receipt.outcome }}</p>
      <p v-if="readback === null" role="status">{{ text.notFound }}</p>
    </template>
    <template #footer>
      <div class="acquisition-actions">
        <ConsoleActionButton tone="secondary" :disabled="Boolean(busy)" @click="dialog = false">{{ text.close }}</ConsoleActionButton>
        <ConsoleActionButton tone="secondary" :disabled="!online || !canReadback || Boolean(busy)" @click="openTarget">{{ text.readback }}</ConsoleActionButton>
        <ConsoleActionButton :disabled="!online || !canPost || Boolean(busy)" @click="push">{{ sendState === "unknown" ? text.retry : text.push }}</ConsoleActionButton>
      </div>
    </template>
  </ElDialog>

  <ElDialog v-model="showTarget" :title="text.readback" width="min(850px, 92vw)" append-to="#sma-overlays">
    <template v-if="readback">
      <p><code>{{ readback.sampleId }}</code> · {{ formatBusinessTime(readback.sampledAt) }}</p>
      <p>{{ readback.plcId }} · DB {{ readback.dbNumber }} · {{ timeLabels(readback.sourceType) }}</p>
      <AcquisitionPointsTable :labels="labels" :points="readback.points" table-id="acquisition.target-detail" />
    </template>
  </ElDialog>
</template>

<style scoped>
.acquisition-card { display: grid; min-width: 0; }
.acquisition-fields { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 13rem), 1fr)); gap: 0.75rem; margin-block: 0.7rem; }
.acquisition-fields input, .acquisition-fields select { min-width: 0; }
.acquisition-actions, .acquisition-checks { display: flex; flex-wrap: wrap; align-items: center; gap: 0.65rem; margin-block: 0.75rem; }
.acquisition-selection { border: 0; padding: 0; min-width: 0; margin-block: 1rem; }
.acquisition-selection label { display: inline-flex; align-items: center; gap: 0.35rem; }
.acquisition-mapping-row { align-items: center; }
.acquisition-mapping-row .field { display: grid; }
.acquisition-sequence { max-width: 24rem; }
.acquisition-feedback { overflow-wrap: anywhere; }
.acquisition-body { max-height: min(41vh, 23rem); overflow: auto; white-space: pre-wrap; overflow-wrap: anywhere; color: inherit; }
</style>
