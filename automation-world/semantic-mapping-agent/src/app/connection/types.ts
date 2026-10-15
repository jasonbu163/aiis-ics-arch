/**
 * File Path: /automation-world/semantic-mapping-agent/src/app/connection/types.ts
 * Description: Connection and current-state interaction contracts.
 * Main Features: Types app defaults, database checks, normalized all-method OpenAPI catalog entries, and state rows.
 */
export interface AppDefaults { backendBaseUrl: string; externalIoEnabled: boolean; configurationSource: string }

export interface BackendConnectionProfile {
  scheme: "http" | "https";
  host: string;
  port: number;
}

export interface BackendOpenApiResult {
  baseUrl: string;
  openApiVersion: string;
  pathCount: number;
  operationCount: number;
  operations: BackendOpenApiOperation[];
}

export interface BackendOpenApiOperation {
  method: string;
  path: string;
  summary: string | null;
  operationId: string | null;
  operationSnapshot: Record<string, unknown>;
  requestContract: BackendOpenApiParameter[] | null;
  bodyTemplate: Record<string, unknown>;
  normalizationStatus: "ready" | "unsupported";
  normalizationErrorCode: string | null;
  contentHash: string;
  /** Compatibility view for the read-only Backend connection catalog. */
  jsonTemplate: string | null;
}

export interface BackendOpenApiParameter {
  parameterKey: string;
  location: "body" | "query" | "path" | "header";
  name: string;
  jsonPath: string | null;
  dataType: "string" | "integer" | "number" | "boolean" | "datetime";
  required: boolean;
}

