<!--
  文件路径: /frontend-next-js/src/app/monitor/views/temperature/index.vue
  功能描述: 过程监控曲线页面，作为组件编排器管理 Tab 状态和数据获取
  主要功能:
    - 管理温度、张力、速度、质量四个 Tab
    - 负责从后端 API 获取全量曲线数据
    - 将数据通过 props 传递给子组件
-->
<template>
  <div class="monitor-temperature-page page-layout">
    <BaseCard class="monitor-workspace-card" :title="$t('monitor.temperature')" v-loading="loading">
      <BusinessDataSourceSelect v-model="sourceSelection" />
      <section class="monitor-control-section">
        <el-form class="monitor-control-form" label-position="top">
          <el-form-item :label="$t('monitor.temperatureControl.date')">
            <el-date-picker
              v-model="selectedDate"
              type="date"
              :placeholder="$t('common.pleaseSelect')"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              :clearable="false"
            />
          </el-form-item>
          <el-form-item class="curve-type-field" :label="$t('monitor.temperatureControl.curveType')">
            <el-select v-model="activeTab" :placeholder="$t('monitor.temperatureControl.curveType')">
              <el-option value="temperature" :label="$t('monitor.temperatureTabs.temperature')" />
              <el-option value="tension" :label="$t('monitor.temperatureTabs.tension')" />
              <el-option value="speed" :label="$t('monitor.temperatureTabs.speed')" />
              <el-option value="quality" :label="$t('monitor.temperatureTabs.quality')" />
            </el-select>
          </el-form-item>
          <el-form-item class="monitor-filter-actions">
            <ActionButton variant="primary" :loading="loading" @click="fetchData">
              <el-icon><Search /></el-icon>
              {{ $t('common.search') }}
            </ActionButton>
            <ActionButton @click="handleReset">
              <el-icon><Refresh /></el-icon>
              {{ $t('common.reset') }}
            </ActionButton>
          </el-form-item>
        </el-form>
      </section>

      <section class="monitor-content-section">
        <TemperatureCurve v-if="activeTab === 'temperature'" :data="curveData" active />
        <TensionCurve v-else-if="activeTab === 'tension'" :data="curveData" active />
        <SpeedCurve v-else-if="activeTab === 'speed'" :data="curveData" active />
        <QualityCurve v-else :data="curveData" active />
      </section>
    </BaseCard>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import BusinessDataSourceSelect from '@/components/BusinessDataSourceSelect.vue'
import { parseBusinessDataSource, businessDataSourceQuery, createRequestGeneration } from '@/utils/businessDataSource.mjs'

import { ref, onMounted, computed, watch } from 'vue'
import { Refresh, Search } from '@element-plus/icons-vue'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import { getTemperatureData } from '@/app/monitor/api'
import { formatDate } from '@/utils/date'
import TemperatureCurve from '@/app/monitor/components/TemperatureCurve.vue'
import TensionCurve from '@/app/monitor/components/TensionCurve.vue'
import SpeedCurve from '@/app/monitor/components/SpeedCurve.vue'
import QualityCurve from '@/app/monitor/components/QualityCurve.vue'

const route = useRoute()
const router = useRouter()
const sourceSelection = computed({
  get: () => parseBusinessDataSource(route.query),
  set: value => router.replace({ query: businessDataSourceQuery(route.query, value) })
})
const requestGeneration = createRequestGeneration()

const activeTab = ref('temperature')
const selectedDate = ref(formatDate(new Date()))
const curveData = ref({})
const loading = ref(false)
const defaultTab = 'temperature'

const resetForm = () => {
  activeTab.value = defaultTab
  selectedDate.value = formatDate(new Date())
}

/**
 * 获取监控数据
 */
const fetchData = async () => {
  const generation = requestGeneration.begin()
  curveData.value = { trends: [], latest: {} }
  if (!sourceSelection.value.ready) { loading.value = false; return }
  loading.value = true
  try {
    const data = await getTemperatureData({ ...sourceSelection.value, date: selectedDate.value })
    if (!requestGeneration.isCurrent(generation)) return
    curveData.value = data || {}
  } catch (error) {
    console.error('Failed to fetch monitoring data:', error)
  } finally {
    if (requestGeneration.isCurrent(generation)) loading.value = false
  }
}

const handleReset = () => {
  resetForm()
  fetchData()
}

watch(() => [route.query.dataSource, route.query.equipmentId, selectedDate.value], () => {
  requestGeneration.invalidate()
  curveData.value = { trends: [], latest: {} }
  fetchData()
})

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.monitor-temperature-page {
  display: flex;
  flex-direction: column;
  animation: fadeIn var(--transition-normal);
}

.monitor-workspace-card :deep(.base-card__body) {
  padding: 0;
}

.monitor-control-section {
  padding: 24px;
  border-bottom: 1px solid var(--border-secondary);
}

.monitor-control-form {
  display: grid;
  grid-template-columns: minmax(360px, 1.35fr) minmax(240px, 0.8fr) auto;
  gap: 22px;
  align-items: end;
  width: 100%;
}

.monitor-control-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.monitor-control-form :deep(.el-form-item__label) {
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 650;
  line-height: 1.2;
  margin-bottom: 8px;
  padding: 0;
}

.monitor-control-form :deep(.el-date-editor),
.monitor-control-form :deep(.el-select) {
  width: 100%;
}

.monitor-filter-actions {
  justify-self: end;
}

.monitor-filter-actions :deep(.el-form-item__content) {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  flex-wrap: nowrap;
}

.monitor-content-section {
  min-width: 0;
  padding: 24px;
}

@media (max-width: 768px) {
  .monitor-control-section,
  .monitor-content-section {
    padding: 16px;
  }

  .monitor-control-form {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .monitor-filter-actions {
    justify-self: start;
  }

  .monitor-filter-actions :deep(.el-form-item__content) {
    justify-content: flex-start;
    flex-wrap: wrap;
  }
}
</style>
