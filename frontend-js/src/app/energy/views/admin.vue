<!-- 能耗管理下的管理员表计指标配置与写入登记。 -->
<template>
  <div class="page-layout energy-configuration">
    <BaseCard :title="t('energy.configuration')" compact>
      <el-radio-group v-model="active" class="card-action-segmented" :aria-label="t('energy.configuration')">
        <el-radio-button value="metrics">{{ t('energy.observation.energyConfig') }}</el-radio-button>
        <el-radio-button value="sources">{{ t('energy.writeSources.title') }}</el-radio-button>
      </el-radio-group>
    </BaseCard>
    <EnergyAdmin v-if="active === 'metrics'" kind="config" />
    <EnergyWriteSources v-else />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import BaseCard from '@/components/common/BaseCard.vue'
import EnergyAdmin from '../components/EnergyAdmin.vue'
import EnergyWriteSources from '../components/EnergyWriteSources.vue'

const { t } = useI18n()
const active = ref('metrics')
</script>

<style scoped>
.energy-configuration { display: grid; align-content: start; gap: var(--space-lg); min-width: 0; }
.energy-configuration > :deep(.base-card) { height: auto; min-width: 0; }
.energy-configuration :deep(.base-card__header) { flex-wrap: wrap; padding-block: 10px; }
@media (max-width: 1279px) {
  :global(body:has(.energy-configuration)) { min-width: 0; }
}
</style>
