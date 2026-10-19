<!-- PLC配置：SQLite草稿与显式连接测试；迁入历史归配置栏详情，保存不连接。 -->
<template>
  <template v-if="local">
    <ConsoleCard title-key="common.local.plcConfiguration" body-class="console-card__body--table">
      <template #actions><ConsoleActionButton label-key="common.local.addPlc" tone="primary" :disabled="local.busy || !!plcEditor || local.plcs.length >= 4" @click="addLocalPlc" /></template>
      <template #tools><div class="console-stack"><p class="daa-capability-note">{{ t('common.local.workflowHint') }}</p><div class="console-action-group"><ConsoleActionButton label-key="common.local.configurePoints" :disabled="!local.plcs.length || !!plcEditor || local.busy" @click="emit('open-points')" /></div><p class="daa-capability-note">{{ t('common.local.plcLimits') }}</p></div></template>
      <ConsoleTableShell :current-page="1" :page-size="4" :total="local.plcs.length" :pagination="false">
        <el-table :data="local.plcs" row-key="id" :empty-text="t(local.draft ? 'common.local.emptyPlcs' : 'common.feedback.notLoaded')" :tooltip-options="{ appendTo: '#daa-feedback' }">
          <el-table-column prop="name" :label="t('common.local.name')" min-width="170" show-overflow-tooltip />
          <el-table-column :label="t('common.local.endpoint')" min-width="220"><template #default="{ row }"><span>{{ row.host || '—' }}:{{ row.port }}</span><small class="muted-cell">{{ t('common.local.rack') }} {{ row.rack }} · {{ t('common.local.slot') }} {{ row.slot }}</small></template></el-table-column>
          <el-table-column :label="t('common.local.enabled')" width="95"><template #default="{ row }"><el-tag :type="row.enabled ? 'success' : 'info'" effect="plain">{{ local.label(String(row.enabled)) }}</el-tag></template></el-table-column>
          <el-table-column :label="t('common.local.state')" min-width="130"><template #default="{ row }"><el-tag :type="local.state(row.id)?.connected ? 'success' : 'info'" effect="plain">{{ local.snapshot ? local.label(local.state(row.id)?.phase ?? 'stopped') : '—' }}</el-tag></template></el-table-column>
          <el-table-column :label="t('common.local.actions')" width="220"><template #default="{ row }"><div class="row-actions"><ConsoleActionButton size="small" label-key="common.local.edit" :disabled="local.busy || !!plcEditor" @click="editLocalPlc(row)" /><ConsoleActionButton size="small" label-key="common.local.testConnection" :disabled="local.busy || !local.view?.active" @click="local.control('daa_test_connection', [row.id])" /></div></template></el-table-column>
        </el-table>
      </ConsoleTableShell>
      <p class="daa-capability-note">{{ t('common.local.testActiveHint') }}</p>
      <Teleport to="#daa-feedback">
        <ElDialog :model-value="!!plcEditor" :title="t('common.local.editPlc') + ' · ' + (plcEditor?.name ?? '')" :append-to-body="false" :close-on-click-modal="false" :close-on-press-escape="!local.busy" :show-close="!local.busy" width="min(780px, calc(100vw - 32px))" @update:model-value="$event || cancelLocalEdit()">
          <div v-if="plcEditor" class="console-stack">
            <el-alert v-if="local.error" :title="local.label(local.error)" type="error" :closable="false" show-icon />
        <p class="daa-capability-note">{{ t('common.local.editHint') }}</p>
        <ElForm :disabled="local.busy" label-position="top" class="daa-local-form-grid" @submit.prevent>
          <ElFormItem :label="t('common.local.name')"><ElInput v-model="plcEditor.name" maxlength="100" /></ElFormItem>
          <ElFormItem :label="t('common.local.enabled')"><ElSwitch v-model="plcEditor.enabled" /></ElFormItem>
          <ElFormItem :label="t('common.local.host')"><ElInput v-model="plcEditor.host" /></ElFormItem>
          <ElFormItem :label="t('common.local.port')"><ElInputNumber v-model="plcEditor.port" :min="1" :max="65535" :precision="0" controls-position="right" /></ElFormItem>
          <ElFormItem :label="t('common.local.rack')"><ElInputNumber v-model="plcEditor.rack" :min="0" :max="7" :precision="0" controls-position="right" /></ElFormItem>
          <ElFormItem :label="t('common.local.slot')"><ElInputNumber v-model="plcEditor.slot" :min="0" :max="31" :precision="0" controls-position="right" /></ElFormItem>
        </ElForm>
        <div class="console-action-group"><ConsoleActionButton label-key="common.local.cancelEdit" :disabled="local.busy" @click="cancelLocalEdit" /><ConsoleActionButton label-key="common.local.save" :disabled="local.busy" tone="primary" @click="applyLocalEdit" /><ConsoleActionButton v-if="!addedPlcId" label-key="common.local.remove" :disabled="local.busy" tone="danger" @click="removeLocalPlc(plcEditor.id)" /></div>
        <details class="daa-details"><summary>{{ t('common.local.identityDetails') }}</summary><code>{{ plcEditor.id }}</code><p class="diagnostic-message">{{ t('common.local.plcTimeouts') }}</p></details>
          </div>
        </ElDialog>
      </Teleport>
      <details class="daa-details"><summary>{{ t('common.local.operations') }}</summary><div v-for="op in local.snapshot?.operations.filter(o => o.action === 'test')" :key="op.operationId"><p>{{ local.plcs.find(p => p.id === op.plcId)?.name }} · {{ local.label(op.phase) }} · {{ local.label(op.reason) }}</p><pre class="daa-local-raw">{{ op.result }}</pre></div></details>
    </ConsoleCard>
  </template>
</template>

<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue';
import { ElDialog, ElForm, ElFormItem, ElInput, ElInputNumber, ElSwitch } from 'element-plus';
import ConsoleTableShell from '../../../../components/console/ConsoleTableShell.vue';
import type { Plc } from '../../../../services/localAcquisition';

import { inject } from 'vue';
import { localConsoleKey } from '../../../../console/composables/useLocalAcquisitionConsole';
const local = inject(localConsoleKey);
import { Cpu } from '@element-plus/icons-vue';
import { useI18n } from 'vue-i18n';
import ConsoleCard from '../../../../components/console/ConsoleCard.vue';
import ConsoleActionButton from '../../../../components/console/ConsoleActionButton.vue';
const emit = defineEmits<{ 'open-points': [] }>();
const { t } = useI18n();
async function removeLocalPlc(id: string) { if (await local?.confirmAction('common.local.removeConfirm')) { local?.removePlc(id); plcEditor.value = null; addedPlcId.value = ''; } }

const plcEditor = ref<Plc | null>(null);
const addedPlcId = ref('');
function editLocalPlc(p: Plc) { if (local) local.selectedPlc = p.id; plcEditor.value = JSON.parse(JSON.stringify(p)); }
function addLocalPlc() {
    if (!local?.draft || local.plcs.length >= 4) return;
    const id = crypto.randomUUID(); addedPlcId.value = id;
    plcEditor.value = { id, name: t('common.local.newPlc'), enabled: false, host: '', port: 102, rack: 0, slot: 1, connectTimeoutMs: 1000, ioTimeoutMs: 500, deadlineMs: 5000 };
}
function cancelLocalEdit() { plcEditor.value = null; addedPlcId.value = ''; }
async function applyLocalEdit() {
    const owner = local, edit = plcEditor.value;
    if (!owner?.draft || !edit) return;
    const candidate = JSON.parse(JSON.stringify(owner.draft));
    const index = candidate.plcs.findIndex((p: Plc) => p.id === edit.id);
    if (index < 0) candidate.plcs.push(JSON.parse(JSON.stringify(edit)));
    else candidate.plcs[index] = JSON.parse(JSON.stringify(edit));
    if (await owner.saveCandidate(candidate)) { owner.selectedPlc = edit.id; plcEditor.value = null; addedPlcId.value = ''; }
}

watch(plcEditor, v => { if (local) local.editing = !!v; });
watch(() => local?.view, () => { plcEditor.value = null; addedPlcId.value = ''; });
onUnmounted(() => { if (local) local.editing = false; });
</script>
