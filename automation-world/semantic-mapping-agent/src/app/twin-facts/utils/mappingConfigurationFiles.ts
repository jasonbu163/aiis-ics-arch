/**
 * File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/utils/mappingConfigurationFiles.ts
 * Description: JSON/XLSX exchange helpers for API-first Mapping configuration resources.
 * Main Features:
 *   - Generates resource-specific templates and exports with native Save As MIME types
 *   - Parses bounded WebView files into the normalized Backend import shape
 *   - Does not persist source files or access local paths directly
 */
import * as XLSX from "xlsx";

import type {
  MappingConfiguration,
  MappingValueRuleConfiguration,
  TargetApiConfiguration,
} from "../types";

export type MappingConfigurationFileFormat = "json" | "xlsx";
export type MappingConfigurationResource = "targetApis" | "mappingValueRules" | "mappings";

export interface MappingConfigurationGeneratedFile {
  fileName: string;
  mimeType: string;
  contents: Uint8Array;
}

const RESOURCE_HEADERS: Record<MappingConfigurationResource, readonly string[]> = {
  targetApis: [
    "apiKey", "name", "httpMethod", "path", "schemaSource", "operationId", "bodyTemplateJson",
    "parameterSchemaJson", "idempotencySupported", "enabled",
  ],
  mappingValueRules: [
    "valueRuleKey", "name", "dataType", "originSourceKey", "originFactName", "valuesJson", "enabled",
  ],
  mappings: ["mappingKey", "name", "sourceKey", "targetApiKey", "bindingsJson", "intervalMs", "enabled"],
};
const LEGACY_TARGET_API_HEADERS = [
  "apiKey", "name", "path", "schemaSource", "operationId", "bodyTemplateJson",
  "parameterSchemaJson", "idempotencySupported", "enabled",
] as const;

export function createMappingConfigurationTemplateFile(
  resource: MappingConfigurationResource,
  format: MappingConfigurationFileFormat,
): MappingConfigurationGeneratedFile {
  return createRowsFile(resource, format, [], `${resource}-template`);
}

export function createTargetApiExportFile(
  format: MappingConfigurationFileFormat,
  configurations: TargetApiConfiguration[],
): MappingConfigurationGeneratedFile {
  return createRowsFile("targetApis", format, configurations.map((item) => ({
    apiKey: item.apiKey,
    name: item.name,
    httpMethod: item.httpMethod,
    path: item.path,
    schemaSource: item.schemaSource,
    operationId: item.operationId ?? "",
    bodyTemplateJson: JSON.stringify(item.bodyTemplate),
    parameterSchemaJson: JSON.stringify(item.parameterSchema),
    idempotencySupported: item.idempotencySupported,
    enabled: item.enabled,
  })), "target-apis");
}

export function createMappingValueRuleExportFile(
  format: MappingConfigurationFileFormat,
  configurations: MappingValueRuleConfiguration[],
): MappingConfigurationGeneratedFile {
  const rows = configurations.map((item) => ({
    valueRuleKey: item.valueRuleKey,
    name: item.name,
    dataType: item.dataType,
    originSourceKey: item.originSourceKey ?? "",
    originFactName: item.originFactName ?? "",
    ...(format === "json" ? { values: item.values } : { valuesJson: JSON.stringify(item.values) }),
    enabled: item.enabled,
  }));
  return createRowsFile("mappingValueRules", format, rows, "mapping-value-rules");
}

export function createMappingConfigurationExportFile(
  format: MappingConfigurationFileFormat,
  configurations: MappingConfiguration[],
): MappingConfigurationGeneratedFile {
  const rows = configurations.map((item) => ({
    mappingKey: item.mappingKey,
    name: item.name,
    sourceKey: item.sourceKey,
    targetApiKey: item.targetApiKey,
    ...(format === "json" ? { bindings: item.bindings } : { bindingsJson: JSON.stringify(item.bindings) }),
    intervalMs: item.intervalMs,
    enabled: item.enabled,
  }));
  return createRowsFile("mappings", format, rows, "mapping-configurations");
}

export async function parseMappingConfigurationFile(
  resource: MappingConfigurationResource,
  file: File,
): Promise<unknown[]> {
  const extension = file.name.toLowerCase().split(".").pop();
  if (extension === "json") {
    const payload = JSON.parse(await file.text()) as unknown;
    if (!isRecord(payload) || !Array.isArray(payload[resource])) throw new Error("MAPPING_FILE_JSON_INVALID");
    return payload[resource];
  }
  if (extension !== "xlsx") throw new Error("MAPPING_FILE_TYPE_INVALID");
  const workbook = XLSX.read(await file.arrayBuffer(), { type: "array", raw: false });
  if (workbook.vbaraw || workbook.SheetNames.length !== 1 || workbook.SheetNames[0] !== resource) {
    throw new Error("MAPPING_FILE_WORKBOOK_INVALID");
  }
  const worksheet = workbook.Sheets[resource];
  if (!worksheet) throw new Error("MAPPING_FILE_WORKBOOK_INVALID");
  for (const [address, cell] of Object.entries(worksheet)) {
    if (!address.startsWith("!") && typeof cell === "object" && cell && "f" in cell && cell.f) {
      throw new Error("MAPPING_FILE_FORMULA_UNSUPPORTED");
    }
  }
  const expectedHeaders = RESOURCE_HEADERS[resource];
  const matrix = XLSX.utils.sheet_to_json<unknown[]>(worksheet, {
    header: 1,
    raw: false,
    defval: "",
    blankrows: false,
  }) as unknown[][];
  const [header, ...rows] = matrix;
  const legacyTarget = resource === "targetApis"
    && Array.isArray(header)
    && header.length === LEGACY_TARGET_API_HEADERS.length
    && header.every((value, index) => value === LEGACY_TARGET_API_HEADERS[index]);
  const headers = legacyTarget ? LEGACY_TARGET_API_HEADERS : expectedHeaders;
  if (!Array.isArray(header) || header.length !== headers.length || header.some((value, index) => value !== headers[index])) {
    throw new Error("MAPPING_FILE_HEADER_INVALID");
  }
  return rows.map((cells) => normalizeXlsxRow(resource, Object.fromEntries(
    headers.map((key, index) => [key, cells[index]]),
  ), legacyTarget));
}

function createRowsFile(
  resource: MappingConfigurationResource,
  format: MappingConfigurationFileFormat,
  rows: Array<Record<string, unknown>>,
  name: string,
): MappingConfigurationGeneratedFile {
  if (format === "json") {
    return {
      fileName: `${name}.json`,
      mimeType: "application/json;charset=utf-8",
      contents: new TextEncoder().encode(`${JSON.stringify({ [resource]: rows }, null, 2)}\n`),
    };
  }
  const headers = RESOURCE_HEADERS[resource];
  const worksheet = XLSX.utils.aoa_to_sheet([
    [...headers],
    ...rows.map((row) => headers.map((header) => row[header] ?? "")),
  ]);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, resource);
  return {
    fileName: `${name}.xlsx`,
    mimeType: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    contents: new Uint8Array(XLSX.write(workbook, { type: "array", bookType: "xlsx" })),
  };
}

function normalizeXlsxRow(
  resource: MappingConfigurationResource,
  row: Record<string, unknown>,
  legacyTarget = false,
): Record<string, unknown> {
  if (resource === "targetApis") {
    return {
      ...row,
      httpMethod: legacyTarget ? "POST" : row.httpMethod,
      operationId: stringOrNull(row.operationId),
      idempotencySupported: booleanValue(row.idempotencySupported),
      enabled: booleanValue(row.enabled),
    };
  }
  if (resource === "mappingValueRules") {
    return {
      ...row,
      values: parseJsonText(row.valuesJson),
      originSourceKey: stringOrNull(row.originSourceKey),
      originFactName: stringOrNull(row.originFactName),
      enabled: booleanValue(row.enabled),
    };
  }
  return {
    ...row,
    bindings: parseJsonText(row.bindingsJson),
    intervalMs: numericValue(row.intervalMs),
    enabled: booleanValue(row.enabled),
  };
}

function parseJsonText(value: unknown): unknown {
  if (typeof value !== "string") throw new Error("MAPPING_FILE_JSON_FIELD_INVALID");
  return JSON.parse(value);
}

function stringOrNull(value: unknown): string | null {
  const text = String(value ?? "").trim();
  return text || null;
}

function booleanValue(value: unknown): boolean {
  if (value === true || value === "true" || value === "TRUE" || value === "1" || value === 1) return true;
  if (value === false || value === "false" || value === "FALSE" || value === "0" || value === 0 || value === "") return false;
  throw new Error("MAPPING_FILE_BOOLEAN_INVALID");
}

function numericValue(value: unknown): number {
  const numberValue = Number(value);
  if (!Number.isInteger(numberValue) || numberValue < 1) throw new Error("MAPPING_FILE_NUMBER_INVALID");
  return numberValue;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}
