<!--
  File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/components/MappingBatchOperationsDialog.vue
  Description: Module-private resource-scoped Mapping JSON/XLSX batch-operation dialog.
  Main Features:
    - Emits file exchange and Backend preview/apply intentions for one configuration resource
    - Shows a backend import preview before the explicit single apply confirmation
    - Reuses the existing browser file chooser and native Tauri save path via its parent
-->
<script setup lang="ts">
import { ElDialog } from "element-plus";
import { ConsoleActionButton } from "@aw-ui";
import { ref } from "vue";

import type { LocaleMessages } from "../../../locales";
import type { ConfigurationImportPreview } from "../types";
import type { MappingConfigurationFileFormat } from "../utils/mappingConfigurationFiles";

const props = defineProps<{
  labels: LocaleMessages;
  title: string;
  busy: boolean;
  savingFile: boolean;
  preview: ConfigurationImportPreview | null;
  error: string;
  enabled: boolean;
}>();

const emit = defineEmits<{
  close: [];
  "download-template": [format: MappingConfigurationFileFormat];
  export: [format: MappingConfigurationFileFormat];
  import: [file: File];
  apply: [];
}>();

const fileInput = ref<HTMLInputElement | null>(null);

function chooseFile() {
  fileInput.value?.click();
}

function importFile(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  input.value = "";
  if (file) emit("import", file);
}
</script>

<template>
  <Teleport to="#sma-overlays"><ElDialog :model-value="Boolean(true)" :append-to-body="false" :title="title" class="sma-dialog mapping-batch-dialog" @close="$emit('close')">
<template #header><div class="panel-header facts-dialog-header">
        <div>
          <p class="panel-kicker">{{ labels.batchFormatHint }}</p>
          <h2 id="mapping-batch-dialog-title">{{ title }}</h2>
        </div>
      </div></template>
      <p>{{ labels.mappingBatchOperationsHint }}</p>
      <div class="facts-file-actions">
        <ConsoleActionButton tone="secondary" native-type="button" :disabled="savingFile" @click="$emit('download-template', 'json')">{{ labels.collectionFactsTemplateJson }}</ConsoleActionButton>
        <ConsoleActionButton tone="secondary" native-type="button" :disabled="savingFile" @click="$emit('download-template', 'xlsx')">{{ labels.collectionFactsTemplateXlsx }}</ConsoleActionButton>
        <ConsoleActionButton tone="secondary" native-type="button" :disabled="savingFile" @click="$emit('export', 'json')">{{ labels.collectionFactsExportJson }}</ConsoleActionButton>
        <ConsoleActionButton tone="secondary" native-type="button" :disabled="savingFile" @click="$emit('export', 'xlsx')">{{ labels.collectionFactsExportXlsx }}</ConsoleActionButton>
        <ConsoleActionButton tone="primary" native-type="button" :disabled="!enabled || busy || savingFile" @click="chooseFile">{{ labels.mappingBatchImport }}</ConsoleActionButton>
      </div>
      <input ref="fileInput" class="facts-file-input" type="file" accept=".json,application/json,.xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" @change="importFile" />
      <p v-if="error" class="warning">{{ labels.mappingBatchOperationFailed }} {{ /CONFLICT|PREVIEW_CHANGED/.test(error) ? labels.localConfigurationConflict : error }}</p>
      <section v-if="preview" class="mapping-import-preview">
        <h3>{{ labels.mappingBatchPreviewTitle }}</h3>
        <dl class="facts-preview-summary">
          <div><dt>{{ labels.mappingBatchCreated }}</dt><dd>{{ preview.createdKeys.length }}</dd></div>
          <div><dt>{{ labels.mappingBatchUpdated }}</dt><dd>{{ preview.updatedKeys.length }}</dd></div>
          <div><dt>{{ labels.mappingBatchUnchanged }}</dt><dd>{{ preview.unchangedKeys.length }}</dd></div>
          <div><dt>{{ labels.mappingBatchErrors }}</dt><dd>{{ preview.errors.length }}</dd></div>
        </dl>
        <div class="mapping-import-keys">
          <h4>{{ labels.mappingBatchCreated }}</h4>
          <ul><li v-for="key in preview.createdKeys" :key="key"><code>{{ key }}</code></li></ul>
          <h4>{{ labels.mappingBatchUpdated }}</h4>
          <ul><li v-for="key in preview.updatedKeys" :key="key"><code>{{ key }}</code></li></ul>
          <h4>{{ labels.mappingBatchUnchanged }}</h4>
          <ul><li v-for="key in preview.unchangedKeys" :key="key"><code>{{ key }}</code></li></ul>
        </div>
        <div v-if="preview.errors.length" class="warning">
          <p>{{ labels.mappingBatchPreviewErrors }}</p>
          <ul class="mapping-import-errors"><li v-for="item in preview.errors" :key="`${item.key}:${item.errorCode}`"><code>{{ item.key }}</code> · {{ item.errorCode }}</li></ul>
        </div>
        <div class="action-row facts-editor-actions">
          <ConsoleActionButton tone="primary" native-type="button" :disabled="!enabled || busy || preview.errors.length > 0" @click="$emit('apply')">{{ labels.mappingBatchApply }}</ConsoleActionButton>
        </div>
      </section>
      <div class="action-row facts-editor-actions"><ConsoleActionButton tone="secondary" native-type="button" :disabled="busy || savingFile" @click="$emit('close')">{{ labels.collectionFactsCancel }}</ConsoleActionButton></div>

</ElDialog></Teleport>
</template>

<style scoped>
.mapping-import-preview { margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--line); }
.mapping-import-preview h3 { margin: 0 0 12px; font-size: 15px; }
.mapping-import-keys { overflow-wrap: anywhere; }
.mapping-import-keys h4 { margin: 12px 0 4px; }
.mapping-import-errors { margin: 8px 0 0; padding-left: 20px; }
</style>
