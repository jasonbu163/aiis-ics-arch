<!-- 过程样本管理员管理列表。 -->
<template>
  <div class="page-layout observation-data-page">
    <BaseCard :title="t('monitor.observation.dataManagement')" compact>
      <el-radio-group model-value="process" class="card-action-segmented" :aria-label="t('monitor.observation.dataManagement')">
        <el-radio-button value="process">{{ t('monitor.observation.processRecords') }}</el-radio-button>
      </el-radio-group>
    </BaseCard>
    <RecordList target="history" />
  </div>
</template>
<script setup>
import { useI18n } from 'vue-i18n'
import BaseCard from '@/components/common/BaseCard.vue'
import RecordList from '@/app/equipment/components/observations/RecordList.vue'

const { t } = useI18n()
</script>
<style scoped>
.observation-data-page { display: flex; flex-direction: column; gap: var(--space-lg); min-width: 0; }
.observation-data-page > :deep(.base-card) { height: auto; min-width: 0; }
.observation-data-page :deep(.card-action-segmented.el-radio-group) { flex-wrap: wrap; height: auto; }
</style>
