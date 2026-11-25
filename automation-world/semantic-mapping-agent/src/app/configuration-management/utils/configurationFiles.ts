/** SMA 配置包的依赖选择、脱敏、JSON／XLSX 往返及旧文件转换。 */
import * as XLSX from "xlsx";
import type { ChangeIntent } from "../../twin-facts/api/localConfiguration";
import type { MappingConfigurationFileFormat, MappingConfigurationGeneratedFile } from "../../twin-facts/utils/mappingConfigurationFiles";
import { parseMappingConfigurationWorkbook } from "../../twin-facts/utils/mappingConfigurationFiles";

type JsonRecord = Record<string, unknown>;
const FORMAT = "aiis.sma.configuration";
const VERSION = 2;
const MAX_BYTES = 10 * 1024 * 1024;
const MAX_ROWS = 10_000;
const MAX_XLSX_CELL = 32_767;

const FIELDS = {
  httpSources: "id sourceKey name url query intervalMs timeoutMs enabled responsePath responseCondition points",
  httpPoints: "pointKey name dataType path selector qualityPath observedAtPath sampleIdPath acceptedQuality",
  targetApis: "id apiKey name httpMethod path schemaSource operationId bodyTemplate parameterSchema idempotencySupported enabled url timeoutMs receipt",
  targetParameters: "parameterKey location name jsonPath dataType required",
  mappingValueRules: "id valueRuleKey name dataType values originSourceKey originFactName enabled",
  mappings: "id mappingKey name sourceKey targetApiKey bindings intervalMs maxAgeMs enabled",
  mappingBindings: "kind value sourceKey factName valueRuleKey",
  sourceMetadata: "sourceKey factName dataType factKind sourceLocator definitionVersion",
  connection: "scheme host port",
} as const;

const ENTITY_FIELDS = {
  httpSources: ["sourceKey"],
  httpPoints: ["sourceKey", "pointKey"],
  targetApis: ["apiKey"],
  mappingValueRules: ["valueRuleKey"],
  mappings: ["mappingKey"],
  sourceMetadata: ["sourceKey", "factName"],
} as const;
const COLLECTIONS = ["httpSources", "targetApis", "mappingValueRules", "mappings", "sourceMetadata"] as const;
const LEGACY_RESOURCES = ["targetApis", "mappingValueRules", "mappings"] as const;
type Collection = typeof COLLECTIONS[number];
type Resource = keyof typeof ENTITY_FIELDS;
type LegacyResource = typeof LEGACY_RESOURCES[number];
type Locations = Map<string, string>;

interface ExchangeDocument extends Partial<Record<Collection, JsonRecord[]>> {
  connection?: JsonRecord;
}
interface ExchangePackage {
  format: typeof FORMAT;
  schemaVersion: typeof VERSION;
  document: ExchangeDocument;
  redactions?: string[];
}
export interface ExchangeItem {
  resource: Resource;
  key: string;
  selectionKey: string;
  name: string;
  parent?: string;
}
interface ExchangeEntity extends ExchangeItem { value: JsonRecord }
export interface ParsedConfigurationFile {
  intent: ChangeIntent;
  locations: Locations;
  redactions: string[];
  legacy: boolean;
}

export class ConfigurationFileError extends Error {
  constructor(public code: string, public location = "") {
    super(code);
  }
}

function fail(code: string, location?: string): never {
  throw new ConfigurationFileError(code, location);
}

function isRecord(value: unknown): value is JsonRecord {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function record(value: unknown, location: string): JsonRecord {
  return isRecord(value) ? value : fail("fieldType", location);
}

function rows(value: unknown, location: string): unknown[] {
  if (!Array.isArray(value)) fail("fieldType", location);
  if (value.length > MAX_ROWS) fail("tooLarge", location);
  return value;
}

function parseJson(text: unknown, location: string): unknown {
  if (typeof text !== "string") fail("fieldType", location);
  try {
    return JSON.parse(text);
  } catch {
    return fail("invalidJson", location);
  }
}

function pick(value: JsonRecord, fields: string): JsonRecord {
  return Object.fromEntries(fields.split(" ").filter(key => Object.hasOwn(value, key)).map(key => [key, value[key]]));
}

function knownFields(value: JsonRecord, fields: string, location: string) {
  const allowed = fields.split(" ");
  for (const key of Object.keys(value)) {
    if (!allowed.includes(key)) fail("unknownField", `${location}.${key}`);
  }
}

function requiredString(value: unknown, location: string): string {
  if (typeof value !== "string" || !value.trim()) fail("fieldType", location);
  return value;
}

function stableKey(value: unknown, location: string): string {
  const key = requiredString(value, location);
  if (/\s|\p{Cc}/u.test(key) || new TextEncoder().encode(key).length > 256) fail("invalidKey", location);
  return key;
}

function selectionKey(resource: Resource, key: string, parent?: string) {
  return JSON.stringify([resource, parent ?? null, key]);
}

function entityKey(resource: Resource, key: string, parent?: string) {
  return parent === undefined ? `${resource}:${key}` : `${resource}:${parent}:${key}`;
}

function inventory(raw: unknown): ExchangeEntity[] {
  const document = record(raw, "document");
  const result: ExchangeEntity[] = [];
  const add = (resource: Resource, value: JsonRecord, key: string, parent?: string) => {
    result.push({ resource, key, parent, value, selectionKey: selectionKey(resource, key, parent), name: String(value.name ?? key) });
  };
  for (const resource of COLLECTIONS) {
    for (const row of document[resource] as JsonRecord[] ?? []) {
      if (resource === "sourceMetadata") {
        add(resource, row, row.factName as string, row.sourceKey as string);
      } else {
        add(resource, row, row[ENTITY_FIELDS[resource][0]] as string);
      }
      if (resource === "httpSources") {
        for (const point of row.points as JsonRecord[] ?? []) add("httpPoints", point, point.pointKey as string, row.sourceKey as string);
      }
    }
  }
  return result;
}

export function listExchangeItems(document: unknown): ExchangeItem[] {
  return inventory(document).map(({ value: _value, ...item }) => item);
}

export function selectExchangeConfiguration(raw: unknown, selected: ReadonlySet<string>, includeConnection: boolean) {
  const items = inventory(raw);
  const byKey = new Map(items.map(item => [item.selectionKey, item]));
  const included = new Set<ExchangeEntity>();
  const missing = new Set<string>();
  function include(resource: Resource, key: unknown, parent?: unknown) {
    if (typeof key !== "string" || !key) return;
    const owner = typeof parent === "string" ? parent : undefined;
    const item = byKey.get(selectionKey(resource, key, owner));
    if (item) included.add(item);
    else missing.add(entityKey(resource, key, owner));
  }
  function includePoint(source: unknown, point: unknown) {
    if (typeof source !== "string" || typeof point !== "string" || !source || !point) return;
    const kind = byKey.has(selectionKey("httpPoints", point, source)) ? "httpPoints" : "sourceMetadata";
    include(kind, point, source);
  }
  for (const key of selected) {
    const item = byKey.get(key);
    if (item) included.add(item);
  }
  // JS Set iteration visits new dependencies until the closure is complete.
  for (const { resource, value, parent } of included) {
    if (resource === "httpPoints") include("httpSources", parent);
    if (resource === "mappingValueRules") includePoint(value.originSourceKey, value.originFactName);
    if (resource === "mappings") {
      include("targetApis", value.targetApiKey);
      for (const entry of Object.values(record(value.bindings, "bindings"))) {
        const binding = record(entry, "bindings");
        if (binding.kind === "fact") includePoint(binding.sourceKey ?? value.sourceKey, binding.factName);
        include("mappingValueRules", binding.valueRuleKey);
      }
    }
  }
  const document: ExchangeDocument = {};
  const sources = new Map<string, JsonRecord[]>();
  for (const item of included) {
    if (item.resource !== "httpPoints") continue;
    const group = sources.get(item.parent!) ?? [];
    group.push(pick(item.value, FIELDS.httpPoints));
    sources.set(item.parent!, group);
  }
  for (const { resource, key, value } of included) {
    if (resource === "httpPoints") continue;
    const portable = pick(value, FIELDS[resource]);
    if (resource === "httpSources") portable.points = sources.get(key) ?? [];
    if (resource === "targetApis") {
      portable.parameterSchema = (value.parameterSchema as JsonRecord[]).map(parameter => pick(parameter, FIELDS.targetParameters));
    }
    if (resource === "mappings") {
      portable.bindings = Object.fromEntries(Object.entries(record(value.bindings, "bindings")).map(
        ([field, binding]) => [field, pick(record(binding, field), FIELDS.mappingBindings)],
      ));
    }
    (document[resource] ??= []).push(portable);
  }
  if (includeConnection) document.connection = pick(record(record(raw, "document").connection, "connection"), FIELDS.connection);
  const redactions = redact(document, record(raw, "document"));
  const bundle: ExchangePackage = { format: FORMAT, schemaVersion: VERSION, document };
  if (redactions.length) bundle.redactions = redactions;
  return {
    bundle,
    dependencies: [...included].filter(item => !selected.has(item.selectionKey)),
    missing: [...missing],
    redactions,
  };
}

// 配置中可移植的是路径和类型。凭据值从 URL、query、模板和参数绑定中排除。
function sensitiveName(name: string): boolean {
  const key = name.toLowerCase().replace(/[^a-z0-9]/g, "");
  return /(?:authorization|cookie|password|passwd|passcode|apikey|accesskey|privatekey|clientkey|token|secret|credential|credentials|signature|sessionid|assertion)$/.test(key)
    || ["auth", "pwd", "sig", "sessionid", "jwt"].includes(key);
}

function credentialText(value: unknown): boolean {
  return typeof value === "string" && (/^\s*(?:bearer|basic|digest|aws4-hmac-sha256)\s+\S+/i.test(value)
    || /^eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$/.test(value)
    || /^(?:gh[pousr]_|github_pat_|sk-(?:proj-)?)[A-Za-z0-9_-]{12,}$/.test(value));
}

function scrubUrl(value: unknown): unknown {
  if (typeof value !== "string") return value;
  const parts = /^(https?:\/\/)([^/?#]*)([^?#]*)(\?[^#]*)?(#.*)?$/i.exec(value);
  if (!parts) return value;
  const [, prefix, authority, path, query, fragment] = parts;
  const host = authority.slice(authority.lastIndexOf("@") + 1);
  const unsafe = (part: string) => [...new URLSearchParams(part)].some(([key, text]) => sensitiveName(key) || credentialText(text));
  const queryEntries = query?.slice(1).split("&") ?? [];
  const safeQuery = queryEntries.filter(entry => !unsafe(entry));
  const safeFragment = fragment && unsafe(fragment.slice(1)) ? "" : fragment ?? "";
  if (host === authority && safeQuery.length === queryEntries.length && safeFragment === (fragment ?? "")) return value;
  return prefix + host + path + (safeQuery.length ? "?" + safeQuery.join("&") : "") + safeFragment;
}

function redact(document: ExchangeDocument, context: JsonRecord): string[] {
  const marks = new Set<string>();
  const targets = new Map<string, JsonRecord>();
  const targetChanges = new Set<string>();
  const secretRules = new Set<string>();
  const ruleChanges = new Set<string>();
  const sourceChanges = new Set<string>();
  for (const target of context.targetApis as JsonRecord[] ?? []) targets.set(String(target.apiKey), target);
  for (const target of document.targetApis ?? []) targets.set(String(target.apiKey), target);
  function sensitiveBinding(mapping: JsonRecord, parameterKey: string) {
    const target = targets.get(String(mapping.targetApiKey));
    const parameter = (target?.parameterSchema as JsonRecord[] | undefined)?.find(item => item.parameterKey === parameterKey);
    return sensitiveName(String(parameter?.name ?? parameterKey.split(":").at(-1)))
      || (typeof parameter?.jsonPath === "string" && parameter.jsonPath.split(".").some(sensitiveName));
  }
  for (const mapping of (context.mappings as JsonRecord[] ?? []).concat(document.mappings ?? [])) {
    for (const [key, binding] of Object.entries(record(mapping.bindings, "bindings"))) {
      if (isRecord(binding) && sensitiveBinding(mapping, key) && typeof binding.valueRuleKey === "string") secretRules.add(binding.valueRuleKey);
    }
  }
  function mark(row: JsonRecord, field: string, old: unknown, next: unknown, location: string) {
    if (old === next) return;
    row[field] = next;
    marks.add(`${location}.${field}`);
  }
  function scrubTemplate(value: unknown, depth = 0, sensitive = false): unknown {
    if (depth > 90) fail("tooLarge", "bodyTemplate");
    if (Array.isArray(value)) return value.map(item => scrubTemplate(item, depth + 1, sensitive));
    if (!isRecord(value)) return sensitive || credentialText(value) ? null : value;
    return Object.fromEntries(Object.entries(value).map(([key, child]) => [
      key, scrubTemplate(child, depth + 1, sensitive || sensitiveName(key)),
    ]));
  }
  function sensitivePath(path: unknown) {
    return typeof path === "string" && path.split(/[.\[\]/]/).some(sensitiveName);
  }
  for (const source of document.httpSources ?? []) {
    const sourceKey = String(source.sourceKey);
    const location = entityKey("httpSources", sourceKey);
    const url = scrubUrl(source.url);
    const query = Object.entries(record(source.query ?? {}, `${location}.query`));
    const safeQuery = query.filter(([key, value]) => !sensitiveName(key) && !credentialText(value));
    if (url !== source.url || safeQuery.length !== query.length) {
      source.enabled = false;
      sourceChanges.add(sourceKey);
    }
    mark(source, "url", source.url, url, location);
    if (safeQuery.length !== query.length) mark(source, "query", source.query, Object.fromEntries(safeQuery), location);
    if (isRecord(source.responseCondition) && (sensitivePath(source.responseCondition.path) || credentialText(source.responseCondition.equals))) {
      delete source.responseCondition;
      source.enabled = false;
      sourceChanges.add(sourceKey);
      marks.add(`${location}.responseCondition`);
    }
    for (const point of source.points as JsonRecord[] ?? []) {
      if (!isRecord(point.selector) || !(sensitivePath(point.selector.key) || credentialText(point.selector.value))) continue;
      delete point.selector;
      source.enabled = false;
      sourceChanges.add(sourceKey);
      marks.add(`${entityKey("httpPoints", String(point.pointKey), sourceKey)}.selector`);
    }
  }
  for (const item of document.sourceMetadata ?? []) {
    mark(item, "sourceLocator", item.sourceLocator, scrubUrl(item.sourceLocator), entityKey("sourceMetadata", String(item.factName), String(item.sourceKey)));
  }
  for (const target of document.targetApis ?? []) {
    const targetKey = String(target.apiKey);
    const location = entityKey("targetApis", targetKey);
    const previous = marks.size;
    mark(target, "url", target.url, scrubUrl(target.url), location);
    const template = scrubTemplate(target.bodyTemplate);
    if (JSON.stringify(template) !== JSON.stringify(target.bodyTemplate)) mark(target, "bodyTemplate", target.bodyTemplate, template, location);
    if (isRecord(target.receipt) && (sensitivePath(target.receipt.path) || credentialText(target.receipt.equals))) {
      delete target.receipt;
      marks.add(`${location}.receipt`);
    }
    if (marks.size !== previous) {
      target.enabled = false;
      targetChanges.add(targetKey);
    }
  }
  for (const rule of document.mappingValueRules ?? []) {
    const ruleKey = String(rule.valueRuleKey);
    const values = rule.values as unknown[];
    if (!Array.isArray(values) || !values.length) continue;
    if (secretRules.has(ruleKey) || (typeof rule.originFactName === "string" && sensitiveName(rule.originFactName)) || values.some(credentialText)) {
      mark(rule, "values", values, [], entityKey("mappingValueRules", ruleKey));
      rule.enabled = false;
      ruleChanges.add(ruleKey);
    }
  }
  for (const mapping of document.mappings ?? []) {
    const location = entityKey("mappings", String(mapping.mappingKey));
    const bindings = record(mapping.bindings, `${location}.bindings`);
    const safeBindings = Object.fromEntries(Object.entries(bindings).filter(([key, binding]) => {
      if (!isRecord(binding)) return true;
      return !(binding.kind === "constant" && (sensitiveBinding(mapping, key) || credentialText(binding.value))
        || ruleChanges.has(String(binding.valueRuleKey)));
    }));
    if (Object.keys(safeBindings).length !== Object.keys(bindings).length) {
      mark(mapping, "bindings", bindings, safeBindings, location);
      mapping.enabled = false;
    }
    if (targetChanges.has(String(mapping.targetApiKey)) || Object.values(safeBindings).some(binding => isRecord(binding) && sourceChanges.has(String(binding.sourceKey)))) {
      mapping.enabled = false;
      marks.add(`${location}.enabled`);
    }
  }
  return [...marks];
}

type Cell = string | number | boolean | null;
interface SpreadsheetRow { cells: unknown[]; location: string }
const HEADERS = {
  manifest: ["format", "schemaVersion"],
  connection: ["scheme", "host", "port"],
  httpSources: ["sourceKey", "configurationJson"],
  httpPoints: ["sourceKey", "pointKey", "path", "configurationJson"],
  targetApis: ["apiKey", "configurationJson"],
  targetParameters: ["apiKey", "parameterKey", "jsonPath", "configurationJson"],
  mappingValueRules: ["valueRuleKey", "configurationJson"],
  mappings: ["mappingKey", "configurationJson"],
  mappingBindings: ["mappingKey", "parameterKey", "configurationJson"],
  sourceMetadata: ["sourceKey", "factName", "configurationJson"],
  redactions: ["field"],
} as const;
type Sheet = keyof typeof HEADERS;

function writeWorkbook(bundle: ExchangePackage): Uint8Array {
  const workbook = XLSX.utils.book_new();
  function append(sheet: Sheet, data: Cell[][]) {
    if (data.length > MAX_ROWS) fail("tooLarge", sheet);
    data.forEach((row, index) => row.forEach((value, column) => {
      if (typeof value === "string" && value.length > MAX_XLSX_CELL) fail("tooLarge", `${sheet}!${XLSX.utils.encode_cell({ r: index + 1, c: column })}`);
    }));
    XLSX.utils.book_append_sheet(workbook, XLSX.utils.aoa_to_sheet([[...HEADERS[sheet]], ...data]), sheet);
  }
  append("manifest", [[FORMAT, VERSION]]);
  const { document } = bundle;
  if (document.connection) append("connection", [HEADERS.connection.map(key => document.connection![key] as Cell)]);
  for (const resource of COLLECTIONS) {
    const list = document[resource];
    if (!list) continue;
    const keyField = ENTITY_FIELDS[resource][0];
    if (resource === "sourceMetadata") {
      append(resource, list.map(({ sourceKey, factName, ...rest }) => [sourceKey as string, factName as string, JSON.stringify(rest)]));
      continue;
    }
    const childField = resource === "httpSources" ? "points" : resource === "targetApis" ? "parameterSchema" : resource === "mappings" ? "bindings" : null;
    append(resource, list.map(item => {
      const rest = { ...item };
      delete rest[keyField];
      if (childField) delete rest[childField];
      return [item[keyField] as string, JSON.stringify(rest)];
    }));
    if (resource === "httpSources") {
      append("httpPoints", list.flatMap(source => (source.points as JsonRecord[]).map(({ pointKey, path, ...rest }) =>
        [source.sourceKey as string, pointKey as string, path as string, JSON.stringify(rest)])));
    }
    if (resource === "targetApis") {
      append("targetParameters", list.flatMap(target => (target.parameterSchema as JsonRecord[]).map(({ parameterKey, jsonPath, ...rest }) =>
        [target.apiKey as string, parameterKey as string, jsonPath as string | null, JSON.stringify(rest)])));
    }
    if (resource === "mappings") {
      append("mappingBindings", list.flatMap(mapping => Object.entries(record(mapping.bindings, "bindings")).map(([key, binding]) =>
        [mapping.mappingKey as string, key, JSON.stringify(binding)])));
    }
  }
  if (bundle.redactions?.length) append("redactions", bundle.redactions.map(field => [field]));
  return new Uint8Array(XLSX.write(workbook, { type: "array", bookType: "xlsx", compression: true }));
}

export function createConfigurationFile(format: MappingConfigurationFileFormat, bundle: ExchangePackage): MappingConfigurationGeneratedFile {
  const contents = format === "json"
    ? new TextEncoder().encode(`${JSON.stringify(bundle, null, 2)}\n`)
    : writeWorkbook(bundle);
  if (contents.byteLength > MAX_BYTES) fail("tooLarge");
  return {
    fileName: `sma-configuration.${format}`,
    mimeType: format === "json" ? "application/json;charset=utf-8" : "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    contents,
  };
}

function readWorkbook(bytes: ArrayBuffer): XLSX.WorkBook {
  const prefix = new Uint8Array(bytes, 0, Math.min(4, bytes.byteLength));
  if (prefix.join(",") !== "80,75,3,4") fail("invalidWorkbook");
  let workbook: XLSX.WorkBook;
  try {
    workbook = XLSX.read(bytes, { type: "array", bookVBA: true, bookFiles: true, cellFormula: true, cellHTML: false });
  } catch {
    return fail("invalidWorkbook");
  }
  const { keys = [], files = {} } = workbook as XLSX.WorkBook & {
    keys?: string[];
    files?: Record<string, { content?: Uint8Array }>;
  };
  const contentTypes = files["[Content_Types].xml"]?.content;
  if (!contentTypes) fail("invalidWorkbook");
  if (workbook.vbaraw || /<Override\b[^>]*\bContentType\s*=\s*["'][^"']*macroEnabled/i.test(new TextDecoder().decode(contentTypes))
    || keys.some(key => /(?:vbaProject|macroSheets|externalLinks|activeX)/i.test(key))) fail("unsafeWorkbook");
  if (!workbook.SheetNames.length || new Set(workbook.SheetNames).size !== workbook.SheetNames.length) fail("invalidWorkbook");
  for (const name of workbook.SheetNames) {
    const sheet = workbook.Sheets[name];
    if (!sheet || sheet["!type"] && sheet["!type"] !== "sheet") fail("invalidWorkbook", name);
    const range = XLSX.utils.decode_range(sheet["!ref"] ?? "A1");
    if (range.e.r > MAX_ROWS || range.e.c > 31) fail("tooLarge", name);
    for (const [address, cell] of Object.entries(sheet)) {
      if (address.startsWith("!")) continue;
      if (cell.f !== undefined || cell.F !== undefined) fail("formula", `${name}!${address}`);
      if (cell.t === "e") fail("invalidCell", `${name}!${address}`);
    }
  }
  return workbook;
}

function readRows(workbook: XLSX.WorkBook, name: Sheet): SpreadsheetRow[] {
  const sheet = workbook.Sheets[name];
  if (!sheet) return [];
  const columns = HEADERS[name];
  const range = XLSX.utils.decode_range(sheet["!ref"] ?? "A1");
  const cells = (row: number): unknown[] => Array.from({ length: range.e.c + 1 }, (_, column) => sheet[XLSX.utils.encode_cell({ r: row, c: column })]?.v ?? null);
  const first = cells(0);
  if (first.length !== columns.length || columns.some((key, i) => first[i] !== key)) fail("invalidHeader", `${name}!1`);
  const result: SpreadsheetRow[] = [];
  for (let i = 1; i <= range.e.r; i++) {
    const line = cells(i);
    if (line.some(value => value !== null)) result.push({ cells: line, location: `${name}!${i + 1}` });
  }
  return result;
}

function readSpreadsheet(workbook: XLSX.WorkBook, locations: Locations): ExchangePackage {
  for (const name of workbook.SheetNames) if (!Object.hasOwn(HEADERS, name)) fail("unknownSheet", name);
  const manifest = readRows(workbook, "manifest");
  if (manifest.length !== 1 || manifest[0].cells[0] !== FORMAT || manifest[0].cells[1] !== VERSION) fail("unsupportedVersion", "manifest!2");
  const document: ExchangeDocument = {};
  const connection = readRows(workbook, "connection");
  if (connection.length > 1 || (workbook.Sheets.connection && !connection.length)) fail("invalidWorkbook", "connection");
  if (connection.length) {
    document.connection = Object.fromEntries(HEADERS.connection.map((key, i) => [key, connection[0].cells[i]]));
    locations.set("connection", connection[0].location);
  }
  const parents = new Map<string, JsonRecord>();
  for (const resource of COLLECTIONS) {
    if (!workbook.Sheets[resource]) continue;
    document[resource] = readRows(workbook, resource).map(({ cells, location }) => {
      const primary = stableKey(cells[0], `${location}.A`);
      const nested = resource === "sourceMetadata" ? stableKey(cells[1], `${location}.B`) : undefined;
      const key = nested === undefined ? entityKey(resource, primary) : entityKey(resource, nested, primary);
      const jsonColumn = nested === undefined ? "B" : "C";
      if (locations.has(key)) fail("duplicate", `${location}.A`);
      locations.set(key, location);
      const value = record(parseJson(cells[nested === undefined ? 1 : 2], `${location}.${jsonColumn}`), location);
      const keyField = ENTITY_FIELDS[resource][0];
      if (Object.hasOwn(value, keyField) || (nested !== undefined && Object.hasOwn(value, "factName"))) fail("duplicate", `${location}.${keyField}`);
      value[keyField] = primary;
      const children = resource === "httpSources" ? "points" : resource === "targetApis" ? "parameterSchema" : resource === "mappings" ? "bindings" : null;
      if (children) {
        if (Object.hasOwn(value, children)) fail("duplicate", `${location}.${children}`);
        value[children] = children === "bindings" ? Object.create(null) : [];
      }
      if (nested !== undefined) value.factName = nested;
      parents.set(key, value);
      return value;
    });
  }
  for (const [sheet, owner, field, childKey, path] of [
    ["httpPoints", "httpSources", "points", "pointKey", "path"],
    ["targetParameters", "targetApis", "parameterSchema", "parameterKey", "jsonPath"],
    ["mappingBindings", "mappings", "bindings", null, null],
  ] as const) {
    if (Boolean(workbook.Sheets[sheet]) !== Boolean(workbook.Sheets[owner])) fail("invalidWorkbook", sheet);
    for (const { cells, location } of readRows(workbook, sheet)) {
      const parent = stableKey(cells[0], `${location}.A`);
      const id = (sheet === "httpPoints" ? stableKey : requiredString)(cells[1], `${location}.B`);
      const key = `${sheet}:${parent}:${id}`;
      if (locations.has(key)) fail("duplicate", `${location}.B`);
      const value = parents.get(entityKey(owner, parent));
      if (!value) fail("missingReference", `${location}.A`);
      locations.set(key, location);
      if (sheet !== "httpPoints") locations.set(`${owner}:${parent}:${id}`, location);
      const child = record(parseJson(cells[path ? 3 : 2], `${location}.${path ? "D" : "C"}`), location);
      if (childKey && path) {
        if (Object.hasOwn(child, childKey) || Object.hasOwn(child, path)) fail("duplicate", `${location}.${childKey}`);
        child[childKey] = id;
        child[path] = cells[2];
        (value[field] as JsonRecord[]).push(child);
      } else {
        (value[field] as JsonRecord)[id] = child;
      }
    }
  }
  const redactions = readRows(workbook, "redactions").map(({ cells, location }) => requiredString(cells[0], `${location}.A`));
  return { format: FORMAT, schemaVersion: VERSION, document, redactions };
}

function validateDocument(document: unknown, locations: Locations, legacy = false): asserts document is ExchangeDocument {
  const value = record(document, "document");
  knownFields(value, `connection ${COLLECTIONS.join(" ")}`, "document");
  const seen = new Set<string>();
  const ids = new Set<string>();
  function unique(key: string, location: string, keys = seen) {
    if (keys.has(key)) fail("duplicate", location);
    keys.add(key);
  }
  function verifyFields(row: JsonRecord, location: string, fields: Record<string, "boolean" | "number" | "string">) {
    for (const [name, type] of Object.entries(fields)) {
      if (typeof row[name] !== type || type === "number" && !Number.isFinite(row[name])) fail("fieldType", `${location}.${name}`);
    }
  }
  if (value.connection !== undefined) {
    const location = locations.get("connection") ?? "document.connection";
    const connection = record(value.connection, location);
    knownFields(connection, FIELDS.connection, location);
    verifyFields(connection, location, { scheme: "string", host: "string", port: "number" });
  }
  for (const resource of COLLECTIONS) {
    if (!Object.hasOwn(value, resource)) continue;
    rows(value[resource], `document.${resource}`).forEach((entry, index) => {
      const fallback = `document.${resource}[${index}]`;
      const row = record(entry, fallback);
      const keyField = ENTITY_FIELDS[resource][0];
      const derivedRule = legacy && resource === "mappingValueRules" && row.valueRuleKey === null;
      const key = derivedRule
        ? JSON.stringify([stableKey(row.originSourceKey, `${fallback}.originSourceKey`), stableKey(row.originFactName, `${fallback}.originFactName`)])
        : stableKey(row[keyField], `${fallback}.${keyField}`);
      const ownerKey = resource === "sourceMetadata" ? entityKey(resource, stableKey(row.factName, `${fallback}.factName`), key) : entityKey(resource, key);
      const location = seen.has(ownerKey) ? fallback : locations.get(ownerKey) ?? fallback;
      locations.set(ownerKey, location);
      knownFields(row, FIELDS[resource], location);
      unique(ownerKey, `${location}.${keyField}`);
      if (row.id !== undefined) unique(`${resource}:${stableKey(row.id, `${location}.id`)}`, `${location}.id`, ids);
      if (resource !== "sourceMetadata") verifyFields(row, location, { name: "string", enabled: "boolean" });
      if (resource === "httpSources") {
        verifyFields(row, location, { url: "string", intervalMs: "number", timeoutMs: "number" });
        const query = record(row.query ?? {}, `${location}.query`);
        for (const [name, item] of Object.entries(query)) if (typeof item !== "string") fail("fieldType", `${location}.query.${name}`);
        if (row.responseCondition != null) knownFields(record(row.responseCondition, `${location}.responseCondition`), "path equals", `${location}.responseCondition`);
        rows(row.points, `${location}.points`).forEach((entry, i) => {
          const point = record(entry, `${location}.points[${i}]`);
          const pointId = stableKey(point.pointKey, `${location}.points[${i}].pointKey`);
          const identity = entityKey("httpPoints", pointId, key);
          const pointLocation = seen.has(identity) ? `${location}.points[${i}]` : locations.get(identity) ?? `${location}.points[${i}]`;
          locations.set(identity, pointLocation);
          unique(identity, `${pointLocation}.pointKey`);
          knownFields(point, FIELDS.httpPoints, pointLocation);
          verifyFields(point, pointLocation, { path: "string", name: "string", dataType: "string" });
          if (point.selector != null) knownFields(record(point.selector, `${pointLocation}.selector`), "path key value", `${pointLocation}.selector`);
        });
      }
      if (resource === "targetApis") {
        verifyFields(row, location, { path: "string", httpMethod: "string", schemaSource: "string", idempotencySupported: "boolean" });
        record(row.bodyTemplate, `${location}.bodyTemplate`);
        if (row.receipt != null) knownFields(record(row.receipt, `${location}.receipt`), "path equals", `${location}.receipt`);
        rows(row.parameterSchema, `${location}.parameterSchema`).forEach((entry, i) => {
          const parameter = record(entry, `${location}.parameterSchema[${i}]`);
          const id = requiredString(parameter.parameterKey, `${location}.parameterSchema[${i}].parameterKey`);
          const identity = `targetApis:${key}:${id}`;
          const parameterLocation = locations.get(identity) ?? `${location}.parameterSchema[${i}]`;
          locations.set(identity, parameterLocation);
          unique(`targetParameters:${key}:${id}`, `${parameterLocation}.parameterKey`);
          knownFields(parameter, FIELDS.targetParameters, parameterLocation);
          verifyFields(parameter, parameterLocation, { location: "string", name: "string", dataType: "string", required: "boolean" });
        });
      }
      if (resource === "mappingValueRules") {
        verifyFields(row, location, { dataType: "string" });
        rows(row.values, `${location}.values`);
      }
      if (resource === "mappings") {
        verifyFields(row, location, { targetApiKey: "string", intervalMs: "number" });
        for (const [key, binding] of Object.entries(record(row.bindings, `${location}.bindings`))) {
          const identity = `${ownerKey}:${key}`;
          const bindingLocation = locations.get(identity) ?? `${location}.bindings.${key}`;
          locations.set(identity, bindingLocation);
          knownFields(record(binding, bindingLocation), FIELDS.mappingBindings, bindingLocation);
        }
      }
    });
  }
}

function legacyRows(resource: LegacyResource, source: unknown[], locations: Locations, lines?: number[]): JsonRecord[] {
  return source.map((item, index) => {
    const fallback = lines ? `${resource}!${lines[index]}` : `${resource}[${index}]`;
    const row = { ...record(item, fallback) };
    if (resource === "targetApis") {
      row.httpMethod ??= "POST";
      if (row.operationId === undefined || row.operationId === "") row.operationId = null;
      row.bodyTemplate ??= parseJson(row.bodyTemplateJson, `${fallback}.bodyTemplateJson`);
      row.parameterSchema ??= parseJson(row.parameterSchemaJson, `${fallback}.parameterSchemaJson`);
    }
    if (resource === "mappingValueRules") {
      row.values ??= parseJson(row.valuesJson, `${fallback}.valuesJson`);
      for (const key of ["valueRuleKey", "originSourceKey", "originFactName"]) {
        if (row[key] === undefined || row[key] === "") row[key] = null;
      }
    }
    if (resource === "mappings") {
      row.bindings ??= parseJson(row.bindingsJson, `${fallback}.bindingsJson`);
      if (row.sourceKey === "") row.sourceKey = null;
    }
    const key = row[ENTITY_FIELDS[resource][0]];
    if (typeof key === "string") {
      const identity = entityKey(resource, key);
      if (locations.has(identity)) fail("duplicate", `${fallback}.${ENTITY_FIELDS[resource][0]}`);
      locations.set(identity, fallback);
    }
    return pick(row, FIELDS[resource]);
  });
}

function prepareBundle(bundle: JsonRecord, locations: Locations, context: unknown, legacy = false): ParsedConfigurationFile {
  const document = bundle.document;
  validateDocument(document, locations, legacy);
  const fileMarks = bundle.redactions === undefined ? [] : rows(bundle.redactions, "redactions").map((item, i) => requiredString(item, `redactions[${i}]`));
  if (!Object.keys(document).length) fail("emptyFile", "document");
  const detected = redact(document, isRecord(context) ? context : {});
  if (detected.length && !legacy) fail("credentials", detected[0]);
  // 旧规则模板允许留空，由原生导入按来源和点位生成稳定规则 ID。
  const unkeyedLegacyRule = legacy && document.mappingValueRules?.some(rule => rule.valueRuleKey === null);
  return {
    intent: unkeyedLegacyRule
      ? { kind: "import", resource: "mappingValueRules", id: null, payload: document.mappingValueRules }
      : { kind: "merge", resource: "configuration", id: null, payload: document },
    redactions: [...new Set([...fileMarks, ...detected])],
    locations,
    legacy,
  };
}

export async function parseConfigurationFile(file: File, context?: unknown): Promise<ParsedConfigurationFile> {
  if (file.size > MAX_BYTES) fail("tooLarge");
  const locations: Locations = new Map();
  const extension = file.name.toLowerCase().split(".").pop();
  if (extension === "xlsx") {
    const workbook = readWorkbook(await file.arrayBuffer());
    if (workbook.SheetNames.includes("manifest")) return prepareBundle({ ...readSpreadsheet(workbook, locations) }, locations, context);
    const [resource] = workbook.SheetNames;
    if (workbook.SheetNames.length !== 1 || !LEGACY_RESOURCES.includes(resource as LegacyResource)) fail("invalidWorkbook");
    const kind = resource as LegacyResource;
    let parsed: unknown[];
    const lines: number[] = [];
    try { parsed = parseMappingConfigurationWorkbook(kind, workbook, line => lines.push(line)); }
    catch (error) {
      const [code, location] = String(error instanceof Error ? error.message : error).split(":", 2);
      fail(code === "MAPPING_FILE_HEADER_INVALID" ? "invalidHeader" : "invalidCell", location ?? resource);
    }
    const document = { [kind]: legacyRows(kind, parsed, locations, lines) };
    return prepareBundle({ document }, locations, context, true);
  }
  if (extension !== "json") fail("fileType");
  const json = record(parseJson((await file.text()).replace(/^\uFEFF/, ""), "$"), "$");
  if (Object.hasOwn(json, "format") || Object.hasOwn(json, "schemaVersion")) {
    if (json.format !== FORMAT || (json.schemaVersion !== VERSION && json.schemaVersion !== 1)) fail("unsupportedVersion", "schemaVersion");
    if (json.schemaVersion === 1) {
      knownFields(json, "format schemaVersion document", "$");
      record(json.document, "document");
      return { intent: { kind: "restore", resource: "configuration", id: null, payload: json }, redactions: [], locations, legacy: true };
    }
    knownFields(json, "format schemaVersion document redactions", "$");
    return prepareBundle(json, locations, context);
  }
  const [resource] = Object.keys(json);
  if (Object.keys(json).length !== 1 || !LEGACY_RESOURCES.includes(resource as LegacyResource)) fail("invalidJson", "$");
  const kind = resource as LegacyResource;
  return prepareBundle({ document: { [kind]: legacyRows(kind, rows(json[kind], kind), locations) } }, locations, context, true);
}
