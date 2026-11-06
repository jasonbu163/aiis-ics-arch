<!-- 单owner真实投递控件：工作台运行卡/存储设置与有界队列，不发浏览器HTTP。 -->
<template>
  <ConsoleCard v-if="local" title-key="common.delivery.title" compact>
    <ElAlert v-if="!local.bootstrap.uploadAvailable" :title="t('common.delivery.unavailable')" type="info" :closable="false" />
    <template v-else>
      <dl class="daa-local-facts"><dt>{{ t('common.delivery.target') }}</dt><dd>{{ local.delivery?.targetId || '—' }}</dd><dt>{{ t('common.delivery.origin') }}</dt><dd>{{ local.delivery?.origin || '—' }}</dd><dt>{{ t('common.delivery.state') }}</dt><dd>{{ label(local.delivery?.state) }}</dd><dt>{{ t('common.delivery.pending') }}</dt><dd>{{ local.delivery?.pending ?? '—' }}</dd><dt>{{ t('common.delivery.unfrozen') }}</dt><dd>{{ local.delivery?.sampleCounts?.unfrozen ?? '—' }}</dd><dt>{{ t('common.delivery.frozen') }}</dt><dd>{{ local.delivery?.sampleCounts?.frozen ?? '—' }}</dd><dt>{{ t('common.delivery.needsProcessing') }}</dt><dd>{{ local.delivery?.sampleCounts?.needsProcessing ?? '—' }}</dd><dt>{{ t('common.delivery.acknowledged') }}</dt><dd>{{ local.delivery?.acknowledged ?? '—' }}</dd><dt>{{ t('common.delivery.lastAck') }}</dt><dd>{{ formatBusinessTime(local.delivery?.lastAcknowledgedAt) }}</dd></dl>
      <p class="daa-capability-note">{{ t('common.delivery.countUnits') }}</p>
      <p v-if="local.delivery?.lastError" class="daa-capability-note">{{ local.label(local.delivery.lastError) }}</p>
      <div class="daa-delivery-actions"><ConsoleActionButton label-key="common.delivery.start" :disabled="local.busy || local.delivery?.running" @click="local.deliveryControl('start')" /><ConsoleActionButton label-key="common.delivery.pause" :disabled="local.busy || !local.delivery?.running" @click="local.deliveryControl('pause')" /><ConsoleActionButton label-key="common.delivery.resume" :disabled="local.busy || local.delivery?.running" @click="local.deliveryControl('resume')" /></div>
      <p class="daa-capability-note">{{ t('common.delivery.boundary') }}</p>
      <template v-if="configure">
        <div class="daa-delivery-actions"><ConsoleActionButton label-key="common.delivery.settings" :disabled="local.busy" @click="local.editDelivery" /><ConsoleActionButton label-key="common.delivery.source" :disabled="local.busy" @click="local.showSourceMaterial" /><ConsoleActionButton label-key="common.delivery.test" :disabled="local.busy || !local.selectedPlc" @click="local.openFactsRead" /><ConsoleActionButton label-key="common.delivery.preview" :disabled="local.busy || !local.history?.items.length" @click="local.previewFacts" /><ConsoleActionButton label-key="common.delivery.refreshQueue" :disabled="local.busy" @click="local.loadDeliveries()" /></div>
        <dl class="daa-local-facts"><dt>{{ t('common.delivery.requestBytes') }}</dt><dd>{{ local.formatBytes(local.delivery?.requestBytes) }}</dd><dt>{{ t('common.delivery.receiptBytes') }}</dt><dd>{{ local.formatBytes(local.delivery?.receiptBytes) }}</dd><dt>{{ t('common.delivery.metadataBytes') }}</dt><dd>{{ local.formatBytes(local.delivery?.metadataBytes) }}</dd></dl>
        <div class="daa-delivery-actions"><ElSelect v-model="local.deliveryKind" append-to="#daa-feedback" :aria-label="t('common.delivery.logKind')" @change="local.loadDeliveries()"><ElOption value="batches" :label="t('common.delivery.queue')" /><ElOption value="events" :label="t('common.delivery.logs')" /></ElSelect><ConsoleActionButton size="small" label-key="common.delivery.resetWidths" @click="resetColumns" /><ElSelect :model-value="local.deliveryPageSize" :disabled="local.busy" append-to="#daa-feedback" :aria-label="t('common.delivery.pageSize')" @change="size => local!.loadDeliveries('reset', Number(size))"><ElOption v-for="size in [10,20,50]" :key="size" :value="size" :label="String(size)" /></ElSelect></div>
        <div class="daa-delivery-table"><ElTable :key="tableVersion" border :data="local.deliveryPage?.items ?? []" row-key="batchId" :empty-text="t('common.delivery.empty')" @header-dragend="resizeColumn"><ElTableColumn column-key="batchId" prop="batchId" :label="t('common.delivery.batch')" :width="widths.batchId" :min-width="180" /><ElTableColumn column-key="state" :label="t('common.delivery.state')" :width="widths.state" :min-width="130"><template #default="{ row }">{{ row.event ? local.label(row.event) : label(row.state) }}</template></ElTableColumn><ElTableColumn column-key="attempt" prop="attempt" :label="t('common.delivery.attempt')" :width="widths.attempt" :min-width="80" /><ElTableColumn column-key="createdAt" :label="t('common.delivery.createdAt')" :width="widths.createdAt" :min-width="190"><template #default="{ row }">{{ formatBusinessTime(row.createdAt) }}</template></ElTableColumn><ElTableColumn column-key="lastError" :label="t('common.delivery.reason')" :width="widths.lastError" :min-width="160"><template #default="{ row }">{{ row.lastError ? local.label(row.lastError) : '—' }}</template></ElTableColumn><ElTableColumn :label="t('common.delivery.details')" :width="110" :resizable="false" fixed="right"><template #default="{ row }"><ConsoleActionButton v-if="!row.event" size="small" label-key="common.delivery.details" @click="local.inspectDelivery(row.batchId)" /></template></ElTableColumn></ElTable></div>
        <div class="daa-delivery-actions"><ConsoleActionButton size="small" label-key="common.delivery.previous" :disabled="local.busy || local.deliveryCursors.length <= 1" @click="local.loadDeliveries('previous')" /><span>{{ t('common.delivery.page', { page: local.deliveryPageNumber }) }}</span><ConsoleActionButton size="small" label-key="common.delivery.next" :disabled="local.busy || !local.deliveryPage?.nextCursor" @click="local.loadDeliveries('next')" /></div>
      </template>
    </template>
  </ConsoleCard>
  <FactsDeliveryDialog v-if="local?.deliveryDialog" />
</template>
<script setup lang="ts">
import { inject, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElAlert, ElTable, ElTableColumn, ElSelect, ElOption } from 'element-plus'
import { localConsoleKey } from '../../console/composables/useLocalAcquisitionConsole'
import { formatBusinessTime } from '../../console/time'
import { loadWidths, saveWidth, resetWidths, widthKey } from '../../console/tableWidths'
import ConsoleCard from './ConsoleCard.vue'
import ConsoleActionButton from './ConsoleActionButton.vue'
import FactsDeliveryDialog from './FactsDeliveryDialog.vue'
defineProps<{ configure?: boolean }>()
const local = inject(localConsoleKey), { t, te } = useI18n()
const label = (state?: string) => state && te(`common.delivery.states.${state}`) ? t(`common.delivery.states.${state}`) : local?.label(state)
const columns = [{ id: 'batchId', width: 280, min: 180 }, { id: 'state', width: 170, min: 130 }, { id: 'attempt', width: 90, min: 80 }, { id: 'createdAt', width: 200, min: 190 }, { id: 'lastError', width: 220, min: 160 }]
let storage: Storage | undefined
try { storage = window.localStorage } catch { /* 无存储时保留默认布局。 */ }
const key = widthKey('com.aiis.aw.dataacquisitionagent', 'storage.delivery-queue'), widths = ref(loadWidths(storage, key, columns)), tableVersion = ref(0)
function resizeColumn(width: number, _old: number, column: { columnKey?: string }) { widths.value = saveWidth(storage, key, columns, widths.value, column.columnKey ?? '', width); tableVersion.value++ }
function resetColumns() { widths.value = resetWidths(storage, key, columns); tableVersion.value++ }
</script>
