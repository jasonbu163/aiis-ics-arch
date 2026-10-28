<!-- DAA本地SQLite视图：唯一local owner提供状态/动作，导航不驱动PLC或health。 -->
<template>
  <template v-if="local">

    <div class="daa-local-metrics">
      <ConsoleMetricCard label-key="common.local.pendingSummary" :value="local.snapshot ? String(local.snapshot.capacity.pendingCount) : '—'" />
      <ConsoleMetricCard label-key="common.local.capacity" :value="local.label(local.snapshot?.capacity.state)" />
      <ConsoleMetricCard label-key="common.local.mainBytes" :value="local.formatBytes(local.snapshot?.capacity.mainBytes)" />
      <ConsoleMetricCard label-key="common.local.quotaMiB" :value="local.snapshot ? String(local.snapshot.capacity.quotaBytes / 1048576) : '—'" />
    </div>
    <el-alert :title="t('common.local.uploadPending')" type="info" :closable="false" />
    <el-alert v-if="local.snapshot && !local.snapshot.capacity.admission" :title="t('common.local.capacityRisk')" :description="local.label(local.snapshot.capacity.state)" type="warning" :closable="false" show-icon />
    <LocalHistoryPanel />
    <ConsoleCard title-key="common.local.storage" compact>
      <ElCollapse>
        <ElCollapseItem name="policy" :title="t('common.local.storagePolicyDetails')">
          <ElForm v-if="local.draft" label-position="top" class="daa-local-form-grid" @submit.prevent>
            <ElFormItem :label="t('common.local.quotaMiB')"><ElInputNumber :model-value="local.draft.storage.quotaBytes / 1048576" :min="128" :max="65536" :precision="0" controls-position="right" @update:model-value="local.draft.storage.quotaBytes = Number($event) * 1048576" /></ElFormItem>
            <ElFormItem :label="t('common.local.retentionDays')"><ElInputNumber v-model="local.draft.storage.retentionDays" :min="1" :max="30" :precision="0" controls-position="right" /></ElFormItem>
          </ElForm>
          <p class="daa-capability-note">{{ t('common.local.retentionNote') }}</p>
        </ElCollapseItem>
        <ElCollapseItem name="files" :title="t('common.local.storageDetails')">
          <dl class="daa-local-facts"><template v-for="key in ['mainBytes', 'journalBytes', 'configBytes', 'configJournalBytes', 'logBytes', 'reservedBytes', 'freeBytes', 'pendingBytes'] as const" :key="key"><dt>{{ t('common.local.' + key) }}</dt><dd>{{ local.formatBytes(local.snapshot?.capacity[key]) }}</dd></template><dt>{{ t('common.local.oldestPending') }}</dt><dd>{{ formatBusinessTime(local.snapshot?.capacity.oldestPending) }}</dd></dl>
        </ElCollapseItem>
      </ElCollapse>
    </ConsoleCard>
    <details class="daa-details"><summary>{{ t('common.local.logs') }}</summary><LocalLogPanel /></details>
  </template>
</template>

<script setup lang="ts">
import { ElForm, ElFormItem, ElInputNumber, ElCollapse, ElCollapseItem } from 'element-plus';
import ConsoleMetricCard from '../../../../components/console/ConsoleMetricCard.vue';

import LocalHistoryPanel from '../../../../components/console/LocalHistoryPanel.vue';
import LocalLogPanel from '../../../../components/console/LocalLogPanel.vue';
import { inject } from 'vue';
import { formatBusinessTime } from '../../../../console/time';
import { localConsoleKey } from '../../../../console/composables/useLocalAcquisitionConsole';
const local = inject(localConsoleKey);
import { Tickets } from '@element-plus/icons-vue';
import { useI18n } from 'vue-i18n';
import ConsoleCard from '../../../../components/console/ConsoleCard.vue';
const { t } = useI18n();

</script>
