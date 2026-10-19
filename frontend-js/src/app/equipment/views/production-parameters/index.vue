<!--
  文件路径: /frontend-next-js/src/app/equipment/views/production-parameters/index.vue
  功能描述: 生产参数页面，使用统一卡片规范展示当前生产过程参数
  主要功能:
    - 使用三段式主卡展示当前生产状态
    - 收敛展示当前卷基础信息、尺寸、重量与实时速度
    - 展示开卷、加热、均热、冷却、卷取过程详情
    - 自动刷新后端数据
-->
<template>
  <div class="production-parameters-page page-layout">
    <BaseCard class="production-parameters-workspace-card" :title="$t('equipment.productionParams.title')" v-loading="loading">
      <template #actions>
        <ActionButton variant="refresh" :loading="loading" @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          {{ $t('common.refresh') }}
        </ActionButton>
      </template>
      <BusinessDataSourceSelect v-model="sourceSelection" />

      <section class="production-parameters-summary-section">
        <div class="production-parameters-summary-panel">
          <div class="summary-primary">
            <div class="summary-status-main">
              <el-tag :type="statusType" size="large" class="status-tag">
                {{ statusText }}
              </el-tag>
              <span class="update-time">{{ $t('equipment.common.lastUpdate') }}: {{ lastUpdateText }}</span>
            </div>
          </div>

          <div class="summary-detail-grid">
            <div v-for="item in summaryItems" :key="item.label" class="summary-detail-item">
              <span class="summary-detail-label">{{ item.label }}</span>
              <strong class="summary-detail-value">{{ item.value }}</strong>
            </div>
          </div>
        </div>
      </section>

      <section class="production-parameters-content-section">
        <BaseCard class="process-card" :title="$t('equipment.productionParams.processDetail')" compact>
          <div class="table-scroll">
            <el-table :data="processSteps" border stripe class="vibe-table">
              <el-table-column prop="step" :label="$t('equipment.productionParams.processDetail')" min-width="140">
                <template #default="{ row }">
                  {{ translateStep(row.step) }}
                </template>
              </el-table-column>
              <el-table-column prop="status" :label="$t('equipment.common.status')" width="120">
                <template #default="{ row }">
                  <el-tag :type="getStepStatusType(row.status)" size="small">
                    {{ $t('equipment.productionParams.status.' + row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="startTime" :label="$t('common.startTime')" width="150" />
              <el-table-column prop="endTime" :label="$t('common.endTime')" width="150" />
              <el-table-column prop="duration" :label="$t('common.duration')" width="120" />
              <el-table-column prop="temperature" :label="$t('equipment.common.tempUnitLabel')" width="130" />
              <el-table-column prop="remark" :label="$t('common.remark')" min-width="160" />
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

import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import { getProductionParametersData } from '@/app/equipment/api'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const sourceSelection = computed({
  get: () => parseBusinessDataSource(route.query),
  set: value => router.replace({ query: businessDataSourceQuery(route.query, value) })
})
const requestGeneration = createRequestGeneration()


const UPDATE_INTERVAL = 5000
const loading = ref(false)
const updateTime = ref(new Date().toLocaleString())
let updateTimer = null

const productionParameters = ref({})

const processSteps = ref([])

const statusText = computed(() => {
  if (productionParameters.value.status === 'producing') return t('equipment.productionParams.producing')
  return productionParameters.value.status ? t(`equipment.productionParams.status.${productionParameters.value.status}`) : '-'
})
const statusType = computed(() => productionParameters.value.status === 'producing' ? 'success' : getStepStatusType(productionParameters.value.status))
const lastUpdateText = computed(() => productionParameters.value.lastUpdate || (sourceSelection.value.dataSource === 'http' ? '-' : updateTime.value))

const summaryItems = computed(() => [
  { label: t('equipment.productionParams.coilNo'), value: productionParameters.value.coilNo || '-' },
  { label: t('equipment.productionParams.grade'), value: productionParameters.value.grade || '-' },
  { label: t('equipment.productionParams.thickness'), value: `${formatNumber(productionParameters.value.thickness)} ${t('common.unit.mm')}` },
  { label: t('equipment.productionParams.width'), value: `${formatNumber(productionParameters.value.width)} ${t('common.unit.mm')}` },
  { label: t('equipment.productionParams.weight'), value: `${formatNumber(productionParameters.value.weight)} ${t('common.unit.ton')}` },
  { label: t('equipment.productionParams.speed'), value: `${formatNumber(productionParameters.value.speed)} ${t('common.unit.speed')}` },
  { label: t('equipment.productionParams.entryTime'), value: productionParameters.value.entryTime || '-' },
  { label: t('equipment.productionParams.totalTime'), value: `${formatNumber(productionParameters.value.totalTime)} ${t('common.unit.min')}` }
])

const formatNumber = (value) => value === null || value === undefined ? '-' : Number(value).toLocaleString(undefined, {
  maximumFractionDigits: 2
})

const getStepStatusType = (status) => {
  const map = {
    completed: 'success',
    processing: 'primary',
    pending: 'info'
  }
  return map[status] || 'info'
}

const translateStep = (step) => {
  if (!step) return '-'

  const match = step.match(/^(.*?)([0-9]*)$/)
  const key = match?.[1] || step
  const suffix = match?.[2] || ''

  return t(`equipment.productionParams.steps.${key}`) + (suffix ? ` ${suffix}` : '')
}

const handleRefresh = () => {
  loadData()
}

const loadData = async () => {
  const generation = requestGeneration.begin()
  if (!sourceSelection.value.ready) { clearSourceData(); loading.value = false; return }
  loading.value = true
  try {
    const data = await getProductionParametersData(sourceSelection.value)
    if (!requestGeneration.isCurrent(generation)) return
    if (data) {
      productionParameters.value = data.productionParameters || data
      processSteps.value = data.processSteps || []
    }
  } catch (error) {
    if (!requestGeneration.isCurrent(generation)) return
    clearSourceData()
    console.error('Failed to load production parameters data:', error)
    ElMessage.error(t('common.loadFailed'))
  } finally {
    if (requestGeneration.isCurrent(generation)) loading.value = false
    updateTime.value = new Date().toLocaleString()
  }
}

const clearSourceData = () => {
  productionParameters.value = {}
  processSteps.value = []
}
watch(() => [route.query.dataSource, route.query.equipmentId], () => {
  requestGeneration.invalidate()
  clearSourceData()
  loadData()
})

onMounted(() => {
  clearSourceData()
  loadData()
  updateTimer = setInterval(loadData, UPDATE_INTERVAL)
})

onBeforeUnmount(() => {
  if (updateTimer) {
    clearInterval(updateTimer)
  }
})
</script>

<style scoped>
.production-parameters-page {
  animation: fadeIn var(--transition-normal);
}

.production-parameters-workspace-card :deep(.base-card__body) {
  padding: 0;
}

.production-parameters-summary-section {
  padding: 24px;
  border-bottom: 1px solid var(--border-secondary);
}

.production-parameters-summary-panel {
  overflow: hidden;
  border: 1px solid var(--card-border);
  border-radius: calc(var(--card-radius) - 4px);
  background: var(--card-bg);
  box-shadow: var(--shadow-sm);
}

.summary-primary {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 24px;
  min-height: 78px;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-secondary);
  background: var(--bg-secondary);
}

.summary-status-main {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.status-tag {
  flex: 0 0 auto;
}

.update-time {
  color: var(--text-secondary);
  font-size: 14px;
}

.summary-detail-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1px;
  overflow: hidden;
  background: var(--border-secondary);
}

.summary-detail-item {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
  min-height: 92px;
  padding: 18px 20px;
  background: var(--card-bg);
}

.summary-detail-label {
  color: var(--text-secondary);
  font-size: 13px;
}

.summary-detail-value {
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 650;
  line-height: 1.35;
}

.production-parameters-content-section {
  padding: 24px;
}

.process-card :deep(.base-card__body) {
  padding: 0;
}

.table-scroll {
  width: 100%;
  padding: 24px;
  overflow-x: auto;
}

@media (max-width: 1400px) {
  .summary-detail-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 1100px) {
  .summary-detail-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .summary-primary {
    align-items: flex-start;
  }
}

@media (max-width: 768px) {
  .production-parameters-summary-section,
  .production-parameters-content-section {
    padding: 16px;
  }

  .summary-detail-grid {
    grid-template-columns: 1fr;
  }

  .table-scroll {
    padding: 16px;
  }
}
</style>
