<!--
  文件路径: /frontend-next-js/src/app/monitor/components/hmi/CoilerTensionPanel.vue
  功能描述: HMI 收放卷与张力监控组件
  主要功能:
    - 展示开卷、炉内张力、收卷相关点位
    - 对直径、张力、速度、规格等字段进行分区显示
    - 复用统一点位读取和数值展示逻辑
-->
<template>
  <section class="coiler-tension-panel">
    <article v-for="panel in panels" :key="panel.id" class="coiler-panel">
      <header class="coiler-panel__header">{{ $t(panel.titleKey) }}</header>
      <div class="coiler-panel__body">
        <HmiValueCell
          v-for="field in panel.fields"
          :key="field.key"
          :label="$t(field.labelKey)"
          :value="readPoint(payload, field.key, field.fallbackKey)"
          :unit="field.unit"
          :decimals="field.decimals"
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
  panels: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
.coiler-tension-panel {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.coiler-panel {
  min-width: 0;
  overflow: hidden;
  border: 1px solid var(--border-secondary);
  border-radius: 8px;
  background: var(--bg-panel);
}

.coiler-panel__header {
  padding: 12px 14px;
  border-bottom: 1px solid var(--border-secondary);
  color: var(--text-primary);
  font-weight: 650;
}

.coiler-panel__body {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  padding: 12px;
}

@media (max-width: 1180px) {
  .coiler-tension-panel {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .coiler-panel__body {
    grid-template-columns: 1fr;
  }
}
</style>
