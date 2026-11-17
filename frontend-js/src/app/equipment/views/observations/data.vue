<!-- 设备最新整包的管理员管理列表。 -->
<template><div class="page-layout"><BaseCard :title="t('equipment.observation.dataManagement')"><RecordList target="latest" /></BaseCard></div></template>
<script setup>
import { useI18n } from 'vue-i18n'
import BaseCard from '@/components/common/BaseCard.vue'
import RecordList from '../../components/observations/RecordList.vue'
const { t } = useI18n()
</script>
