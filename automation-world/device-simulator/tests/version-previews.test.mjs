/** 版本列表事实刷新与取消的两个增量自检：用真实Vue状态及只读IPC替身，不开窗口/用户库。 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import vm from 'node:vm';
import ts from 'typescript';

const require = createRequire(import.meta.url);
const source = readFileSync(new URL('../src/console/composables/useDeviceSimulator.ts', import.meta.url), 'utf8');
const code = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } }).outputText;
class IpcFailure extends Error { constructor(code) { super(code); this.code = code; this.unknown = false; this.currentEtag = null; } }
function host(ipc) {
    const context = { exports: {}, require: name => name === 'vue' ? require('vue') : { IpcFailure, ...ipc } };
    vm.runInNewContext(code, context, { filename: 'useDeviceSimulator.js' });
    return context.exports.useDeviceSimulator();
}
function facts(revision, offset = 0) {
    return { etag: 'persisted-etag', workspace: { schemaVersion: 1, instances: [], sourceVersions: [] }, revisions: [{ revisionId: revision, canDelete: true, protection: [] }], revisionTotal: 101, selections: [], latestRevision: revision, draftMatchesLatest: false, offset };
}
function edit(state) {
    state.configuration.value = facts('original');
    state.draft.value = { schemaVersion: 1, instances: [{ id: 'synthetic', name: 'unsaved edit' }], sourceVersions: [] };
    return state.draft.value;
}

test('revision refresh updates facts without replacing the unsaved editor or its saved CAS identity', async () => {
    const state = host({ getConfiguration: async () => ({ ...facts('fresh'), etag: 'external-etag' }) });
    const draft = edit(state);
    await state.refreshRevisions();
    assert.equal(state.draft.value, draft);
    assert.equal(state.draft.value.instances[0].name, 'unsaved edit');
    assert.equal(state.configuration.value.etag, 'persisted-etag');
    assert.equal(state.configuration.value.workspace.instances.length, 0);
    assert.equal(state.configuration.value.latestRevision, 'fresh');
    assert.equal(state.configuration.value.revisions[0].revisionId, 'fresh');
    assert.equal(state.dirty.value, true);
});

test('late older lists are discarded and preview cancellation refreshes occupancy even while another operation is busy', async () => {
    const waiting = [], cancelled = [];
    let immediate = false;
    const state = host({ getConfiguration: () => immediate ? Promise.resolve(facts('released')) : new Promise(resolve => waiting.push(resolve)), cancelPreview: async preview => { cancelled.push(preview.token); } });
    const draft = edit(state);
    const older = state.refreshRevisions(0), newer = state.refreshRevisions(100);
    waiting[1](facts('newer')); await newer;
    waiting[0](facts('older')); await older;
    assert.equal(state.configuration.value.revisions[0].revisionId, 'newer');
    assert.equal(state.revisionOffset.value, 100);
    state.busy.value = true;
    state.unknown.value = true;
    immediate = true;
    await state.releasePreview({ token: 'synthetic-preview' });
    assert.deepEqual(cancelled, ['synthetic-preview']);
    assert.equal(state.configuration.value.revisions[0].revisionId, 'released');
    assert.equal(state.configuration.value.revisions[0].canDelete, true);
    assert.equal(state.busy.value, true);
    assert.equal(state.unknown.value, true);
    assert.equal(state.draft.value, draft);
});
