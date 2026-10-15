/**
 * File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/store/apiFirstMappingRuntime.ts
 * Description: Reactive controls for the continuous API-first Mapping Runtime.
 * Main Features:
 *   - Starts one Tauri HTTP-only runtime from the saved Backend connection profile
 *   - Polls Runtime status independently from Simulation and legacy Service Projection
 *   - Applies local app-open auto-start only through the same normal start action
 */
import { onBeforeUnmount, ref } from "vue";

import {
  getApiFirstMappingRuntime,
  pauseApiFirstMappingRuntime,
  resumeApiFirstMappingRuntime,
  savedBackendBaseUrl,
  startApiFirstMappingRuntime,
  stopApiFirstMappingRuntime,
} from "../api";
import type { TwinRuntimeSnapshot } from "../types";

const EMPTY_API_FIRST_MAPPING_RUNTIME: TwinRuntimeSnapshot = {
  runtimeType: "api_first_mapping",
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

export function useApiFirstMappingRuntimeStore() {
  const runtime = ref<TwinRuntimeSnapshot>({ ...EMPTY_API_FIRST_MAPPING_RUNTIME });
  const busy = ref(false);
  const error = ref("");
  let timer: number | null = null;

  async function refresh() {
    runtime.value = await getApiFirstMappingRuntime();
  }

  async function action(
    actionName: "start" | "pause" | "resume" | "stop",
  ) {
    await withBusy(async () => {
      if (actionName === "start") {
        runtime.value = await startApiFirstMappingRuntime({
          backendBaseUrl: savedBackendBaseUrl(),
        });
      } else if (actionName === "pause") {
        runtime.value = await pauseApiFirstMappingRuntime();
      } else if (actionName === "resume") {
        runtime.value = await resumeApiFirstMappingRuntime();
      } else {
        runtime.value = await stopApiFirstMappingRuntime();
      }
    });
  }

  async function autoStartIfEnabled(enabled: boolean) {
    if (enabled) await action("start");
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

  async function withBusy(operation: () => Promise<void>) {
    busy.value = true;
    error.value = "";
    try {
      await operation();
    } catch (caught) {
      error.value = String(caught);
      throw caught;
    } finally {
      busy.value = false;
    }
  }

  function setRefreshError(caught: unknown) {
    error.value ||= String(caught);
  }

  onBeforeUnmount(stopPolling);
  return {
    runtime,
    busy,
    error,
    refresh,
    action,
    autoStartIfEnabled,
    startPolling,
    stopPolling,
  };
}
