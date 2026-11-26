<!-- 能耗配置管理上卡切换表计管理、表计指标配置、写入登记、曲线设置与单价项目配置。 -->
<template>
  <div class="page-layout energy-configuration">
    <BaseCard :title="t('energy.configuration')" compact>
      <el-radio-group v-model="active" class="card-action-segmented" :aria-label="t('energy.configuration')">
        <el-radio-button value="meters">{{ t('energy.meters.title') }}</el-radio-button>
        <el-radio-button value="metrics">{{ t('energy.observation.energyConfig') }}</el-radio-button>
        <el-radio-button value="sources">{{ t('energy.writeSources.title') }}</el-radio-button>
        <el-radio-button value="prices">{{ t('energy.pricing.items') }}</el-radio-button>
        <el-radio-button value="curves">{{ t('energy.curves.title') }}</el-radio-button>
      </el-radio-group>
    </BaseCard>
    <EnergyMeters v-if="active === 'meters'" />
    <EnergyAdmin v-else-if="active === 'metrics'" kind="config" />
    <EnergyWriteSources v-else-if="active === 'sources'" />
    <EnergyPriceItems v-else-if="active === 'prices'" />
    <EnergyCurveGroups v-else-if="active === 'curves'" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import BaseCard from '@/components/common/BaseCard.vue'
import EnergyMeters from '../components/EnergyMeters.vue'
import EnergyAdmin from '../components/EnergyAdmin.vue'
import EnergyPriceItems from '../components/EnergyPriceItems.vue'
import EnergyCurveGroups from '../components/EnergyCurveGroups.vue'
import EnergyWriteSources from '../components/EnergyWriteSources.vue'

const { t } = useI18n()
const active = ref('metrics')
</script>

<style scoped>
.energy-configuration {
  display: grid;
  align-content: start;
  gap: var(--space-lg);
  min-width: 0;
  container: energy-config / inline-size;
}
.energy-configuration > :deep(.base-card) { height: auto; min-width: 0; }
.energy-configuration :deep(.base-card__header) { flex-wrap: wrap; padding-block: 10px; }
.energy-configuration :deep(.card-action-segmented.el-radio-group) { flex-wrap: wrap; height: auto; }
@media (max-width: 1279px) {
  :global(body:has(.energy-configuration)) { min-width: 0; }
}
@media (max-width: 768px) {
  /* 展开侧栏时，为多行应用顶栏预留空间。 */
  @container energy-config (max-width: 300px) {
    .energy-configuration > :deep(.base-card:first-child) { margin-block-start: 56px; }
  }
  @container energy-config (max-width: 250px) {
    .energy-configuration > :deep(.base-card:first-child) { margin-block-start: 108px; }
  }
  @container energy-config (max-width: 200px) {
    .energy-configuration > :deep(.base-card:first-child) { margin-block-start: 160px; }
  }
}
</style>
