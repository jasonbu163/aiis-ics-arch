/**
 * File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/store/apiMaterials.ts
 * Description: Persistent OpenAPI API Material selection state.
 * Main Features:
 *   - Merges an all-method OpenAPI catalog with Backend-owned selected materials
 *   - Keeps checkbox changes as drafts until an explicit atomic save
 *   - Disables save after failed, empty, or incomplete catalog loads
 */
import { computed, ref } from "vue";

import { loadBackendConnectionProfile, testBackendOpenApi } from "../../connection/api";
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
      const catalog = await testBackendOpenApi(loadBackendConnectionProfile());
      if (!catalog.operations.length) throw new Error("API_MATERIAL_CATALOG_EMPTY");
      const locator = `${catalog.baseUrl}/openapi.json`;
      const saved = await listApiMaterialsFromBackend(locator);
      operations.value = catalog.operations;
      savedMaterials.value = saved;
      selectedIdentities.value = saved.map(
        (material) => apiMaterialIdentity(material.httpMethod, material.path),
      );
      sourceLocator.value = locator;
      catalogFingerprint.value = await buildCatalogFingerprint(catalog.operations);
      catalogReady.value = true;
    } catch (caught) {
      operations.value = [];
      savedMaterials.value = [];
      selectedIdentities.value = [];
      sourceLocator.value = "";
      catalogFingerprint.value = "";
      error.value = String(caught);
      throw caught;
    } finally {
      busy.value = false;
    }
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
      });
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
