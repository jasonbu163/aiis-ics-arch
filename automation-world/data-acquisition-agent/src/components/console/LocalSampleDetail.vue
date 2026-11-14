<!-- 历史样本详情：冻结摘要、分页点位结果和按需格式化JSON；不调用IPC或修改样本。 -->
<template>
  <div class="daa-history-detail">
    <section v-if="details" class="daa-sample-section">
      <div class="daa-sample-heading">
        <h3>{{ t('common.local.sampleView.summary') }}</h3>
        <div class="tag-row"><span class="muted-cell">{{ t('common.local.sampleView.delivery') }}</span><ElTag type="info" effect="plain">{{ deliveryLabel }}</ElTag></div>
      </div>
      <dl class="daa-sample-summary">
        <div><dt>{{ t('common.local.plc') }}</dt><dd>{{ details.plc || '—' }}</dd></div>
        <div><dt>{{ t('common.local.db') }}</dt><dd>{{ details.dbNumber }}</dd></div>
        <div><dt>{{ t('common.local.group') }}</dt><dd>{{ details.group || '—' }}</dd></div>
        <div><dt>{{ t('common.local.sampleView.savedAt') }}</dt><dd>{{ formatBusinessTime(details.savedAt) }}</dd></div>
        <div><dt>{{ t('common.local.origin') }}</dt><dd>{{ details.origin === 's7' ? 'S7' : label(details.origin) }}</dd></div>
        <div><dt>{{ t('common.local.sampleView.pointQuality') }}</dt><dd>{{ t('common.local.sampleView.qualityCount', { good: details.good, total: details.rows.length }) }}<span v-if="details.good < details.rows.length" class="muted-cell">{{ t('common.local.sampleView.otherCount', { count: details.rows.length - details.good }) }}</span></dd></div>
      </dl>
      <p class="daa-capability-note">{{ t('common.local.sampleView.timezone', { timezone: BUSINESS_TIME_ZONE }) }}</p>
    </section>
    <ElAlert v-else type="warning" :closable="false" :title="t('common.local.sampleView.unavailable')" />

    <section v-if="details" class="daa-sample-section">
      <div class="daa-sample-heading"><h3>{{ t('common.local.sampleView.points') }}</h3><ConsoleActionButton size="small" label-key="common.local.sampleView.resetWidths" @click="resetColumns" /></div>
      <ConsoleTableShell v-model:current-page="page" v-model:page-size="pageSize" :page-sizes="[10, 20, 50]" :total="details.rows.length">
        <ElTable :key="tableVersion" class="daa-sample-table" border :data="pagedRows" row-key="id" :empty-text="t('common.local.sampleView.empty')" @header-dragend="resizeColumn">
          <ElTableColumn column-key="name" :label="t('common.local.sampleView.point')" :width="widths.name" :min-width="180"><template #default="{ row }"><strong>{{ row.name }}</strong><span v-if="row.sourcePath && row.sourcePath !== row.name" class="muted-cell">{{ row.sourcePath }}</span></template></ElTableColumn>
          <ElTableColumn column-key="value" prop="value" :label="t('common.local.sampleView.value')" :width="widths.value" :min-width="100"><template #default="{ row }"><code>{{ row.value }}</code></template></ElTableColumn>
          <ElTableColumn column-key="dataType" prop="dataType" :label="t('common.local.sampleView.type')" :width="widths.dataType" :min-width="70" />
          <ElTableColumn column-key="address" prop="address" :label="t('common.local.sampleView.address')" :width="widths.address" :min-width="90" />
          <ElTableColumn column-key="quality" :label="t('common.local.quality')" :width="widths.quality" :min-width="100"><template #default="{ row }"><ElTag :type="row.quality === 'good' ? 'success' : 'warning'" effect="plain">{{ label(row.quality) }}</ElTag><span v-if="row.reason" class="muted-cell">{{ label(row.reason) }}</span></template></ElTableColumn>
          <ElTableColumn column-key="observedAt" :label="t('common.local.sampleView.observedAt')" :width="widths.observedAt" :min-width="200"><template #default="{ row }">{{ formatBusinessTime(row.observedAt) }}</template></ElTableColumn>
        </ElTable>
      </ConsoleTableShell>
    </section>

    <section v-if="raw.sampleUpload" class="daa-sample-section">
      <h3>{{ t('common.delivery.v2Detail') }}</h3>
      <dl class="daa-local-facts"><dt>{{ t('common.delivery.state') }}</dt><dd>{{ deliveryLabel }}</dd><dt>{{ t('common.delivery.sourceInstance') }}</dt><dd>{{ raw.sampleUpload.instanceId }}</dd><dt>{{ t('common.delivery.sourcePlc') }}</dt><dd>{{ raw.sampleUpload.plcId }}</dd><dt>{{ t('common.delivery.sourceGeneration') }}</dt><dd>{{ raw.sampleUpload.sourceGeneration }}</dd><dt>{{ t('common.delivery.attempt') }}</dt><dd>{{ raw.sampleUpload.attempt }}</dd><dt>{{ t('common.delivery.dispatchedAt') }}</dt><dd>{{ formatBusinessTime(raw.sampleUpload.dispatchedAt) }}</dd><dt>{{ t('common.delivery.confirmedAt') }}</dt><dd>{{ formatBusinessTime(raw.sampleUpload.acknowledgedAt) }}</dd><dt v-if="raw.sampleUpload.lastError">{{ t('common.delivery.reason') }}</dt><dd v-if="raw.sampleUpload.lastError">{{ label(raw.sampleUpload.lastError) }}</dd></dl>
      <details class="daa-details"><summary>{{ t('common.delivery.diagnostics') }}</summary><dl class="daa-local-facts"><dt>{{ t('common.delivery.origin') }}</dt><dd>{{ raw.sampleUpload.origin }}</dd><dt>{{ t('common.delivery.bodyDigest') }}</dt><dd>{{ raw.sampleUpload.bodySha256 || '—' }}</dd><dt>{{ t('common.delivery.receipt') }}</dt><dd>{{ raw.sampleUpload.receiptSha256 || '—' }}</dd></dl></details>
    </section>
    <section v-if="raw.deliveries?.length" class="daa-sample-section">
      <h3>{{ t('common.delivery.sampleLinks') }}</h3><dl v-for="part in raw.deliveries" :key="part.part" class="daa-local-facts"><dt>{{ t('common.delivery.part') }}</dt><dd>{{ part.part }} / {{ part.parts }}</dd><dt>{{ t('common.delivery.state') }}</dt><dd>{{ t('common.delivery.states.' + part.state) }}</dd><dt>{{ t('common.delivery.batch') }}</dt><dd>{{ part.batchId || '—' }}</dd><dt>{{ t('common.delivery.receipt') }}</dt><dd>{{ part.receiptId || '—' }}</dd><dt>{{ t('common.delivery.reason') }}</dt><dd>{{ part.lastError ? label(part.lastError) : '—' }}</dd></dl>
    </section>
    <section class="daa-sample-section">
      <p class="daa-capability-note">{{ t('common.local.sampleView.originalNote') }}</p>
      <details v-for="entry in jsonEntries" :key="entry.id" class="daa-details" @toggle="toggleJson(entry.id, $event)">
        <summary>{{ t(entry.title) }}</summary>
        <template v-if="jsonOpen[entry.id]">
          <code v-if="entry.id === 'payload'" class="muted-cell">{{ t('common.local.sampleView.sampleId') }} {{ sampleId }}</code>
          <code class="muted-cell">SHA-256 {{ raw[entry.hash] }}</code>
          <pre class="daa-sample-json">{{ formatSampleJson(raw[entry.id]) }}</pre>
        </template>
      </details>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElAlert, ElTable, ElTableColumn, ElTag } from 'element-plus'
import type { RawSample } from '../../services/localAcquisition'
import { sampleDetails, formatSampleJson } from '../../console/sampleDetails'
import { BUSINESS_TIME_ZONE, formatBusinessTime } from '../../console/time'
import { loadWidths, saveWidth, resetWidths, widthKey } from '../../console/tableWidths'
import ConsoleActionButton from './ConsoleActionButton.vue'
import ConsoleTableShell from './ConsoleTableShell.vue'

const props = defineProps<{ raw: RawSample; sampleId: string }>()
const { t, te } = useI18n()
const label = (code: string) => code ? te(`common.local.codes.${code}`) ? t(`common.local.codes.${code}`) : code : '—'
const details = computed(() => sampleDetails(props.raw))
const deliveryLabel = computed(() => props.raw.sampleUpload ? (te(`common.delivery.states.${props.raw.sampleUpload.state}`) ? t(`common.delivery.states.${props.raw.sampleUpload.state}`) : label(props.raw.sampleUpload.state)) : props.raw.deliveryState === 'local_only' ? t('common.delivery.localOnly') : props.raw.deliveryState === 'acknowledged' ? t('common.delivery.legacyConfirmed') : props.raw.deliveryState === 'pending' ? t('common.local.sampleView.pending') : label(props.raw.deliveryState))
const page = ref(1), pageSize = ref(20)
const pagedRows = computed(() => details.value?.rows.slice((page.value - 1) * pageSize.value, page.value * pageSize.value) ?? [])
watch(pageSize, () => { page.value = 1 })
const jsonOpen = reactive({ payload: false, manifest: false, context: false })
const jsonEntries = [
  { id: 'payload', hash: 'sha256', title: 'common.local.sampleView.json' },
  { id: 'manifest', hash: 'manifestSha256', title: 'common.local.manifest' },
  { id: 'context', hash: 'contextSha256', title: 'common.local.context' }
] as const
function toggleJson(id: keyof typeof jsonOpen, event: Event) { jsonOpen[id] = (event.target as HTMLDetailsElement).open }
watch(() => props.raw.payload, () => { page.value = 1 })
const columns = [
  { id: 'name', width: 240, min: 180 }, { id: 'value', width: 120, min: 100 },
  { id: 'dataType', width: 90, min: 70 }, { id: 'address', width: 110, min: 90 },
  { id: 'quality', width: 140, min: 100 }, { id: 'observedAt', width: 210, min: 200 }
]
let storage: Storage | undefined
try { storage = window.localStorage } catch { /* 受限环境保留默认列宽。 */ }
const preferencesKey = widthKey('com.aiis.aw.dataacquisitionagent', 'storage.sample-points')
const widths = ref(loadWidths(storage, preferencesKey, columns)), tableVersion = ref(0)
function resizeColumn(width: number, _old: number, column: { columnKey?: string }) {
  widths.value = saveWidth(storage, preferencesKey, columns, widths.value, column.columnKey ?? '', width)
  tableVersion.value++
}
function resetColumns() { widths.value = resetWidths(storage, preferencesKey, columns); tableVersion.value++ }
</script>
