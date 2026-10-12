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
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { Refresh } from '@element-plus/icons-vue'
import { getDriveData } from '@/app/equipment/api'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'

const { t } = useI18n()
let updateTimer = null
const loading = ref(false)

const processParams = ref([
  { id: 'tv', nameKey: 'equipment.driveParams.tv', kind: 'single', value: 1250, unit: '', decimals: 0 },
  { id: 'km', nameKey: 'equipment.driveParams.km', kind: 'single', value: 0.85, unit: '', decimals: 2 },
  { id: 'oxygen', nameKey: 'equipment.driveParams.oxygen', kind: 'single', value: 8, unit: 'ppm', decimals: 0 },
  { id: 'mufflePressure', nameKey: 'equipment.driveParams.mufflePressure', kind: 'single', value: 150, unit: 'Pa', decimals: 0 },
  { id: 'dewPoint', nameKey: 'equipment.driveParams.dewPoint', kind: 'compare', set: -45, actual: -46, deviation: -1, status: 'normal', unit: '℃', decimals: 2 },
  { id: 'nh3Flow', nameKey: 'equipment.driveParams.nh3Flow', kind: 'compare', set: 50, actual: 49, deviation: -1, status: 'normal', unit: 'm³/h', decimals: 2 },
  { id: 'ngFlow', nameKey: 'equipment.driveParams.ngFlow', kind: 'compare', set: 120, actual: 118, deviation: -2, status: 'normal', unit: 'm³/h', decimals: 2 }
])

const tensionParams = ref([
  { id: 'uncoiler', nameKey: 'equipment.driveParams.tension.uncoiler', set: 15, actual: 14.8, deviation: -0.2, status: 'normal' },
  { id: 'entryLooper', nameKey: 'equipment.driveParams.tension.entryLooper', set: 12, actual: 12.1, deviation: 0.1, status: 'normal' },
  { id: 'furnace', nameKey: 'equipment.driveParams.tension.furnace', set: 10, actual: 9.8, deviation: -0.2, status: 'normal' },
  { id: 'exitLooper', nameKey: 'equipment.driveParams.tension.exitLooper', set: 12, actual: 12.2, deviation: 0.2, status: 'normal' },
  { id: 'recoiler', nameKey: 'equipment.driveParams.tension.recoiler', set: 18, actual: 17.9, deviation: -0.1, status: 'normal' }
])

const hasValue = (value) => value !== undefined && value !== null

const getStatusText = (status) => {
  return t(`equipment.driveParams.status.${status || 'normal'}`)
}

const getTagType = (status) => {
  if (status === 'danger') return 'danger'
  if (status === 'warning') return 'warning'
  return 'success'
}

const getValueClass = (row) => {
  return row.status ? `value-text--${row.status}` : ''
}

const formatValue = (value, decimals = 0) => {
  if (!hasValue(value)) return ''
  return Number(value).toFixed(decimals)
}

const formatCurrentValue = (row) => {
  const value = hasValue(row.actual) ? row.actual : row.value
  const formatted = formatValue(value, row.decimals)
  return row.unit ? `${formatted} ${row.unit}` : formatted
}

const formatSignedValue = (value, decimals = 2) => {
  if (!hasValue(value)) return ''
  const number = Number(value)
  return `${number > 0 ? '+' : ''}${number.toFixed(decimals)}`
}

const handleRefresh = () => {
  loadData()
}

const loadData = async () => {
  loading.value = true
  try {
    const data = await getDriveData()
    if (data) {
      mapApiData(data)
    }
  } catch (error) {
    console.error('Failed to load drive data:', error)
    ElMessage.error(t('common.error'))
  } finally {
    loading.value = false
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

onMounted(() => {
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
