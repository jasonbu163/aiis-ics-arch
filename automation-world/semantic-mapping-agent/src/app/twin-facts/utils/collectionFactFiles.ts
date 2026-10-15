/**
 * File Path: /automation-world/semantic-mapping-agent/src/app/twin-facts/utils/collectionFactFiles.ts
 * Description: JSON/XLSX exchange helpers for Collection Facts definitions and values.
 * Main Features:
 *   - Generates definition templates and current-source exports
 *   - Produces in-memory files for bounded native saving or browser fallback download
 *   - Parses only declared JSON wrappers or one declared XLSX worksheet
 *   - Rejects formulas, macros, unexpected sheets, and malformed row shapes
 */
import * as XLSX from "xlsx";

import type {
  BackendCollectionFactRecord,
  CollectionFactContract,
  CollectionFactDataType,
  CollectionFactDefinitionFileRow,
  CollectionFactFileFormat,
  CollectionFactKind,
  CollectionFactValueFileRow,
} from "../types";

const DEFINITION_HEADERS = ["sourceKey", "name", "factKind", "dataType"] as const;
const VALUE_HEADERS = ["sourceKey", "contractVersion", "name", "value"] as const;
const DATA_TYPES = new Set<CollectionFactDataType>(["string", "integer", "number", "boolean", "datetime"]);
const FACT_KINDS = new Set<CollectionFactKind>(["current", "incremental"]);

export interface CollectionFactGeneratedFile {
  fileName: string;
  mimeType: string;
  contents: Uint8Array;
}

export async function parseDefinitionFile(file: File): Promise<CollectionFactDefinitionFileRow[]> {
  const parsed = await parseFile(file, "facts", DEFINITION_HEADERS);
  const rows = extractJsonRows(parsed, "facts");
  return rows.map((row, index) => ({
    sourceKey: requiredText(row.sourceKey, index, "sourceKey"),
    name: requiredText(row.name, index, "name"),
    factKind: requiredFactKind(row.factKind, index),
    dataType: requiredDataType(row.dataType, index),
  }));
}

export async function parseValueFile(file: File): Promise<CollectionFactValueFileRow[]> {
  const parsed = await parseFile(file, "values", VALUE_HEADERS);
  const rows = extractJsonRows(parsed, "values");
  return rows.map((row, index) => ({
    sourceKey: requiredText(row.sourceKey, index, "sourceKey"),
    contractVersion: requiredText(row.contractVersion, index, "contractVersion"),
    name: requiredText(row.name, index, "name"),
    value: valueText(row.value, parsed.emptyCellsAreNull),
  }));
}

export function createDefinitionTemplateFile(format: CollectionFactFileFormat): CollectionFactGeneratedFile {
  return createRowsFile(format, "facts", DEFINITION_HEADERS, [], "collection-facts-definition-template");
}

export function createDefinitionExportFile(
  format: CollectionFactFileFormat,
  contract: CollectionFactContract,
): CollectionFactGeneratedFile {
  return createRowsFile(
    format,
    "facts",
    DEFINITION_HEADERS,
    definitionRowsFromContract(contract),
    `${contract.sourceKey}-collection-facts-definition`,
  );
}

export function createValueExportFile(
  format: CollectionFactFileFormat,
  sourceKey: string,
  facts: BackendCollectionFactRecord[],
): CollectionFactGeneratedFile {
  return createRowsFile(
    format,
    "values",
    VALUE_HEADERS,
    facts.map((fact) => ({
      sourceKey,
      contractVersion: fact.contractVersion,
      name: fact.name,
      value: fact.value,
    })),
    `${sourceKey}-collection-facts-values`,
  );
}

export function definitionRowsFromContract(contract: CollectionFactContract): CollectionFactDefinitionFileRow[] {
  return (["current", "incremental"] as const).flatMap((factKind) => Object.entries(contract[factKind])
    .map(([name, dataType]) => ({ sourceKey: contract.sourceKey, name, factKind, dataType })));
}

type ParsedRows = { rows: Array<Record<string, unknown>>; emptyCellsAreNull: boolean };

async function parseFile(
  file: File,
  sheetName: string,
  headers: readonly string[],
): Promise<ParsedRows> {
  const extension = file.name.toLowerCase().split(".").pop();
  if (extension === "json") {
    const parsed = JSON.parse(await file.text()) as unknown;
    if (!isRecord(parsed) || !Array.isArray(parsed[sheetName])) throw new Error("COLLECTION_FACT_FILE_JSON_INVALID");
    return { rows: parsed[sheetName].map(asRecord), emptyCellsAreNull: false };
  }
  if (extension !== "xlsx") throw new Error("COLLECTION_FACT_FILE_TYPE_INVALID");

  const workbook = XLSX.read(await file.arrayBuffer(), { type: "array", raw: false });
  if (workbook.vbaraw || workbook.SheetNames.length !== 1 || workbook.SheetNames[0] !== sheetName) {
    throw new Error("COLLECTION_FACT_FILE_WORKBOOK_INVALID");
  }
  const worksheet = workbook.Sheets[sheetName];
  if (!worksheet) throw new Error("COLLECTION_FACT_FILE_WORKBOOK_INVALID");
  for (const [cellAddress, cell] of Object.entries(worksheet)) {
    if (!cellAddress.startsWith("!") && typeof cell === "object" && cell && "f" in cell && cell.f) {
      throw new Error("COLLECTION_FACT_FILE_FORMULA_UNSUPPORTED");
    }
  }
  const matrix = XLSX.utils.sheet_to_json<unknown[]>(worksheet, {
    header: 1,
    raw: false,
    defval: "",
    blankrows: false,
  }) as unknown[][];
  const [header, ...body] = matrix;
  if (!Array.isArray(header) || header.length !== headers.length || header.some((value, index) => value !== headers[index])) {
    throw new Error("COLLECTION_FACT_FILE_HEADER_INVALID");
  }
  return {
    rows: body.map((cells) => Object.fromEntries(headers.map((key, index) => [key, cells[index]]))),
    emptyCellsAreNull: true,
  };
}

function extractJsonRows(parsed: ParsedRows, _wrapper: "facts" | "values") {
  return parsed.rows;
}

function asRecord(value: unknown): Record<string, unknown> {
  if (!isRecord(value)) throw new Error("COLLECTION_FACT_FILE_ROW_INVALID");
  return value;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function requiredText(value: unknown, rowIndex: number, field: string): string {
  if (typeof value !== "string" || !value.trim()) {
    throw new Error(`COLLECTION_FACT_FILE_${field.toUpperCase()}_INVALID:${rowIndex + 1}`);
  }
  return value.trim();
}

function requiredFactKind(value: unknown, rowIndex: number): CollectionFactKind {
  if (typeof value !== "string" || !FACT_KINDS.has(value as CollectionFactKind)) {
    throw new Error(`COLLECTION_FACT_FILE_FACT_KIND_INVALID:${rowIndex + 1}`);
  }
  return value as CollectionFactKind;
}

function requiredDataType(value: unknown, rowIndex: number): CollectionFactDataType {
  if (typeof value !== "string" || !DATA_TYPES.has(value as CollectionFactDataType)) {
    throw new Error(`COLLECTION_FACT_FILE_DATA_TYPE_INVALID:${rowIndex + 1}`);
  }
  return value as CollectionFactDataType;
}

function valueText(value: unknown, emptyCellsAreNull: boolean): string | null {
  if (value === null) return null;
  if (value === undefined) throw new Error("COLLECTION_FACT_FILE_VALUE_REQUIRED");
  if (typeof value === "string") return emptyCellsAreNull && value === "" ? null : value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  throw new Error("COLLECTION_FACT_FILE_VALUE_INVALID");
}

export function downloadCollectionFactFile(file: CollectionFactGeneratedFile) {
  const browserContents = new Uint8Array(file.contents);
  const blob = new Blob([browserContents.buffer], { type: file.mimeType });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = file.fileName;
  anchor.style.display = "none";
  document.body.append(anchor);
  anchor.click();
  window.setTimeout(() => {
    anchor.remove();
    URL.revokeObjectURL(url);
  }, 1_000);
}

function createRowsFile(
  format: CollectionFactFileFormat,
  sheetName: "facts" | "values",
  headers: readonly string[],
  rows: object[],
  fileBaseName: string,
): CollectionFactGeneratedFile {
  if (format === "json") {
    return {
      fileName: `${fileBaseName}.json`,
      mimeType: "application/json;charset=utf-8",
      contents: new TextEncoder().encode(JSON.stringify({ [sheetName]: rows }, null, 2)),
    };
  }
  const worksheet = XLSX.utils.json_to_sheet(rows, { header: [...headers] });
  XLSX.utils.sheet_add_aoa(worksheet, [[...headers]], { origin: "A1" });
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, sheetName);
  return {
    fileName: `${fileBaseName}.xlsx`,
    mimeType: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    contents: new Uint8Array(XLSX.write(workbook, { bookType: "xlsx", type: "array" })),
  };
}
