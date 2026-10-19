<!-- 本地配置工作流：真实草稿与显式保存/激活；原折叠详情承接运行版本及迁入历史。 -->
<template>
  <ConsoleCard v-if="local" class="daa-revision-bar" compact title-key="common.local.configuration">
    <template #actions>
      <el-tag type="warning" effect="plain" :title="t('common.local.origin')">{{ local.bootstrap.origin }}</el-tag>
      <el-tag :type="local.dirty ? 'warning' : 'info'" effect="plain">{{ t(local.draft ? (local.dirty ? 'common.local.draftDirty' : 'common.local.draftSaved') : 'common.local.draftLoading') }}</el-tag>
      <ConsoleActionButton label-key="common.local.save" :disabled="local.busy || local.editing || !local.draft" :tone="local.dirty ? 'primary' : 'secondary'" @click="local.save" />
      <ConsoleActionButton label-key="common.local.activate" :disabled="local.busy || local.editing || local.dirty || !local.view || !!local.view.issues.length" @click="activate(false)" />
    </template>
    <div class="console-stack">
      <el-alert v-if="local.error" :title="local.label(local.error)" type="error" :closable="false" show-icon />
      <p v-if="local.conflictVersion" class="diagnostic-message">{{ t('common.local.currentEtag') }}: {{ local.conflictVersion }}</p>
      <el-alert v-if="local.snapshotError" :title="local.snapshot ? t('common.local.staleSnapshot', { time: local.snapshot.generatedAt }) : t('common.feedback.notLoaded')" :description="local.label(local.snapshotError)" type="warning" :closable="false" show-icon />
      <el-alert v-if="local.notice && !local.dirty && !local.editing" :title="local.label(local.notice)" type="success" :closable="false" />
      <p class="daa-capability-note">{{ t(local.editing ? 'common.local.finishEditing' : 'common.local.saveApplyHint') }}</p>
      <div v-if="migrationAttention" class="console-action-group">
        <span class="daa-capability-note">{{ t(migrationAttention) }}</span>
        <ConsoleActionButton size="small" label-key="common.local.migration.openDetails" @click="openMigrationDetails" />
      </div>
      <details ref="configurationDetails" class="daa-details">
        <summary>{{ t('common.local.configurationDetails') }}</summary>
        <p class="daa-source-note">{{ t('common.local.boundary', { origin: local.bootstrap.origin }) }}</p>
        <dl class="daa-local-facts">
          <template v-for="key in ['active', 'loaded', 'used', 'etag'] as const" :key="key"><dt>{{ t('common.local.' + key) }}</dt><dd><code>{{ local.view?.[key] ?? '—' }}</code></dd></template>
          <dt>{{ t('common.local.phase') }}</dt><dd>{{ local.label(local.view?.phase) }}</dd>
        </dl>
        <div class="console-action-group">
          <ConsoleActionButton size="small" label-key="common.local.reload" :disabled="local.busy" @click="reload" />
          <ConsoleActionButton size="small" label-key="common.local.rollback" :disabled="local.busy || !local.view?.previous" @click="activate(true)" />
        </div>
        <YamlMigrationNotice />
      </details>
      <ul v-if="local.view?.issues.length" class="daa-local-issues"><li v-for="(issue, i) in local.view.issues" :key="i">{{ local.label(issue.code) }} · {{ issue.file }}:{{ issue.line }} {{ issue.path }}</li></ul>
    </div>
  </ConsoleCard>
</template>
<script setup lang="ts">
import { computed, inject, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { localConsoleKey } from '../../console/composables/useLocalAcquisitionConsole'
import ConsoleCard from './ConsoleCard.vue'
import ConsoleActionButton from './ConsoleActionButton.vue'
import YamlMigrationNotice from './YamlMigrationNotice.vue'
const local = inject(localConsoleKey)
const { t } = useI18n()
const configurationDetails = ref<HTMLDetailsElement | null>(null)
const migrationAttention = computed(() => local?.migration?.statusPersistence === 'unknown'
  ? 'common.local.migration.unknownHint'
  : local?.migration?.status === 'failed' && local.migration.retryAllowed === true
    ? 'common.local.migration.failedHint' : '')
function openMigrationDetails() { if (configurationDetails.value) configurationDetails.value.open = true }
async function activate(rollback: boolean) { if (await local?.confirmAction(rollback ? 'common.local.rollbackConfirm' : 'common.local.activateConfirm')) await local?.activate(rollback) }
async function reload() { if (await local?.confirmAction('common.local.reloadConfirm')) await local?.reload() }
</script>
