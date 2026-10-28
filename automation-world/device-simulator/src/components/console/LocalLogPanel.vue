<!-- 沿DAA日志表/过滤/分页范式，仅查询DS有界日志事实，不导入采样历史服务。 -->
<template>
  <ConsoleCard title-key="simulator.logs">
    <template #actions>
      <ConsoleActionButton label-key="simulator.refresh" @click="load" />
    </template>
    <div class="console-stack">
      <div class="ds-log-filter">
        <el-input v-model="filter" :placeholder="t('simulator.eventFilter')" maxlength="100" clearable />
        <ConsoleActionButton label-key="simulator.filter" @click="page=1;load()" />
      </div>
      <el-alert v-if="local.logs?.observabilityDegraded" :title="t('simulator.observabilityDegraded',{count:local.logs.lost})" type="warning" :closable="false" />
      <dl class="ds-log-facts">
        <div v-for="field in counters" :key="field" class="ds-log-fact">
          <dt>{{ t('simulator.logCounters.'+field) }}</dt>
          <dd>{{ local.logs?.[field]??'—' }}</dd>
        </div>
        <div class="ds-log-fact">
          <dt>{{ t('simulator.storageBytes') }}</dt>
          <dd>{{ local.logs?.storageBytes||'—' }}</dd>
        </div>
        <div class="ds-log-fact ds-log-fact--path">
          <dt>{{ t('simulator.configurationPath') }}</dt>
          <dd class="ds-wrap">{{ local.logs?.configurationPath||'—' }}</dd>
        </div>
      </dl>
      <ConsoleTableShell v-model:current-page="page" :page-size="50" :page-sizes="[50]" :total="local.logs?.retained||0">
        <ConsoleDataTable table-id="storage.events" :data="local.logs?.rows||[]">
          <el-table-column column-key="event" min-width="200" prop="event" :label="t('simulator.event')" />
          <el-table-column column-key="instance" min-width="180" prop="instance" :label="t('simulator.instance')" />
          <el-table-column column-key="timestamp" min-width="205" :label="t('simulator.updated')">
            <template #header><span>{{ t('simulator.updated') }} <ConsoleFieldHelp :label="t('simulator.updated')" :text="t('simulator.calendarTimeHint')" /></span></template>
            <template #default="{row}"><span :title="row.timestamp||''">{{ formatShanghaiTime(row.timestamp)||t('simulator.calendarTimeUnavailable') }}</span></template>
          </el-table-column>
          <el-table-column column-key="monotonic_ns" min-width="180" align="right" prop="monotonic_ns" :label="t('simulator.monotonicTime')" />
          <el-table-column column-key="operationId" min-width="180" prop="operationId" :label="t('simulator.operationId')" />
        </ConsoleDataTable>
      </ConsoleTableShell>
    </div>
  </ConsoleCard>
</template>
<script setup lang="ts">
import ConsoleDataTable from './ConsoleDataTable.vue';
import { inject, onMounted, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { simulatorKey } from '../../console/composables/useDeviceSimulator';
import { formatShanghaiTime } from '../../console/time';
import ConsoleFieldHelp from './ConsoleFieldHelp.vue';
import ConsoleCard from './ConsoleCard.vue';
import ConsoleActionButton from './ConsoleActionButton.vue';
import ConsoleTableShell from './ConsoleTableShell.vue';
const counters = ['lost', 'stdoutWriteErrors', 'stdoutDroppedBytes', 'fileWriteErrors', 'fileDroppedBytes', 'fileQueueDroppedLines', 'fileRotations'] as const;
const local = inject(simulatorKey)!, { t } = useI18n(), page = ref(1), filter = ref('');
function load() { void local.loadLogs((page.value - 1) * 50, filter.value || null); }
watch(page, load);
onMounted(load);
</script>
