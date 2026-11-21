/** 采集回环草稿和最新操作状态，只驻留在页面内存。 */
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { acquisition, type AcquisitionPoint, type Detail, type HistoryPage, type LoopbackConfig, type RequestPreview, type PushResult, type SourceChoice } from "../api/acquisition";
import { loadLocalConfiguration, localConfiguration } from "../api/localConfiguration";
import { isTauriRuntime } from "../../tauri";

const emptyConfig = (): LoopbackConfig => ({
  materialKey: "", plcId: "", dbNumber: 0, pointIds: [],
  target: { plcId: "", dbNumber: 0, instanceId: "", sourceGeneration: "" },
  moves: [], groupId: null, configRevision: null,
});
const clone = (value: LoopbackConfig): LoopbackConfig => JSON.parse(JSON.stringify(value)) as LoopbackConfig;

export function useAcquisitionLoopback() {
  const config = ref(emptyConfig());
  const revision = ref(0);
  const ready = ref(false);
  const busy = ref("");
  const error = ref("");
  const sources = ref<SourceChoice[] | null>(null);
  const choices = ref<AcquisitionPoint[]>([]);
  const latest = ref<AcquisitionPoint[] | null>(null);
  const missing = ref<string[]>([]);
  const allPoints = ref(true);
  const history = ref<HistoryPage | null>(null);
  const detail = ref<Detail | null>(null);
  const from = ref("");
  const to = ref("");
  const sourceSeq = ref("");
  const preview = ref<RequestPreview | null>(null);
  const receipt = ref<PushResult | null>(null);
  const readback = ref<Detail | null>();
  const sendState = ref<"ready" | "unknown" | "done" | "rejected">("ready");
  let epoch = 0;
  let running = 0;
  const materials = computed(() => localConfiguration.value?.document.materials.filter(
    item => item.httpMethod === "GET" && item.path === "/api/v1/acquisition-data/latest",
  ) ?? []);
  const databases = computed(() => sources.value?.find(item => item.plcId === config.value.plcId)?.dbNumbers ?? []);
  const sourceReady = computed(() => ready.value && Boolean(config.value.materialKey && config.value.plcId && config.value.dbNumber));
  const mixed = computed(() => new Set(latest.value?.map(point => point.sampleId).filter(Boolean)).size > 1);
  const canPost = computed(() => Boolean(preview.value) && (sendState.value === "ready" || sendState.value === "unknown"));
  const canReadback = computed(() => Boolean(preview.value) && (sendState.value === "done" || sendState.value === "unknown"));
  const query = () => ({ materialKey: config.value.materialKey, plcId: config.value.plcId, dbNumber: config.value.dbNumber });

  function invalidate() {
    epoch++;
    const hadPreview = preview.value !== null || busy.value === "preview";
    preview.value = null;
    receipt.value = null;
    readback.value = undefined;
    sendState.value = "ready";
    if (hadPreview && isTauriRuntime()) void acquisition.invalidate().catch(() => {});
  }

  function clearSourceResults() {
    choices.value = [];
    latest.value = null;
    missing.value = [];
    history.value = null;
    detail.value = null;
  }

  watch(() => JSON.stringify(config.value), invalidate, { flush: "sync" });
  watch(() => JSON.stringify(query()), () => {
    clearSourceResults();
  });
  watch([allPoints, () => JSON.stringify(config.value.pointIds)], () => {
    latest.value = null;
    missing.value = [];
  });
  watch([sourceSeq, from, to], () => {
    invalidate();
  }, { flush: "sync" });
  watch(() => JSON.stringify(localConfiguration.value?.document.connection), () => {
    if (busy.value === "load") return;
    invalidate();
    sources.value = null;
    clearSourceResults();
  });
  watch(() => localConfiguration.value?.revision, (value) => {
    if (ready.value && busy.value !== "save" && busy.value !== "load" && revision.value !== value) invalidate();
  });

  async function run<T>(name: string, action: () => Promise<T>, apply: (value: T) => void) {
    if (busy.value) return;
    const token = ++running;
    const current = epoch;
    error.value = "";
    busy.value = name;
    try {
      const result = await action();
      if (current === epoch) apply(result);
    } catch (failure) {
      if (current === epoch) {
        error.value = String(failure);
        if (name === "push") sendState.value = error.value.includes("SMA_ACQUISITION_RESULT_UNKNOWN") ? "unknown" : "rejected";
      }
    } finally {
      if (running === token) busy.value = "";
    }
  }

  function restoreSaved() {
    return run("load", loadLocalConfiguration, snapshot => {
      const stored = snapshot.document.acquisitionLoopback;
      config.value = stored ? clone(stored) : emptyConfig();
      if (!stored && materials.value.length === 1) config.value.materialKey = materials.value[0].materialKey;
      allPoints.value = !config.value.pointIds.length;
      revision.value = snapshot.revision;
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
    config.value.moves = [];
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
      return;
    }
    return run("latest", () => acquisition.latest(query(), allCandidates || allPoints.value ? [] : [...config.value.pointIds]), result => {
      if (allCandidates || allPoints.value) choices.value = result.items;
      latest.value = result.items;
      missing.value = result.missingPointIds;
    });
  }

  function applyHistory(page = 1) {
    if (!sourceReady.value) return;
    invalidate();
    history.value = null;
    detail.value = null;
    const asShanghai = (value: string) => value.length === 16 ? value + ":00+08:00" : value + "+08:00";
    return run("history", () => acquisition.history(query(), asShanghai(from.value), asShanghai(to.value), page), result => {
      history.value = result;
    });
  }

  function pickSample(id: string) {
    invalidate();
    detail.value = null;
    return run("detail", () => acquisition.sample(query(), id), result => {
      detail.value = result;
    });
  }

  function save() {
    if (!allPoints.value && config.value.pointIds.length === 0) {
      error.value = "SMA_ACQUISITION_SELECTION_REQUIRED";
      return;
    }
    const pruned = clone(config.value);
    if (allPoints.value) pruned.pointIds = [];
    pruned.moves = pruned.moves.filter(item => (item.to || item.name) && (!pruned.pointIds.length || pruned.pointIds.includes(item.from)));
    const configToSave = { ...pruned, groupId: pruned.groupId || null, configRevision: pruned.configRevision || null };
    return run("save", () => acquisition.save(configToSave, revision.value), snapshot => {
      revision.value = snapshot.revision;
      config.value = configToSave;
    });
  }
  const saved = computed(() => (allPoints.value || config.value.pointIds.length > 0)
    && JSON.stringify(localConfiguration.value?.document.acquisitionLoopback) === JSON.stringify(config.value)
    && revision.value === localConfiguration.value?.revision);
  function prepare() {
    if (!detail.value || !saved.value) return;
    const id = detail.value.id;
    invalidate();
    return run("preview", () => acquisition.preview(id, sourceSeq.value, revision.value), result => {
      preview.value = result;
    });
  }

  function push() {
    const id = preview.value?.id;
    if (!id || !canPost.value || !saved.value) return;
    return run("push", () => acquisition.push(id), result => {
      receipt.value = result;
      sendState.value = "done";
    });
  }

  function checkTarget() {
    const id = preview.value?.id;
    if (!id || !canReadback.value) return;
    return run("readback", () => acquisition.readback(id), result => {
      readback.value = result;
    });
  }

  function changeAllPoints(selected: boolean) {
    allPoints.value = selected;
    if (selected) config.value.pointIds = [];
    invalidate();
  }

  function setMove(from: string, key: "to" | "name", value: string) {
    const existing = config.value.moves.find(item => item.from === from);
    if (existing) {
      existing[key] = value || null;
      if (!existing.to && !existing.name) config.value.moves = config.value.moves.filter(item => item.from !== from);
    } else if (value) {
      config.value.moves.push({ from, to: key === "to" ? value : null, name: key === "name" ? value : null });
    }
  }

  onBeforeUnmount(invalidate);
  return { config, ready, busy, error, sources, choices, latest, missing, allPoints, history, detail,
    from, to, sourceSeq, preview, receipt, readback, sendState, materials, databases, sourceReady,
    mixed, canPost, canReadback, saved, restoreSaved, loadSources, sourceChanged, dbChanged, testLatest,
    applyHistory, pickSample, save, prepare, push, checkTarget, changeAllPoints, setMove };
}
