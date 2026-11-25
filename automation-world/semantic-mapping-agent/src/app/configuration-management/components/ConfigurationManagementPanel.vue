<!-- SMA 配置管理。按依赖导出，预览并确认同一 SQLite revision 的导入。 -->
<script setup lang="ts">
import { computed, onMounted, ref, shallowRef } from "vue";
import { ElCheckbox, ElDialog } from "element-plus";
import { ConsoleActionButton, ConsoleCard, StatusCapsule, type CardHeaderStatus } from "@aw-ui";
import { isTauriRuntime } from "../../tauri";
import { saveCollectionFactFile } from "../../twin-facts/api";
import { applyConfiguration, exportConfiguration, loadLocalConfiguration, localConfiguration, previewConfiguration, type LocalImportPreview } from "../../twin-facts/api/localConfiguration";
import type { MappingConfigurationFileFormat } from "../../twin-facts/utils/mappingConfigurationFiles";
import type { LocaleMessages } from "../../../locales";
import { formatBusinessTime } from "../../../console/time";
import { useTableWidths, vTableWidths } from "../../../console/tableWidths";
import { ConfigurationFileError, createConfigurationFile, listExchangeItems, parseConfigurationFile, selectExchangeConfiguration, type ExchangeItem, type ParsedConfigurationFile } from "../utils/configurationFiles";

const props = defineProps<{ labels: LocaleMessages }>();
const emit = defineEmits<{ changed: [] }>();
const text = computed(() => props.labels.configurationExchange);
const enabled = isTauriRuntime();
const operation = ref<"load" | "export" | "read" | "apply" | null>(null);
const selected = shallowRef(new Set<string>());
const includeConnection = ref(false);
const exported = ref(false);
const imported = ref(false);
const exportError = shallowRef<unknown>(null);
const importError = shallowRef<unknown>(null);
const fileInput = ref<HTMLInputElement | null>(null);
const reviewedFile = shallowRef<File | null>(null);
const importOpen = ref(false);
const confirmed = ref(false);
const parsed = shallowRef<ParsedConfigurationFile | null>(null);
const preview = shallowRef<LocalImportPreview | null>(null);
const restore = computed(() => parsed.value?.intent.kind === "restore");
const stale = computed(() => preview.value !== null && preview.value.expectedRevision !== localConfiguration.value?.revision);
const canApply = computed(() => enabled && !operation.value && !stale.value && Boolean(preview.value?.token)
  && preview.value?.errors.length === 0 && (!restore.value || confirmed.value));
const current = computed(() => localConfiguration.value);
const inventory = computed(() => current.value ? listExchangeItems(current.value.document) : []);
const exportPlan = computed(() => {
  try {
    return { selection: current.value ? selectExchangeConfiguration(current.value.document, selected.value, includeConnection.value) : null, error: null };
  } catch (error) {
    return { selection: null, error };
  }
});
const selection = computed(() => exportPlan.value.selection);
const canExport = computed(() => enabled && !operation.value && Boolean(selection.value && Object.keys(selection.value.bundle.document).length > 0 && !selection.value.missing.length));
const canBackup = computed(() => enabled && !operation.value && Boolean(current.value) && includeConnection.value);
const groups = computed(() => (Object.keys(text.value.resources) as ExchangeItem["resource"][]).map(resource => ({
  resource, items: inventory.value.filter(item => item.resource === resource),
})).filter(group => group.items.length));
const headerStatuses = computed<CardHeaderStatus[]>(() => current.value ? [{
  id: "revision", label: `${text.value.revision} ${current.value.revision}`, tone: "neutral",
}] : []);

type Status = keyof LocaleMessages["configurationExchange"]["change"];
type ErrorKey = keyof LocaleMessages["configurationExchange"]["error"];
interface PreviewRow { key: string; status: Status; location: string; details?: string }
const widths = useTableWidths("configuration-import", [
  { id: "status", width: 135 }, { id: "key", width: 265 },
  { id: "location", width: 200 }, { id: "detail", width: 245 },
]);
const statusTones = {
  created: "success", updated: "neutral", unchanged: "neutral", deleted: "warning",
  conflict: "danger", missing: "warning", invalid: "danger",
} as const;

function classify(code: string): Status {
  if (/REFERENCE_MISSING|NOT_FOUND/.test(code)) return "missing";
  if (/DUPLICATE|CONFLICT|IMMUTABLE/.test(code)) return "conflict";
  return "invalid";
}

const displayRows = computed<PreviewRow[]>(() => {
  const result = preview.value;
  if (!result) return [];
  const locations = parsed.value?.locations;
  return [
    ...([
      ["created", result.createdKeys], ["updated", result.updatedKeys],
      ["unchanged", result.unchangedKeys], ["deleted", result.deletedKeys],
    ] as const).flatMap(([status, keys]) => keys.map(key => ({ key, status, location: locations?.get(key) ?? "" }))),
    ...result.errors.map(({ key, errorCode }) => {
      const [code, ...suffix] = errorCode.split(":");
      const errorIdentity = suffix.join(":");
      const exact = locations?.get(key) ?? locations?.get(errorIdentity);
      const firstDetail = suffix[0];
      const partial = Array.from(locations?.entries() ?? []).find(([id]) =>
        errorIdentity.startsWith(id + ":") || id.endsWith(":" + errorIdentity)
        || Boolean(firstDetail && id.endsWith(":" + firstDetail)));
      return { key, status: classify(code), location: exact ?? partial?.[1] ?? "", details: code };
    }),
  ];
});

function userError(value: unknown): { label: string; detail: string } {
  if (value instanceof ConfigurationFileError) {
    const label = text.value.error[value.code as ErrorKey] ?? text.value.error.invalid;
    return { label, detail: value.location };
  }
  const raw = (value instanceof Error ? value.message : String(value)).replace(/^Error:\s*/, "").split(":")[0];
  const code = /^[A-Z0-9_]+$/.test(raw) ? raw : "";
  const key: ErrorKey = /PREVIEW_CHANGED|PREVIEW_REQUIRED|^SMA_CONFIGURATION_CONFLICT$/.test(code) ? "stale"
    : /RUNTIME_BUSY/.test(code) ? "busy"
    : /EXPORT_CREDENTIALS/.test(code) ? "backupCredentials"
    : /REFERENCE_MISSING/.test(code) ? "missingReference"
    : /CONFLICT|DUPLICATE/.test(code) ? "conflict"
    : /LIMIT_EXCEEDED/.test(code) ? "tooLarge"
    : /UNSUPPORTED/.test(code) ? "unsupportedVersion"
    : "invalid";
  return { label: text.value.error[key], detail: code };
}

function toggle(item: ExchangeItem, checked: boolean) {
  const keys = new Set(selected.value);
  if (checked) keys.add(item.selectionKey);
  else keys.delete(item.selectionKey);
  selected.value = keys;
  exported.value = false;
}

function selectAll() {
  selected.value = new Set(inventory.value.map(item => item.selectionKey));
  exported.value = false;
}

function clearSelection() {
  selected.value = new Set();
  includeConnection.value = false;
  exported.value = false;
}

async function saveFile(format: MappingConfigurationFileFormat | "backup") {
  const bundle = selection.value?.bundle;
  if (format === "backup" ? !canBackup.value : (!canExport.value || !bundle)) return;
  operation.value = "export";
  exportError.value = null;
  exported.value = false;
  try {
    const file = format === "backup" ? {
      fileName: "sma-configuration-backup.json",
      mimeType: "application/json;charset=utf-8",
      contents: new TextEncoder().encode(await exportConfiguration()),
    } : createConfigurationFile(format, bundle!);
    exported.value = await saveCollectionFactFile(file);
  } catch (error) {
    exportError.value = error;
  } finally {
    operation.value = null;
  }
}

async function reviewFile(file: File) {
  if (!enabled || operation.value) return;
  reviewedFile.value = file;
  importOpen.value = true;
  imported.value = false;
  confirmed.value = false;
  importError.value = null;
  parsed.value = null;
  preview.value = null;
  operation.value = "read";
  try {
    const snapshot = await loadLocalConfiguration();
    const decoded = await parseConfigurationFile(file, snapshot.document);
    if (!importOpen.value) return;
    parsed.value = decoded;
    const result = await previewConfiguration(decoded.intent, snapshot.revision);
    if (importOpen.value) preview.value = result;
  } catch (error) {
    if (importOpen.value) importError.value = error;
  } finally {
    operation.value = null;
  }
}

function chooseFile(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  input.value = "";
  if (file) void reviewFile(file);
}

function closeImport() {
  importOpen.value = false;
  reviewedFile.value = null;
  parsed.value = null;
  preview.value = null;
  confirmed.value = false;
  importError.value = null;
}

async function saveImport() {
  const result = preview.value;
  const intent = parsed.value?.intent;
  if (!canApply.value || !result || !intent) return;
  const before = JSON.stringify(current.value?.document.connection);
  operation.value = "apply";
  importError.value = null;
  try {
    const applied = await applyConfiguration(intent, result, true);
    if (before !== JSON.stringify(applied.document.connection)) window.dispatchEvent(new Event("sma-backend-connection-changed"));
    imported.value = true;
    closeImport();
    emit("changed");
  } catch (error) {
    if (importOpen.value) {
      importError.value = error;
      if (userError(error).label === text.value.error.stale) preview.value = null;
    }
  } finally {
    operation.value = null;
  }
}

onMounted(async () => {
  if (!enabled || current.value) return;
  operation.value = "load";
  try { await loadLocalConfiguration(); }
  catch (error) { exportError.value = error; }
  finally { operation.value = null; }
});
</script>

<template>
  <div class="configuration-management">
    <ConsoleCard :title="text.exportTitle" :help="text.exportHelp" :help-label="text.exportTitle + labels.cardHelpSuffix"
      :header-statuses="headerStatuses" help-append-to="#sma-overlays">
      <template #actions>
        <ConsoleActionButton tone="secondary" :disabled="!canExport" @click="saveFile('json')">{{ text.exportJson }}</ConsoleActionButton>
        <ConsoleActionButton tone="secondary" :disabled="!canExport" @click="saveFile('xlsx')">{{ text.exportXlsx }}</ConsoleActionButton>
      </template>
      <p v-if="!enabled" class="hint" role="status">{{ text.desktopRequired }}</p>
      <p v-else-if="operation === 'load'" class="hint" role="status">{{ labels.loading }}</p>
      <template v-else-if="current">
        <p class="configuration-saved">{{ text.savedAt }} <strong>{{ formatBusinessTime(current.updatedAt) }}</strong></p>
        <div class="configuration-toolbar">
          <ElCheckbox v-model="includeConnection" :disabled="Boolean(operation)" @change="exported = false">{{ text.includeConnection }}</ElCheckbox>
          <div class="action-row">
            <ConsoleActionButton tone="secondary" :disabled="Boolean(operation) || !inventory.length" @click="selectAll">{{ text.chooseAll }}</ConsoleActionButton>
            <ConsoleActionButton tone="secondary" :disabled="Boolean(operation) || (!selected.size && !includeConnection)" @click="clearSelection">{{ text.clearSelection }}</ConsoleActionButton>
          </div>
        </div>
        <p v-if="!inventory.length" class="hint">{{ text.inventoryEmpty }}</p>
        <div v-else class="configuration-groups">
          <details v-for="group in groups" :key="group.resource">
            <summary>
              {{ text.resources[group.resource] }}
              <span>{{ group.items.filter(item => selected.has(item.selectionKey)).length }} / {{ group.items.length }}</span>
            </summary>
            <div class="configuration-options">
              <ElCheckbox v-for="item in group.items" :key="item.selectionKey" :model-value="selected.has(item.selectionKey)"
                :disabled="Boolean(operation)" @change="toggle(item, $event === true)">
                {{ item.name }} <code>{{ item.parent ? item.parent + " / " : "" }}{{ item.key }}</code>
              </ElCheckbox>
            </div>
          </details>
        </div>
        <p v-if="!selected.size && !includeConnection" class="hint">{{ text.selectionEmpty }}</p>
        <details v-if="selection?.dependencies.length" class="configuration-review-details">
          <summary>{{ text.autoIncluded }} ({{ selection.dependencies.length }})</summary>
          <ul><li v-for="item in selection.dependencies" :key="item.selectionKey">{{ text.resources[item.resource] }} · <code>{{ item.parent ? item.parent + " / " : "" }}{{ item.key }}</code></li></ul>
        </details>
        <div v-if="selection?.missing.length" class="warning" role="alert">
          <p>{{ text.missingDependencies }}</p>
          <ul><li v-for="key in selection.missing" :key="key"><code>{{ key }}</code></li></ul>
        </div>
        <details v-if="selection?.redactions.length" class="configuration-review-details" open>
          <summary>{{ text.redactions }} ({{ selection.redactions.length }})</summary>
          <p class="hint">{{ text.redactionHelp }}</p>
          <ul><li v-for="key in selection.redactions" :key="key"><code>{{ key }}</code></li></ul>
        </details>
        <p class="hint">{{ text.backupHelp }}</p>
        <ConsoleActionButton tone="secondary" :disabled="!canBackup" @click="saveFile('backup')">{{ text.exportLegacy }}</ConsoleActionButton>
      </template>
      <p v-if="operation === 'export'" class="hint" role="status">{{ text.exportBusy }}</p>
      <p v-if="exported" class="hint" role="status">{{ text.exported }}</p>
      <p v-if="exportError || exportPlan.error" class="warning" role="alert">{{ userError(exportError || exportPlan.error).label }} <code>{{ userError(exportError || exportPlan.error).detail }}</code></p>
    </ConsoleCard>

    <ConsoleCard :title="text.importTitle">
      <template #actions>
        <ConsoleActionButton tone="secondary" :disabled="!enabled || Boolean(operation)" @click="fileInput?.click()">{{ text.chooseFile }}</ConsoleActionButton>
      </template>
      <p class="hint">{{ text.importHelp }}</p>
      <p class="hint">{{ text.legacyHelp }}</p>
      <input ref="fileInput" class="facts-file-input" type="file" accept=".json,.xlsx" :disabled="!enabled || Boolean(operation)" @change="chooseFile" />
      <p v-if="imported" class="hint" role="status">{{ text.imported }}</p>
    </ConsoleCard>
  </div>

  <Teleport to="#sma-overlays">
    <ElDialog v-model="importOpen" class="sma-dialog standard-form-dialog compact-form-dialog configuration-import-dialog"
      :append-to-body="false" :close-on-click-modal="true" :title="text.previewTitle" @close="closeImport">
      <template #header="{ titleId, titleClass }"><h2 :id="titleId" :class="titleClass">{{ text.previewTitle }}</h2></template>
      <p v-if="reviewedFile" class="configuration-file"><strong>{{ reviewedFile.name }}</strong></p>
      <p v-if="operation === 'read'" class="hint" role="status">{{ text.readBusy }}</p>
      <p v-if="operation === 'apply'" class="hint" role="status">{{ text.saveBusy }}</p>
      <p v-if="stale" class="warning" role="alert">{{ text.error.stale }}</p>
      <p v-if="importError" class="warning" role="alert">{{ userError(importError).label }} <code>{{ userError(importError).detail }}</code></p>
      <p v-if="restore" class="warning">{{ text.restoreWarning }}</p>
      <details v-if="parsed?.redactions.length" class="configuration-review-details" open>
        <summary>{{ text.redactions }} ({{ parsed.redactions.length }})</summary>
        <p class="hint">{{ text.redactionHelp }}</p>
        <ul><li v-for="key in parsed.redactions" :key="key"><code>{{ key }}</code></li></ul>
      </details>
      <div v-if="preview && displayRows.length" class="configuration-toolbar">
        <p class="configuration-saved">{{ text.revision }} <strong>{{ preview.expectedRevision }}</strong></p>
        <ConsoleActionButton tone="secondary" :title="text.resetWidthsHint" @click="widths.reset()">{{ text.resetWidths }}</ConsoleActionButton>
      </div>
      <div v-if="displayRows.length" class="table-scroll configuration-preview-table">
        <table v-table-widths="[widths, text.resizeColumn]">
          <thead><tr><th v-for="caption in text.columns" :key="caption" scope="col">{{ caption }}</th></tr></thead>
          <tbody><tr v-for="(item, index) in displayRows" :key="`${item.status}:${item.key}:${index}`">
            <td><StatusCapsule :tone="statusTones[item.status]" :label="text.change[item.status]" /></td>
            <td><code>{{ item.key }}</code></td>
            <td><code>{{ item.location || "—" }}</code></td>
            <td><code>{{ item.details || "—" }}</code></td>
          </tr></tbody>
        </table>
      </div>
      <p v-else-if="preview" class="hint">{{ text.previewEmpty }}</p>
      <ElCheckbox v-if="restore && preview?.token" v-model="confirmed" :disabled="Boolean(operation) || stale">{{ text.restoreConfirmation }}</ElCheckbox>
      <template #footer>
        <div class="action-row configuration-dialog-actions">
          <ConsoleActionButton tone="secondary" @click="closeImport">{{ text.cancel }}</ConsoleActionButton>
          <ConsoleActionButton v-if="reviewedFile && (stale || importError)" tone="secondary" :disabled="Boolean(operation)"
            @click="reviewFile(reviewedFile)">{{ text.previewAgain }}</ConsoleActionButton>
          <ConsoleActionButton tone="primary" :disabled="!canApply" @click="saveImport">{{ restore ? text.applyRestore : text.applyMerge }}</ConsoleActionButton>
        </div>
      </template>
    </ElDialog>
  </Teleport>
</template>

<style>
.configuration-management { display: grid; gap: 14px; min-width: 0; }
.configuration-toolbar { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin: 8px 0; }
.configuration-saved { margin: 0; color: var(--agent-text-muted); }
.configuration-saved strong { color: var(--agent-text); margin-inline-start: 6px; }
.configuration-groups { display: grid; gap: 8px; grid-template-columns: repeat(auto-fit, minmax(min(100%, 260px), 1fr)); align-items: start; }
.configuration-groups details, .configuration-review-details { border: 1px solid var(--agent-border); border-radius: var(--agent-control-radius); padding: 8px 12px; overflow-wrap: anywhere; }
.configuration-groups summary, .configuration-review-details summary { cursor: pointer; }
.configuration-groups summary span { margin-inline-start: 8px; color: var(--agent-text-muted); }
.configuration-review-details { margin-top: 8px; max-height: 180px; overflow: auto; }
.configuration-options { display: grid; gap: 3px; max-height: 210px; overflow: auto; margin-top: 6px; }
.configuration-options .el-checkbox { height: auto; min-height: 28px; margin-inline-end: 0; white-space: normal; }
.configuration-options code { color: var(--agent-text-muted); }
.configuration-file { overflow-wrap: anywhere; margin-top: 0; }
.sma-overlays .configuration-import-dialog { display: flex; flex-direction: column; overflow: hidden; }
.configuration-import-dialog .el-dialog__header, .configuration-import-dialog .el-dialog__footer { flex: 0 0 auto; }
.configuration-import-dialog .el-dialog__body { min-height: 0; overflow: auto; }
.configuration-dialog-actions { justify-content: flex-end; flex-wrap: wrap; }
</style>
