/**
 * File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/store/collectionFacts.ts
 * Description: Reactive backend-owned Fact Table state and guarded contract/value mutations.
 * Main Features:
 *   - Loads source-scoped contracts or bootstraps exact not-found sources in page memory
 *   - Loads single/all-source paged facts through the Backend API
 *   - Holds definition changes in page memory until Preview then explicit Apply
 *   - Validates typed value updates locally before the Backend Values API
 */
import { computed, ref } from "vue";

import {
  applyCollectionFactsContractToBackend,
  listCollectionFactsFromBackend,
  previewCollectionFactsContractFromBackend,
  readCollectionFactsContractFromBackend,
  updateCollectionFactValuesInBackend,
} from "../api";
import type {
  BackendCollectionFactListQuery,
  BackendCollectionFactPage,
  CollectionFactContract,
  CollectionFactDataType,
  CollectionFactSyncSummary,
  CollectionFactValueInput,
} from "../types";

export const DEFAULT_COLLECTION_FACT_CONTRACT_VERSION = "collection-facts.v1";
const DEFAULT_SOURCE_KEY = "";
const MAX_VALUE_UPDATE_COUNT = 500;
const COLLECTION_FACT_SOURCE_NOT_FOUND = "collection_fact_source_not_found";

const EMPTY_PAGE: BackendCollectionFactPage = { items: [], page: 1, pageSize: 25, total: 0 };

export function useCollectionFactsStore() {
  const selectedSourceKey = ref(DEFAULT_SOURCE_KEY);
  const contract = ref<CollectionFactContract | null>(null);
  const pendingContract = ref<CollectionFactContract | null>(null);
  const pendingPreview = ref<{ contract: CollectionFactContract; summary: CollectionFactSyncSummary } | null>(null);
  const query = ref<BackendCollectionFactListQuery>({
    sourceKey: DEFAULT_SOURCE_KEY,
    page: 1,
    pageSize: 25,
  });
  const factPage = ref<BackendCollectionFactPage>(EMPTY_PAGE);
  const contractBusy = ref(false);
  const inspectorBusy = ref(false);
  const valuesBusy = ref(false);
  const status = ref<"idle" | "previewed" | "saved" | "valuesSaved">("idle");
  const error = ref("");
  const sourceKey = computed(() => selectedSourceKey.value);
  const contractVersion = computed(() => contract.value?.contractVersion ?? DEFAULT_COLLECTION_FACT_CONTRACT_VERSION);
  const previewNeedsConfirmation = computed(() => {
    const summary = pendingPreview.value?.summary;
    return Boolean(summary && (summary.deleted.length || summary.kindChanges.length || summary.typeChanges.length));
  });

  async function load() {
    await withBusy(contractBusy, async () => {
      const source = sourceKey.value;
      contract.value = null;
      pendingContract.value = null;
      pendingPreview.value = null;
      status.value = "idle";
      if (!source) {
        await refreshFacts();
        return;
      }
      let loaded: CollectionFactContract;
      try {
        loaded = await readCollectionFactsContractFromBackend(source);
      } catch (caught) {
        if (!(caught instanceof Error) || caught.message !== COLLECTION_FACT_SOURCE_NOT_FOUND) throw caught;
        loaded = emptyContract(source);
      }
      await refreshFacts();
      contract.value = cloneContract(loaded);
    });
  }

  async function previewContract(candidate: CollectionFactContract) {
    await withBusy(contractBusy, async () => {
      const normalized = normalizeContract(candidate);
      const preview = await previewCollectionFactsContractFromBackend(normalized);
      pendingContract.value = normalized;
      pendingPreview.value = {
        contract: cloneContract(preview.contract),
        summary: cloneSummary(preview.summary),
      };
      status.value = "previewed";
    });
  }

  async function applyPendingContract() {
    await withBusy(contractBusy, async () => {
      if (!pendingContract.value) throw new Error("COLLECTION_FACT_PREVIEW_REQUIRED");
      const applied = await applyCollectionFactsContractToBackend(pendingContract.value);
      contract.value = cloneContract(applied.contract);
      pendingContract.value = null;
      pendingPreview.value = null;
      status.value = "saved";
      syncSourceKey(contract.value.sourceKey);
      await refreshFacts();
    });
  }

  function discardPendingContract() {
    pendingContract.value = null;
    pendingPreview.value = null;
    status.value = "idle";
  }

  async function refreshFacts() {
    await withBusy(inspectorBusy, async () => {
      const source = sourceKey.value;
      factPage.value = await listCollectionFactsFromBackend({ ...query.value, sourceKey: source || undefined });
    });
  }

  async function updateQuery(patch: Partial<BackendCollectionFactListQuery>) {
    query.value = { ...query.value, ...patch };
    await refreshFacts();
  }

  async function updateValues(values: CollectionFactValueInput[]) {
    await withBusy(valuesBusy, async () => {
      const savedContract = contract.value;
      if (!savedContract) throw new Error("COLLECTION_FACT_CONTRACT_REQUIRED");
      validateValueUpdates(savedContract, values);
      await updateCollectionFactValuesInBackend(savedContract.sourceKey, {
        contractVersion: savedContract.contractVersion,
        values,
      });
      status.value = "valuesSaved";
      await refreshFacts();
    });
  }

  async function listAllFacts() {
    const source = sourceKey.value;
    if (!source) return [];
    const first = await listCollectionFactsFromBackend({ sourceKey: source, page: 1, pageSize: 100 });
    const items = [...first.items];
    const pageCount = Math.ceil(first.total / first.pageSize);
    for (let page = 2; page <= pageCount; page += 1) {
      const next = await listCollectionFactsFromBackend({ sourceKey: source, page, pageSize: first.pageSize });
      items.push(...next.items);
    }
    return items;
  }

  function setSourceKey(value: string) {
    syncSourceKey(value.trim());
    contract.value = null;
    pendingContract.value = null;
    pendingPreview.value = null;
    factPage.value = EMPTY_PAGE;
    status.value = "idle";
    error.value = "";
  }

  function syncSourceKey(value: string) {
    selectedSourceKey.value = value;
    query.value = {
      ...query.value,
      sourceKey: value || undefined,
      page: 1,
    };
  }

  async function withBusy(target: { value: boolean }, operation: () => Promise<void>) {
    target.value = true;
    error.value = "";
    try {
      await operation();
    } catch (caught) {
      error.value = String(caught);
      throw caught;
    } finally {
      target.value = false;
    }
  }

  return {
    contract,
    pendingPreview,
    query,
    factPage,
    contractBusy,
    inspectorBusy,
    valuesBusy,
    status,
    error,
    sourceKey,
    contractVersion,
    previewNeedsConfirmation,
    setSourceKey,
    load,
    previewContract,
    applyPendingContract,
    discardPendingContract,
    refreshFacts,
    updateQuery,
    updateValues,
    listAllFacts,
  };
}

function emptyContract(sourceKey: string): CollectionFactContract {
  return {
    contractVersion: DEFAULT_COLLECTION_FACT_CONTRACT_VERSION,
    sourceKey,
    current: {},
    incremental: {},
  };
}

function normalizeContract(candidate: CollectionFactContract): CollectionFactContract {
  const sourceKey = candidate.sourceKey.trim();
  if (!sourceKey) throw new Error("COLLECTION_FACT_SOURCE_REQUIRED");
  return {
    contractVersion: candidate.contractVersion.trim() || DEFAULT_COLLECTION_FACT_CONTRACT_VERSION,
    sourceKey,
    current: { ...candidate.current },
    incremental: { ...candidate.incremental },
  };
}

function cloneContract(contract: CollectionFactContract): CollectionFactContract {
  return {
    contractVersion: contract.contractVersion,
    sourceKey: contract.sourceKey,
    current: { ...contract.current },
    incremental: { ...contract.incremental },
  };
}

function cloneSummary(summary: CollectionFactSyncSummary): CollectionFactSyncSummary {
  return {
    added: [...summary.added],
    retained: [...summary.retained],
    deleted: [...summary.deleted],
    kindChanges: summary.kindChanges.map((change) => ({ ...change })),
    typeChanges: summary.typeChanges.map((change) => ({ ...change })),
    versionOnly: [...summary.versionOnly],
  };
}

function validateValueUpdates(contract: CollectionFactContract, values: CollectionFactValueInput[]) {
  if (!values.length || values.length > MAX_VALUE_UPDATE_COUNT) {
    throw new Error("COLLECTION_FACT_VALUE_BATCH_SIZE_INVALID");
  }
  const definitions = new Map<string, CollectionFactDataType>([
    ...Object.entries(contract.current),
    ...Object.entries(contract.incremental),
  ]);
  const names = new Set<string>();
  for (const item of values) {
    if (!item.name || names.has(item.name)) throw new Error("COLLECTION_FACT_VALUE_NAME_INVALID");
    names.add(item.name);
    const dataType = definitions.get(item.name);
    if (!dataType) throw new Error("COLLECTION_FACT_VALUE_UNKNOWN_NAME");
    if (!matchesDataType(item.value, dataType)) throw new Error("COLLECTION_FACT_VALUE_TYPE_INVALID");
  }
}

function matchesDataType(value: string | null, dataType: CollectionFactDataType): boolean {
  if (value === null) return true;
  if (dataType === "string") return true;
  if (dataType === "integer") return /^[-+]?\d+$/.test(value.trim());
  if (dataType === "number") return value.trim() !== "" && Number.isFinite(Number(value));
  if (dataType === "boolean") return value === "true" || value === "false";
  return value.trim().length > 0 && !Number.isNaN(Date.parse(value));
}
