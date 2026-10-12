<!--
  文件路径: /frontend-next-js/src/app/monitor/views/energy/index.vue
  功能描述: 能耗监控页面，使用新卡片规范构建统计与趋势视图
  主要功能:
    - 展示今日和本月能耗统计卡片
    - 展示能耗趋势曲线图
    - 自动刷新数据
-->
<template>
  <div class="monitor-energy-page page-layout">
    <section class="metric-grid">
      <MetricCard
        v-for="card in metricCards"
        :key="card.title"
        :title="card.title"
        :value="card.value"
        :unit="card.unit"
        :details="card.details"
        align="start"
      />
    </section>

    <BaseCard class="trend-card" :title="t('monitor.energyPage.trendTitle')" v-loading="loading">
      <template #actions>
        <div class="card-actions">
          <el-radio-group v-model="timeRange" size="small" class="card-action-segmented" @change="handleRefresh">
            <el-radio-button label="realtime">{{ t('monitor.energyPage.timeRange.realtime') }}</el-radio-button>
            <el-radio-button label="hour">{{ t('monitor.energyPage.timeRange.hour') }}</el-radio-button>
            <el-radio-button label="day">{{ t('monitor.energyPage.timeRange.day') }}</el-radio-button>
          </el-radio-group>
          <ActionButton variant="refresh" :loading="loading" @click="handleRefresh">
            <el-icon><Refresh /></el-icon>
            {{ t('monitor.energyPage.refresh') }}
          </ActionButton>
        </div>
      </template>

      <div class="trend-card__content">
        <el-skeleton :loading="loading" animated :rows="8">
          <template #default>
            <EnergyTrendChart :trends="energyTrends" />
          </template>
        </el-skeleton>
      </div>
    </BaseCard>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import ActionButton from '@/components/common/ActionButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import MetricCard from '@/components/common/MetricCard.vue'
import { getEnergyData } from '@/app/monitor/api'
import EnergyTrendChart from '@/app/monitor/components/EnergyTrendChart.vue'

const { t } = useI18n()
const timeRange = ref('realtime')
const loading = ref(false)
const energyStats = ref({
  todayTotal: { elect: 0, n2: 0 },
  monthTotal: { elect: 0, n2: 0 },
  currentPower: 0
})
const energyTrends = ref([])
let updateTimer = null

const metricCards = computed(() => [
  {
    title: t('monitor.energyStats.todayElectricity'),
    value: formatNumber(energyStats.value.todayTotal?.elect),
    unit: 'kWh',
    details: [
      {
        label: t('monitor.energyStats.todayNitrogen'),
        value: `${formatNumber(energyStats.value.todayTotal?.n2)} m³`
      }
    ]
  },
  {
    title: t('monitor.energyStats.monthElectricity'),
    value: formatNumber(energyStats.value.monthTotal?.elect),
    unit: 'kWh',
    details: [
      {
        label: t('monitor.energyStats.monthNitrogen'),
        value: `${formatNumber(energyStats.value.monthTotal?.n2)} m³`
      }
    ]
  },
  {
    title: t('monitor.energyStats.currentPower'),
    value: formatNumber(energyStats.value.currentPower),
    unit: 'kWh',
    details: [
      {
        label: t('monitor.energyStats.currentSource'),
        value: t('monitor.energyStats.realtimeCurve')
      }
    ]
  }
])

const formatNumber = (value) => Number(value || 0).toLocaleString(undefined, {
  maximumFractionDigits: 1
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await getEnergyData({ timeRange: timeRange.value })
    if (res) {
      energyStats.value = {
        todayTotal: res.todayTotal || { elect: 0, n2: 0 },
        monthTotal: res.monthTotal || { elect: 0, n2: 0 },
        currentPower: res.currentPower || 0
      }

      if (res.trends) {
        energyTrends.value = res.trends || []
      } else if (Array.isArray(res)) {
        energyTrends.value = res
      }
    }
  } catch (error) {
    console.error('Failed to load energy data:', error)
    ElMessage.error(t('monitor.energyPage.loadFailed'))
  } finally {
    loading.value = false
  }
}

const handleRefresh = () => {
  loadData()
}

onMounted(() => {
  loadData()
  updateTimer = setInterval(loadData, 10000)
})

onBeforeUnmount(() => {
  if (updateTimer) {
    clearInterval(updateTimer)
  }
})
</script>

<style scoped>
.monitor-energy-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
  animation: fadeIn var(--transition-normal);
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
  align-items: stretch;
}

.card-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  flex-wrap: wrap;
}

.trend-card {
  min-width: 0;
}

.trend-card :deep(.base-card__body) {
  padding: 0;
}

.trend-card__content {
  min-width: 0;
  padding: 24px;
}

@media (max-width: 1200px) {
  .metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .monitor-energy-page {
    gap: 16px;
  }

  .metric-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .trend-card__content {
    padding: 16px;
  }
}
</style>
