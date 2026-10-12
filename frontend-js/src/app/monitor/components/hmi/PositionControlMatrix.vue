<!--
  文件路径: /frontend-next-js/src/app/monitor/components/hmi/PositionControlMatrix.vue
  功能描述: HMI 刷辊位置与产线状态组件
  主要功能:
    - 展示刷辊实际位置点位
    - 展示复位、使能、故障、运行等 Bool 状态点位
    - 为后续操作类写入点位预留只读展示结构
-->
<template>
  <section class="position-control-matrix">
    <article v-for="group in groups" :key="group.id" class="position-group">
      <header class="position-group__header">{{ $t(group.titleKey) }}</header>
      <div class="position-group__body">
        <component
          :is="item.type === 'state' ? HmiStateCell : HmiValueCell"
          v-for="item in group.items"
          :key="item.key"
          :label="$t(item.labelKey)"
          :value="readPoint(payload, item.key)"
          :unit="item.type === 'state' ? undefined : '%'"
          :decimals="item.type === 'state' ? undefined : 1"
        />
      </div>
    </article>
  </section>
</template>

<script setup>
import HmiStateCell from './HmiStateCell.vue'
import HmiValueCell from './HmiValueCell.vue'
import { readPoint } from './hmiUtils'

defineProps({
  payload: {
    type: Object,
    default: () => ({})
  },
  groups: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
.position-control-matrix {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(280px, 0.6fr);
  gap: 14px;
}

.position-group {
  min-width: 0;
  overflow: hidden;
  border: 1px solid var(--border-secondary);
  border-radius: 8px;
  background: var(--bg-panel);
}

.position-group__header {
  padding: 12px 14px;
  border-bottom: 1px solid var(--border-secondary);
  color: var(--text-primary);
  font-weight: 650;
}

.position-group__body {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  padding: 12px;
}

@media (max-width: 1080px) {
  .position-control-matrix {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .position-group__body {
    grid-template-columns: 1fr;
  }
}
</style>
