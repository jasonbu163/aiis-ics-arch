<!-- 温度、传动和清洗共用的过程历史曲线页面。 -->
<template>
  <div class="page-layout">
    <BaseCard :title="$t(route.meta.titleKey)" v-loading="loading">
      <div class="curve-toolbar">
        <el-select v-model="equipment" :placeholder="t('equipment.observation.selectDeviceOrSource')" filterable>
          <el-option v-for="device in devices" :key="device.equipmentId" :value="device.equipmentId"
            :label="sourceLabel(device, locale.startsWith('en') ? device.nameEn : device.nameZh)" />
        </el-select>
        <el-input v-model="task" clearable :placeholder="t('equipment.observation.taskNo')" />
        <el-date-picker v-model="range" type="datetimerange" value-format="YYYY-MM-DD HH:mm:ss"
          format="YYYY-MM-DD HH:mm:ss" :range-separator="'–'" />
        <ActionButton variant="primary" @click="refresh">{{ t('equipment.observation.search') }}</ActionButton>
      </div>
      <el-alert v-if="failed" :title="t('equipment.observation.loadFailed')" type="error" show-icon :closable="false">
        <ActionButton @click="retry">{{ t('monitor.observation.retry') }}</ActionButton>
      </el-alert>
      <EmptyAxes v-else-if="!equipment" :reason="t(devices.length ? 'monitor.observation.chooseDevice' : 'monitor.observation.noDevices')" />
      <EmptyAxes v-else-if="!range?.length" :reason="t('monitor.observation.chooseRange')" />
      <EmptyAxes v-else-if="result && !result.groups.length" :reason="t('monitor.observation.noCurves')" />
      <div v-else class="curve-grid">
        <CurveChart v-for="group in result?.groups || []" :key="group.curveGroupKey" :group="group" :range="chartRange" />
      </div>
    </BaseCard>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import ActionButton from '@/components/common/ActionButton.vue'
import { sourceLabel } from '@/app/equipment/components/observations/columnModel'
import BaseCard from '@/components/common/BaseCard.vue'
import { shanghaiInputToRfc3339 } from '@/utils/date'
import CurveChart from '../../components/observations/CurveChart.vue'
import EmptyAxes from '../../components/observations/EmptyAxes.vue'
import { historyCurves, monitorOptions } from '../../api/observations'

const { t, locale } = useI18n()
const route = useRoute()
const devices = ref([])
const equipment = ref('')
const task = ref('')
const range = ref(null)
const chartRange = computed(() => range.value?.length === 2 ? range.value.map(shanghaiInputToRfc3339) : [])
const result = ref(null)
const loading = ref(false)
const failed = ref(false)
let generation = 0

async function refresh() {
  if (!equipment.value || !range.value?.length) return
  const current = ++generation
  loading.value = true
  try {
    const data = await historyCurves({ equipmentId: equipment.value, category: route.meta.observationCategory,
      taskNo: task.value || undefined, from: shanghaiInputToRfc3339(range.value[0]), to: shanghaiInputToRfc3339(range.value[1]) }, locale.value)
    if (current === generation) { result.value = data; failed.value = false }
  } catch { if (current === generation) failed.value = true }
  finally { if (current === generation) loading.value = false }
}
watch([equipment, () => route.meta.observationCategory], () => {
  generation++
  result.value = null
  failed.value = false
  loading.value = false
  refresh()
})
watch([task, range], () => {
  generation++
  result.value = null
  loading.value = false
})
watch(locale, refresh)
async function initialize() {
  try { devices.value = await monitorOptions(); equipment.value = devices.value[0]?.equipmentId || ''; failed.value = false }
  catch { failed.value = true }
}
async function retry() { if (!devices.value.length) await initialize(); if (equipment.value && range.value?.length) await refresh() }
onMounted(initialize)
</script>

<style scoped>
.curve-toolbar { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 18px; }
.curve-toolbar .el-select, .curve-toolbar .el-input { width: 210px; }
.curve-grid { display: grid; gap: 14px; }
</style>
