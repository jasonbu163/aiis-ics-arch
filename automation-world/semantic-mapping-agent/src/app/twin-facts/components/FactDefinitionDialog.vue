<!--
File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/components/FactDefinitionDialog.vue
Description: Module-private Fact Table definition editor dialog.
Main Features:
  - Presents the existing definition draft without owning contract or preview state
  - Emits explicit field patches, Preview, and one Cancel intent to FactsTablePanel
-->
<script setup lang="ts">
import type { LocaleMessages } from "../../../locales";
import type { CollectionFactDataType, CollectionFactKind } from "../types";

interface DefinitionDraft {
  originalName: string | null;
  name: string;
  factKind: CollectionFactKind;
  dataType: CollectionFactDataType;
}

const props = defineProps<{
  labels: LocaleMessages;
  contractVersion: string;
  draft: DefinitionDraft;
  factKinds: CollectionFactKind[];
  dataTypes: CollectionFactDataType[];
  busy: boolean;
  enabled: boolean;
  invalid: boolean;
}>();

const emit = defineEmits<{
  close: [];
  preview: [];
  "update-draft": [patch: Partial<DefinitionDraft>];
}>();

function updateName(event: Event) {
  emit("update-draft", { name: (event.target as HTMLInputElement).value });
}

function updateFactKind(event: Event) {
  emit("update-draft", { factKind: (event.target as HTMLSelectElement).value as CollectionFactKind });
}

function updateDataType(event: Event) {
  emit("update-draft", { dataType: (event.target as HTMLSelectElement).value as CollectionFactDataType });
}
</script>

<template>
  <div class="facts-dialog-backdrop" @click.self="$emit('close')">
    <section class="panel facts-dialog" role="dialog" aria-modal="true" aria-labelledby="facts-definition-dialog-title">
      <header class="panel-header facts-dialog-header">
        <div>
          <p class="panel-kicker">{{ props.contractVersion }}</p>
          <h2 id="facts-definition-dialog-title">{{ props.draft.originalName ? props.labels.collectionFactsEditDefinitionTitle : props.labels.collectionFactsNewDefinitionTitle }}</h2>
        </div>
      </header>
      <div class="form-grid">
        <label class="field"><span>{{ props.labels.collectionFactsName }}</span><input :value="props.draft.name" :disabled="props.busy" @input="updateName" /></label>
        <label class="field"><span>{{ props.labels.collectionFactsKind }}</span><select :value="props.draft.factKind" :disabled="props.busy" @change="updateFactKind"><option v-for="kind in props.factKinds" :key="kind" :value="kind">{{ kind }}</option></select></label>
        <label class="field"><span>{{ props.labels.collectionFactsDataType }}</span><select :value="props.draft.dataType" :disabled="props.busy" @change="updateDataType"><option v-for="dataType in props.dataTypes" :key="dataType" :value="dataType">{{ dataType }}</option></select></label>
      </div>
      <p v-if="props.invalid" class="warning">{{ props.labels.collectionFactsDefinitionInvalid }}</p>
      <div class="action-row facts-editor-actions"><button class="secondary-action" type="button" :disabled="props.busy" @click="$emit('close')">{{ props.labels.collectionFactsCancel }}</button><button class="primary-action" type="button" :disabled="!props.enabled || props.busy" @click="$emit('preview')">{{ props.labels.collectionFactsPreview }}</button></div>
    </section>
  </div>
</template>
