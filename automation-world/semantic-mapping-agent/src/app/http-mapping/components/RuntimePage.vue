<!-- 采集和上报独立启停，展示实际 HTTP 在途、排队处置和各映射结果。 -->
<script setup lang="ts">
import { ConsoleActionButton, ConsoleCard, StatusCapsule } from "@aw-ui";
import { computed, ref } from "vue";
import { usePagination } from "../../../components/usePagination";
import { formatBusinessTime } from "../../../console/time";
import { localConfiguration } from "../../twin-facts/api/localConfiguration";
import { httpMapping } from "../api";
import { useHttpMessages } from "../messages";
import type { PostResult, RuntimeLimits, RuntimeSide } from "../types";
import { describeError, matchesFilter, postStatusLabel } from "../ui";
import { usePoll } from "../usePoll";
import HttpTable from "./HttpTable.vue";
import PostResultDetails from "./PostResultDetails.vue";
import SmaDialog from "./SmaDialog.vue";

const props = defineProps<{ native: boolean; ioEnabled: boolean }>();
const ui = useHttpMessages();
const { data: status, busy, error, refresh, publish } = usePoll(props.native, httpMapping.status);
const sides = ["get", "post"] as const;
const pending = ref({ get: false, post: false });
const sideError = ref({ get: "", post: "" });
const liveMetrics = ["active", "inFlight", "queued", "completed"] as const;
const counters = ["failed", "blocked", "timedOut", "unknown", "saturated", "skipped", "discarded", "peakInFlight", "peakQueued"] as const;
const configuration = computed(() => localConfiguration.value?.document);
const limits = computed<RuntimeLimits | undefined>(() => {
  const document = configuration.value;
  if (!document) return undefined;
  if (document.runtimeLimits) return document.runtimeLimits;
  const get = status.value?.get.limits;
  const post = status.value?.post.limits;
  if (!get?.concurrency || !post?.concurrency || !post.perTarget) return undefined;
  return {
    getConcurrency: get.concurrency, getQueue: get.queue,
    postConcurrency: post.concurrency, postQueue: post.queue, perTargetConcurrency: post.perTarget,
  };
});
const limitKeys = {
  get: ["getConcurrency", "getQueue"],
  post: ["postConcurrency", "postQueue", "perTargetConcurrency"],
} as const;

async function control(side: RuntimeSide, start: boolean) {
  if (pending.value[side] || (start && !props.ioEnabled)) return;
  sideError.value[side] = "";
  pending.value[side] = true;
  try {
    const updated = await (start ? httpMapping.start(side) : httpMapping.stop(side));
    if (status.value) publish({ ...status.value, [side]: updated });
    await refresh();
  } catch (caught) {
    sideError.value[side] = describeError(caught);
  } finally {
    pending.value[side] = false;
  }
}

const limitsOpen = ref(false);
const limitsDraft = ref<RuntimeLimits>();
const limitsForm = ref<HTMLFormElement>();
const limitsBusy = ref(false);
const limitsError = ref("");
const limitsSaved = ref(false);
let limitsRevision = 0;
function editLimits() {
  if (!limits.value) return;
  limitsDraft.value = { ...limits.value };
  limitsRevision = localConfiguration.value?.revision ?? 0;
  limitsError.value = "";
  limitsSaved.value = false;
  limitsOpen.value = true;
}

async function saveLimits() {
  if (!limitsOpen.value || !limitsDraft.value || limitsBusy.value) return;
  limitsBusy.value = true;
  limitsError.value = "";
  try {
    await httpMapping.saveLimits({ ...limitsDraft.value }, limitsRevision);
    limitsSaved.value = true;
    limitsOpen.value = false;
    await refresh();
  } catch (caught) {
    const code = describeError(caught);
    limitsError.value = `${code.includes("CONFLICT") ? ui.value.conflict : ui.value.invalid} (${code})`;
  } finally {
    limitsBusy.value = false;
  }
}

const resultFilter = ref("");
const filterDraft = ref("");
const resultsTable = ref<InstanceType<typeof HttpTable>>();
const peaksTable = ref<InstanceType<typeof HttpTable>>();
const rows = computed(() => {
  const saved = new Map((configuration.value?.mappings ?? []).map(mapping => [mapping.id, mapping]));
  const results = status.value?.mappings ?? {};
  const unknown = status.value?.lastUnknown ?? {};
  const ids = new Set([...saved.keys(), ...Object.keys(results), ...Object.keys(unknown)]);
  return [...ids].map(id => ({
    id,
    name: saved.get(id)?.name ?? id,
    target: saved.get(id)?.targetApiKey ?? "",
    result: Object.hasOwn(results, id) ? results[id] : undefined,
    unknown: Object.hasOwn(unknown, id) ? unknown[id] : undefined,
  })).filter(row => matchesFilter(resultFilter.value, row.id, row.name, row.target));
});
const { page, pageSize, pagedItems, total } = usePagination(() => rows.value);
function queryResults() {
  resultFilter.value = filterDraft.value;
  page.value = 1;
}
const columns = computed(() => [
  { id: "name", title: ui.value.mappings, width: 166 },
  { id: "target", title: ui.value.target, width: 148 },
  { id: "execution", title: ui.value.runId, width: 138 },
  { id: "finishedAt", title: ui.value.finishedAt, width: 166 },
  { id: "unknown", title: ui.value.previousUnknown, width: 175 },
  { id: "result", title: ui.value.status, width: 175, fixed: true },
]);
const targetStats = computed(() => {
  const current = status.value?.post.targetInFlight ?? {};
  const peak = status.value?.post.targetPeakInFlight ?? {};
  const keys = new Set([...Object.keys(current), ...Object.keys(peak)]);
  return [...keys].sort().map(target => ({
    target,
    current: Object.hasOwn(current, target) ? current[target] : 0,
    peak: Object.hasOwn(peak, target) ? peak[target] : 0,
  }));
});
const peakColumns = computed(() => [
  { id: "target", title: ui.value.target, width: 350, min: 170 },
  { id: "inFlight", title: ui.value.inFlight, width: 170 },
  { id: "peakInFlight", title: ui.value.peakInFlight, width: 170 },
]);

const detailsOpen = ref(false);
const selectedResult = ref<PostResult | null>(null);
function showResult(result: PostResult) { selectedResult.value = result; detailsOpen.value = true; }
</script>

<template>
  <div class="mapping-page-stack">
    <ConsoleCard :title="ui.runtime" :help="ui.runtimeHelp" :help-label="ui.runtimeHelp" help-append-to="#sma-overlays">
      <template #actions><ConsoleActionButton :disabled="!limits || limitsBusy" @click="editLimits">{{ ui.configureLimits }}</ConsoleActionButton></template>
      <template #refresh><ConsoleActionButton :disabled="!native" :loading="busy" @click="refresh()">{{ ui.reload }}</ConsoleActionButton></template>
      <p v-if="error" class="warning" role="alert">{{ ui.invalid }} ({{ error }})</p>
      <p v-if="limitsSaved" class="notice" role="status">{{ ui.saved }}</p>
      <p v-if="!status" role="status">{{ busy ? ui.loading : ui.noRuntimeData }}</p>
      <div v-else class="http-runtime-grid">
        <ConsoleCard v-for="side in sides" :key="side" class="http-runtime-side" compact :title="side === 'get' ? ui.getSide : ui.postSide">
          <template #title-aside>
            <StatusCapsule :label="ui[status[side].phase]" :tone="status[side].phase === 'running' ? 'success' : status[side].phase === 'stopping' ? 'warning' : 'neutral'" />
          </template>
          <template #actions>
            <ConsoleActionButton v-if="status[side].phase === 'stopped'" tone="primary" :loading="pending[side]" :disabled="!ioEnabled"
              :title="!ioEnabled ? ui.httpDisabled : undefined" @click="control(side, true)">{{ side === 'get' ? ui.startGet : ui.startPost }}</ConsoleActionButton>
            <ConsoleActionButton v-else tone="danger" :loading="pending[side]" :disabled="status[side].phase === 'stopping'" @click="control(side, false)">{{ side === 'get' ? ui.stopGet : ui.stopPost }}</ConsoleActionButton>
          </template>
          <p v-if="sideError[side] || status[side].lastError" class="warning" role="status">{{ sideError[side] || status[side].lastError }}</p>
          <dl class="http-runtime-metrics http-runtime-live">
            <div v-for="metric in liveMetrics" :key="metric"><dt>{{ metric === 'active' ? ui.activeLines : ui[metric] }}</dt><dd>{{ status[side][metric] }}</dd></div>
          </dl>
          <dl class="http-runtime-metrics http-runtime-counters">
            <div v-for="metric in counters" :key="metric"><dt>{{ ui[metric] }}</dt><dd>{{ status[side][metric] }}</dd></div>
          </dl>
          <dl class="http-runtime-metrics http-runtime-capacity">
            <div><dt>{{ ui.concurrency }}</dt><dd>{{ status[side].limits.concurrency }}</dd></div>
            <div><dt>{{ ui.queueCapacity }}</dt><dd>{{ status[side].limits.queue }}</dd></div>
            <div v-if="side === 'post'"><dt>{{ ui.targetConcurrency }}</dt><dd>{{ status.post.limits.perTarget }}</dd></div>
          </dl>
        </ConsoleCard>
      </div>
    </ConsoleCard>
    <ConsoleCard :title="ui.recentRuns">
      <template #actions><ConsoleActionButton :title="ui.resetHelp" @click="resultsTable?.resetWidths()">{{ ui.reset }}</ConsoleActionButton></template>
      <template #tools>
        <form class="http-runtime-filter" role="search" @submit.prevent="queryResults">
          <input v-model="filterDraft" type="search" :aria-label="ui.search" :placeholder="ui.search">
          <ConsoleActionButton tone="primary" native-type="submit">{{ ui.queryResults }}</ConsoleActionButton>
        </form>
      </template>
      <HttpTable ref="resultsTable" v-model:page="page" v-model:page-size="pageSize" table-id="http-runs"
        :columns="columns" :caption="ui.recentRuns" :total="total" :busy="busy" hide-tools>
        <tr v-for="row in pagedItems" :key="row.id">
          <td><strong>{{ row.name }}</strong></td><td>{{ row.target || ui.missing }}</td>
          <td>{{ row.result?.runId ?? ui.missing }}</td>
          <td>{{ formatBusinessTime(row.result?.finishedAt) }}</td>
          <td><ConsoleActionButton v-if="row.unknown" variant="row" @click="showResult(row.unknown)">{{ formatBusinessTime(row.unknown.finishedAt) }}</ConsoleActionButton><span v-else>{{ ui.missing }}</span></td>
          <td><ConsoleActionButton v-if="row.result" variant="row" @click="showResult(row.result)">{{ postStatusLabel(ui, row.result.status) }}</ConsoleActionButton><span v-else>{{ ui.noLatestResult }}</span></td>
        </tr>
      </HttpTable>
    </ConsoleCard>
    <ConsoleCard :title="ui.targetPeak" class="http-runtime-peaks">
      <template #actions><ConsoleActionButton :title="ui.resetHelp" @click="peaksTable?.resetWidths()">{{ ui.reset }}</ConsoleActionButton></template>
      <HttpTable ref="peaksTable" table-id="http-target-peaks" :columns="peakColumns" :caption="ui.targetPeak"
        :total="targetStats.length" :busy="busy" hide-tools>
        <tr v-for="target in targetStats" :key="target.target"><td>{{ target.target }}</td><td>{{ target.current }}</td><td>{{ target.peak }}</td></tr>
      </HttpTable>
    </ConsoleCard>
  </div>

  <SmaDialog v-model="limitsOpen" :title="ui.runtimeLimits" :error="limitsError" compact>
    <form v-if="limitsDraft" ref="limitsForm" class="http-stack" @submit.prevent="saveLimits">
      <fieldset v-for="side in sides" :key="side" class="http-runtime-limit-group">
        <legend>{{ side === 'get' ? ui.getSide : ui.postSide }}</legend>
        <div class="http-form-grid">
          <label v-for="key in limitKeys[side]" :key="key" class="field">
            <span>{{ key === 'perTargetConcurrency' ? ui.targetConcurrency : ui[key] }}</span>
            <input v-model.number="limitsDraft[key]" type="number" min="1" :max="key === 'getQueue' || key === 'postQueue' ? 10000 : 128" step="1" required>
          </label>
        </div>
      </fieldset>
    </form>
    <template #footer><ConsoleActionButton @click="limitsOpen = false">{{ ui.cancel }}</ConsoleActionButton><ConsoleActionButton tone="primary" :loading="limitsBusy" @click="limitsForm?.requestSubmit()">{{ ui.save }}</ConsoleActionButton></template>
  </SmaDialog>
  <SmaDialog v-model="detailsOpen" :title="ui.sentResult" compact>
    <PostResultDetails v-if="selectedResult" :result="selectedResult" />
    <template #footer><ConsoleActionButton @click="detailsOpen = false">{{ ui.close }}</ConsoleActionButton></template>
  </SmaDialog>
</template>
