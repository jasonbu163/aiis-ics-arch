<!--
  文件路径: /frontend-next-js/src/app/monitor/components/hmi/HeatingZoneGrid.vue
  功能描述: HMI 加热与液位矩阵组件
  主要功能:
    - 按 HMI 原画面展示烘干、清洗、碱洗单元
    - 显示实际温度、设定温度、输出和液位点位
    - 使用统一 HMI 数值单元格保持刷新稳定
-->
<template>
  <section class="heating-zone-grid">
    <article v-for="unit in units" :key="unit.id" class="heating-unit">
      <header class="heating-unit__header">{{ $t(unit.labelKey) }}</header>
      <div class="heating-unit__body">
        <HmiValueCell
          :label="$t('monitor.realtime.hmi.fields.actualTemp')"
          :value="readPoint(payload, unit.actualKey)"
          unit="℃"
          :decimals="0"
          compact
        />
        <HmiValueCell
          :label="$t('monitor.realtime.hmi.fields.setTemp')"
          :value="readPoint(payload, unit.setKey)"
          unit="℃"
          :decimals="0"
          compact
        />
        <HmiValueCell
          :label="$t('monitor.realtime.hmi.fields.output')"
          :value="readPoint(payload, unit.outputKey)"
          unit="%"
          :decimals="1"
          compact
        />
        <HmiValueCell
          v-if="unit.liquidKey"
          :label="$t('monitor.realtime.hmi.fields.liquid')"
          :value="readPoint(payload, unit.liquidKey)"
          unit="mm"
          :decimals="1"
          compact
        />
      </div>
    </article>
  </section>
</template>

<script setup>
import HmiValueCell from './HmiValueCell.vue'
import { readPoint } from './hmiUtils'

defineProps({
  payload: {
    type: Object,
    default: () => ({})
  },
  units: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
.heating-zone-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(124px, 1fr));
  gap: 10px;
}

.heating-unit {
  min-width: 0;
  overflow: hidden;
  border: 1px solid var(--border-secondary);
  border-radius: 8px;
  background: var(--bg-panel);
}

.heating-unit__header {
  min-height: 40px;
  padding: 10px;
  border-bottom: 1px solid var(--border-secondary);
  color: var(--text-primary);
  font-weight: 650;
  text-align: center;
}

.heating-unit__body {
  display: grid;
  gap: 8px;
  padding: 8px;
}

@media (max-width: 1440px) {
  .heating-zone-grid {
    grid-template-columns: repeat(4, minmax(124px, 1fr));
  }
}

@media (max-width: 900px) {
  .heating-zone-grid {
    grid-template-columns: repeat(2, minmax(124px, 1fr));
  }
}

@media (max-width: 560px) {
  .heating-zone-grid {
    grid-template-columns: 1fr;
  }
}
</style>
