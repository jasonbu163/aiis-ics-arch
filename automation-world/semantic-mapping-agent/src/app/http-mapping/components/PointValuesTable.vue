<!-- 点位诊断展示每个采集值的原始身份、质量与时间。 -->
<script setup lang="ts">
import { computed } from "vue";
import { StatusCapsule } from "@aw-ui";
import { formatBusinessTime } from "../../../console/time";
import { useHttpMessages } from "../messages";
import { jsonText } from "../ui";
import type { PointValue } from "../types";
import HttpTable from "./HttpTable.vue";

defineProps<{ values: PointValue[]; tableId: string }>();
const ui = useHttpMessages();
const columns = computed(() => [
  { id: "pointKey", title: ui.value.point, width: 140 },
  { id: "value", title: ui.value.value, width: 140 },
  { id: "quality", title: ui.value.quality, width: 105, min: 75 },
  { id: "observedAt", title: ui.value.observedAt, width: 176 },
  { id: "sampleId", title: ui.value.sampleId, width: 156 },
  { id: "diagnostic", title: ui.value.diagnostic, width: 190 },
]);
</script>

<template>
  <HttpTable :table-id="tableId" :columns="columns" :total="values.length" :caption="ui.parsedPoints">
    <tr v-for="point in values" :key="point.pointKey">
      <td>{{ point.pointKey }}</td>
      <td><code>{{ point.value === null ? ui.missing : jsonText(point.value) }}</code></td>
      <td>
        <StatusCapsule v-if="point.quality" :label="point.quality === 'good' ? ui.qualityGood : point.quality === 'bad' ? ui.qualityBad : point.quality"
          :tone="point.quality === 'good' ? 'success' : 'warning'" />
        <template v-else>{{ ui.missing }}</template>
      </td>
      <td>{{ formatBusinessTime(point.observedAt) }}</td><td>{{ point.sampleId ?? ui.missing }}</td><td>{{ point.errorCode ?? ui.missing }}</td>
    </tr>
  </HttpTable>
</template>
