<!-- 上报与记录均绑定同一原生 owner；实时发送和补传共用样本、目标和回执。 -->
<template>
  <template v-if="local">
    <ConsoleCard title-key="common.delivery.title" compact>
      <template v-if="local.bootstrap.uploadAvailable" #actions>
        <ConsoleActionButton v-if="configure" label-key="common.delivery.settings" :disabled="local.busy" @click="local.editDelivery" />
        <ConsoleActionButton v-if="local.deliverySnapshotError || local.delivery?.running" label-key="common.delivery.pause" tone="primary" :disabled="local.busy" @click="local.deliveryControl('pause')" />
        <ConsoleActionButton v-else label-key="common.delivery.startOrResume" tone="primary" :disabled="local.busy || !local.delivery" @click="local.deliveryControl('start')" />
      </template>
      <ElAlert v-if="!local.bootstrap.uploadAvailable" :title="t('common.delivery.unavailable')" type="info" :closable="false" />
      <template v-else>
        <ElAlert v-if="local.deliverySnapshotError" :title="t('common.delivery.snapshotUnavailable')" :description="local.label(local.deliverySnapshotError)" type="warning" :closable="false" show-icon />
        <div class="daa-reporting-status">
          <span class="daa-reporting-status__pill" :class="{ 'is-running': deliveryFresh?.state === 'running', 'is-warning': ['unknown', 'needs_processing'].includes(deliveryFresh?.state || '') }">{{ label(deliveryFresh?.state) }}</span>
          <span class="daa-capability-note">{{ t('common.delivery.statusNote') }}</span>
        </div>
        <div class="daa-reporting-destination">
          <span>{{ t('common.delivery.origin') }}</span><strong>{{ deliveryFresh?.origin || '—' }}</strong>
          <span>{{ t('common.delivery.lastAck') }}</span><strong>{{ formatBusinessTime(deliveryFresh?.lastAcknowledgedAt) }}</strong>
        </div>
        <div class="daa-reporting-stats" :aria-label="t('common.delivery.statistics')">
          <div v-for="stat in stats" :key="stat.key" class="daa-reporting-stat">
            <div class="daa-reporting-stat__label">
              <span>{{ t(stat.label) }}</span>
              <div class="daa-delivery-help" @mouseenter="hoverHelp = stat.key" @mouseleave="hoverHelp = ''">
                <button type="button" class="daa-help-button" :aria-label="t(stat.label) + ' · ' + t('common.delivery.helpLabel')" :aria-expanded="helpVisible(stat.key)" :aria-describedby="'daa-help-' + stat.key" @focus="focusHelp = stat.key" @blur="focusHelp = ''; touchHelp = ''" @click="touchHelp = touchHelp === stat.key ? '' : stat.key">?</button>
                <div v-show="helpVisible(stat.key)" :id="'daa-help-' + stat.key" role="tooltip" class="daa-help-text">{{ t(stat.help) }}</div>
              </div>
            </div>
            <strong>{{ stat.value ?? '—' }}</strong>
          </div>
        </div>
        <p class="daa-capability-note">{{ t('common.delivery.countUnits') }} {{ t('common.delivery.historicalV1') }}: {{ deliveryFresh?.historicalV1Acknowledged ?? '—' }}</p>
        <ElAlert v-if="deliveryFresh?.lastError" :title="local.label(deliveryFresh.lastError)" type="error" :closable="false" show-icon />
        <ElAlert v-if="deliveryFresh?.sampleCounts?.unknown" :title="t('common.delivery.unknownAlert')" :description="t('common.delivery.unknownAlertHint')" type="warning" :closable="false" show-icon />
        <ElAlert v-if="deliveryFresh?.needsReason" :title="t('common.delivery.needsProcessing')" :description="local.label(deliveryFresh.needsReason)" type="warning" :closable="false" show-icon />
      </template>
    </ConsoleCard>

    <ConsoleCard v-if="configure && local.bootstrap.uploadAvailable" title-key="common.delivery.records" body-class="console-card__body--table" compact>
      <template #actions>
        <ConsoleActionButton size="small" label-key="common.delivery.source" :disabled="local.busy" @click="local.showSourceMaterial" />
        <ConsoleActionButton size="small" label-key="common.delivery.refreshQueue" :disabled="local.busy" @click="local.loadDeliveries()" />
        <ConsoleActionButton size="small" label-key="common.delivery.resetWidths" @click="resetColumns" />
      </template>
      <template #tools>
        <div class="daa-reporting-filter" role="group" :aria-label="t('common.delivery.filterByState')">
          <ConsoleActionButton v-for="filter in filters" :key="filter.state" size="small" :label-key="filter.label" :tone="local.deliveryState === filter.state ? 'primary' : 'secondary'" :disabled="local.busy" :aria-pressed="local.deliveryState === filter.state" @click="selectState(filter.state)" />
        </div>
        <p class="daa-capability-note">{{ t('common.delivery.recordsNote') }}</p>
      </template>
      <div class="daa-delivery-table"><ElTable :key="tableVersion" border :data="local.deliveryPage?.items ?? []" row-key="batchId" :empty-text="t('common.delivery.empty')" @header-dragend="resizeColumn">
        <ElTableColumn column-key="createdAt" :label="t('common.delivery.createdAt')" :width="widths.createdAt" :min-width="190"><template #default="{ row }">{{ formatBusinessTime(row.createdAt) }}</template></ElTableColumn>
        <ElTableColumn column-key="plcId" :label="t('common.delivery.plc')" :width="widths.plcId" :min-width="120"><template #default="{ row }"><span :title="row.plcId">{{ plcName(row.plcId) }}</span></template></ElTableColumn>
        <ElTableColumn column-key="dbNumber" prop="dbNumber" :label="t('common.delivery.db')" :width="widths.dbNumber" :min-width="80" />
        <ElTableColumn column-key="state" :label="t('common.delivery.state')" :width="widths.state" :min-width="130"><template #default="{ row }">{{ label(row.state) }}</template></ElTableColumn>
        <ElTableColumn column-key="lastError" :label="t('common.delivery.reason')" :width="widths.lastError" :min-width="160"><template #default="{ row }">{{ row.lastError ? local.label(row.lastError) : '—' }}</template></ElTableColumn>
        <ElTableColumn column-key="batchId" prop="batchId" :label="t('common.delivery.batch')" :width="widths.batchId" :min-width="180" />
        <ElTableColumn column-key="attempt" prop="attempt" :label="t('common.delivery.attempt')" :width="widths.attempt" :min-width="80" />
        <ElTableColumn :label="t('common.local.actions')" :width="240" :resizable="false" fixed="right"><template #default="{ row }"><div class="row-actions"><ConsoleActionButton size="small" label-key="common.local.sampleDetails" :disabled="local.busy" @click="openSample(row.batchId)" /><ConsoleActionButton size="small" label-key="common.delivery.details" :disabled="local.busy" @click="local.inspectDelivery(row.batchId)" /></div></template></ElTableColumn>
      </ElTable></div>
      <div class="daa-delivery-actions"><ConsoleActionButton size="small" label-key="common.delivery.previous" :disabled="local.busy || local.deliveryCursors.length <= 1" @click="local.loadDeliveries('previous')" /><span>{{ t('common.delivery.page', { page: local.deliveryPageNumber }) }}</span><ConsoleActionButton size="small" label-key="common.delivery.next" :disabled="local.busy || !local.deliveryPage?.nextCursor" @click="local.loadDeliveries('next')" /><ElSelect :model-value="local.deliveryPageSize" :disabled="local.busy" append-to="#daa-feedback" :aria-label="t('common.delivery.pageSize')" @change="size => local!.loadDeliveries('reset', Number(size))"><ElOption v-for="size in [10,20,50]" :key="size" :value="size" :label="String(size)" /></ElSelect></div>
    </ConsoleCard>
    <FactsDeliveryDialog v-if="local.deliveryDialog" />
    <Teleport to="#daa-feedback">
      <ElDialog v-model="detailsVisible" :title="t('common.local.sampleDetails')" width="min(960px, calc(100vw - 32px))" :append-to-body="false" :close-on-click-modal="false" destroy-on-close>
        <LocalSampleDetail v-if="local.raw && local.rawSampleId === detailSampleId" :key="detailSampleId" :raw="local.raw" :sample-id="detailSampleId" />
        <template #footer><ConsoleActionButton label-key="common.local.closeDetails" @click="detailsVisible = false" /></template>
      </ElDialog>
    </Teleport>
  </template>
</template>
<script setup lang="ts">
import { computed, inject, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElAlert, ElDialog, ElTable, ElTableColumn, ElSelect, ElOption } from 'element-plus'
import { localConsoleKey } from '../../console/composables/useLocalAcquisitionConsole'
import { formatBusinessTime } from '../../console/time'
import { loadWidths, saveWidth, resetWidths, widthKey } from '../../console/tableWidths'
import ConsoleCard from './ConsoleCard.vue'
import ConsoleActionButton from './ConsoleActionButton.vue'
import FactsDeliveryDialog from './FactsDeliveryDialog.vue'
import LocalSampleDetail from './LocalSampleDetail.vue'
const props = defineProps<{ configure?: boolean }>()
const local = inject(localConsoleKey), { t, te } = useI18n()
const deliveryFresh = computed(() => local?.deliverySnapshotError ? null : local?.delivery)
const label = (state?: string) => state && te(`common.delivery.states.${state}`) ? t(`common.delivery.states.${state}`) : local?.label(state)
const plcName = (id: string) => local?.view?.draft.plcs.find(plc => plc.id === id)?.name || id
const hoverHelp = ref(''), focusHelp = ref(''), touchHelp = ref('')
const detailsVisible = ref(false), detailSampleId = ref('')
const helpVisible = (key: string) => hoverHelp.value === key || focusHelp.value === key || touchHelp.value === key
const stats = computed(() => [
  { key: 'pending', label: 'common.delivery.pending', help: 'common.delivery.pendingHint', value: deliveryFresh.value?.sampleCounts?.pending },
  { key: 'unknown', label: 'common.delivery.unknownSamples', help: 'common.delivery.unknownHint', value: deliveryFresh.value?.sampleCounts?.unknown },
  { key: 'needs', label: 'common.delivery.needsProcessing', help: 'common.delivery.needsHint', value: deliveryFresh.value?.sampleCounts?.needsProcessing },
  { key: 'acknowledged', label: 'common.delivery.acknowledged', help: 'common.delivery.acknowledgedHint', value: deliveryFresh.value?.sampleCounts?.acknowledged },
])
const filters = [
  { state: '', label: 'common.delivery.allStates' },
  { state: 'pending', label: 'common.delivery.pending' },
  { state: 'unknown', label: 'common.delivery.unknownSamples' },
  { state: 'needs_processing', label: 'common.delivery.needsProcessing' },
  { state: 'acknowledged', label: 'common.delivery.acknowledged' },
]
const countSignature = () => JSON.stringify(local?.delivery?.sampleCounts ?? null)
let queueSignature = ''
onMounted(() => { if (props.configure && local?.bootstrap.uploadAvailable) { local.deliveryKind = 'batches'; queueSignature = countSignature(); void local.loadDeliveries() } })
watch(() => [countSignature(), local?.busy], () => {
  if (!props.configure || !local?.bootstrap.uploadAvailable || local.busy || queueSignature === countSignature()) return
  queueSignature = countSignature()
  void local.loadDeliveries()
})
function selectState(state: string) { if (local) { local.deliveryKind = 'batches'; local.deliveryState = state; void local.loadDeliveries() } }
async function openSample(sampleId: string) {
  const owner = local
  if (!owner) return
  detailsVisible.value = false
  if (await owner.inspect(sampleId) && owner.rawSampleId === sampleId) { detailSampleId.value = sampleId; detailsVisible.value = true }
}
const columns = [{ id: 'batchId', width: 280, min: 180 }, { id: 'plcId', width: 150, min: 120 }, { id: 'dbNumber', width: 90, min: 80 }, { id: 'state', width: 170, min: 130 }, { id: 'attempt', width: 90, min: 80 }, { id: 'createdAt', width: 200, min: 190 }, { id: 'lastError', width: 220, min: 160 }]
let storage: Storage | undefined
try { storage = window.localStorage } catch { /* 无存储时保留默认布局。 */ }
const key = widthKey('com.aiis.aw.dataacquisitionagent', 'storage.delivery-queue'), widths = ref(loadWidths(storage, key, columns)), tableVersion = ref(0)
function resizeColumn(width: number, _old: number, column: { columnKey?: string }) { widths.value = saveWidth(storage, key, columns, widths.value, column.columnKey ?? '', width); tableVersion.value++ }
function resetColumns() { widths.value = resetWidths(storage, key, columns); tableVersion.value++ }
</script>
