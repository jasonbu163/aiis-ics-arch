<!--
  File Path: /frontend-next-js/src/app/equipment/views/drive/index.vue
  功能描述: 传动部分工艺参数页面，展示传动系统实时参数
  主要功能:
    - 使用标准表格卡片展示工艺参数
    - 使用标准表格卡片展示张力参数
    - 展示设定值、实际值、偏差与状态
    - 自动刷新数据
-->
<template>
  <div class="drive-params-container page-layout">
    <BaseCard class="drive-workspace-card" :title="$t('equipment.driveParams.title')" v-loading="loading">
      <template #actions>
        <ActionButton variant="refresh" :loading="loading" @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          {{ $t('common.refresh') }}
        </ActionButton>
      </template>
      <BusinessDataSourceSelect v-model="sourceSelection" />

      <section class="drive-content-section">
        <BaseCard class="drive-table-card" :title="$t('equipment.driveParams.processParams')" compact>
          <div class="table-scroll">
            <el-table :data="processParams" border stripe class="vibe-table drive-table">
              <el-table-column prop="nameKey" :label="$t('equipment.driveParams.parameter')" min-width="180">
                <template #default="{ row }">
                  <span class="parameter-name">{{ t(row.nameKey) }}</span>
                </template>
              </el-table-column>
              <el-table-column :label="$t('equipment.common.actual')" width="160" align="right">
                <template #default="{ row }">
                  <span class="value-text" :class="getValueClass(row)">
                    {{ formatCurrentValue(row) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column :label="$t('equipment.common.set')" width="160" align="right">
                <template #default="{ row }">
                  <span v-if="hasValue(row.set)">{{ formatValue(row.set, row.decimals) }} {{ row.unit }}</span>
                </template>
              </el-table-column>
              <el-table-column :label="$t('equipment.common.deviation')" width="160" align="right">
                <template #default="{ row }">
                  <span v-if="hasValue(row.deviation)" :class="getValueClass(row)">
                    {{ formatSignedValue(row.deviation, row.decimals) }} {{ row.unit }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column :label="$t('equipment.common.status')" width="120" align="center">
                <template #default="{ row }">
                  <el-tag v-if="row.status" :type="getTagType(row.status)" effect="light" round>
                    {{ getStatusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </BaseCard>

        <BaseCard class="drive-table-card" :title="$t('equipment.driveParams.tensionParams')" compact>
          <div class="table-scroll">
            <el-table :data="tensionParams" border stripe class="vibe-table drive-table">
              <el-table-column prop="nameKey" :label="$t('equipment.driveParams.station')" min-width="180">
                <template #default="{ row }">
                  <span class="parameter-name">{{ t(row.nameKey) }}</span>
                </template>
              </el-table-column>
              <el-table-column :label="$t('equipment.common.actual')" width="160" align="right">
                <template #default="{ row }">
                  <span class="value-text" :class="getValueClass(row)">
                    {{ formatValue(row.actual, 2) }} kN
                  </span>
                </template>
              </el-table-column>
              <el-table-column :label="$t('equipment.common.set')" width="160" align="right">
                <template #default="{ row }">
                  {{ formatValue(row.set, 2) }} kN
                </template>
              </el-table-column>
              <el-table-column :label="$t('equipment.common.deviation')" width="160" align="right">
                <template #default="{ row }">
                  <span :class="getValueClass(row)">{{ formatSignedValue(row.deviation, 2) }} kN</span>
                </template>
              </el-table-column>
              <el-table-column :label="$t('equipment.common.status')" width="120" align="center">
                <template #default="{ row }">
                  <el-tag :type="getTagType(row.status)" effect="light" round>
                    {{ getStatusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </BaseCard>
      </section>
    </BaseCard>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import BusinessDataSourceSelect from '@/components/BusinessDataSourceSelect.vue'
import { parseBusinessDataSource, businessDataSourceQuery, createRequestGeneration } from '@/utils/businessDataSource.mjs'

import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { Refresh } from '@element-plus/icons-vue'
import { getDriveData } from '@/app/equipment/api'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const sourceSelection = computed({
  get: () => parseBusinessDataSource(route.query),
  set: value => router.replace({ query: businessDataSourceQuery(route.query, value) })
})
const requestGeneration = createRequestGeneration()

let updateTimer = null
const loading = ref(false)

const processParams = ref([
  { id: 'tv', nameKey: 'equipment.driveParams.tv', kind: 'single', value: null, unit: '', decimals: 0 },
  { id: 'km', nameKey: 'equipment.driveParams.km', kind: 'single', value: null, unit: '', decimals: 2 },
  { id: 'oxygen', nameKey: 'equipment.driveParams.oxygen', kind: 'single', value: null, unit: 'ppm', decimals: 0 },
  { id: 'mufflePressure', nameKey: 'equipment.driveParams.mufflePressure', kind: 'single', value: null, unit: 'Pa', decimals: 0 },
  { id: 'dewPoint', nameKey: 'equipment.driveParams.dewPoint', kind: 'compare', set: null, actual: null, deviation: null, status: null, unit: '℃', decimals: 2 },
  { id: 'nh3Flow', nameKey: 'equipment.driveParams.nh3Flow', kind: 'compare', set: null, actual: null, deviation: null, status: null, unit: 'm³/h', decimals: 2 },
  { id: 'ngFlow', nameKey: 'equipment.driveParams.ngFlow', kind: 'compare', set: null, actual: null, deviation: null, status: null, unit: 'm³/h', decimals: 2 }
])

const tensionParams = ref([
  { id: 'uncoiler', nameKey: 'equipment.driveParams.tension.uncoiler', set: null, actual: null, deviation: null, status: null },
  { id: 'entryLooper', nameKey: 'equipment.driveParams.tension.entryLooper', set: null, actual: null, deviation: null, status: null },
  { id: 'furnace', nameKey: 'equipment.driveParams.tension.furnace', set: null, actual: null, deviation: null, status: null },
  { id: 'exitLooper', nameKey: 'equipment.driveParams.tension.exitLooper', set: null, actual: null, deviation: null, status: null },
  { id: 'recoiler', nameKey: 'equipment.driveParams.tension.recoiler', set: null, actual: null, deviation: null, status: null }
])

const hasValue = (value) => value !== undefined && value !== null

const getStatusText = (status) => {
  return status ? t(`equipment.driveParams.status.${status}`) : '-'
}

const getTagType = (status) => {
  if (status === 'danger') return 'danger'
  if (status === 'warning') return 'warning'
  return status ? 'success' : 'info'
}

const getValueClass = (row) => {
  return row.status ? `value-text--${row.status}` : ''
}

const formatValue = (value, decimals = 0) => {
  if (!hasValue(value)) return '-'
  return Number(value).toFixed(decimals)
}

const formatCurrentValue = (row) => {
  const value = hasValue(row.actual) ? row.actual : row.value
  const formatted = formatValue(value, row.decimals)
  return row.unit ? `${formatted} ${row.unit}` : formatted
}

const formatSignedValue = (value, decimals = 2) => {
  if (!hasValue(value)) return '-'
  const number = Number(value)
  return `${number > 0 ? '+' : ''}${number.toFixed(decimals)}`
}

const handleRefresh = () => {
  loadData()
}

const loadData = async () => {
  const generation = requestGeneration.begin()
  if (!sourceSelection.value.ready) { clearSourceData(); loading.value = false; return }
  loading.value = true
  try {
    const data = await getDriveData(sourceSelection.value)
    if (!requestGeneration.isCurrent(generation)) return
    if (data) {
      mapApiData(data)
    }
  } catch (error) {
    if (!requestGeneration.isCurrent(generation)) return
    clearSourceData()
    console.error('Failed to load drive data:', error)
    ElMessage.error(t('common.error'))
  } finally {
    if (requestGeneration.isCurrent(generation)) loading.value = false
  }
}

const mapApiData = (data) => {
  if (data.processItems?.length) {
    processParams.value.forEach(item => {
      const source = data.processItems.find(sourceItem => sourceItem.id === item.id)
      if (!source) return
      Object.assign(item, {
        value: source.value,
        set: source.set,
        actual: source.actual,
        deviation: source.deviation,
        status: source.status,
        unit: source.unit ?? item.unit,
        decimals: source.decimals ?? item.decimals
      })
    })
  } else if (data.processParams) {
    const pp = data.processParams
    processParams.value.forEach(item => {
      if (item.id === 'tv') item.value = pp.tv
      if (item.id === 'km') item.value = pp.km
      if (item.id === 'oxygen') item.value = pp.oxygen
      if (item.id === 'mufflePressure') item.value = pp.mufflePressure
      if (item.id === 'dewPoint') {
        item.set = pp.dewPointSet
        item.actual = pp.dewPointActual
        item.deviation = pp.dewPointActual - pp.dewPointSet
      }
      if (item.id === 'nh3Flow') {
        item.set = pp.nh3FlowSet
        item.actual = pp.nh3FlowActual
        item.deviation = pp.nh3FlowActual - pp.nh3FlowSet
      }
      if (item.id === 'ngFlow') {
        item.set = pp.ngFlowSet
        item.actual = pp.ngFlowActual
        item.deviation = pp.ngFlowActual - pp.ngFlowSet
      }
    })
  }

  if (data.tensionItems?.length) {
    tensionParams.value.forEach(item => {
      const source = data.tensionItems.find(sourceItem => sourceItem.id === item.id)
      if (!source) return
      Object.assign(item, {
        set: source.set,
        actual: source.actual,
        deviation: source.deviation,
        status: source.status
      })
    })
  } else if (data.tensionParams) {
    const tp = data.tensionParams
    tensionParams.value.forEach(item => {
      const setId = `${item.id}Set`
      const actualId = `${item.id}Actual`
      if (tp[setId] !== undefined) item.set = tp[setId]
      if (tp[actualId] !== undefined) item.actual = tp[actualId]
      item.deviation = item.actual - item.set
    })
  }
}

const updateData = () => {
  loadData()
}

const clearSourceData = () => {
  processParams.value.forEach(row => Object.assign(row, { value:null, set:null, actual:null, deviation:null, status:null }))
  tensionParams.value.forEach(row => Object.assign(row, { set:null, actual:null, deviation:null, status:null }))
}
watch(() => [route.query.dataSource, route.query.equipmentId], () => {
  requestGeneration.invalidate()
  clearSourceData()
  loadData()
})

onMounted(() => {
  clearSourceData()
  loadData()
  updateTimer = setInterval(updateData, 3000)
})

onBeforeUnmount(() => {
  if (updateTimer) {
    clearInterval(updateTimer)
  }
})
</script>

<style scoped>
.drive-params-container {
  display: flex;
  flex-direction: column;
  animation: fadeIn var(--transition-normal);
}

.drive-workspace-card :deep(.base-card__body) {
  padding: 0;
}

.drive-content-section {
  display: grid;
  gap: 20px;
  padding: 24px;
}

.drive-table-card :deep(.base-card__body) {
  padding: 0;
}

.table-scroll {
  overflow-x: auto;
  padding: 20px;
}

.drive-table {
  min-width: 760px;
}

.parameter-name {
  color: var(--text-primary);
  font-weight: 590;
}

.value-text {
  color: var(--text-primary);
  font-weight: 650;
}

.value-text--normal {
  color: var(--success);
}

.value-text--warning {
  color: var(--warning);
}

.value-text--danger {
  color: var(--danger);
}

@media (max-width: 768px) {
  .drive-content-section {
    padding: 16px;
    gap: 16px;
  }

  .table-scroll {
    padding: 16px;
  }
}
</style>
