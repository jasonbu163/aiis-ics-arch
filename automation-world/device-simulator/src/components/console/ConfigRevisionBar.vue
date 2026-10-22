<!-- 沿DAA保存/版本事实条，适配DS草稿；校验问题定位到实例、DB和点。 -->
<template>
  <ConsoleCard title-key="simulator.configuration" compact>
    <template #actions>
      <el-tag :type="local.dirty ? 'warning' : 'info'">{{ t(local.dirty ? 'simulator.dirty' : 'simulator.saved') }}</el-tag>
      <ConsoleActionButton label-key="simulator.save" data-testid="configuration-save" :disabled="local.busy || local.editing || !local.draft" :loading="local.busy" :tone="local.dirty ? 'primary' : 'secondary'" @click="local.save()" />
      <ConsoleActionButton label-key="simulator.reload" :disabled="local.busy" @click="reloadOpen = true" />
    </template>
    <p>{{ t('simulator.saveApplyHint') }}</p>
    <code class="ds-wrap">{{ local.configuration?.etag || '—' }}</code>
    <ul v-if="local.configuration?.issues.length" class="ds-issues">
      <li v-for="(issue, index) in local.configuration.issues.slice(0, 100)" :key="index">
        {{ issueLabel(issue.code) }} · {{ issueLocation(issue) }}
      </li>
    </ul>
    <ConsoleOperationDialog v-model="reloadOpen" title-key="simulator.reload" message-key="simulator.reloadHint" cancel-label-key="simulator.cancel" confirm-label-key="simulator.confirm" @confirm="reload" />
  </ConsoleCard>
</template>
<script setup lang="ts">
import { inject, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import type { Issue } from '../../services/deviceSimulator';
import { simulatorKey } from '../../console/composables/useDeviceSimulator';
import ConsoleCard from './ConsoleCard.vue';
import ConsoleActionButton from './ConsoleActionButton.vue';
import ConsoleOperationDialog from './ConsoleOperationDialog.vue';
const local = inject(simulatorKey)!;
const { t, te } = useI18n();
const reloadOpen = ref(false);
function issueLabel(code: string) {
    const key = 'simulator.errors.' + code;
    return te(key) ? t(key) : t('simulator.configurationBlocked');
}
function issueLocation(issue: Issue) {
    const instance = local.draft?.instances.find(item => item.id === issue.instanceId);
    const db = instance?.dbs.find(item => item.id === issue.dbId);
    const point = db?.points.find(item => item.id === issue.pointId);
    return [
        instance ? `${t('simulator.instance')}: ${instance.name}` : t('simulator.configuration'),
        db ? `DB${db.number} · ${db.name}` : null,
        point ? `${t('simulator.levels.point')}: ${point.name || point.sourcePath}` : null,
    ].filter(Boolean).join(' / ');
}
async function reload() {
    await local.action(local.reload);
    if (!local.error)
        reloadOpen.value = false;
}
</script>
