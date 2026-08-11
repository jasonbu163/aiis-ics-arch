<!--
  文件路径: /frontend-js/src/components/common/MetricCard.vue
  功能描述: 通用指标卡片组件
  主要功能:
    - 展示指标标题、图标、数值与单位
    - 支持设定值/实际值等明细行
    - 复用 BaseCard 保持全局卡片视觉一致
-->
<template>
  <BaseCard class="metric-card" :title="title" :compact="compact">
    <template v-if="$slots.icon" #icon>
      <span class="metric-card__icon">
        <slot name="icon" />
      </span>
    </template>

    <div class="metric-card__content" :class="`metric-card__content--${align}`">
      <div class="metric-card__main">
        <span class="metric-card__value" :style="valueStyle">{{ value }}</span>
        <span v-if="unit" class="metric-card__unit">{{ unit }}</span>
      </div>

      <div v-if="details.length" class="metric-card__details">
        <div v-for="detail in details" :key="detail.label" class="metric-card__detail-row">
          <span class="metric-card__detail-label">{{ detail.label }}</span>
          <span class="metric-card__detail-value" :style="detail.valueStyle">{{ detail.value }}</span>
        </div>
      </div>
    </div>
  </BaseCard>
</template>

<script setup>
import BaseCard from './BaseCard.vue'

defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  unit: {
    type: String,
    default: ''
  },
  details: {
    type: Array,
    default: () => []
  },
  valueStyle: {
    type: Object,
    default: () => ({})
  },
  align: {
    type: String,
    default: 'center',
    validator: value => ['start', 'center'].includes(value)
  },
  compact: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.metric-card {
  min-height: 178px;
}

.metric-card__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border: 1px solid var(--border-secondary);
  border-radius: 10px;
  color: var(--primary);
  background: var(--bg-secondary);
}

.metric-card__content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 84px;
}

.metric-card__content--center {
  align-items: center;
  text-align: center;
}

.metric-card__content--start {
  align-items: flex-start;
  text-align: left;
}

.metric-card__main {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
  min-width: 0;
}

.metric-card__value {
  color: var(--text-primary);
  font-size: 36px;
  font-weight: 650;
  line-height: 1;
  overflow-wrap: anywhere;
}

.metric-card__unit {
  color: var(--text-tertiary);
  font-size: 15px;
  font-weight: 510;
}

.metric-card__details {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
  margin-top: 18px;
}

.metric-card__detail-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.3;
}

.metric-card__detail-label {
  color: var(--text-tertiary);
}

.metric-card__detail-value {
  color: var(--text-secondary);
  font-weight: 590;
  text-align: right;
}

@media (max-width: 768px) {
  .metric-card {
    min-height: 150px;
  }

  .metric-card__value {
    font-size: 30px;
  }
}
</style>
