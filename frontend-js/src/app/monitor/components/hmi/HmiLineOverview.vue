<!--
  文件路径: /frontend-next-js/src/app/monitor/components/hmi/HmiLineOverview.vue
  功能描述: HMI 产线总览组件
  主要功能:
    - 展示采集状态、关键过程指标和当前配方
    - 消费 latest snapshot payload 中的实时点位
    - 作为 HMI 多画面入口的第一屏业务总览
-->
<template>
  <section class="hmi-overview">
    <div class="hmi-overview__collector">
      <header class="hmi-panel-header">
        <h3>{{ $t('monitor.realtime.hmi.overview.collector') }}</h3>
      </header>
      <div class="collector-grid">
        <HmiValueCell :label="$t('monitor.realtime.sourceMode')" :value="collector.mode" compact />
        <HmiValueCell :label="$t('monitor.realtime.sampleCount')" :value="collector.sampleCount" compact />
        <HmiValueCell :label="$t('monitor.realtime.rawPointCount')" :value="latest.rawPointCount" compact />
        <HmiValueCell :label="$t('monitor.realtime.lastSampleAt')" :value="sampleTime" compact />
      </div>
    </div>

    <div class="hmi-overview__metrics">
      <header class="hmi-panel-header">
        <h3>{{ $t('monitor.realtime.hmi.overview.process') }}</h3>
      </header>
      <div class="metric-grid">
        <HmiValueCell
          v-for="metric in metrics"
          :key="metric.id"
          :label="$t(metric.labelKey)"
          :value="readPoint(payload, metric.key, metric.fallbackKey)"
          :unit="metric.unit"
          :decimals="metric.decimals"
        />
      </div>
    </div>

    <div class="hmi-overview__recipe">
      <header class="hmi-panel-header">
        <h3>{{ $t('monitor.realtime.hmi.overview.recipe') }}</h3>
      </header>
      <div class="recipe-grid">
        <HmiValueCell :label="$t('monitor.realtime.coilNumber')" :value="recipe.coilNumber" compact />
        <HmiValueCell :label="$t('monitor.realtime.coilType')" :value="recipe.coilType" compact />
        <HmiValueCell :label="$t('monitor.realtime.width')" :value="recipe.width" unit="mm" :decimals="1" compact />
        <HmiValueCell :label="$t('monitor.realtime.thickness')" :value="recipe.thickness" unit="mm" :decimals="2" compact />
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import HmiValueCell from './HmiValueCell.vue'
import { readPoint } from './hmiUtils'

const props = defineProps({
  payload: {
    type: Object,
    default: () => ({})
  },
  collector: {
    type: Object,
    default: () => ({})
  },
  latest: {
    type: Object,
    default: () => ({})
  },
  metrics: {
    type: Array,
    default: () => []
  },
  recipe: {
    type: Object,
    default: () => ({})
  }
})

const sampleTime = computed(() => props.collector.lastSampleAt || props.latest.updatedAt)
</script>

<style scoped>
.hmi-overview {
  display: grid;
  grid-template-columns: minmax(280px, 0.75fr) minmax(0, 1.25fr);
  gap: 16px;
}

.hmi-overview__collector,
.hmi-overview__metrics,
.hmi-overview__recipe {
  display: grid;
  gap: 12px;
  min-width: 0;
}

.hmi-overview__metrics {
  grid-column: 1 / -1;
}

.hmi-panel-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 15px;
  font-weight: 650;
}

.collector-grid,
.metric-grid,
.recipe-grid {
  display: grid;
  gap: 10px;
}

.collector-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.metric-grid {
  grid-template-columns: repeat(6, minmax(0, 1fr));
}

.recipe-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

@media (max-width: 1280px) {
  .hmi-overview {
    grid-template-columns: 1fr;
  }

  .metric-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .collector-grid,
  .metric-grid,
  .recipe-grid {
    grid-template-columns: 1fr;
  }
}
</style>
