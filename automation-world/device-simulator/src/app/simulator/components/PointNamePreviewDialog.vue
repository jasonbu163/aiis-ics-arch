<!-- 布局/命名预览共享DAA确认弹层范式；只展示服务候选，取消不提交。 -->
<template>
  <el-dialog :model-value="!!preview" :title="t('simulator.preview')" :append-to-body="false" width="min(920px, calc(100vw - 32px))" @close="emit('cancel')">
    <template v-if="preview">
      <p>{{ t('simulator.previewSaveOnly') }}</p>
      <el-table :data="rows" max-height="420">
        <el-table-column v-for="column in columns" :key="column" :label="t('simulator.'+column)">
          <template #default="{row}">{{ display(row[column]) }}</template>
        </el-table-column>
      </el-table>
      <p v-if="!rows.length">{{ t('simulator.layoutReady') }}</p>
    </template>
    <template #footer>
      <ConsoleActionButton label-key="simulator.cancel" data-testid="preview-cancel" @click="emit('cancel')" />
      <ConsoleActionButton label-key="simulator.confirm" tone="primary" data-testid="preview-confirm" :loading="busy" :disabled="busy" @click="emit('confirm')" />
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { computed } from 'vue';
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
}>(), { t } = useI18n();
const rows = computed(() => Array.isArray(props.preview?.details.rows) ? props.preview!.details.rows as Record<string, Json>[] : []);
const columns = ['pointId', 'name', 'mode', 'reason'];
function display(value: Json | undefined) { return value === null || value === undefined ? '—' : String(value); }
</script>
