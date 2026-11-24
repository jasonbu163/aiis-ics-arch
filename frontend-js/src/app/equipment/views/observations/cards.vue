<!-- 配置驱动的设备实时卡片，四个设备页面复用。 -->
<template>
  <div class="page-layout observation-page">
    <BaseCard :title="t(route.meta.titleKey)">
      <template #actions>
        <div class="table-actions">
          <span v-if="applied.task || data?.taskNo" class="card-status-pill">
            {{ tr(applied.task ? 'currentTask' : 'recentSample') }} · {{ applied.task || data.taskNo }}
          </span>
          <el-switch v-model="autoRefresh" class="card-action-switch" :inactive-text="tr('autoRefresh')" :aria-label="tr('autoRefresh')" />
          <ActionButton :disabled="loading || initializing" @click="retry">{{ tr('refresh') }}</ActionButton>
        </div>
      </template>
      <el-form class="observation-toolbar" label-position="top" @submit.prevent="apply">
        <el-form-item :label="tr('deviceOrSource')">
          <el-select v-model="equipment" :placeholder="tr('selectDeviceOrSource')" filterable>
            <el-option v-for="device in devices" :key="device.equipmentId" :value="device.equipmentId"
              :label="sourceLabel(device, locale.startsWith('en') ? device.nameEn : device.nameZh)" />
          </el-select>
        </el-form-item>
        <el-form-item :label="tr('taskNo')">
          <el-select v-model="manualTask" :placeholder="tr('followRecent')" clearable :loading="loadingTasks">
            <el-option v-for="item in tasks" :key="item.taskNo" :value="item.taskNo" :label="item.taskNo" />
          </el-select>
        </el-form-item>
        <el-form-item class="observation-filter-actions">
          <div class="table-actions">
            <ActionButton native-type="submit" variant="primary" :disabled="!equipment">{{ tr('search') }}</ActionButton>
            <ActionButton :disabled="!devices.length" @click="restore">{{ tr('restoreDefault') }}</ActionButton>
          </div>
        </el-form-item>
      </el-form>
      <el-alert v-if="manualUnavailable" :title="tr('taskUnavailable')" type="warning" show-icon :closable="false" />
      <el-alert v-if="failed || taskOptionsFailed" :title="tr('loadFailed')" type="error" show-icon :closable="false" />
      <p v-if="(loading || initializing) && !data" class="observation-message" role="status">{{ t('common.loading') }}</p>
      <p v-else-if="!failed && !devices.length" class="observation-message" role="status">{{ tr('noSources') }}</p>
      <p v-else-if="data && !data.cards.length" class="observation-message" role="status">{{ tr('emptyCards') }}</p>
      <p v-else-if="data && !data.taskNo" class="observation-message" role="status">{{ tr('noSampleTask') }}</p>
      <div v-if="data?.taskNo && data.cards.length">
        <p v-if="data.tied" class="observation-notice" role="status">{{ tr('equalTime') }}</p>
        <div class="observation-grid" :class="{ 'observation-grid--production': page === 'production' }">
          <section v-for="card in data.cards" :key="card.cardKey" class="observation-card">
            <header class="observation-card__header">
              <h3>{{ card.title }}</h3>
              <el-tooltip :content="timeLabel(card)" placement="top" :trigger="['hover', 'focus']" :trigger-keys="[]">
                <span class="clock-trigger">
                  <button type="button" class="clock-action" :aria-label="timeLabel(card)"
                    :aria-expanded="expanded.has(card.cardKey)" @click="toggleTime(card.cardKey)">
                    <el-icon aria-hidden="true"><Clock /></el-icon>
                  </button>
                </span>
              </el-tooltip>
            </header>
            <div class="observation-card__body">
              <div v-for="item in card.items" :key="item.metricKey" class="observation-item">
                <div class="observation-label">{{ item.label }}<span v-if="item.unit"> ({{ item.unit }})</span></div>
                <div class="observation-value">
                  <el-tag v-if="!missing(item) && typeof item.value === 'boolean'" type="info" effect="plain" class="observation-boolean">
                    {{ formatted(item) }}
                  </el-tag>
                  <span v-else class="observation-measurement">{{ formatted(item) }}</span>
                  <el-tag v-if="missing(item)" type="info" size="small" class="observation-state">{{ tr('missing') }}</el-tag>
                  <el-tag v-else-if="item.dataState === 'stale'" type="warning" size="small" class="observation-state">{{ tr('stale') }}</el-tag>
                </div>
                <div v-if="expanded.has(card.cardKey)" class="observation-time">
                  {{ tr('sampledAt') }}: {{ !missing(item) && formatShanghaiDateTime(item.observedAt) || '—' }}
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </BaseCard>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { Clock } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import ActionButton from '@/components/common/ActionButton.vue'
import { sourceLabel } from '@/app/equipment/components/observations/columnModel'
import BaseCard from '@/components/common/BaseCard.vue'
import { formatShanghaiDateTime } from '@/utils/date'
import { equipmentOptions, latestCards, sampledTasks } from '../../api/observations'

const route = useRoute()
const { t, locale } = useI18n()
const tr = (key, params) => t(`equipment.observation.${key}`, params)
const page = computed(() => route.meta.observationPage)
const devices = ref([])
const equipment = ref('')
const manualTask = ref('')
const tasks = ref([])
const applied = ref({ equipment: '', task: '' })
const manualUnavailable = ref(false)
const data = ref(null)
const expanded = ref(new Set())
const autoRefresh = ref(true)
const loading = ref(false)
const loadingTasks = ref(false)
const initializing = ref(false)
const failed = ref(false)
const taskOptionsFailed = ref(false)
let timer
let generation = 0
let optionsGeneration = 0
let devicesGeneration = 0

function missing(item) { return item.dataState === 'missing' || item.value == null }
function formatted(item) {
  if (missing(item)) return '—'
  if (typeof item.value === 'number' && Number.isInteger(item.decimals)) return item.value.toFixed(item.decimals)
  return String(item.value)
}
function timeLabel(card) {
  return tr(expanded.value.has(card.cardKey) ? 'hideCardTimes' : 'showCardTimes', { card: card.title })
}
function toggleTime(key) {
  if (expanded.value.has(key)) expanded.value.delete(key)
  else expanded.value.add(key)
}
function changeSource() {
  manualTask.value = ''
  tasks.value = []
  return loadTasks()
}
async function loadTasks() {
  const source = equipment.value
  const current = ++optionsGeneration
  loadingTasks.value = !!source
  taskOptionsFailed.value = false
  if (!source) return
  try {
    const result = await sampledTasks(source)
    if (current === optionsGeneration) tasks.value = result.tasks
  } catch {
    if (current === optionsGeneration) taskOptionsFailed.value = true
  } finally {
    if (current === optionsGeneration) loadingTasks.value = false
  }
}
async function refresh() {
  if (!applied.value.equipment || !page.value || loading.value) return
  const selection = applied.value
  const current = ++generation
  loading.value = true
  if (equipment.value === selection.equipment && !loadingTasks.value) loadTasks()
  try {
    const result = await latestCards({ equipmentId: selection.equipment, pageKey: page.value,
      taskNo: selection.task || undefined }, locale.value)
    if (current !== generation) return
    if (data.value?.taskNo !== result.taskNo) expanded.value.clear()
    data.value = result
    failed.value = false
    manualUnavailable.value = false
  } catch (error) {
    if (current !== generation) return
    manualUnavailable.value = !!selection.task && error.response?.status === 404
    if (manualUnavailable.value) {
      data.value = null
      expanded.value.clear()
    }
    failed.value = !manualUnavailable.value
  } finally {
    if (current === generation) loading.value = false
  }
}
function supersede() {
  generation++
  loading.value = false
  failed.value = false
  manualUnavailable.value = false
}
function apply() {
  const changed = equipment.value !== applied.value.equipment || manualTask.value !== applied.value.task
  if (!changed && loading.value) return
  if (changed) {
    data.value = null
    expanded.value.clear()
  }
  applied.value = { equipment: equipment.value, task: manualTask.value }
  supersede()
  return refresh()
}
function restore() {
  equipment.value = devices.value[0]?.equipmentId || ''
  manualTask.value = ''
  return apply()
}
async function initialize() {
  if (initializing.value) return
  const current = ++devicesGeneration
  initializing.value = true
  failed.value = false
  try {
    const available = await equipmentOptions()
    if (current !== devicesGeneration) return
    devices.value = available
    await restore()
  } catch {
    if (current === devicesGeneration) failed.value = true
  } finally {
    if (current === devicesGeneration) initializing.value = false
  }
}
function retry() {
  return devices.value.length ? refresh() : initialize()
}
function scheduleRefresh() {
  window.clearInterval(timer)
  if (autoRefresh.value && page.value) timer = window.setInterval(refresh, 5000)
}
watch(equipment, changeSource, { flush: 'sync' })
watch([autoRefresh, page], scheduleRefresh)
watch(page, () => {
  supersede()
  if (!page.value) return
  data.value = null
  expanded.value.clear()
  refresh()
})
watch(locale, () => { supersede(); refresh() })
onMounted(() => { scheduleRefresh(); initialize() })
onBeforeUnmount(() => {
  generation++
  optionsGeneration++
  devicesGeneration++
  window.clearInterval(timer)
})
</script>

<style scoped>
.observation-page { --observation-inset: var(--space-lg); min-width: 0; }
.observation-page :deep(.base-card) { height: auto; min-width: 0; }
.observation-page :deep(.base-card__header) { padding-block: 10px; flex-wrap: wrap; }
.observation-page :deep(.base-card__actions) { min-width: 0; max-width: 100%; margin-inline-start: auto; }
.observation-toolbar {
  display: flex; flex-wrap: wrap; align-items: flex-end; gap: 4px 16px;
  margin: 0 calc(-1 * var(--observation-inset)) 16px;
  padding-inline: var(--observation-inset); border-bottom: 1px solid var(--border-secondary);
}
.observation-toolbar :deep(.el-form-item) { flex: 1 1 200px; min-width: 0; }
.observation-toolbar :deep(.el-select) { width: 100%; }
.observation-toolbar .observation-filter-actions { flex: 0 1 auto; margin-inline-start: auto; }
.observation-message, .observation-notice { color: var(--text-secondary); }
.observation-message { text-align: center; padding: var(--space-md); }
.observation-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 230px), 1fr)); gap: var(--space-md); }
.observation-grid--production { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.observation-card { min-width: 0; border: 1px solid var(--border-secondary); border-radius: var(--el-border-radius-base); background: var(--card-bg); }
.observation-card__header { display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 10px 14px; border-bottom: 1px solid var(--border-secondary); }
.observation-card h3 { margin: 0; font-size: 15px; overflow-wrap: anywhere; }
.observation-card__body { padding: 14px; }
.clock-trigger { display: flex; flex: none; }
.clock-action {
  display: inline-grid; place-items: center; width: 32px; height: 32px;
  border: 0; border-radius: var(--el-border-radius-small); background: transparent;
  color: var(--text-secondary); font-size: 16px; cursor: pointer;
}
.clock-action:hover, .clock-action[aria-expanded="true"] { color: var(--primary); background: var(--primary-subtle); }
.clock-action:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
.observation-item + .observation-item { margin-top: 12px; }
.observation-label, .observation-time { color: var(--text-secondary); overflow-wrap: anywhere; }
.observation-label { font-size: 13px; }
.observation-value { display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: center; gap: 8px; margin-top: 3px; }
.observation-measurement { color: var(--text-primary); font-size: 20px; font-weight: 600; overflow-wrap: anywhere; }
.observation-boolean { grid-column: 1; justify-self: start; }
.observation-state { grid-column: 2; justify-self: end; }
.observation-time { font-size: 12px; margin-top: 4px; }
@media (max-width: 768px) {
  .observation-page { --observation-inset: 18px; }
  .observation-grid--production { grid-template-columns: minmax(0, 1fr); }
}
</style>
