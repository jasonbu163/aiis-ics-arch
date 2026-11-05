/** SMA HTTP映射启动偏好；不暴露已退役的producer状态。 */
import { ref } from "vue";
import { loadRuntimeStartupPreferences, saveRuntimeStartupPreferences } from "../api";
import { isTauriRuntime } from "../../tauri";
import type { RuntimeStartupPreferences } from "../types";

export function useMappingStartupStore() {
  const runtimeStartupPreferences = ref<RuntimeStartupPreferences>({ schemaVersion: 1, runtimeAutoStart: {
    apiMappingRuntime: { enabled: false, factsPollingIntervalMs: 1000 },
  } });
  const runtimeStartupBusy = ref(false);
  const runtimeStartupError = ref("");
  async function perform(operation: () => Promise<void>) {
    runtimeStartupBusy.value = true;
    runtimeStartupError.value = "";
    try { await operation(); }
    catch (caught) { runtimeStartupError.value = String(caught); throw caught; }
    finally { runtimeStartupBusy.value = false; }
  }
  async function loadStartupPreferences() {
    if (!isTauriRuntime()) return;
    await perform(async () => { runtimeStartupPreferences.value = await loadRuntimeStartupPreferences(); });
  }
  async function setApiMappingRuntimeAutoStart(enabled: boolean) {
    await perform(async () => {
      const current = runtimeStartupPreferences.value;
      const next = { ...current, runtimeAutoStart: { apiMappingRuntime: { ...current.runtimeAutoStart.apiMappingRuntime, enabled } } };
      await saveRuntimeStartupPreferences(next);
      runtimeStartupPreferences.value = next;
    });
  }
  return { runtimeStartupPreferences, runtimeStartupBusy, runtimeStartupError, loadStartupPreferences, setApiMappingRuntimeAutoStart };
}
