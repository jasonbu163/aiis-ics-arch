<!-- 目标和映射共用已冻结的单次 POST 预览；取消或更改输入使令牌失效。 -->
<script setup lang="ts">
import { ConsoleActionButton } from "@aw-ui";
import { computed, onBeforeUnmount, ref, shallowRef, watch } from "vue";
import { localConfiguration } from "../../twin-facts/api/localConfiguration";
import type { TargetApiConfiguration } from "../../twin-facts/types";
import { httpMapping } from "../api";
import { useHttpMessages } from "../messages";
import type { PostPreview, PostResult, Scalar } from "../types";
import { describeError, jsonText, parameterLocation, readScalar, typeLabel } from "../ui";
import PostResultDetails from "./PostResultDetails.vue";
import PreviewSources from "./PreviewSources.vue";
import SmaDialog from "./SmaDialog.vue";

const props = defineProps<{ mappingId?: string | null; target?: TargetApiConfiguration | null; ioEnabled: boolean }>();
const emit = defineEmits<{ result: [id: string, result: PostResult] }>();
const open = defineModel<boolean>({ required: true });
const sending = defineModel<boolean>("sending", { default: false });
const ui = useHttpMessages();
const currentRevision = computed(() => localConfiguration.value?.revision ?? 0);
const preview = shallowRef<PostPreview | null>(null);
const result = shallowRef<PostResult | null>(null);
const values = ref<Record<string, string>>({});
const included = ref<Record<string, boolean>>({});
const busy = ref(false);
const stale = ref(false);
const error = ref("");
let generation = 0;

function cancelToken(token: string | null | undefined) {
  if (token) void httpMapping.cancel(token).catch(() => {
    // 界面已丢弃令牌；Rust 仍会核对有效期、修订和单次消费。
  });
}

function invalidate() {
  generation++;
  cancelToken(preview.value?.token);
  preview.value = null;
}

watch(open, shown => {
  if (!shown) invalidate();
}, { flush: "sync" });

watch(open, shown => {
  if (!shown) return;
  // 同一父组件更新先传 open 再传测试对象，表单在所有 props 就绪后初始化。
  invalidate();
  values.value = Object.fromEntries((props.target?.parameterSchema ?? []).map(parameter => [
    parameter.parameterKey, parameter.dataType === "boolean" ? "false" : "",
  ]));
  included.value = Object.fromEntries((props.target?.parameterSchema ?? []).map(parameter => [parameter.parameterKey, parameter.required]));
  result.value = null;
  stale.value = false;
  error.value = "";
  if (props.mappingId) void generate();
}, { flush: "post" });

watch([currentRevision, () => props.mappingId, () => props.target?.id, () => props.ioEnabled, values, included], () => {
  if (!open.value || sending.value || (!preview.value && !busy.value)) return;
  invalidate();
  stale.value = true;
  error.value = "";
}, { deep: true, flush: "sync" });

onBeforeUnmount(invalidate);

async function generate() {
  if (!open.value || busy.value || sending.value) return;
  invalidate();
  stale.value = false;
  error.value = "";
  result.value = null;
  const observed = generation;
  busy.value = true;
  try {
    let generated: PostPreview;
    if (props.target) {
      const fields: [string, Scalar][] = [];
      for (const parameter of props.target.parameterSchema) {
        const key = parameter.parameterKey;
        if (!parameter.required && !included.value[key]) continue;
        try {
          fields.push([key, readScalar(values.value[key] ?? "", parameter.dataType)]);
        } catch {
          throw new Error(`SMA_INPUT_SCALAR_INVALID:${key}`);
        }
      }
      generated = await httpMapping.previewTarget(props.target.id, currentRevision.value, Object.fromEntries(fields));
    } else if (props.mappingId) {
      generated = await httpMapping.previewMapping(props.mappingId, currentRevision.value);
    } else {
      return;
    }
    if (!open.value || observed !== generation || generated.revision !== currentRevision.value) {
      cancelToken(generated.token);
      return;
    }
    preview.value = generated;
  } catch (caught) {
    if (observed === generation) error.value = describeError(caught);
  } finally {
    busy.value = false;
  }
}

async function send() {
  const prepared = preview.value;
  if (!open.value || !prepared?.token || !prepared.request || sending.value || busy.value || !props.ioEnabled
      || prepared.revision !== currentRevision.value) return;
  const id = props.target?.id ?? props.mappingId;
  if (!id) return;
  const token = prepared.token;
  // 先移除界面令牌，防止同一预览被双击或重复提交。
  preview.value = { ...prepared, token: null };
  sending.value = true;
  error.value = "";
  try {
    const sent = await httpMapping.confirm(token);
    result.value = sent;
    emit("result", id, sent);
  } catch (caught) {
    error.value = describeError(caught);
    stale.value = true;
  } finally {
    sending.value = false;
  }
}
</script>

<template>
  <SmaDialog v-model="open" :title="ui.previewTitle" :error="error">
    <p v-if="stale" class="warning" role="status">{{ ui.stalePreview }}</p>
    <p v-if="busy" role="status">{{ ui.loading }}</p>
    <template v-if="!result">
      <p>{{ ui.previewHelp }}</p>
      <p v-if="!ioEnabled" class="hint">{{ ui.httpDisabled }}</p>
      <div v-if="target?.parameterSchema.length" class="http-form-grid">
        <div v-for="parameter in target.parameterSchema" :key="parameter.parameterKey" class="field">
          <label v-if="!parameter.required" class="http-checkbox">
            <input v-model="included[parameter.parameterKey]" type="checkbox" :disabled="sending">
            <span>{{ parameterLocation(ui, parameter.location) }} · {{ parameter.name }} · {{ ui.optional }}</span>
          </label>
          <label class="field">
            <span v-if="parameter.required">{{ parameterLocation(ui, parameter.location) }} · {{ parameter.name }} · {{ ui.required }}</span>
            <span>{{ typeLabel(ui, parameter.dataType) }}</span>
            <select v-if="parameter.dataType === 'boolean'" v-model="values[parameter.parameterKey]" :disabled="sending || !included[parameter.parameterKey]">
              <option value="true">true</option><option value="false">false</option>
            </select>
            <input v-else v-model="values[parameter.parameterKey]" :disabled="sending || !included[parameter.parameterKey]">
          </label>
        </div>
      </div>
      <template v-if="preview">
        <section v-if="preview.request" class="http-dialog-section">
          <div class="http-section-header"><h3>{{ ui.request }}</h3></div>
          <p class="http-request-line"><strong>{{ preview.request.method }}</strong> <code>{{ preview.request.url }}</code></p>
          <pre v-if="preview.request.headers.length" class="http-code">{{ preview.request.headers.map(([name, value]) => name + ': ' + value).join('\n') }}</pre>
          <pre v-if="preview.request.body != null" class="http-code">{{ jsonText(preview.request.body) }}</pre>
        </section>
        <PreviewSources :sources="preview.sources" :diagnostics="preview.diagnostics" />
      </template>
    </template>
    <PostResultDetails v-else :result="result" />
    <template #footer>
      <ConsoleActionButton @click="open = false">{{ result ? ui.close : ui.cancel }}</ConsoleActionButton>
      <ConsoleActionButton v-if="!result && !preview?.token && !sending" tone="primary" :loading="busy" @click="generate">
        {{ stale || preview ? ui.generatePreview : ui.preview }}
      </ConsoleActionButton>
      <ConsoleActionButton v-if="!result && (preview?.token || sending)" tone="primary"
        :loading="sending" :disabled="!preview?.token || !preview?.request || !ioEnabled" @click="send">{{ ui.sendOnce }}</ConsoleActionButton>
    </template>
  </SmaDialog>
</template>
