<!--
  File Path: /control-agent/src/app/collection/views/status/index.vue
  Description: PLC collection status view for the Control Agent console
  Main Features:
    - Displays collection metrics, gates, policy and latest groups
    - Shows per-PLC read and persistence controls backed by runtime state
    - Receives all runtime actions from the console composition root
-->
<template>
  <section id="collection" class="console-section">
    <MetricGrid
      accessibility-label-key="collection.ariaLabel"
      collection
      featured-label-key="collection.collector"
      :featured-value="runtimeSnapshot.plcCollectionStatus.gates.collectorKey"
      :featured-detail="collectionStatusText"
      :items="collectionMetricItems"
    />

    <ReadinessGrid
      accessibility-label-key="collection.gatesAriaLabel"
      :items="collectionGateItems"
    />

    <ConsoleCard
      body-class="console-card__body--table"
      :icon="Cpu"
      title-key="collection.plcUnits"
    >
      <ConsoleTableShell
        :current-page="1"
        :page-size="20"
        :pagination="false"
        :total="runtimeSnapshot.plcCollectionStatus.plcUnits.length"
      >
        <el-table
          v-if="runtimeSnapshot.plcCollectionStatus.plcUnits.length > 0"
          :data="runtimeSnapshot.plcCollectionStatus.plcUnits"
          border
          class="agent-table agent-table--plc-units"
          empty-text="-"
          row-key="plcKey"
          size="small"
          stripe
        >
          <el-table-column
            prop="plcKey"
            :label="t('collection.plcKey')"
            width="112"
            show-overflow-tooltip
          />
          <el-table-column :label="t('collection.endpoint')" min-width="210" show-overflow-tooltip>
            <template #default="{ row }">
              {{ formatPlcEndpoint(row) }}
            </template>
          </el-table-column>
          <el-table-column :label="t('collection.readState')" width="128">
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.readState)" effect="plain">
                {{ plcRuntimeStatusText(row.readState) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column :label="t('collection.persistenceState')" width="128">
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.persistenceState)" effect="plain">
                {{ plcCollectionStatusText(row.persistenceState) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column :label="t('collection.sampleState')" width="112">
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.sampleStatus)" effect="plain">
                {{ plcSampleStatusText(row.sampleStatus) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column :label="t('collection.groupPointCounts')" width="124">
            <template #default="{ row }">
              {{ row.groupCount }} / {{ row.pointCount }}
            </template>
          </el-table-column>
          <el-table-column :label="t('collection.lastSuccess')" width="170" show-overflow-tooltip>
            <template #default="{ row }">
              {{ formatOptional(row.lastSuccessAt) }}
            </template>
          </el-table-column>
          <el-table-column
            prop="failureCount"
            :label="t('collection.failureCount')"
            width="88"
          />
          <el-table-column
            prop="lastError"
            :label="t('collection.lastError')"
            min-width="220"
            show-overflow-tooltip
          />
          <el-table-column :label="t('collection.actions')" width="236" fixed="right" align="center">
            <template #default="{ row }">
              <div class="plc-unit-actions">
                <ConsoleActionButton
                  v-if="isPlcReadActive(row)"
                  :disabled="isPlcControlDisabled('stop_read', row)"
                  :icon="SwitchButton"
                  label-key="collection.controls.stopRead"
                  :loading="collectionControlBusy"
                  size="small"
                  :title="plcControlDisabledReason('stop_read', row)"
                  tone="warning"
                  @click="runPlcControl('stop_read', row.plcKey)"
                />
                <ConsoleActionButton
                  v-else
                  :disabled="isPlcControlDisabled('start_read', row)"
                  :icon="VideoPlay"
                  label-key="collection.controls.startRead"
                  :loading="collectionControlBusy"
                  size="small"
                  :title="plcControlDisabledReason('start_read', row)"
                  tone="success"
                  @click="runPlcControl('start_read', row.plcKey)"
                />
                <ConsoleActionButton
                  v-if="row.persistenceState === 'enabled'"
                  :disabled="isPlcControlDisabled('pause_persistence', row)"
                  :icon="SwitchButton"
                  label-key="collection.controls.pausePersistence"
                  :loading="collectionControlBusy"
                  size="small"
                  :title="plcControlDisabledReason('pause_persistence', row)"
                  tone="secondary"
                  @click="runPlcControl('pause_persistence', row.plcKey)"
                />
                <ConsoleActionButton
                  v-else
                  :disabled="isPlcControlDisabled('enable_persistence', row)"
                  :icon="VideoPlay"
                  label-key="collection.controls.enablePersistence"
                  :loading="collectionControlBusy"
                  size="small"
                  :title="plcControlDisabledReason('enable_persistence', row)"
                  tone="primary"
                  @click="runPlcControl('enable_persistence', row.plcKey)"
                />
              </div>
            </template>
          </el-table-column>
        </el-table>
        <p v-else class="diagnostic-message">{{ t('collection.noUnits') }}</p>
      </ConsoleTableShell>
    </ConsoleCard>

    <el-row :gutter="16">
      <el-col :lg="10" :md="24">
        <div class="console-column-stack">
          <ConsoleCard :icon="Operation" title-key="collection.sectionTitle">
            <template #actions>
              <div class="console-action-group">
                <ConsoleActionButton
                  :disabled="collectionStartDisabled"
                  :icon="VideoPlay"
                  label-key="collection.controls.start"
                  :loading="collectionControlBusy"
                  tone="success"
                  @click="confirmStartCollection"
                />
                <ConsoleActionButton
                  :disabled="collectionStopDisabled"
                  :icon="SwitchButton"
                  label-key="collection.controls.stop"
                  :loading="collectionControlBusy"
                  tone="warning"
                  @click="confirmStopCollection"
                />
              </div>
            </template>

            <ConsoleInfoGrid>
              <el-descriptions-item :label="t('collection.status')">
                {{ collectionStatusText }}
              </el-descriptions-item>
              <el-descriptions-item :label="t('collection.target')">
                {{ t('collection.targets.all') }}
              </el-descriptions-item>
              <el-descriptions-item :label="t('collection.worker')">
                {{ formatOptional(runtimeSnapshot.plcCollectionStatus.collectorState.workerId) }}
              </el-descriptions-item>
              <el-descriptions-item :label="t('collection.mode')">
                {{ formatOptional(runtimeSnapshot.plcCollectionStatus.collectorState.mode) }}
              </el-descriptions-item>
              <el-descriptions-item :label="t('collection.heartbeat')">
                {{ formatOptional(runtimeSnapshot.plcCollectionStatus.collectorState.lastHeartbeatAt) }}
              </el-descriptions-item>
              <el-descriptions-item :label="t('collection.lastSample')">
                {{ formatOptional(runtimeSnapshot.plcCollectionStatus.collectorState.lastSampleAt) }}
              </el-descriptions-item>
              <el-descriptions-item :label="t('collection.durations')">
                {{ collectionDurationsText }}
              </el-descriptions-item>
              <el-descriptions-item :label="t('collection.lastError')">
                {{ formatOptional(runtimeSnapshot.plcCollectionStatus.collectorState.lastError) }}
              </el-descriptions-item>
            </ConsoleInfoGrid>
            <el-alert
              v-if="collectionControlResult"
              :closable="false"
              :description="collectionControlResultDescription"
              :title="collectionControlResultTitle"
              :type="collectionControlResultType"
              class="collection-control-result"
              show-icon
            />
            <p class="diagnostic-message">{{ collectionMessageText }}</p>
          </ConsoleCard>

          <ConsoleCard :icon="Tickets" title-key="collection.snapshotPolicy.title">
            <ConsoleInfoGrid>
              <el-descriptions-item :label="t('collection.snapshotPolicy.status')">
                {{ snapshotPolicyStatusText }}
              </el-descriptions-item>
              <el-descriptions-item :label="t('collection.snapshotPolicy.path')">
                {{ runtimeSnapshot.plcCollectionStatus.snapshotPolicy.configuredPath }}
              </el-descriptions-item>
              <el-descriptions-item :label="t('collection.snapshotPolicy.latestMode')">
                {{ runtimeSnapshot.plcCollectionStatus.snapshotPolicy.latestMode }}
              </el-descriptions-item>
              <el-descriptions-item :label="t('collection.snapshotPolicy.retention')">
                {{ snapshotPolicyRetentionText }}
              </el-descriptions-item>
              <el-descriptions-item :label="t('collection.snapshotPolicy.selectedPoints')">
                {{ snapshotPolicyPointText }}
              </el-descriptions-item>
              <el-descriptions-item :label="t('collection.snapshotPolicy.validation')">
                {{ snapshotPolicyValidationText }}
              </el-descriptions-item>
            </ConsoleInfoGrid>
            <p class="diagnostic-message">{{ snapshotPolicyMessageText }}</p>
          </ConsoleCard>
        </div>
      </el-col>

      <el-col :lg="14" :md="24">
        <ConsoleCard
          body-class="console-card__body--table"
          :icon="Grid"
          title-key="collection.latestGroups"
        >
          <ConsoleTableShell
            v-model:current-page="collectionPageModel"
            v-model:page-size="collectionPageSizeModel"
            :page-sizes="tablePageSizeOptions"
            :total="runtimeSnapshot.plcCollectionStatus.latestGroups.length"
          >
            <el-table
              :data="pagedCollectionGroups"
              border
              class="agent-table agent-table--latest-groups"
              empty-text="-"
              :row-key="collectionGroupRowKey"
              size="small"
              stripe
            >
              <el-table-column
                :label="t('collection.group')"
                width="190"
                fixed="left"
                show-overflow-tooltip
              >
                <template #default="{ row }">
                  <strong>DB{{ row.dbNumber }}</strong>
                  <span class="muted-cell">{{ row.plcKey }} / {{ row.groupName }}</span>
                </template>
              </el-table-column>
              <el-table-column :label="t('collection.quality')" width="130">
                <template #default="{ row }">
                  <el-tag :type="statusTagType(row.quality)" effect="plain">
                    {{ row.quality }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column :label="t('collection.counts')" min-width="170">
                <template #default="{ row }">
                  {{ formatGroupCounts(row.decodedCount, row.unsupportedCount) }}
                </template>
              </el-table-column>
              <el-table-column :label="t('collection.rawSnapshot')" width="130">
                <template #default="{ row }">
                  {{ row.rawSnapshotId > 0 ? `#${row.rawSnapshotId}` : '-' }}
                </template>
              </el-table-column>
              <el-table-column :label="t('collection.timing')" min-width="220" show-overflow-tooltip>
                <template #default="{ row }">
                  {{ formatCollectionTiming(row.collectedAt, row.readDurationMs) }}
                </template>
              </el-table-column>
              <el-table-column
                prop="errorMessage"
                :label="t('collection.error')"
                min-width="180"
                show-overflow-tooltip
              />
            </el-table>
          </ConsoleTableShell>
        </ConsoleCard>
      </el-col>
    </el-row>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Cpu, Grid, Operation, SwitchButton, Tickets, VideoPlay } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import MetricGrid from '../../../../components/common/MetricGrid.vue'
import ConsoleActionButton from '../../../../components/console/ConsoleActionButton.vue'
import ConsoleCard from '../../../../components/console/ConsoleCard.vue'
import ConsoleInfoGrid from '../../../../components/console/ConsoleInfoGrid.vue'
import ConsoleTableShell from '../../../../components/console/ConsoleTableShell.vue'
import ReadinessGrid from '../../../../components/console/ReadinessGrid.vue'
import type { MetricItem, OperationItem } from '../../../../console/types'
import type {
  PlcCollectionControlResult,
  PlcLatestGroupSnapshot,
  PlcRuntimeUnitSnapshot,
  RuntimeSnapshot
} from '../../../../services/runtimeSnapshot'

const props = defineProps<{
  collectionControlBusy: boolean
  collectionControlResult: PlcCollectionControlResult | null
  collectionControlResultDescription: string
  collectionControlResultTitle: string
  collectionControlResultType: 'success' | 'warning' | 'error' | 'info'
  collectionDurationsText: string
  collectionGateItems: OperationItem[]
  collectionMessageText: string
  collectionMetricItems: MetricItem[]
  collectionPage: number
  collectionPageSize: number
  collectionStartDisabled: boolean
  collectionStatusText: string
  collectionStopDisabled: boolean
  confirmStartCollection: () => Promise<void>
  confirmStopCollection: () => Promise<void>
  formatCollectionTiming: (collectedAt: string, readDurationMs: number) => string
  formatGroupCounts: (decodedCount: number, unsupportedCount: number) => string
  formatOptional: (value: string) => string
  formatPlcEndpoint: (unit: PlcRuntimeUnitSnapshot) => string
  isPlcControlDisabled: (
    action: 'start_read' | 'stop_read' | 'enable_persistence' | 'pause_persistence',
    unit: PlcRuntimeUnitSnapshot
  ) => boolean
  plcControlDisabledReason: (
    action: 'start_read' | 'stop_read' | 'enable_persistence' | 'pause_persistence',
    unit: PlcRuntimeUnitSnapshot
  ) => string
  pagedCollectionGroups: PlcLatestGroupSnapshot[]
  plcCollectionStatusText: (status: string) => string
  plcRuntimeStatusText: (status: string) => string
  plcSampleStatusText: (status: string) => string
  runtimeSnapshot: RuntimeSnapshot
  runPlcControl: (
    action: 'start_read' | 'stop_read' | 'enable_persistence' | 'pause_persistence',
    target: string
  ) => Promise<PlcCollectionControlResult>
  snapshotPolicyMessageText: string
  snapshotPolicyPointText: string
  snapshotPolicyRetentionText: string
  snapshotPolicyStatusText: string
  snapshotPolicyValidationText: string
  statusTagType: (status: string) => string
  tablePageSizeOptions: number[]
}>()

const emit = defineEmits<{
  'update:collection-page': [page: number]
  'update:collection-page-size': [pageSize: number]
}>()

const { t } = useI18n()

const collectionPageModel = computed({
  get: () => props.collectionPage,
  set: (page: number) => emit('update:collection-page', page)
})

const collectionPageSizeModel = computed({
  get: () => props.collectionPageSize,
  set: (pageSize: number) => emit('update:collection-page-size', pageSize)
})

function isPlcReadActive(unit: PlcRuntimeUnitSnapshot) {
  return ['starting', 'running', 'stopping'].includes(unit.readState)
}

const collectionGroupRowKey = (row: PlcLatestGroupSnapshot) =>
  `${row.plcKey}:${row.dbNumber}:${row.groupName}`
</script>
