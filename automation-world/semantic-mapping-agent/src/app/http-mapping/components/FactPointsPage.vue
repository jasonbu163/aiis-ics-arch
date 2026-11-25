<!-- 事实点位按来源展示 SQLite 最近成功快照、原始采集身份及最近失败。 -->
<script setup lang="ts">
import { ConsoleActionButton, ConsoleCard, StatusCapsule } from "@aw-ui";
import { computed, ref, watch } from "vue";
import { formatBusinessTime } from "../../../console/time";
import { usePagination } from "../../../components/usePagination";
import { localConfiguration } from "../../twin-facts/api/localConfiguration";
import { httpMapping } from "../api";
import { useHttpMessages } from "../messages";
import { jsonText, matchesFilter, typeLabel } from "../ui";
import { usePoll } from "../usePoll";
import HttpTable from "./HttpTable.vue";

const props = defineProps<{ native: boolean }>();
const ui = useHttpMessages();
const { data, busy, error, refresh } = usePoll(props.native, httpMapping.latestSources);
const filterSource = ref("");
const search = ref("");
const clock = ref(Date.now());
watch(data, () => { clock.value = Date.now(); });
const sources = computed(() => localConfiguration.value?.document.httpSources ?? []);
const rows = computed(() => {
  const records = new Map(data.value?.map(item => [item.sourceKey, item]));
  return sources.value.filter(source => !filterSource.value || source.sourceKey === filterSource.value)
    .flatMap(source => {
      const latest = records.get(source.sourceKey);
      const points = new Map(latest?.snapshot?.points.map(point => [point.pointKey, point]));
      return source.points.filter(point => matchesFilter(search.value, point.name, point.pointKey, source.name, source.sourceKey))
        .map(definition => ({ source, latest, definition, point: points.get(definition.pointKey) }));
    });
});
const { page, pageSize, total, pagedItems } = usePagination(() => rows.value, 25);
watch([filterSource, search], () => { page.value = 1; });
watch(sources, all => {
  if (filterSource.value && !all.some(source => source.sourceKey === filterSource.value)) filterSource.value = "";
});
const columns = computed(() => [
  { id: "source", title: ui.value.source, width: 155 },
  { id: "point", title: ui.value.point, width: 147 },
  { id: "kind", title: ui.value.kind, width: 104 },
  { id: "value", title: ui.value.value, width: 140 },
  { id: "quality", title: ui.value.quality, width: 100, min: 75 },
  { id: "snapshot", title: ui.value.snapshot, width: 133 },
  { id: "collectedAt", title: ui.value.collectedAt, width: 169 },
  { id: "snapshotAge", title: ui.value.snapshotAge, width: 142 },
  { id: "observedAt", title: ui.value.observedAt, width: 169 },
  { id: "sampleId", title: ui.value.sampleId, width: 153 },
  { id: "attempt", title: ui.value.attemptedAt, width: 167 },
  { id: "diagnostics", title: ui.value.diagnostic, width: 213 },
]);
function age(collectedAt: string | undefined) {
  const time = Date.parse(collectedAt ?? "");
  return Number.isFinite(time) && clock.value >= time ? Math.floor((clock.value - time) / 1000) : ui.value.missing;
}
</script>

<template>
  <ConsoleCard :title="ui.factPoints" :help="ui.snapshotHelp" :help-label="ui.snapshotHelp" help-append-to="#sma-overlays">
    <template #refresh><ConsoleActionButton :disabled="!native" :loading="busy" @click="refresh()">{{ ui.reload }}</ConsoleActionButton></template>
    <p v-if="error" class="warning" role="alert">{{ ui.invalid }} ({{ error }})</p>
    <HttpTable v-model:page="page" v-model:page-size="pageSize" table-id="http-fact-points" :columns="columns" :total="total" :busy="busy" :caption="ui.factPoints">
      <template #filters>
        <select v-model="filterSource" :aria-label="ui.source">
          <option value="">{{ ui.anySource }}</option>
          <option v-for="source in sources" :key="source.id" :value="source.sourceKey">{{ source.name }}</option>
        </select>
        <input v-model="search" type="search" :aria-label="ui.search" :placeholder="ui.search">
      </template>
      <tr v-for="{ source, definition, point, latest } in pagedItems" :key="`${source.id}:${definition.pointKey}`">
        <td><strong>{{ source.name }}</strong><br><small>{{ source.sourceKey }}</small></td>
        <td><strong>{{ definition.name }}</strong><br><small>{{ definition.pointKey }}</small></td>
        <td>{{ typeLabel(ui, definition.dataType) }}</td>
        <td><code>{{ point?.value == null ? ui.missing : jsonText(point.value) }}</code></td>
        <td>
          <StatusCapsule v-if="point?.quality" :label="point.quality === 'good' ? ui.qualityGood : point.quality === 'bad' ? ui.qualityBad : point.quality"
            :tone="point.quality === 'good' ? 'success' : 'warning'" />
          <template v-else>{{ ui.missing }}</template>
        </td>
        <td>{{ latest?.snapshot?.version ?? ui.missing }}<br v-if="latest?.fromPreviousSession"><small v-if="latest?.fromPreviousSession">{{ ui.oldSnapshot }}</small></td>
        <td>{{ formatBusinessTime(latest?.snapshot?.collectedAt) }}</td><td>{{ age(latest?.snapshot?.collectedAt) }}</td><td>{{ formatBusinessTime(point?.observedAt) }}</td>
        <td>{{ point?.sampleId ?? ui.missing }}</td><td>{{ formatBusinessTime(latest?.lastAttemptAt) }}</td>
        <td><span v-if="latest?.lastErrorCode || point?.errorCode" class="warning">{{ [latest?.lastErrorCode, point?.errorCode].filter(Boolean).join(' · ') }}</span><template v-else>{{ ui.missing }}</template></td>
      </tr>
    </HttpTable>
  </ConsoleCard>
</template>
