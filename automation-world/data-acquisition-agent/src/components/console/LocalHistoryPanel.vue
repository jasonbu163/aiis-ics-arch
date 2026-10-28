<!-- 本地历史主工作区：有界游标分页、上海时间筛选与原始内容只读弹窗，复用CU卡片/动作/表格壳。 -->
<template>
  <ConsoleCard v-if="local" title-key="common.local.history" body-class="console-card__body--table">
    <template #actions><ConsoleActionButton label-key="common.local.resetHistoryWidths" @click="resetHistoryWidths" /><ConsoleActionButton label-key="common.local.search" tone="primary" :disabled="local.busy" @click="local.loadHistory(false)" /></template>
    <template #tools>
      <ElForm label-position="top" class="daa-local-filters" :disabled="local.busy" @submit.prevent="local.loadHistory(false)">
        <ElFormItem :label="t('common.local.plc')"><ElSelect v-model="local.historyFilter.plcId" append-to="#daa-feedback" @change="local.loadHistory(false)"><ElOption :label="t('common.local.all')" value="" /><ElOption v-for="p in local.plcs" :key="p.id" :label="p.name" :value="p.id" /></ElSelect></ElFormItem>
        <ElFormItem :label="t('common.local.group')"><ElSelect v-model="local.historyFilter.groupId" append-to="#daa-feedback" @change="local.loadHistory(false)"><ElOption :label="t('common.local.all')" value="" /><ElOption v-for="g in local.draft?.groups" :key="g.id" :label="g.name" :value="g.id" /></ElSelect></ElFormItem>
        <ElFormItem :label="t('common.local.quality')"><ElSelect v-model="local.historyFilter.quality" append-to="#daa-feedback" @change="local.loadHistory(false)"><ElOption :label="t('common.local.all')" value="" /><ElOption v-for="q in ['good', 'partial', 'bad']" :key="q" :label="local.label(q)" :value="q" /></ElSelect></ElFormItem>
        <ElFormItem :label="t('common.local.from')"><ElDatePicker v-model="fromDate" type="datetime" format="YYYY-MM-DD HH:mm:ss" value-format="YYYY-MM-DDTHH:mm:ss" :editable="false" clearable append-to="#daa-feedback" @change="local.loadHistory(false)" /></ElFormItem>
        <ElFormItem :label="t('common.local.to')"><ElDatePicker v-model="toDate" type="datetime" format="YYYY-MM-DD HH:mm:ss" value-format="YYYY-MM-DDTHH:mm:ss" :editable="false" clearable append-to="#daa-feedback" @change="local.loadHistory(false)" /></ElFormItem>
      </ElForm>
      <p class="daa-capability-note">{{ t('common.local.historyTimezone', { timezone }) }}</p>
    </template>
    <ConsoleTableShell :current-page="local.historyPage" :page-size="local.historyPageSize" :total="local.history?.items.length ?? 0" :pagination="false">
      <el-table :key="tableVersion" class="daa-history-table" border @header-dragend="resizeColumn" :data="local.history?.items ?? []" row-key="sampleId" :empty-text="t(local.history ? local.historyPage > 1 ? 'common.local.historyEnd' : 'common.local.emptyHistory' : 'common.local.historyNotLoaded')" :tooltip-options="{ appendTo: '#daa-feedback' }">
        <el-table-column column-key="savedAt" prop="savedAt" :label="t('common.local.time')" :width="widths.savedAt" :min-width="200"><template #default="{ row }">{{ formatBusinessTime(row.savedAt) }}</template></el-table-column>
        <el-table-column column-key="plcId" :label="t('common.local.plc')" :width="widths.plcId" :min-width="150"><template #default="{ row }">{{ local.plcs.find(p => p.id === row.plcId)?.name ?? row.plcId }}</template></el-table-column>
        <el-table-column column-key="dbNumber" prop="dbNumber" :label="t('common.local.db')" :width="widths.dbNumber" :min-width="65" />
        <el-table-column column-key="sourceSeq" prop="sourceSeq" :label="t('common.local.seq')" :width="widths.sourceSeq" :min-width="90" />
        <el-table-column column-key="quality" :label="t('common.local.quality')" :width="widths.quality" :min-width="100"><template #default="{ row }"><el-tag :type="row.quality === 'good' ? 'success' : 'warning'" effect="plain">{{ local.label(row.quality) }}</el-tag></template></el-table-column>
        <el-table-column column-key="actions" :label="t('common.local.actions')" width="140" :resizable="false" fixed="right"><template #default="{ row }"><div class="row-actions"><ConsoleActionButton size="small" label-key="common.local.sampleDetails" :disabled="local.busy" @click="openSample(row.sampleId)" /></div></template></el-table-column>
      </el-table>
    </ConsoleTableShell>
    <footer class="daa-history-pagination">
      <span>{{ local.history ? t('common.local.historyPage', { page: local.historyPage, count: local.history.items.length }) : t('common.local.historyNotLoaded') }}</span>
      <div class="row-actions">
        <label for="daa-history-size">{{ t('common.local.historyPageSize') }}</label>
        <ElSelect id="daa-history-size" :model-value="local.historyPageSize" class="daa-history-size" :disabled="local.busy" append-to="#daa-feedback" @change="changePageSize"><ElOption v-for="size in [10, 20, 50]" :key="size" :value="size" :label="String(size)" /></ElSelect>
        <ConsoleActionButton size="small" label-key="common.local.previous" :disabled="local.busy || !local.historyPreviousAvailable" @click="local.loadHistory('previous')" />
        <ConsoleActionButton size="small" label-key="common.local.next" :disabled="local.busy || !local.historyNextAvailable" @click="local.loadHistory(true)" />
      </div>
      <p v-if="local.historyPreviousBounded" class="daa-capability-note">{{ t('common.local.historyCursorBounded') }}</p>
    </footer>
  </ConsoleCard>
  <Teleport v-if="local" to="#daa-feedback">
    <ElDialog v-model="detailsVisible" :title="t('common.local.sampleDetails')" width="min(960px, calc(100vw - 32px))" :append-to-body="false" :close-on-click-modal="false" destroy-on-close>
      <div v-if="local.raw && local.rawSampleId === detailSampleId" class="daa-history-detail">
        <div class="tag-row"><h3>{{ t('common.local.original') }}</h3><el-tag type="info" effect="plain">{{ local.label(local.raw.deliveryState) }}</el-tag></div>
        <code class="muted-cell">{{ detailSampleId }}<br>SHA-256 {{ local.raw.sha256 }}</code>
        <pre class="daa-local-raw">{{ local.raw.payload }}</pre>
        <details class="daa-details"><summary>{{ t('common.local.manifest') }}</summary><code class="muted-cell">SHA-256 {{ local.raw.manifestSha256 }}</code><pre class="daa-local-raw">{{ local.raw.manifest }}</pre></details>
        <details class="daa-details"><summary>{{ t('common.local.context') }}</summary><code class="muted-cell">SHA-256 {{ local.raw.contextSha256 }}</code><pre class="daa-local-raw">{{ local.raw.context }}</pre></details>
      </div>
      <template #footer><ConsoleActionButton label-key="common.local.closeDetails" @click="detailsVisible = false" /></template>
    </ElDialog>
  </Teleport>
</template>
<script setup lang="ts">
import { computed, inject, ref } from 'vue'
import { BUSINESS_TIME_ZONE, formatBusinessTime, wallTime, historyBoundary } from '../../console/time'
import { loadWidths, saveWidth, resetWidths, widthKey } from '../../console/tableWidths'
import { useI18n } from 'vue-i18n'
import { ElForm, ElFormItem, ElDatePicker, ElDialog, ElSelect, ElOption } from 'element-plus'
import { localConsoleKey } from '../../console/composables/useLocalAcquisitionConsole'
import ConsoleCard from './ConsoleCard.vue'
import ConsoleActionButton from './ConsoleActionButton.vue'
import ConsoleTableShell from './ConsoleTableShell.vue'
const local = inject(localConsoleKey)
const { t } = useI18n()
const detailsVisible = ref(false), detailSampleId = ref('')
const timezone = BUSINESS_TIME_ZONE
function timeModel(field: 'from' | 'to') {
  return computed<string>({
    get: () => wallTime(local?.historyFilter[field]),
    set: value => { if (local) local.historyFilter[field] = historyBoundary(value, field === 'to') }
  })
}
const columns = [ { id: 'savedAt', width: 210, min: 200 }, { id: 'plcId', width: 180, min: 150 }, { id: 'dbNumber', width: 80, min: 65 }, { id: 'sourceSeq', width: 110, min: 90 }, { id: 'quality', width: 110, min: 100 } ]
let storage: Storage | undefined
try { storage = window.localStorage } catch { /* Restricted browser storage uses defaults. */ }
const preferencesKey = widthKey('com.aiis.aw.dataacquisitionagent', 'storage.history')
const widths = ref(loadWidths(storage, preferencesKey, columns)), tableVersion = ref(0)
function resizeColumn(width: number, _old: number, column: { columnKey?: string }) {
  widths.value = saveWidth(storage, preferencesKey, columns, widths.value, column.columnKey ?? '', width)
  // Recreate the table so Element Plus also applies the minimum to its internal realWidth.
  tableVersion.value++
}
function resetHistoryWidths() { widths.value = resetWidths(storage, preferencesKey, columns); tableVersion.value++ }
const fromDate = timeModel('from'), toDate = timeModel('to')
function changePageSize(size: unknown) { void local?.loadHistory(false, Number(size)) }
async function openSample(sampleId: string) {
  const owner = local
  if (!owner) return
  detailsVisible.value = false
  if (await owner.inspect(sampleId) && owner.rawSampleId === sampleId) {
    detailSampleId.value = sampleId
    detailsVisible.value = true
  }
}
</script>
