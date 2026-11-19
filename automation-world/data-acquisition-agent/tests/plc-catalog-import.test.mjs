/** 目录导入 owner：只读预览、目标变更失效、一次提交与未知结果恢复。 */
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const ts = require('typescript'), vue = require('vue');
const source = readFileSync(new URL('../src/console/composables/useLocalAcquisitionConsole.ts', import.meta.url), 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText;
const clone = value => JSON.parse(JSON.stringify(value));
class LocalCommandError extends Error { constructor(code, unknown = false) { super(code); this.commitUnknown = unknown; } }
const catalog = JSON.parse(readFileSync(new URL('./fixtures/plc-catalog-v1.json', import.meta.url), 'utf8'));

async function fixture(t) {
    const draft = { schemaVersion: 1, plcs: [], dbs: [], points: [], groups: [], sources: [], storage: { quotaBytes: 1073741824, retentionDays: 7 } };
    const server = { view: { schemaVersion: 1, draft, etag: 'e1', active: null, previous: null, loaded: null, used: null, phase: 'loaded', issues: [] }, calls: [], failConfirm: null, failPreview: null, failReload: null, remap: false, missingId: false };
    const service = { bootstrap: { localStorage: true, origin: 'fixture' }, LocalCommandError,
        async localCall(command, request) {
            server.calls.push({ command, request: clone(request ?? null) });
            if (command === 'daa_get_configuration') {
                if (server.failReload) { const error = server.failReload; server.failReload = null; throw error; }
                return clone(server.view);
            }
            if (command === 'daa_get_local_snapshot') return { operations: [] };
            if (command === 'daa_cancel_catalog') return {};
            if (command === 'daa_preview_catalog') {
                if (server.failPreview) { const error = server.failPreview; server.failPreview = null; throw error; }
                assert.equal(request.expectedEtag, server.view.etag);
                return { catalog: clone(catalog), sha256: 'file-sha', target: clone(request.target ?? catalog.plc.connection), previewToken: 'token-' + server.calls.length, etag: request.expectedEtag, historyConflict: server.remap, localPlcId: server.remap ? 'new-local-id' : catalog.origin.plc_id, localDbIds: {}, localPointIds: {} };
            }
            if (command === 'daa_confirm_catalog') {
                if (server.failConfirm) { const error = server.failConfirm; server.failConfirm = null; throw error; }
                assert.equal(request.input.expectedEtag, server.view.etag);
                if (server.remap && !request.input.asNewLocalInstance) throw new LocalCommandError('catalog_history_choice_required');
                const localId = server.remap ? 'new-local-id' : catalog.origin.plc_id;
                server.view.draft.plcs.push({ id: localId, name: catalog.plc.name });
                server.view.etag = 'e2';
                return clone({ ...server.view, ...(server.missingId ? {} : { importedLocalPlcId: localId }) });
            }
            throw new Error('unexpected IPC ' + command);
        },
        previewPointNames() { throw new Error('unexpected point preview'); },
        confirmPointNames() { throw new Error('unexpected point confirmation'); },
    };
    const module = { exports: {} };
    new Function('require', 'module', 'exports', compiled)(id => {
        if (id === 'vue') return { ...vue, onMounted() {}, onUnmounted() {} };
        if (id === 'element-plus') return { ElMessageBox: { confirm: async () => {} } };
        if (id === 'vue-i18n') return { useI18n: () => ({ t: key => key, te: () => false }) };
        if (id.endsWith('/services/localAcquisition')) return service;
        if (id.endsWith('/services/factsDelivery')) return {};
        if (id === '../time') return {};
        throw new Error('unexpected import ' + id);
    }, module, module.exports);
    const scope = vue.effectScope(), local = scope.run(() => module.exports.useLocalAcquisitionConsole());
    t.after(() => scope.stop());
    await local.reload(); await vue.nextTick();
    return { local, server };
}
const fileEvent = (bytes = [123, 125]) => ({ target: { files: [{ name: 'export.json', size: bytes.length, slice: (start, end) => ({ arrayBuffer: async () => Uint8Array.from(bytes.slice(start, end)).buffer }) }], value: 'selected' } });

test('preview is read only; target changes require a fresh confirmation', async t => {
    const { local, server } = await fixture(t);
    local.openCatalog();
    await local.readCatalogFile(fileEvent([0x7b, 0x7d, 0x0a]));
    assert.equal(local.catalogPreview.sha256, 'file-sha');
    assert.deepEqual(server.calls.at(-1).request.bytes, [0x7b, 0x7d, 0x0a]);
    assert.equal(server.view.etag, 'e1');
    local.catalogConfirmed = true;
    local.catalogTarget.port = 31999;
    assert.equal(local.catalogPreview, null);
    assert.equal(local.catalogConfirmed, false);
    await local.confirmCatalog();
    assert.equal(server.calls.filter(call => call.command === 'daa_confirm_catalog').length, 0);
    await local.previewCatalog();
    assert.equal(server.calls.at(-1).request.target.port, 31999);
    local.catalogConfirmed = true;
    await local.confirmCatalog();
    const commit = server.calls.find(call => call.command === 'daa_confirm_catalog');
    assert.equal(commit.request.input.target.port, 31999);
    assert.deepEqual(commit.request.input.bytes, [0x7b, 0x7d, 0x0a]);
    assert.equal(server.view.etag, 'e2');
    assert.equal(local.catalogDialogOpen, false);
    assert.equal(local.selectedPlc, catalog.origin.plc_id);
});

test('a conflicting initial endpoint remains editable before a new preview', async t => {
    const { local, server } = await fixture(t);
    const bytes = [...Buffer.from(JSON.stringify(catalog))];
    server.failPreview = new LocalCommandError('duplicate_endpoint');
    local.openCatalog(); await local.readCatalogFile(fileEvent(bytes));
    assert.equal(local.error, 'duplicate_endpoint');
    assert.equal(local.catalogTarget.host, catalog.plc.connection.host);
    local.catalogTarget.port = 31999;
    await local.previewCatalog();
    assert.equal(server.calls.at(-1).request.target.port, 31999);
    assert.ok(local.catalogPreview);
    assert.equal(server.view.etag, 'e1');
});

test('historical import selects the committed local identity and never guesses an unknown result', async t => {
    const { local, server } = await fixture(t); server.remap = true;
    local.openCatalog(); await local.readCatalogFile(fileEvent());
    assert.equal(local.catalogPreview.historyConflict, true);
    local.catalogTarget.port = 31990;
    local.catalogAsNew = true; await local.previewCatalog(); local.catalogConfirmed = true;
    await local.confirmCatalog();
    assert.equal(server.calls.find(call => call.command === 'daa_confirm_catalog').request.input.asNewLocalInstance, true);
    assert.equal(server.calls.find(call => call.command === 'daa_confirm_catalog').request.input.target.port, 31990);
    assert.equal(local.selectedPlc, 'new-local-id');
    assert.equal(local.selectedDb, '');
    const next = await fixture(t); next.server.remap = true; next.server.missingId = true;
    next.local.openCatalog(); await next.local.readCatalogFile(fileEvent()); next.local.catalogAsNew = true;
    await next.local.previewCatalog(); next.local.catalogConfirmed = true; await next.local.confirmCatalog();
    assert.equal(next.local.catalogUnknown, true);
    assert.notEqual(next.local.selectedPlc, 'new-local-id');
});

test('cancel does not save; unknown result blocks retry until successful reload', async t => {
    const { local, server } = await fixture(t);
    local.openCatalog(); await local.readCatalogFile(fileEvent());
    local.closeCatalog(); await vue.nextTick();
    assert.equal(server.calls.at(-1).command, 'daa_cancel_catalog');
    assert.equal(server.view.etag, 'e1');
    local.openCatalog(); await local.readCatalogFile(fileEvent());
    local.catalogConfirmed = true; server.failConfirm = new LocalCommandError('storage_pending');
    await local.confirmCatalog();
    assert.equal(local.catalogUnknown, true);
    const calls = server.calls.filter(call => call.command === 'daa_confirm_catalog').length;
    await local.confirmCatalog(); await local.previewCatalog(); await local.save(); await local.activate();
    assert.equal(server.calls.filter(call => call.command === 'daa_confirm_catalog').length, calls);
    server.failReload = new Error('not available'); await local.reload();
    assert.equal(local.catalogUnknown, true);
    await local.reload();
    assert.equal(local.catalogUnknown, false);
    assert.equal(server.view.etag, 'e1');
});

test('changed or unreadable selected file invalidates preview before commit', async t => {
    const { local, server } = await fixture(t);
    let bytes = [123, 125];
    const file = { name: 'export.json', size: 2, slice: (start, end) => ({ arrayBuffer: async () => {
        if (!bytes) throw new Error('file gone');
        return Uint8Array.from(bytes.slice(start, end)).buffer;
    } }) };
    const event = () => ({ target: { files: [file], value: 'selected' } });
    local.openCatalog(); await local.readCatalogFile(event()); local.catalogConfirmed = true;
    bytes = [123, 32]; await local.confirmCatalog();
    assert.equal(server.calls.filter(call => call.command === 'daa_confirm_catalog').length, 0);
    assert.equal(server.calls.at(-1).command, 'daa_cancel_catalog');
    assert.equal(local.catalogPreview, null);
    assert.equal(local.catalogUnknown, false);
    assert.equal(local.error, 'catalog_file_changed');
    bytes = [123, 125]; await local.readCatalogFile(event()); local.catalogConfirmed = true;
    bytes = null; await local.confirmCatalog();
    assert.equal(server.calls.filter(call => call.command === 'daa_confirm_catalog').length, 0);
    assert.equal(local.catalogUnknown, false);
    assert.equal(local.error, 'catalog_file_changed');
});

test('catalog controls and both locale trees remain present', () => {
    const sourcePanel = readFileSync(new URL('../src/app/plc/components/SourceImportPanel.vue', import.meta.url), 'utf8');
    const dialog = readFileSync(new URL('../src/app/plc/components/CatalogImportDialog.vue', import.meta.url), 'utf8');
    const page = readFileSync(new URL('../src/app/plc/views/diagnostics/index.vue', import.meta.url), 'utf8');
    assert.doesNotMatch(sourcePanel, /CatalogImportDialog/);
    assert.match(page, /CatalogImportDialog/);
    assert.match(dialog, /catalogConfirmed/);
    assert.match(dialog, /catalog\.dbs/);
    const zh = JSON.parse(readFileSync(new URL('../src/app/plc/locales/zh-CN.json', import.meta.url)));
    const en = JSON.parse(readFileSync(new URL('../src/app/plc/locales/en-US.json', import.meta.url)));
    const keys = o => Object.keys(o).sort().flatMap(k => o[k] && typeof o[k] === 'object' ? keys(o[k]).map(child => `${k}.${child}`) : [k]);
    assert.deepEqual(keys(zh.catalog), keys(en.catalog));
});
