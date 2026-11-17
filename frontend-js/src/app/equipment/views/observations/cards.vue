<!-- 配置驱动的设备实时卡片，四个设备页面复用。 -->
<template>
  <div class="page-layout observation-page">
    <BaseCard :title="$t(route.meta.titleKey)" v-loading="loading">
      <div class="observation-toolbar">
        <el-select v-model="equipment" :placeholder="t('equipment.observation.selectDevice')" filterable>
          <el-option v-for="device in devices" :key="device.equipmentId" :value="device.equipmentId"
            :label="locale.startsWith('en') ? device.nameEn : device.nameZh" />
        </el-select>
        <el-select v-model="manualTask" :placeholder="t('equipment.observation.followRecent')" clearable>
          <el-option v-for="item in tasks" :key="item.taskNo" :value="item.taskNo" :label="item.taskNo" />
        </el-select>
        <ActionButton v-if="manualTask" @click="manualTask = ''">{{ t('equipment.observation.followRecent') }}</ActionButton>
        <ActionButton @click="refresh">{{ t('equipment.observation.refresh') }}</ActionButton>
        <span v-if="data?.taskNo">{{ t('equipment.observation.recentSample') }}: {{ data.taskNo }}</span>
        <span v-else-if="data">{{ t('equipment.observation.noSampleTask') }}</span>
        <span v-if="data?.tied">{{ t('equipment.observation.equalTime') }}</span>
      </div>
      <el-alert v-if="manualUnavailable" :title="t('equipment.observation.taskUnavailable')" type="warning" show-icon :closable="false" />
      <el-alert v-if="failed" :title="t('equipment.observation.loadFailed')" type="error" show-icon :closable="false" />
      <el-empty v-else-if="data && !data.cards.length" :description="t('equipment.observation.emptyCards')" />
      <div v-else class="observation-grid">
        <section v-for="card in data?.cards || []" :key="card.cardKey" class="observation-card">
          <h3>{{ card.title }}</h3>
          <div v-for="item in card.items" :key="item.metricKey" class="observation-item">
            <div class="observation-label">{{ item.label }}<span v-if="item.unit"> ({{ item.unit }})</span></div>
            <div class="observation-value">
              <span>{{ formatted(item) }}</span>
              <el-tag v-if="item.dataState === 'stale'" type="warning" size="small">{{ t('equipment.observation.stale') }}</el-tag>
            </div>
            <div v-if="item.dataState === 'stale'" class="observation-time">
              {{ t('equipment.observation.sampledAt') }}: {{ formatShanghaiDateTime(item.observedAt) || '—' }}
            </div>
          </div>
        </section>
      </div>
    </BaseCard>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import { formatShanghaiDateTime } from '@/utils/date'
import { equipmentOptions, latestCards, sampledTasks } from '../../api/observations'

const route = useRoute()
const { t, locale } = useI18n()
const equipment = ref('')
const devices = ref([])
const tasks = ref([])
const manualTask = ref('')
const manualUnavailable = ref(false)
const data = ref(null)
const loading = ref(false)
const failed = ref(false)
let timer
let generation = 0

function formatted(item) {
  if (item.dataState === 'missing' || item.value === null) return '—'
  if (typeof item.value === 'number' && Number.isInteger(item.decimals)) return item.value.toFixed(item.decimals)
  return String(item.value)
}
async function refresh() {
  if (!equipment.value) return
  const current = ++generation
  loading.value = true
  try {
    const list = await sampledTasks(equipment.value)
    if (current !== generation) return
    tasks.value = list.tasks
    if (manualTask.value && !tasks.value.some(item => item.taskNo === manualTask.value)) {
      manualUnavailable.value = true; data.value = null; failed.value = false; return
    }
    const result = await latestCards({ equipmentId: equipment.value, pageKey: route.meta.observationPage,
      taskNo: manualTask.value || undefined }, locale.value)
    if (current === generation) { data.value = result; failed.value = false; manualUnavailable.value = false }
  } catch {
    if (current === generation) failed.value = true
  } finally {
    if (current === generation) loading.value = false
  }
}
async function initialize() {
  try {
    devices.value = await equipmentOptions()
    equipment.value = devices.value[0]?.equipmentId || ''
  } catch { failed.value = true }
}
watch(equipment, () => { manualTask.value = ''; tasks.value = []; manualUnavailable.value = false })
watch([equipment, manualTask, () => route.meta.observationPage], () => {
  generation++
  data.value = null
  failed.value = false
  loading.value = false
  refresh()
})
watch(locale, refresh)
onMounted(() => { initialize(); timer = window.setInterval(refresh, 5000) })
onBeforeUnmount(() => { generation++; window.clearInterval(timer) })
</script>

<style scoped>
.observation-toolbar { display: flex; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 18px; }
.observation-toolbar .el-select { width: 220px; }
.observation-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 14px; }
.observation-card { border: 1px solid var(--border-color); border-radius: 8px; padding: 14px; background: var(--bg-card); }
.observation-card h3 { margin: 0 0 12px; padding-bottom: 10px; border-bottom: 1px solid var(--border-color); font-size: 15px; }
.observation-item + .observation-item { margin-top: 12px; }
.observation-label { color: var(--text-secondary); font-size: 13px; }
.observation-value { display: flex; align-items: center; gap: 8px; margin-top: 3px; font-size: 20px; font-weight: 600; }
.observation-time { color: var(--text-secondary); font-size: 12px; margin-top: 4px; }
</style>
