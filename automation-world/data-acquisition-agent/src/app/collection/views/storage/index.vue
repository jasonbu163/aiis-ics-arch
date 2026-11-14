<!-- 上报、样本记录和本地存储使用同一原生 owner；保留原有策略保存与历史入口。 -->
<template>
  <template v-if="local">
    <FactsDeliveryPanel configure />

    <ConsoleCard title-key="common.delivery.localStorage" compact>
      <template #actions><span class="daa-storage-state">{{ local.label(local.snapshot?.capacity.state) }}</span></template>
      <el-alert v-if="local.snapshot && !local.snapshot.capacity.admission" :title="t('common.local.capacityRisk')" :description="local.label(local.snapshot.capacity.state)" type="warning" :closable="false" show-icon />
      <div class="daa-reporting-stats daa-storage-stats" :aria-label="t('common.delivery.localStorage')">
        <div class="daa-reporting-stat daa-storage-stat">
          <span>{{ t('common.delivery.usedRuntime') }}</span>
          <strong>{{ usedBytes === null ? '—' : local.formatBytes(usedBytes) }} / {{ local.formatBytes(local.snapshotError ? undefined : local.snapshot?.capacity.quotaBytes) }}</strong>
          <ElProgress v-if="usagePercent !== null" :percentage="usagePercent" :show-text="false" />
        </div>
        <div class="daa-reporting-stat daa-storage-stat"><span>{{ t('common.local.pendingBytes') }}</span><strong>{{ local.formatBytes(local.snapshotError ? undefined : local.snapshot?.capacity.pendingBytes) }}</strong></div>
        <div class="daa-reporting-stat daa-storage-stat"><span>{{ t('common.delivery.oldestPendingShort') }}</span><strong>{{ oldestPending }}</strong></div>
        <div class="daa-reporting-stat daa-storage-stat"><span>{{ t('common.delivery.activeRetention') }}</span><strong>{{ activeRetention }}</strong></div>
      </div>
      <ElCollapse>
        <ElCollapseItem name="policy" :title="t('common.local.storagePolicyDetails')">
          <ElForm v-if="local.draft" label-position="top" class="daa-local-form-grid" @submit.prevent>
            <ElFormItem :label="t('common.delivery.draftQuotaMiB')"><ElInputNumber :model-value="local.draft.storage.quotaBytes / 1048576" :min="128" :max="65536" :precision="0" controls-position="right" @update:model-value="local.draft.storage.quotaBytes = Number($event) * 1048576" /></ElFormItem>
            <ElFormItem :label="t('common.delivery.draftRetentionDays')"><ElInputNumber v-model="local.draft.storage.retentionDays" :min="1" :max="30" :precision="0" controls-position="right" /></ElFormItem>
          </ElForm>
          <p class="daa-capability-note">{{ t('common.local.retentionNote') }}</p>
          <p class="daa-capability-note">{{ t('common.delivery.storageSaveHint') }}</p>
        </ElCollapseItem>
        <ElCollapseItem name="files" :title="t('common.local.storageDetails')">
          <dl class="daa-local-facts"><template v-for="key in ['mainBytes', 'journalBytes', 'configBytes', 'configJournalBytes', 'logBytes', 'reservedBytes', 'freeBytes', 'pendingBytes'] as const" :key="key"><dt>{{ t('common.local.' + key) }}</dt><dd>{{ local.formatBytes(local.snapshot?.capacity[key]) }}</dd></template><dt>{{ t('common.local.oldestPending') }}</dt><dd>{{ formatBusinessTime(local.snapshot?.capacity.oldestPending) }}</dd></dl>
        </ElCollapseItem>
      </ElCollapse>
    </ConsoleCard>
    <details class="daa-details"><summary>{{ t('common.local.history') }}</summary><LocalHistoryPanel /></details>
    <details class="daa-details"><summary>{{ t('common.local.logs') }}</summary><LocalLogPanel /></details>
  </template>
</template>

<script setup lang="ts">
import { computed, inject } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElForm, ElFormItem, ElInputNumber, ElCollapse, ElCollapseItem, ElProgress } from 'element-plus'
import FactsDeliveryPanel from '../../../../components/console/FactsDeliveryPanel.vue'
import LocalHistoryPanel from '../../../../components/console/LocalHistoryPanel.vue'
import LocalLogPanel from '../../../../components/console/LocalLogPanel.vue'
import ConsoleCard from '../../../../components/console/ConsoleCard.vue'
import { formatBusinessTime } from '../../../../console/time'
import { localConsoleKey } from '../../../../console/composables/useLocalAcquisitionConsole'
const local = inject(localConsoleKey)
const { t } = useI18n()
const usedBytes = computed(() => local?.snapshot && !local.snapshotError ? local.snapshot.capacity.mainBytes + local.snapshot.capacity.journalBytes : null)
const usagePercent = computed(() => usedBytes.value !== null && local?.snapshot?.capacity.quotaBytes ? Math.min(100, Math.round(usedBytes.value * 100 / local.snapshot.capacity.quotaBytes)) : null)
const oldestPending = computed(() => {
  if (!local?.snapshot || local.snapshotError) return '—'
  const { oldestPending: oldest, pendingCount } = local.snapshot.capacity
  return oldest ? formatBusinessTime(oldest) : pendingCount === 0 ? t('common.delivery.noPending') : '—'
})
const activeRetention = computed(() => {
  if (!local?.snapshot || local.snapshotError) return '—'
  const policy = local.snapshot.activeStorage
  if (!policy) return local.snapshot.configuration.active === null ? t('common.delivery.noActivePolicy') : '—'
  return t('common.delivery.retentionValue', { days: policy.retentionDays })
})
</script>
