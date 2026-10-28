<!-- 布局/命名预览共享DAA确认弹层范式；只展示服务候选，取消不提交。 -->
<template>
  <el-dialog :model-value="!!preview" :title="t('simulator.preview')" :append-to-body="false" width="min(920px, calc(100vw - 32px))" @close="emit('cancel')">
    <template v-if="preview">
      <p>{{ t('simulator.previewSaveOnly') }}</p>
      <template v-if="preview.kind==='names'">
      <ConsoleDataTable table-id="preview.names" :data="rows" max-height="420">
        <el-table-column :column-key="column" min-width="220" v-for="column in columns" :key="column" :label="t('simulator.'+column)">
          <template #default="{row}">{{ display(row[column]) }}</template>
        </el-table-column>
      </ConsoleDataTable>
      </template>
      <template v-else-if="preview.kind==='layout'">
        <p>{{ t('simulator.editing.layoutFacts') }}</p>
        <dl v-if="layoutDb" class="ds-facts">
          <dt>{{ t('simulator.db') }}</dt><dd>DB{{ layoutDb.number }} · {{ layoutDb.name }}</dd>
          <dt>{{ t('simulator.dbLength') }}</dt><dd>{{ layoutDb.length }}</dd>
          <dt>{{ t('simulator.reason') }}</dt><dd>{{ display(preview.details.reason) }}</dd>
        </dl>
        <ConsoleDataTable table-id="preview.layout" v-if="layoutDb" :data="layoutDb.points" max-height="420">
          <el-table-column column-key="name" min-width="200" prop="name" :label="t('simulator.name')" />
          <el-table-column column-key="dataType" min-width="110" prop="dataType" :label="t('simulator.dataType')" />
          <el-table-column column-key="address" min-width="110" :label="t('simulator.address')"><template #default="{row}">{{ row.byte??'—' }}{{ row.bit===null?'':'.'+row.bit }}</template></el-table-column>
          <el-table-column column-key="manualReason" min-width="240" prop="manualReason" :label="t('simulator.manualReason')" />
        </ConsoleDataTable>
        <el-alert v-else :title="t('simulator.editing.previewMissing')" type="warning" :closable="false" />
      </template>
    </template>
    <template #footer>
      <ConsoleActionButton label-key="simulator.cancel" data-testid="preview-cancel" @click="emit('cancel')" />
      <ConsoleActionButton label-key="simulator.confirm" tone="primary" data-testid="preview-confirm" :loading="busy" :disabled="busy" @click="emit('confirm')" />
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import ConsoleDataTable from '../../../components/console/ConsoleDataTable.vue';
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
const layoutDb = computed(()=>props.preview?.workspace.instances.flatMap(i=>i.dbs).find(db=>db.id===props.preview?.details.dbId));
const columns = ['pointId', 'name', 'mode', 'reason'];
function display(value: Json | undefined) { return value === null || value === undefined ? '—' : String(value); }
</script>
