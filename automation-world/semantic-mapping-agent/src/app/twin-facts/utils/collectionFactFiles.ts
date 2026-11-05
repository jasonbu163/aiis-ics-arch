/** SMA只读事实导出与通用文件下载；配置JSON/XLSX交换由mappingConfigurationFiles管理。 */
import * as XLSX from "xlsx";
import type { BackendCollectionFactRecord, CollectionFactFileFormat } from "../types";
const VALUE_HEADERS = ["sourceKey", "contractVersion", "name", "value"] as const;
export interface CollectionFactGeneratedFile { fileName: string; mimeType: string; contents: Uint8Array; }
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
