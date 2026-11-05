/** SMA-002只读职责、交换、偏好隔离和已触达展示回归；全部为内存fixture。 */
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { test } from 'node:test';
import { createServer } from 'vite';
import * as XLSX from 'xlsx';
import { createSSRApp } from 'vue';
import { renderToString } from 'vue/server-renderer';

async function withModules(run) {
  const server = await createServer({ configFile: false, optimizeDeps: { noDiscovery: true, include: [], entries: [] }, server: { middlewareMode: true, hmr: false, ws: false } });
  const previousWindow = globalThis.window;
  const previousFetch = globalThis.fetch;
  const storage = new Map();
  const requests = [];
  const ipcCalls = [];
  let snapshot = { schemaVersion: 1, revision: 0, updatedAt: "2026-11-04T17:00:00.000+08:00", document: { connection: { scheme: "http", host: "127.0.0.1", port: 19292 }, catalog: [], materials: [], targetApis: [], mappingValueRules: [], mappings: [], sourceMetadata: [] } };
  globalThis.window = { localStorage: { getItem: key => storage.get(key) ?? null, setItem: (key, value) => storage.set(key, value), removeItem: key => storage.delete(key) }, dispatchEvent: () => true,
    __TAURI_INTERNALS__: { invoke: async (command, args) => {
      ipcCalls.push({ command, args });
      if (command === "load_local_configuration") return structuredClone(snapshot);
      if (command === "preview_local_configuration") return { token: "fixture-preview", expectedRevision: snapshot.revision, createdKeys: ["fixture"], updatedKeys: [], unchangedKeys: [], deletedKeys: [], errors: [] };
      if (command === "apply_local_configuration") { snapshot = { ...snapshot, revision: snapshot.revision + 1 }; return structuredClone(snapshot); }
      if (command === 'load_app_defaults') return { externalIoEnabled: true, backendBaseUrl: 'http://127.0.0.1:19292', configurationSource: 'memory-fixture' };
      if (command === 'check_external_io') return;
      throw new Error(`Unexpected command: ${command}`);
    } } };
  globalThis.fetch = async (url, options = {}) => {
    requests.push({ url: String(url), method: options.method ?? 'GET', body: options.body ? JSON.parse(options.body) : null });
    const path = new URL(url).pathname;
    if (path.includes('/contracts/')) return new Response(JSON.stringify({ code: 404, errorCode: 'collection_fact_source_not_found' }), { status: 404 });
    const data = path.includes('import-') ? { createdKeys: ['fixture'], updatedKeys: [], unchangedKeys: [], errors: [] }
      : path.includes('collection-facts') ? { items: [], page: 1, pageSize: 25, total: 0 } : [];
    return new Response(JSON.stringify({ code: 200, data }));
  };
  try {
    const connection = await server.ssrLoadModule('/src/app/connection/api/index.ts');
    await connection.loadAppDefaults();
    const local = await server.ssrLoadModule("/src/app/twin-facts/api/localConfiguration.ts"); await local.loadLocalConfiguration();
    await run(server, requests, storage, ipcCalls);
  } finally { globalThis.window = previousWindow; globalThis.fetch = previousFetch; await server.close(); }
}

test('missing source stays null; refresh/filter/paging/export reads never mutate facts', async () => withModules(async (server, requests) => {
  const { useCollectionFactsStore } = await server.ssrLoadModule('/src/app/twin-facts/store/collectionFacts.ts');
  const store = useCollectionFactsStore();
  store.setSourceKey('missing-fixture');
  await store.load();
  assert.equal(store.contract.value, null);
  await store.updateQuery({ name: 'temperature', page: 2, pageSize: 10 });
  await store.listAllFacts();
  assert.ok(requests.some(item => item.url.includes('name=temperature')));
  assert.ok(requests.every(item => item.method === 'GET'));
  const api = await server.ssrLoadModule('/src/app/twin-facts/api/index.ts');
  assert.equal(Object.keys(api).some(key => /Simulation|previewCollectionFactsContract|applyCollectionFactsContract|updateCollectionFactValues/.test(key)), false);
}));

test('JSON/XLSX config template/export/import and explicit preview/apply remain separate', async () => withModules(async (server, requests, _storage, ipcCalls) => {
  const files = await server.ssrLoadModule('/src/app/twin-facts/utils/mappingConfigurationFiles.ts');
  const api = await server.ssrLoadModule('/src/app/twin-facts/api/index.ts');
  const items = {
    targetApis: { apiKey: 'fixture', name: 'Fixture', httpMethod: 'POST', path: '/fixture', schemaSource: 'manual', operationId: null, bodyTemplate: {}, parameterSchema: [], idempotencySupported: false, enabled: true },
    mappingValueRules: { valueRuleKey: 'fixture', name: 'Fixture', dataType: 'integer', values: [1,2], originSourceKey: null, originFactName: null, enabled: true },
    mappings: { mappingKey: 'fixture', name: 'Fixture', sourceKey: null, targetApiKey: 'fixture', bindings: {}, intervalMs: 2500, enabled: true },
  };
  const creators = { targetApis: files.createTargetApiExportFile, mappingValueRules: files.createMappingValueRuleExportFile, mappings: files.createMappingConfigurationExportFile };
  for (const resource of Object.keys(items)) for (const format of ['json', 'xlsx']) {
    const makeFile = generated => new File([generated.contents], generated.fileName, { type: generated.mimeType });
    const template = files.createMappingConfigurationTemplateFile(resource, format);
    assert.deepEqual(await files.parseMappingConfigurationFile(resource, makeFile(template)), []);
    const generated = creators[resource](format, [items[resource]]);
    const parsed = await files.parseMappingConfigurationFile(resource, makeFile(generated));
    assert.equal(parsed.length, 1);
    assert.equal(parsed[0].enabled, true);
    if (resource === 'mappings') assert.equal(parsed[0].intervalMs, 2500);
  }
  assert.equal(requests.length, 0, 'file parsing/export is pure');
  const functions = [
    [api.previewTargetApiImportInBackend, api.applyTargetApiImportInBackend],
    [api.previewMappingValueRuleImportInBackend, api.applyMappingValueRuleImportInBackend],
    [api.previewMappingConfigurationImportInBackend, api.applyMappingConfigurationImportInBackend],
  ];
  for (const [preview, apply] of functions) {
    const before = requests.length;
    await preview([{}]);
    assert.equal(requests.length, before);
    assert.equal(ipcCalls.at(-1).command, 'preview_local_configuration');
    await apply([{}]);
    assert.equal(ipcCalls.at(-1).command, 'apply_local_configuration');
    assert.equal(requests.length, before);
  }
  const facts = await server.ssrLoadModule('/src/app/twin-facts/utils/collectionFactFiles.ts');
  for (const format of ['json','xlsx']) {
    const generated = facts.createValueExportFile(format, 'source', [{ sourceKey:'source', contractVersion:'v1', name:'point', value:null }]);
    if (format === 'json') assert.equal(JSON.parse(new TextDecoder().decode(generated.contents)).values[0].value, null);
    else assert.equal(XLSX.read(generated.contents).SheetNames[0], 'values');
  }
}));

test('table widths persist by stable field id and reset; Shanghai time rejects missing/monotonic values', async () => withModules(async (server, _requests, storage) => {
  const { useTableWidths, resolveTableWidths } = await server.ssrLoadModule('/src/console/tableWidths.ts');
  const columns = [{ id:'name',width:220,min:100 },{id:'updatedAt',width:190,min:160}];
  assert.deepEqual(resolveTableWidths(columns, { name:20, removed:999, updatedAt:'bad' }), {name:100,updatedAt:190});
  const listeners = new Map();
  window.addEventListener = (event, callback) => listeners.set(event, callback);
  window.removeEventListener = event => listeners.delete(event);
  async function makeTable(id) {
    let table;
    await renderToString(createSSRApp({ setup() { table = useTableWidths(id, columns); return () => null; } }));
    return table;
  }
  const table = await makeTable('source-facts');
  table.startResize('name', { button:0, clientX:220, preventDefault(){} });
  listeners.get('pointermove')({ clientX:320 });
  listeners.get('pointerup')();
  assert.equal(table.widths.value.name, 320);
  assert.equal((await makeTable('source-facts')).widths.value.name, 320);
  assert.equal((await makeTable('other-table')).widths.value.name, 220);
  table.reset();
  assert.equal(table.widths.value.name,220);
  assert.equal(storage.has('sma.table-widths.v1.source-facts'), false);
  assert.equal(listeners.size,0);
  const { formatBusinessTime } = await server.ssrLoadModule('/src/console/time.ts');
  assert.equal(formatBusinessTime('2026-11-03T16:00:01.123Z'),'2026-11-04 00:00:01');
  assert.equal(formatBusinessTime('2026-11-04T00:00:01.987+08:00'),'2026-11-04 00:00:01');
  for (const value of [null,'123456','2026-11-04T00:00:00','invalid']) assert.equal(formatBusinessTime(value,'missing'),'missing');
}));

test('retired paths/IPC/help metadata close and bilingual manifest/labels resolve', async () => {
  const walk = path => readdirSync(path, { withFileTypes: true }).flatMap(entry => entry.isDirectory() ? walk(`${path}/${entry.name}`) : [`${path}/${entry.name}`]);
  const source = walk('src').filter(path => /\.(ts|vue|css)$/.test(path)).map(path => readFileSync(path,'utf8')).join('\n');
  assert.doesNotMatch(source,/collectionFactSimulation|SimulationRuntime|simulation-rules|\/values["`]|helpQuickStart|helpGlossary|helpTopicId|helpKey|markdown-it/);
  const rust = walk('src-tauri/src').filter(path => path.endsWith('.rs') && !path.endsWith('config/runtime_startup.rs')).map(path => readFileSync(path,'utf8')).join('\n');
  assert.doesNotMatch(rust,/collection_fact_simulation|services::simulation/);
  await withModules(async server => {
    const { getMessages } = await server.ssrLoadModule('/src/locales/index.ts');
    const { pageManifests } = await server.ssrLoadModule('/src/app/registry.ts');
    const en = getMessages('en-US'), zh = getMessages('zh-CN');
    assert.deepEqual(Object.keys(en).sort(), Object.keys(zh).sort());
    for (const labels of [en,zh]) {
      for (const page of pageManifests) {
        assert.ok(labels[page.labelKey]);
        for(const view of page.views ?? []) assert.ok(labels[view.labelKey]);
      }
      for (const match of source.matchAll(/labels\.(\w+)/g)) if (match[1] !== 'value') assert.ok(match[1] in labels,`missing ${match[1]}`);
    }
  });
});
