/** SMA HTTP 映射的配置、快照与运行 IPC 类型。 */
import type { CollectionFactDataType } from "../twin-facts/types";

export type Scalar = string | number | boolean;
export interface ResponseCondition { path: string; equals: Scalar }
export interface PointSelector { path: string; key: string; value: Scalar }
export interface HttpPointDefinition {
  pointKey: string;
  name: string;
  dataType: CollectionFactDataType;
  path: string;
  selector?: PointSelector | null;
  qualityPath?: string | null;
  observedAtPath?: string | null;
  sampleIdPath?: string | null;
  acceptedQuality?: string[];
}
export interface HttpSourceInput {
  sourceKey: string;
  name: string;
  url: string;
  query: Record<string, string>;
  intervalMs: number;
  timeoutMs: number;
  enabled: boolean;
  responsePath?: string | null;
  responseCondition?: ResponseCondition | null;
  points: HttpPointDefinition[];
}
export interface HttpSource extends HttpSourceInput { id: string }
export interface PointValue {
  pointKey: string;
  value: Scalar | null;
  quality: string | null;
  observedAt: string | null;
  sampleId: string | null;
  errorCode: string | null;
}
export interface SourceTestResult {
  sourceKey: string;
  httpStatus: number | null;
  response: unknown;
  points: PointValue[];
  errorCode: string | null;
}
export interface SourceSnapshot {
  sourceKey: string;
  version: number;
  collectedAt: string;
  points: PointValue[];
}
export interface LatestSource {
  sourceKey: string;
  lastAttemptAt: string | null;
  lastErrorCode: string | null;
  fromPreviousSession: boolean;
  snapshot: SourceSnapshot | null;
}
export interface PreviewSource {
  sourceKey: string;
  version: number | null;
  collectedAt: string | null;
  points: PointValue[];
}
export interface FieldDiagnostic { parameterKey: string; errorCode: string }
export interface PostRequest {
  method: "POST";
  url: string;
  headers: [string, string][];
  body: unknown;
}
export interface PostPreview {
  token: string | null;
  revision: number;
  request: PostRequest | null;
  sources: PreviewSource[];
  diagnostics: FieldDiagnostic[];
}
export type PostStatus = "http_succeeded" | "succeeded" | "failed" | "unknown" | "blocked";
export interface PostResult {
  runId: string;
  status: PostStatus;
  httpStatus: number | null;
  errorCode: string | null;
  response: unknown;
  finishedAt: string;
  sources: PreviewSource[];
  diagnostics: FieldDiagnostic[];
}
export type RuntimeSide = "get" | "post";
export interface RuntimeLimits {
  getConcurrency: number;
  getQueue: number;
  postConcurrency: number;
  postQueue: number;
  perTargetConcurrency: number;
}
export interface RuntimeCounters {
  phase: "stopped" | "running" | "stopping";
  active: number;
  inFlight: number;
  queued: number;
  completed: number;
  failed: number;
  blocked: number;
  timedOut: number;
  unknown: number;
  saturated: number;
  skipped: number;
  discarded: number;
  peakInFlight: number;
  peakQueued: number;
  targetInFlight: Record<string, number>;
  targetPeakInFlight: Record<string, number>;
  lastError: string | null;
  limits: { concurrency: number; queue: number; perTarget: number | null };
}
export interface RuntimeStatus {
  get: RuntimeCounters;
  post: RuntimeCounters;
  mappings: Record<string, PostResult>;
  lastUnknown: Record<string, PostResult>;
}
