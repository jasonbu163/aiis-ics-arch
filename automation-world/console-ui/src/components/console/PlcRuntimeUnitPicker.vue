<!--
  File Path: /control-agent/src/components/console/PlcRuntimeUnitPicker.vue
  Description: PLC runtime-unit selector for Control Agent diagnostics views
  Main Features:
    - Lists all PLC units from the runtime snapshot
    - Shows endpoint and per-unit runtime context before a diagnostic read
    - Emits selection only; PLC commands remain owned by the composition root
-->
<template>
  <div class="plc-runtime-unit-picker">
    <p class="diagnostic-message plc-runtime-unit-picker__hint">
      {{ t('plc.unitPickerHint') }}
    </p>

    <ConsoleTableShell
      :current-page="1"
      :page-size="20"
      :pagination="false"
      :total="units.length"
    >
      <el-table
        v-if="units.length > 0"
        :current-row-key="selectedPlcKey"
        :data="units"
        border
        class="agent-table agent-table--plc-unit-picker"
        empty-text="-"
        highlight-current-row
        row-key="plcKey"
        size="small"
        stripe
        @row-click="selectUnit"
      >
        <el-table-column
          prop="plcKey"
          :label="t('collection.plcKey')"
          width="112"
          show-overflow-tooltip
        />
        <el-table-column :label="t('collection.endpoint')" min-width="220" show-overflow-tooltip>
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
        <el-table-column :label="t('collection.actions')" width="112" fixed="right" align="center">
          <template #default="{ row }">
            <ConsoleActionButton
              :disabled="row.plcKey === selectedPlcKey"
              :label-key="row.plcKey === selectedPlcKey ? 'plc.controls.selected' : 'plc.controls.select'"
              size="small"
              :tone="row.plcKey === selectedPlcKey ? 'secondary' : 'primary'"
              @click.stop="selectUnit(row)"
            />
          </template>
        </el-table-column>
      </el-table>
      <p v-else class="diagnostic-message">{{ t('collection.noUnits') }}</p>
    </ConsoleTableShell>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import ConsoleActionButton from './ConsoleActionButton.vue'
import ConsoleTableShell from './ConsoleTableShell.vue'
import type { PlcRuntimeUnitSnapshot } from '../../services/runtimeSnapshot'

defineProps<{
  formatPlcEndpoint: (unit: PlcRuntimeUnitSnapshot) => string
  plcCollectionStatusText: (status: string) => string
  plcRuntimeStatusText: (status: string) => string
  plcSampleStatusText: (status: string) => string
  selectedPlcKey: string
  statusTagType: (status: string) => string
  units: PlcRuntimeUnitSnapshot[]
}>()

const emit = defineEmits<{
  select: [plcKey: string]
}>()

const { t } = useI18n()

function selectUnit(unit: PlcRuntimeUnitSnapshot) {
  emit('select', unit.plcKey)
}
</script>
