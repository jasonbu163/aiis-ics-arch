/** 隔离配置包回归：真实 JSON／XLSX 字节、旧格式及 Vue 层的导入确认/CAS。 */
import assert from "node:assert/strict";
import { after, before, test } from "node:test";
import { resolve } from "node:path";
import vue from "@vitejs/plugin-vue";
import { createServer } from "vite";
import * as XLSX from "xlsx";
import { createSSRApp, defineComponent, proxyRefs } from "vue";
import { renderToString } from "vue/server-renderer";

let server;
let exchange;
before(async () => {
  server = await createServer({
    configFile: false,
    plugins: [vue()],
    resolve: { alias: { "@aw-ui": resolve("../console-ui/src/ui/index.ts") }, dedupe: ["vue", "element-plus"] },
    ssr: { external: ["vue", "element-plus"] },
    optimizeDeps: { noDiscovery: true, include: [], entries: [] },
    server: { middlewareMode: true, hmr: false, ws: false },
  });
  exchange = await server.ssrLoadModule("/src/app/configuration-management/utils/configurationFiles.ts");
});
after(async () => { await server?.close(); });

const now = "2026-11-24T08:00:01+08:00";
const configFormat = "aiis.sma.configuration";
const connection = { scheme: "https", host: "saved.fixture.invalid", port: 443 };
const fact = (name, type = "string") => ({ kind: "fact", value: null, sourceKey: name, factName: type, valueRuleKey: null });
const constant = (value) => ({ kind: "constant", value, sourceKey: null, factName: null, valueRuleKey: null });
const parameter = (name, dataType, location = "body", jsonPath = location === "body" ? `parameters.${name}` : null) => ({
  parameterKey: `${location}:${name}`, location, name, jsonPath, dataType, required: true,
});
const point = (pointKey, dataType, path) => ({ pointKey, dataType, path, name: pointKey });
const source = (sourceKey, points) => ({
  sourceKey, id: `source-${sourceKey}`, name: sourceKey, points, url: `https://${sourceKey}.fixture.invalid/get`,
  query: { page: "0" }, intervalMs: 1000, timeoutMs: 200, enabled: true,
});

function fixtureDocument() {
  return {
    connection, catalog: [], materials: [], sourceMetadata: [],
    runtimeLimits: { getConcurrency: 3 }, runtimeSnapshot: { value: "fixture-runtime-only" },
    httpSources: [
      source("a", [{ ...point("integer", "integer", "$.temperature"), sampleIdPath: "$.id", observedAtPath: "$.at" }, point("unused", "number", "$.unused")]),
      source("b", [{ ...point("string", "string", "$.value"), selector: { path: "$.items", key: "$.id", value: "provenance" } }]),
      source("c", [point("rule-origin", "boolean", "$.ok")]),
    ],
    targetApis: [{
      id: "keep-stable-target-identity", apiKey: "post", name: "Post", httpMethod: "POST", path: "/fixture",
      url: "https://target.fixture.invalid/post", timeoutMs: 250,
      schemaSource: "openapi", originType: "api_material", originMaterialKey: "local-only-material",
      operationId: null, bodyTemplate: { parameters: { integer: null, order: null, enabled: null, zero: null }, nested: [false, 0, "", "=1+2"] },
      parameterSchema: [
        parameter("integer", "integer"), parameter("order", "string"),
        parameter("enabled", "boolean"), parameter("zero", "integer"),
      ],
      receipt: { path: "$.ok", equals: false },
      idempotencySupported: false, enabled: true, updatedAt: now, lastReceipt: { state: "sent" },
    }],
    mappingValueRules: [{
      id: "rule-boolean", name: "Flags", valueRuleKey: "bool", originSourceKey: "c", originFactName: "rule-origin",
      values: [false, true], dataType: "boolean", enabled: true,
    }],
    mappings: [{
      id: "keep-stable-mapping-identity", mappingKey: "report", name: "Report", targetApiKey: "post", targetApiId: "derived",
      sourceKey: null, bindings: {
        "body:integer": fact("a", "integer"), "body:order": fact("b"),
        "body:enabled": { ...constant(false), valueRuleKey: "bool" }, "body:zero": constant(0),
      },
      maxAgeMs: 5000, intervalMs: 500, enabled: true, logs: ["discarded"],
    }],
  };
}

function selected(document, only, includeConnection = false) {
  const items = exchange.listExchangeItems(document);
  const keys = new Set(items.filter(item => !only || only(item)).map(item => item.selectionKey));
  return exchange.selectExchangeConfiguration(document, keys, includeConnection);
}

const jsonFile = (value, name = "fixture.json") => new File([JSON.stringify(value)], name);
const excelFile = (book, type = "xlsx") => new File([XLSX.write(book, { type: "buffer", bookType: type })], "fixture.xlsx");
const normalize = (object) => JSON.parse(JSON.stringify(object));

test("one mapping recursively includes its two points, rule's origin point, parent sources and target", () => {
  const plan = selected(fixtureDocument(), item => item.resource === "mappings");
  const pack = plan.bundle;
  assert.equal(pack.format, configFormat);
  assert.equal(pack.schemaVersion, 2);
  assert.deepEqual(plan.missing, []);
  assert.equal(plan.dependencies.length, 8);
  assert.deepEqual(pack.document.httpSources.map(item => [item.sourceKey, item.points.map(point => point.pointKey)]), [
    ["a", ["integer"]], ["b", ["string"]], ["c", ["rule-origin"]],
  ]);
  assert.equal(pack.document.connection, undefined);
  assert.equal(pack.document.targetApis[0].id, "keep-stable-target-identity");
  assert.equal(pack.document.targetApis[0].originMaterialKey, undefined);
  assert.equal(pack.document.mappings[0].id, "keep-stable-mapping-identity");
  assert.equal(pack.document.runtimeSnapshot, undefined);
  assert.equal(pack.document.runtimeLimits, undefined);
  const pointPlan = selected(fixtureDocument(), item => item.resource === "httpPoints" && item.key === "unused");
  assert.deepEqual(pointPlan.bundle.document.httpSources.flatMap(item => item.points.map(point => point.pointKey)), ["unused"]);
  assert.deepEqual(pointPlan.dependencies.map(item => item.key), ["a"]);
  const missing = fixtureDocument();
  missing.httpSources.pop();
  assert.deepEqual(selected(missing, item => item.resource === "mappings").missing, ["sourceMetadata:c:rule-origin"]);
});

test("actual JSON and XLSX bytes round-trip both selections, types, paths, user opt-in connection and stable IDs", async () => {
  for (const only of [null, item => item.resource === "mappings"]) {
    const { bundle } = selected(fixtureDocument(), only, !only);
    for (const format of ["json", "xlsx"]) {
      const generated = exchange.createConfigurationFile(format, bundle);
      assert.equal(generated.fileName, `sma-configuration.${format}`);
      if (format === "xlsx") {
        assert.deepEqual([...generated.contents.slice(0, 4)], [80, 75, 3, 4]);
        const book = XLSX.read(generated.contents, { type: "array" });
        assert.ok(book.SheetNames.includes("httpPoints"));
        assert.ok(book.SheetNames.includes("targetParameters"));
        assert.ok(book.SheetNames.includes("mappingBindings"));
        assert.equal(book.Sheets.manifest.B2.v, 2);
        assert.equal(book.Sheets.httpPoints.C2.v, "$.temperature");
        assert.equal(book.Sheets.targetParameters.C2.v, "parameters.integer");
      }
      const result = await exchange.parseConfigurationFile(new File([generated.contents], generated.fileName));
      assert.equal(result.intent.kind, "merge");
      assert.deepEqual(normalize(result.intent.payload), normalize(bundle.document));
      assert.deepEqual(result.intent.payload.targetApis[0].bodyTemplate.nested, [false, 0, "", "=1+2"]);
      assert.equal(result.intent.payload.mappings[0].bindings["body:enabled"].value, false);
      assert.equal(result.intent.payload.mappings[0].bindings["body:zero"].value, 0);
      assert.equal(result.intent.payload.targetApis[0].receipt.equals, false);
      if (format === "xlsx") assert.equal(result.locations.get("mappings:report:body:zero"), "mappingBindings!5");
    }
  }
});

test("credentials are absent from either format and affected definitions remain editable after import", async () => {
  const document = fixtureDocument();
  document.httpSources[0].url = "https://fixture-user:fixture-password@a.fixture.invalid/get?access_token=fixture-token&offset=0";
  document.httpSources[0].query = { "x-api-key": "fixture-api-key", stable: "0" };
  document.targetApis[0].url = "https://target.fixture.invalid/post/{id}?session_token=fixture-url-token";
  document.targetApis[0].parameterSchema.push(parameter("id", "string", "path"));
  document.targetApis[0].parameterSchema.push(parameter("Authorization", "string", "header"));
  document.targetApis[0].bodyTemplate.credentials = { service: "fixture-nested-password" };
  document.mappings[0].bindings["header:Authorization"] = constant("fixture-static-auth");
  const { bundle, redactions } = selected(document);
  assert.deepEqual(redactions.sort(), [
    "httpSources:a.query", "httpSources:a.url", "mappings:report.bindings", "mappings:report.enabled",
    "targetApis:post.bodyTemplate", "targetApis:post.url",
  ]);
  assert.equal(document.mappings[0].bindings["header:Authorization"].value, "fixture-static-auth");
  assert.equal(bundle.document.httpSources[0].url, "https://a.fixture.invalid/get?offset=0");
  assert.deepEqual(bundle.document.httpSources[0].query, { stable: "0" });
  assert.deepEqual(bundle.document.targetApis[0].bodyTemplate.credentials, { service: null });
  assert.equal(bundle.document.targetApis[0].url, "https://target.fixture.invalid/post/{id}");
  assert.ok(bundle.document.targetApis[0].parameterSchema.some(item => item.parameterKey === "header:Authorization"));
  assert.equal(bundle.document.mappings[0].bindings["header:Authorization"], undefined);
  for (const format of ["json", "xlsx"]) {
    const generated = exchange.createConfigurationFile(format, bundle);
    const parsed = await exchange.parseConfigurationFile(new File([generated.contents], generated.fileName));
    assert.equal(parsed.redactions.length, redactions.length);
    assert.equal(parsed.intent.payload.httpSources[0].enabled, false);
    assert.equal(parsed.intent.payload.targetApis[0].enabled, false);
    assert.equal(parsed.intent.payload.mappings[0].enabled, false);
    assert.doesNotMatch(JSON.stringify(parsed.intent.payload), /fixture-(?:user|password|token|api-key|nested-password|static-auth|url-token)|fixture-runtime-only/);
  }
  const tampered = normalize(bundle);
  tampered.document.mappings[0].bindings["header:Authorization"] = constant("fixture-illegal-credential");
  await assert.rejects(exchange.parseConfigurationFile(jsonFile(tampered)), { code: "credentials", location: "mappings:report.bindings" });
});

test("bad formats, workbook locations, duplicate identities and nonliteral cells fail before preview", async () => {
  const { bundle } = selected(fixtureDocument());
  const workbook = () => XLSX.read(exchange.createConfigurationFile("xlsx", bundle).contents, { type: "array" });

  const corrupted = new File(["not an actual workbook"], "corrupt.xlsx");
  await assert.rejects(exchange.parseConfigurationFile(corrupted), { code: "invalidWorkbook" });
  const unknownVersion = { ...bundle, schemaVersion: 77 };
  await assert.rejects(exchange.parseConfigurationFile(jsonFile(unknownVersion)), { code: "unsupportedVersion" });
  await assert.rejects(exchange.parseConfigurationFile(new File(["{"], "broken.json")), { code: "invalidJson" });
  const duplicate = normalize(bundle);
  duplicate.document.httpSources.push(duplicate.document.httpSources[0]);
  await assert.rejects(exchange.parseConfigurationFile(jsonFile(duplicate)), { code: "duplicate", location: "document.httpSources[3].sourceKey" });
  const duplicatesId = normalize(bundle);
  duplicatesId.document.httpSources[1].id = duplicatesId.document.httpSources[0].id;
  await assert.rejects(exchange.parseConfigurationFile(jsonFile(duplicatesId)), { code: "duplicate", location: "document.httpSources[1].id" });
  const runtimeField = { ...bundle, document: { ...bundle.document, runtimeSnapshot: {} } };
  await assert.rejects(exchange.parseConfigurationFile(jsonFile(runtimeField)), { code: "unknownField", location: "document.runtimeSnapshot" });

  const formula = workbook();
  formula.Sheets.httpPoints.D2 = { t: "n", f: "2+2", v: 4 };
  await assert.rejects(exchange.parseConfigurationFile(excelFile(formula)), { code: "formula", location: "httpPoints!D2" });
  const macro = workbook();
  macro.vbaraw = Buffer.from("isolated workbook marker");
  await assert.rejects(exchange.parseConfigurationFile(excelFile(macro, "xlsm")), { code: "unsafeWorkbook" });
  const missingOwner = workbook();
  missingOwner.Sheets.httpPoints.A2 = { t: "s", v: "absent" };
  await assert.rejects(exchange.parseConfigurationFile(excelFile(missingOwner)), { code: "missingReference", location: "httpPoints!2.A" });
  const typeMismatch = workbook();
  const typedCell = typeMismatch.Sheets.httpSources.B2;
  typedCell.v = JSON.stringify({ ...JSON.parse(typedCell.v), enabled: "false" });
  await assert.rejects(exchange.parseConfigurationFile(excelFile(typeMismatch)), { code: "fieldType", location: "httpSources!2.enabled" });
  await assert.rejects(exchange.parseConfigurationFile({ name: "big.json", size: 10 * 1024 * 1024 + 1 }), { code: "tooLarge" });
});

test("original version-one backup remains a replacement and older single collections convert to merge", async () => {
  const oldDocument = fixtureDocument();
  delete oldDocument.httpSources;
  delete oldDocument.runtimeSnapshot;
  delete oldDocument.runtimeLimits;
  const backup = { format: configFormat, schemaVersion: 1, document: oldDocument };
  const restored = await exchange.parseConfigurationFile(jsonFile(backup));
  assert.deepEqual(restored.intent, { kind: "restore", resource: "configuration", id: null, payload: backup });

  const legacyFiles = await server.ssrLoadModule("/src/app/twin-facts/utils/mappingConfigurationFiles.ts");
  const document = fixtureDocument();
  for (const [resource, writer] of [
    ["targetApis", legacyFiles.createTargetApiExportFile],
    ["mappingValueRules", legacyFiles.createMappingValueRuleExportFile],
    ["mappings", legacyFiles.createMappingConfigurationExportFile],
  ]) {
    for (const format of ["json", "xlsx"]) {
      const file = writer(format, document[resource]);
      const parsed = await exchange.parseConfigurationFile(new File([file.contents], file.fileName), document);
      assert.equal(parsed.legacy, true);
      assert.equal(parsed.intent.kind, "merge");
      assert.deepEqual(Object.keys(parsed.intent.payload), [resource]);
      assert.equal(parsed.intent.payload[resource].length, 1);
      if (resource === "mappings") {
        assert.equal(parsed.intent.payload.mappings[0].bindings["body:enabled"].value, false);
        assert.equal(parsed.intent.payload.mappings[0].sourceKey, null);
      }
    }
  }
  const book = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(book, XLSX.utils.aoa_to_sheet([
    ["apiKey", "name", "path", "schemaSource", "operationId", "bodyTemplateJson", "parameterSchemaJson", "idempotencySupported", "enabled"],
    ["old", "Old target", "/fixture", "manual", "", "{}", "[]", false, true],
  ]), "targetApis");
  const parsed = await exchange.parseConfigurationFile(excelFile(book));
  assert.equal(parsed.intent.payload.targetApis[0].httpMethod, "POST");
  assert.equal(parsed.locations.get("targetApis:old"), "targetApis!2");
  const unkeyed = await exchange.parseConfigurationFile(jsonFile({ mappingValueRules: [{
    valueRuleKey: null, name: "Derived rule", dataType: "boolean", originSourceKey: "c",
    originFactName: "rule-origin", values: [false], enabled: true,
  }] }));
  assert.equal(unkeyed.intent.kind, "import");
  assert.equal(unkeyed.intent.resource, "mappingValueRules");
});

test("configuration UI repeats the exact preview intent on explicit confirmation and rejects stale or duplicate apply", async () => {
  const document = fixtureDocument();
  let revision = 12;
  let commits = 0;
  const calls = [];
  const { bundle } = selected(document, item => item.resource === "mappings");
  const file = jsonFile(bundle);
  const oldWindow = globalThis.window;
  const fixture = () => ({ schemaVersion: 1, revision, updatedAt: now, document });
  globalThis.window = { localStorage: { getItem: () => null }, __TAURI_INTERNALS__: {
    invoke: async (command, args) => {
      calls.push({ command, args: normalize(args ?? {}) });
      if (command === "load_local_configuration") return fixture();
      if (command === "preview_local_configuration") {
        assert.equal(args.expectedRevision, revision);
        return { token: `rev-${revision}`, expectedRevision: revision, createdKeys: ["mappings:report"],
          updatedKeys: [], unchangedKeys: [], deletedKeys: [], conflictKeys: [], errors: [] };
      }
      if (command === "apply_local_configuration") {
        assert.equal(args.confirmed, true);
        assert.equal(args.token, `rev-${args.expectedRevision}`);
        if (args.expectedRevision !== revision) throw "SMA_CONFIGURATION_CONFLICT";
        revision++;
        commits++;
        return fixture();
      }
      throw new Error(`Unexpected configuration IPC ${command}`);
    },
  } };
  try {
    const locale = await server.ssrLoadModule("/src/locales/index.ts");
    const { default: Panel } = await server.ssrLoadModule("/src/app/configuration-management/components/ConfigurationManagementPanel.vue");
    let state;
    const wrapper = defineComponent({ setup() {
      state = proxyRefs(Panel.setup({ labels: locale.getMessages("en-US") }, { expose() {}, emit() {} }));
      return () => null;
    } });
    await renderToString(createSSRApp(wrapper));
    await state.reviewFile(file);
    assert.equal(state.canApply, true);
    assert.equal(commits, 0);
    state.closeImport();
    await state.saveImport();
    assert.equal(commits, 0);
    assert.equal(calls.some(call => call.command === "apply_local_configuration"), false);

    await state.reviewFile(file);
    revision++;
    await state.saveImport();
    assert.equal(commits, 0);
    assert.equal(state.canApply, false);
    assert.equal(state.userError(state.importError).label, "The configuration revision changed. Preview the file again.");

    await state.reviewFile(file);
    const review = calls.at(-1).args;
    await Promise.all([state.saveImport(), state.saveImport()]);
    assert.equal(commits, 1);
    const applied = calls.at(-1).args;
    assert.deepEqual(applied.intent, review.intent);
    assert.equal(applied.expectedRevision, review.expectedRevision);
    assert.equal(state.imported, true);
    assert.equal(state.importOpen, false);
    assert.deepEqual(Object.keys(locale.getMessages("en-US").configurationExchange.error), Object.keys(locale.getMessages("zh-CN").configurationExchange.error));
  } finally {
    globalThis.window = oldWindow;
  }
});
