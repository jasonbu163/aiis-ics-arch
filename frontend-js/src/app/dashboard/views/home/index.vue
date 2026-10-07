<!--
  文件路径: /frontend-next-js/src/app/dashboard/views/home/index.vue
  功能描述: 系统工作台首页，整合各功能模块组件
  主要功能:
    - 生产数据统计卡片展示 (StatCards)
    - 数据可视化图表展示 (6个独立图表组件)
    - 当前生产状态展示 (ProductionStatus)
    - 近期计划列表展示 (RecentPlans)
    - 快捷入口导航 (QuickLinks)
-->
<template>
  <div class="dashboard page-layout">
    <el-row :gutter="20" class="chart-row">
      <el-col :span="24">
        <StatCards :stats="stats" />
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="16">
        <ProductionTrendChart :data="productionTrend" />
      </el-col>
      <el-col :xs="24" :lg="8">
        <QualityPieChart :data="qualityDistribution" />
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="8">
        <OEERadarChart :data="oeeAnalysis" />
      </el-col>
      <el-col :xs="24" :lg="16">
        <TemperatureTrendChart :data="temperatureTrend" @refresh="loadDashboardData" />
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="12">
        <EnergyMonitorChart :data="energyConsumption" />
      </el-col>
      <el-col :xs="24" :lg="12">
        <DowntimeAnalysisChart :data="downtimeAnalysis" />
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="12">
        <ProductionStatus :production-status="productionStatus" />
      </el-col>
      <el-col :xs="24" :lg="12">
        <RecentPlans :recent-plans="recentPlans" />
      </el-col>
    </el-row>

    <!-- <el-row :gutter="20" class="chart-row">
      <el-col :span="24">
        <QuickLinks :quick-links="quickLinks" />
      </el-col>
    </el-row> -->
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import {
  getDashboardStats,
  getProductionTrend,
  getQualityDistribution,
  getOEEAnalysis,
  getTemperatureTrend,
  getEnergyConsumption,
  getDowntimeAnalysis,
  getProductionStatus,
  getRecentPlans
} from '@/app/dashboard/api'

// 导入子组件
import StatCards from '@/app/dashboard/components/StatCards.vue'
import ProductionTrendChart from '@/app/dashboard/components/ProductionTrendChart.vue'
import QualityPieChart from '@/app/dashboard/components/QualityPieChart.vue'
import OEERadarChart from '@/app/dashboard/components/OEERadarChart.vue'
import TemperatureTrendChart from '@/app/dashboard/components/TemperatureTrendChart.vue'
import EnergyMonitorChart from '@/app/dashboard/components/EnergyMonitorChart.vue'
import DowntimeAnalysisChart from '@/app/dashboard/components/DowntimeAnalysisChart.vue'
import ProductionStatus from '@/app/dashboard/components/ProductionStatus.vue'
import RecentPlans from '@/app/dashboard/components/RecentPlans.vue'
import QuickLinks from '@/app/dashboard/components/QuickLinks.vue'

const { t } = useI18n()

const loading = ref(false)

// 数据状态
const stats = ref({
  todayProduction: 0,
  pendingPlans: 0,
  completedCoils: 0,
  oee: 0,
  energyConsumption: 0
})

const productionTrend = ref({ days: [], actual: [], target: [] })
const qualityDistribution = ref({ grades: [] })
const oeeAnalysis = ref({ indicators: [], currentWeek: [], lastWeek: [] })
const temperatureTrend = ref({ zones: [], hours: [], data: [] })
const energyConsumption = ref({ hours: [], electricity: [], gas: [] })
const downtimeAnalysis = ref({ reasons: [], duration: [], colors: [] })
const productionStatus = ref({
  onlineCoil: { id: '', progress: 0, status: '' },
  readyCoil: { id: '', grade: '', weight: 0 },
  currentSpeed: 0,
  furnaceTemp: 0
})
const recentPlans = ref([])
const quickLinks = ref([
  { nameKey: 'planManagement', icon: 'Calendar', bgColor: 'var(--primary)', path: '/plan/list' },
  { nameKey: 'performanceQuery', icon: 'DataLine', bgColor: 'var(--danger)', path: '/performance/list' },
  { nameKey: 'monitorCurve', icon: 'TrendCharts', bgColor: 'var(--info)', path: '/monitor/temperature' },
  { nameKey: 'energyStats', icon: 'Cpu', bgColor: 'var(--warning)', path: '/monitor/energy' },
  { nameKey: 'efficiencyStats', icon: 'DataAnalysis', bgColor: 'var(--success)', path: '/performance/efficiency' },
  { nameKey: 'equipmentStatus', icon: 'SetUp', bgColor: 'var(--primary-light)', path: '/equipment/production-parameters' }
])

let refreshTimer = null

const loadDashboardData = async () => {
  loading.value = true
  try {
    // 并行加载所有数据
    const [
      statsRes,
      trendRes,
      qualityRes,
      oeeRes,
      tempRes,
      energyRes,
      downtimeRes,
      statusRes,
      plansRes
    ] = await Promise.allSettled([
      getDashboardStats().catch(() => ({})),
      getProductionTrend().catch(() => ({ days: [], actual: [], target: [] })),
      getQualityDistribution().catch(() => ({ grades: [] })),
      getOEEAnalysis().catch(() => ({ indicators: [], currentWeek: [], lastWeek: [] })),
      getTemperatureTrend().catch(() => ({ zones: [], hours: [], data: [] })),
      getEnergyConsumption().catch(() => ({ hours: [], electricity: [], gas: [] })),
      getDowntimeAnalysis().catch(() => ({ reasons: [], duration: [], colors: [] })),
      getProductionStatus().catch(() => ({ onlineCoil: { id: '', progress: 0, status: '' }, readyCoil: { id: '', grade: '', weight: 0 }, currentSpeed: 0, furnaceTemp: 0 })),
      getRecentPlans().catch(() => ({ plans: [] }))
    ])

    // 更新状态
    stats.value = statsRes.status === 'fulfilled' ? statsRes.value : {}
    productionTrend.value = trendRes.status === 'fulfilled' ? trendRes.value : { days: [], actual: [], target: [] }
    qualityDistribution.value = qualityRes.status === 'fulfilled' ? qualityRes.value : { grades: [] }
    oeeAnalysis.value = oeeRes.status === 'fulfilled' ? oeeRes.value : { indicators: [], currentWeek: [], lastWeek: [] }
    temperatureTrend.value = tempRes.status === 'fulfilled' ? tempRes.value : { zones: [], hours: [], data: [] }
    energyConsumption.value = energyRes.status === 'fulfilled' ? energyRes.value : { hours: [], electricity: [], gas: [] }
    downtimeAnalysis.value = downtimeRes.status === 'fulfilled' ? downtimeRes.value : { reasons: [], duration: [], colors: [] }
    productionStatus.value = statusRes.status === 'fulfilled' ? statusRes.value : { onlineCoil: { id: '', progress: 0, status: '' }, readyCoil: { id: '', grade: '', weight: 0 }, currentSpeed: 0, furnaceTemp: 0 }
    recentPlans.value = plansRes.status === 'fulfilled' ? plansRes.value?.plans || [] : []
  } catch (error) {
    ElMessage.error(t('plan.messages.loadError'))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDashboardData()
  refreshTimer = setInterval(loadDashboardData, 30000)
})

onBeforeUnmount(() => {
  clearInterval(refreshTimer)
})
</script>

<style scoped>
.dashboard {
  animation: fadeIn 0.5s;
  padding-top: 4px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.chart-row {
  margin-bottom: 0;
}

.chart-row .el-col {
  margin-bottom: 20px;
}

.chart-row:last-child .el-col:last-child {
  margin-bottom: 0;
}

</style>
