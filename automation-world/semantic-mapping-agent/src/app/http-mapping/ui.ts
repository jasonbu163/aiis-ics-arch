/** SMA HTTP 表单中的标量、目标地址与 JSON Pointer 展示。 */
import { formatBackendBaseUrl } from "../connection/api";
import type { BackendConnectionProfile } from "../connection/types";
import type { CollectionFactDataType, TargetApiParameter } from "../twin-facts/types";
import type { HttpMessages } from "./messages";
import type { HttpPointDefinition, PostStatus, Scalar } from "./types";

export const scalarTypes = ["string", "integer", "number", "boolean", "datetime"] as const;

export function typeLabel(ui: HttpMessages, type: CollectionFactDataType) {
  const names = { string: ui.valueString, integer: ui.valueInteger, number: ui.valueNumber, boolean: ui.valueBoolean, datetime: ui.valueDateTime };
  return names[type] ?? type;
}

export function parameterLocation(ui: HttpMessages, location: TargetApiParameter["location"]) {
  return { body: ui.paramBody, query: ui.paramQuery, path: ui.paramPath, header: ui.paramHeader }[location];
}

export function postStatusLabel(ui: HttpMessages, status: PostStatus) {
  return { http_succeeded: ui.resultHttp, succeeded: ui.resultSucceeded, failed: ui.resultFailed, unknown: ui.resultUnknown, blocked: ui.resultBlocked }[status] ?? status;
}

export function postStatusTone(status: PostStatus) {
  if (status === "http_succeeded" || status === "succeeded") return "success";
  if (status === "failed") return "danger";
  return "warning";
}

export function jsonText(value: unknown): string {
  return value === undefined ? "" : JSON.stringify(value, null, 2);
}

export function inputText(value: unknown): string {
  return value == null ? "" : typeof value === "string" ? value : jsonText(value);
}

export function readScalar(text: string, type: CollectionFactDataType): Scalar {
  if (type === "string" || type === "datetime") return text;
  if (type === "boolean" && (text === "true" || text === "false")) return text === "true";
  if (type === "number" || type === "integer") {
    const value = readJsonScalar(text);
    if (typeof value === "number" && (type === "number" || Number.isSafeInteger(value))) return value;
  }
  throw new Error("SMA_INPUT_SCALAR_INVALID");
}

export function readJsonScalar(text: string): Scalar {
  let value: unknown;
  try { value = JSON.parse(text); } catch { throw new Error("SMA_INPUT_SCALAR_INVALID"); }
  if (typeof value === "string" || typeof value === "boolean"
      || (typeof value === "number" && Number.isFinite(value))) return value;
  throw new Error("SMA_INPUT_SCALAR_INVALID");
}

export function targetAddress(url: string | null | undefined, path: string, connection?: BackendConnectionProfile): string {
  if (url) return url;
  try {
    if (connection) return formatBackendBaseUrl(connection) + path;
  } catch { /* 未配置连接时仍可显示保存的路径。 */ }
  return path;
}

export function targetParameter(parameter: TargetApiParameter): TargetApiParameter {
  const name = parameter.name.trim();
  const path = parameter.location === "body" ? (parameter.jsonPath?.trim() || name) : null;
  return {
    ...parameter,
    name,
    jsonPath: path,
    parameterKey: `${parameter.location}:${name}`,
    required: parameter.required || parameter.location === "path",
  };
}

export function matchesFilter(filter: string, ...fields: (string | null | undefined)[]): boolean {
  const needle = filter.trim().toLocaleLowerCase();
  return !needle || fields.some(field => field?.toLocaleLowerCase().includes(needle));
}

export function pointerValue(value: unknown, pointer: string): unknown {
  if (!pointer) return value;
  if (!pointer.startsWith("/")) return undefined;
  for (const part of pointer.slice(1).split("/")) {
    const key = part.replace(/~1/g, "/").replace(/~0/g, "~");
    if (!value || typeof value !== "object" || !Object.prototype.hasOwnProperty.call(value, key)) return undefined;
    value = (value as Record<string, unknown>)[key];
  }
  return value;
}

type PointCandidate = Omit<HttpPointDefinition, "pointKey"> & { value: Scalar };

function scalarType(value: unknown): CollectionFactDataType | undefined {
  if (typeof value === "string") return "string";
  if (typeof value === "boolean") return "boolean";
  if (typeof value === "number" && Number.isFinite(value)) return Number.isInteger(value) ? "integer" : "number";
}

const acquisitionTypes: Record<string, CollectionFactDataType> = {
  BOOL: "boolean", INT: "integer", DINT: "integer", WORD: "integer", DWORD: "integer",
  REAL: "number", LREAL: "number", STRING: "string",
};

export function responsePointCandidates(response: unknown, responsePath: string, sourceUrl: string): PointCandidate[] {
  const body = pointerValue(response, responsePath);
  let pathname = "";
  try { pathname = new URL(sourceUrl).pathname; } catch { /* 无效 URL 由保存和 GET 验证。 */ }
  const acquisition = /^\/api\/v1\/acquisition-data\/(latest|history\/[^/]+)$/.exec(pathname)?.[1];
  if (acquisition) {
    const arrayPath = acquisition === "latest" ? "/items" : "/points";
    const path = responsePath === "/data" ? arrayPath : `/data${arrayPath}`;
    const points = pointerValue(body, path);
    if (Array.isArray(points)) {
      return points.slice(0, 500).flatMap((point: Record<string, unknown> | null) => {
        const id = point?.pointId;
        const value = point?.value;
        const dataType = acquisitionTypes[String(point?.dataType).toUpperCase()] ?? scalarType(value);
        if (typeof id !== "string" || !dataType || !scalarType(value)) return [];
        return [{
          name: typeof point?.name === "string" && point.name ? point.name : id,
          dataType, path: "/value", value: value as Scalar,
          selector: { path, key: "/pointId", value: id },
          qualityPath: "/quality", observedAtPath: "/observedAt", sampleIdPath: "/sampleId",
          acceptedQuality: ["good"],
        }];
      });
    }
  }
  const found: PointCandidate[] = [];
  function walk(value: unknown, path: string, name: string, depth: number) {
    if (found.length >= 500 || depth > 15) return;
    const dataType = scalarType(value);
    if (dataType) {
      found.push({ name, dataType, path, value: value as Scalar });
    } else if (value && typeof value === "object") {
      for (const [key, child] of Object.entries(value)) {
        walk(child, `${path}/${key.replace(/~/g, "~0").replace(/\//g, "~1")}`, key, depth + 1);
        if (found.length >= 500) break;
      }
    }
  }
  walk(body, "", "value", 0);
  return found;
}

export function describeError(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}
