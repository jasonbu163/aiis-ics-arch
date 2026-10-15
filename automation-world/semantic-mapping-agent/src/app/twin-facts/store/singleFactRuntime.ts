/**
 * File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/store/singleFactRuntime.ts
 * Description: Simulation lifecycle and compatible runtime startup preferences.
 * Main Features: Builds saved-source point settings, removes orphan rules on save, persists local app-open preferences, and keeps each runtime lifecycle separate.
 */
import { computed, onBeforeUnmount, ref } from "vue";

import {
  createSimulationRuleInBackend,
  deleteSimulationRuleInBackend,
  getCollectionFactSimulationRuntime,
  loadRuntimeStartupPreferences,
  listCollectionFactsFromBackend,
  listSimulationRulesFromBackend,
  pauseCollectionFactSimulationRuntime,
  resumeCollectionFactSimulationRuntime,
  savedBackendBaseUrl,
  saveRuntimeStartupPreferences,
  startCollectionFactSimulationRuntime,
  stopCollectionFactSimulationRuntime,
  updateSimulationRuleInBackend,
} from "../api";
import { isTauriRuntime } from "../../tauri";
import type {
  CollectionFactDataType,
  CollectionSimulationPointEditor,
  SimulationCurrentTimeMode,
  SimulationRuleConfiguration,
  TwinRuntimeSnapshot,
  RuntimeStartupPreferences,
} from "../types";

const EMPTY_SIMULATION: TwinRuntimeSnapshot = {
  runtimeType: "collection_fact_simulation",
  status: "idle",
  runId: null,
  channel: null,
  profileId: null,
  profileVersion: null,
  profileHash: null,
  processedItems: 0,
  successfulTransactions: 0,
  failedTransactions: 0,
  cursor: null,
  lastErrorCode: null,
  lastErrorMessage: null,
  logs: [],
};

const MIN_INTERVAL_MS = 20;
const MAX_INTERVAL_MS = 86_400_000;
const DEFAULT_MAPPING_FACTS_POLLING_INTERVAL_MS = 1000;

const DEFAULT_RUNTIME_STARTUP_PREFERENCES: RuntimeStartupPreferences = {
  schemaVersion: 1,
  runtimeAutoStart: {
    collectionFactSimulation: {
      enabled: false,
      sourceKey: null,
    },
    apiMappingRuntime: {
      enabled: false,
      factsPollingIntervalMs: DEFAULT_MAPPING_FACTS_POLLING_INTERVAL_MS,
    },
  },
};

export function useSingleFactRuntimeStore(sourceKey: () => string) {
  const simulation = ref<TwinRuntimeSnapshot>({ ...EMPTY_SIMULATION });
  const simulationPoints = ref<CollectionSimulationPointEditor[]>([]);
  const simulationBusy = ref(false);
  const simulationSettingsBusy = ref(false);
  const simulationSettingsDirty = ref(false);
  const pointsBusy = ref(false);
  const simulationError = ref("");
  const runtimeStartupPreferences = ref<RuntimeStartupPreferences>(cloneRuntimeStartupPreferences());
  const runtimeStartupBusy = ref(false);
  const runtimeStartupError = ref("");
  let timer: number | null = null;

  const enabledPointCount = computed(
    () => simulationPoints.value.filter((point) => point.writeCurrentTime || hasSequenceValues(point)).length,
  );
  const pointsValid = computed(() => simulationPoints.value.every((point) => point.validationError === null));

  async function loadSimulationPoints() {
    pointsBusy.value = true;
    simulationError.value = "";
    try {
      const source = sourceKey();
      if (!source) {
        simulationPoints.value = [];
        simulationSettingsDirty.value = false;
        return;
      }
      const [firstPage, savedRules] = await Promise.all([
        listCollectionFactsFromBackend({ sourceKey: source, page: 1, pageSize: 100 }),
        listSimulationRulesFromBackend(),
      ]);
      const facts = [...firstPage.items];
      const pageCount = Math.ceil(firstPage.total / firstPage.pageSize);
      for (let page = 2; page <= pageCount; page += 1) {
        const nextPage = await listCollectionFactsFromBackend({ sourceKey: source, page, pageSize: firstPage.pageSize });
        facts.push(...nextPage.items);
      }
      const rulesByFactName = new Map(
        savedRules
          .filter((rule) => rule.sourceKey === source)
          .map((rule) => [rule.factName, rule]),
      );
      simulationPoints.value = facts
        .sort((left, right) => left.name.localeCompare(right.name))
        .map((fact) => {
          const rule = rulesByFactName.get(fact.name);
          return {
            ruleId: rule?.id ?? null,
            factName: fact.name,
            dataType: fact.dataType,
            valuesJson: JSON.stringify(rule?.sequence ?? []),
            intervalMs: rule?.intervalMs ?? 1000,
            writeCurrentTime: rule?.writeCurrentTime ?? false,
            currentTimeMode: rule?.currentTimeMode ?? "utc",
            currentTimeZone: rule?.currentTimeZone ?? null,
            validationError: null,
          };
        });
      simulationPoints.value.forEach(validatePoint);
      simulationSettingsDirty.value = false;
    } catch (caught) {
      simulationError.value = String(caught);
      throw caught;
    } finally {
      pointsBusy.value = false;
    }
  }

  function updatePointValues(factName: string, valuesJson: string) {
    const point = simulationPoints.value.find((candidate) => candidate.factName === factName);
    if (!point) return;
    point.valuesJson = valuesJson;
    validatePoint(point);
    simulationSettingsDirty.value = true;
  }

  function updatePointInterval(factName: string, intervalMs: number) {
    const point = simulationPoints.value.find((candidate) => candidate.factName === factName);
    if (!point) return;
    point.intervalMs = intervalMs;
    validatePoint(point);
    simulationSettingsDirty.value = true;
  }

  function updatePointCurrentTime(
    factName: string,
    writeCurrentTime: boolean,
    currentTimeMode: SimulationCurrentTimeMode = "utc",
    currentTimeZone: string | null = null,
  ) {
    const point = simulationPoints.value.find((candidate) => candidate.factName === factName);
    if (!point || point.dataType !== "datetime") return;
    point.writeCurrentTime = writeCurrentTime;
    point.currentTimeMode = writeCurrentTime ? currentTimeMode : "utc";
    point.currentTimeZone = writeCurrentTime && currentTimeMode === "custom" ? currentTimeZone : null;
    validatePoint(point);
    simulationSettingsDirty.value = true;
  }

  function validatePoint(point: CollectionSimulationPointEditor) {
    if (!Number.isInteger(point.intervalMs) || point.intervalMs < MIN_INTERVAL_MS || point.intervalMs > MAX_INTERVAL_MS) {
      point.validationError = "SIMULATION_POINT_INTERVAL_INVALID";
      return;
    }
    if (point.writeCurrentTime && point.dataType !== "datetime") {
      point.validationError = "SIMULATION_POINT_CURRENT_TIME_INVALID";
      return;
    }
    if (point.writeCurrentTime) {
      if (!["utc", "system", "custom"].includes(point.currentTimeMode)) {
        point.validationError = "SIMULATION_POINT_CURRENT_TIME_MODE_INVALID";
      } else if (point.currentTimeMode === "custom" && !point.currentTimeZone?.trim()) {
        point.validationError = "SIMULATION_POINT_CUSTOM_TIME_ZONE_REQUIRED";
      } else {
        point.validationError = null;
      }
      return;
    }
    try {
      const values = JSON.parse(point.valuesJson) as unknown;
      if (!Array.isArray(values)) {
        point.validationError = "SIMULATION_POINT_VALUES_ARRAY_REQUIRED";
        return;
      }
      point.validationError = values.every((value) => matchesDataType(value, point.dataType))
        ? null
        : "SIMULATION_POINT_VALUE_TYPE_INVALID";
    } catch {
      point.validationError = "SIMULATION_POINT_VALUES_JSON_INVALID";
    }
  }

  async function saveSimulationSettings() {
    await withBusy(simulationSettingsBusy, simulationError, async () => {
      const source = sourceKey().trim();
      if (!source) throw new Error("COLLECTION_SIMULATION_SOURCE_REQUIRED");
      simulationPoints.value.forEach(validatePoint);
      if (!pointsValid.value) throw new Error("SIMULATION_POINT_CONFIGURATION_INVALID");

      // Use the complete, fresh source list, never the visible or filtered editor rows.
      const firstPage = await listCollectionFactsFromBackend({ sourceKey: source, page: 1, pageSize: 100 });
      const facts = [...firstPage.items];
      const pageCount = Math.ceil(firstPage.total / firstPage.pageSize);
      for (let page = 2; page <= pageCount; page += 1) {
        const nextPage = await listCollectionFactsFromBackend({ sourceKey: source, page, pageSize: firstPage.pageSize });
        facts.push(...nextPage.items);
      }
      const factNames = new Set(facts.map((fact) => fact.name));
      const savedRules = await listSimulationRulesFromBackend();

      for (const point of simulationPoints.value) {
        if (!factNames.has(point.factName)) continue;
        const sequence = point.writeCurrentTime ? [] : JSON.parse(point.valuesJson) as unknown[];
        const input = {
          sourceKey: source,
          factName: point.factName,
          sequence,
          intervalMs: point.intervalMs,
          enabled: point.writeCurrentTime || sequence.length > 0,
          writeCurrentTime: point.writeCurrentTime,
          currentTimeMode: point.currentTimeMode,
          currentTimeZone: point.currentTimeZone,
        };
        const saved = point.ruleId
          ? await updateSimulationRuleInBackend(point.ruleId, input)
          : await createSimulationRuleInBackend(input);
        applySavedSimulationRule(point, saved);
      }

      for (const rule of savedRules) {
        if (rule.sourceKey === source && !factNames.has(rule.factName)) {
          await deleteSimulationRuleInBackend(rule.id);
        }
      }

      await loadSimulationPoints();
      simulationSettingsDirty.value = false;
    });
  }

  async function refresh() {
    simulation.value = await getCollectionFactSimulationRuntime();
  }

  async function loadStartupPreferences() {
    if (!isTauriRuntime()) return;
    runtimeStartupBusy.value = true;
    runtimeStartupError.value = "";
    try {
      runtimeStartupPreferences.value = await loadRuntimeStartupPreferences();
    } catch (caught) {
      runtimeStartupError.value = String(caught);
      throw caught;
    } finally {
      runtimeStartupBusy.value = false;
    }
  }

  function autoStartSimulationSourceKey(): string | null {
    const autoStart = runtimeStartupPreferences.value.runtimeAutoStart.collectionFactSimulation;
    return autoStart.enabled ? autoStart.sourceKey : null;
  }

  async function setSimulationAutoStart(enabled: boolean) {
    const source = sourceKey().trim();
    if (enabled && !source) throw new Error("RUNTIME_STARTUP_SIMULATION_SOURCE_REQUIRED");
    const current = runtimeStartupPreferences.value;
    await saveStartupPreferences({
      ...current,
      runtimeAutoStart: {
        ...current.runtimeAutoStart,
        collectionFactSimulation: {
          enabled,
          sourceKey: enabled ? source : current.runtimeAutoStart.collectionFactSimulation.sourceKey,
        },
      },
    });
  }

  async function setApiMappingRuntimeAutoStart(enabled: boolean) {
    const current = runtimeStartupPreferences.value;
    await saveStartupPreferences({
      ...current,
      runtimeAutoStart: {
        ...current.runtimeAutoStart,
        apiMappingRuntime: {
          ...current.runtimeAutoStart.apiMappingRuntime,
          enabled,
        },
      },
    });
  }

  async function autoStartSimulationIfEnabled() {
    const autoStart = runtimeStartupPreferences.value.runtimeAutoStart.collectionFactSimulation;
    if (!autoStart.enabled) return;
    if (!autoStart.sourceKey || autoStart.sourceKey !== sourceKey().trim()) {
      throw new Error("RUNTIME_STARTUP_SIMULATION_SOURCE_MISMATCH");
    }
    await simulationAction("start");
  }

  async function simulationAction(action: "start" | "pause" | "resume" | "stop") {
    await withBusy(simulationBusy, simulationError, async () => {
      if (action === "start") {
        if (simulationSettingsDirty.value) throw new Error("SIMULATION_SETTINGS_SAVE_REQUIRED");
        simulationPoints.value.forEach(validatePoint);
        if (!pointsValid.value) throw new Error("SIMULATION_POINT_CONFIGURATION_INVALID");
        if (enabledPointCount.value === 0) throw new Error("SIMULATION_NO_ENABLED_POINTS");
        const source = sourceKey().trim();
        if (!source) throw new Error("COLLECTION_SIMULATION_SOURCE_REQUIRED");
        simulation.value = await startCollectionFactSimulationRuntime({
          backendBaseUrl: savedBackendBaseUrl(),
          sourceKey: source,
        });
      } else if (action === "pause") simulation.value = await pauseCollectionFactSimulationRuntime();
      else if (action === "resume") simulation.value = await resumeCollectionFactSimulationRuntime();
      else simulation.value = await stopCollectionFactSimulationRuntime();
    });
  }

  function startPolling() {
    if (timer !== null) return;
    void refresh().catch(setRefreshError);
    timer = window.setInterval(() => void refresh().catch(setRefreshError), 1000);
  }

  function stopPolling() {
    if (timer !== null) window.clearInterval(timer);
    timer = null;
  }

  function setRefreshError(caught: unknown) {
    const message = String(caught);
    simulationError.value ||= message;
  }

  async function withBusy(target: { value: boolean }, error: { value: string }, operation: () => Promise<void>) {
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

  async function saveStartupPreferences(preferences: RuntimeStartupPreferences) {
    if (!isTauriRuntime()) throw new Error("RUNTIME_STARTUP_TAURI_REQUIRED");
    runtimeStartupBusy.value = true;
    runtimeStartupError.value = "";
    try {
      await saveRuntimeStartupPreferences(preferences);
      runtimeStartupPreferences.value = preferences;
    } catch (caught) {
      runtimeStartupError.value = String(caught);
      throw caught;
    } finally {
      runtimeStartupBusy.value = false;
    }
  }

  onBeforeUnmount(stopPolling);
  return {
    simulation,
    simulationPoints,
    simulationBusy,
    simulationSettingsBusy,
    simulationSettingsDirty,
    pointsBusy,
    simulationError,
    runtimeStartupPreferences,
    runtimeStartupBusy,
    runtimeStartupError,
    enabledPointCount,
    pointsValid,
    loadSimulationPoints,
    updatePointValues,
    updatePointInterval,
    updatePointCurrentTime,
    saveSimulationSettings,
    refresh,
    loadStartupPreferences,
    autoStartSimulationSourceKey,
    setSimulationAutoStart,
    setApiMappingRuntimeAutoStart,
    autoStartSimulationIfEnabled,
    simulationAction,
    startPolling,
    stopPolling,
  };
}

function cloneRuntimeStartupPreferences(): RuntimeStartupPreferences {
  return {
    schemaVersion: DEFAULT_RUNTIME_STARTUP_PREFERENCES.schemaVersion,
    runtimeAutoStart: {
      collectionFactSimulation: {
        ...DEFAULT_RUNTIME_STARTUP_PREFERENCES.runtimeAutoStart.collectionFactSimulation,
      },
      apiMappingRuntime: {
        ...DEFAULT_RUNTIME_STARTUP_PREFERENCES.runtimeAutoStart.apiMappingRuntime,
      },
    },
  };
}

function hasSequenceValues(point: CollectionSimulationPointEditor): boolean {
  try {
    const values = JSON.parse(point.valuesJson) as unknown;
    return Array.isArray(values) && values.length > 0;
  } catch {
    return false;
  }
}

function applySavedSimulationRule(
  point: CollectionSimulationPointEditor,
  rule: SimulationRuleConfiguration,
) {
  point.ruleId = rule.id;
  point.valuesJson = JSON.stringify(rule.sequence);
  point.intervalMs = rule.intervalMs;
  point.writeCurrentTime = rule.writeCurrentTime;
  point.currentTimeMode = rule.currentTimeMode;
  point.currentTimeZone = rule.currentTimeZone;
  point.validationError = null;
}

function matchesDataType(value: unknown, dataType: CollectionFactDataType): boolean {
  if (dataType === "string") return typeof value === "string";
  if (dataType === "integer") return typeof value === "number" && Number.isInteger(value);
  if (dataType === "number") return typeof value === "number" && Number.isFinite(value);
  if (dataType === "boolean") return typeof value === "boolean";
  return typeof value === "string"
    && value.length >= 20
    && value.includes("T")
    && /(?:Z|[+-]\d{2}:\d{2})$/i.test(value)
    && !Number.isNaN(Date.parse(value));
}
