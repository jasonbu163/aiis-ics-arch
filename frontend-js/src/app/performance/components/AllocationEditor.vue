<!--
  文件路径: /frontend-next-js/src/app/performance/components/AllocationEditor.vue
  功能描述: 分/合卷卷重分配编辑器
  主要功能:
    - split 模式编辑多个目标卷及分配卷重
    - merge 模式编辑结果卷和来源分配卷重
    - 只做输入完整性展示，不推断业务关系
-->
<template>
  <BaseCard :title="$t('performance.splitWorkbench.allocation.title')" compact>
    <div class="allocation-editor">
      <template v-if="mode === 'split'">
        <div class="allocation-editor__toolbar">
          <span class="allocation-editor__summary">
            {{ $t('performance.splitWorkbench.allocation.totalAllocated') }}:
            {{ formatWeight(splitTotalAllocated) }}
          </span>
          <ActionButton variant="primary" size="small" @click="emit('addSplitTarget')">
            {{ $t('performance.splitWorkbench.actions.addTarget') }}
          </ActionButton>
        </div>

        <el-table
          :data="splitTargets"
          class="allocation-editor__table"
          border
          :empty-text="$t('performance.splitWorkbench.allocation.noTargets')"
        >
          <el-table-column :label="$t('performance.splitWorkbench.allocation.targetCoilNo')" min-width="170">
            <template #default="{ row }">
              <el-input
                :model-value="row.coilNo"
                :placeholder="$t('performance.splitWorkbench.allocation.targetCoilNoPlaceholder')"
                @update:model-value="updateSplitTarget(row.clientId, 'coilNo', $event)"
              />
            </template>
          </el-table-column>
          <el-table-column :label="$t('performance.splitWorkbench.allocation.allocatedWeight')" min-width="150">
            <template #default="{ row }">
              <el-input-number
                :model-value="row.allocatedWeight"
                :min="0"
                :precision="3"
                :step="1"
                controls-position="right"
                @update:model-value="updateSplitTarget(row.clientId, 'allocatedWeight', $event)"
              />
            </template>
          </el-table-column>
          <el-table-column :label="$t('performance.grade')" min-width="120">
            <template #default="{ row }">
              <el-input :model-value="row.grade" @update:model-value="updateSplitTarget(row.clientId, 'grade', $event)" />
            </template>
          </el-table-column>
          <el-table-column :label="$t('performance.spec')" min-width="140">
            <template #default="{ row }">
              <el-input :model-value="row.spec" @update:model-value="updateSplitTarget(row.clientId, 'spec', $event)" />
            </template>
          </el-table-column>
          <el-table-column :label="$t('performance.splitWorkbench.allocation.remark')" min-width="180">
            <template #default="{ row }">
              <el-input :model-value="row.remark" @update:model-value="updateSplitTarget(row.clientId, 'remark', $event)" />
            </template>
          </el-table-column>
          <el-table-column :label="$t('common.actions')" width="100" fixed="right">
            <template #default="{ row }">
              <ActionButton variant="danger" size="small" @click="emit('removeSplitTarget', row.clientId)">
                {{ $t('common.delete') }}
              </ActionButton>
            </template>
          </el-table-column>
        </el-table>
      </template>

      <template v-else>
        <el-form class="allocation-editor__form" label-position="top">
          <el-row :gutter="16">
            <el-col :xs="24" :md="8">
              <el-form-item :label="$t('performance.splitWorkbench.allocation.resultCoilNo')">
                <el-input
                  :model-value="mergeTarget.coilNo"
                  :placeholder="$t('performance.splitWorkbench.allocation.resultCoilNoPlaceholder')"
                  @update:model-value="updateMergeTarget('coilNo', $event)"
                />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="8">
              <el-form-item :label="$t('performance.grade')">
                <el-input :model-value="mergeTarget.grade" @update:model-value="updateMergeTarget('grade', $event)" />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="8">
              <el-form-item :label="$t('performance.spec')">
                <el-input :model-value="mergeTarget.spec" @update:model-value="updateMergeTarget('spec', $event)" />
              </el-form-item>
            </el-col>
            <el-col :xs="24">
              <el-form-item :label="$t('performance.splitWorkbench.allocation.remark')">
                <el-input
                  :model-value="mergeTarget.remark"
                  type="textarea"
                  :autosize="{ minRows: 2, maxRows: 4 }"
                  @update:model-value="updateMergeTarget('remark', $event)"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>

        <div class="allocation-editor__toolbar">
          <span class="allocation-editor__summary">
            {{ $t('performance.splitWorkbench.allocation.totalAllocated') }}:
            {{ formatWeight(mergeTotalAllocated) }}
          </span>
        </div>

        <el-table
          :data="mergeAllocations"
          class="allocation-editor__table"
          border
          :empty-text="$t('performance.splitWorkbench.allocation.noSources')"
        >
          <el-table-column :label="$t('performance.coilNo')" min-width="150">
            <template #default="{ row }">
              {{ getSource(row.performanceId)?.coilNo || row.performanceId }}
            </template>
          </el-table-column>
          <el-table-column :label="$t('performance.splitWorkbench.source.availableWeight')" min-width="140">
            <template #default="{ row }">
              {{ formatWeight(getSummary(row.performanceId)?.availableWeight) }}
            </template>
          </el-table-column>
          <el-table-column :label="$t('performance.splitWorkbench.allocation.allocatedWeight')" min-width="160">
            <template #default="{ row }">
              <el-input-number
                :model-value="row.allocatedWeight"
                :min="0"
                :precision="3"
                :step="1"
                controls-position="right"
                @update:model-value="updateMergeAllocation(row.performanceId, $event)"
              />
            </template>
          </el-table-column>
        </el-table>
      </template>
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
  splitTargets: {
    type: Array,
    default: () => []
  },
  mergeTarget: {
    type: Object,
    default: () => ({})
  },
  mergeAllocations: {
    type: Array,
    default: () => []
  },
  selectedSources: {
    type: Array,
    default: () => []
  },
  summaries: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits([
  'updateSplitTarget',
  'addSplitTarget',
  'removeSplitTarget',
  'updateMergeTarget',
  'updateMergeAllocation'
])
const { t } = useI18n()

const numberValue = (value) => {
  const numericValue = Number(value)
  return Number.isFinite(numericValue) ? numericValue : 0
}

const splitTotalAllocated = computed(() => props.splitTargets.reduce((total, item) => total + numberValue(item.allocatedWeight), 0))
const mergeTotalAllocated = computed(() => props.mergeAllocations.reduce((total, item) => total + numberValue(item.allocatedWeight), 0))

const formatWeight = (value) => {
  if (value === null || value === undefined || value === '') return t('performance.splitWorkbench.empty')
  const numericValue = Number(value)
  return Number.isFinite(numericValue) ? numericValue.toFixed(3) : String(value)
}

const updateSplitTarget = (clientId, field, value) => {
  emit('updateSplitTarget', { clientId, field, value })
}

const updateMergeTarget = (field, value) => {
  emit('updateMergeTarget', { field, value })
}

const updateMergeAllocation = (performanceId, allocatedWeight) => {
  emit('updateMergeAllocation', { performanceId, allocatedWeight })
}

const getSource = (performanceId) => props.selectedSources.find((item) => item.id === performanceId)
const getSummary = (performanceId) => props.summaries?.[performanceId] || {}
</script>

<style scoped>
.allocation-editor {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.allocation-editor__toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.allocation-editor__summary {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.4;
}

.allocation-editor__table {
  width: 100%;
}

.allocation-editor__form {
  width: 100%;
}

:deep(.el-input-number) {
  width: 100%;
}
</style>
