<!-- DAA来源导入私有视图：仅展示逐块映射/分页与折叠差异；状态和IPC仍归唯一owner。 -->
<template>
  <section class="daa-source-import">
    <p class="daa-capability-note">{{ t('plc.sourceImport.help') }}</p>
    <el-alert v-if="local.dirty || local.editing" :title="t('common.local.saveBeforeTools')" type="warning" :closable="false" />
    <div class="console-action-group daa-source-import__picker"><input ref="fileInput" type="file" accept=".db,.udt" multiple hidden @change="local.readFiles" /><ConsoleActionButton label-key="common.local.importFile" tone="primary" :disabled="local.busy || local.dirty || local.editing || !local.selectedPlc" @click="fileInput?.click()" /><span class="daa-capability-note">{{ local.sources.map(s => s.name).join(' · ') || t('plc.sourceImport.chooseHint') }}</span></div>
    <template v-if="local.identification && local.sources.length">
      <p>{{ t('plc.sourceImport.counts', { files: local.identification.fileCount, dbs: local.identification.dbCount, udts: local.identification.udtCount }) }}</p>
      <el-table :data="local.pagedImportRows" :row-key="rowKey" :tooltip-options="{ appendTo: '#daa-feedback' }">
        <el-table-column :label="t('plc.sourceImport.selected')" width="92"><template #default="{ row }"><ElCheckbox v-model="row.mapping.selected" :disabled="local.busy" :aria-label="t('plc.sourceImport.selectBlock', { name: row.block.blockKey.name })" /></template></el-table-column>
        <el-table-column :label="t('plc.sourceImport.block')" min-width="170"><template #default="{ row }"><strong>{{ row.block.blockKey.name }}</strong><small class="muted-cell">{{ row.block.file }}:{{ row.block.line }} · {{ t('plc.sourceImport.leaves', { count: row.block.leafCount }) }}</small></template></el-table-column>
        <el-table-column :label="t('common.local.dbNumber')" min-width="140"><template #default="{ row }"><ElInputNumber :model-value="row.mapping.dbNumber" @update:model-value="row.mapping.dbNumber = $event ?? null" :disabled="local.busy" :min="1" :max="65535" :precision="0" controls-position="right" :aria-label="t('common.local.dbNumber') + ' ' + row.block.blockKey.name" /></template></el-table-column>
        <el-table-column :label="t('plc.sourceImport.target')" min-width="190"><template #default="{ row }"><ElSelect v-model="row.mapping.targetId" :disabled="local.busy" clearable append-to="#daa-feedback" :placeholder="t('plc.sourceImport.newBlock')" @change="local.changeImportTarget(row.mapping)"><ElOption v-for="d in local.dbs" :key="d.id" :label="d.name + ' · DB' + d.number" :value="d.id" /></ElSelect></template></el-table-column>
        <el-table-column :label="t('plc.sourceImport.diagnostics')" min-width="220"><template #default="{ row }"><span v-if="!row.block.issues.length">{{ t(row.mapping.targetId ? 'plc.sourceImport.updateCandidate' : 'plc.sourceImport.newBlock') }}</span><p v-for="(issue, i) in row.block.issues" :key="i">{{ local.label(issue.code) }} · {{ issue.file }}:{{ issue.line }} {{ issue.path }}</p></template></el-table-column>
      </el-table>
      <ElPagination v-model:current-page="local.importPage" v-model:page-size="local.importPageSize" :page-sizes="[10, 20, 50]" :total="local.importRows.length" layout="total, sizes, prev, pager, next" @size-change="local.importPage = 1" />
      <details class="daa-details"><summary>{{ t('plc.sourceImport.types') }}</summary><p v-for="b in local.identification.blocks.filter(b => b.blockKey.kind === 'TYPE')" :key="b.sourceIndex + ':' + b.blockKey.name">{{ b.file }}:{{ b.line }} · {{ b.blockKey.name }}<span v-for="i in b.issues" :key="i.code"> · {{ local.label(i.code) }}</span></p></details>
      <div class="console-action-group"><ConsoleActionButton label-key="common.local.previewImport" :disabled="local.busy || local.dirty || local.editing || !local.mappings.some(m => m.selected)" @click="local.importSources(false)" /></div>
    </template>
    <p v-if="local.preview" class="daa-capability-note">{{ t(local.preview.canConfirm ? 'plc.sourceImport.ready' : 'plc.sourceImport.blocked') }}</p>
    <p v-for="(issue, i) in local.preview?.issues.slice(0, 3) ?? []" :key="i" class="daa-capability-note">{{ local.label(issue.code) }} · {{ issue.file }}:{{ issue.line }}</p>
    <div class="console-action-group"><ConsoleActionButton label-key="plc.sourceImport.structure" :disabled="!local.dbs.length || local.busy" @click="local.sourceStructureOpen = true" /></div>
    <Teleport to="#daa-feedback"><ElDialog v-model="local.sourcePreviewOpen" :title="t('common.local.importChanges')" :append-to-body="false" :close-on-click-modal="false" :show-close="!local.busy" :close-on-press-escape="!local.busy" width="min(1000px, calc(100vw - 32px))" class="daa-import-dialog">
    <section v-if="local.preview" class="daa-local-edit-section">
      
      <p>{{ t(local.preview.canConfirm ? 'plc.sourceImport.ready' : 'plc.sourceImport.blocked') }}</p>
      <p class="daa-capability-note">{{ t('plc.naming.importSummary', { count: local.preview.nameChanges.length, pending: local.preview.nameChanges.filter(p => p.proposedMode === 'pending').length }) }}</p>
      <details class="daa-details"><summary>{{ t('plc.naming.newName') }}</summary><p v-for="row in local.preview.nameChanges" :key="row.pointId" class="daa-name-diff">{{ row.sourcePath }} · {{ row.oldName || '—' }} → {{ row.proposedName || t('plc.naming.modes.pending') }} · {{ t('plc.naming.modes.' + (row.proposedMode ?? 'legacy')) }}</p></details>
      <p v-for="(issue, i) in local.preview.issues" :key="i">{{ local.label(issue.code) }} · {{ issue.file }}:{{ issue.line }} {{ issue.path }}</p>
      <details v-for="delta in local.preview.deltas" :key="delta.dbId" class="daa-details"><summary>{{ delta.blockName }} · DB{{ delta.number }} · {{ local.label(delta.status) }}</summary>
        <p>{{ t('plc.sourceImport.preservation', { points: delta.preservedPoints, manual: delta.preservedManual, invalidated: delta.invalidatedConfirmations }) }}</p>
        <p v-if="delta.layoutChanged">{{ t('plc.sourceImport.layoutChanged') }}</p><p v-if="delta.commentsChanged">{{ t('plc.sourceImport.commentsChanged') }}</p><p v-if="delta.isolatedUdtVersions">{{ t('plc.sourceImport.udtIsolation') }}</p>
        <p>{{ t('plc.sourceImport.added') }}: {{ delta.addedPaths.join(', ') || '—' }}</p><p>{{ t('plc.sourceImport.changedTypes') }}: {{ delta.typeChangedPaths.join(', ') || '—' }}</p>
      </details>
      <details v-for="d in local.preview.configuration.dbs.filter(d => local.preview?.deltas.some(x => x.dbId === d.id))" :key="d.id" class="daa-details"><summary>{{ d.name }} · {{ t('plc.sourceImport.structure') }}</summary><ElTree :data="d.tree" node-key="path" :props="{ children: 'children', label: 'name' }" :expand-on-click-node="false"><template #default="{ data }"><span>{{ data.name }} · {{ data.dataType }} · {{ data.line }}</span></template></ElTree></details>
      <details class="daa-details"><summary>{{ t('plc.sourceImport.readiness') }}</summary><p v-for="(i, n) in local.preview.readiness" :key="n">{{ local.label(i.code) }} · {{ i.path }}</p></details>
    </section>
      <template #footer><div class="console-action-group"><ConsoleActionButton label-key="plc.sourceImport.closePreview" :disabled="local.busy" @click="local.sourcePreviewOpen = false" /><ConsoleActionButton label-key="common.local.confirmImport" tone="primary" :disabled="local.busy || local.dirty || local.editing || !local.preview?.canConfirm" @click="local.importSources(true)" /></div></template>
    </ElDialog>
    <ElDialog v-model="local.sourceStructureOpen" :title="t('plc.sourceImport.structure')" :append-to-body="false" :close-on-click-modal="false" width="min(900px, calc(100vw - 32px))" class="daa-import-dialog">
      <p class="daa-capability-note">{{ t('plc.sourceImport.lengthEditHint') }}</p>
      <details v-for="d in local.dbs.filter(d => !local.selectedDb || d.id === local.selectedDb)" :key="d.id" class="daa-details"><summary>{{ d.name }} · DB{{ d.number }} · {{ local.label(d.complete ? 'complete' : 'incomplete') }}</summary><ElForm label-position="top" @submit.prevent><ElFormItem :label="t('common.local.dbLength')"><ElInputNumber v-model="d.length" :disabled="local.busy" :min="1" :max="65536" :precision="0" controls-position="right" /></ElFormItem></ElForm><ElTree :data="d.tree" node-key="path" :props="{ children: 'children', label: 'name' }" :expand-on-click-node="false"><template #default="{ data }"><span>{{ data.name }} · {{ data.dataType }} · {{ data.line }}</span></template></ElTree></details>
    </ElDialog></Teleport>
  </section>
</template>
<script setup lang="ts">
import { ElDialog, ElTree, ElCheckbox, ElForm, ElFormItem, ElInputNumber, ElOption, ElSelect } from 'element-plus';
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import type { LocalConsole } from '../../../console/composables/useLocalAcquisitionConsole';
import type { IdentifiedBlock } from '../../../services/localAcquisition';
import ConsoleActionButton from '../../../components/console/ConsoleActionButton.vue';
const props = defineProps<{ local: LocalConsole }>();
const { t } = useI18n();
const fileInput = ref<HTMLInputElement | null>(null);
const rowKey = (row: { block: IdentifiedBlock }) => JSON.stringify([row.block.sourceIndex, row.block.blockKey]);
</script>
