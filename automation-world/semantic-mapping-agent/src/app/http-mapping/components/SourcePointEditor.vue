<!-- 源点位编辑保留稳定 ID、取值路径与显式的数组选择。 -->
<script setup lang="ts">
import { ConsoleActionButton } from "@aw-ui";
import { useHttpMessages } from "../messages";
import { scalarTypes, typeLabel } from "../ui";
import type { SourcePointDraft } from "../sourceDraft";

defineProps<{ point: SourcePointDraft; expanded: boolean }>();
const emit = defineEmits<{ remove: [] }>();
const ui = useHttpMessages();
</script>

<template>
  <details :open="expanded">
    <summary>{{ point.name || point.pointKey || ui.editPoint }} <code v-if="point.pointKey">{{ point.pointKey }}</code></summary>
    <div class="http-form-grid">
      <label class="field"><span>{{ ui.key }}</span><input v-model.trim="point.pointKey" required></label>
      <label class="field"><span>{{ ui.name }}</span><input v-model.trim="point.name" required></label>
      <label class="field"><span>{{ ui.kind }}</span><select v-model="point.dataType">
        <option v-for="type in scalarTypes" :key="type" :value="type">{{ typeLabel(ui, type) }}</option>
      </select></label>
      <label class="field"><span>{{ ui.pointPath }}</span><input v-model.trim="point.path"></label>
    </div>
    <details class="http-dialog-section" :open="point.selectById || undefined">
      <summary>{{ ui.advanced }}</summary>
      <p class="hint">{{ ui.arrayHelp }}</p>
      <div class="http-form-grid">
        <label class="http-checkbox http-wide"><input v-model="point.selectById" type="checkbox"><span>{{ ui.selectorEnabled }}</span></label>
        <template v-if="point.selectById">
          <label class="field"><span>{{ ui.selectorArray }}</span><input v-model.trim="point.selectorArray"></label>
          <label class="field"><span>{{ ui.selectorKey }}</span><input v-model.trim="point.selectorKey"></label>
          <label class="field"><span>{{ ui.selectorValue }}</span><input v-model="point.selectorValue" required></label>
        </template>
        <label class="field"><span>{{ ui.qualityPath }}</span><input v-model.trim="point.qualityPath"></label>
        <label class="field"><span>{{ ui.observedAtPath }}</span><input v-model.trim="point.observedAtPath"></label>
        <label class="field"><span>{{ ui.sampleIdPath }}</span><input v-model.trim="point.sampleIdPath"></label>
        <label class="field"><span>{{ ui.acceptedQuality }}</span><input v-model.trim="point.acceptedQuality"></label>
      </div>
    </details>
    <ConsoleActionButton size="small" tone="danger" class="http-point-remove" @click="emit('remove')">{{ ui.remove }}</ConsoleActionButton>
  </details>
</template>
