<!-- POST 结果区分 HTTP 成功、业务回执、失败、阻断和未知。 -->
<script setup lang="ts">
import { StatusCapsule } from "@aw-ui";
import { formatBusinessTime } from "../../../console/time";
import { useHttpMessages } from "../messages";
import type { PostResult } from "../types";
import { jsonText, postStatusLabel, postStatusTone } from "../ui";
import PreviewSources from "./PreviewSources.vue";

defineProps<{ result: PostResult }>();
const ui = useHttpMessages();
</script>

<template>
  <div class="http-stack">
    <div class="http-inline">
      <StatusCapsule :label="postStatusLabel(ui, result.status)" :tone="postStatusTone(result.status)" />
      <span v-if="result.httpStatus !== null">{{ ui.httpStatus }} {{ result.httpStatus }}</span>
      <code>{{ result.errorCode }}</code>
    </div>
    <p v-if="result.status === 'unknown'" class="warning" role="status">{{ ui.resultUnknownHelp }}</p>
    <dl class="http-runtime-metrics">
      <div><dt>{{ ui.runId }}</dt><dd>{{ result.runId }}</dd></div>
      <div><dt>{{ ui.finishedAt }}</dt><dd>{{ formatBusinessTime(result.finishedAt) }}</dd></div>
    </dl>
    <PreviewSources :sources="result.sources" :diagnostics="result.diagnostics" />
    <details v-if="result.response != null" class="http-dialog-section">
      <summary>{{ ui.rawResponse }}</summary><pre class="http-code">{{ jsonText(result.response) }}</pre>
    </details>
  </div>
</template>
