/**
 * File Path: /automation-world/semantic-mapping-agent/src/app/tauri.ts
 * Description: Thin Tauri transport shared by module-owned IPC facades.
 * Main Features: Detects the desktop runtime and invokes commands without business ownership.
 */
import { invoke } from "@tauri-apps/api/core";

function hasTauriRuntime(): boolean {
  return (
    typeof window !== "undefined" &&
    "__TAURI_INTERNALS__" in (window as Window & { __TAURI_INTERNALS__?: unknown })
  );
}

export function isTauriRuntime(): boolean {
  return hasTauriRuntime();
}

export function invokeCommand<T>(command: string, args?: Record<string, unknown>): Promise<T> {
  if (!hasTauriRuntime()) {
    throw new Error("TAURI_RUNTIME_REQUIRED");
  }
  return invoke<T>(command, args);
}
