<!-- 迁入时记录：仅在配置栏既有详情内展示Rust有界历史与权威重试动作。 -->
<template>
  <section v-if="local?.migration" class="console-stack">
    <h3>{{ t('common.local.migration.title') }}</h3>
    <div class="console-action-group"><ConsoleActionButton v-if="local.migration.retryAllowed" label-key="common.local.migration.retry" :disabled="local.busy || local.dirty || local.editing" @click="local.retryMigration()" /></div>
    <div class="console-stack">
      <el-alert :title="local.migration.status === 'failed' ? t('common.local.migration.failed') : local.label(local.migration.status)" :description="t('common.local.migration.boundary')" :type="local.migration.status === 'failed' ? 'warning' : 'info'" :closable="false" show-icon />
      <p>{{ t('common.local.migration.counts', local.migration.counts) }}</p>
      <p v-if="local.migration.errorCode">{{ local.label(local.migration.errorCode) }}</p>
      <p v-if="local.migration.statusPersistence === 'unknown'">{{ t('common.local.migration.persistenceUnknown') }}</p>
      <p v-if="local.dirty || local.editing">{{ t('common.local.migration.unsaved') }}</p>
      <p class="daa-source-note">{{ t('common.local.migration.details') }}</p>
        <p v-for="source in local.migration.sources" :key="source.kind">{{ local.label(source.kind) }} · {{ source.path }} · {{ local.label(source.origin) }} · {{ source.bytes ?? '—' }} B · {{ source.sha256 ?? local.label(source.hashUnavailable) }}</p>
        <p v-if="local.migration.sources.some(s => s.origin === 'application_default')">{{ t('common.local.migration.example') }}</p>
        <p v-for="(issue, index) in local.migration.diagnostics" :key="index">{{ local.label(issue.code) }} · {{ issue.path }}</p>
        <p>{{ t('common.local.migration.diagnostics', { total: local.migration.diagnosticTotal, omitted: local.migration.diagnosticOmitted }) }}</p>
        <p>{{ t('common.local.migration.attempt') }}: {{ local.migration.attemptId ?? '—' }}</p>
    </div>
  </section>
</template>
<script setup lang="ts">
import { inject } from 'vue'
import { useI18n } from 'vue-i18n'
import { localConsoleKey } from '../../console/composables/useLocalAcquisitionConsole'
import ConsoleActionButton from './ConsoleActionButton.vue'
const local = inject(localConsoleKey)
const { t } = useI18n()
</script>
