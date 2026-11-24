<!-- 采集最新值及独立手工回环工作区，操作阶段与对账上下文仅存于会话。 -->
<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from "vue";
import { ConsoleActionButton, ConsoleCard, useTableColumnWidths } from "@aw-ui";
import { ElDialog, ElTable, ElTableColumn } from "element-plus";
import { externalIoEnabled, formatBackendBaseUrl } from "../../connection/api";
import { localConfiguration } from "../api/localConfiguration";
import type { LocaleMessages } from "../../../locales";
import { formatBusinessTime } from "../../../console/time";
import { useAcquisitionLoopback } from "../store/acquisitionLoopback";
import AcquisitionPointsTable from "./AcquisitionPointsTable.vue";

const props = defineProps<{ labels: LocaleMessages; enabled: boolean; readOnly?: boolean }>();
const emit = defineEmits<{ navigate: [id: string] }>();
const online = computed(() => props.enabled && externalIoEnabled());
const text = computed(() => props.labels.acquisition);
const {
  config, ready, busy, error, errorAt, sources, choices, latest, missing, allPoints, history, detail,
  from, to, sourceSeq, preview, receipt, readback, sendState, materials, databases, materialReady, pointsReady, rangeValid,
  mixed, canPost, canReadback, saved, restoreSaved, loadSources, sourceChanged, dbChanged, testLatest,
  applyHistory, pickSample, save, prepare, push, checkTarget, changeAllPoints, setMove, invalidate,
} = useAcquisitionLoopback();
const dialog = ref(false);
const showTarget = ref(false);
const leavingUnknown = ref(false);
const unknownReference = ref<{ id: string; when: string; destination: string } | null>(null);
const step = ref(0);
const visited = ref(0);
const stepTitle = ref<HTMLElement | null>(null);
const modalTitle = ref<HTMLElement | null>(null);
const steps = computed(() => [text.value.sourceStep, text.value.historyStep, text.value.targetStep, text.value.reviewStep]);
const connection = computed(() => {
  const profile = localConfiguration.value?.document.connection;
  return profile?.host ? formatBackendBaseUrl(profile) : "";
});
const sourceOptions = computed(() => sources.value?.map(item => item.plcId) ?? []);
const mappingPoints = computed(() => (detail.value?.points ?? choices.value)
  .filter(point => allPoints.value || config.value.pointIds.includes(point.pointId)));
const historyMins = { sampledAt: 170, sampleId: 220, pointCount: 95, sourceType: 110 };
const historyWidth = useTableColumnWidths("sma", "acquisition.history", historyMins);
const sourceBlocker = computed(() => {
  if (!online.value) return text.value.httpDisabled;
  if (!connection.value) return text.value.connectionRequired;
  if (!materialReady.value) return text.value.materialNeeded;
  if (!config.value.plcId) return text.value.plcRequired;
  if (!config.value.dbNumber) return text.value.dbRequired;
  return "";
});
const historyBlocker = computed(() => sourceBlocker.value || (!from.value ? text.value.startRequired
  : !to.value ? text.value.endRequired : !rangeValid.value ? text.value.rangeInvalid : ""));
const sampleBlocker = computed(() => {
  if (!detail.value) return text.value.sampleRequired;
  return mappingPoints.value.length === (allPoints.value ? detail.value.points.length : config.value.pointIds.length)
    && mappingPoints.value.length > 0 ? "" : text.value.missing;
});
const targetBlocker = computed(() => {
  const { target, plcId, dbNumber } = config.value;
  if (!target.plcId || !target.instanceId || !target.sourceGeneration) return text.value.targetRequired;
  if (!Number.isInteger(target.dbNumber) || target.dbNumber < 1 || target.dbNumber > 65535) return text.value.targetDbInvalid;
  if (target.plcId === plcId && target.dbNumber === dbNumber) return text.value.targetEqualsSource;
  return "";
});
const sequenceValid = computed(() => /^[1-9]\d{0,18}$/.test(sourceSeq.value)
  && BigInt(sourceSeq.value) <= 9223372036854775806n);
const reviewBlocker = computed(() => sourceBlocker.value || sampleBlocker.value || targetBlocker.value
  || (!sequenceValid.value ? text.value.sequenceHelp : !saved.value ? text.value.saveRequired : ""));
const readbackState = computed(() => busy.value === "readback" ? "loading"
  : errorAt.value === "readback" ? "failed" : readback.value ? "found" : "missing");
const summaries = computed(() => [
  [text.value.sourceSummary, `${config.value.plcId} / DB ${config.value.dbNumber}`],
  [text.value.targetTitle, `${config.value.target.plcId} / DB ${config.value.target.dbNumber}`],
  [text.value.instance, config.value.target.instanceId], [text.value.generation, config.value.target.sourceGeneration],
  [text.value.sequence, sourceSeq.value], [text.value.pointCount, mappingPoints.value.length],
  [text.value.sampleId, preview.value?.sampleId], [text.value.sampledAt, formatBusinessTime(preview.value?.sampledAt)],
]);
const errorLabel = computed(() => {
  const code = error.value;
  if (code.includes("RESULT_UNKNOWN")) return text.value.unknown;
  if (code.includes("SEQUENCE_INVALID")) return text.value.sequenceHelp;
  if (code.includes("TARGET_EQUALS_SOURCE")) return text.value.targetEqualsSource;
  if (code.includes("MATERIAL_MISSING")) return text.value.materialNeeded;
  if (code.includes("RESPONSE_INVALID")) return text.value.invalidResponse;
  if (code.includes("TIMEOUT")) return text.value.timeout;
  if (code.includes("TRANSPORT")) return text.value.connectionFailure;
  if (code.includes("EXTERNAL_IO_DISABLED")) return text.value.httpDisabled;
  if (code.toUpperCase().includes("CONFLICT") || code.includes("(409)")) return text.value.conflict;
  if (code.includes("HTTP") || code.includes("plc_facts")) return text.value.httpFailure;
  if (code.includes("POINTS_MISSING")) return text.value.missing;
  if (code.includes("SELECTION_REQUIRED")) return text.value.selectPoint;
  return text.value.failure;
});
async function goTo(next: number) {
  if (busy.value || sendState.value === "unknown" && next !== 3) return;
  step.value = next;
  visited.value = Math.max(visited.value, next);
  await nextTick();
  stepTitle.value?.focus();
}
function canEnter(next: number) {
  if (busy.value || sendState.value === "unknown" && next !== 3) return false;
  if (next === 0) return true;
  if (sourceBlocker.value || !pointsReady.value) return false;
  if (next === 1) return true;
  if (sampleBlocker.value) return false;
  return next === 2 || !reviewBlocker.value;
}
function advance(next: number) { if (canEnter(next)) void goTo(next); }
watch([sourceBlocker, sampleBlocker, reviewBlocker], ([source, sample, review]) => {
  const available = source || !pointsReady.value ? 0 : sample ? 1 : review ? 2 : 3;
  visited.value = Math.min(visited.value, available);
  if (!dialog.value && step.value > available) step.value = available;
});
watch(sendState, state => {
  if (state === "unknown" && preview.value) {
    unknownReference.value = {
      id: preview.value.sampleId, when: preview.value.sampledAt,
      destination: `${config.value.target.plcId} / DB ${config.value.target.dbNumber}`,
    };
  } else if (state === "done") {
    unknownReference.value = null;
  }
});
async function openPreview() {
  if (reviewBlocker.value) return;
  if (!preview.value) await prepare();
  if (preview.value) {
    leavingUnknown.value = false;
    dialog.value = true;
  }
}
async function openTarget() {
  showTarget.value = true;
  void nextTick(() => modalTitle.value?.focus());
  await checkTarget();
}
function closePreview(done?: () => void) {
  if (busy.value === "push") return;
  if (showTarget.value) {
    showTarget.value = false;
    void nextTick(() => modalTitle.value?.focus());
    return;
  }
  if (sendState.value === "unknown" && !leavingUnknown.value) {
    leavingUnknown.value = true;
    return;
  }
  leavingUnknown.value = false;
  if (done) done();
  else dialog.value = false;
}
function editFromPreview() {
  closePreview();
  if (sendState.value === "ready") void goTo(2);
}
function abandonPreview() {
  invalidate();
  leavingUnknown.value = false;
  dialog.value = false;
  void goTo(2);
}
const timeLabels = (source: string | null | undefined) => source === "daa" ? text.value.daa : source === "external" ? text.value.external : "—";
onMounted(() => { void restoreSaved(); });
</script>

<template>
  <nav v-if="!readOnly" :aria-label="text.stepsLabel" class="acquisition-stepper">
    <ol>
      <li v-for="(name, index) in steps" :key="name">
        <button type="button" :aria-current="step === index ? 'step' : undefined"
          :disabled="index > visited || !canEnter(index)" @click="advance(index)">
          <span class="acquisition-step-number">{{ index + 1 }}</span>
          <span>{{ name }}<small>{{ step === index ? text.currentStep : index < visited ? text.completedStep : text.pendingStep }}</small></span>
        </button>
      </li>
    </ol>
  </nav>
  <p v-if="!readOnly && unknownReference && !dialog" class="warning acquisition-feedback" role="status">
    {{ text.unknownHelp }} <code>{{ unknownReference.destination }}</code> ·
    <code>{{ unknownReference.id }}</code> · {{ formatBusinessTime(unknownReference.when) }}
  </p>
  <ConsoleCard v-if="readOnly || step === 0" :title="readOnly ? text.latestTitle : text.sourceStep" class="acquisition-card">
    <template #actions>
      <ConsoleActionButton tone="secondary" :disabled="Boolean(busy)" @click="restoreSaved">{{ text.reload }}</ConsoleActionButton>
      <ConsoleActionButton :disabled="!ready || !online || !connection || Boolean(busy)" @click="loadSources">{{ text.loadSources }}</ConsoleActionButton>
    </template>
    <p ref="stepTitle" tabindex="-1" role="status" class="acquisition-feedback">
      {{ labels.backendConnection }} · <code>{{ connection || '—' }}</code> · {{ online ? labels.httpEnabled : text.httpDisabled }}
    </p>
    <p v-if="!connection || !online" class="warning" role="status">
      {{ !online ? text.httpDisabled : text.connectionRequired }}
      <ConsoleActionButton tone="secondary" @click="emit('navigate', 'connection')">{{ labels.navBackendConnection }}</ConsoleActionButton>
    </p>
    <p v-if="error && ['load', 'options', 'latest'].includes(errorAt)" class="warning acquisition-feedback" role="alert">{{ errorLabel }}<br><code>{{ error }}</code></p>
    <fieldset class="acquisition-fieldset" :disabled="Boolean(busy)">
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
    <p v-if="ready && !materialReady" class="warning" role="status">
      {{ text.materialNeeded }} <ConsoleActionButton tone="secondary" @click="emit('navigate', 'api-materials')">{{ labels.apiMaterialsTitle }}</ConsoleActionButton>
    </p>
    <p v-if="sources === null && connection && online" role="status">{{ text.loadSourcesHint }}</p>
    <p v-if="sources?.length === 0" role="status">{{ text.noData }}</p>
    <div class="acquisition-actions">
      <ConsoleActionButton tone="secondary" :disabled="Boolean(sourceBlocker || busy)" @click="testLatest(true)">{{ text.loadPoints }}</ConsoleActionButton>
      <ConsoleActionButton tone="secondary" :disabled="Boolean(sourceBlocker || busy || !pointsReady)" @click="testLatest()">{{ text.testGet }}</ConsoleActionButton>
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
    </fieldset>
    <p v-if="busy" role="status">{{ labels.loading }}</p>
    <p v-if="missing.length" class="warning" role="status">{{ text.missing }} {{ missing.join(", ") }}</p>
    <p v-if="mixed && !readOnly" role="status">{{ text.mixed }}</p>
    <AcquisitionPointsTable v-if="latest" :labels="labels" :points="latest"
      :table-id="readOnly ? 'acquisition.latest' : 'acquisition.loopback.latest'" />
    <template #footer>
      <div class="acquisition-step-footer">
        <p v-if="sourceBlocker || !pointsReady" role="status">{{ sourceBlocker || text.selectPoint }}</p>
        <ConsoleActionButton v-if="!readOnly" tone="primary" :disabled="!canEnter(1)" @click="advance(1)">{{ text.continueHistory }}</ConsoleActionButton>
      </div>
    </template>
  </ConsoleCard>

  <ConsoleCard v-if="!readOnly && step === 1" :title="text.historyStep" class="acquisition-card">
    <p ref="stepTitle" tabindex="-1" class="acquisition-feedback">{{ text.sourceSummary }} · <code>{{ config.plcId }} / DB {{ config.dbNumber }}</code></p>
    <div class="acquisition-fields">
      <label class="field"><span>{{ text.from }}</span><input v-model="from" type="datetime-local" step="1"></label>
      <label class="field"><span>{{ text.to }}</span><input v-model="to" type="datetime-local" step="1"></label>
    </div>
    <div class="acquisition-actions">
      <ConsoleActionButton :disabled="Boolean(historyBlocker || busy)" :aria-describedby="historyBlocker ? 'acquisition-history-blocker' : undefined" @click="applyHistory()">{{ text.search }}</ConsoleActionButton>
      <ConsoleActionButton v-if="history" tone="secondary" :title="text.resetWidths" @click="historyWidth.reset">{{ text.resetWidths }}</ConsoleActionButton>
    </div>
    <p v-if="historyBlocker" id="acquisition-history-blocker" role="status">{{ historyBlocker }}</p>
    <p v-else-if="busy === 'history' || busy === 'detail'" role="status">{{ labels.loading }}</p>
    <p v-else-if="error && ['history', 'detail'].includes(errorAt)" class="warning acquisition-feedback" role="alert">{{ errorLabel }}<br><code>{{ error }}</code></p>
    <p v-else-if="!history" role="status">{{ text.historyNotQueried }}</p>
    <template v-if="history">
      <ElTable :key="historyWidth.tableVersion.value" :data="history.items" row-key="id" border :empty-text="text.noData" @header-dragend="historyWidth.resize">
        <ElTableColumn v-for="(minWidth, key) in historyMins" :key="key" :prop="key" :label="text[key]"
          :min-width="minWidth" :width="historyWidth.widths.value[key] || undefined" resizable>
          <template #default="{ row }">{{ key === 'sampledAt' ? formatBusinessTime(row.sampledAt) : key === 'sourceType' ? timeLabels(row.sourceType) : row[key] }}</template>
        </ElTableColumn>
        <ElTableColumn :label="text.actions" :width="160" align="center" fixed="right">
          <template #default="{ row }">
            <ConsoleActionButton tone="secondary" variant="row" :disabled="Boolean(busy) || detail?.id === row.id" @click="pickSample(row.id)">{{ detail?.id === row.id ? text.sampleChosen : text.chooseSample }}</ConsoleActionButton>
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
    <template #footer>
      <div class="acquisition-step-footer">
        <p v-if="sampleBlocker" role="status">{{ sampleBlocker }}</p>
        <div class="acquisition-footer-actions">
          <ConsoleActionButton tone="secondary" :disabled="Boolean(busy)" @click="advance(0)">{{ text.backStep }}</ConsoleActionButton>
          <ConsoleActionButton tone="primary" :disabled="!canEnter(2)" @click="advance(2)">{{ text.continueTarget }}</ConsoleActionButton>
        </div>
      </div>
    </template>
  </ConsoleCard>

  <ConsoleCard v-if="!readOnly && step === 2" :title="text.targetStep" class="acquisition-card">
    <p ref="stepTitle" tabindex="-1" class="acquisition-feedback">{{ text.sourceSummary }} · <code>{{ config.plcId }} / DB {{ config.dbNumber }}</code> · {{ detail?.sampleId }} · {{ text.pointCount }} {{ mappingPoints.length }} · {{ formatBusinessTime(detail?.sampledAt) }}</p>
    <p>{{ text.targetHelp }}</p>
    <fieldset class="acquisition-fieldset" :disabled="Boolean(busy)">
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
    </fieldset>
    <p v-if="error && errorAt === 'save'" class="warning acquisition-feedback" role="alert">{{ errorLabel }}<br><code>{{ error }}</code></p>
    <p v-else-if="busy === 'save'" role="status">{{ labels.loading }}</p>
    <p v-else-if="saved" role="status">{{ text.saved }}</p>
    <template #footer>
      <div class="acquisition-step-footer">
        <p v-if="reviewBlocker" role="status">{{ reviewBlocker }}</p>
        <div class="acquisition-footer-actions">
          <ConsoleActionButton tone="secondary" :disabled="Boolean(busy)" @click="advance(1)">{{ text.backStep }}</ConsoleActionButton>
          <ConsoleActionButton tone="secondary" :disabled="Boolean(busy || targetBlocker || sampleBlocker || sourceBlocker || saved)" @click="save">{{ text.save }}</ConsoleActionButton>
          <ConsoleActionButton tone="primary" :disabled="!canEnter(3)" @click="advance(3)">{{ text.continueReview }}</ConsoleActionButton>
        </div>
      </div>
    </template>
  </ConsoleCard>

  <ConsoleCard v-if="!readOnly && step === 3" :title="text.reviewStep" class="acquisition-card">
    <p ref="stepTitle" tabindex="-1">{{ text.reviewHint }}</p>
    <dl class="acquisition-summary">
      <div v-for="[label, value] in summaries.slice(0, 6)" :key="label"><dt>{{ label }}</dt><dd>{{ value }}</dd></div>
    </dl>
    <p v-if="receipt" role="status">{{ text.committed }} · {{ receipt.receipt.outcome }} · <code>{{ receipt.receipt.sampleId }}</code></p>
    <p v-if="error && errorAt === 'preview'" class="warning acquisition-feedback" role="alert">{{ errorLabel }}<br><code>{{ error }}</code></p>
    <p v-if="busy === 'preview'" role="status">{{ labels.loading }}</p>
    <template #footer>
      <div class="acquisition-step-footer">
        <p v-if="reviewBlocker" role="status">{{ reviewBlocker }}</p>
        <div class="acquisition-footer-actions">
          <ConsoleActionButton tone="secondary" :disabled="!canEnter(2)" @click="advance(2)">{{ text.backStep }}</ConsoleActionButton>
          <ConsoleActionButton tone="primary" :disabled="Boolean(busy || reviewBlocker)" @click="openPreview">{{ text.preview }}</ConsoleActionButton>
        </div>
      </div>
    </template>
  </ConsoleCard>

  <ElDialog v-if="!readOnly" v-model="dialog" :title="showTarget ? text.readback : text.preview"
    class="sma-acquisition-dialog" width="min(800px, 92vw)" align-center append-to="#sma-overlays"
    :close-on-click-modal="false" :show-close="busy !== 'push'" :close-on-press-escape="busy !== 'push'"
    :before-close="closePreview" @opened="modalTitle?.focus()" @closed="showTarget = false; stepTitle?.focus()">
    <div ref="modalTitle" tabindex="-1" class="acquisition-dialog-content">
      <template v-if="showTarget">
        <p class="acquisition-feedback">{{ text.targetTitle }} · <code>{{ config.target.plcId }} / DB {{ config.target.dbNumber }}</code> · <code>{{ preview?.sampleId }}</code></p>
        <p v-if="readbackState === 'loading'" role="status">{{ labels.loading }}</p>
        <p v-else-if="readbackState === 'failed'" class="warning acquisition-feedback" role="alert">{{ errorLabel }}<br><code>{{ error }}</code></p>
        <p v-else-if="readbackState === 'missing'" role="status">{{ text.notFound }}</p>
        <template v-else-if="readback">
          <p class="acquisition-feedback">{{ text.sampledAt }} · {{ formatBusinessTime(readback.sampledAt) }} · {{ timeLabels(readback.sourceType) }}</p>
          <AcquisitionPointsTable :labels="labels" :points="readback.points" table-id="acquisition.target-detail" />
        </template>
      </template>
      <template v-else-if="preview">
        <dl class="acquisition-summary">
          <div v-for="[label, value] in summaries" :key="label"><dt>{{ label }}</dt><dd>{{ value }}</dd></div>
        </dl>
        <p v-if="busy === 'push'" role="status">{{ text.sending }}</p>
        <p v-if="error && errorAt === 'push'" class="warning acquisition-feedback" role="alert">{{ errorLabel }}<br><code>{{ error }}</code></p>
        <p v-if="sendState === 'unknown'" role="status">{{ text.unknownHelp }}</p>
        <p v-if="leavingUnknown" class="warning" role="status">{{ text.leaveUnknownHint }}</p>
        <p v-if="receipt" role="status">HTTP {{ receipt.httpStatus }} · {{ receipt.receipt.status }} · {{ receipt.receipt.outcome }}</p>
        <p class="acquisition-feedback"><code>POST {{ preview.url }}</code></p>
        <pre class="acquisition-body" tabindex="0">{{ preview.body }}</pre>
      </template>
    </div>
    <template #footer>
      <div class="acquisition-footer-actions">
        <ConsoleActionButton v-if="showTarget" tone="secondary" @click="closePreview()">{{ text.close }}</ConsoleActionButton>
        <template v-else>
          <ConsoleActionButton tone="secondary" :disabled="Boolean(busy)" @click="editFromPreview">
            {{ leavingUnknown ? text.keepForLater : sendState === 'ready' ? text.returnToEdit : text.close }}
          </ConsoleActionButton>
          <ConsoleActionButton v-if="leavingUnknown" tone="secondary" :disabled="Boolean(busy)" @click="abandonPreview">{{ text.discardPending }}</ConsoleActionButton>
          <ConsoleActionButton v-if="canPost" :tone="sendState === 'unknown' ? 'secondary' : 'primary'" :disabled="!online || Boolean(busy)" @click="push">{{ sendState === "unknown" ? text.retry : text.push }}</ConsoleActionButton>
          <ConsoleActionButton v-if="canReadback" tone="primary" :disabled="!online || Boolean(busy)" @click="openTarget">{{ text.readback }}</ConsoleActionButton>
        </template>
      </div>
    </template>
  </ElDialog>
</template>

<style scoped>
.acquisition-card { display: grid; min-width: 0; }
.acquisition-stepper ol { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 10rem), 1fr)); gap: .5rem; list-style: none; margin: 0 0 .75rem; padding: 0; }
.acquisition-stepper button { display: flex; width: 100%; align-items: center; gap: .55rem; padding: .6rem; border: 1px solid var(--agent-border); border-radius: var(--agent-control-radius); text-align: start; color: var(--agent-text); background: var(--agent-surface); font: inherit; }
.acquisition-stepper button[aria-current="step"] { border-color: var(--agent-accent); background: var(--agent-surface-muted); font-weight: 650; }
.acquisition-stepper button:disabled { color: var(--agent-text-muted); cursor: default; }
.acquisition-stepper small { display: block; color: var(--agent-text-muted); }
.acquisition-step-number { align-self: flex-start; color: var(--agent-accent-strong); font-variant-numeric: tabular-nums; }
.acquisition-fieldset { border: 0; padding: 0; margin: 0; min-width: 0; }
.acquisition-fields { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 13rem), 1fr)); gap: 0.75rem; margin-block: 0.7rem; }
.acquisition-fields input, .acquisition-fields select { min-width: 0; }
.acquisition-actions, .acquisition-checks { display: flex; flex-wrap: wrap; align-items: center; gap: 0.65rem; margin-block: 0.75rem; }
.acquisition-selection { border: 0; padding: 0; min-width: 0; margin-block: 1rem; }
.acquisition-selection label { display: inline-flex; align-items: center; gap: 0.35rem; }
.acquisition-mapping-row { align-items: center; }
.acquisition-mapping-row .field { display: grid; }
.acquisition-sequence { max-width: 24rem; }
.acquisition-feedback { overflow-wrap: anywhere; }
.acquisition-step-footer { display: flex; align-items: center; flex-wrap: wrap; gap: .75rem; }
.acquisition-step-footer p { margin: 0; }
.acquisition-step-footer > :last-child { margin-inline-start: auto; }
.acquisition-footer-actions { display: flex; flex-wrap: wrap; justify-content: flex-end; align-items: center; gap: .55rem; }
.acquisition-footer-actions :deep(.el-button + .el-button) { margin-left: 0; }
.acquisition-summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 13rem), 1fr)); gap: .6rem 1rem; padding: .7rem; margin: .35rem 0; border: 1px solid var(--agent-border); border-radius: var(--agent-control-radius); background: var(--agent-surface-muted); }
.acquisition-summary dt { color: var(--agent-text-muted); }
.acquisition-summary dd { margin: .15rem 0 0; overflow-wrap: anywhere; }
.acquisition-body { white-space: pre-wrap; overflow-wrap: anywhere; color: inherit; margin: 0; }
.acquisition-dialog-content { display: grid; gap: .5rem; min-width: 0; }
.acquisition-dialog-content p { margin: .25rem 0; }
</style>

<style>
#sma-overlays .sma-acquisition-dialog { display: flex; flex-direction: column; max-height: calc(100vh - 2rem); min-width: 0; }
#sma-overlays .sma-acquisition-dialog .el-dialog__header,
#sma-overlays .sma-acquisition-dialog .el-dialog__footer { flex: none; }
#sma-overlays .sma-acquisition-dialog .el-dialog__body { min-height: 0; min-width: 0; overflow: auto; }
</style>
