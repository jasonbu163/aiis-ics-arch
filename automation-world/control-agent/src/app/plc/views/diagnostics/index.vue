<!--
  File Path: /control-agent/src/app/plc/views/diagnostics/index.vue
  Description: PLC diagnostics view for the Control Agent console
  Main Features:
    - Displays PLC point-contract and endpoint state
    - Provides a targeted one-shot sample read without owning a polling loop
    - Receives all Tauri command actions from the composition root
-->
<template>
  <section id="plc" class="console-section">
    <ConsoleCard :icon="Cpu" title-key="plc.runtimeUnits">
      <PlcRuntimeUnitPicker
        :format-plc-endpoint="formatPlcEndpoint"
        :plc-collection-status-text="plcCollectionStatusText"
        :plc-runtime-status-text="plcRuntimeStatusText"
        :plc-sample-status-text="plcSampleStatusText"
        :selected-plc-key="selectedPlcKey"
        :status-tag-type="statusTagType"
        :units="runtimeSnapshot.plcCollectionStatus.plcUnits"
        @select="selectPlcKey"
      />
    </ConsoleCard>

    <el-row :gutter="16">
      <el-col :lg="10" :md="24">
        <ConsoleCard :icon="Cpu" title-key="plc.sectionTitle">
          <template #actions>
            <div class="console-action-group">
              <ConsoleActionButton
                :disabled="plcReadStartDisabled"
                :icon="Refresh"
                label-key="plc.controls.readOnce"
                :loading="plcReadBusy"
                :title="plcReadDisabledReason"
                tone="success"
                @click="readPlcSampleOnce"
              />
            </div>
          </template>

          <ConsoleInfoGrid>
            <el-descriptions-item :label="t('plc.status')">
              {{ plcContractStatusText }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('plc.path')">
              {{ runtimeSnapshot.plcPointContract.configuredPath }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('plc.selectedPlc')">
              {{ selectedPlcTargetLabel }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('plc.endpoint')">
              {{ plcEndpointText }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('plc.endpointProbe')">
              {{ plcEndpointProbeText }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('plc.sampleRead')">
              {{ plcSampleReadText }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('plc.runtimeUnit')">
              {{ selectedPlcRuntimeStatusText }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('plc.collectionUnit')">
              {{ selectedPlcCollectionStatusText }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('plc.driver')">
              {{ runtimeSnapshot.plcSampleRead.driver }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('plc.plcCount')">
              {{ runtimeSnapshot.plcPointContract.plcCount }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('plc.groupCount')">
              {{ runtimeSnapshot.plcPointContract.groupCount }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('plc.pointCount')">
              {{ selectedPlcPointSummaryText }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('plc.readableWritable')">
              {{ readableWritableText }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('plc.issues')">
              {{ pointContractIssuesText }}
            </el-descriptions-item>
          </ConsoleInfoGrid>
          <p v-if="selectedPlcKey === 'all'" class="diagnostic-message">
            {{ t('plc.selectOneForSample') }}
          </p>
          <div class="tag-row tag-row-spaced">
            <el-tag
              v-for="item in runtimeSnapshot.plcPointContract.typeCounts"
              :key="item.dataType"
              effect="plain"
            >
              {{ item.dataType }}: {{ item.count }}
            </el-tag>
          </div>
          <el-alert
            v-if="plcReadMessage"
            :closable="false"
            :description="plcReadMessage"
            :title="t('plc.controls.resultTitle')"
            :type="plcReadMessageType"
            class="collection-control-result"
            show-icon
          />
        </ConsoleCard>
      </el-col>

      <el-col :lg="14" :md="24">
        <ConsoleCard
          body-class="console-card__body--table"
          :icon="Grid"
          title-key="plc.sampleValues"
        >
          <div class="tag-row">
            <el-tag effect="plain">
              {{ t('plc.selectedPlc') }}: {{ selectedPlcTargetLabel }}
            </el-tag>
          </div>
          <ConsoleTableShell
            v-model:current-page="samplePageModel"
            v-model:page-size="samplePageSizeModel"
            :page-sizes="tablePageSizeOptions"
            :total="plcSampleValueCount"
          >
            <el-table
              :data="pagedPlcSamples"
              border
              class="agent-table agent-table--sample-values"
              empty-text="-"
              size="small"
              stripe
            >
              <el-table-column
                prop="name"
                :label="t('plc.pointName')"
                min-width="180"
                show-overflow-tooltip
              />
              <el-table-column prop="dataType" :label="t('plc.dataType')" width="110" />
              <el-table-column
                prop="value"
                :label="t('plc.value')"
                min-width="120"
                show-overflow-tooltip
              />
              <el-table-column :label="t('plc.dbOffset')" min-width="150">
                <template #default="{ row }">
                  DB{{ row.dbNumber }} / {{ row.offset }} / {{ row.bit }}
                </template>
              </el-table-column>
            </el-table>
          </ConsoleTableShell>
        </ConsoleCard>
      </el-col>
    </el-row>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Cpu, Grid, Refresh } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import ConsoleActionButton from '../../../../components/console/ConsoleActionButton.vue'
import ConsoleCard from '../../../../components/console/ConsoleCard.vue'
import ConsoleInfoGrid from '../../../../components/console/ConsoleInfoGrid.vue'
import PlcRuntimeUnitPicker from '../../../../components/console/PlcRuntimeUnitPicker.vue'
import ConsoleTableShell from '../../../../components/console/ConsoleTableShell.vue'
import type {
  PlcSampleValue,
  PlcRuntimeUnitSnapshot,
  RuntimeSnapshot
} from '../../../../services/runtimeSnapshot'

const props = defineProps<{
  formatPlcEndpoint: (unit: PlcRuntimeUnitSnapshot) => string
  pagedPlcSamples: PlcSampleValue[]
  plcContractStatusText: string
  plcEndpointProbeText: string
  plcEndpointText: string
  plcReadBusy: boolean
  plcReadDisabledReason: string
  plcReadMessage: string
  plcReadMessageType: 'success' | 'warning' | 'error' | 'info'
  plcReadStartDisabled: boolean
  plcSampleValueCount: number
  plcSampleReadText: string
  plcCollectionStatusText: (status: string) => string
  plcRuntimeStatusText: (status: string) => string
  plcSampleStatusText: (status: string) => string
  pointContractIssuesText: string
  readableWritableText: string
  runtimeSnapshot: RuntimeSnapshot
  selectedPlcCollectionStatusText: string
  selectedPlcKey: string
  selectedPlcPointSummaryText: string
  selectedPlcRuntimeStatusText: string
  selectedPlcTargetLabel: string
  samplePage: number
  samplePageSize: number
  readPlcSampleOnce: () => Promise<void>
  statusTagType: (status: string) => string
  tablePageSizeOptions: number[]
}>()

const emit = defineEmits<{
  'update:sample-page': [page: number]
  'update:sample-page-size': [pageSize: number]
  'update:selected-plc-key': [value: string]
}>()

const { t } = useI18n()

const samplePageModel = computed({
  get: () => props.samplePage,
  set: (page: number) => emit('update:sample-page', page)
})

const samplePageSizeModel = computed({
  get: () => props.samplePageSize,
  set: (pageSize: number) => emit('update:sample-page-size', pageSize)
})

function selectPlcKey(value: string) {
  emit('update:selected-plc-key', value)
}
</script>
