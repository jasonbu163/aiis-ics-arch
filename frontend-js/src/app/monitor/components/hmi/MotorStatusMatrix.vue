<!--
  文件路径: /frontend-next-js/src/app/monitor/components/hmi/MotorStatusMatrix.vue
  功能描述: HMI 电机状态矩阵组件
  主要功能:
    - 按设备分组复刻电机状态信息表格
    - 显示转速、电流、转矩和状态点位
    - 对当前未映射点位使用空值占位，便于后续补齐 PLC 映射
-->
<template>
  <section class="motor-status-matrix">
    <div v-for="(row, rowIndex) in groups" :key="rowIndex" class="motor-row">
      <article v-for="device in row" :key="device" class="motor-card">
        <header class="motor-card__title">{{ $t(`monitor.realtime.hmi.motor.devices.${device}`) }}</header>
        <div class="motor-card__body">
          <HmiValueCell
            :label="$t('monitor.realtime.hmi.motor.rows.rpm')"
            :value="readPoint(payload, pointKeys(device).rpmKey)"
            unit="rpm"
            :decimals="0"
            compact
          />
          <HmiValueCell
            :label="$t('monitor.realtime.hmi.motor.rows.current')"
            :value="readPoint(payload, pointKeys(device).currentKey)"
            unit="%"
            :decimals="1"
            compact
          />
          <HmiValueCell
            :label="$t('monitor.realtime.hmi.motor.rows.torque')"
            :value="readPoint(payload, pointKeys(device).torqueKey)"
            unit="%"
            :decimals="1"
            compact
          />
          <HmiStateCell
            :label="$t('monitor.realtime.hmi.motor.rows.status')"
            :value="readPoint(payload, pointKeys(device).stateKey)"
          />
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import HmiStateCell from './HmiStateCell.vue'
import HmiValueCell from './HmiValueCell.vue'
import { readPoint } from './hmiUtils'

const props = defineProps({
  payload: {
    type: Object,
    default: () => ({})
  },
  groups: {
    type: Array,
    default: () => []
  },
  fallbackKeys: {
    type: Object,
    default: () => ({})
  }
})

const pointKeys = (device) => props.fallbackKeys[device] || {}
</script>

<style scoped>
.motor-status-matrix {
  display: grid;
  gap: 18px;
}

.motor-row {
  display: grid;
  grid-template-columns: repeat(7, minmax(124px, 1fr));
  gap: 10px;
}

.motor-card {
  min-width: 0;
  overflow: hidden;
  border: 1px solid var(--border-secondary);
  border-radius: 8px;
  background: var(--bg-panel);
}

.motor-card__title {
  min-height: 38px;
  padding: 9px 8px;
  border-bottom: 1px solid var(--border-secondary);
  color: var(--text-primary);
  font-weight: 650;
  text-align: center;
}

.motor-card__body {
  display: grid;
  gap: 8px;
  padding: 8px;
}

@media (max-width: 1440px) {
  .motor-row {
    grid-template-columns: repeat(4, minmax(124px, 1fr));
  }
}

@media (max-width: 900px) {
  .motor-row {
    grid-template-columns: repeat(2, minmax(124px, 1fr));
  }
}

@media (max-width: 560px) {
  .motor-row {
    grid-template-columns: 1fr;
  }
}
</style>
