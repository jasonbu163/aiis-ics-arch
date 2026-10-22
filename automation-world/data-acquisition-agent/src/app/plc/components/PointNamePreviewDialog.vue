<!-- 技术名差异纯展示：选择/候选/token仍归唯一owner；分页与窄窗复用CU。 -->
<template>
  <Teleport to="#daa-feedback"><ElDialog :model-value="local.namePreviewOpen" :title="t('plc.naming.preview')" :append-to-body="false" :close-on-click-modal="false" width="min(1000px, calc(100vw - 32px))" class="daa-name-dialog" @update:model-value="$event || local.closeNames()">
    <p class="daa-capability-note">{{ t('plc.naming.explicitHint') }}</p>
    <el-alert v-if="local.error" :title="local.label(local.error)" type="error" :closable="false" />
    <p v-for="(issue, i) in local.namePreview?.readiness ?? []" :key="i">{{ local.label(issue.code) }} · {{ issue.path }}</p>
    <el-table :data="local.pagedNames" row-key="pointId" size="small">
      <el-table-column :label="t('plc.naming.sourcePath')" prop="sourcePath" min-width="180" />
      <el-table-column :label="t('plc.naming.oldName')" min-width="180"><template #default="{ row }"><strong>{{ row.oldName || '—' }}</strong><small class="muted-cell">{{ t('plc.naming.modes.' + (row.oldMode ?? 'legacy')) }}</small></template></el-table-column>
      <el-table-column :label="t('plc.naming.newName')" min-width="200"><template #default="{ row }"><strong>{{ row.proposedName || t('plc.naming.modes.pending') }}</strong><small class="muted-cell">{{ t('plc.naming.modes.' + (row.proposedMode ?? 'legacy')) }}</small></template></el-table-column>
      <el-table-column :label="t('plc.naming.reason')" min-width="190"><template #default="{ row }">{{ t('plc.naming.reasons.' + row.reason) }}<small class="muted-cell">{{ t(row.addressConfirmed ? 'plc.naming.addressConfirmed' : 'plc.naming.addressPending') }}</small></template></el-table-column>
    </el-table>
    <ElPagination v-model:current-page="local.namePage" v-model:page-size="local.namePageSize" :page-sizes="[10, 20, 50]" :total="local.namePreview?.rows.length ?? 0" layout="total, sizes, prev, pager, next" @size-change="local.namePage = 1" />
    <template #footer><div class="console-action-group"><ConsoleActionButton label-key="common.local.cancelEdit" :disabled="local.busy" @click="local.closeNames" /><ConsoleActionButton label-key="plc.naming.confirm" tone="primary" :disabled="local.busy || !local.namePreview?.canConfirm" @click="local.confirmNames" /></div></template>
  </ElDialog></Teleport>
</template>
<script setup lang="ts">
import { ElDialog, ElPagination } from 'element-plus';
import { useI18n } from 'vue-i18n';
import type { LocalConsole } from '../../../console/composables/useLocalAcquisitionConsole';
import ConsoleActionButton from '../../../components/console/ConsoleActionButton.vue';
defineProps<{ local: LocalConsole }>();
const { t } = useI18n();
</script>
