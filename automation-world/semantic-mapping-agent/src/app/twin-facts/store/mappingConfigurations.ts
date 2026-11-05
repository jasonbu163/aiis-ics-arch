/** 本地映射CRUD、离线来源身份与草稿/已保存纯预览。 */
import { computed, ref } from "vue";
import { changeConfiguration, loadLocalConfiguration, localConfiguration, currentRevision, previewSavedMapping } from "../api/localConfiguration";

import {
  applyMappingConfigurationImportInBackend,
  createMappingConfigurationInBackend,
  deleteMappingConfigurationInBackend,
  listCollectionFactsFromBackend,
  previewMappingConfigurationImportInBackend,
  runMappingManualOnce,
  savedBackendBaseUrl,
  updateMappingConfigurationInBackend,
} from "../api";
import type {
  BackendCollectionFactRecord,
  ConfigurationImportPreview,
  MappingConfiguration,
  MappingConfigurationBinding,
  MappingConfigurationInput,
  MappingManualRunSummary,
  MappingValueRuleConfiguration,
  TargetApiConfiguration,
} from "../types";

export interface MappingConfigurationDraft {
  mappingKey: string;
  name: string;
  targetApiKey: string;
  bindings: Record<string, MappingConfigurationBinding>;
  intervalMs: number;
  enabled: boolean;
}

export interface LocalMappingConfigurationDraft {
  localId: string;
  draft: MappingConfigurationDraft;
}

function emptyDraft(): MappingConfigurationDraft {
  return {
    mappingKey: "",
    name: "",
    targetApiKey: "",
    bindings: {},
    intervalMs: 1000,
    enabled: true,
  };
}

function cloneBindings(bindings: Record<string, MappingConfigurationBinding>) {
  return Object.fromEntries(Object.entries(bindings).map(([path, binding]) => [path, { ...binding }]));
}

function normalizeBindings(
  bindings: Record<string, MappingConfigurationBinding>,
  legacySourceKey: string | null,
) {
  return Object.fromEntries(Object.entries(bindings).map(([path, binding]) => [path, {
    ...binding,
    sourceKey: binding.kind === "fact" ? binding.sourceKey ?? legacySourceKey : null,
  }]));
}

function cloneDraft(draft: MappingConfigurationDraft): MappingConfigurationDraft {
  return { ...draft, bindings: cloneBindings(draft.bindings) };
}

function draftFromConfiguration(mapping: MappingConfiguration): MappingConfigurationDraft {
  return {
    mappingKey: mapping.mappingKey,
    name: mapping.name,
    targetApiKey: mapping.targetApiKey,
    bindings: normalizeBindings(mapping.bindings, mapping.sourceKey),
    intervalMs: mapping.intervalMs,
    enabled: mapping.enabled,
  };
}

function draftFromTargetApi(targetApi: TargetApiConfiguration): MappingConfigurationDraft {
  return {
    ...emptyDraft(),
    mappingKey: `mapping-${targetApi.apiKey}`.slice(0, 100),
    name: targetApi.name,
    targetApiKey: targetApi.apiKey,
    bindings: Object.fromEntries(targetApi.parameterSchema.map((parameter) => [parameter.parameterKey, {
      kind: "fact",
      value: null,
      sourceKey: null,
      factName: null,
      valueRuleKey: null,
    }])),
  };
}

function validateDraft(draft: MappingConfigurationDraft): MappingConfigurationInput {
  const mappingKey = draft.mappingKey.trim();
  const name = draft.name.trim();
  if (!mappingKey || !name || !draft.targetApiKey || draft.intervalMs < 1) {
    throw new Error("MAPPING_CONFIGURATION_REQUIRED");
  }
  const bindings: Record<string, MappingConfigurationBinding> = Object.fromEntries(Object.entries(draft.bindings).map(([path, binding]) => {
    if (binding.kind === "constant") {
      return [path, { ...binding, sourceKey: null, factName: null }];
    }
    const sourceKey = binding.sourceKey?.trim() ?? "";
    const factName = binding.factName?.trim() ?? "";
    if (!sourceKey || !factName) throw new Error("MAPPING_CONFIGURATION_REQUIRED");
    return [path, { ...binding, sourceKey, factName, value: null }];
  }));
  if (!Object.values(bindings).some(binding => binding.kind === "fact")) throw new Error("MAPPING_CONFIGURATION_FACT_REQUIRED");
  return {
    mappingKey,
    name,
    sourceKey: null,
    targetApiKey: draft.targetApiKey,
    bindings,
    intervalMs: Math.floor(draft.intervalMs),
    enabled: draft.enabled,
  };
}

export interface MappingRequestPreview {
  resolvedPath: string;
  query: Record<string, unknown>;
  headers: Record<string, unknown>;
  body: Record<string, unknown>;
  unresolved: string[];
}

export function buildMappingRequestPreview(
  targetApi: TargetApiConfiguration | null,
  bindings: Record<string, MappingConfigurationBinding>,
  facts: BackendCollectionFactRecord[],
): MappingRequestPreview {
  if (!targetApi) return { resolvedPath: "", query: {}, headers: {}, body: {}, unresolved: [] };
  const factValues = new Map(facts.map((fact) => [
    `${fact.sourceKey}\u0000${fact.name}`,
    parseFactValue(fact),
  ]));
  const preview: MappingRequestPreview = {
    resolvedPath: targetApi.path,
    query: {},
    headers: {},
    body: {},
    unresolved: [],
  };
  for (const parameter of targetApi.parameterSchema) {
    const binding = bindings[parameter.parameterKey];
    const value = binding?.kind === "constant"
      ? binding.value
      : binding?.sourceKey && binding.factName
        ? factValues.get(`${binding.sourceKey}\u0000${binding.factName}`)
        : undefined;
    if (value === undefined || value === null) {
      preview.unresolved.push(parameter.parameterKey);
      continue;
    }
    if (parameter.location === "path") {
      preview.resolvedPath = preview.resolvedPath.replace(`{${parameter.name}}`, encodeURIComponent(String(value)));
    } else if (parameter.location === "query") {
      preview.query[parameter.name] = value;
    } else if (parameter.location === "header") {
      preview.headers[parameter.name] = value;
    } else {
      setJsonPath(preview.body, parameter.jsonPath ?? parameter.name, value);
    }
  }
  return preview;
}

function parseFactValue(fact: BackendCollectionFactRecord): unknown {
  if (fact.value === null) return undefined;
  if (fact.dataType === "boolean") return fact.value === "true" ? true : fact.value === "false" ? false : undefined;
  if (fact.dataType === "integer") {
    const value = Number(fact.value);
    return Number.isInteger(value) ? value : undefined;
  }
  if (fact.dataType === "number") {
    const value = Number(fact.value);
    return Number.isFinite(value) ? value : undefined;
  }
  return fact.value;
}

function setJsonPath(target: Record<string, unknown>, path: string, value: unknown) {
  const segments = path.split(".").filter(Boolean);
  let current = target;
  segments.forEach((segment, index) => {
    if (index === segments.length - 1) {
      current[segment] = value;
      return;
    }
    const child = current[segment];
    if (!child || typeof child !== "object" || Array.isArray(child)) current[segment] = {};
    current = current[segment] as Record<string, unknown>;
  });
}

export function useMappingConfigurationsStore() {
  let loadedRevision = localConfiguration.value?.revision ?? 0;
  let draftRevision = loadedRevision;
  const configurations = ref<MappingConfiguration[]>([]);
  const localDrafts = ref<LocalMappingConfigurationDraft[]>([]);
  const targetApis = ref<TargetApiConfiguration[]>([]);
  const valueRules = ref<MappingValueRuleConfiguration[]>([]);
  const sourceFacts = ref<BackendCollectionFactRecord[]>([]);
  const draft = ref<MappingConfigurationDraft>(emptyDraft());
  const selectedId = ref<string | null>(null);
  const selectedDraftId = ref<string | null>(null);
  const busy = ref(false);
  const factsBusy = ref(false);
  const status = ref<"idle" | "saved" | "deleted">("idle");
  const error = ref("");
  const importPreview = ref<ConfigurationImportPreview | null>(null);
  const importItems = ref<unknown[]>([]);
  const manualRuns = ref<Record<string, MappingManualRunSummary>>({});
  const manualRunBusyIds = ref<string[]>([]);
  const selectedTargetApi = computed(() => targetApis.value.find(
    (item) => item.apiKey === draft.value.targetApiKey,
  ) ?? null);
  const selectedTargetApiLocked = computed(() => selectedDraftId.value !== null);
  const savedPreview = ref<Record<string, unknown> | null>(null);
  async function previewSaved(id: string) { await run(async () => { savedPreview.value = await previewSavedMapping(id); }); }
  const requestPreview = computed(() => buildMappingRequestPreview(
    selectedTargetApi.value,
    draft.value.bindings,
    sourceFacts.value,
  ));

  async function load() {
    await run(async () => {
      await loadBackendResources();
      appendMissingTargetApiDrafts();
    });
  }

  async function loadBackendResources() {
    const snapshot = await loadLocalConfiguration();
    configurations.value = snapshot.document.mappings; targetApis.value = snapshot.document.targetApis;
    valueRules.value = snapshot.document.mappingValueRules; loadedRevision = snapshot.revision;
    manualRuns.value = {};
  }

  function appendMissingTargetApiDrafts() {
    const configuredTargetKeys = new Set(configurations.value.map((item) => item.targetApiKey));
    const localTargetKeys = new Set(localDrafts.value.map((item) => item.draft.targetApiKey));
    const loadedDrafts = targetApis.value
      .filter((item) => item.enabled && !configuredTargetKeys.has(item.apiKey) && !localTargetKeys.has(item.apiKey))
      .map((item) => ({ localId: crypto.randomUUID(), draft: draftFromTargetApi(item) }));
    if (loadedDrafts.length) localDrafts.value = [...localDrafts.value, ...loadedDrafts];
  }

  async function loadTargetApiDrafts() {
    await run(async () => {
      await loadBackendResources();
      appendMissingTargetApiDrafts();
    });
  }

  async function loadSourceFacts() {
    factsBusy.value = true;
    error.value = "";
    try {
      const sourceLocator = `${savedBackendBaseUrl()}/api/integration/v1/collection-facts`;
      const facts: BackendCollectionFactRecord[] = [];
      let pageNumber = 1;
      while (true) {
        const page = await listCollectionFactsFromBackend({ page: pageNumber, pageSize: 100 });
        facts.push(...page.items);
        if (page.items.length < 100) break;
        pageNumber += 1;
      }
      if (sourceLocator !== `${savedBackendBaseUrl()}/api/integration/v1/collection-facts`) throw new Error("SMA_SOURCE_CONTEXT_CHANGED");
      sourceFacts.value = facts;
      const saved = await loadLocalConfiguration();
      const metadata = new Map(saved.document.sourceMetadata.map(item => [`${item.sourceKey}\u0000${item.factName}`, item]));
      for (const fact of facts) metadata.set(`${fact.sourceKey}\u0000${fact.name}`, { sourceKey: fact.sourceKey, factName: fact.name, dataType: fact.dataType, factKind: fact.factKind, sourceLocator, definitionVersion: fact.contractVersion });
      await changeConfiguration({ kind: "metadata", resource: "sourceMetadata", id: null, payload: [...metadata.values()] }, saved.revision);
    } catch (caught) {
      error.value = String(caught);
      throw caught;
    } finally {
      factsBusy.value = false;
    }
  }

  function startCreate() {
    draftRevision = currentRevision();
    selectedId.value = null;
    selectedDraftId.value = null;
    draft.value = emptyDraft();
    status.value = "idle";
    error.value = "";

  }

  async function open(mappingId: string) {
    draftRevision = loadedRevision;
    const mapping = configurations.value.find((item) => item.id === mappingId);
    if (!mapping) return;
    selectedId.value = mapping.id;
    selectedDraftId.value = null;
    draft.value = draftFromConfiguration(mapping);
    status.value = "idle";

  }

  async function openDraft(localId: string) {
    draftRevision = loadedRevision;
    const localDraft = localDrafts.value.find((item) => item.localId === localId);
    if (!localDraft) return;
    selectedId.value = null;
    selectedDraftId.value = localId;
    draft.value = cloneDraft(localDraft.draft);
    status.value = "idle";

  }

  function removeDraft(localId: string) {
    localDrafts.value = localDrafts.value.filter((item) => item.localId !== localId);
    if (selectedDraftId.value === localId) startCreate();
  }

  function updateDraft(patch: Partial<MappingConfigurationDraft>) {
    draft.value = { ...draft.value, ...patch };
  }

  function updateBinding(path: string, patch: Partial<MappingConfigurationBinding>) {
    const current = draft.value.bindings[path] ?? {
      kind: "fact",
      value: null,
      sourceKey: null,
      factName: null,
      valueRuleKey: null,
    };
    updateDraft({ bindings: { ...draft.value.bindings, [path]: { ...current, ...patch } } });
  }

  function initializeBindings(targetApiKey = draft.value.targetApiKey) {
    const targetApi = targetApis.value.find((item) => item.apiKey === targetApiKey) ?? null;
    if (!targetApi) return;
    const bindings = Object.fromEntries(targetApi.parameterSchema.map((parameter) => [parameter.parameterKey, (
      draft.value.bindings[parameter.parameterKey] ?? {
        kind: "fact",
        value: null,
        sourceKey: null,
        factName: null,
        valueRuleKey: null,
      }
    )]));
    updateDraft({ bindings });
  }

  async function save() {
    await run(async () => {
      const input = validateDraft(draft.value);
      const saved = selectedId.value
        ? await updateMappingConfigurationInBackend(selectedId.value, input, draftRevision)
        : await createMappingConfigurationInBackend(input, draftRevision);
      configurations.value = [...configurations.value.filter((item) => item.id !== saved.id), saved]
        .sort((left, right) => left.name.localeCompare(right.name));
      if (selectedDraftId.value) {
        localDrafts.value = localDrafts.value.filter((item) => item.localId !== selectedDraftId.value);
        selectedDraftId.value = null;
      }
      selectedId.value = saved.id;
      draft.value = draftFromConfiguration(saved);
      loadedRevision = currentRevision(); draftRevision = loadedRevision;
      status.value = "saved";
    });
  }

  async function remove(mappingId: string) {
    await run(async () => {
      await deleteMappingConfigurationInBackend(mappingId, loadedRevision);
      loadedRevision = currentRevision();
      configurations.value = configurations.value.filter((item) => item.id !== mappingId);
      const { [mappingId]: _removedRun, ...remainingRuns } = manualRuns.value;
      manualRuns.value = remainingRuns;
      if (selectedId.value === mappingId) startCreate();
      status.value = "deleted";
    });
  }

  async function previewImport(items: unknown[]) {
    await run(async () => {
      importPreview.value = await previewMappingConfigurationImportInBackend(items);
      importItems.value = items;
    });
  }

  async function applyImport() {
    await run(async () => {
      if (!importItems.value.length || !importPreview.value || importPreview.value.errors.length) {
        throw new Error("MAPPING_CONFIGURATION_IMPORT_PREVIEW_REQUIRED");
      }
      await applyMappingConfigurationImportInBackend(importItems.value);
      await loadBackendResources();
      importItems.value = [];
      importPreview.value = null;
      loadedRevision = currentRevision(); draftRevision = loadedRevision;
      status.value = "saved";
    });
  }

  function clearImport() {
    importItems.value = [];
    importPreview.value = null;
  }

  async function runManual(mappingId: string) {
    await run(async () => { await runMappingManualOnce(mappingId, ""); });
  }

  async function run(operation: () => Promise<void>) {
    busy.value = true;
    error.value = "";
    try {
      await operation();
    } catch (caught) {
      error.value = String(caught);
      throw caught;
    } finally {
      busy.value = false;
    }
  }

  return {
    configurations,
    localDrafts,
    targetApis,
    valueRules,
    sourceFacts,
    draft,
    selectedId,
    selectedDraftId,
    selectedTargetApi,
    selectedTargetApiLocked,
    requestPreview, savedPreview, previewSaved,
    busy,
    factsBusy,
    status,
    error,
    importPreview,
    manualRuns,
    manualRunBusyIds,
    load,
    loadTargetApiDrafts,
    loadSourceFacts,
    startCreate,
    open,
    openDraft,
    removeDraft,
    updateDraft,
    updateBinding,
    initializeBindings,
    save,
    remove,
    previewImport,
    applyImport,
    clearImport,
    runManual,
  };
}
