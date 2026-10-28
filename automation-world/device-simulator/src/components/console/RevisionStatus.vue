<!-- 版本状态摘要：一致时只显示一次运行版本，问号保留三类状态及完整身份。 -->
<template>
  <div class="ds-inline" data-testid="revision-facts">
    <span>{{ t('simulator.versionDisplay.loaded', {version: label(loaded)}) }}</span>
    <el-tag v-if="aligned" type="success" size="small">{{ t('simulator.versionDisplay.aligned') }}</el-tag>
    <template v-else>
      <span v-if="saved">{{ t('simulator.versionDisplay.latest', {version: label(saved)}) }}</span>
      <span v-if="selected && selected !== saved && selected !== loaded">{{ t('simulator.versionDisplay.selected', {version: label(selected)}) }}</span>
      <el-tag v-if="saved || selected" type="warning" size="small">{{ t('simulator.versionDisplay.pending') }}</el-tag>
    </template>
    <ConsoleFieldHelp :label="t('simulator.versionDisplay.title')" :text="details" />
  </div>
</template>
<script setup lang="ts">
import { computed, inject } from 'vue';
import { useI18n } from 'vue-i18n';
import { simulatorKey } from '../../console/composables/useDeviceSimulator';
import { revisionLabel } from '../../console/revisions';
import ConsoleFieldHelp from './ConsoleFieldHelp.vue';
const props = defineProps<{ saved?: string | null; selected?: string | null; loaded?: string | null; etag?: string; hint?: string }>();
const local = inject(simulatorKey)!;
const { t } = useI18n();
const label = (id?: string | null) => revisionLabel(id, local.configuration?.revisions);
const aligned = computed(() => !!props.saved && props.saved === props.selected && props.selected === props.loaded);
const details = computed(() => [
    t('simulator.savedSelectedLoaded'),
    ...(props.hint ? [props.hint] : []),
    ...(['saved', 'selected', 'loaded'] as const).map(field => `${t('simulator.versionDisplay.' + field + 'Detail')}: ${label(props[field])} · ${props[field] || '—'}`),
    ...(props.etag ? [`${t('simulator.versionDisplay.etag')}: ${props.etag}`] : []),
].join('\n'));
</script>
