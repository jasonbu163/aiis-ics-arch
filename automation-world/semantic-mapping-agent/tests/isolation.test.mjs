/** SMA configuration/storage isolation and fail-closed HTTP facade regression. */
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { createServer } from 'vite';

test('old TSS storage is ignored and all disabled HTTP entry points reject before fetch', async () => {
  const storage = new Map([['tss.backend-connection.v1', JSON.stringify({ scheme: 'http', host: 'old-profile.invalid', port: 8144 })]]);
  globalThis.window = { localStorage: { getItem: key => storage.get(key) ?? null, setItem: (key, value) => storage.set(key, value) }, dispatchEvent: () => true };
  let requests = 0;
  const previousFetch = globalThis.fetch;
  globalThis.fetch = async () => { requests++; throw new Error('external request must not occur'); };
  const server = await createServer({ configFile: false, optimizeDeps: { noDiscovery: true, include: [], entries: [] }, server: { middlewareMode: true, hmr: false, ws: false } });
  try {
    const connection = await server.ssrLoadModule('/src/app/connection/api/index.ts');
    const facts = await server.ssrLoadModule('/src/app/twin-facts/api/index.ts');
    assert.deepEqual(connection.loadBackendConnectionProfile(), { scheme: 'http', host: '', port: 0 });
    assert.equal((await connection.loadAppDefaults()).externalIoEnabled, false);
    await assert.rejects(connection.testBackendOpenApi({ scheme: 'http', host: 'fixture.invalid', port: 9000 }), /SMA_EXTERNAL_IO_DISABLED/);
    await assert.rejects(connection.managementRequest('/never'), /SMA_EXTERNAL_IO_DISABLED/);
    await assert.rejects(facts.listTargetApiConfigurationsFromBackend(), /SMA_EXTERNAL_IO_DISABLED/);
    assert.equal(requests, 0);
    connection.saveBackendConnectionProfile({ scheme: 'http', host: 'fixture.invalid', port: 9000 });
    assert.ok(storage.has('sma.backend-connection.v1'));
    assert.equal(JSON.parse(storage.get('tss.backend-connection.v1')).host, 'old-profile.invalid');
  } finally { await server.close(); globalThis.fetch = previousFetch; delete globalThis.window; }
});

test('inherited mapping preview preserves path/query/header/body and typed facts without HTTP', async () => {
  const server = await createServer({ configFile: false, optimizeDeps: { noDiscovery: true, include: [], entries: [] }, server: { middlewareMode: true, hmr: false, ws: false } });
  try {
    const { buildMappingRequestPreview } = await server.ssrLoadModule('/src/app/twin-facts/store/mappingConfigurations.ts');
    const parameter = (location, name, jsonPath = null) => ({ parameterKey: `${location}:${name}`, location, name, jsonPath, dataType: 'string', required: true });
    const target = { path: '/measure/{id}', parameterSchema: [parameter('path', 'id'), parameter('query', 'mode'), parameter('header', 'X-Fixture'), parameter('body', 'measurement', 'sample.value')] };
    const fixed = value => ({ kind: 'constant', value, sourceKey: null, factName: null, valueRuleKey: null });
    const preview = buildMappingRequestPreview(target, { 'path:id': fixed('fixture/a'), 'query:mode': fixed('local'), 'header:X-Fixture': fixed('review'), 'body:measurement': { kind: 'fact', sourceKey: 'fixture-source', factName: 'measurement', valueRuleKey: null } }, [{ sourceKey: 'fixture-source', name: 'measurement', dataType: 'number', value: '3.5' }]);
    assert.deepEqual(preview, { resolvedPath: '/measure/fixture%2Fa', query: { mode: 'local' }, headers: { 'X-Fixture': 'review' }, body: { sample: { value: 3.5 } }, unresolved: [] });
  } finally { await server.close(); }
});
