<!-- 计划与实绩侧栏复用同一个管理员共享字段管理页面。 -->
<template>
  <div ref="pageRoot" :style="{ paddingTop: `${pagePadding}px` }">
    <BaseCard :title="t(`${module}.workflow.sharedFieldSettings`)" class="shared-field-page">
      <TaskFieldEditor :key="module" kind="shared" :module="module" :api="api" />
    </BaseCard>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import BaseCard from '@/components/common/BaseCard.vue'
import TaskFieldEditor from '../../components/TaskFieldEditor.vue'
import { useTaskPagePadding } from '../../components/useTaskPagePadding'
import { getConfig, saveConfig, deleteField } from '../../api'

const api = { getConfig, saveConfig, deleteField }

defineProps({ module: { type: String, required: true } })
const { t } = useI18n()
const { pageRoot, pagePadding } = useTaskPagePadding()
</script>

<style scoped>
.shared-field-page { min-width: 0; }
.shared-field-page :deep(.base-card__body) { min-width: 0; }
</style>
