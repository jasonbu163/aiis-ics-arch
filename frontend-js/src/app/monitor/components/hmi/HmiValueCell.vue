<!--
  文件路径: /frontend-next-js/src/app/monitor/components/hmi/HmiValueCell.vue
  功能描述: HMI 数值单元格组件
  主要功能:
    - 统一数值、单位和标签展示
    - 保持固定尺寸，避免实时刷新导致布局跳动
    - 支持紧凑型 HMI 网格复用
-->
<template>
  <div class="hmi-value-cell" :class="{ 'hmi-value-cell--compact': compact }">
    <span class="hmi-value-cell__label">{{ label }}</span>
    <strong class="hmi-value-cell__value">
      {{ formattedValue }}
      <small v-if="unit">{{ unit }}</small>
    </strong>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatPointValue } from './hmiUtils'

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String, Boolean],
    default: undefined
  },
  unit: {
    type: String,
    default: ''
  },
  decimals: {
    type: Number,
    default: 0
  },
  compact: {
    type: Boolean,
    default: false
  }
})

const formattedValue = computed(() => formatPointValue(props.value, props.decimals))
</script>

<style scoped>
.hmi-value-cell {
  display: grid;
  grid-template-rows: minmax(18px, auto) minmax(28px, auto);
  gap: 6px;
  min-width: 0;
  min-height: 72px;
  padding: 10px 12px;
  border: 1px solid var(--border-secondary);
  border-radius: 6px;
  background: var(--bg-panel);
}

.hmi-value-cell--compact {
  min-height: 58px;
  padding: 8px 10px;
}

.hmi-value-cell__label {
  overflow: hidden;
  color: var(--text-tertiary);
  font-size: 12px;
  line-height: 1.35;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.hmi-value-cell__value {
  display: flex;
  align-items: baseline;
  gap: 4px;
  min-width: 0;
  color: var(--primary);
  font-family: var(--font-mono, monospace);
  font-size: 20px;
  font-weight: 700;
  line-height: 1.2;
}

.hmi-value-cell--compact .hmi-value-cell__value {
  font-size: 17px;
}

.hmi-value-cell__value small {
  color: var(--text-tertiary);
  font-family: inherit;
  font-size: 11px;
  font-weight: 500;
}
</style>
