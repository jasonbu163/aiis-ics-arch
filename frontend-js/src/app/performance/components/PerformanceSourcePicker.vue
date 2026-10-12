<!--
  文件路径: /frontend-next-js/src/app/performance/components/PerformanceSourcePicker.vue
  功能描述: 分/合卷来源实绩选择器
  主要功能:
    - 按模式选择一个或多个来源实绩
    - 展示 B17 lineage summary 中的有效卷重和可用卷重
    - 不做自动来源选择或业务关系推断
-->
<template>
  <BaseCard :title="$t('performance.splitWorkbench.source.title')" compact>
    <template #actions>
      <ActionButton variant="refresh" size="small" :loading="loading" @click="emit('refresh')">
        {{ $t('common.refresh') }}
      </ActionButton>
    </template>

    <div class="source-picker">
      <el-alert
        class="source-picker__notice"
        :title="$t(`performance.splitWorkbench.source.${mode}Hint`)"
        type="info"
        :closable="false"
      />

      <el-select
        :model-value="selectValue"
        class="source-picker__select"
        :multiple="mode === 'merge'"
        filterable
        clearable
        :collapse-tags="mode === 'merge'"
        :max-collapse-tags="2"
        :placeholder="$t('performance.splitWorkbench.source.placeholder')"
        @update:model-value="handleSelectChange"
      >
        <el-option
          v-for="item in candidates"
          :key="item.id"
          :label="formatOptionLabel(item)"
          :value="item.id"
        />
      </el-select>

      <el-table
        v-loading="loading"
        :data="selectedRows"
        class="source-picker__table"
        border
        :empty-text="$t('performance.splitWorkbench.source.empty')"
      >
        <el-table-column prop="coilNo" :label="$t('performance.coilNo')" min-width="150" />
        <el-table-column prop="grade" :label="$t('performance.grade')" min-width="110" />
        <el-table-column prop="spec" :label="$t('performance.spec')" min-width="130" />
        <el-table-column :label="$t('performance.splitWorkbench.source.effectiveWeight')" min-width="140">
          <template #default="{ row }">
            {{ formatWeight(getSummary(row.id)?.effectiveWeight) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('performance.splitWorkbench.source.effectiveWeightSource')" min-width="170">
          <template #default="{ row }">
            {{ formatDict('effectiveWeightSources', getSummary(row.id)?.effectiveWeightSource) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('performance.splitWorkbench.source.availableWeight')" min-width="140">
          <template #default="{ row }">
            {{ formatWeight(getSummary(row.id)?.availableWeight) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('performance.splitWorkbench.source.recordSource')" min-width="150">
          <template #default="{ row }">
            {{ formatDict('recordSources', row.recordSource) }}
          </template>
        </el-table-column>
      </el-table>
    </div>
  </BaseCard>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import BaseCard from '@/components/common/BaseCard.vue'
import ActionButton from '@/components/common/ActionButton.vue'

const props = defineProps({
  mode: {
    type: String,
    required: true,
    validator: (value) => ['split', 'merge'].includes(value)
  },
  candidates: {
    type: Array,
    default: () => []
  },
  selectedIds: {
    type: Array,
    default: () => []
  },
  summaries: {
    type: Object,
    default: () => ({})
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:selectedIds', 'refresh'])
const { t, te } = useI18n()

const selectedRows = computed(() => props.selectedIds
  .map((id) => props.candidates.find((item) => item.id === id))
  .filter(Boolean))

const selectValue = computed(() => (props.mode === 'merge' ? props.selectedIds : props.selectedIds[0] ?? null))

const handleSelectChange = (value) => {
  const nextIds = Array.isArray(value) ? value : (value ? [value] : [])
  emit('update:selectedIds', props.mode === 'split' ? nextIds.slice(0, 1) : nextIds)
}

const getSummary = (id) => props.summaries?.[id] || {}

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

const formatOptionLabel = (item) => {
  const summary = getSummary(item.id)
  const availableWeight = summary.availableWeight ?? item.availableWeight ?? item.weight
  return `${item.coilNo || item.id} / ${item.grade || t('performance.splitWorkbench.empty')} / ${formatWeight(availableWeight)}`
}
</script>

<style scoped>
.source-picker {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.source-picker__notice {
  margin: 0;
}

.source-picker__select {
  width: min(100%, 560px);
}

.source-picker__table {
  width: 100%;
}
</style>
