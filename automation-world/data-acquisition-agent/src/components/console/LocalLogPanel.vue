<!-- 有界运行事件：复用CU卡片/表格壳，保留显式游标与错误反馈。 -->
<template>
  <ConsoleCard v-if="local" title-key="common.local.logs" body-class="console-card__body--table" compact>
    <template #actions><ConsoleActionButton size="small" :disabled="local.busy" label-key="common.local.reloadLogs" @click="local.loadLogs(true)" /><ConsoleActionButton size="small" :disabled="local.busy" label-key="common.local.next" @click="local.loadLogs(false)" /></template>
    <ConsoleTableShell :current-page="1" :page-size="200" :total="local.logs.length" :pagination="false">
      <el-table :data="local.logs" :empty-text="t('common.local.emptyLogs')" :tooltip-options="{ appendTo: '#daa-feedback' }" size="small" row-key="cursor">
        <el-table-column prop="createdAt" :label="t('common.local.time')" min-width="190" />
        <el-table-column :label="t('common.local.logs')" min-width="160"><template #default="{ row }">{{ local.label(row.event) }}</template></el-table-column>
        <el-table-column :label="t('common.local.result')" min-width="120"><template #default="{ row }">{{ local.label(row.result) }}</template></el-table-column>
        <el-table-column prop="resource" :label="t('common.local.resource')" min-width="160" show-overflow-tooltip />
      </el-table>
    </ConsoleTableShell>
  </ConsoleCard>
</template>
<script setup lang="ts">
import { inject } from 'vue'
import { useI18n } from 'vue-i18n'
import { localConsoleKey } from '../../console/composables/useLocalAcquisitionConsole'
import ConsoleCard from './ConsoleCard.vue'
import ConsoleActionButton from './ConsoleActionButton.vue'
import ConsoleTableShell from './ConsoleTableShell.vue'
const local = inject(localConsoleKey)
const { t } = useI18n()
</script>
