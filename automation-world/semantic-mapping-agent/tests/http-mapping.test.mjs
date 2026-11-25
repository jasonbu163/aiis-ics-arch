/** HTTP 页面回归：从响应选择点位时稳定定位，并保留可配置标量。 */
import assert from "node:assert/strict";
import { test } from "node:test";
import { createServer } from "vite";

test("JSON response point picker uses stable acquisition IDs and escapes arbitrary object keys", async () => {
  const server = await createServer({
    configFile: false,
    envDir: false,
    optimizeDeps: { noDiscovery: true, include: [], entries: [] },
    server: { middlewareMode: true, hmr: false, ws: false },
  });
  try {
    const { pointerValue, responsePointCandidates } = await server.ssrLoadModule("/src/app/http-mapping/ui.ts");
    const { pointDraft, pointDefinition } = await server.ssrLoadModule("/src/app/http-mapping/sourceDraft.ts");
    const url = "http://127.0.0.1:1/api/v1/acquisition-data/latest";
    const first = { pointId: "heat", name: "Furnace", dataType: "REAL", value: 0, quality: "good" };
    const second = { pointId: "running", name: "Running", dataType: "BOOL", value: false };
    const candidates = responsePointCandidates({ data: { items: [first, second] } }, "/data", url);
    const reordered = responsePointCandidates({ data: { items: [second, first] } }, "/data", url);
    assert.deepEqual(candidates.map(point => point.selector), [
      { path: "/items", key: "/pointId", value: "heat" },
      { path: "/items", key: "/pointId", value: "running" },
    ]);
    assert.deepEqual(reordered.toReversed(), candidates);
    assert.deepEqual(candidates.map(point => [point.dataType, point.value]), [["number", 0], ["boolean", false]]);
    const { value, ...definition } = candidates[1];
    assert.equal(value, false);
    assert.deepEqual(pointDefinition(pointDraft({ ...definition, pointKey: "running" })), { ...definition, pointKey: "running" });
    const history = responsePointCandidates({ data: { points: [first] } }, "", "http://127.0.0.1:1/api/v1/acquisition-data/history/F1");
    assert.equal(history[0].selector.path, "/data/points");
    const body = { "tilde~/nested": [{ value: "" }] };
    const [leaf] = responsePointCandidates(body, "", "http://127.0.0.1:1/generic");
    assert.equal(leaf.path, "/tilde~0~1nested/0/value");
    assert.equal(pointerValue(body, leaf.path), "");
  } finally {
    await server.close();
  }
});

test("fixed and receipt scalar editors preserve zero, false and empty strings", async () => {
  const server = await createServer({
    configFile: false,
    envDir: false,
    optimizeDeps: { noDiscovery: true, include: [], entries: [] },
    server: { middlewareMode: true, hmr: false, ws: false },
  });
  try {
    const { readScalar, readJsonScalar } = await server.ssrLoadModule("/src/app/http-mapping/ui.ts");
    assert.equal(readScalar("0", "integer"), 0);
    assert.equal(readScalar("false", "boolean"), false);
    assert.equal(readScalar("", "string"), "");
    assert.equal(readScalar("2026-11-24T08:00:00+08:00", "datetime"), "2026-11-24T08:00:00+08:00");
    assert.equal(readJsonScalar("false"), false);
    assert.equal(readJsonScalar('""'), "");
    assert.throws(() => readScalar("false", "number"), /SMA_INPUT_SCALAR_INVALID/);
    assert.throws(() => readScalar("1.5", "integer"), /SMA_INPUT_SCALAR_INVALID/);
    assert.throws(() => readJsonScalar("null"), /SMA_INPUT_SCALAR_INVALID/);
  } finally {
    await server.close();
  }
});
