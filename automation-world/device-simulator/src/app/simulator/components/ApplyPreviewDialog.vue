<!-- 停机apply明确列保值/初始化/删除；无隐式start，回旧版默认全初始化。 -->
<template>
  <el-dialog :model-value="!!preview" :title="t('simulator.applyPreview')" :append-to-body="false" width="min(980px, calc(100vw - 32px))" :close-on-click-modal="!busy" @close="emit('cancel')">
    <div v-if="preview" class="console-stack" data-testid="apply-preview">
      <el-alert :title="t(preview.details.initializeAll?'simulator.initializeAllHint':'simulator.preserveHint')" type="warning" :closable="false" />
      <el-checkbox :model-value="preview.details.initializeAll===true" :disabled="preview.details.rollback===true||busy" @update:model-value="emit('retention',$event?'initialize_all':'preserve_compatible_hold')">{{ t('simulator.initializeAll') }}</el-checkbox>
      <ConsoleDataTable table-id="preview.apply" :data="rows" max-height="380">
        <el-table-column column-key="point" min-width="220" :label="t('simulator.name')">
          <template #default="{row}">{{ pointName(row.pointId) }}</template>
        </el-table-column>
        <el-table-column column-key="result" min-width="160" :label="t('simulator.action')">
          <template #default="{row}">{{ t('simulator.actions.'+row.action) }}</template>
        </el-table-column>
        <el-table-column column-key="reason" min-width="280" :label="t('simulator.reason')">
          <template #default="{row}">{{ t('simulator.reasons.'+row.reason) }}</template>
        </el-table-column>
      </ConsoleDataTable>
      <el-checkbox v-model="acknowledged" data-testid="apply-ack">{{ t('simulator.applyAcknowledge') }}</el-checkbox>
    </div>
    <template #footer>
      <ConsoleActionButton label-key="simulator.cancel" data-testid="apply-cancel" :disabled="busy" @click="emit('cancel')" />
      <ConsoleActionButton label-key="simulator.confirmApply" tone="primary" data-testid="apply-confirm" :disabled="busy||!acknowledged" :loading="busy" @click="emit('confirm')" />
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import ConsoleDataTable from '../../../components/console/ConsoleDataTable.vue';
import { computed, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import type { Preview, Json } from '../../../services/deviceSimulator';
import ConsoleActionButton from '../../../components/console/ConsoleActionButton.vue';
const props = defineProps<{
    preview: Preview | null;
    busy: boolean;
}>(), emit = defineEmits<{
    cancel: [
    ];
    confirm: [
    ];
    retention: [
        mode: string
    ];
}>(), { t } = useI18n(), acknowledged = ref(false);
watch(() => props.preview, () => acknowledged.value = false);
const rows = computed(() => Array.isArray(props.preview?.details.rows) ? props.preview!.details.rows as Record<string, Json>[] : []);
function pointName(id: Json | undefined) { return props.preview?.workspace.instances.flatMap(i => i.dbs).flatMap(d => d.points).find(p => p.id === id)?.name || String(id ?? '—'); }
</script>
