/** SMA只读源事实状态：查询、分页及导出；来源缺失保持null。 */
import { computed, ref } from "vue";

import {
  listCollectionFactsFromBackend,
  readCollectionFactsContractFromBackend,
} from "../api";
import type {
  BackendCollectionFactListQuery,
  BackendCollectionFactPage,
  CollectionFactContract,
} from "../types";

const DEFAULT_SOURCE_KEY = "";
const COLLECTION_FACT_SOURCE_NOT_FOUND = "collection_fact_source_not_found";

const EMPTY_PAGE: BackendCollectionFactPage = { items: [], page: 1, pageSize: 25, total: 0 };

export function useCollectionFactsStore() {
  const selectedSourceKey = ref(DEFAULT_SOURCE_KEY);
  const contract = ref<CollectionFactContract | null>(null);
  const query = ref<BackendCollectionFactListQuery>({
    sourceKey: DEFAULT_SOURCE_KEY,
    page: 1,
    pageSize: 25,
  });
  const factPage = ref<BackendCollectionFactPage>(EMPTY_PAGE);
  const contractBusy = ref(false);
  const inspectorBusy = ref(false);
  const error = ref("");
  const sourceKey = computed(() => selectedSourceKey.value);
  async function load() {
    await withBusy(contractBusy, async () => {
      const source = sourceKey.value;
      contract.value = null;
      if (!source) {
        await refreshFacts();
        return;
      }
      let loaded: CollectionFactContract | null;
      try {
        loaded = await readCollectionFactsContractFromBackend(source);
      } catch (caught) {
        if (!(caught instanceof Error) || caught.message !== COLLECTION_FACT_SOURCE_NOT_FOUND) throw caught;
        loaded = null;
      }
      await refreshFacts();
      contract.value = loaded;
    });
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
    factPage.value = EMPTY_PAGE;
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
    query,
    factPage,
    contractBusy,
    inspectorBusy,
    error,
    sourceKey,
    setSourceKey,
    load,
    refreshFacts,
    updateQuery,
    listAllFacts,
  };
}
