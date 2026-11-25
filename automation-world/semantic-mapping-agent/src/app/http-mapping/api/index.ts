/** SMA HTTP 页面仅通过 Tauri 调用 Rust；配置沿用 SQLite revision 门面。 */
import { invokeCommand } from "../../tauri";
import type { SourceChoice } from "../../twin-facts/api/acquisition";
import { changeConfiguration } from "../../twin-facts/api/localConfiguration";
import type {
  LatestSource, PostPreview, PostResult, RuntimeCounters, RuntimeLimits, RuntimeSide, RuntimeStatus,
  Scalar, SourceTestResult,
} from "../types";

export const httpMapping = {
  acquisitionOptions: () => invokeCommand<{ items: SourceChoice[] }>("acquisition_options"),
  testSource: (sourceKey: string) => invokeCommand<SourceTestResult>("sma_test_source", { sourceKey }),
  latestSources: () => invokeCommand<LatestSource[]>("sma_latest_sources"),
  previewMapping: (mappingId: string, expectedRevision: number) =>
    invokeCommand<PostPreview>("sma_preview_mapping", { mappingId, expectedRevision }),
  previewTarget: (targetApiId: string, expectedRevision: number, values: Record<string, Scalar>) =>
    invokeCommand<PostPreview>("sma_preview_target", { targetApiId, expectedRevision, values }),
  confirm: (token: string) => invokeCommand<PostResult>("sma_confirm_post", { token }),
  cancel: (token: string) => invokeCommand<void>("sma_cancel_post", { token }),
  status: () => invokeCommand<RuntimeStatus>("sma_runtime_status"),
  start: (side: RuntimeSide) => invokeCommand<RuntimeCounters>("sma_start_runtime", { side }),
  stop: (side: RuntimeSide) => invokeCommand<RuntimeCounters>("sma_stop_runtime", { side }),
  saveLimits: (payload: RuntimeLimits, revision: number) =>
    changeConfiguration({ kind: "runtimeLimits", resource: "runtimeLimits", id: null, payload }, revision),
};
