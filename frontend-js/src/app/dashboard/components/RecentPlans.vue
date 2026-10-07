<!--
  文件路径: /frontend-next-js/src/app/dashboard/components/RecentPlans.vue
  功能描述: Dashboard 近期计划列表组件
  主要功能:
    - 展示近期生产计划列表
    - 支持状态标签显示
    - 支持跳转到计划列表页面
-->
<template>
  <BaseCard class="chart-card" :title="$t('dashboard.recentPlans')">
    <template #actions>
      <el-button text type="primary" size="small" class="card-action-button" @click="$router.push('/plan/list')">
        {{ $t('dashboard.viewAll') }}
      </el-button>
    </template>
    <el-table :data="recentPlans" border size="small" max-height="260">
      <el-table-column prop="coilNo" :label="$t('plan.coilNo')" width="120" />
      <el-table-column prop="grade" :label="$t('plan.steelGrade')" width="80" />
      <el-table-column prop="weight" :label="$t('plan.weight')" width="100">
        <template #default="{ row }">{{ row.weight?.toFixed(3) }}</template>
      </el-table-column>
      <el-table-column prop="status" :label="$t('plan.status')">
        <template #default="{ row }">
          <PlanStatusTag :status="row.status" size="small" />
        </template>
      </el-table-column>
    </el-table>
  </BaseCard>
</template>

<script setup>
import PlanStatusTag from '@/app/plan/components/PlanStatusTag.vue'
import BaseCard from '@/components/common/BaseCard.vue'

defineProps({
  recentPlans: {
    type: Array,
    required: true,
    default: () => []
  }
})
</script>
