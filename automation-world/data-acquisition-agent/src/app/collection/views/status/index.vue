<!-- DAA本地SQLite视图：唯一local owner提供状态/动作，导航不驱动PLC或health。 -->
<template>
  <template v-if="local">

    <ConsoleCard title-key="common.local.collection" body-class="console-card__body--table">
      <template #tools><el-alert v-if="local.snapshot && !local.snapshot.capacity.admission" :title="t('common.local.capacityRisk')" :description="local.label(local.snapshot.capacity.state)" type="warning" :closable="false" show-icon /><p class="daa-capability-note">{{ t('common.local.runtimeActiveHint') }}</p>
        <div v-if="local.selectedTargets.length" class="console-action-group"><el-tag effect="plain">{{ t('common.local.selectedTargets', { count: local.selectedTargets.length }) }}</el-tag><ConsoleActionButton size="small" label-key="common.local.connectSelected" :disabled="local.busy || !local.view?.active" @click="confirmControl('daa_set_connection', true, local.selectedTargets)" /><ConsoleActionButton size="small" label-key="common.local.disconnectSelected" :disabled="local.busy || !local.view?.active" @click="confirmControl('daa_set_connection', false, local.selectedTargets)" /><ConsoleActionButton size="small" label-key="common.local.startSelected" :disabled="local.busy || !local.view?.active || !local.snapshot?.capacity.admission" @click="confirmControl('daa_set_collection', true, local.selectedTargets)" /><ConsoleActionButton size="small" label-key="common.local.pauseSelected" :disabled="local.busy || !local.view?.active" @click="confirmControl('daa_set_collection', false, local.selectedTargets)" /></div>
      </template>
      <ElCheckboxGroup v-model="local.selectedTargets">
        <ConsoleTableShell :current-page="1" :page-size="4" :total="local.plcs.length" :pagination="false">
          <el-table :data="local.plcs" row-key="id" :empty-text="local.draft ? t('common.local.emptyPlcs') : t('common.feedback.notLoaded')" :tooltip-options="{ appendTo: '#daa-feedback' }">
            <el-table-column width="48"><template #default="{ row }"><ElCheckbox :value="row.id" :aria-label="t('common.local.selectTarget')" /></template></el-table-column>
            <el-table-column prop="name" :label="t('common.local.plc')" min-width="165" />
            <el-table-column :label="t('common.local.state')" min-width="135"><template #default="{ row }"><el-tag v-if="local.snapshot" :type="local.state(row.id)?.error ? 'warning' : local.state(row.id)?.connected ? 'success' : 'info'" effect="plain">{{ local.label(local.state(row.id)?.phase ?? 'stopped') }}</el-tag><span v-else>—</span></template></el-table-column>
            <el-table-column :label="t('common.local.admission')" min-width="140"><template #default="{ row }">{{ local.label(local.state(row.id)?.admission) }}<small v-if="local.state(row.id)?.error" class="muted-cell">{{ local.label(local.state(row.id)?.error) }}</small></template></el-table-column>
            <el-table-column :label="t('common.local.savedCycles')" min-width="130"><template #default="{ row }">{{ local.state(row.id)?.savedCycles ?? '—' }}</template></el-table-column>
            <el-table-column :label="t('common.local.actions')" min-width="230"><template #default="{ row }"><div class="row-actions">
              <ConsoleActionButton v-if="!local.state(row.id)?.connected && !local.state(row.id)?.desiredConnection" size="small" label-key="common.local.connect" :disabled="local.busy || !local.view?.active" @click="local.control('daa_set_connection', [row.id], true)" />
              <ConsoleActionButton v-else size="small" label-key="common.local.disconnect" :disabled="local.busy || !local.view?.active" @click="local.control('daa_set_connection', [row.id], false)" />
              <ConsoleActionButton v-if="local.state(row.id)?.desiredCollection" size="small" label-key="common.local.pause" tone="warning" :disabled="local.busy" @click="local.control('daa_set_collection', [row.id], false)" />
              <ConsoleActionButton v-else size="small" label-key="common.local.start" tone="primary" :disabled="local.busy || !local.state(row.id)?.connected || !local.snapshot?.capacity.admission" @click="local.control('daa_set_collection', [row.id], true)" />
            </div></template></el-table-column>
          </el-table>
        </ConsoleTableShell>
      </ElCheckboxGroup>
      <details class="daa-details"><summary>{{ t('common.local.allControls') }}</summary><div class="console-action-group"><ConsoleActionButton label-key="common.local.connectAll" :disabled="local.busy || !local.view?.active" @click="confirmControl('daa_set_connection', true)" /><ConsoleActionButton label-key="common.local.disconnectAll" :disabled="local.busy || !local.view?.active" @click="confirmControl('daa_set_connection', false)" /><ConsoleActionButton label-key="common.local.startAll" :disabled="local.busy || !local.view?.active || !local.snapshot?.capacity.admission" @click="confirmControl('daa_set_collection', true)" /><ConsoleActionButton label-key="common.local.pauseAll" :disabled="local.busy || !local.view?.active" @click="confirmControl('daa_set_collection', false)" /></div></details>
      <details class="daa-details"><summary>{{ t('common.local.runtimeDetails') }}</summary><section v-for="p in local.plcs" :key="p.id" class="daa-local-edit-section"><h3>{{ p.name }}</h3><p>{{ t('common.local.intents', { connection: local.state(p.id) ? local.label(String(local.state(p.id)?.desiredConnection)) : '—', collection: local.state(p.id) ? local.label(String(local.state(p.id)?.desiredCollection)) : '—', actual: local.state(p.id) ? local.label(String(local.state(p.id)?.connected)) : '—' }) }}</p><p class="daa-capability-note">{{ t('common.local.used') }}: {{ local.state(p.id)?.usedRevision ?? '—' }}</p><p v-for="g in local.state(p.id)?.groups" :key="g.groupId">{{ local.draft?.groups.find(x => x.id === g.groupId)?.name ?? g.groupId }} · {{ g.intervalMs }} ms · {{ t('common.local.duration') }} {{ g.durationMs }} ms · {{ t('common.local.missed') }} {{ g.missedTicks }}</p></section></details>
      <details class="daa-details"><summary>{{ t('common.local.operations') }}</summary><div v-for="op in local.snapshot?.operations" :key="op.operationId"><p>{{ local.plcs.find(p => p.id === op.plcId)?.name }} · {{ local.label(op.action) }} · {{ local.label(op.phase) }} · {{ local.label(op.reason) }}</p><pre class="daa-local-raw">{{ op.operationId }}
{{ op.result }}</pre></div></details>
    </ConsoleCard>
    <details class="daa-details"><summary>{{ t('common.local.logs') }}</summary><LocalLogPanel /></details>
  </template>
</template>

<script setup lang="ts">
import { ElCheckbox, ElCheckboxGroup } from 'element-plus';

import { inject } from 'vue';
import LocalLogPanel from '../../../../components/console/LocalLogPanel.vue';
import { localConsoleKey } from '../../../../console/composables/useLocalAcquisitionConsole';
const local = inject(localConsoleKey);
import { computed } from 'vue';
import { Cpu } from '@element-plus/icons-vue';
import { useI18n } from 'vue-i18n';
import ConsoleActionButton from '../../../../components/console/ConsoleActionButton.vue';
import ConsoleCard from '../../../../components/console/ConsoleCard.vue';
import ConsoleTableShell from '../../../../components/console/ConsoleTableShell.vue';
const { t } = useI18n();
async function confirmControl(command: 'daa_set_connection' | 'daa_set_collection', desired: boolean, targets?: string[]) {
    const ids = (targets ?? local?.plcs.map(p => p.id) ?? []).slice();
    if (await local?.confirmAction('common.local.controlTargetsConfirm', { count: ids.length })) await local?.control(command, ids, desired);
}

</script>
