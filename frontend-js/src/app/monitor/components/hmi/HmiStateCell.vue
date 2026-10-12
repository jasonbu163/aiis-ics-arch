<!--
  文件路径: /frontend-next-js/src/app/monitor/components/hmi/HmiStateCell.vue
  功能描述: HMI 状态单元格组件
  主要功能:
    - 统一 Bool/状态点位展示
    - 使用稳定尺寸显示运行、停止、异常、未知状态
    - 为电机矩阵和状态面板复用
-->
<template>
  <div class="hmi-state-cell" :class="stateClass">
    <span class="hmi-state-cell__label">{{ label }}</span>
    <strong class="hmi-state-cell__value">{{ stateText }}</strong>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { isActiveState } from './hmiUtils'

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: [Boolean, Number, String],
    default: undefined
  },
  activeType: {
    type: String,
    default: 'success',
    validator: (value) => ['success', 'danger', 'warning'].includes(value)
  }
})

const { t } = useI18n()

const hasValue = computed(() => props.value !== undefined && props.value !== null && props.value !== '')
const active = computed(() => isActiveState(props.value))

const stateText = computed(() => {
  if (!hasValue.value) return t('monitor.realtime.hmi.state.unknown')
  return active.value ? t('monitor.realtime.hmi.state.active') : t('monitor.realtime.hmi.state.inactive')
})

const stateClass = computed(() => {
  if (!hasValue.value) return 'hmi-state-cell--unknown'
  return active.value ? `hmi-state-cell--${props.activeType}` : 'hmi-state-cell--idle'
})
</script>

<style scoped>
.hmi-state-cell {
  display: grid;
  grid-template-rows: minmax(18px, auto) minmax(24px, auto);
  gap: 6px;
  min-height: 58px;
  padding: 8px 10px;
  border: 1px solid var(--border-secondary);
  border-radius: 6px;
  background: var(--bg-panel);
}

.hmi-state-cell__label {
  overflow: hidden;
  color: var(--text-tertiary);
  font-size: 12px;
  line-height: 1.35;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.hmi-state-cell__value {
  color: var(--text-secondary);
  font-size: 15px;
  font-weight: 700;
}

.hmi-state-cell--success .hmi-state-cell__value {
  color: var(--success);
}

.hmi-state-cell--danger .hmi-state-cell__value {
  color: var(--danger);
}

.hmi-state-cell--warning .hmi-state-cell__value {
  color: var(--warning);
}

.hmi-state-cell--unknown .hmi-state-cell__value {
  color: var(--text-tertiary);
}
</style>
