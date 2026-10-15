<!--
File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/components/FactValueDialog.vue
Description: Module-private Fact Table value editor dialog.
Main Features:
  - Presents one existing fact value, SQL NULL choice, and a type-specific read-only format example
  - Emits field patches, Save, and one Cancel intent to FactsTablePanel
-->
<script setup lang="ts">
import type { LocaleMessages } from "../../../locales";
import type { CollectionFactDataType } from "../types";

interface ValueDraft {
  name: string;
  dataType: CollectionFactDataType;
  value: string;
  isNull: boolean;
}

const VALUE_EXAMPLE_KEYS: Record<CollectionFactDataType, keyof LocaleMessages> = {
  string: "collectionFactsValueExampleString",
  integer: "collectionFactsValueExampleInteger",
  number: "collectionFactsValueExampleNumber",
  boolean: "collectionFactsValueExampleBoolean",
  datetime: "collectionFactsValueExampleDatetime",
};

const props = defineProps<{
  labels: LocaleMessages;
  draft: ValueDraft;
  busy: boolean;
  enabled: boolean;
  invalid: boolean;
}>();

const emit = defineEmits<{
  close: [];
  save: [];
  "update-draft": [patch: Partial<ValueDraft>];
}>();

function updateValue(event: Event) {
  emit("update-draft", { value: (event.target as HTMLInputElement).value });
}

function updateNull(event: Event) {
  emit("update-draft", { isNull: (event.target as HTMLInputElement).checked });
}
</script>

<template>
  <div class="facts-dialog-backdrop" @click.self="$emit('close')">
    <section class="panel facts-dialog facts-value-dialog" role="dialog" aria-modal="true" aria-labelledby="facts-value-dialog-title">
      <header class="panel-header facts-dialog-header">
        <div>
          <p class="panel-kicker"><code>{{ props.draft.name }}</code> · {{ props.draft.dataType }}</p>
          <h2 id="facts-value-dialog-title">{{ props.labels.collectionFactsEditValueTitle }}</h2>
        </div>
      </header>
      <label class="field">
        <span>{{ props.labels.collectionFactsValue }}</span>
        <input :value="props.draft.value" :disabled="props.busy || props.draft.isNull" @input="updateValue" />
        <small>{{ props.labels[VALUE_EXAMPLE_KEYS[props.draft.dataType]] }}</small>
      </label>
      <label class="check-field"><input :checked="props.draft.isNull" type="checkbox" :disabled="props.busy" @change="updateNull" /><span>{{ props.labels.collectionFactsSetNull }}</span></label>
      <p v-if="props.invalid" class="warning">{{ props.labels.collectionFactsValueInvalid }}</p>
      <div class="action-row facts-editor-actions"><button class="secondary-action" type="button" :disabled="props.busy" @click="$emit('close')">{{ props.labels.collectionFactsCancel }}</button><button class="primary-action" type="button" :disabled="!props.enabled || props.busy" @click="$emit('save')">{{ props.labels.collectionFactsSaveValue }}</button></div>
    </section>
  </div>
</template>
