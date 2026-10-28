<!-- DS真实工作台：空配置为empty，运行控制必须使用当前loaded版本和epoch。 -->
<template>
  <section class="console-stack" data-testid="page-overview">
    <MetricGrid accessibility-label-key="simulator.runtimeMetrics" featured-label-key="simulator.instances" :featured-value="String(local.snapshot?.instances.length||0)" :featured-detail="t('simulator.independentServer')" :items="metrics" />
    <ConsoleCard title-key="simulator.instances">
      <template #actions>
        <ConsoleActionButton label-key="simulator.createInstance" data-testid="overview-create" @click="emitCreate" />
      </template>
      <el-empty :image-size="64" v-if="!local.snapshot?.instances.length" :description="t('simulator.emptyInstances')" />
      <ConsoleDataTable table-id="workbench.instances" v-else :data="local.snapshot.instances" row-key="instanceId">
        <el-table-column column-key="name" min-width="180" prop="name" :label="t('simulator.name')" />
        <el-table-column column-key="endpoint" min-width="190" prop="endpoint" :label="t('simulator.endpoint')" />
        <el-table-column column-key="state" min-width="110" :label="t('simulator.state')">
          <template #default="{row}">
            <span data-testid="runtime-state" :data-state="row.state">{{ t('simulator.states.'+row.state) }}</span>
          </template>
        </el-table-column>
        <el-table-column column-key="connections" min-width="130" :label="t('simulator.connections')">
          <template #default="{row}">{{ row.c }} / {{ row.h }} / {{ row.closing }}</template>
        </el-table-column>
        <el-table-column column-key="epoch" min-width="90" align="right" prop="epoch" :label="t('simulator.epoch')" />
        <el-table-column column-key="revision" min-width="280" :label="t('simulator.versionDisplay.title')">
          <template #default="{row}">
            <RevisionStatus :saved="row.savedRevision" :selected="row.selectedRevision" :loaded="row.loadedRevision" />
          </template>
        </el-table-column>
        <el-table-column column-key="actions" width="500" :resizable="false" :show-overflow-tooltip="false" fixed="right" :label="t('simulator.action')">
          <template #default="{row}">
            <div class="ds-actions">
              <ConsoleActionButton v-for="command in ['start','pause','resume','stop','reset']" :key="command" :label-key="'simulator.'+command" size="small" :data-testid="'control-'+command" :disabled="local.busy||!row.loadedRevision||(command==='start'&&row.state!=='stopped')||(command==='pause'&&row.state!=='running')||(command==='resume'&&row.state!=='paused')||(command==='reset'&&row.state!=='stopped')" @click="control(row,command)" />
            </div>
          </template>
        </el-table-column>
      </ConsoleDataTable>
    </ConsoleCard>
    <ConsoleOperationDialog v-model="resetOpen" title-key="simulator.reset" message-key="simulator.resetHint" cancel-label-key="simulator.cancel" confirm-label-key="simulator.confirm" confirm-tone="danger" @confirm="reset" />
  </section>
</template>
<script setup lang="ts">
import ConsoleDataTable from '../../../../components/console/ConsoleDataTable.vue';
import { computed, inject, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { simulatorKey } from '../../../../console/composables/useDeviceSimulator';
import type { RuntimeInstance } from '../../../../services/deviceSimulator';
import MetricGrid from '../../../../components/common/MetricGrid.vue';
import ConsoleCard from '../../../../components/console/ConsoleCard.vue';
import ConsoleActionButton from '../../../../components/console/ConsoleActionButton.vue';
import ConsoleOperationDialog from '../../../../components/console/ConsoleOperationDialog.vue';
import RevisionStatus from '../../../../components/console/RevisionStatus.vue';
const local = inject(simulatorKey)!, { t } = useI18n(), resetOpen = ref(false), target = ref<RuntimeInstance | null>(null);
const metrics = computed(() => [{ key: 'running', labelKey: 'simulator.running', value: String(local.snapshot?.instances.filter(i => i.state === 'running').length || 0) }, { key: 'connections', labelKey: 'simulator.connections', value: String(local.snapshot?.instances.reduce((n, i) => n + i.tcp, 0) || 0) }, { key: 'pending', labelKey: 'simulator.queue', value: String(local.snapshot?.instances.reduce((n, i) => n + i.protocolWaiting + i.ruleWaiting + i.uiWaiting, 0) || 0) }]);
function emitCreate() { document.dispatchEvent(new CustomEvent('ds-navigate', { detail: 'instances' })); }
function control(row: RuntimeInstance, command: string) { if (command === 'reset') {
    target.value = row;
    resetOpen.value = true;
}
else
    void local.control(row, command); }
async function reset() { if (target.value) {
    await local.control(target.value, 'reset', true);
    if (!local.error)
        resetOpen.value = false;
} }
</script>
