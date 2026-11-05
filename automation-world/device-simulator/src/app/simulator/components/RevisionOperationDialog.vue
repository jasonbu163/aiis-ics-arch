<!-- 版本发布/单个与批量删除共用清单；回退保留必须显式确认放弃，不改变当前加载或运行值。 -->
<template>
  <el-dialog :model-value="!!preview" :title="t(publishing ? 'simulator.versions.publishTitle' : 'simulator.versions.deleteTitle')" :append-to-body="false" width="min(820px, calc(100vw - 32px))" :show-close="!busy" :close-on-click-modal="!busy" :close-on-press-escape="!busy" @close="emit('cancel')">
    <div v-if="preview" class="console-stack" data-testid="version-preview">
      <el-alert v-if="unknown" :title="t('simulator.versions.unknownHint')" type="warning" :closable="false" />
      <el-alert v-if="publishing" :title="t(preview.details.unchanged ? 'simulator.versions.unchanged' : 'simulator.versions.createNotice', { version: preview.details.nextSavedSeq })" type="info" :closable="false" />
      <p>{{ t('simulator.versions.workspaceHint') }}</p>
      <p>{{ t('simulator.versions.cleanupNotice', { count: rows.length }) }}</p>
      <el-alert v-if="releases.length" :title="t('simulator.versions.rollbackWarning')" type="warning" :closable="false" />
      <ConsoleDataTable v-if="rows.length" table-id="preview.revision-changes" :data="rows" row-key="revisionId">
        <el-table-column column-key="version" min-width="140" :label="t('simulator.versionDisplay.title')"><template #default="{row}">v{{ row.savedSeq }}</template></el-table-column>
        <el-table-column column-key="savedTime" min-width="210" :label="t('simulator.versions.savedTime')"><template #default="{row}">{{ formatShanghaiTime(row.createdUtc) || '—' }}</template></el-table-column>
        <el-table-column v-if="releases.length" column-key="rollbackInstances" min-width="220" :label="t('simulator.versions.rollbackInstances')"><template #default="{row}">{{ rollbackNames(row.revisionId) }}</template></el-table-column>
      </ConsoleDataTable>
      <el-checkbox v-if="releases.length" v-model="releaseRollback" class="revision-release-ack" :disabled="busy || unknown" data-testid="rollback-release-confirm">{{ t('simulator.versions.releaseRollback') }}</el-checkbox>
      <p>{{ t('simulator.versions.retentionHint') }}</p>
    </div>
    <template #footer>
      <ConsoleActionButton label-key="simulator.cancel" data-testid="version-cancel" :disabled="busy" @click="emit('cancel')" />
      <ConsoleActionButton :label-key="publishing ? 'simulator.versions.confirmPublish' : 'simulator.versions.confirmDelete'" :tone="publishing ? 'primary' : 'danger'" data-testid="version-confirm" :disabled="busy || blocked || releases.length > 0 && !releaseRollback" :loading="busy" @click="emit('confirm', releaseRollback)" />
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import type { Instance, Preview, Revision, RollbackRelease } from '../../../services/deviceSimulator';
import { formatShanghaiTime } from '../../../console/time';
import ConsoleDataTable from '../../../components/console/ConsoleDataTable.vue';
import ConsoleActionButton from '../../../components/console/ConsoleActionButton.vue';
const props = defineProps<{ preview: Preview | null; busy: boolean; blocked: boolean; unknown: boolean; instances?: Pick<Instance, 'id' | 'name'>[] }>();
const emit = defineEmits<{ cancel: []; confirm: [releaseRollback: boolean] }>(), { t } = useI18n();
const releaseRollback = ref(false);
watch(() => props.preview?.token, () => { releaseRollback.value = false; });
const publishing = computed(() => props.preview?.kind === 'publish_revision');
const rows = computed(() => Array.isArray(props.preview?.details.deleteRevisions) ? props.preview!.details.deleteRevisions as Pick<Revision, 'revisionId' | 'savedSeq' | 'createdUtc'>[] : []);
const releases = computed(() => Array.isArray(props.preview?.details.rollbackReleases) ? props.preview!.details.rollbackReleases as RollbackRelease[] : []);
function rollbackNames(revisionId: string) { return releases.value.filter(r => r.revisionId === revisionId).map(r => props.instances?.find(i => i.id === r.instanceId)?.name || r.instanceId).join(' / ') || '—'; }
</script>
<style scoped>
.revision-release-ack { height:auto;white-space:normal;align-items:baseline; }
.revision-release-ack :deep(.el-checkbox__label) { white-space:normal;overflow-wrap:anywhere; }
</style>
