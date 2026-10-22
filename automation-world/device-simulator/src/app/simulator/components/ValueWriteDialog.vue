<!-- 一次性typed写入，显式显示旧/新及CAS；未知回执不自动重试或改配置初值。 -->
<template>
  <el-dialog :model-value="!!point" :title="t(maintenance?'simulator.maintenanceWrite':'simulator.writeValue')" :append-to-body="false" width="min(680px, calc(100vw - 32px))" @close="emit('cancel')">
    <div v-if="point" class="console-stack" data-testid="value-write-dialog">
      <p>{{ point.name }} · {{ point.dataType }}</p>
      <p>{{ t('simulator.oldValue') }}: {{ point.value }}</p>
      <p>{{ t('simulator.epoch') }} {{ local.runtime?.epoch }} · {{ t('simulator.pointSeq') }} {{ point.pointSeq }}</p>
      <el-input v-model="text" data-testid="value-input" />
      <el-alert v-if="maintenance" :title="t('simulator.maintenanceHint')" type="warning" :closable="false" />
      <el-checkbox v-model="confirmed" data-testid="value-ack">{{ t('simulator.writeAcknowledge') }}</el-checkbox>
      <el-alert v-if="unknown" :title="t('simulator.unknownReceipt')" type="warning" :closable="false" />
    </div>
    <template #footer>
      <ConsoleActionButton label-key="simulator.cancel" data-testid="value-cancel" @click="emit('cancel')" />
      <ConsoleActionButton label-key="simulator.confirmWrite" tone="primary" data-testid="value-confirm" :disabled="local.busy||!confirmed||unknown" @click="write" />
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { inject, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { simulatorKey } from '../../../console/composables/useDeviceSimulator';
import { writePoint, type RuntimePoint, type Json } from '../../../services/deviceSimulator';
import ConsoleActionButton from '../../../components/console/ConsoleActionButton.vue';
const props = defineProps<{
    point: RuntimePoint | null;
    maintenance: boolean;
}>(), emit = defineEmits<{
    cancel: [
    ];
    written: [
    ];
}>(), local = inject(simulatorKey)!, { t } = useI18n(), text = ref(''), confirmed = ref(false), unknown = ref(false);
watch(() => props.point, p => { text.value = String(p?.value ?? ''); confirmed.value = false; unknown.value = false; });
async function write() { const p = props.point, r = local.runtime; if (!p || !r)
    return; let value: Json = text.value; if (p.dataType === 'BOOL') {
    if (!['true', 'false', '0', '1'].includes(text.value)) {
        local.error = 'typed_value_invalid';
        return;
    }
    value = text.value === 'true' || text.value === '1';
}
else if (p.dataType !== 'CHAR' && !p.dataType.startsWith('STRING[')) {
    value = Number(text.value);
    if (!text.value.trim() || !Number.isFinite(value)) {
        local.error = 'typed_value_invalid';
        return;
    }
} const result = await local.action(() => writePoint({ instanceId: r.instanceId, pointId: p.pointId, expectedLoadedRevision: r.loadedRevision, epoch: r.epoch, pointSeq: p.pointSeq, value, source: props.maintenance ? 'maintenance' : 'ordinary', confirmed: true })); if (result !== undefined)
    emit('written');
else if (local.unknown)
    unknown.value = true; }
</script>
