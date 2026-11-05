/** 本地catalog/勾选草稿、显式OpenAPI预览应用与CAS保存。 */
import { computed, ref } from "vue";
import { currentRevision, loadLocalConfiguration, previewConfiguration, applyConfiguration, type LocalImportPreview, type ChangeIntent } from "../api/localConfiguration";

import { normalizeBackendOpenApiDocument, loadBackendConnectionProfile, testBackendOpenApi } from "../../connection/api";
import type { BackendOpenApiOperation } from "../../connection/types";
import { listApiMaterialsFromBackend, syncApiMaterialSelectionInBackend } from "../api";
import type { ApiMaterialConfiguration, ApiMaterialSelectionResult } from "../types";

export function apiMaterialIdentity(method: string, path: string): string {
  return `${method.toUpperCase()} ${path}`;
}

async function buildCatalogFingerprint(operations: BackendOpenApiOperation[]): Promise<string> {
  const source = operations.map((operation) => operation.contentHash).sort().join(":");
  const digest = await globalThis.crypto.subtle.digest("SHA-256", new TextEncoder().encode(source));
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

export function useApiMaterialsStore() {
  let selectionRevision = 0;
  const catalogCandidates = ref<BackendOpenApiOperation[]>([]);
  const operations = ref<BackendOpenApiOperation[]>([]);
  const savedMaterials = ref<ApiMaterialConfiguration[]>([]);
  const selectedIdentities = ref<string[]>([]);
  const sourceLocator = ref("");
  const catalogFingerprint = ref("");
  const catalogReady = ref(false);
  const busy = ref(false);
  const saving = ref(false);
  const error = ref("");
  const result = ref<ApiMaterialSelectionResult | null>(null);

  const savedIdentities = computed(() => new Set(savedMaterials.value.map(
    (material) => apiMaterialIdentity(material.httpMethod, material.path),
  )));
  const missingSavedMaterials = computed(() => {
    const catalogIdentities = new Set(operations.value.map(
      (operation) => apiMaterialIdentity(operation.method, operation.path),
    ));
    return savedMaterials.value.filter(
      (material) => !catalogIdentities.has(apiMaterialIdentity(material.httpMethod, material.path)),
    );
  });
  const canSave = computed(() => catalogReady.value && operations.value.length > 0 && !busy.value && !saving.value);

  async function load() {
    busy.value = true;
    catalogReady.value = false;
    error.value = "";
    result.value = null;
    try {
      const snapshot = await loadLocalConfiguration();
      selectionRevision = snapshot.revision;
      operations.value = snapshot.document.catalog;
      savedMaterials.value = snapshot.document.materials;
      selectedIdentities.value = savedMaterials.value.map(m => apiMaterialIdentity(m.httpMethod, m.path));
      sourceLocator.value = snapshot.document.catalog[0]?.sourceLocator ?? "";
      catalogFingerprint.value = await buildCatalogFingerprint(operations.value);
      catalogReady.value = operations.value.length > 0;
    } catch (caught) { error.value = String(caught); throw caught;
    } finally {
      busy.value = false;
    }
  }

  const catalogPreview = ref<LocalImportPreview | null>(null);
  let catalogIntent: ChangeIntent | null = null;
  async function previewCatalog(file?: File) {
    busy.value = true; error.value = ""; catalogPreview.value = null; catalogIntent = null;
    try {
      let entries: BackendOpenApiOperation[]; let locator: string;
      if (file) {
        if (file.size > 10 * 1024 * 1024) throw new Error("SMA_CONFIGURATION_LIMIT_EXCEEDED");
        entries = await normalizeBackendOpenApiDocument(JSON.parse(await file.text()));
        locator = `file:${file.name}`;
      } else { const result = await testBackendOpenApi(loadBackendConnectionProfile()); entries = result.operations; locator = `${result.baseUrl}/openapi.json`; }
      catalogCandidates.value = entries;
      catalogIntent = { kind: "catalog", resource: "catalog", id: null, payload: entries.map(entry => ({ ...entry, sourceLocator: locator })) };
      catalogPreview.value = await previewConfiguration(catalogIntent);
    } catch (caught) { error.value = String(caught); throw caught; } finally { busy.value = false; }
  }
  async function applyCatalog() {
    if (!catalogIntent || !catalogPreview.value || catalogPreview.value.errors.length) throw new Error("SMA_CONFIGURATION_PREVIEW_REQUIRED");
    busy.value = true; error.value = "";
    try { await applyConfiguration(catalogIntent, catalogPreview.value); catalogPreview.value = null; catalogIntent = null; await load(); }
    catch (caught) { error.value = String(caught); throw caught; } finally { busy.value = false; }
  }

  function toggle(method: string, path: string, selected: boolean) {
    const identity = apiMaterialIdentity(method, path);
    const current = new Set(selectedIdentities.value);
    if (selected) current.add(identity);
    else current.delete(identity);
    selectedIdentities.value = [...current];
  }

  async function save() {
    if (!canSave.value) throw new Error("API_MATERIAL_CATALOG_NOT_READY");
    saving.value = true;
    error.value = "";
    try {
      const selected = new Set(selectedIdentities.value);
      result.value = await syncApiMaterialSelectionInBackend({
        sourceLocator: sourceLocator.value,
        catalogFingerprint: catalogFingerprint.value,
        catalogSucceeded: true,
        operations: operations.value.map((operation) => ({
          selected: selected.has(apiMaterialIdentity(operation.method, operation.path)),
          httpMethod: operation.method,
          path: operation.path,
          operationId: operation.operationId,
          name: operation.summary ?? operation.operationId ?? `${operation.method} ${operation.path}`,
          operationSnapshot: operation.operationSnapshot,
          requestContract: operation.requestContract,
          bodyTemplate: operation.bodyTemplate,
          normalizationStatus: operation.normalizationStatus,
          normalizationErrorCode: operation.normalizationErrorCode,
          contentHash: operation.contentHash,
        })),
      }, selectionRevision);
      selectionRevision = currentRevision();
      savedMaterials.value = result.value.materials;
      selectedIdentities.value = result.value.materials.map(
        (material) => apiMaterialIdentity(material.httpMethod, material.path),
      );
    } catch (caught) {
      error.value = String(caught);
      throw caught;
    } finally {
      saving.value = false;
    }
  }

  return {
    catalogCandidates, catalogPreview, previewCatalog, applyCatalog,
    operations,
    savedMaterials,
    selectedIdentities,
    savedIdentities,
    missingSavedMaterials,
    sourceLocator,
    catalogReady,
    busy,
    saving,
    error,
    result,
    canSave,
    load,
    toggle,
    save,
  };
}
