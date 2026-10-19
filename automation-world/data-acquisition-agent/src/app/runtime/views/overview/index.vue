<!-- DAA本地SQLite视图：唯一local owner提供状态/动作，导航不驱动PLC或health。 -->
<template>
  <template v-if="local">

    <div class="daa-local-metrics">
      <ConsoleMetricCard label-key="common.local.connectedCount" :value="local.snapshot ? String(local.snapshot.plcs.filter(p => p.connected).length) + ' / ' + String(local.plcs.length) : '—'" />
      <ConsoleMetricCard label-key="common.local.collectionCount" :value="local.snapshot ? String(local.snapshot.plcs.filter(p => p.phase === 'collecting').length) : '—'" />
      <ConsoleMetricCard label-key="common.local.pendingSummary" :value="local.snapshot ? String(local.snapshot.capacity.pendingCount) : '—'" />
      <ConsoleMetricCard label-key="common.local.capacity" :value="local.label(local.snapshot?.capacity.state)" />
    </div>
  </template>
</template>

<script setup lang="ts">
import ConsoleMetricCard from '../../../../components/console/ConsoleMetricCard.vue';

import { inject } from 'vue';
import { localConsoleKey } from '../../../../console/composables/useLocalAcquisitionConsole';
const local = inject(localConsoleKey);
import { Monitor } from '@element-plus/icons-vue';
import { useI18n } from 'vue-i18n';

</script>
