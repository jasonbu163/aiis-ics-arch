<!-- 同owner分页typed快照；普通/维护来源按钮按真实effective策略开放。 -->
<template>
  <section class="console-stack" data-testid="page-values">
    <ConsoleCard title-key="simulator.values">
      <div class="ds-inline">
        <el-select v-model="local.instanceId" data-testid="values-instance">
          <el-option v-for="i in local.draft?.instances" :key="i.id" :value="i.id" :label="i.name" />
        </el-select>
        <el-tag>{{ t(local.snapshot?.stale?'simulator.stale':'simulator.current') }}</el-tag>
        <span>{{ t('simulator.epoch') }} {{ values?.epoch||'—' }}</span>
        <span>{{ t('simulator.seq') }} {{ values?.seq||'—' }}</span>
        <span data-testid="values-loaded-revision">{{ t('simulator.versionDisplay.loaded',{version:revisionLabel(values?.loadedRevision,local.configuration?.revisions)}) }} <ConsoleFieldHelp :label="t('simulator.versionDisplay.title')" :text="t('simulator.savedSelectedLoaded')+'\n'+(values?.loadedRevision||'—')" /></span>
      </div>
      <ConsoleTableShell v-model:current-page="page" v-model:page-size="local.valueLimit" :page-sizes="[10,20,50]" :total="values?.total||0">
        <ConsoleDataTable table-id="runtime.values" class="ds-technical-table" :data="values?.rows||[]" row-key="pointId" data-testid="values-table">
          <el-table-column column-key="name" min-width="180" prop="name" :label="t('simulator.name')" />
          <el-table-column column-key="dbNumber" min-width="90" prop="dbNumber" :label="t('simulator.dbNumber')" />
          <el-table-column column-key="address" min-width="110" :label="t('simulator.address')">
            <template #default="{row}">{{ row.byte }}{{ row.bit===null?'':'.'+row.bit }}</template>
          </el-table-column>
          <el-table-column column-key="dataType" min-width="110" prop="dataType" :label="t('simulator.dataType')" />
          <el-table-column column-key="value" min-width="160" align="right" :label="t('simulator.value')">
            <template #default="{row}">
              <span :data-testid="'value-'+row.name">{{ row.value }}</span>
            </template>
          </el-table-column>
          <el-table-column column-key="pointSeq" min-width="130" align="right" prop="pointSeq" :label="t('simulator.pointSeq')" />
          <el-table-column column-key="source" min-width="150" :label="t('simulator.source')">
            <template #default="{row}">{{ t('simulator.sources.'+row.source) }}</template>
          </el-table-column>
          <el-table-column column-key="updatedAt" min-width="205" :label="t('simulator.pointUpdated')">
            <template #header><span>{{ t('simulator.pointUpdated') }} <ConsoleFieldHelp :label="t('simulator.pointUpdated')" :text="t('simulator.pointUpdatedHint')" /></span></template>
            <template #default="{row}">{{ formatShanghaiTime(row.updatedAt)||t('simulator.calendarTimeUnavailable') }}</template>
          </el-table-column>
          <el-table-column column-key="actions" width="340" :resizable="false" :show-overflow-tooltip="false" fixed="right" :label="t('simulator.action')">
            <template #header><span>{{ t('simulator.action') }} <ConsoleFieldHelp :label="t('simulator.action')" :text="t('simulator.writeKindsHint')" /></span></template>
            <template #default="{row}">
              <div class="ds-actions"><ConsoleActionButton label-key="simulator.writeValue" size="small" data-testid="value-write" :disabled="!canWrite(row,false)" @click="open(row,false)" />
              <ConsoleActionButton label-key="simulator.maintenanceWrite" size="small" data-testid="value-maintenance" :disabled="!canWrite(row,true)" @click="open(row,true)" /></div>
            </template>
          </el-table-column>
        </ConsoleDataTable>
      </ConsoleTableShell>
      <div class="ds-inline"><span>{{ t('simulator.policySourcesTitle') }}</span><ConsoleFieldHelp :label="t('simulator.policySourcesTitle')" :text="t('simulator.effectiveHint')" /></div>
      <el-descriptions v-for="row in values?.rows||[]" :key="row.pointId" :title="row.name" :column="2" size="small">
        <el-descriptions-item :label="t('simulator.owner')">{{ t('simulator.owners.'+row.effective.owner) }}</el-descriptions-item>
        <el-descriptions-item :label="t('simulator.mode')">{{ t('simulator.modes.'+row.effective.mode) }}</el-descriptions-item>
        <el-descriptions-item v-for="(origin,field) in row.effective.inheritedFrom" :key="field" :label="fieldLabel(String(field))">{{ originLabel(origin) }}</el-descriptions-item>
      </el-descriptions>
    </ConsoleCard>
    <ConnectionPanel />
    <ValueWriteDialog :point="writing" :maintenance="maintenance" @cancel="writing=null" @written="writing=null" />
  </section>
</template>
<script setup lang="ts">
import ConsoleDataTable from '../../../../components/console/ConsoleDataTable.vue';
import { computed, inject, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { simulatorKey } from '../../../../console/composables/useDeviceSimulator';
import type { RuntimePoint } from '../../../../services/deviceSimulator';
import { formatShanghaiTime } from '../../../../console/time';
import { revisionLabel } from '../../../../console/revisions';
import ConsoleFieldHelp from '../../../../components/console/ConsoleFieldHelp.vue';
import ConsoleCard from '../../../../components/console/ConsoleCard.vue';
import ConsoleActionButton from '../../../../components/console/ConsoleActionButton.vue';
import ConsoleTableShell from '../../../../components/console/ConsoleTableShell.vue';
import ConnectionPanel from '../../components/ConnectionPanel.vue';
import ValueWriteDialog from '../../components/ValueWriteDialog.vue';
const local = inject(simulatorKey)!, { t } = useI18n(), page = ref(1), writing = ref<RuntimePoint | null>(null), maintenance = ref(false), values = computed(() => local.snapshot?.values?.instanceId === local.instanceId ? local.snapshot.values : null);
watch([page, () => local.valueLimit], () => { local.valueOffset = (page.value - 1) * local.valueLimit; void local.refresh(); });
watch(() => local.instanceId, () => { page.value = 1; local.valueOffset = 0; void local.refresh(); });
function canWrite(row: RuntimePoint, maint: boolean) { const e = row.effective; return !local.busy && !local.snapshot?.stale && ['running', 'paused'].includes(local.runtime?.state || '') && e.mode === 'hold' && (maint ? !!e.uiMaintenance && ['client', 'none'].includes(e.owner || '') : e.owner === 'ui' && !!e.uiWrite); }
function fieldLabel(field: string) { const keys: Record<string, string> = { client_read: 'clientRead', client_write: 'clientWrite', ui_write: 'uiWrite', ui_maintenance: 'uiMaintenance', initial: 'initial', mode: 'mode', owner: 'owner', rule: 'ruleParameters' }; return t('simulator.' + (keys[field] || 'policy')); }
function originLabel(origin: string) { const [level, identity] = origin.split(':'); return t('simulator.levels.' + level) + (identity ? ' · ' + identity : ''); }
function open(row: RuntimePoint, maint: boolean) { writing.value = JSON.parse(JSON.stringify(row)); maintenance.value = maint; }
</script>

