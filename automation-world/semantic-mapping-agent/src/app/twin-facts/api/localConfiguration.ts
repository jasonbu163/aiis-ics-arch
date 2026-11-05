/** SMA配置IPC门面：Rust/SQLite唯一权威；不自动读旧localStorage或远端配置。 */
import { shallowRef } from "vue";
import { invokeCommand, isTauriRuntime } from "../../tauri";
import type { BackendConnectionProfile, BackendOpenApiOperation } from "../../connection/types";
import type { ApiMaterialConfiguration, TargetApiConfiguration, MappingValueRuleConfiguration, MappingConfiguration, ConfigurationImportPreview } from "../types";
export interface SourceMetadata { sourceKey: string; factName: string; dataType: string; factKind: string | null; sourceLocator: string; definitionVersion: string | null }
export interface ConfigurationDocument { connection: BackendConnectionProfile; catalog: (BackendOpenApiOperation & { sourceLocator: string })[]; materials: ApiMaterialConfiguration[]; targetApis: TargetApiConfiguration[]; mappingValueRules: MappingValueRuleConfiguration[]; mappings: MappingConfiguration[]; sourceMetadata: SourceMetadata[] }
export interface ConfigurationSnapshot { schemaVersion: number; revision: number; updatedAt: string; document: ConfigurationDocument }
export interface ChangeIntent { kind: string; resource: string; id: string | null; payload: unknown }
export interface LocalImportPreview extends ConfigurationImportPreview { token: string; expectedRevision: number; deletedKeys: string[] }
export const localConfiguration = shallowRef<ConfigurationSnapshot | null>(null);
function native<T>(command: string, args?: Record<string, unknown>): Promise<T> { if (!isTauriRuntime()) return Promise.reject(new Error("SMA_LOCAL_CONFIGURATION_TAURI_REQUIRED")); return invokeCommand<T>(command, args); }
export async function loadLocalConfiguration() { const snapshot = await native<ConfigurationSnapshot>("load_local_configuration"); localConfiguration.value = snapshot; return snapshot; }
export function currentRevision() { const value = localConfiguration.value; if (!value) throw new Error("SMA_CONFIGURATION_NOT_READY"); return value.revision; }
export function currentConnection(): BackendConnectionProfile { return { ...(localConfiguration.value?.document.connection ?? { scheme: "http", host: "", port: 0 }) }; }
export async function changeConfiguration(intent: ChangeIntent, expectedRevision = currentRevision()) { const snapshot = await native<ConfigurationSnapshot>("change_local_configuration", { expectedRevision, intent }); localConfiguration.value = snapshot; return snapshot; }
export function previewConfiguration(intent: ChangeIntent, expectedRevision = currentRevision()) { return native<LocalImportPreview>("preview_local_configuration", { expectedRevision, intent }); }
export async function applyConfiguration(intent: ChangeIntent, preview: LocalImportPreview, confirmed = false) { const snapshot = await native<ConfigurationSnapshot>("apply_local_configuration", { expectedRevision: preview.expectedRevision, intent, token: preview.token, confirmed }); localConfiguration.value = snapshot; return snapshot; }
export function exportConfiguration() { return native<string>("export_local_configuration"); }
export function previewSavedMapping(mappingId: string) { return native<Record<string, unknown>>("preview_saved_local_mapping", { mappingId, expectedRevision: currentRevision() }); }
export async function listLocalResource<K extends "materials" | "targetApis" | "mappingValueRules" | "mappings">(resource: K): Promise<ConfigurationDocument[K]> { return (await loadLocalConfiguration()).document[resource]; }
export async function saveLocalResource<T>(resource: string, payload: unknown, id: string | null, expectedRevision = currentRevision()): Promise<T> {
  const snapshot = await changeConfiguration({ kind: "upsert", resource, id, payload }, expectedRevision);
  const values = snapshot.document[resource as "targetApis"] as unknown as Record<string, unknown>[];
  const input = payload as Record<string, unknown>;
  const key = resource === "targetApis" ? "apiKey" : resource === "mappingValueRules" ? "valueRuleKey" : "mappingKey";
  const saved = values.find(value => id ? value.id === id : input[key] ? value[key] === input[key] : resource === "mappingValueRules" && value.originSourceKey === input.originSourceKey && value.originFactName === input.originFactName);
  if (!saved) throw new Error("SMA_CONFIGURATION_SAVE_RESULT_INVALID");
  return saved as T;
}
export async function deleteLocalResource(resource: string, id: string, expectedRevision = currentRevision()) { await changeConfiguration({ kind: "delete", resource, id, payload: null }, expectedRevision); return { id }; }
const importPreviews = new Map<string, { serialized: string; preview: LocalImportPreview }>();
export async function previewResourceImport(resource: string, items: unknown[]) { const intent = { kind: "import", resource, id: null, payload: items }; const preview = await previewConfiguration(intent); importPreviews.set(resource, { serialized: JSON.stringify(items), preview }); return preview; }
export async function applyResourceImport(resource: string, items: unknown[]) { const previous = importPreviews.get(resource); if (!previous || previous.serialized !== JSON.stringify(items)) throw new Error("SMA_CONFIGURATION_PREVIEW_CHANGED"); await applyConfiguration({ kind: "import", resource, id: null, payload: items }, previous.preview); importPreviews.delete(resource); return previous.preview; }
