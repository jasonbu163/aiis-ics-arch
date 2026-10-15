<!--
File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/components/FactBatchOperationsDialog.vue
Description: Module-private Fact Table JSON/XLSX batch-operation dialog.
Main Features:
  - Emits definition-template, export, and selected-upload intentions without parsing business data
  - Keeps complete definition replacement visibly high risk and defaults it off
  - Allows definition import for an empty source while values wait for Applied definitions
  - Keeps one Cancel action while the parent owns generated files and import validation
-->
<script setup lang="ts">
import { ref } from "vue";

import type { LocaleMessages } from "../../../locales";
import type { CollectionFactFileFormat } from "../types";

type FileIntent = "definitions" | "values";

const props = defineProps<{
  labels: LocaleMessages;
  hasContract: boolean;
  hasAppliedDefinitions: boolean;
  contractBusy: boolean;
  valuesBusy: boolean;
  savingFile: boolean;
  enabled: boolean;
  replaceDefinitions: boolean;
  fileErrorText: string;
  exportError: boolean;
}>();

const emit = defineEmits<{
  close: [];
  "update:replace-definitions": [value: boolean];
  "download-definition-template": [format: CollectionFactFileFormat];
  "download-definition": [format: CollectionFactFileFormat];
  "export-values": [format: CollectionFactFileFormat];
  "import-file": [intent: FileIntent, file: File];
}>();

const fileInput = ref<HTMLInputElement | null>(null);
const fileIntent = ref<FileIntent | null>(null);

function chooseFile(intent: FileIntent) {
  fileIntent.value = intent;
  fileInput.value?.click();
}

function importFile(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  const intent = fileIntent.value;
  input.value = "";
  fileIntent.value = null;
  if (file && intent) emit("import-file", intent, file);
}
</script>

<template>
  <div class="facts-dialog-backdrop" @click.self="$emit('close')">
    <section class="panel facts-dialog facts-batch-dialog" role="dialog" aria-modal="true" aria-labelledby="facts-batch-dialog-title">
      <header class="panel-header facts-dialog-header">
        <div>
          <p class="panel-kicker">{{ props.labels.collectionFactsFileExchangeKicker }}</p>
          <h2 id="facts-batch-dialog-title">{{ props.labels.collectionFactsBatchOperationsTitle }}</h2>
        </div>
      </header>
      <p>{{ props.labels.collectionFactsBatchOperationsHint }}</p>
      <div class="facts-file-grid">
        <article>
          <h3>{{ props.labels.collectionFactsDefinitionFile }}</h3>
          <div class="facts-file-actions">
            <button class="secondary-action" type="button" :disabled="props.savingFile" @click="$emit('download-definition-template', 'json')">{{ props.labels.collectionFactsTemplateJson }}</button>
            <button class="secondary-action" type="button" :disabled="props.savingFile" @click="$emit('download-definition-template', 'xlsx')">{{ props.labels.collectionFactsTemplateXlsx }}</button>
            <button class="secondary-action" type="button" :disabled="!props.hasContract || props.savingFile" @click="$emit('download-definition', 'json')">{{ props.labels.collectionFactsExportJson }}</button>
            <button class="secondary-action" type="button" :disabled="!props.hasContract || props.savingFile" @click="$emit('download-definition', 'xlsx')">{{ props.labels.collectionFactsExportXlsx }}</button>
            <button class="primary-action" type="button" :disabled="!props.enabled || !props.hasContract || props.contractBusy || props.savingFile" @click="chooseFile('definitions')">{{ props.labels.collectionFactsImportDefinition }}</button>
          </div>
          <p v-if="!props.hasContract" class="warning facts-replace-risk">{{ props.labels.collectionFactsLoadContractFirst }}</p>
          <label class="check-field facts-replace-toggle">
            <input :checked="props.replaceDefinitions" type="checkbox" :disabled="!props.hasContract || props.contractBusy || props.savingFile" @change="$emit('update:replace-definitions', ($event.target as HTMLInputElement).checked)" />
            <span>{{ props.labels.collectionFactsReplaceDefinitions }}</span>
          </label>
          <p class="warning facts-replace-risk">{{ props.labels.collectionFactsReplaceDefinitionsRisk }}</p>
        </article>
        <article>
          <h3>{{ props.labels.collectionFactsValueFile }}</h3>
          <div class="facts-file-actions">
            <button class="secondary-action" type="button" :disabled="!props.hasContract || props.savingFile" :aria-busy="props.savingFile" @click="$emit('export-values', 'json')">{{ props.savingFile ? props.labels.loading : props.labels.collectionFactsExportJson }}</button>
            <button class="secondary-action" type="button" :disabled="!props.hasContract || props.savingFile" :aria-busy="props.savingFile" @click="$emit('export-values', 'xlsx')">{{ props.savingFile ? props.labels.loading : props.labels.collectionFactsExportXlsx }}</button>
            <button class="primary-action" type="button" :disabled="!props.enabled || !props.hasAppliedDefinitions || props.valuesBusy || props.savingFile" @click="chooseFile('values')">{{ props.labels.collectionFactsImportValues }}</button>
          </div>
        </article>
      </div>
      <input ref="fileInput" class="facts-file-input" type="file" accept=".json,application/json,.xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" @change="importFile" />
      <p v-if="props.fileErrorText" class="warning">{{ props.fileErrorText }}</p>
      <p v-if="props.exportError" class="warning">{{ props.labels.collectionFactsOperationFailed }}</p>
      <div class="action-row facts-editor-actions"><button class="secondary-action" type="button" :disabled="props.contractBusy || props.valuesBusy || props.savingFile" @click="$emit('close')">{{ props.labels.collectionFactsCancel }}</button></div>
    </section>
  </div>
</template>
