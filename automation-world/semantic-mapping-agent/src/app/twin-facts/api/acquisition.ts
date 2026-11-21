/** 采集回环的原生 IPC 封装，临时样本不参与配置缓存。 */
import { invokeCommand } from "../../tauri";
import { localConfiguration, type ConfigurationSnapshot } from "./localConfiguration";

export interface TargetIdentity { plcId: string; dbNumber: number; instanceId: string; sourceGeneration: string }
export interface PointMove { from: string; to: string | null; name: string | null }
export interface LoopbackConfig {
  materialKey: string;
  plcId: string;
  dbNumber: number;
  pointIds: string[];
  target: TargetIdentity;
  moves: PointMove[];
  groupId: string | null;
  configRevision: string | null;
}
export interface SourceChoice { plcId: string; dbNumbers: number[] }
export interface AcquisitionPoint {
  pointId: string; name?: string; dataType: string; valueText: string;
  quality: "good" | "bad"; reason?: string | null; observedAt: string; sampleId?: string;
  sourceType?: "daa" | "external";
}
export interface Summary {
  id: string; sampleId: string; sampledAt: string; pointCount: number; plcId: string;
  dbNumber: number; instanceId: string; sourceType?: "daa" | "external" | null;
}
export interface Detail extends Summary { points: AcquisitionPoint[] }
export interface HistoryPage { items: Summary[]; total: number; page: number; totalPages: number }
export interface Query { materialKey: string; plcId: string; dbNumber: number }
export interface RequestPreview { id: string; sampleId: string; url: string; body: string; sampledAt: string }
export interface PushResult { httpStatus: 200; receipt: { instanceId: string; sampleId: string; status: "committed"; outcome: "created" | "duplicate"; contractVersion: "plc-facts/v2" } }

export const acquisition = {
  options: () => invokeCommand<{ items: SourceChoice[] }>("acquisition_options"),
  latest: (query: Query, pointIds: string[]) => invokeCommand<{ items: AcquisitionPoint[]; missingPointIds: string[] }>("acquisition_latest", { ...query, pointIds }),
  history: (query: Query, from: string, to: string, page: number) =>
    invokeCommand<HistoryPage>("acquisition_history", { ...query, from, to, page }),
  sample: (query: Query, historyId: string) => invokeCommand<Detail>("acquisition_sample", { ...query, historyId }),
  async save(config: LoopbackConfig, expectedRevision: number) {
    const snapshot = await invokeCommand<ConfigurationSnapshot>("save_acquisition_loopback", { config, expectedRevision });
    localConfiguration.value = snapshot;
    return snapshot;
  },
  preview: (historyId: string, sourceSeq: string, expectedRevision: number) =>
    invokeCommand<RequestPreview>("acquisition_preview", { historyId, sourceSeq, expectedRevision }),
  invalidate: () => invokeCommand<void>("acquisition_forget_preview"),
  push: (previewId: string) => invokeCommand<PushResult>("acquisition_test_push", { previewId }),
  readback: (previewId: string) => invokeCommand<Detail | null>("acquisition_readback", { previewId }),
};
