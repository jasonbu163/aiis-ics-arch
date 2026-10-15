/**
 * File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/api/index.ts
 * Description: Collection Facts, API-first Mapping configuration, and Runtime IPC facade.
 * Main Features: Keeps API Materials, Mapping configuration, and Simulation settings Backend-owned while Tauri owns Mapping delivery and local runtime startup preferences.
 */
import { invokeCommand, isTauriRuntime } from "../../tauri";
import { formatBackendBaseUrl, loadBackendConnectionProfile, requireExternalIo } from "../../connection/api";
import type {
  BackendCollectionFactListQuery,
  BackendCollectionFactPage,
  ApiMaterialConfiguration,
  ApiMaterialSelectionResult,
  CollectionFactContract,
  CollectionFactContractPreview,
  CollectionFactValueUpdate,
  CollectionFactValueUpdateResponse,
  ConfigurationImportPreview,
  ApiFirstMappingRuntimeStartRequest,
  CollectionSimulationStartRequest,
  RuntimeStartupPreferences,
  SimulationRuleConfiguration,
  SimulationRuleConfigurationInput,
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
const TSS_TARGET_APIS_API_PATH = "/api/tss/v1/target-apis";
const TSS_API_MATERIALS_API_PATH = "/api/tss/v1/api-materials";
const TSS_MAPPING_VALUE_RULES_API_PATH = "/api/tss/v1/mapping-value-rules";
const TSS_MAPPINGS_API_PATH = "/api/tss/v1/mappings";
const TSS_SIMULATION_RULES_API_PATH = "/api/tss/v1/simulation-rules";
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

export function previewCollectionFactsContractFromBackend(
  contract: CollectionFactContract,
): Promise<CollectionFactContractPreview> {
  return requestBackendData(`${COLLECTION_FACTS_API_PATH}/contracts/preview`, {
    method: "POST",
    body: JSON.stringify(contract),
  });
}

export function applyCollectionFactsContractToBackend(
  contract: CollectionFactContract,
): Promise<CollectionFactContractPreview> {
  return requestBackendData(
    `${COLLECTION_FACTS_API_PATH}/contracts/${encodeURIComponent(contract.sourceKey)}`,
    {
      method: "PUT",
      body: JSON.stringify(contract),
    },
  );
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

export function updateCollectionFactValuesInBackend(
  sourceKey: string,
  update: CollectionFactValueUpdate,
): Promise<CollectionFactValueUpdateResponse> {
  return requestBackendData(`${COLLECTION_FACTS_API_PATH}/${encodeURIComponent(sourceKey)}/values`, {
    method: "PUT",
    body: JSON.stringify(update),
  });
}

export function listSimulationRulesFromBackend(): Promise<SimulationRuleConfiguration[]> {
  return requestBackendData(TSS_SIMULATION_RULES_API_PATH);
}

export function createSimulationRuleInBackend(
  input: SimulationRuleConfigurationInput,
): Promise<SimulationRuleConfiguration> {
  return requestBackendData(TSS_SIMULATION_RULES_API_PATH, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updateSimulationRuleInBackend(
  simulationRuleId: string,
  input: SimulationRuleConfigurationInput,
): Promise<SimulationRuleConfiguration> {
  return requestBackendData(`${TSS_SIMULATION_RULES_API_PATH}/${encodeURIComponent(simulationRuleId)}`, {
    method: "PUT",
    body: JSON.stringify(input),
  });
}

export function savedBackendBaseUrl(): string {
  return formatBackendBaseUrl(loadBackendConnectionProfile());
}

export function deleteSimulationRuleInBackend(ruleId: string): Promise<unknown> {
  return requestBackendData(`${TSS_SIMULATION_RULES_API_PATH}/${encodeURIComponent(ruleId)}`, {
    method: "DELETE",
  });
}

export function listTargetApiConfigurationsFromBackend(): Promise<TargetApiConfiguration[]> {
  return requestBackendData(TSS_TARGET_APIS_API_PATH);
}

export function listApiMaterialsFromBackend(
  sourceLocator: string,
): Promise<ApiMaterialConfiguration[]> {
  const query = new URLSearchParams({ sourceLocator });
  return requestBackendData(`${TSS_API_MATERIALS_API_PATH}?${query.toString()}`);
}

export function syncApiMaterialSelectionInBackend(input: unknown): Promise<ApiMaterialSelectionResult> {
  return requestBackendData(`${TSS_API_MATERIALS_API_PATH}/selection`, {
    method: "PUT",
    body: JSON.stringify(input),
  });
}

export function loadTargetApisFromMaterialsInBackend(
  materialKeys: string[],
): Promise<TargetApiMaterialLoadResult> {
  return requestBackendData(`${TSS_TARGET_APIS_API_PATH}/load-materials`, {
    method: "POST",
    body: JSON.stringify({ materialKeys }),
  });
}

export function getTargetApiConfigurationFromBackend(
  targetApiId: string,
): Promise<TargetApiConfiguration> {
  return requestBackendData(`${TSS_TARGET_APIS_API_PATH}/${encodeURIComponent(targetApiId)}`);
}

export function createTargetApiConfigurationInBackend(
  input: TargetApiConfigurationInput,
): Promise<TargetApiConfiguration> {
  return requestBackendData(TSS_TARGET_APIS_API_PATH, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updateTargetApiConfigurationInBackend(
  targetApiId: string,
  input: TargetApiConfigurationInput,
): Promise<TargetApiConfiguration> {
  const { apiKey: _apiKey, ...update } = input;
  return requestBackendData(`${TSS_TARGET_APIS_API_PATH}/${encodeURIComponent(targetApiId)}`, {
    method: "PUT",
    body: JSON.stringify(update),
  });
}

export function previewTargetApiImportInBackend(
  items: unknown[],
): Promise<ConfigurationImportPreview> {
  return requestBackendData(`${TSS_TARGET_APIS_API_PATH}/import-preview`, {
    method: "POST",
    body: JSON.stringify({ items }),
  });
}

export function applyTargetApiImportInBackend(
  items: unknown[],
): Promise<ConfigurationImportPreview> {
  return requestBackendData(`${TSS_TARGET_APIS_API_PATH}/import-apply`, {
    method: "POST",
    body: JSON.stringify({ items }),
  });
}

export function deleteTargetApiConfigurationInBackend(
  targetApiId: string,
): Promise<{ id: string }> {
  return requestBackendData(`${TSS_TARGET_APIS_API_PATH}/${encodeURIComponent(targetApiId)}`, {
    method: "DELETE",
  });
}

export function listMappingValueRulesFromBackend(): Promise<MappingValueRuleConfiguration[]> {
  return requestBackendData(TSS_MAPPING_VALUE_RULES_API_PATH);
}

export function createMappingValueRuleInBackend(
  input: MappingValueRuleConfigurationInput,
): Promise<MappingValueRuleConfiguration> {
  return requestBackendData(TSS_MAPPING_VALUE_RULES_API_PATH, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updateMappingValueRuleInBackend(
  valueRuleId: string,
  input: MappingValueRuleConfigurationInput,
): Promise<MappingValueRuleConfiguration> {
  const {
    valueRuleKey: _valueRuleKey,
    originSourceKey: _originSourceKey,
    originFactName: _originFactName,
    ...update
  } = input;
  return requestBackendData(`${TSS_MAPPING_VALUE_RULES_API_PATH}/${encodeURIComponent(valueRuleId)}`, {
    method: "PUT",
    body: JSON.stringify(update),
  });
}

export function deleteMappingValueRuleInBackend(valueRuleId: string): Promise<{ id: string }> {
  return requestBackendData(`${TSS_MAPPING_VALUE_RULES_API_PATH}/${encodeURIComponent(valueRuleId)}`, {
    method: "DELETE",
  });
}

export function previewMappingValueRuleImportInBackend(
  items: unknown[],
): Promise<ConfigurationImportPreview> {
  return requestBackendData(`${TSS_MAPPING_VALUE_RULES_API_PATH}/import-preview`, {
    method: "POST",
    body: JSON.stringify({ items }),
  });
}

export function applyMappingValueRuleImportInBackend(
  items: unknown[],
): Promise<ConfigurationImportPreview> {
  return requestBackendData(`${TSS_MAPPING_VALUE_RULES_API_PATH}/import-apply`, {
    method: "POST",
    body: JSON.stringify({ items }),
  });
}

export function listMappingConfigurationsFromBackend(): Promise<MappingConfiguration[]> {
  return requestBackendData(TSS_MAPPINGS_API_PATH);
}

export function listMappingManualRunsFromBackend(
  mappingId: string,
): Promise<MappingManualRunRecord[]> {
  return requestBackendData(
    `${TSS_MAPPINGS_API_PATH}/${encodeURIComponent(mappingId)}/manual-runs`,
  );
}

export function runMappingManualOnce(
  mappingId: string,
  expectedRowVersion: string,
): Promise<MappingManualRunResult> {
  if (!isTauriRuntime()) return Promise.reject(new Error("MAPPING_MANUAL_RUN_TAURI_REQUIRED"));
  return invokeCommand("run_mapping_manual_once", {
    mappingId,
    expectedRowVersion,
    backendBaseUrl: savedBackendBaseUrl(),
  });
}

export function createMappingConfigurationInBackend(
  input: MappingConfigurationInput,
): Promise<MappingConfiguration> {
  return requestBackendData(TSS_MAPPINGS_API_PATH, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updateMappingConfigurationInBackend(
  mappingId: string,
  input: MappingConfigurationInput,
): Promise<MappingConfiguration> {
  const { mappingKey: _mappingKey, ...update } = input;
  return requestBackendData(`${TSS_MAPPINGS_API_PATH}/${encodeURIComponent(mappingId)}`, {
    method: "PUT",
    body: JSON.stringify(update),
  });
}

export function deleteMappingConfigurationInBackend(mappingId: string): Promise<{ id: string }> {
  return requestBackendData(`${TSS_MAPPINGS_API_PATH}/${encodeURIComponent(mappingId)}`, {
    method: "DELETE",
  });
}

export function previewMappingConfigurationImportInBackend(
  items: unknown[],
): Promise<ConfigurationImportPreview> {
  return requestBackendData(`${TSS_MAPPINGS_API_PATH}/import-preview`, {
    method: "POST",
    body: JSON.stringify({ items }),
  });
}

export function applyMappingConfigurationImportInBackend(
  items: unknown[],
): Promise<ConfigurationImportPreview> {
  return requestBackendData(`${TSS_MAPPINGS_API_PATH}/import-apply`, {
    method: "POST",
    body: JSON.stringify({ items }),
  });
}

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

export function startCollectionFactSimulationRuntime(
  request: CollectionSimulationStartRequest,
): Promise<TwinRuntimeSnapshot> {
  return invokeCommand("start_collection_fact_simulation_runtime", { request });
}

export function pauseCollectionFactSimulationRuntime(): Promise<TwinRuntimeSnapshot> {
  return invokeCommand("pause_collection_fact_simulation_runtime");
}

export function resumeCollectionFactSimulationRuntime(): Promise<TwinRuntimeSnapshot> {
  return invokeCommand("resume_collection_fact_simulation_runtime");
}

export function stopCollectionFactSimulationRuntime(): Promise<TwinRuntimeSnapshot> {
  return invokeCommand("stop_collection_fact_simulation_runtime");
}

export function getCollectionFactSimulationRuntime(): Promise<TwinRuntimeSnapshot> {
  return invokeCommand("get_collection_fact_simulation_runtime");
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

