<!-- 采集点位只读表，列宽偏好使用 CU 公共实现。 -->
<script setup lang="ts">
import { ConsoleActionButton, useTableColumnWidths } from "@aw-ui";
import { ElTable, ElTableColumn } from "element-plus";
import type { LocaleMessages } from "../../../locales";
import type { AcquisitionPoint } from "../api/acquisition";
import { formatBusinessTime } from "../../../console/time";

const props = defineProps<{ labels: LocaleMessages; points: AcquisitionPoint[]; tableId: string }>();
const minimums = { pointId: 140, name: 150, dataType: 95, valueText: 95, quality: 90, reason: 140, observedAt: 160, sourceType: 105 };
const width = useTableColumnWidths("sma", props.tableId, minimums);
</script>

<template>
  <div class="acquisition-table">
    <ConsoleActionButton tone="secondary" :title="labels.acquisition.resetWidths" @click="width.reset">{{ labels.acquisition.resetWidths }}</ConsoleActionButton>
    <ElTable :key="width.tableVersion.value" :data="points" row-key="pointId" border :empty-text="labels.acquisition.noData"
      @header-dragend="width.resize">
      <ElTableColumn v-for="(minWidth, key) in minimums" :key="key" :prop="key" :label="labels.acquisition[key]"
        :min-width="minWidth" :width="width.widths.value[key] || undefined" resizable>
        <template #default="{ row }">
          <template v-if="key === 'observedAt'">{{ formatBusinessTime(row.observedAt) }}</template>
          <template v-else-if="key === 'quality'">{{ row.quality === 'good' ? labels.acquisition.good : labels.acquisition.bad }}</template>
          <template v-else-if="key === 'sourceType'">{{ row.sourceType === 'daa' ? labels.acquisition.daa : row.sourceType === 'external' ? labels.acquisition.external : '—' }}</template>
          <template v-else>{{ row[key] === '' || row[key] == null ? '—' : row[key] }}</template>
        </template>
      </ElTableColumn>
    </ElTable>
  </div>
</template>

<style scoped>
.acquisition-table { display: grid; gap: 0.65rem; min-width: 0; width: 100%; }
.acquisition-table > :first-child { justify-self: start; }
</style>
