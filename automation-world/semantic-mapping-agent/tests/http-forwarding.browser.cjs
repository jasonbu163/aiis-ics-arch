// Run as an async (page, baseURL) Playwright callback against local Vite. IPC and OpenAPI are fixtures.
async (page, baseURL) => {
  const expect = (ok, message) => { if (!ok) throw new Error(message); };
  const origin = new URL(baseURL).origin;
  const endpoint = "http://fixture.invalid:18081";
  const time = "2026-11-24T16:30:01.000+08:00";
  const fullText = "Long fixture preview for the scrolling body. ".repeat(320);
  const operation = {
    openapi: "3.0.3",
    info: { title: "SMA fixture", version: "1.0" },
    paths: {
      "/collect-new": { get: { summary: "Fixture GET operation", operationId: "fixture-get", responses: { 200: { description: "OK" } } } },
      "/post-new": { post: { summary: "Fixture POST operation", operationId: "fixture-post", responses: { 200: { description: "OK" } } } },
    },
  };
  const unexpected = [];
  await page.route("**/*", route => {
    const address = new URL(route.request().url());
    if (address.origin === endpoint && address.pathname === "/openapi.json") {
      return route.fulfill({ json: operation, headers: { "Access-Control-Allow-Origin": "*" } });
    }
    if (address.origin === origin) return route.continue();
    unexpected.push(address.origin);
    return route.abort();
  });
  await page.addInitScript(({ endpoint, time, fullText }) => {
    localStorage.setItem("sma.locale", "en-US");
    localStorage.setItem("sma.theme", "light");
    localStorage.setItem("sma.table-widths.v1.http-sources", JSON.stringify({ name: 220 }));
    const point = { pointKey: "temperature", name: "Fixture temperature", path: "/temperature", dataType: "number" };
    const reading = { pointKey: point.pointKey, value: 0, quality: "good", observedAt: time, sampleId: "sample-8", errorCode: null };
    const source = { id: "httpSources:source", sourceKey: "source", name: "Fixture source", url: `${endpoint}/latest`, query: {}, enabled: true, intervalMs: 1000, timeoutMs: 500, points: [point] };
    const target = { id: "targetApis:target", apiKey: "target", name: "Fixture target", url: `${endpoint}/push`, path: "/push", httpMethod: "POST", timeoutMs: 500, enabled: true, schemaSource: "manual", originType: "manual", originMaterialKey: null, operationId: null, bodyTemplate: { v: null }, parameterSchema: [{ parameterKey: "body:v", location: "body", name: "v", jsonPath: "v", dataType: "integer", required: true }], idempotencySupported: false, rowVersion: null, createdAt: time, updatedAt: time };
    const rule = { id: "mappingValueRules:valid", valueRuleKey: "valid", name: "Fixture rule", dataType: "number", values: [0, 900], originSourceKey: source.sourceKey, originFactName: point.pointKey, enabled: true, rowVersion: null, createdAt: time, updatedAt: time };
    const mapping = { id: "mappings:line", mappingKey: "line", name: "Fixture mapping", targetApiKey: target.apiKey, targetApiId: target.id, intervalMs: 4000, maxAgeMs: 20000, enabled: true, bindings: { "body:v": { kind: "constant", value: 0, sourceKey: null, factName: null, valueRuleKey: null } }, createdAt: time, updatedAt: time, rowVersion: null };
    const limits = { getConcurrency: 4, getQueue: 6, postConcurrency: 5, postQueue: 8, perTargetConcurrency: 2 };
    let snapshot = { schemaVersion: 1, revision: 3, updatedAt: time, document: { connection: { scheme: "http", host: "fixture.invalid", port: 18081 }, catalog: [], materials: [], sourceMetadata: [], targetApis: [target], mappingValueRules: [rule], mappings: [mapping], httpSources: [source], runtimeLimits: limits } };
    const lane = { phase: "stopped", active: 0, inFlight: 0, queued: 0, completed: 0, failed: 0, blocked: 0, timedOut: 0, unknown: 0, saturated: 0, skipped: 0, discarded: 0, peakInFlight: 0, peakQueued: 0, targetInFlight: {}, targetPeakInFlight: {}, limits: { concurrency: 4, queue: 6, perTarget: 2 } };
    const status = { get: { ...lane }, post: { ...lane }, mappings: {}, lastUnknown: {} };
    const calls = [];
    let activeToken = "";
    let sequences = 0;
    let lastExport = null;
    window.__smaFixture = { calls, exportBytes: () => lastExport };
    window.__TAURI_INTERNALS__ = { invoke: async (command, args) => {
      const data = args ?? {};
      calls.push({ command, data: command === "save_collection_fact_file" ? { fileName: data.fileName } : structuredClone(data) });
      switch (command) {
        case "load_app_defaults": return { externalIoEnabled: true, backendBaseUrl: endpoint, configurationSource: "browser-fixture" };
        case "check_external_io": return undefined;
        case "load_local_configuration": return structuredClone(snapshot);
        case "acquisition_options": return { items: [{ plcId: "fixture-plc", dbNumbers: [21, 22] }] };
        case "sma_latest_sources": return [{ sourceKey: source.sourceKey, lastAttemptAt: time, lastErrorCode: null, fromPreviousSession: false, snapshot: { sourceKey: source.sourceKey, version: 8, collectedAt: time, points: [reading] } }];
        case "sma_test_source": return { sourceKey: data.sourceKey, httpStatus: 200, response: { temperature: 0 }, points: [reading], errorCode: null };
        case "sma_runtime_status": return structuredClone(status);
        case "sma_start_runtime": case "sma_stop_runtime": {
          status[data.side].phase = command === "sma_start_runtime" ? "running" : "stopped";
          return structuredClone(status[data.side]);
        }
        case "sma_preview_mapping": case "sma_preview_target": {
          activeToken = `preview-${++sequences}`;
          return { token: activeToken, revision: snapshot.revision, request: { method: "POST", url: target.url, headers: [], body: { v: 0, text: fullText } }, sources: [{ sourceKey: source.sourceKey, version: 8, collectedAt: time, points: [reading] }], diagnostics: [] };
        }
        case "sma_cancel_post": if (activeToken === data.token) activeToken = ""; return undefined;
        case "sma_confirm_post": {
          if (!activeToken || data.token !== activeToken) throw "SMA_HTTP_PREVIEW_REQUIRED";
          activeToken = "";
          return { status: "http_succeeded", runId: "single-fixture", httpStatus: 200, finishedAt: time, sources: [], diagnostics: [], response: { code: 200 } };
        }
        case "change_local_configuration": {
          if (data.expectedRevision !== snapshot.revision) throw "SMA_CONFIGURATION_CONFLICT";
          const entry = data.intent;
          if (entry.kind === "upsert") {
            const key = { httpSources: "sourceKey", targetApis: "apiKey", mappingValueRules: "valueRuleKey", mappings: "mappingKey" }[entry.resource];
            const stored = { ...entry.payload, id: entry.id ?? `${entry.resource}:${entry.payload[key]}`, createdAt: time, updatedAt: time, rowVersion: null };
            snapshot.document[entry.resource] = [...snapshot.document[entry.resource].filter(item => item.id !== stored.id), stored];
            snapshot.revision++;
          }
          return structuredClone(snapshot);
        }
        case "save_collection_fact_file": lastExport = data.contents; return true;
        case "preview_local_configuration": return { token: "import-fixture", expectedRevision: snapshot.revision, createdKeys: ["httpSources:new"], updatedKeys: [], unchangedKeys: [], deletedKeys: [], errors: [], conflictKeys: [] };
        case "apply_local_configuration": snapshot.revision++; return structuredClone(snapshot);
        default: throw new Error(`Unexpected SMA browser fixture call ${command}`);
      }
    } };
  }, { endpoint, time, fullText });

  const nav = id => page.locator(`[data-navigation-id="${id}"]`);
  const showing = () => page.getByRole("dialog", { exact: true });
  const by = (name, host = page) => host.getByRole("button", { name, exact: true });
  const callsOf = command => page.evaluate(name => window.__smaFixture.calls.filter(call => call.command === name), command);
  const go = async (group, leaf) => {
    const entry = nav(leaf);
    if (!await entry.isVisible()) await nav(group).locator(".el-sub-menu__title").click();
    await entry.click();
    expect(await entry.getAttribute("aria-current") === "page", `navigation failed for ${leaf}`);
  };
  const overlay = async dialog => {
    await page.mouse.click(8, 8);
    await dialog.waitFor({ state: "hidden" });
  };
  const fits = async dialog => {
    await dialog.evaluate(async wrapper => {
      await new Promise(resolve => requestAnimationFrame(resolve));
      const root = wrapper.closest(".el-overlay") ?? wrapper;
      await Promise.allSettled(root.getAnimations({ subtree: true }).filter(animation => animation.effect?.getTiming().iterations !== Infinity).map(animation => animation.finished));
    });
    const box = await dialog.locator(".el-dialog").boundingBox();
    const footer = await dialog.locator(".el-dialog__footer").boundingBox();
    const screen = page.viewportSize();
    expect(box && box.x >= 0 && box.x + box.width <= screen.width + 1 && box.y >= 0, "dialog clipped at viewport");
    expect(footer && footer.y + footer.height <= screen.height + 1, "dialog footer outside viewport");
  };
  const fromOpenApi = async (path, stableId, title) => {
    await by("Add from OpenAPI").click();
    const picker = page.getByRole("dialog", { name: "Select OpenAPI operation" });
    await by("Read saved connection", picker).click();
    const option = picker.locator("option").filter({ hasText: path });
    await option.waitFor({ state: "attached" });
    await picker.locator("select").selectOption(await option.getAttribute("value"));
    await by("Use operation", picker).click();
    const editor = page.getByRole("dialog", { name: title });
    await editor.getByLabel("Stable ID").fill(stableId);
    await by("Save", editor).click();
    await editor.waitFor({ state: "hidden" });
  };

  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto(baseURL);
  for (const [group, id] of [
    ["workbench-group", "connection"], ["workbench-group", "configuration"], ["workbench-group", "runtime"],
    ["facts-group", "fact-sources"], ["facts-group", "fact-points"], ["interfaces-group", "target-apis"],
    ["mappings-group", "value-rules"], ["mappings-group", "mappings"],
  ]) await go(group, id);
  expect((await callsOf("sma_start_runtime")).length === 0, "navigation started runtime");

  await go("facts-group", "fact-sources");
  await by("Test GET").click();
  const getResult = page.getByRole("dialog", { name: "GET test result" });
  await getResult.getByText("HTTP status 200", { exact: true }).waitFor();
  await getResult.getByRole("cell", { name: "temperature", exact: true }).waitFor();
  await overlay(getResult);
  const label = page.getByRole("table", { name: "Fact sources" }).getByRole("columnheader", { name: "Name" });
  const handle = label.locator(".sma-column-resizer");
  const start = await handle.boundingBox();
  expect(start, "no draggable source column");
  await page.mouse.move(start.x + start.width / 2, start.y + start.height / 2);
  await page.mouse.down();
  await page.mouse.move(start.x + 38, start.y + start.height / 2, { steps: 4 });
  await page.mouse.up();
  const width = await page.evaluate(() => JSON.parse(localStorage.getItem("sma.table-widths.v1.http-sources")).name);
  expect(width > 220, "column width did not persist after dragging");

  await by("Add manually").click();
  const sourceDialog = page.getByRole("dialog", { name: "Add GET source" });
  await sourceDialog.getByLabel("Stable ID").fill("fixture-manual");
  await sourceDialog.getByLabel("Name", { exact: true }).fill("Manual GET fixture");
  await sourceDialog.getByLabel("Full HTTP(S) URL").fill(`${endpoint}/manual`);
  await by("Save", sourceDialog).click();
  await page.getByText("Manual GET fixture", { exact: true }).waitFor();
  await fromOpenApi("/collect-new", "fixture-open-get", "Add GET source");
  await page.getByText("Fixture GET operation", { exact: true }).waitFor();

  await go("interfaces-group", "target-apis");
  await by("Test POST").click();
  const preview = page.getByRole("dialog", { name: "Preview POST" });
  await preview.locator("input").first().fill("0");
  await by("Preview", preview).click();
  await by("Confirm and send once", preview).waitFor();
  await fits(preview);
  await overlay(preview);
  expect((await callsOf("sma_confirm_post")).length === 0, "test GET, preview or backdrop sent POST");

  await by("Test POST").click();
  await preview.locator("input").first().fill("0");
  await by("Preview", preview).click();
  await by("Confirm and send once", preview).press("Enter");
  await preview.getByText("single-fixture", { exact: true }).waitFor();
  expect((await callsOf("sma_confirm_post")).length === 1, "expected exactly one test confirmation");
  await by("Close", preview).click();
  await by("Add manually").click();
  const targetEditor = page.getByRole("dialog", { name: "Add POST target" });
  await targetEditor.getByLabel("Stable ID").fill("fixture-manual-post");
  await targetEditor.getByLabel("Name", { exact: true }).fill("Manual target fixture");
  await targetEditor.getByLabel("Full HTTP(S) URL").fill(`${endpoint}/manual-post`);
  await by("Save", targetEditor).click();
  await page.getByText("Manual target fixture", { exact: true }).waitFor();
  await fromOpenApi("/post-new", "fixture-open-post", "Add POST target");
  await page.getByText("Fixture POST operation", { exact: true }).waitFor();

  await go("workbench-group", "runtime");
  await by("Start acquisition").click();
  await by("Stop acquisition").waitFor();
  expect((await callsOf("sma_start_runtime")).map(call => call.data.side).join() === "get", "collection also started delivery");
  await by("Start delivery").click();
  await by("Stop delivery").waitFor();
  await by("Stop acquisition").click();
  await by("Stop delivery").click();

  await go("workbench-group", "configuration");
  await by("Select all").click();
  await by("Export JSON").click();
  await page.getByText("Configuration file saved.").waitFor();
  const bytes = await page.evaluate(() => window.__smaFixture.exportBytes());
  await page.locator("input[accept='.json,.xlsx']").setInputFiles({ name: "fixture.json", mimeType: "application/json", buffer: Buffer.from(bytes) });
  const review = page.getByRole("dialog", { name: "Review configuration import" });
  await review.getByText("httpSources:new", { exact: true }).waitFor();
  await fits(review);
  await overlay(review);
  expect((await callsOf("apply_local_configuration")).length === 0, "backdrop applied configuration");

  await page.setViewportSize({ width: 1024, height: 768 });
  await by("Switch to dark mode").click();
  await by("Switch to Chinese").click();
  expect(await page.locator("#sma-overlays").getAttribute("data-aw-theme") === "dark", "dialogs did not switch theme");
  await go("mappings-group", "value-rules");
  await by("编辑").click();
  const ruleEditor = showing();
  await ruleEditor.waitFor();
  await fits(ruleEditor);
  await page.keyboard.press("Escape");
  await ruleEditor.waitFor({ state: "hidden" });
  await go("interfaces-group", "target-apis");
  const fixtureTarget = page.getByRole("row").filter({ hasText: "Fixture target" });
  await by("测试 POST", fixtureTarget).click();
  const chinese = page.getByRole("dialog", { name: "预览 POST" });
  await chinese.locator("input").first().fill("0");
  await by("预览", chinese).click();
  await by("确认发送一次", chinese).waitFor();
  await fits(chinese);
  const scroll = await chinese.locator(".el-dialog__body").evaluate(body => ({ height: body.clientHeight, overflow: getComputedStyle(body).overflowY }));
  expect(scroll.height > 0 && ["scroll", "auto"].includes(scroll.overflow), "dialog body does not scroll independently");
  await overlay(chinese);
  for (const [width, height, theme] of [[1440, 900, "dark"], [1024, 768, "light"]]) {
    await page.setViewportSize({ width, height });
    if (theme === "light") await by("切换为亮色").click();
    await by("编辑", fixtureTarget).click();
    const editor = page.getByRole("dialog", { name: "编辑 POST 目标" });
    await editor.waitFor();
    await fits(editor);
    await overlay(editor);
  }
  expect((await callsOf("sma_confirm_post")).length === 1, "dark-theme backdrop sent a POST");
  expect(!unexpected.length, "unexpected browser traffic outside local fixture");
  return "Eight pages, source GET, local columns, preview/confirm, JSON review, keyboard/backdrop and desktop/tablet theme checked.";
};
