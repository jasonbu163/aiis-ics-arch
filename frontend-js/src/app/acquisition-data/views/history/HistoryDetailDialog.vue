<!-- 文件路径: /frontend-js/src/app/acquisition-data/views/history/HistoryDetailDialog.vue
     功能描述: 展示当前历史样本的完整只读点值与采集时间。 -->
<template>
  <el-dialog :model-value="visible" :title="$t('acquisition-data.detail')" width="min(1100px, 95vw)"
    class="standard-form-dialog" destroy-on-close @update:model-value="$emit('update:visible', $event)">
    <div v-if="state === 'loading'" class="message" role="status">{{ $t('acquisition-data.loading') }}</div>
    <div v-else-if="state === 'unavailable'" class="message" role="alert">{{ $t('acquisition-data.unavailable') }}</div>
    <div v-else-if="state === 'error' || state === 'forbidden'" class="message" role="alert">
      {{ $t(`acquisition-data.${state}`) }}
      <ActionButton size="small" @click="$emit('retry')">{{ $t('acquisition-data.retry') }}</ActionButton>
    </div>
    <template v-else-if="detail">
      <div class="detail-heading">
        <div><strong>{{ $t('acquisition-data.plc') }}:</strong> {{ detail.plcId }}</div>
        <div><strong>{{ $t('acquisition-data.db') }}:</strong> DB{{ detail.dbNumber }}</div>
        <div><strong>{{ $t('acquisition-data.columns.sourceType') }}:</strong> {{ $t(`acquisition-data.source.${sourceKey(detail.sourceType)}`) }}</div>
        <div><strong>{{ $t('acquisition-data.columns.instanceId') }}:</strong> {{ detail.instanceId }}</div>
        <div><strong>{{ $t('acquisition-data.columns.sampleId') }}:</strong> {{ detail.sampleId }}</div>
        <div><strong>{{ $t('acquisition-data.columns.groupId') }}:</strong> {{ detail.groupId ?? '—' }}</div>
        <div><strong>{{ $t('acquisition-data.columns.configRevision') }}:</strong> {{ detail.configRevision ?? '—' }}</div>
        <div><strong>{{ $t('acquisition-data.columns.sampledAt') }}:</strong> <span :title="detail.sampledAt || ''">{{ formatShanghaiDateTime(detail.sampledAt) || $t('acquisition-data.missingTime') }}</span></div>
        <ActionButton size="small" @click="columns.reset">{{ $t('acquisition-data.resetWidths') }}</ActionButton>
      </div>
      <div class="table-scroll">
        <el-table :key="columns.version.value" :data="detail.points" border stripe class="vibe-table" @header-dragend="columns.onHeaderDragEnd">
          <el-table-column prop="name" :label="$t('acquisition-data.columns.pointName')" :width="columns.widths.name" :min-width="120">
            <template #default="{ row }">{{ row.name || row.pointId }}</template>
          </el-table-column>
          <el-table-column prop="pointId" :label="$t('acquisition-data.columns.pointId')" :width="columns.widths.pointId" :min-width="120" />
          <el-table-column prop="dataType" :label="$t('acquisition-data.columns.dataType')" :width="columns.widths.dataType" :min-width="90" />
          <el-table-column prop="value" :label="$t('acquisition-data.columns.value')" :width="columns.widths.value" :min-width="100">
            <template #default="{ row }">{{ rawValue(row.value) }}</template>
          </el-table-column>
          <el-table-column prop="quality" :label="$t('acquisition-data.columns.quality')" :width="columns.widths.quality" :min-width="100">
            <template #default="{ row }"><el-tag :type="qualityKey(row) === 'good' ? 'success' : 'danger'">{{ $t(`acquisition-data.quality.${qualityKey(row)}`) }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="reason" :label="$t('acquisition-data.columns.reason')" :width="columns.widths.reason" :min-width="100">
            <template #default="{ row }">{{ row.reason ?? '—' }}</template>
          </el-table-column>
          <el-table-column prop="observedAt" :label="$t('acquisition-data.columns.observedAt')" :width="columns.widths.observedAt" :min-width="170">
            <template #default="{ row }"><span :title="row.observedAt || ''">{{ formatShanghaiDateTime(row.observedAt) || $t('acquisition-data.missingTime') }}</span></template>
          </el-table-column>
        </el-table>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import ActionButton from '@/components/common/ActionButton.vue'
import { formatShanghaiDateTime } from '@/utils/date'
import { useTableColumnWidths } from '@/utils/tableColumnWidths'
import { rawValue, qualityKey, sourceKey } from '../../composables/useAcquisitionScope'
defineProps({ visible: Boolean, state: String, detail: Object })
defineEmits(['update:visible', 'retry'])
const columns = useTableColumnWidths('acquisition-data.history.detail', {
  name: { width: 190, minWidth: 120 }, pointId: { width: 190, minWidth: 120 },
  dataType: { width: 120, minWidth: 90 }, value: { width: 150, minWidth: 100 },
  quality: { width: 130, minWidth: 100 }, reason: { width: 150, minWidth: 100 },
  observedAt: { width: 200, minWidth: 170 }
})
</script>

<style scoped>
.detail-heading { display: flex; flex-wrap: wrap; gap: 12px 24px; align-items: center; margin-bottom: 16px; color: var(--text-primary); overflow-wrap: anywhere; }
.table-scroll { width: 100%; overflow-x: auto; }
.message { color: var(--text-secondary); display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
</style>
