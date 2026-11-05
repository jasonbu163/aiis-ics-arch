/** 本地配置IPC、显式门禁只读事实、已关闭正常投递入口。 */
import { localConfiguration, listLocalResource, saveLocalResource, deleteLocalResource, previewResourceImport, applyResourceImport, changeConfiguration } from "./localConfiguration";
import { invokeCommand, isTauriRuntime } from "../../tauri";
import { formatBackendBaseUrl, loadBackendConnectionProfile, requireExternalIo } from "../../connection/api";
import type {
  BackendCollectionFactListQuery,
  BackendCollectionFactPage,
  ApiMaterialSelectionResult,
  CollectionFactContract,
  ApiFirstMappingRuntimeStartRequest,
  RuntimeStartupPreferences,
  MappingConfiguration,
  MappingConfigurationInput,
  MappingManualRunRecord,
  MappingManualRunResult,
  MappingValueRuleConfiguration,
  MappingValueRuleConfigurationInput,
  TargetApiConfiguration,
  TargetApiConfigurationInput,
  TargetApiMaterialLoadResult,
  TwinRuntimeSnapshot,
} from "../types";
import {
  downloadCollectionFactFile,
  type CollectionFactGeneratedFile,
} from "../utils/collectionFactFiles";

const COLLECTION_FACTS_API_PATH = "/api/integration/v1/collection-facts";
const BACKEND_REQUEST_TIMEOUT_MS = 5000;

interface BackendEnvelope<T> {
  code?: unknown;
  message?: unknown;
  data?: T;
  errorCode?: unknown;
}

export async function saveCollectionFactFile(file: CollectionFactGeneratedFile): Promise<boolean> {
  if (!isTauriRuntime()) {
    downloadCollectionFactFile(file);
    return true;
  }
  return invokeCommand("save_collection_fact_file", {
    fileName: file.fileName,
    mimeType: file.mimeType,
    contents: Array.from(file.contents),
  });
}

export function readCollectionFactsContractFromBackend(
  sourceKey: string,
): Promise<CollectionFactContract> {
  return requestBackendData(`${COLLECTION_FACTS_API_PATH}/contracts/${encodeURIComponent(sourceKey)}`);
}

export function listCollectionFactsFromBackend(
  query: BackendCollectionFactListQuery,
): Promise<BackendCollectionFactPage> {
  const parameters = new URLSearchParams();
  if (query.sourceKey) parameters.set("sourceKey", query.sourceKey);
  if (query.name) parameters.set("name", query.name);
  if (query.factKind) parameters.set("factKind", query.factKind);
  if (query.dataType) parameters.set("dataType", query.dataType);
  if (query.page) parameters.set("page", String(query.page));
  if (query.pageSize) parameters.set("pageSize", String(query.pageSize));
  const suffix = parameters.size ? `?${parameters.toString()}` : "";
  return requestBackendData(`${COLLECTION_FACTS_API_PATH}${suffix}`);
}

export function savedBackendBaseUrl(): string {
  return formatBackendBaseUrl(loadBackendConnectionProfile());
}

// Historical facade names are retained for callers; every business configuration operation is local IPC.
export function listTargetApiConfigurationsFromBackend() { return listLocalResource("targetApis"); }
export function listApiMaterialsFromBackend(_sourceLocator = "") { return listLocalResource("materials"); }
export async function syncApiMaterialSelectionInBackend(input: unknown, revision?: number): Promise<ApiMaterialSelectionResult> {
  const before = localConfiguration.value?.document.materials ?? [];
  const data = input as { operations: { selected: boolean; httpMethod: string; path: string }[] };
  const snapshot = await changeConfiguration({ kind: "selection", resource: "materials", id: null, payload: data.operations.filter(o => o.selected).map(o => `${o.httpMethod} ${o.path}`) }, revision);
  const after = snapshot.document.materials;
  return { created: after.filter(m => !before.some(b => b.id === m.id)).length, updated: after.filter(m => before.some(b => b.id === m.id && b.updatedAt !== m.updatedAt)).length, unchanged: after.filter(m => before.some(b => b.id === m.id && b.updatedAt === m.updatedAt)).length, removed: before.filter(b => !after.some(m => m.id === b.id)).length, materials: after };
}
export async function loadTargetApisFromMaterialsInBackend(materialKeys: string[], revision?: number): Promise<TargetApiMaterialLoadResult> {
  const before = localConfiguration.value?.document.targetApis ?? [];
  const snapshot = await changeConfiguration({ kind: "loadMaterials", resource: "targetApis", id: null, payload: materialKeys }, revision);
  return { created: snapshot.document.targetApis.filter(t => !before.some(b => b.id === t.id)).map(t => t.apiKey), skipped: [], requiresConfiguration: [], targetApis: snapshot.document.targetApis };
}
export async function getTargetApiConfigurationFromBackend(id: string) { const item = (await listLocalResource("targetApis")).find(t => t.id === id); if (!item) throw new Error("SMA_CONFIGURATION_NOT_FOUND"); return item; }
export function createTargetApiConfigurationInBackend(input: TargetApiConfigurationInput, revision?: number) { return saveLocalResource<TargetApiConfiguration>("targetApis", input, null, revision); }
export function updateTargetApiConfigurationInBackend(id: string, input: TargetApiConfigurationInput, revision?: number) { return saveLocalResource<TargetApiConfiguration>("targetApis", input, id, revision); }
export function deleteTargetApiConfigurationInBackend(id: string, revision?: number) { return deleteLocalResource("targetApis", id, revision); }
export function previewTargetApiImportInBackend(items: unknown[]) { return previewResourceImport("targetApis", items); }
export function applyTargetApiImportInBackend(items: unknown[]) { return applyResourceImport("targetApis", items); }
export function listMappingValueRulesFromBackend() { return listLocalResource("mappingValueRules"); }
export function createMappingValueRuleInBackend(input: MappingValueRuleConfigurationInput, revision?: number) { return saveLocalResource<MappingValueRuleConfiguration>("mappingValueRules", input, null, revision); }
export function updateMappingValueRuleInBackend(id: string, input: MappingValueRuleConfigurationInput, revision?: number) { return saveLocalResource<MappingValueRuleConfiguration>("mappingValueRules", input, id, revision); }
export function deleteMappingValueRuleInBackend(id: string, revision?: number) { return deleteLocalResource("mappingValueRules", id, revision); }
export function previewMappingValueRuleImportInBackend(items: unknown[]) { return previewResourceImport("mappingValueRules", items); }
export function applyMappingValueRuleImportInBackend(items: unknown[]) { return applyResourceImport("mappingValueRules", items); }
export function listMappingConfigurationsFromBackend() { return listLocalResource("mappings"); }
export function listMappingManualRunsFromBackend(_mappingId: string): Promise<MappingManualRunRecord[]> { return Promise.resolve([]); }
export function runMappingManualOnce(mappingId: string, expectedRowVersion: string): Promise<MappingManualRunResult> {
  return invokeCommand("run_mapping_manual_once", { mappingId, expectedRowVersion, backendBaseUrl: "" });
}
export function createMappingConfigurationInBackend(input: MappingConfigurationInput, revision?: number) { return saveLocalResource<MappingConfiguration>("mappings", input, null, revision); }
export function updateMappingConfigurationInBackend(id: string, input: MappingConfigurationInput, revision?: number) { return saveLocalResource<MappingConfiguration>("mappings", input, id, revision); }
export function deleteMappingConfigurationInBackend(id: string, revision?: number) { return deleteLocalResource("mappings", id, revision); }
export function previewMappingConfigurationImportInBackend(items: unknown[]) { return previewResourceImport("mappings", items); }
export function applyMappingConfigurationImportInBackend(items: unknown[]) { return applyResourceImport("mappings", items); }

async function requestBackendData<T>(
  path: string,
  options: { method?: string; body?: string } = {},
): Promise<T> {
  await requireExternalIo();
  const controller = new AbortController();
  const timeoutId = globalThis.setTimeout(() => controller.abort(), BACKEND_REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(`${formatBackendBaseUrl(loadBackendConnectionProfile())}${path}`, {
      method: options.method,
      body: options.body,
      headers: {
        accept: "application/json",
        ...(options.body ? { "content-type": "application/json" } : {}),
      },
      signal: controller.signal,
    });
    const envelope = await readBackendEnvelope<T>(response);
    if (!response.ok || envelope.code !== 200 || envelope.data === undefined) {
      throw new Error(backendError(envelope, response.status));
    }
    return envelope.data;
  } catch (error) {
    if (controller.signal.aborted) throw new Error("BACKEND_REQUEST_TIMEOUT");
    throw error;
  } finally {
    globalThis.clearTimeout(timeoutId);
  }
}

async function readBackendEnvelope<T>(response: Response): Promise<BackendEnvelope<T>> {
  try {
    const payload: unknown = await response.json();
    if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
      throw new Error("BACKEND_RESPONSE_INVALID");
    }
    return payload as BackendEnvelope<T>;
  } catch (error) {
    if (error instanceof Error && error.message === "BACKEND_RESPONSE_INVALID") throw error;
    throw new Error("BACKEND_RESPONSE_INVALID");
  }
}

function backendError(envelope: BackendEnvelope<unknown>, status: number): string {
  if (typeof envelope.errorCode === "string") return envelope.errorCode;
  if (typeof envelope.message === "string" && envelope.message) return envelope.message;
  return `BACKEND_REQUEST_FAILED:${status}`;
}

export function startApiFirstMappingRuntime(
  request: ApiFirstMappingRuntimeStartRequest,
): Promise<TwinRuntimeSnapshot> {
  return invokeCommand("start_api_first_mapping_runtime", { request });
}

export function pauseApiFirstMappingRuntime(): Promise<TwinRuntimeSnapshot> {
  return invokeCommand("pause_api_first_mapping_runtime");
}

export function resumeApiFirstMappingRuntime(): Promise<TwinRuntimeSnapshot> {
  return invokeCommand("resume_api_first_mapping_runtime");
}

export function stopApiFirstMappingRuntime(): Promise<TwinRuntimeSnapshot> {
  return invokeCommand("stop_api_first_mapping_runtime");
}

export function getApiFirstMappingRuntime(): Promise<TwinRuntimeSnapshot> {
  return invokeCommand("get_api_first_mapping_runtime");
}

export function loadRuntimeStartupPreferences(): Promise<RuntimeStartupPreferences> {
  if (!isTauriRuntime()) return Promise.reject(new Error("RUNTIME_STARTUP_TAURI_REQUIRED"));
  return invokeCommand("load_runtime_startup_preferences");
}

export function saveRuntimeStartupPreferences(
  preferences: RuntimeStartupPreferences,
): Promise<void> {
  if (!isTauriRuntime()) return Promise.reject(new Error("RUNTIME_STARTUP_TAURI_REQUIRED"));
  return invokeCommand("save_runtime_startup_preferences", { preferences });
}

