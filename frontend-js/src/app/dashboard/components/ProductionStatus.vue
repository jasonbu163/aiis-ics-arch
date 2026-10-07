<!--
  文件路径: /frontend-next-js/src/app/dashboard/components/ProductionStatus.vue
  功能描述: Dashboard 生产状态展示组件
  主要功能:
    - 展示在线卷号、待执行卷号、当前速度、炉区温度等生产状态
    - 支持日夜模式适配
-->
<template>
  <BaseCard class="chart-card" :title="$t('dashboard.productionStatus.title')">
    <div class="production-status">
      <div class="status-item">
        <div class="status-icon-wrapper active">
          <el-icon :size="28"><VideoPlay /></el-icon>
        </div>
        <div class="status-content">
          <div class="status-label">{{ $t('dashboard.productionStatus.onlineCoil') }}</div>
          <div class="status-value">{{ productionStatus.onlineCoil?.id || '-' }}</div>
          <el-tag type="success" size="small">{{ $t('dashboard.productionStatus.producing') }}</el-tag>
        </div>
        <div class="status-progress">
          <el-progress type="circle" :percentage="productionStatus.onlineCoil?.progress || 0" :width="56" />
        </div>
      </div>
      <div class="status-item">
        <div class="status-icon-wrapper pending">
          <el-icon :size="28"><Clock /></el-icon>
        </div>
        <div class="status-content">
          <div class="status-label">{{ $t('dashboard.productionStatus.readyCoil') }}</div>
          <div class="status-value">{{ productionStatus.readyCoil?.id || '-' }}</div>
          <el-tag type="warning" size="small">{{ $t('dashboard.productionStatus.waiting') }}</el-tag>
        </div>
        <div class="status-info">
          <div class="info-item">
            <span class="label">{{ $t('plan.steelGrade') }}:</span>
            <span class="value">{{ productionStatus.readyCoil?.grade || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">{{ $t('plan.weight') }}:</span>
            <span class="value">{{ productionStatus.readyCoil?.weight || 0 }}{{ $t('common.unit.ton') }}</span>
          </div>
        </div>
      </div>
      <div class="status-item">
        <div class="status-icon-wrapper info">
          <el-icon :size="28"><Connection /></el-icon>
        </div>
        <div class="status-content">
          <div class="status-label">{{ $t('dashboard.productionStatus.currentSpeed') }}</div>
          <div class="status-value">{{ productionStatus.currentSpeed || 0 }} m/{{ $t('common.unit.min') }}</div>
          <el-progress :percentage="Math.min((productionStatus.currentSpeed || 0) / 20 * 100, 100)" :show-text="false" />
        </div>
      </div>
      <div class="status-item">
        <div class="status-icon-wrapper info">
          <el-icon :size="28"><Odometer /></el-icon>
        </div>
        <div class="status-content">
          <div class="status-label">{{ $t('dashboard.productionStatus.furnaceTemp') }}</div>
          <div class="status-value">{{ productionStatus.furnaceTemp || 0 }} ℃</div>
          <el-tag :type="productionStatus.furnaceTemp > 950 ? 'danger' : 'success'" size="small">
            {{ productionStatus.furnaceTemp > 950 ? $t('dashboard.productionStatus.high') : $t('dashboard.productionStatus.normal') }}
          </el-tag>
        </div>
      </div>
    </div>
  </BaseCard>
</template>

<script setup>
import BaseCard from '@/components/common/BaseCard.vue'

defineProps({
  productionStatus: {
    type: Object,
    required: true,
    default: () => ({
      onlineCoil: { id: '', progress: 0, status: '' },
      readyCoil: { id: '', grade: '', weight: 0 },
      currentSpeed: 0,
      furnaceTemp: 0
    })
  }
})
</script>

<style scoped>
.production-status { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }

.status-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-secondary);
  border-radius: 18px;
  transition: all 0.3s;
}

.status-item:hover { background: rgba(255, 255, 255, 0.05); border-color: var(--border-primary); transform: translateY(-2px); }

.status-icon-wrapper {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  flex-shrink: 0;
  color: var(--bg-primary);
}

.status-icon-wrapper.active { background: var(--success); }
.status-icon-wrapper.pending { background: var(--warning); }
.status-icon-wrapper.info { background: var(--primary); }

.status-content { flex: 1; }
.status-label { font-size: 12px; color: var(--text-secondary); margin-bottom: 4px; }
.status-value { font-size: 16px; font-weight: 590; color: var(--text-primary); margin-bottom: 6px; letter-spacing: -0.02em; }

.status-progress { flex-shrink: 0; }
.status-info { display: flex; flex-direction: column; gap: 4px; }
.info-item { font-size: 12px; }
.info-item .label { color: var(--text-secondary); }
.info-item .value { color: var(--text-primary); font-weight: 500; }

@media (max-width: 768px) {
  .production-status { grid-template-columns: 1fr; }
}

[data-theme="dark"] .status-item:hover { box-shadow: 0 24px 48px rgba(0, 0, 0, 0.28); }
</style>
