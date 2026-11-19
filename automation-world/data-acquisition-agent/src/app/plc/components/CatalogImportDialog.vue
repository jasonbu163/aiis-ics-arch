<!-- DS 逐 PLC JSON 预览：只新建，明确确认端点及完整目录后提交一次草稿。 -->
<template>
  <Teleport to="#daa-feedback">
    <ElDialog :model-value="local.catalogDialogOpen" :title="t('plc.catalog.title')" :append-to-body="false" :close-on-click-modal="false" :close-on-press-escape="!local.busy" :show-close="!local.busy" width="min(1200px, calc(100vw - 32px))" class="daa-import-dialog" @update:model-value="$event || local.closeCatalog()">
      <div class="console-stack">
        <p class="daa-capability-note">{{ t('plc.catalog.scope') }}</p>
        <div class="console-action-group"><input ref="picker" type="file" accept=".json,application/json" hidden @change="local.readCatalogFile" /><ConsoleActionButton label-key="plc.catalog.choose" :disabled="local.busy || local.mutationUnknown" @click="picker?.click()" /></div>
        <ElAlert v-if="local.error" :title="local.label(local.error)" type="error" :closable="false" show-icon />
        <ElAlert v-if="local.catalogUnknown" :title="t('plc.catalog.unknown')" type="warning" :closable="false" show-icon><ConsoleActionButton label-key="plc.naming.reloadAfterUnknown" :disabled="local.busy" @click="local.reload" /></ElAlert>
        <template v-if="local.catalogTarget">
          <h3>{{ t('plc.catalog.target') }}</h3>
          <ElForm :disabled="local.busy || local.mutationUnknown" label-position="top" class="daa-local-form-grid" @submit.prevent>
            <ElFormItem :label="t('plc.catalog.host')"><ElInput v-model="local.catalogTarget.host" /></ElFormItem>
            <ElFormItem :label="t('plc.catalog.port')"><ElInputNumber v-model="local.catalogTarget.port" :min="1" :max="65535" :precision="0" /></ElFormItem>
            <ElFormItem :label="t('plc.catalog.rack')"><ElInputNumber v-model="local.catalogTarget.rack" :min="0" :max="7" :precision="0" /></ElFormItem>
            <ElFormItem :label="t('plc.catalog.slot')"><ElInputNumber v-model="local.catalogTarget.slot" :min="0" :max="31" :precision="0" /></ElFormItem>
          </ElForm>
          <p class="daa-capability-note">{{ t('plc.catalog.loopback') }}</p>
          <ConsoleActionButton label-key="plc.catalog.repreview" :disabled="local.busy || local.mutationUnknown" @click="local.previewCatalog" />
        </template>
        <template v-if="local.catalogPreview">
          <dl class="daa-local-facts">
            <dt>{{ t('plc.catalog.plc') }}</dt><dd>{{ local.catalogPreview.catalog.plc.name }} · {{ local.catalogPreview.catalog.origin.plc_id }}</dd>
            <template v-if="local.catalogPreview.historyConflict"><dt>{{ t('plc.catalog.localIdentity') }}</dt><dd><code>{{ local.catalogPreview.localPlcId }}</code></dd></template>
            <dt>{{ t('plc.catalog.origin') }}</dt><dd>{{ local.catalogPreview.catalog.origin.kind }} · {{ local.catalogPreview.catalog.origin.profile_id }}</dd>
            <dt>{{ t('plc.catalog.producer') }}</dt><dd>{{ local.catalogPreview.catalog.export.producer }} · {{ local.catalogPreview.catalog.export.profile_id }}</dd>
            <dt>{{ t('plc.catalog.revision') }}</dt><dd>{{ local.catalogPreview.catalog.export.revision_id }} · {{ local.catalogPreview.catalog.export.exported_at }}</dd>
            <dt>{{ t('plc.catalog.sourceTarget') }}</dt><dd>{{ local.catalogPreview.catalog.plc.connection.host }}:{{ local.catalogPreview.catalog.plc.connection.port }} · {{ local.catalogPreview.catalog.plc.connection.rack }}/{{ local.catalogPreview.catalog.plc.connection.slot }}<template v-if="local.catalogPreview.catalog.plc.connection.local_tsap !== undefined || local.catalogPreview.catalog.plc.connection.remote_tsap !== undefined"> · TSAP {{ local.catalogPreview.catalog.plc.connection.local_tsap ?? '—' }}/{{ local.catalogPreview.catalog.plc.connection.remote_tsap ?? '—' }}</template></dd>
            <dt>{{ t('plc.catalog.fileSha') }}</dt><dd><code>{{ local.catalogPreview.sha256 }}</code></dd>
            <dt>{{ t('plc.catalog.payloadSha') }}</dt><dd><code>{{ local.catalogPreview.catalog.export.payload_sha256 }}</code></dd>
          </dl>
          <p class="daa-capability-note">{{ t('plc.catalog.hashHint') }}</p>
          <template v-if="local.catalogPreview.historyConflict"><ElAlert :title="t('plc.catalog.historyHint')" type="warning" :closable="false" show-icon /><ElCheckbox v-model="local.catalogAsNew" :disabled="local.busy" @change="local.previewCatalog">{{ t('plc.catalog.asNew') }}</ElCheckbox></template>
          <div class="console-action-group"><ConsoleActionButton label-key="plc.catalog.resetWidths" @click="resetColumnWidths" /></div>
          <ConsoleTableShell v-model:current-page="page" v-model:page-size="pageSize" :page-sizes="[10,20,50]" :total="rows.length" layout="total, sizes, prev, pager, next">
            <el-table :key="tableVersion" border :data="paged" row-key="id" @header-dragend="resizeColumn">
              <el-table-column column-key="db" :label="t('plc.catalog.db')" :width="widths.db" :min-width="180"><template #default="{ row }">{{ row.dbName }} · DB{{ row.dbNumber }} · {{ row.dbSize }} B<small class="muted-cell">{{ row.dbId }} · {{ t('plc.catalog.sourceEnabled') }}: {{ row.dbEnabled === undefined ? t('plc.catalog.notProvided') : local.label(String(row.dbEnabled)) }}</small><small v-if="local.catalogPreview?.historyConflict" class="muted-cell">{{ t('plc.catalog.localIdentity') }}: {{ local.catalogPreview.localDbIds[row.dbId] }}</small></template></el-table-column>
              <el-table-column column-key="name" :label="t('plc.naming.technicalName')" :width="widths.name" :min-width="180"><template #default="{ row }">{{ row.name }}<small class="muted-cell">{{ row.id }}</small><small v-if="local.catalogPreview?.historyConflict" class="muted-cell">{{ t('plc.catalog.localIdentity') }}: {{ local.catalogPreview.localPointIds[row.id] }}</small></template></el-table-column>
              <el-table-column column-key="address" :label="t('common.local.addressSummary')" :width="widths.address" :min-width="120"><template #default="{ row }">{{ row.data_type }} · {{ row.byte_offset }}<template v-if="row.bit !== undefined">.{{ row.bit }}</template></template></el-table-column>
              <el-table-column column-key="sourcePath" :label="t('plc.catalog.sourcePath')" :width="widths.sourcePath" :min-width="130"><template #default="{ row }">{{ row.source_path ?? t('plc.catalog.notProvided') }}</template></el-table-column>
              <el-table-column column-key="zh" :label="t('plc.naming.displayNameZh')" :width="widths.zh" :min-width="120"><template #default="{ row }">{{ row.display_names?.['zh-CN'] ?? '' }}</template></el-table-column>
              <el-table-column column-key="en" :label="t('plc.naming.displayNameEn')" :width="widths.en" :min-width="120"><template #default="{ row }">{{ row.display_names?.['en-US'] ?? '' }}</template></el-table-column>
              <el-table-column column-key="legacy" :label="t('plc.catalog.legacy')" :width="widths.legacy" :min-width="130"><template #default="{ row }">{{ row.display_name ?? t('plc.catalog.notProvided') }}</template></el-table-column>
              <el-table-column column-key="description" :label="t('plc.catalog.description')" :width="widths.description" :min-width="140"><template #default="{ row }">{{ row.description ?? t('plc.catalog.notProvided') }}</template></el-table-column>
              <el-table-column column-key="enabled" :label="t('plc.catalog.sourceEnabled')" :width="widths.enabled" :min-width="120"><template #default="{ row }">{{ local.label(String(row.source_enabled)) }}</template></el-table-column>
            </el-table>
          </ConsoleTableShell>
          <ElCheckbox v-model="local.catalogConfirmed" :disabled="local.busy || local.mutationUnknown">{{ t('plc.catalog.confirmTarget') }}</ElCheckbox>
        </template>
      </div>
      <template #footer><div class="console-action-group"><ConsoleActionButton label-key="common.local.cancelEdit" :disabled="local.busy" @click="local.closeCatalog" /><ConsoleActionButton label-key="plc.catalog.commit" tone="primary" :disabled="local.busy || local.dirty || local.editing || local.mutationUnknown || !local.catalogPreview || !local.catalogConfirmed || (local.catalogPreview.historyConflict && !local.catalogAsNew)" @click="local.confirmCatalog" /></div></template>
    </ElDialog>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElAlert, ElCheckbox, ElDialog, ElForm, ElFormItem, ElInput, ElInputNumber } from 'element-plus';
import type { LocalConsole } from '../../../console/composables/useLocalAcquisitionConsole';
import { loadWidths, resetWidths, saveWidth, widthKey } from '../../../console/tableWidths';
import ConsoleActionButton from '../../../components/console/ConsoleActionButton.vue';
import ConsoleTableShell from '../../../components/console/ConsoleTableShell.vue';

const props = defineProps<{ local: LocalConsole }>();
const { t } = useI18n();
const picker = ref<HTMLInputElement | null>(null), page = ref(1), pageSize = ref(20), tableVersion = ref(0);
const rows = computed(() => props.local.catalogPreview?.catalog.dbs.flatMap(db => db.points.map(point => ({ ...point, dbId: db.id, dbName: db.name, dbNumber: db.number, dbSize: db.size_bytes, dbEnabled: db.source_enabled }))) ?? []);
const paged = computed(() => rows.value.slice((page.value - 1) * pageSize.value, page.value * pageSize.value));
watch([pageSize, () => props.local.catalogPreview], () => { page.value = 1; });
const columns = [{ id: 'db', width: 220, min: 180 }, { id: 'name', width: 220, min: 180 }, { id: 'address', width: 140, min: 120 }, { id: 'sourcePath', width: 160, min: 130 }, { id: 'zh', width: 150, min: 120 }, { id: 'en', width: 150, min: 120 }, { id: 'legacy', width: 150, min: 130 }, { id: 'description', width: 180, min: 140 }, { id: 'enabled', width: 130, min: 120 }];
let storage: Storage | undefined;
try { storage = window.localStorage; } catch { /* 无本机偏好时保留默认列宽。 */ }
const key = widthKey('com.aiis.aw.dataacquisitionagent', 'plc.catalog.preview');
const widths = ref(loadWidths(storage, key, columns));
function resizeColumn(width: number, _old: number, column: { columnKey?: string }) { widths.value = saveWidth(storage, key, columns, widths.value, column.columnKey ?? '', width); tableVersion.value++; }
function resetColumnWidths() { widths.value = resetWidths(storage, key, columns); tableVersion.value++; }
</script>
