<!-- 过程样本与独立能耗样本的管理员管理列表。 -->
<template>
  <div class="page-layout observation-data-page">
    <BaseCard :title="t('monitor.observation.dataManagement')" compact>
      <el-radio-group v-model="active" class="card-action-segmented" :aria-label="t('monitor.observation.dataManagement')">
        <el-radio-button value="process">{{ t('monitor.observation.processRecords') }}</el-radio-button>
        <el-radio-button value="energy">{{ t('monitor.observation.energyRecords') }}</el-radio-button>
      </el-radio-group>
    </BaseCard>
    <RecordList v-if="active === 'process'" target="history" />
    <EnergyAdmin v-else kind="samples" />
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import BaseCard from '@/components/common/BaseCard.vue'
import RecordList from '@/app/equipment/components/observations/RecordList.vue'
import EnergyAdmin from '../../components/observations/EnergyAdmin.vue'

const { t } = useI18n()
const active = ref('process')
</script>
<style scoped>
.observation-data-page { display: flex; flex-direction: column; gap: var(--space-lg); min-width: 0; }
.observation-data-page > :deep(.base-card) { height: auto; min-width: 0; }
.observation-data-page :deep(.card-action-segmented.el-radio-group) { flex-wrap: wrap; height: auto; }
</style>
