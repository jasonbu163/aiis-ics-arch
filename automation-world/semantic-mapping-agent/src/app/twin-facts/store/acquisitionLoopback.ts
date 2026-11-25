/** 采集点位只读查询，返回值只保留在当前会话。 */
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { acquisition, type AcquisitionPoint, type SourceChoice } from "../api/acquisition";
import { loadLocalConfiguration, localConfiguration } from "../api/localConfiguration";

export function useAcquisitionLatest() {
  const config = ref({ materialKey: "", plcId: "", dbNumber: 0, pointIds: [] as string[] });
  const ready = ref(false);
  const busy = ref("");
  const error = ref("");
  const errorAt = ref("");
  const sources = ref<SourceChoice[] | null>(null);
  const choices = ref<AcquisitionPoint[]>([]);
  const latest = ref<AcquisitionPoint[] | null>(null);
  const missing = ref<string[]>([]);
  const allPoints = ref(true);
  let epoch = 0;
  const materials = computed(() => localConfiguration.value?.document.materials.filter(
    item => item.httpMethod === "GET" && item.path === "/api/v1/acquisition-data/latest",
  ) ?? []);
  const databases = computed(() => sources.value?.find(item => item.plcId === config.value.plcId)?.dbNumbers ?? []);
  const materialReady = computed(() => materials.value.some(item => item.materialKey === config.value.materialKey));
  const sourceReady = computed(() => ready.value && materialReady.value && Boolean(config.value.plcId && config.value.dbNumber));
  const pointsReady = computed(() => allPoints.value || config.value.pointIds.length > 0);
  const query = () => ({ materialKey: config.value.materialKey, plcId: config.value.plcId, dbNumber: config.value.dbNumber });

  function invalidate() { epoch++; }

  function clearSourceResults() {
    choices.value = [];
    latest.value = null;
    missing.value = [];
  }

  watch(() => JSON.stringify(config.value), invalidate, { flush: "sync" });
  watch(() => JSON.stringify(query()), () => {
    clearSourceResults();
  }, { flush: "sync" });
  watch([allPoints, () => JSON.stringify(config.value.pointIds)], () => {
    latest.value = null;
    missing.value = [];
  });
  watch(() => JSON.stringify(localConfiguration.value?.document.connection), () => {
    if (busy.value === "load") return;
    invalidate();
    sources.value = null;
    clearSourceResults();
  });
  async function run<T>(name: string, action: () => Promise<T>, apply: (value: T) => void) {
    if (busy.value) return;
    const current = epoch;
    error.value = "";
    errorAt.value = "";
    busy.value = name;
    try {
      const result = await action();
      if (current === epoch) apply(result);
    } catch (failure) {
      if (current === epoch) {
        error.value = String(failure);
        errorAt.value = name;
      }
    } finally {
      busy.value = "";
    }
  }

  function restoreSaved() {
    return run("load", loadLocalConfiguration, snapshot => {
      const stored = snapshot.document.acquisitionLoopback;
      config.value = { materialKey: stored?.materialKey ?? "", plcId: stored?.plcId ?? "", dbNumber: stored?.dbNumber ?? 0, pointIds: [...(stored?.pointIds ?? [])] };
      if (!stored && materials.value.length === 1) config.value.materialKey = materials.value[0].materialKey;
      allPoints.value = !config.value.pointIds.length;
      ready.value = true;
      clearSourceResults();
    });
  }

  function loadSources() {
    return run("options", acquisition.options, result => {
      sources.value = result.items;
    });
  }

  function sourceChanged() {
    config.value.dbNumber = 0;
    dbChanged();
  }
  function dbChanged() {
    config.value.pointIds = [];
    allPoints.value = true;
    clearSourceResults();
  }

  function testLatest(allCandidates = false) {
    if (!sourceReady.value) return;
    invalidate();
    latest.value = null;
    missing.value = [];
    if (!allCandidates && !allPoints.value && !config.value.pointIds.length) {
      error.value = "SMA_ACQUISITION_SELECTION_REQUIRED";
      errorAt.value = "latest";
      return;
    }
    return run("latest", () => acquisition.latest(query(), allCandidates || allPoints.value ? [] : [...config.value.pointIds]), result => {
      if (allCandidates || allPoints.value) choices.value = result.items;
      latest.value = result.items;
      missing.value = result.missingPointIds;
    });
  }

  function changeAllPoints(selected: boolean) {
    allPoints.value = selected;
    if (selected) config.value.pointIds = [];
    invalidate();
  }

  onBeforeUnmount(invalidate);
  return { config, ready, busy, error, errorAt, sources, choices, latest, missing, allPoints, materials, databases,
    materialReady, pointsReady, restoreSaved, loadSources, sourceChanged, dbChanged, testLatest, changeAllPoints };
}
