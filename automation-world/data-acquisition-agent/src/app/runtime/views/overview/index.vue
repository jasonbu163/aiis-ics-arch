<!-- DAA本地SQLite视图：唯一local owner提供状态/动作，导航不驱动PLC或health。 -->
<template>
  <template v-if="local">
    <div class="daa-local-metrics">
      <ConsoleMetricCard label-key="common.local.connectedCount" :value="local.snapshot && !local.snapshotError ? String(local.snapshot.plcs.filter(p => p.connected).length) + ' / ' + String(local.snapshot.plcs.length) : '—'" />
      <ConsoleMetricCard label-key="common.local.collectionCount" :value="local.snapshot && !local.snapshotError ? String(local.snapshot.plcs.filter(p => p.phase === 'collecting').length) : '—'" />
      <ConsoleMetricCard label-key="common.local.pendingSummary" :value="local.snapshot && !local.snapshotError ? String(local.snapshot.capacity.pendingCount) : '—'" />
      <ConsoleMetricCard label-key="common.local.capacity" :value="local.snapshotError ? '—' : local.label(local.snapshot?.capacity.state)" />
    </div>
    <el-alert v-if="local.error" :title="local.label(local.error)" type="error" :closable="false" show-icon />
    <p v-if="local.conflictVersion" class="diagnostic-message">{{ t('common.local.currentEtag') }}: {{ local.conflictVersion }}</p>
    <el-alert v-if="local.snapshotError" :title="local.snapshot ? t('common.local.staleSnapshot', { time: formatBusinessTime(local.snapshot.generatedAt) }) : t('common.feedback.notLoaded')" :description="local.label(local.snapshotError)" type="warning" :closable="false" show-icon />
    <el-alert v-if="local.view && !local.view.active" :title="t('common.startup.inactive')" type="info" :closable="false" show-icon />
    <el-alert v-if="local.dirty" :title="t('common.startup.dirty')" type="warning" :closable="false" show-icon />
    <el-alert v-if="local.notice && !local.dirty && !local.editing" :title="local.label(local.notice)" type="success" :closable="false" />
    <StartupSettings />
    <FactsDeliveryPanel />
  </template>
</template>

<script setup lang="ts">
import FactsDeliveryPanel from '../../../../components/console/FactsDeliveryPanel.vue';
import ConsoleMetricCard from '../../../../components/console/ConsoleMetricCard.vue';
import StartupSettings from '../../../../components/console/StartupSettings.vue';
import { formatBusinessTime } from '../../../../console/time';

import { inject } from 'vue';
import { localConsoleKey } from '../../../../console/composables/useLocalAcquisitionConsole';
const local = inject(localConsoleKey);
import { useI18n } from 'vue-i18n';
const { t } = useI18n();
</script>
