<!-- 温度、传动和清洗共用的过程历史曲线页面。 -->
<template>
  <div class="page-layout curve-page">
    <BaseCard :title="t(route.meta.titleKey)">
      <template #actions>
        <div class="table-actions">
          <span v-if="appliedSource" class="card-status-pill">{{ tr('appliedHistorySource', { source: appliedSource }) }}</span>
          <span v-if="applied?.taskNo" class="card-status-pill">
            {{ displayedMode === 'latest' ? tr('recentHistoryTask') : equipmentText('currentTask') }} · {{ applied.taskNo }}
          </span>
          <el-switch v-model="autoRefresh" class="card-action-switch" :inactive-text="equipmentText('autoRefresh')" :aria-label="equipmentText('autoRefresh')" />
          <ActionButton :disabled="loading || initializing" @click="retry">{{ equipmentText('refresh') }}</ActionButton>
        </div>
      </template>
      <el-form class="curve-toolbar" label-position="top" @submit.prevent="submit">
        <el-form-item :label="equipmentText('deviceOrSource')">
          <el-select v-model="draft.equipmentId" :placeholder="tr('allHistorySources')"
            clearable filterable :value-on-clear="''" @change="selectSource">
            <el-option value="" :label="tr('allHistorySources')" />
            <el-option v-for="device in devices" :key="device.equipmentId" :value="device.equipmentId"
              :label="deviceName(device)" />
          </el-select>
        </el-form-item>
        <el-form-item :label="equipmentText('taskNo')" :error="taskError">
          <el-autocomplete v-model="draft.taskNo" clearable :fetch-suggestions="taskSuggestions"
            :placeholder="tr('chooseHistoryTask')" @update:model-value="editTask" />
        </el-form-item>
        <el-form-item class="curve-time-range" :label="tr('historyTimeRange')" :error="formError" @input.capture="typeRange">
          <el-date-picker v-model="draft.range" type="datetimerange" value-format="YYYY-MM-DD HH:mm:ss"
            format="YYYY-MM-DD HH:mm:ss" :range-separator="'–'" @calendar-change="pickRange"
            @update:model-value="editRange" />
        </el-form-item>
        <el-form-item class="curve-filter-actions">
          <div class="table-actions">
            <ActionButton native-type="submit" variant="primary" :disabled="!devices.length">{{ equipmentText('search') }}</ActionButton>
            <ActionButton :disabled="!devices.length" @click="restore">{{ equipmentText('restoreDefault') }}</ActionButton>
          </div>
        </el-form-item>
      </el-form>
      <el-alert v-if="failed || taskOptionsFailed" :title="requestError ? tr(requestError) : equipmentText('loadFailed')" type="error" show-icon :closable="false">
        <ActionButton @click="retry">{{ tr('retry') }}</ActionButton>
      </el-alert>
      <p v-if="(loading || initializing) && !result" class="curve-message" role="status">{{ t('common.loading') }}</p>
      <p v-else-if="emptyMessage" class="curve-message" role="status">{{ emptyMessage }}</p>
      <div v-if="groups.length" class="curve-grid">
        <CurveChart v-for="group in groups" :key="group.curveGroupKey" :group="group" :range="appliedRange" />
      </div>
    </BaseCard>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import ActionButton from '@/components/common/ActionButton.vue'
import { sourceLabel } from '@/app/equipment/components/observations/columnModel'
import BaseCard from '@/components/common/BaseCard.vue'
import { formatShanghaiDateTime, shanghaiInputToRfc3339 } from '@/utils/date'
import CurveChart from '../../components/observations/CurveChart.vue'
import { historyCurves, historyDefaultContext, monitorOptions } from '../../api/observations'

const { t, locale } = useI18n()
const route = useRoute()
const tr = (key, params) => t(`monitor.observation.${key}`, params)
const equipmentText = key => t(`equipment.observation.${key}`)
const category = computed(() => route.meta.observationCategory)
const devices = ref([])
const draft = reactive({ equipmentId: '', taskNo: '', range: null })
const draftDirty = ref(false)
const formError = ref('')
const taskError = ref('')
const recentTasks = ref([])
const taskOptionsFailed = ref(false)
const applied = ref(null)
const appliedRange = computed(() => applied.value ? [applied.value.from, applied.value.to] : [])
const appliedSource = computed(() => {
  const id = applied.value?.equipmentId
  const device = devices.value.find(item => item.equipmentId === id)
  return device ? deviceName(device) : id
})
const appliedMode = ref('latest')
const displayedMode = ref('latest')
const result = ref(null)
const hasCurves = ref(null)
const loading = ref(false)
const initializing = ref(false)
const failed = ref(false)
const requestError = ref('')
const autoRefresh = ref(false)
let defaultSource = ''
let taskDiscovery = null
let draftRawRange = null
let explicitRange = false
let typedRange = null
let rangePending = false
let generation = 0
let tasksGeneration = 0
let devicesGeneration = 0
let timer

function drawable(point) { return point.present !== false && Number.isFinite(point.value) }
const groups = computed(() => result.value?.groups.filter(group =>
  group.series.some(series => series.points.some(drawable))) ?? [])
const emptyMessage = computed(() => {
  if (failed.value || loading.value || initializing.value) return ''
  if (!devices.value.length) return tr('noDevices')
  if (hasCurves.value === false) return tr('noCurves')
  if (!groups.value.length) return tr(appliedMode.value === 'task' ? 'noHistoryTaskSamples' : 'noHistorySamples')
  return ''
})

function deviceName(device) {
  return sourceLabel(device, locale.value.startsWith('en') ? device.nameEn : device.nameZh)
}

function supersede() {
  generation++
  loading.value = false
  failed.value = false
  requestError.value = ''
}

function markRangeEdited() {
  draftRawRange = null
  draftDirty.value = true
  formError.value = ''
}

function editRange() {
  if (!draft.range?.length) typedRange = null
  explicitRange = Boolean((typedRange ?? draft.range)?.some(Boolean))
  rangePending = false
  markRangeEdited()
}

function typeRange(event) {
  // Preserve typed values before the picker restores cleared or rejected input.
  const inputs = [...event.currentTarget.querySelectorAll('input')]
  const index = inputs.indexOf(event.target)
  if (index < 0) return
  typedRange ??= inputs.map(input => input.value)
  typedRange[index] = event.target.value
  explicitRange = typedRange.some(Boolean)
  rangePending = false
  markRangeEdited()
}

function pickRange() {
  typedRange = null
  explicitRange = true
  rangePending = true
  markRangeEdited()
}

function editTask() {
  draftDirty.value = true
  taskError.value = ''
}

function taskSuggestions(query) {
  const term = query.toUpperCase().trim()
  return recentTasks.value.filter(item => item.taskNo.includes(term)).map(item => ({ value: item.taskNo }))
}

function selectSource() {
  draftDirty.value = true
  recentTasks.value = []
  formError.value = ''
  return loadTaskOptions()
}

async function loadTaskOptions() {
  const requestedSource = draft.equipmentId
  const requestedCategory = category.value
  const current = ++tasksGeneration
  taskOptionsFailed.value = false
  if (!requestedSource || !requestedCategory) return
  try {
    const context = await historyDefaultContext({ equipmentId: requestedSource, category: requestedCategory })
    if (current === tasksGeneration) recentTasks.value = context.recentTasks
  } catch {
    if (current === tasksGeneration) taskOptionsFailed.value = true
  }
}

function syncDraft(anchor, task) {
  if (draftDirty.value) return
  Object.assign(draft, {
    taskNo: anchor?.taskNo ?? task ?? '',
    range: anchor ? [formatShanghaiDateTime(anchor.from), formatShanghaiDateTime(anchor.to)] : null
  })
  draftRawRange = anchor ? [anchor.from, anchor.to] : null
  explicitRange = false
  typedRange = null
  rangePending = false
}

async function refresh() {
  if (!devices.value.length || !category.value || loading.value) return
  const requestedCategory = category.value
  const mode = appliedMode.value
  const discovery = mode === 'task' ? taskDiscovery : { equipmentId: defaultSource || undefined }
  const current = ++generation
  loading.value = true
  failed.value = false
  requestError.value = ''
  try {
    let conditions = applied.value
    let context = null
    if (mode !== 'fixed') {
      context = await historyDefaultContext({ category: requestedCategory, ...discovery })
      if (current !== generation) return
      const anchor = context.anchor
      conditions = anchor ? { equipmentId: anchor.equipmentId, taskNo: anchor.taskNo, from: anchor.from, to: anchor.to } : null
    }
    const response = conditions ? await historyCurves({ ...conditions, category: requestedCategory }, locale.value) : null
    if (current !== generation) return
    if (context) {
      hasCurves.value = context.hasCurves
      if (!draftDirty.value) recentTasks.value = context.recentTasks
      syncDraft(context.anchor, discovery.taskNo)
    }
    applied.value = conditions
    displayedMode.value = mode === 'latest' ? 'latest' : 'fixed'
    result.value = response
    if (response) hasCurves.value = response.groups.length > 0
    failed.value = false
    if (mode === 'task' && conditions) {
      appliedMode.value = 'fixed'
      taskDiscovery = null
    }
  } catch (error) {
    if (current === generation) {
      failed.value = true
      const status = error?.response?.status ?? error?.code
      if (status === 403) requestError.value = 'historySourceForbidden'
      if (status === 503) requestError.value = 'historyTargetUnavailable'
      if ((error?.response?.data?.errorCode ?? error?.message) === 'equipment_observation.invalid_task') {
        requestError.value = 'invalidHistoryTask'
      }
    }
  } finally {
    if (current === generation) loading.value = false
  }
}

function submit() {
  formError.value = ''
  taskError.value = ''
  const input = draft.taskNo ?? ''
  const task = input.replace(/^[\x09-\x0d\x1c-\x20]+|[\x09-\x0d\x1c-\x20]+$/g, '')
  if (input && !/^[A-Za-z0-9_.-]{1,50}$/.test(task)) {
    taskError.value = tr('invalidHistoryTask')
    return
  }
  const taskNo = task.toUpperCase() || undefined
  const source = draft.equipmentId || undefined
  if (taskNo && !explicitRange) {
    if (loading.value && appliedMode.value === 'task' &&
        taskDiscovery.taskNo === taskNo && taskDiscovery.equipmentId === source) return
    taskDiscovery = { equipmentId: source, taskNo }
    appliedMode.value = 'task'
    draftDirty.value = false
    applied.value = null
    result.value = null
    hasCurves.value = null
    supersede()
    return refresh()
  }
  const range = draftRawRange ?? (typedRange ?? draft.range)?.map(shanghaiInputToRfc3339)
  if (rangePending || !range || range.length !== 2 || !range.every(Boolean) || range[1] < range[0]) {
    formError.value = tr(explicitRange ? 'invalidHistoryRange' : 'chooseRange')
    return
  }
  const equipmentId = source ?? applied.value?.equipmentId
  if (!equipmentId) {
    formError.value = tr('chooseDevice')
    return
  }
  const conditions = { equipmentId, taskNo, from: range[0], to: range[1] }
  const changed = JSON.stringify(conditions) !== JSON.stringify(applied.value)
  if (!changed && appliedMode.value === 'fixed' && loading.value) return
  if (changed) result.value = null
  applied.value = conditions
  appliedMode.value = 'fixed'
  taskDiscovery = null
  displayedMode.value = 'fixed'
  formError.value = ''
  draft.taskNo = conditions.taskNo || ''
  draftDirty.value = false
  supersede()
  return refresh()
}

function restore() {
  const source = draft.equipmentId || ''
  const samePendingDefault = loading.value && appliedMode.value === 'latest' && defaultSource === source
  tasksGeneration++
  taskOptionsFailed.value = false
  draftDirty.value = false
  draftRawRange = null
  explicitRange = false
  typedRange = null
  rangePending = false
  formError.value = ''
  taskError.value = ''
  if (samePendingDefault) return
  defaultSource = source
  taskDiscovery = null
  appliedMode.value = 'latest'
  supersede()
  if (defaultSource && defaultSource !== applied.value?.equipmentId) {
    result.value = null
    applied.value = null
  }
  return refresh()
}

async function initialize() {
  if (initializing.value) return
  const current = ++devicesGeneration
  initializing.value = true
  failed.value = false
  try {
    const available = await monitorOptions()
    if (current !== devicesGeneration) return
    devices.value = available
    await refresh()
  } catch {
    if (current === devicesGeneration) failed.value = true
  } finally {
    if (current === devicesGeneration) initializing.value = false
  }
}

function retry() {
  if (taskOptionsFailed.value && draft.equipmentId) loadTaskOptions()
  return devices.value.length ? refresh() : initialize()
}

function scheduleRefresh() {
  window.clearInterval(timer)
  if (autoRefresh.value && category.value) timer = window.setInterval(() => {
    if (appliedMode.value !== 'task') refresh()
  }, 5000)
}

watch([autoRefresh, category], scheduleRefresh)
watch(category, () => {
  supersede()
  tasksGeneration++
  taskOptionsFailed.value = false
  applied.value = null
  appliedMode.value = 'latest'
  result.value = null
  hasCurves.value = null
  recentTasks.value = []
  defaultSource = ''
  taskDiscovery = null
  draftDirty.value = false
  draftRawRange = null
  explicitRange = false
  typedRange = null
  rangePending = false
  formError.value = ''
  taskError.value = ''
  Object.assign(draft, { equipmentId: '', taskNo: '', range: null })
  refresh()
})
watch(locale, () => { supersede(); refresh() })
onMounted(initialize)
onBeforeUnmount(() => {
  generation++
  tasksGeneration++
  devicesGeneration++
  window.clearInterval(timer)
})
</script>

<style scoped>
.curve-page { --curve-inset: var(--space-lg); min-width: 0; }
.curve-page :deep(.base-card) { height: auto; min-width: 0; }
.curve-page :deep(.base-card__header) { padding-block: 10px; flex-wrap: wrap; }
.curve-page :deep(.base-card__actions) { min-width: 0; max-width: 100%; margin-inline-start: auto; }
.curve-toolbar {
  display: flex; flex-wrap: wrap; align-items: flex-end; gap: 4px 16px;
  margin: 0 calc(-1 * var(--curve-inset)) 16px;
  padding-inline: var(--curve-inset); border-bottom: 1px solid var(--border-secondary);
}
.curve-toolbar :deep(.el-form-item) { flex: 1 1 175px; min-width: 0; }
.curve-toolbar :deep(.el-select), .curve-toolbar :deep(.el-autocomplete), .curve-toolbar :deep(.el-date-editor) { width: 100%; min-width: 0; }
.curve-toolbar .curve-time-range { flex: 1 1 330px; }
.curve-toolbar .curve-filter-actions { flex: 0 1 auto; margin-inline-start: auto; }
.curve-grid { display: grid; gap: var(--space-md); min-width: 0; }
.curve-message { color: var(--text-secondary); text-align: center; padding: var(--space-md); }
@media (max-width: 768px) { .curve-page { --curve-inset: 18px; } }
@media (max-width: 600px) {
  /* Keep the open navigation usable above the curve page at phone widths. */
  :global(.main-layout:has(.curve-page)) { flex-direction: column; }
  :global(.main-layout:has(.curve-page) > .main-container) { flex: 1; min-height: 0; height: auto; }
  :global(.main-layout:has(.curve-page):not(:has(> .main-container-sidebar-hidden)) > .sidebar) {
    width: 100% !important; max-height: min(150px, 22dvh);
    flex: none; border-right: 0; border-bottom: 1px solid var(--border-primary);
  }
  :global(.main-layout:has(.curve-page):not(:has(> .main-container-sidebar-hidden)) .sidebar-brand-footer) {
    display: none;
  }
}
</style>
