/**
 * File Path: /automation-world/semantic-mapping-agent/src/app/connection/api/index.ts
 * Description: Connection, current-state, and browser-local Backend bootstrap facade.
 * Main Features: Preserves command payloads and normalizes standard OpenAPI operations with safe numeric Decimal unions.
 */
import { invokeCommand, isTauriRuntime } from "../../tauri";
import type {
  AppDefaults,
  BackendConnectionProfile,
  BackendOpenApiParameter,
  BackendOpenApiOperation,
  BackendOpenApiResult,
} from "../types";

const BACKEND_CONNECTION_STORAGE_KEY = "sma.backend-connection.v1";
const OPENAPI_REQUEST_TIMEOUT_MS = 5000;
const OPENAPI_HTTP_METHODS = ["get", "put", "post", "delete", "options", "head", "patch", "trace"] as const;
const MAX_OPENAPI_TEMPLATE_DEPTH = 8;
const DEFAULT_BACKEND_CONNECTION: BackendConnectionProfile = {
  scheme: "http",
  host: "",
  port: 0,
};

let defaults: AppDefaults = { backendBaseUrl: "", externalIoEnabled: false, configurationSource: "browser-preview" };
export async function loadAppDefaults(): Promise<AppDefaults> {
  if (isTauriRuntime()) defaults = await invokeCommand<AppDefaults>("load_app_defaults");
  return defaults;
}
export function externalIoEnabled(): boolean { return defaults.externalIoEnabled; }
export async function requireExternalIo(): Promise<void> {
  if (isTauriRuntime()) await invokeCommand("check_external_io");
  else if (!defaults.externalIoEnabled) throw new Error("SMA_EXTERNAL_IO_DISABLED");
}

/** HTTP management uses the saved Backend profile in both WebView and browser. */
export async function managementRequest<T>(path: string, options: { method?: string; body?: unknown } = {}): Promise<T> {
  await requireExternalIo();
  const baseUrl = formatBackendBaseUrl(loadBackendConnectionProfile());
  const controller = new AbortController();
  const timer = globalThis.setTimeout(() => controller.abort(), 12000);
  try {
    const response = await fetch(`${baseUrl}${path}`, {
      method: options.method ?? "GET",
      headers: { accept: "application/json", "Content-Type": "application/json" },
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
      signal: controller.signal, cache: "no-store", redirect: "error",
    });
    const envelope = await response.json();
    if (!response.ok || envelope.code !== 200) throw new Error(envelope.errorCode || `MANAGEMENT_REQUEST_FAILED:${response.status}`);
    if (envelope.data === undefined || envelope.data === null) throw new Error("MANAGEMENT_RESPONSE_INVALID");
    // Never deliver a response from an address that was changed while it was in flight.
    if (baseUrl !== formatBackendBaseUrl(loadBackendConnectionProfile())) throw new Error("MANAGEMENT_CONTEXT_CHANGED");
    return envelope.data as T;
  } catch (error) {
    if (controller.signal.aborted) throw new Error("MANAGEMENT_REQUEST_TIMEOUT");
    throw error;
  } finally { globalThis.clearTimeout(timer); }
}

export function loadBackendConnectionProfile(): BackendConnectionProfile {
  if (typeof window === "undefined") return { ...DEFAULT_BACKEND_CONNECTION };

  try {
    const raw = window.localStorage.getItem(BACKEND_CONNECTION_STORAGE_KEY);
    if (!raw) {
      if (!defaults.backendBaseUrl) return { ...DEFAULT_BACKEND_CONNECTION };
      const url = new URL(defaults.backendBaseUrl);
      return { scheme: url.protocol === "https:" ? "https" : "http", host: url.hostname, port: Number(url.port || (url.protocol === "https:" ? 443 : 80)) };
    }
    return normalizeBackendConnection(JSON.parse(raw));
  } catch {
    return { ...DEFAULT_BACKEND_CONNECTION };
  }
}

export function saveBackendConnectionProfile(profile: BackendConnectionProfile): BackendConnectionProfile {
  const normalized = normalizeBackendConnection(profile);
  formatBackendBaseUrl(normalized);

  if (typeof window !== "undefined") {
    if (!window.dispatchEvent(new Event("sma-backend-connection-changing", { cancelable: true }))) {
      throw new Error("BACKEND_CONNECTION_CHANGE_CANCELLED");
    }
    try {
      window.localStorage.setItem(BACKEND_CONNECTION_STORAGE_KEY, JSON.stringify(normalized));
      window.dispatchEvent(new Event("sma-backend-connection-changed"));
    } catch {
      throw new Error("BACKEND_CONNECTION_SAVE_FAILED");
    }
  }

  return normalized;
}

export async function testBackendOpenApi(
  profile: BackendConnectionProfile,
): Promise<BackendOpenApiResult> {
  await requireExternalIo();
  const baseUrl = formatBackendBaseUrl(profile);
  const controller = new AbortController();
  const timeoutId = globalThis.setTimeout(() => controller.abort(), OPENAPI_REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(`${baseUrl}/openapi.json`, {
      headers: { accept: "application/json" },
      signal: controller.signal,
    });
    if (!response.ok) throw new Error(`OPENAPI_REQUEST_FAILED:${response.status}`);

    let document: unknown;
    try {
      document = await response.json();
    } catch {
      throw new Error("OPENAPI_RESPONSE_INVALID");
    }

    if (!isOpenApiDocument(document)) throw new Error("OPENAPI_DOCUMENT_INVALID");

    const operations = await normalizeBackendOpenApiDocument(document);
    return {
      baseUrl,
      openApiVersion: document.openapi,
      pathCount: Object.keys(document.paths).length,
      operationCount: operations.length,
      operations,
    };
  } catch (error) {
    if (controller.signal.aborted) throw new Error("OPENAPI_REQUEST_TIMEOUT");
    throw error;
  } finally {
    globalThis.clearTimeout(timeoutId);
  }
}

export function formatBackendBaseUrl(profile: BackendConnectionProfile): string {
  const normalized = normalizeBackendConnection(profile);
  if (!normalized.host) throw new Error("BACKEND_HOST_REQUIRED");
  if (!Number.isInteger(normalized.port) || normalized.port < 1 || normalized.port > 65535) {
    throw new Error("BACKEND_PORT_INVALID");
  }

  try {
    return new URL(`${normalized.scheme}://${normalized.host}:${normalized.port}`).toString().replace(/\/$/, "");
  } catch {
    throw new Error("BACKEND_ADDRESS_INVALID");
  }
}

function normalizeBackendConnection(value: unknown): BackendConnectionProfile {
  const candidate = value as Partial<BackendConnectionProfile>;
  return {
    scheme: candidate.scheme === "https" ? "https" : "http",
    host: typeof candidate.host === "string" ? candidate.host.trim() : "",
    port: Number(candidate.port),
  };
}

type JsonRecord = Record<string, unknown>;

interface OpenApiDocument {
  openapi: string;
  paths: JsonRecord;
  components?: JsonRecord;
  security?: unknown;
}

function isOpenApiDocument(value: unknown): value is OpenApiDocument {
  if (!value || typeof value !== "object" || Array.isArray(value)) return false;
  const candidate = value as JsonRecord;
  return typeof candidate.openapi === "string"
    && Boolean(candidate.paths)
    && typeof candidate.paths === "object"
    && !Array.isArray(candidate.paths);
}

export async function normalizeBackendOpenApiDocument(
  document: unknown,
): Promise<BackendOpenApiOperation[]> {
  if (!isOpenApiDocument(document)) throw new Error("OPENAPI_DOCUMENT_INVALID");
  const operations: Omit<BackendOpenApiOperation, "contentHash">[] = [];

  for (const [path, pathItem] of Object.entries(document.paths)) {
    if (!isJsonRecord(pathItem)) continue;
    for (const method of OPENAPI_HTTP_METHODS) {
      const operation = pathItem[method];
      if (!isJsonRecord(operation)) continue;
      const effectiveParameters = effectiveOpenApiParameters(pathItem, operation, document);
      const normalized = effectiveParameters.errorCode
        ? unsupported(effectiveParameters.errorCode)
        : normalizeOpenApiRequest(path, effectiveParameters.parameters, operation, document);
      const operationSnapshot = {
        method: method.toUpperCase(),
        path,
        summary: readString(operation.summary),
        operationId: readString(operation.operationId),
        parameters: effectiveParameters.parameters,
        requestBody: operation.requestBody ?? null,
        security: operation.security ?? document.security ?? null,
        servers: operation.servers ?? null,
      };
      operations.push({
        method: method.toUpperCase(),
        path,
        summary: readString(operation.summary) ?? readString(operation.operationId),
        operationId: readString(operation.operationId),
        operationSnapshot,
        requestContract: normalized.errorCode ? null : normalized.parameters,
        bodyTemplate: normalized.errorCode ? {} : normalized.bodyTemplate,
        normalizationStatus: normalized.errorCode ? "unsupported" : "ready",
        normalizationErrorCode: normalized.errorCode,
        jsonTemplate: normalized.errorCode || !Object.keys(normalized.bodyTemplate).length
          ? null
          : JSON.stringify(normalized.bodyTemplate, null, 2),
      });
    }
  }

  return Promise.all(operations.map(async (operation) => ({
    ...operation,
    contentHash: await sha256(canonicalJson(operation.operationSnapshot)),
  })));
}

interface OpenApiNormalizationResult {
  parameters: BackendOpenApiParameter[];
  bodyTemplate: JsonRecord;
  errorCode: string | null;
}

function normalizeOpenApiRequest(
  path: string,
  rawParameters: unknown[],
  operation: JsonRecord,
  document: OpenApiDocument,
): OpenApiNormalizationResult {
  if (Array.isArray(operation.servers) && operation.servers.length > 0) {
    return unsupported("unsupported_external_server");
  }
  const security = operation.security ?? document.security;
  if (Array.isArray(security) && security.length > 0) return unsupported("unsupported_security");

  const parameterMap = new Map<string, BackendOpenApiParameter>();
  for (const rawParameter of rawParameters) {
    const parameter = resolveLocalReference(rawParameter, document);
    if (!parameter) return unsupported("unsupported_unresolved_reference");
    const location = readString(parameter.in);
    const name = readString(parameter.name);
    if (!name || !location || !["path", "query", "header", "cookie"].includes(location)) {
      return unsupported("unsupported_parameter");
    }
    if (location === "cookie") return unsupported("unsupported_cookie_parameter");
    if (location === "header" && ["authorization", "proxy-authorization"].includes(name.toLowerCase())) {
      return unsupported("unsupported_auth_header");
    }
    const schema = resolveLocalReference(parameter.schema, document);
    if (!schema) return unsupported("unsupported_unresolved_reference");
    if (hasUnsupportedSchemaShape(schema)) return unsupported("unsupported_parameter_schema");
    const dataType = openApiDataType(schemaTypeForTss(schema) ?? "", readString(schema.format));
    if (!dataType) return unsupported("unsupported_parameter_schema");
    const normalizedParameter: BackendOpenApiParameter = {
      parameterKey: `${location}:${name}`,
      location: location as "path" | "query" | "header",
      name,
      jsonPath: null,
      dataType,
      required: location === "path" || parameter.required === true,
    };
    parameterMap.set(normalizedParameter.parameterKey, normalizedParameter);
  }
  const parameters = [...parameterMap.values()];
  const placeholders = new Set([...path.matchAll(/\{([^{}]+)\}/g)].map((match) => match[1]));
  const pathNames = new Set(parameters.filter((parameter) => parameter.location === "path").map((parameter) => parameter.name));
  if (placeholders.size !== pathNames.size || [...placeholders].some((name) => !pathNames.has(name))) {
    return unsupported("unsupported_path_parameter_mismatch");
  }

  let bodyTemplate: JsonRecord = {};
  if (operation.requestBody !== undefined) {
    const requestBody = resolveLocalReference(operation.requestBody, document);
    if (!requestBody) return unsupported("unsupported_unresolved_reference");
    const content = isJsonRecord(requestBody.content) ? requestBody.content : null;
    if (!content || !isJsonRecord(content["application/json"])) {
      return unsupported("unsupported_request_content_type");
    }
    const jsonContent = resolveLocalReference(content["application/json"], document);
    const schema = jsonContent ? resolveLocalReference(jsonContent.schema, document) : null;
    if (!schema) return unsupported("unsupported_unresolved_reference");
    const body = collectBodyParameters(schema, document, "", requestBody.required === true, 0, new Set());
    if (body.errorCode) return unsupported(body.errorCode);
    parameters.push(...body.parameters);
    bodyTemplate = body.template;
  }
  if (new Set(parameters.map((parameter) => parameter.parameterKey)).size !== parameters.length) {
    return unsupported("unsupported_duplicate_parameter");
  }
  return { parameters, bodyTemplate, errorCode: null };
}

interface EffectiveOpenApiParameters {
  parameters: unknown[];
  errorCode: string | null;
}

function effectiveOpenApiParameters(
  pathItem: JsonRecord,
  operation: JsonRecord,
  document: OpenApiDocument,
): EffectiveOpenApiParameters {
  const pathParameters = Array.isArray(pathItem.parameters) ? pathItem.parameters : [];
  const operationParameters = Array.isArray(operation.parameters) ? operation.parameters : [];
  const effective = new Map<string, unknown>();
  for (const [levelIndex, level] of [pathParameters, operationParameters].entries()) {
    const levelIdentities = new Set<string>();
    for (const [parameterIndex, rawParameter] of level.entries()) {
      const parameter = resolveLocalReference(rawParameter, document);
      const location = parameter ? readString(parameter.in) : null;
      const name = parameter ? readString(parameter.name) : null;
      if (!location || !name) {
        effective.set(`invalid:${levelIndex}:${parameterIndex}`, rawParameter);
        continue;
      }
      const identity = `${location}:${name}`;
      if (levelIdentities.has(identity)) {
        return {
          parameters: [...pathParameters, ...operationParameters],
          errorCode: "unsupported_duplicate_parameter",
        };
      }
      levelIdentities.add(identity);
      effective.set(identity, parameter);
    }
  }
  return { parameters: [...effective.values()], errorCode: null };
}

function unsupported(errorCode: string): OpenApiNormalizationResult {
  return { parameters: [], bodyTemplate: {}, errorCode };
}

interface BodyNormalizationResult {
  parameters: BackendOpenApiParameter[];
  template: JsonRecord;
  errorCode: string | null;
}

function collectBodyParameters(
  schema: JsonRecord,
  document: OpenApiDocument,
  prefix: string,
  required: boolean,
  depth: number,
  visitedReferences: Set<string>,
): BodyNormalizationResult {
  if (depth >= MAX_OPENAPI_TEMPLATE_DEPTH) return { parameters: [], template: {}, errorCode: "unsupported_schema_depth" };

  const reference = readString(schema.$ref);
  if (reference) {
    if (!reference.startsWith("#/") || visitedReferences.has(reference)) {
      return { parameters: [], template: {}, errorCode: "unsupported_recursive_reference" };
    }
    const resolved = resolveLocalReference(schema, document);
    if (!resolved || resolved === schema) return { parameters: [], template: {}, errorCode: "unsupported_unresolved_reference" };
    const nextVisitedReferences = new Set(visitedReferences);
    nextVisitedReferences.add(reference);
    return collectBodyParameters(resolved, document, prefix, required, depth + 1, nextVisitedReferences);
  }
  if (hasUnsupportedSchemaShape(schema)) return { parameters: [], template: {}, errorCode: "unsupported_body_schema" };

  const properties = isJsonRecord(schema.properties) ? schema.properties : null;
  const type = schemaTypeForTss(schema);
  if (type === "object" || properties) {
    if (!properties) return { parameters: [], template: {}, errorCode: prefix ? "unsupported_body_schema" : null };
    const requiredNames = new Set(
      Array.isArray(schema.required)
        ? schema.required.filter((item): item is string => typeof item === "string")
        : [],
    );
    const parameters: BackendOpenApiParameter[] = [];
    const template: JsonRecord = {};
    for (const [name, propertySchema] of Object.entries(properties)) {
      if (name.includes(".")) return { parameters: [], template: {}, errorCode: "unsupported_body_schema" };
      if (!isJsonRecord(propertySchema)) return { parameters: [], template: {}, errorCode: "unsupported_body_schema" };
      const child = collectBodyParameters(
        propertySchema,
        document,
        prefix ? `${prefix}.${name}` : name,
        required && requiredNames.has(name),
        depth + 1,
        visitedReferences,
      );
      if (child.errorCode) return child;
      parameters.push(...child.parameters);
      const childType = schemaTypeForTss(propertySchema);
      if (childType === "object" || isJsonRecord(propertySchema.properties) || readString(propertySchema.$ref)) {
        template[name] = child.template;
      } else {
        template[name] = templateValue(childType);
      }
    }
    return { parameters, template, errorCode: null };
  }

  if (!prefix || type === "array" || type === "null" || !type) {
    return { parameters: [], template: {}, errorCode: "unsupported_body_schema" };
  }
  const dataType = openApiDataType(type, readString(schema.format));
  return dataType
    ? {
      parameters: [{
        parameterKey: `body:${prefix}`,
        location: "body",
        name: prefix,
        jsonPath: prefix,
        dataType,
        required,
      }],
      template: {},
      errorCode: null,
    }
    : { parameters: [], template: {}, errorCode: "unsupported_body_schema" };
}

function openApiDataType(
  type: string,
  format: string | null,
): BackendOpenApiParameter["dataType"] | null {
  if (type === "string") return format === "date-time" ? "datetime" : "string";
  if (type === "integer" || type === "number" || type === "boolean") return type;
  return null;
}

function templateValue(type: string | null): unknown {
  if (type === "integer" || type === "number") return 0;
  if (type === "boolean") return false;
  return "";
}

function hasUnsupportedSchemaShape(schema: JsonRecord): boolean {
  return schema.items !== undefined
    || schema.not !== undefined
    || Array.isArray(schema.oneOf)
    || Array.isArray(schema.allOf)
    || (Array.isArray(schema.anyOf) && !isNumberStringScalarUnion(schema));
}

function schemaTypeForTss(schema: JsonRecord): string | null {
  return isNumberStringScalarUnion(schema) ? "number" : readSchemaType(schema.type);
}

function isNumberStringScalarUnion(schema: JsonRecord): boolean {
  if (!Array.isArray(schema.anyOf) || schema.anyOf.length !== 2) return false;
  const branches = schema.anyOf.filter(isJsonRecord);
  return branches.length === 2
    && branches.some((branch) => readSchemaType(branch.type) === "number")
    && branches.some((branch) => readSchemaType(branch.type) === "string");
}

function resolveLocalReference(value: unknown, document: OpenApiDocument): JsonRecord | null {
  if (!isJsonRecord(value)) return null;
  const reference = readString(value.$ref);
  if (!reference?.startsWith("#/")) return value;
  const resolved = reference.slice(2).split("/").reduce<unknown>((current, segment) => {
    if (!isJsonRecord(current)) return undefined;
    return current[segment.replace(/~1/g, "/").replace(/~0/g, "~")];
  }, document);
  return isJsonRecord(resolved) ? resolved : null;
}

function readSchemaType(value: unknown): string | null {
  if (typeof value === "string") return value;
  if (!Array.isArray(value)) return null;
  return value.find((item): item is string => typeof item === "string" && item !== "null") ?? null;
}

function readString(value: unknown): string | null {
  return typeof value === "string" ? value : null;
}

function isJsonRecord(value: unknown): value is JsonRecord {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function canonicalJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (isJsonRecord(value)) {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

async function sha256(value: string): Promise<string> {
  const digest = await globalThis.crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}
