<!--
  文件路径: /frontend-next-js/src/app/dashboard/components/StatCards.vue
  功能描述: Dashboard 统计卡片组件
  主要功能:
    - 展示今日产量、待执行计划、已完成卷数、OEE 等核心指标
    - 支持日夜模式适配
    - 响应式布局
-->
<template>
  <el-row :gutter="20" class="stats-row">
    <el-col :xs="24" :sm="12" :md="6">
      <MetricCard
        :title="`${$t('dashboard.stats.todayProduction')}(${$t('common.unit.ton')})`"
        :value="stats.todayProduction"
      >
        <template #icon>
          <el-icon :size="32"><Box /></el-icon>
        </template>
      </MetricCard>
    </el-col>
    <el-col :xs="24" :sm="12" :md="6">
      <MetricCard :title="$t('dashboard.stats.pendingPlans')" :value="stats.pendingPlans">
        <template #icon>
          <el-icon :size="32"><Document /></el-icon>
        </template>
      </MetricCard>
    </el-col>
    <el-col :xs="24" :sm="12" :md="6">
      <MetricCard :title="$t('dashboard.stats.completedCoils')" :value="stats.completedCoils">
        <template #icon>
          <el-icon :size="32"><Checked /></el-icon>
        </template>
      </MetricCard>
    </el-col>
    <el-col :xs="24" :sm="12" :md="6">
      <MetricCard :title="$t('dashboard.stats.oee')" :value="stats.oee" unit="%">
        <template #icon>
          <el-icon :size="32"><Cpu /></el-icon>
        </template>
      </MetricCard>
    </el-col>
  </el-row>
</template>

<script setup>
import MetricCard from '@/components/common/MetricCard.vue'

defineProps({
  stats: {
    type: Object,
    required: true,
    default: () => ({
      todayProduction: 0,
      pendingPlans: 0,
      completedCoils: 0,
      oee: 0
    })
  }
})
</script>

<style scoped>
/* 间距由父组件 index.vue 统一控制，但内部 el-col 需要设置 margin-bottom 防止贴在一起 */
.stats-row { margin-bottom: 0; }
.stats-row .el-col { margin-bottom: 20px; }

/* 在大屏幕上，如果一行显示4个，最后一个不需要 margin-bottom */
@media (min-width: 992px) {
  .stats-row .el-col:nth-last-child(-n+4) { margin-bottom: 0; }
}

/* 在中等屏幕上，如果一行显示2个，最后两个不需要 margin-bottom */
@media (min-width: 768px) and (max-width: 991px) {
  .stats-row .el-col:nth-last-child(-n+2) { margin-bottom: 0; }
}
</style>
