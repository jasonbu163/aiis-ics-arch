<!--
  文件路径: /frontend-next-js/src/app/performance/components/LineageAuditSummary.vue
  功能描述: B17 transform 与 lineage 审计摘要展示
  主要功能:
    - 展示最近提交的 transform 元数据
    - 展示 lineage entry 快照和当前 lineage summary
    - 呈现后端 errorCode 的本地化业务错误
-->
<template>
  <BaseCard :title="$t('performance.splitWorkbench.audit.title')" compact>
    <div class="lineage-audit-summary">
      <el-alert
        v-if="errorCode"
        class="lineage-audit-summary__alert"
        :title="formatError(errorCode)"
        type="error"
        :closable="false"
      />

      <el-descriptions
        v-if="transform"
        class="lineage-audit-summary__meta"
        :column="3"
        border
      >
        <el-descriptions-item :label="$t('performance.splitWorkbench.audit.transformId')">
          {{ transform.id }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('performance.splitWorkbench.audit.transformType')">
          {{ formatDict('transformTypes', transform.transformType) }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('performance.splitWorkbench.audit.status')">
          {{ formatDict('transformStatuses', transform.status) }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('performance.splitWorkbench.audit.reason')">
          {{ transform.requestedReason || $t('performance.splitWorkbench.empty') }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('performance.splitWorkbench.audit.confirmedAt')">
          {{ transform.confirmedAt || transform.createdAt || $t('performance.splitWorkbench.empty') }}
        </el-descriptions-item>
      </el-descriptions>

      <el-empty
        v-else
        class="lineage-audit-summary__empty"
        :description="$t('performance.splitWorkbench.audit.empty')"
      />

      <el-table
        v-if="transform"
        :data="transform.lineageEntries || []"
        class="lineage-audit-summary__table"
        border
        :empty-text="$t('performance.splitWorkbench.audit.noLineage')"
      >
        <el-table-column prop="performanceId" :label="$t('performance.splitWorkbench.audit.performanceId')" min-width="130" />
        <el-table-column :label="$t('performance.splitWorkbench.audit.role')" min-width="110">
          <template #default="{ row }">
            {{ formatDict('lineageRoles', row.role) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('performance.splitWorkbench.allocation.allocatedWeight')" min-width="140">
          <template #default="{ row }">
            {{ formatWeight(row.allocatedWeight) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('performance.splitWorkbench.source.effectiveWeight')" min-width="140">
          <template #default="{ row }">
            {{ formatWeight(row.effectiveWeightSnapshot) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('performance.splitWorkbench.source.availableWeight')" min-width="150">
          <template #default="{ row }">
            {{ formatWeight(row.availableWeightAfterSnapshot) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('performance.splitWorkbench.source.effectiveWeightSource')" min-width="180">
          <template #default="{ row }">
            {{ formatDict('effectiveWeightSources', row.effectiveWeightSourceSnapshot) }}
          </template>
        </el-table-column>
      </el-table>
    </div>
  </BaseCard>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import BaseCard from '@/components/common/BaseCard.vue'

defineProps({
  transform: {
    type: Object,
    default: null
  },
  errorCode: {
    type: String,
    default: ''
  }
})

const { t, te } = useI18n()

const formatWeight = (value) => {
  if (value === null || value === undefined || value === '') return t('performance.splitWorkbench.empty')
  const numericValue = Number(value)
  return Number.isFinite(numericValue) ? numericValue.toFixed(3) : String(value)
}

const formatDict = (dictName, value) => {
  if (!value) return t('performance.splitWorkbench.empty')
  const key = `performance.splitWorkbench.${dictName}.${value}`
  return te(key) ? t(key) : value
}

const formatError = (errorCode) => {
  const key = `performance.splitWorkbench.errors.${errorCode}`
  return te(key) ? t(key) : errorCode
}
</script>

<style scoped>
.lineage-audit-summary {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.lineage-audit-summary__alert,
.lineage-audit-summary__meta,
.lineage-audit-summary__table {
  width: 100%;
}

.lineage-audit-summary__empty {
  min-height: 180px;
}
</style>
