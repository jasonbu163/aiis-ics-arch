<!-- 文件路径: /frontend-js/src/app/acquisition-data/views/history/index.vue
     功能描述: 以上海采集时间查询分页样本及只读详情。 -->
<template>
  <div ref="pageRoot" class="page-layout" :style="{ paddingTop: `${pagePadding}px` }">
    <BaseCard class="data-card">
      <template #title>
        <h3 class="card-title">{{ $t('acquisition-data.history') }}</h3>
        <el-tooltip placement="bottom-start" :trigger="['hover', 'focus']" :trigger-keys="[]">
          <template #content>
            <div class="help-content">
              <p>{{ $t('acquisition-data.timeZone') }}</p>
              <p>{{ $t('acquisition-data.retention') }}</p>
            </div>
          </template>
          <button class="help-trigger" type="button" :aria-label="$t('acquisition-data.help')" @click="$event.currentTarget.focus()" @keydown.esc.stop="$event.currentTarget.blur()">
            <el-icon><QuestionFilled /></el-icon>
          </button>
        </el-tooltip>
      </template>
      <template #actions>
        <div class="table-actions"><ActionButton @click="columns.reset">{{ $t('acquisition-data.resetWidths') }}</ActionButton></div>
      </template>
      <div class="filter-section">
        <el-form class="filter-form" label-position="top" @submit.prevent="submit">
          <el-form-item :label="$t('acquisition-data.plc')">
            <el-select v-model="plcId" :title="plcId || undefined" :aria-label="plcId ? $t('acquisition-data.selectedPlc', { plcId }) : $t('acquisition-data.plc')" :placeholder="$t('acquisition-data.selectPlc')" :disabled="optionsState !== 'ready' || !options.length" clearable>
              <el-option v-for="item in options" :key="item.plcId" class="plc-option" :label="item.plcId" :value="item.plcId">
                <span>{{ item.plcId }}</span>
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item :label="$t('acquisition-data.db')">
            <el-select v-model="dbNumber" :placeholder="$t('acquisition-data.selectDb')" :disabled="optionsState !== 'ready' || !options.length" clearable>
              <el-option v-for="db in dbNumbers" :key="db" :label="`DB${db}`" :value="db" />
            </el-select>
          </el-form-item>
          <el-form-item :label="$t('acquisition-data.from')">
            <el-input v-model="from" class="date-standard" :aria-label="$t('acquisition-data.from')" :placeholder="$t('acquisition-data.dateTimePlaceholder')" clearable @keydown.enter.prevent="submit" />
            <el-input v-model="from" class="date-narrow" type="textarea" :rows="3" :aria-label="$t('acquisition-data.from')" :placeholder="$t('acquisition-data.dateTimePlaceholder')" @keydown.enter.prevent="submit" />
          </el-form-item>
          <el-form-item :label="$t('acquisition-data.to')">
            <el-input v-model="to" class="date-standard" :aria-label="$t('acquisition-data.to')" :placeholder="$t('acquisition-data.dateTimePlaceholder')" clearable @keydown.enter.prevent="submit" />
            <el-input v-model="to" class="date-narrow" type="textarea" :rows="3" :aria-label="$t('acquisition-data.to')" :placeholder="$t('acquisition-data.dateTimePlaceholder')" @keydown.enter.prevent="submit" />
          </el-form-item>
          <el-form-item class="filter-actions"><ActionButton variant="primary" :disabled="optionsState !== 'ready' || !options.length" :loading="state === 'loading'" @click="submit">{{ $t('acquisition-data.query') }}</ActionButton></el-form-item>
        </el-form>
      </div>
      <div v-if="optionsState !== 'ready'" class="message" role="status">
        {{ $t(`acquisition-data.${optionsState === 'empty' ? 'emptyOptions' : optionsState}`) }}
        <ActionButton v-if="['error', 'forbidden'].includes(optionsState)" size="small" @click="loadOptions">{{ $t('acquisition-data.retry') }}</ActionButton>
      </div>
      <div v-else-if="state === 'invalid'" class="message" role="alert">{{ $t('acquisition-data.invalidRange') }}</div>
      <div v-else-if="state === 'idle'" class="message" role="status">{{ $t('acquisition-data.queryRange') }}</div>
      <div v-else-if="['error', 'forbidden'].includes(state)" class="message" role="alert">
        {{ $t(`acquisition-data.${state}`) }}
        <ActionButton size="small" @click="loadHistory">{{ $t('acquisition-data.retry') }}</ActionButton>
      </div>
      <div v-else-if="!options.length && state === 'ready'" class="message" role="status">{{ $t('acquisition-data.emptyOptions') }}</div>
      <template v-else>
        <div class="table-scroll">
          <el-table :key="columns.version.value" v-loading="state === 'loading'" :data="rows" border stripe class="vibe-table"
            :empty-text="$t(state === 'loading' ? 'acquisition-data.loading' : 'acquisition-data.emptyHistory')" @header-dragend="columns.onHeaderDragEnd">
            <el-table-column prop="plcId" :label="$t('acquisition-data.plc')" :width="columns.widths.plcId" :min-width="120" show-overflow-tooltip />
            <el-table-column prop="dbNumber" :label="$t('acquisition-data.db')" :width="columns.widths.dbNumber" :min-width="80">
              <template #default="{ row }">DB{{ row.dbNumber }}</template>
            </el-table-column>
            <el-table-column prop="sourceType" :label="$t('acquisition-data.columns.sourceType')" :width="columns.widths.sourceType" :min-width="120">
              <template #default="{ row }">{{ $t(`acquisition-data.source.${sourceKey(row.sourceType)}`) }}</template>
            </el-table-column>
            <el-table-column prop="sampleId" :label="$t('acquisition-data.columns.sampleId')" :width="columns.widths.sampleId" :min-width="150" />
            <el-table-column prop="sampledAt" :label="$t('acquisition-data.columns.sampledAt')" :width="columns.widths.sampledAt" :min-width="170">
              <template #default="{ row }"><span :title="row.sampledAt || ''">{{ formatShanghaiDateTime(row.sampledAt) || $t('acquisition-data.missingTime') }}</span></template>
            </el-table-column>
            <el-table-column prop="groupId" :label="$t('acquisition-data.columns.groupId')" :width="columns.widths.groupId" :min-width="120">
              <template #default="{ row }">{{ row.groupId ?? '—' }}</template>
            </el-table-column>
            <el-table-column prop="pointCount" :label="$t('acquisition-data.columns.pointCount')" :width="columns.widths.pointCount" :min-width="90" />
            <el-table-column :label="$t('acquisition-data.columns.actions')" width="120" align="center">
              <template #default="{ row }"><div class="row-actions"><ActionButton size="small" variant="row" @click="openDetail(row.id)">{{ $t('acquisition-data.detail') }}</ActionButton></div></template>
            </el-table-column>
          </el-table>
        </div>
        <div v-if="state === 'ready'" class="pagination-scroll">
          <el-pagination :current-page="page" :page-size="pageSize" :page-sizes="[20, 50, 100]" :total="total"
            layout="total, sizes, prev, pager, next" class="pagination" @current-change="changePage" @size-change="changeSize" />
        </div>
      </template>
    </BaseCard>
    <HistoryDetailDialog :visible="detailVisible" :state="detailState" :detail="detail" @update:visible="setDetailVisible" @retry="retryDetail" />
  </div>
</template>

<script setup>
import { onBeforeUnmount, ref, watch } from 'vue'
import { QuestionFilled } from '@element-plus/icons-vue'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import { formatShanghaiDateTime, shanghaiInputToRfc3339 } from '@/utils/date'
import { useTableColumnWidths } from '@/utils/tableColumnWidths'
import { getHistory, getHistoryDetail } from '../../api/index'
import { useAcquisitionScope, requestStatus, sourceKey } from '../../composables/useAcquisitionScope'
import HistoryDetailDialog from './HistoryDetailDialog.vue'

const { pageRoot, pagePadding, options, optionsState, plcId, dbNumber, dbNumbers, selection, loadOptions } = useAcquisitionScope()
const columns = useTableColumnWidths('acquisition-data.history', {
  plcId: { width: 190, minWidth: 120 }, dbNumber: { width: 100, minWidth: 80 }, sourceType: { width: 140, minWidth: 120 },
  sampleId: { width: 260, minWidth: 150 }, sampledAt: { width: 200, minWidth: 170 },
  groupId: { width: 190, minWidth: 120 }, pointCount: { width: 110, minWidth: 90 }
})
const now = Date.now()
const from = ref(formatShanghaiDateTime(new Date(now - 24 * 60 * 60 * 1000)))
const to = ref(formatShanghaiDateTime(new Date(now)))
const rows = ref([])
const state = ref('idle')
const page = ref(1)
const pageSize = ref(50)
const total = ref(0)
const detailVisible = ref(false)
const detailState = ref('idle')
const detail = ref(null)
let submitted = null
let selectedId = ''
let sequence = 0
let detailSequence = 0

function clearDetail() {
  detailSequence++
  detailVisible.value = false
  detail.value = null
  selectedId = ''
  detailState.value = 'idle'
}
function invalidate() {
  sequence++
  rows.value = []
  total.value = 0
  page.value = 1
  submitted = null
  state.value = 'idle'
  clearDetail()
}
watch([plcId, dbNumber, optionsState, from, to], invalidate, { flush: 'sync' })
// 同步清除旧响应，批量合并 PLC 变化触发的 DB 清空，只发送一次请求。
watch([plcId, dbNumber, optionsState], () => { if (optionsState.value === 'ready') submit() })

function submit() {
  const start = shanghaiInputToRfc3339(from.value)
  const end = shanghaiInputToRfc3339(to.value)
  const span = Date.parse(end) - Date.parse(start)
  invalidate()
  if (optionsState.value !== 'ready') return
  if (!start || !end || !(span > 0 && span <= 7 * 24 * 60 * 60 * 1000)) { state.value = 'invalid'; return }
  submitted = { ...selection(), from: start, to: end }
  loadHistory()
}
async function loadHistory() {
  if (!submitted || optionsState.value !== 'ready') return
  const current = ++sequence
  rows.value = []
  total.value = 0
  clearDetail()
  state.value = 'loading'
  try {
    const data = await getHistory({ ...submitted, page: page.value, pageSize: pageSize.value })
    if (current !== sequence) return
    rows.value = data.items
    total.value = data.total
    state.value = 'ready'
  } catch (error) {
    if (current !== sequence) return
    total.value = 0
    state.value = requestStatus(error)
  }
}
function changePage(value) { if (page.value !== value) { page.value = value; loadHistory() } }
function changeSize(value) { if (pageSize.value !== value) { pageSize.value = value; page.value = 1; loadHistory() } }
async function openDetail(id) {
  if (typeof id !== 'string' || !/^[1-9][0-9]*$/.test(id) || !rows.value.some(row => row.id === id)) return
  selectedId = id
  detailVisible.value = true
  detail.value = null
  detailState.value = 'loading'
  const current = ++detailSequence
  try {
    const data = await getHistoryDetail(id)
    if (current !== detailSequence) return
    detail.value = data
    detailState.value = 'ready'
  } catch (error) {
    if (current !== detailSequence) return
    const status = error?.response?.status ?? error?.code
    if (status === 401 || status === 403) {
      rows.value = []
      total.value = 0
      state.value = requestStatus(error)
      clearDetail()
    } else {
      detailState.value = status === 404 ? 'unavailable' : requestStatus(error)
    }
  }
}
function retryDetail() { if (selectedId) openDetail(selectedId) }
function setDetailVisible(value) { if (!value) clearDetail() }
onBeforeUnmount(() => { sequence++; detailSequence++ })
</script>

<style scoped>
/* 按侧栏展开后的实际内容宽度适配页面。 */
.page-layout { container-type: inline-size; }
.data-card :deep(.base-card__body) { padding: 0; }
.data-card :deep(.base-card__header) { flex-wrap: wrap; padding-block: 12px; }
.data-card :deep(.base-card__actions) { min-width: 0; max-width: 100%; flex: 0 1 auto; }
.data-card :deep(.base-card__title) { white-space: normal; overflow-wrap: anywhere; }
.card-title { margin: 0; color: var(--text-primary); font-size: 16px; font-weight: 590; line-height: 1.35; overflow-wrap: anywhere; }
.help-trigger { display: inline-flex; flex: 0 0 auto; align-items: center; justify-content: center; width: 24px; height: 24px; padding: 0; border: 0; border-radius: 50%; background: transparent; color: var(--text-secondary); font-size: 16px; cursor: pointer; }
.help-trigger:hover { color: var(--primary); }
.help-trigger:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
.help-content { max-width: min(340px, calc(100vw - 56px)); white-space: normal; overflow-wrap: anywhere; }
.help-content p { margin: 0; }
.help-content p + p { margin-top: 8px; }
.data-card :deep(.table-actions) { min-width: 0; max-width: 100%; flex-wrap: wrap; }
.data-card :deep(.table-actions .action-button) { max-width: 100%; min-height: 40px; height: auto; padding-block: 8px; white-space: normal; overflow-wrap: anywhere; }
.plc-option { height: auto; min-height: 34px; padding-block: 6px; line-height: 1.4; white-space: normal; overflow-wrap: anywhere; }
.date-narrow { display: none; }
.filter-section { padding: 20px 24px; border-bottom: 1px solid var(--border-secondary); }
.filter-form { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 200px), 1fr)); gap: 16px; align-items: end; }
.filter-form :deep(.el-form-item) { margin: 0; }
.filter-form :deep(.el-select), .filter-form :deep(.el-input), .filter-form :deep(.el-date-editor) { width: 100%; }
.table-scroll { width: 100%; padding: 24px 24px 0; overflow-x: auto; }
.pagination-scroll { width: 100%; padding: 18px 24px 24px; overflow-x: auto; }
.pagination { display: flex; justify-content: flex-end; width: max-content; min-width: 100%; }
.message { padding: 24px; color: var(--text-secondary); display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
@media (max-width: 600px) { .filter-section, .table-scroll { padding: 16px; } }

@container (min-width: 860px) {
  .filter-form { grid-template-columns: repeat(4, minmax(0, 1fr)) auto; }
}
@container (max-width: 180px) {
  .data-card :deep(.base-card__header) { padding: 12px 6px; gap: 8px; }
  .data-card :deep(.base-card__title-wrap), .data-card :deep(.base-card__actions) { width: 100%; min-width: 0; }
  .data-card :deep(.base-card__title) { white-space: normal; overflow-wrap: anywhere; }
  .data-card :deep(.table-actions) { width: 100%; flex-wrap: wrap; justify-content: flex-start; }
  .data-card :deep(.table-actions .action-button) { max-width: 100%; height: auto; min-height: 40px; padding: 8px 6px; margin-left: 0; white-space: normal; overflow-wrap: anywhere; }
  .filter-section, .table-scroll, .pagination-scroll { padding-inline: 4px; }
  .filter-form { gap: 8px; }
  .filter-form :deep(.el-form-item__label) { white-space: normal; height: auto; line-height: 1.4; overflow-wrap: anywhere; }
  .filter-form :deep(.el-input__wrapper) { padding-inline: 4px; }
}
@container (max-width: 250px) {
  .date-standard { display: none; }
  .date-narrow { display: block; }
  .date-narrow :deep(.el-textarea__inner) { padding: 6px 4px; resize: none; }
}
</style>
