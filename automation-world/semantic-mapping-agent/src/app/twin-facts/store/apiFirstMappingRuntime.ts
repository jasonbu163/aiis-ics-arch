/**
 * File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/store/apiFirstMappingRuntime.ts
 * Description: Reactive controls for the continuous API-first Mapping Runtime.
 * Main Features:
 *   - Polls the HTTP Mapping runtime status independently from source inspection
 *   - Preserves applicable pause and stop controls
 */
import { onBeforeUnmount, ref } from "vue";

import {
  getApiFirstMappingRuntime,
  pauseApiFirstMappingRuntime,
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
    actionName: "pause" | "stop",
  ) {
    await withBusy(async () => {
      if (actionName === "pause") {
        runtime.value = await pauseApiFirstMappingRuntime();
      } else if (actionName === "stop") {
        runtime.value = await stopApiFirstMappingRuntime();
      }
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
    refresh: () => withBusy(refresh),
    action,
    startPolling,
    stopPolling,
  };
}
