<!-- 过程样本与独立能耗样本的管理员管理列表。 -->
<template><div class="page-layout"><BaseCard :title="t('monitor.observation.dataManagement')">
  <el-tabs v-model="active"><el-tab-pane :label="t('monitor.observation.processRecords')" name="process"><RecordList v-if="active === 'process'" target="history" /></el-tab-pane>
    <el-tab-pane :label="t('monitor.observation.energyRecords')" name="energy"><EnergyAdmin v-if="active === 'energy'" kind="samples" /></el-tab-pane></el-tabs>
</BaseCard></div></template>
<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import BaseCard from '@/components/common/BaseCard.vue'
import RecordList from '@/app/equipment/components/observations/RecordList.vue'
import EnergyAdmin from '../../components/observations/EnergyAdmin.vue'
const { t } = useI18n()
const active = ref('process')
</script>
