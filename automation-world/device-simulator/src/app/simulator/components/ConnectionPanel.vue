<!-- 真实连接阶段/占额/peer/时间/bytes；确认只关闭所选ID，不修改其它实例。 -->
<template>
  <ConsoleCard title-key="simulator.connections">
    <ConsoleDataTable table-id="runtime.connections" class="ds-technical-table" :data="local.runtime?.connections||[]" max-height="320">
      <el-table-column column-key="connection" min-width="150" prop="connection" :label="t('simulator.connectionId')" />
      <el-table-column column-key="peer" min-width="180" prop="peer" :label="t('simulator.peer')" />
      <el-table-column column-key="phase" min-width="130" :label="t('simulator.state')">
        <template #default="{row}">{{ t('simulator.states.'+row.phase) }}</template>
      </el-table-column>
      <el-table-column column-key="executing_pdu" min-width="130" align="right" prop="executing_pdu" :label="t('simulator.executing')" />
      <el-table-column column-key="waiting_pdu" min-width="130" align="right" prop="waiting_pdu" :label="t('simulator.waiting')" />
      <el-table-column column-key="accepted_ns" min-width="200" prop="accepted_ns" :label="t('simulator.acceptedNs')" />
      <el-table-column column-key="last_receive_complete_ns" min-width="220" prop="last_receive_complete_ns" :label="t('simulator.lastReceiveNs')" />
      <el-table-column column-key="last_send_complete_ns" min-width="220" prop="last_send_complete_ns" :label="t('simulator.lastSendNs')" />
      <el-table-column column-key="reason" min-width="140" prop="reason" :label="t('simulator.closeReason')" />
      <el-table-column column-key="bytes" min-width="140" align="right" prop="bytes" :label="t('simulator.bytes')" />
      <el-table-column column-key="actions" width="200" :resizable="false" :show-overflow-tooltip="false" fixed="right" :label="t('simulator.action')">
        <template #default="{row}">
          <ConsoleActionButton label-key="simulator.closeConnection" size="small" data-testid="connection-close" @click="closing=row" />
        </template>
      </el-table-column>
    </ConsoleDataTable>
    <el-dialog :model-value="!!closing" :title="t('simulator.closeConnection')" :append-to-body="false" width="min(540px, calc(100vw - 32px))" @close="closing=null">
      <p>{{ t('simulator.closeConnectionHint') }}</p>
      <p>{{ closing?.peer }} · {{ closing?.connection }}</p>
      <template #footer>
        <ConsoleActionButton label-key="simulator.cancel" @click="closing=null" />
        <ConsoleActionButton label-key="simulator.confirm" tone="warning" data-testid="connection-close-confirm" :disabled="local.busy" @click="close" />
      </template>
    </el-dialog>
  </ConsoleCard>
</template>
<script setup lang="ts">
import ConsoleDataTable from '../../../components/console/ConsoleDataTable.vue';
import { inject, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { simulatorKey } from '../../../console/composables/useDeviceSimulator';
import { closeConnection, type Connection } from '../../../services/deviceSimulator';
import ConsoleCard from '../../../components/console/ConsoleCard.vue';
import ConsoleActionButton from '../../../components/console/ConsoleActionButton.vue';
const local = inject(simulatorKey)!, { t } = useI18n(), closing = ref<Connection | null>(null);
async function close() { const r = local.runtime, c = closing.value; if (!r || !c)
    return; const result = await local.action(() => closeConnection({ instanceId: r.instanceId, connectionId: String(c.connection), expectedLoadedRevision: r.loadedRevision, epoch: r.epoch, confirmed: true })); if (result !== undefined)
    closing.value = null; }
</script>
