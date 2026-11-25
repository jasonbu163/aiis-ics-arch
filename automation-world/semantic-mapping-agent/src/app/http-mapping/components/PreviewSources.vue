<!-- 预览与执行详情共用各 GET 来源固定快照及字段诊断展示。 -->
<script setup lang="ts">
import { formatBusinessTime } from "../../../console/time";
import { useHttpMessages } from "../messages";
import type { FieldDiagnostic, PreviewSource } from "../types";
import PointValuesTable from "./PointValuesTable.vue";

defineProps<{ sources: PreviewSource[]; diagnostics: FieldDiagnostic[] }>();
const ui = useHttpMessages();
</script>

<template>
  <section v-if="sources.length" class="http-dialog-section">
    <div class="http-section-header"><h3>{{ ui.factSources }}</h3></div>
    <div class="http-detail-list">
      <details v-for="source in sources" :key="source.sourceKey">
        <summary>
          <strong>{{ source.sourceKey }}</strong> · {{ ui.snapshot }} {{ source.version ?? ui.missing }}
          · {{ ui.collectedAt }} {{ formatBusinessTime(source.collectedAt) }}
        </summary>
        <PointValuesTable :values="source.points" table-id="post-source-points" />
      </details>
    </div>
    <p class="hint">{{ ui.snapshotHelp }}</p>
  </section>
  <section v-if="diagnostics.length" class="http-dialog-section">
    <div class="http-section-header"><h3>{{ ui.diagnostic }}</h3></div>
    <ul>
      <li v-for="diagnostic in diagnostics" :key="`${diagnostic.parameterKey}:${diagnostic.errorCode}`">
        <strong>{{ diagnostic.parameterKey }}</strong> · {{ diagnostic.errorCode }}
      </li>
    </ul>
  </section>
</template>
