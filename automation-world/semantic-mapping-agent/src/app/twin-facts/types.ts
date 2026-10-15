/**
 * File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/types.ts
 * Description: Collection-fact, API-first Mapping configuration, runtime startup, legacy profile, and managed-runtime contracts.
 * Main Features: Types backend-owned Mapping configuration, local runtime startup preferences, manual-run audit summaries, editable material load outcomes, and stable material reason codes.
 */
export type CollectionFactKind = "current" | "incremental";
export type CollectionFactDataType = "string" | "integer" | "number" | "boolean" | "datetime";

export type TargetApiSchemaSource = "manual" | "openapi";
export type TargetApiOriginType = "api_material" | "manual";
export type TargetApiParameterLocation = "body" | "query" | "path" | "header";

export interface TargetApiParameter {
  parameterKey: string;
  location: TargetApiParameterLocation;
  name: string;
  jsonPath: string | null;
  dataType: CollectionFactDataType;
  required: boolean;
}

export interface TargetApiConfigurationInput {
  apiKey: string;
  name: string;
  httpMethod: "GET" | "POST" | "PUT" | "PATCH" | "DELETE" | "HEAD" | "OPTIONS" | "TRACE";
  path: string;
  schemaSource: TargetApiSchemaSource;
  originType?: TargetApiOriginType;
  originMaterialKey?: string | null;
  operationId: string | null;
  bodyTemplate: Record<string, unknown>;
  parameterSchema: TargetApiParameter[];
  idempotencySupported: boolean;
  enabled: boolean;
}

export interface TargetApiConfiguration extends TargetApiConfigurationInput {
  id: string;
  originType: TargetApiOriginType;
  originMaterialKey: string | null;
  rowVersion: string | null;
  createdAt: string;
  updatedAt: string;
}

export type MappingConfigurationBindingKind = "constant" | "fact";

export interface MappingConfigurationBinding {
  kind: MappingConfigurationBindingKind;
  value: unknown | null;
  sourceKey: string | null;
  factName: string | null;
  valueRuleKey: string | null;
}

export interface MappingValueRuleConfigurationInput {
  valueRuleKey: string | null;
  name: string;
  dataType: CollectionFactDataType;
  values: unknown[];
  originSourceKey: string | null;
  originFactName: string | null;
  enabled: boolean;
}

export interface MappingValueRuleConfiguration extends MappingValueRuleConfigurationInput {
  id: string;
  rowVersion: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface MappingConfigurationInput {
  mappingKey: string;
  name: string;
  sourceKey: string | null;
  targetApiKey: string;
  bindings: Record<string, MappingConfigurationBinding>;
  intervalMs: number;
  enabled: boolean;
}

export interface MappingConfiguration extends MappingConfigurationInput {
  id: string;
  targetApiId: string;
  rowVersion: string | null;
  createdAt: string;
  updatedAt: string;
}

export type MappingManualRunStatus =
  | "in_progress"
  | "preflight_rejected"
  | "succeeded"
  | "request_failed"
  | "request_ambiguous";

export interface MappingManualRunSummary {
  runId: string;
  mappingConfigId: string;
  mappingRowVersion: string;
  targetApiId: string;
  targetApiRowVersion: string;
  snapshotId: string;
  status: MappingManualRunStatus;
  errorCode: string | null;
  httpStatusClass: string | null;
  responseSummary: string | null;
  resolvedParameterKeys: string[];
  unresolvedParameterKeys: string[];
}

export interface MappingManualRunRecord extends MappingManualRunSummary {
  resolvedParameterCount: number;
  unresolvedParameterCount: number;
  leaseExpiresAt: string;
  startedAt: string;
  completedAt: string | null;
}

export interface MappingManualRunDiagnostic {
  parameterKey: string;
  errorCode: string;
}

export interface MappingManualRunResult extends MappingManualRunSummary {
  diagnostics: MappingManualRunDiagnostic[];
}

export interface ConfigurationImportError {
  key: string;
  errorCode: string;
}

export interface ConfigurationImportPreview {
  createdKeys: string[];
  updatedKeys: string[];
  unchangedKeys: string[];
  errors: ConfigurationImportError[];
}

export interface TargetApiDraft {
  apiKey: string;
  name: string;
  httpMethod: TargetApiConfigurationInput["httpMethod"];
  path: string;
  schemaSource: TargetApiSchemaSource;
  operationId: string;
  bodyTemplateJson: string;
  parameterSchema: TargetApiParameter[];
  idempotencySupported: boolean;
  enabled: boolean;
}

export interface ApiMaterialConfiguration {
  id: string;
  materialKey: string;
  sourceType: "openapi";
  sourceLocator: string;
  httpMethod: TargetApiConfigurationInput["httpMethod"];
  path: string;
  operationId: string | null;
  name: string;
  operationSnapshot: Record<string, unknown>;
  requestContract: TargetApiParameter[] | null;
  bodyTemplate: Record<string, unknown>;
  normalizationStatus: "ready" | "unsupported";
  normalizationErrorCode: string | null;
  contentHash: string;
  rowVersion: string | null;
  createdAt: string;
  updatedAt: string;
}

export type ApiMaterialNormalizationReasonKey =
  | "apiMaterialsReasonAuthHeader"
  | "apiMaterialsReasonBodySchema"
  | "apiMaterialsReasonCookieParameter"
  | "apiMaterialsReasonDuplicateParameter"
  | "apiMaterialsReasonExternalServer"
  | "apiMaterialsReasonParameter"
  | "apiMaterialsReasonParameterSchema"
  | "apiMaterialsReasonPathParameterMismatch"
  | "apiMaterialsReasonRecursiveReference"
  | "apiMaterialsReasonRequestContentType"
  | "apiMaterialsReasonSchemaDepth"
  | "apiMaterialsReasonSecurity"
  | "apiMaterialsReasonUnresolvedReference"
  | "apiMaterialsReasonUnknown";

const API_MATERIAL_NORMALIZATION_REASON_KEYS: Record<string, ApiMaterialNormalizationReasonKey> = {
  unsupported_auth_header: "apiMaterialsReasonAuthHeader",
  unsupported_body_schema: "apiMaterialsReasonBodySchema",
  unsupported_cookie_parameter: "apiMaterialsReasonCookieParameter",
  unsupported_duplicate_parameter: "apiMaterialsReasonDuplicateParameter",
  unsupported_external_server: "apiMaterialsReasonExternalServer",
  unsupported_parameter: "apiMaterialsReasonParameter",
  unsupported_parameter_schema: "apiMaterialsReasonParameterSchema",
  unsupported_path_parameter_mismatch: "apiMaterialsReasonPathParameterMismatch",
  unsupported_recursive_reference: "apiMaterialsReasonRecursiveReference",
  unsupported_request_content_type: "apiMaterialsReasonRequestContentType",
  unsupported_schema_depth: "apiMaterialsReasonSchemaDepth",
  unsupported_security: "apiMaterialsReasonSecurity",
  unsupported_unresolved_reference: "apiMaterialsReasonUnresolvedReference",
};

export function apiMaterialNormalizationReasonKey(
  errorCode: string | null,
): ApiMaterialNormalizationReasonKey {
  return API_MATERIAL_NORMALIZATION_REASON_KEYS[errorCode ?? ""] ?? "apiMaterialsReasonUnknown";
}

export interface ApiMaterialSelectionResult {
  created: number;
  updated: number;
  unchanged: number;
  removed: number;
  materials: ApiMaterialConfiguration[];
}

export interface TargetApiMaterialLoadResult {
  created: string[];
  skipped: string[];
  requiresConfiguration: string[];
  targetApis: TargetApiConfiguration[];
}

export interface CollectionFactChange {
  name: string;
  from: string;
  to: string;
}

export interface CollectionFactSyncSummary {
  added: string[];
  retained: string[];
  deleted: string[];
  kindChanges: CollectionFactChange[];
  typeChanges: CollectionFactChange[];
  versionOnly: string[];
}

export interface CollectionFactContract {
  contractVersion: string;
  sourceKey: string;
  current: Record<string, CollectionFactDataType>;
  incremental: Record<string, CollectionFactDataType>;
}

export interface CollectionFactContractPreview {
  contract: CollectionFactContract;
  summary: CollectionFactSyncSummary;
}

export interface CollectionFactsWorkspace {
  contractJson: string;
  summary: CollectionFactSyncSummary;
  contractOrigin: "saved" | "generated";
  generatedCounts: {
    current: number;
    incremental: number;
    total: number;
  } | null;
}

export interface CollectionFactListQuery {
  sourceKey?: string;
  nameContains?: string;
  factKind?: CollectionFactKind;
  dataType?: CollectionFactDataType;
  page?: number;
  pageSize?: number;
}

export interface CollectionFactRecord {
  id: number;
  sourceKey: string;
  name: string;
  factKind: CollectionFactKind;
  dataType: CollectionFactDataType;
  valueText: string | null;
  contractVersion: string;
  updatedAt: string;
  rowVersion: string;
}

export interface CollectionFactPage {
  items: CollectionFactRecord[];
  page: number;
  pageSize: number;
  total: number;
}

export interface BackendCollectionFactListQuery {
  sourceKey?: string;
  name?: string;
  factKind?: CollectionFactKind;
  dataType?: CollectionFactDataType;
  page?: number;
  pageSize?: number;
}

export interface BackendCollectionFactRecord {
  sourceKey: string;
  name: string;
  factKind: CollectionFactKind;
  dataType: CollectionFactDataType;
  value: string | null;
  contractVersion: string;
  updatedAt: string;
  rowVersion: string;
}

export interface BackendCollectionFactPage {
  items: BackendCollectionFactRecord[];
  page: number;
  pageSize: number;
  total: number;
}

export interface CollectionFactValueInput {
  name: string;
  value: string | null;
}

export interface CollectionFactValueUpdate {
  contractVersion: string;
  values: CollectionFactValueInput[];
}

export interface CollectionFactValueUpdateResult {
  name: string;
  value: string | null;
  updatedAt: string;
  rowVersion: string;
}

export interface CollectionFactValueUpdateResponse {
  sourceKey: string;
  contractVersion: string;
  updated: CollectionFactValueUpdateResult[];
}

export type CollectionFactFileFormat = "json" | "xlsx";

export interface CollectionFactDefinitionFileRow {
  sourceKey: string;
  name: string;
  factKind: CollectionFactKind;
  dataType: CollectionFactDataType;
}

export interface CollectionFactValueFileRow {
  sourceKey: string;
  contractVersion: string;
  name: string;
  value: string | null;
}

export type TwinRuntimeChannel = "both";

export type SimulationCurrentTimeMode = "utc" | "system" | "custom";

export interface SimulationRuleConfigurationInput {
  sourceKey: string;
  factName: string;
  sequence: unknown[];
  intervalMs: number;
  enabled: boolean;
  writeCurrentTime: boolean;
  currentTimeMode: SimulationCurrentTimeMode;
  currentTimeZone: string | null;
}

export interface SimulationRuleConfiguration extends SimulationRuleConfigurationInput {
  id: string;
  rowVersion: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface CollectionSimulationStartRequest {
  backendBaseUrl: string;
  sourceKey: string;
}

export interface ApiFirstMappingRuntimeStartRequest {
  backendBaseUrl: string;
}

export interface RuntimeStartupPreferences {
  schemaVersion: number;
  runtimeAutoStart: {
    collectionFactSimulation: {
      enabled: boolean;
      sourceKey: string | null;
    };
    apiMappingRuntime: {
      enabled: boolean;
      factsPollingIntervalMs: number;
    };
  };
}

export interface CollectionSimulationPointEditor {
  ruleId: string | null;
  factName: string;
  dataType: CollectionFactDataType;
  valuesJson: string;
  intervalMs: number;
  writeCurrentTime: boolean;
  currentTimeMode: SimulationCurrentTimeMode;
  currentTimeZone: string | null;
  validationError: CollectionSimulationValidationError | null;
}

export type CollectionSimulationValidationError =
  | "SIMULATION_POINT_INTERVAL_INVALID"
  | "SIMULATION_POINT_VALUES_ARRAY_REQUIRED"
  | "SIMULATION_POINT_CURRENT_TIME_INVALID"
  | "SIMULATION_POINT_CURRENT_TIME_MODE_INVALID"
  | "SIMULATION_POINT_CUSTOM_TIME_ZONE_REQUIRED"
  | "SIMULATION_POINT_VALUE_TYPE_INVALID"
  | "SIMULATION_POINT_VALUES_JSON_INVALID";

export type TwinRuntimeStatus =
  | "idle"
  | "starting"
  | "running"
  | "paused"
  | "stopping"
  | "stopped"
  | "blocked"
  | "failed";

export interface TwinRuntimeLogEntry {
  sequence: number;
  timestamp: string;
  event: string;
  runtimeType: string;
  runId: string | null;
  result: string;
  errorCode: string | null;
  message: string;
}

export interface TwinRuntimeSnapshot {
  runtimeType: string;
  status: TwinRuntimeStatus;
  runId: string | null;
  channel: TwinRuntimeChannel | null;
  profileId: string | null;
  profileVersion: string | null;
  profileHash: string | null;
  processedItems: number;
  successfulTransactions: number;
  failedTransactions: number;
  cursor: string | null;
  lastErrorCode: string | null;
  lastErrorMessage: string | null;
  logs: TwinRuntimeLogEntry[];
}

