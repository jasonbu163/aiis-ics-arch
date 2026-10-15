/**
 * File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/store/targetApiConfiguration.ts
 * Description: Reactive backend-owned Target API configuration state.
 * Main Features: Saves location-aware manual targets, imports selected API Materials, and safely removes selected Targets.
 */
import { computed, ref } from "vue";

import {
  applyTargetApiImportInBackend,
  createTargetApiConfigurationInBackend,
  deleteTargetApiConfigurationInBackend,
  getTargetApiConfigurationFromBackend,
  listApiMaterialsFromBackend,
  listMappingConfigurationsFromBackend,
  listTargetApiConfigurationsFromBackend,
  loadTargetApisFromMaterialsInBackend,
  previewTargetApiImportInBackend,
  updateTargetApiConfigurationInBackend,
} from "../api";
import type {
  CollectionFactDataType,
  ApiMaterialConfiguration,
  ConfigurationImportPreview,
  TargetApiConfiguration,
  TargetApiConfigurationInput,
  TargetApiDraft,
  TargetApiParameter,
  TargetApiMaterialLoadResult,
} from "../types";
import { savedBackendBaseUrl } from "../api";

const TARGET_API_DATA_TYPES = new Set<CollectionFactDataType>([
  "string",
  "integer",
  "number",
  "boolean",
  "datetime",
]);

function emptyDraft(): TargetApiDraft {
  return {
    apiKey: "",
    name: "",
    httpMethod: "POST",
    path: "/",
    schemaSource: "manual",
    operationId: "",
    bodyTemplateJson: "{}",
    parameterSchema: [],
    idempotencySupported: false,
    enabled: true,
  };
}

function cloneParameters(parameters: TargetApiParameter[]): TargetApiParameter[] {
  return parameters.map((parameter) => ({ ...parameter }));
}

function draftFromConfiguration(configuration: TargetApiConfiguration): TargetApiDraft {
  return {
    apiKey: configuration.apiKey,
    name: configuration.name,
    httpMethod: configuration.httpMethod,
    path: configuration.path,
    schemaSource: configuration.schemaSource,
    operationId: configuration.operationId ?? "",
    bodyTemplateJson: JSON.stringify(configuration.bodyTemplate, null, 2),
    parameterSchema: cloneParameters(configuration.parameterSchema),
    idempotencySupported: configuration.idempotencySupported,
    enabled: configuration.enabled,
  };
}

function parseBodyTemplate(bodyTemplateJson: string): Record<string, unknown> {
  let value: unknown;
  try {
    value = JSON.parse(bodyTemplateJson);
  } catch {
    throw new Error("TARGET_API_BODY_TEMPLATE_INVALID");
  }
  if (!isJsonRecord(value)) throw new Error("TARGET_API_BODY_TEMPLATE_OBJECT_REQUIRED");
  return value;
}

function validateDraft(draft: TargetApiDraft): TargetApiConfigurationInput {
  const apiKey = draft.apiKey.trim();
  const name = draft.name.trim();
  if (!apiKey) throw new Error("TARGET_API_KEY_REQUIRED");
  const path = draft.path.trim();
  if (!name) throw new Error("TARGET_API_NAME_REQUIRED");
  if (!path.startsWith("/") || path.startsWith("//")) throw new Error("TARGET_API_PATH_INVALID");

  const bodyTemplate = parseBodyTemplate(draft.bodyTemplateJson);
  const parameterSchema = cloneParameters(draft.parameterSchema).map((parameter) => ({
    parameterKey: `${parameter.location}:${parameter.name.trim()}`,
    location: parameter.location,
    name: parameter.name.trim(),
    jsonPath: parameter.location === "body" ? (parameter.jsonPath ?? parameter.name).trim() : null,
    dataType: parameter.dataType,
    required: parameter.location === "path" || parameter.required,
  }));
  const parameterKeys = parameterSchema.map((parameter) => parameter.parameterKey);
  if (parameterKeys.some((key) => !key.split(":", 2)[1]) || new Set(parameterKeys).size !== parameterKeys.length) {
    throw new Error("TARGET_API_PARAMETER_PATH_INVALID");
  }
  if (parameterSchema.some((parameter) => !TARGET_API_DATA_TYPES.has(parameter.dataType))) {
    throw new Error("TARGET_API_PARAMETER_TYPE_INVALID");
  }

  const leafPaths = new Set(collectLeafPaths(bodyTemplate));
  if (parameterSchema.some((parameter) => parameter.location === "body" && !leafPaths.has(parameter.jsonPath ?? ""))) {
    throw new Error("TARGET_API_PARAMETER_PATH_INVALID");
  }
  const placeholders = new Set([...path.matchAll(/\{([^{}]+)\}/g)].map((match) => match[1]));
  const pathNames = new Set(parameterSchema.filter((parameter) => parameter.location === "path").map((parameter) => parameter.name));
  if (placeholders.size !== pathNames.size || [...placeholders].some((item) => !pathNames.has(item))) {
    throw new Error("TARGET_API_PARAMETER_PATH_INVALID");
  }

  return {
    apiKey,
    name,
    httpMethod: draft.httpMethod,
    path,
    schemaSource: draft.schemaSource,
    operationId: draft.operationId.trim() || null,
    bodyTemplate,
    parameterSchema,
    idempotencySupported: draft.idempotencySupported,
    enabled: draft.enabled,
  };
}

function collectLeafPaths(value: unknown, prefix = ""): string[] {
  if (Array.isArray(value)) return prefix ? [prefix] : [];
  if (isJsonRecord(value)) {
    return Object.entries(value).flatMap(([key, child]) => (
      collectLeafPaths(child, prefix ? `${prefix}.${key}` : key)
    ));
  }
  return prefix ? [prefix] : [];
}

function isJsonRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

export function useTargetApiConfigurationStore() {
  const configurations = ref<TargetApiConfiguration[]>([]);
  const draft = ref<TargetApiDraft>(emptyDraft());
  const selectedId = ref<string | null>(null);
  const apiMaterials = ref<ApiMaterialConfiguration[]>([]);
  const selectedMaterialKeys = ref<string[]>([]);
  const materialLoadResult = ref<TargetApiMaterialLoadResult | null>(null);
  const busy = ref(false);
  const status = ref<"idle" | "saved" | "deleted">("idle");
  const error = ref("");
  const importPreview = ref<ConfigurationImportPreview | null>(null);
  const importItems = ref<unknown[]>([]);
  const loadedMaterialKeys = computed(() => new Set(configurations.value
    .map((item) => item.originMaterialKey)
    .filter((key): key is string => Boolean(key))));

  async function load() {
    await run(async () => {
      configurations.value = await listTargetApiConfigurationsFromBackend();
    });
  }

  function startManual() {
    selectedId.value = null;
    draft.value = emptyDraft();
    status.value = "idle";
    error.value = "";
  }

  async function loadApiMaterials() {
    await run(async () => {
      configurations.value = await listTargetApiConfigurationsFromBackend();
      apiMaterials.value = await listApiMaterialsFromBackend(`${savedBackendBaseUrl()}/openapi.json`);
      selectedMaterialKeys.value = [];
      materialLoadResult.value = null;
    });
  }

  function toggleMaterial(materialKey: string, selected: boolean) {
    const current = new Set(selectedMaterialKeys.value);
    if (selected) current.add(materialKey);
    else current.delete(materialKey);
    selectedMaterialKeys.value = [...current];
  }

  async function loadSelectedMaterials() {
    await run(async () => {
      if (!selectedMaterialKeys.value.length) throw new Error("TARGET_API_MATERIAL_SELECTION_REQUIRED");
      materialLoadResult.value = await loadTargetApisFromMaterialsInBackend(selectedMaterialKeys.value);
      configurations.value = materialLoadResult.value.targetApis;
      selectedMaterialKeys.value = [];
      status.value = "saved";
    });
  }

  async function open(targetApiId: string) {
    await run(async () => {
      const configuration = await getTargetApiConfigurationFromBackend(targetApiId);
      selectedId.value = configuration.id;
      draft.value = draftFromConfiguration(configuration);
      status.value = "idle";
    });
  }

  function updateDraft(patch: Partial<TargetApiDraft>) {
    draft.value = { ...draft.value, ...patch };
  }

  function updateParameter(index: number, patch: Partial<TargetApiParameter>) {
    const parameterSchema = cloneParameters(draft.value.parameterSchema);
    parameterSchema[index] = { ...parameterSchema[index], ...patch };
    updateDraft({ parameterSchema });
  }

  function addParameter() {
    updateDraft({
      parameterSchema: [
        ...cloneParameters(draft.value.parameterSchema),
        { parameterKey: "body:", location: "body", name: "", jsonPath: "", dataType: "string", required: false },
      ],
    });
  }

  function removeParameter(index: number) {
    updateDraft({ parameterSchema: draft.value.parameterSchema.filter((_, itemIndex) => itemIndex !== index) });
  }

  async function save() {
    await run(async () => {
      const input = validateDraft(draft.value);
      const saved = selectedId.value
        ? await updateTargetApiConfigurationInBackend(selectedId.value, input)
        : await createTargetApiConfigurationInBackend(input);
      selectedId.value = saved.id;
      draft.value = draftFromConfiguration(saved);
      configurations.value = [
        ...configurations.value.filter((configuration) => configuration.id !== saved.id),
        saved,
      ].sort((left, right) => left.name.localeCompare(right.name));
      status.value = "saved";
    });
  }

  async function remove(targetApiId: string) {
    await run(async () => {
      await deleteTargetApiConfigurationInBackend(targetApiId);
      configurations.value = configurations.value.filter((configuration) => configuration.id !== targetApiId);
      if (selectedId.value === targetApiId) startManual();
      status.value = "deleted";
    });
  }

  async function removeMany(targetApiIds: string[]) {
    const ids = [...new Set(targetApiIds)];
    if (!ids.length) return;
    await run(async () => {
      const selected = new Set(ids);
      const mappings = await listMappingConfigurationsFromBackend();
      if (mappings.some((mapping) => selected.has(mapping.targetApiId))) {
        throw new Error("tss_target_api_in_use");
      }
      for (const targetApiId of ids) {
        await deleteTargetApiConfigurationInBackend(targetApiId);
        configurations.value = configurations.value.filter((item) => item.id !== targetApiId);
        if (selectedId.value === targetApiId) startManual();
      }
      status.value = "deleted";
    });
  }

  async function previewImport(items: unknown[]) {
    await run(async () => {
      const preview = await previewTargetApiImportInBackend(items);
      importItems.value = items;
      importPreview.value = preview;
    });
  }

  async function applyImport() {
    await run(async () => {
      if (!importItems.value.length || !importPreview.value || importPreview.value.errors.length) {
        throw new Error("TARGET_API_IMPORT_PREVIEW_REQUIRED");
      }
      await applyTargetApiImportInBackend(importItems.value);
      importItems.value = [];
      importPreview.value = null;
      configurations.value = await listTargetApiConfigurationsFromBackend();
      status.value = "saved";
    });
  }

  function clearImport() {
    importItems.value = [];
    importPreview.value = null;
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
    draft,
    selectedId,
    apiMaterials,
    selectedMaterialKeys,
    loadedMaterialKeys,
    materialLoadResult,
    busy,
    status,
    error,
    importPreview,
    load,
    startManual,
    loadApiMaterials,
    toggleMaterial,
    loadSelectedMaterials,
    open,
    updateDraft,
    updateParameter,
    addParameter,
    removeParameter,
    save,
    remove,
    removeMany,
    previewImport,
    applyImport,
    clearImport,
  };
}
