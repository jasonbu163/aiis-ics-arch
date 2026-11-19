/** 唯一宿主状态owner：编辑副本与快照分开，显式保存/应用；可见时每秒最多一次快照。 */
import { ref, shallowRef, computed, type InjectionKey, type UnwrapNestedRefs } from 'vue';
import * as ipc from '../../services/deviceSimulator';

// 工作区是 JSON；比较字段值而不依赖前后端对象键的序列化顺序。
function sameJson(a: unknown, b: unknown): boolean {
    if (a === b) return true;
    if (Array.isArray(a) || Array.isArray(b))
        return Array.isArray(a) && Array.isArray(b) && a.length === b.length && a.every((v, i) => sameJson(v, b[i]));
    if (!a || !b || typeof a !== 'object' || typeof b !== 'object') return false;
    const left = a as Record<string, unknown>, right = b as Record<string, unknown>, keys = Object.keys(left);
    return keys.length === Object.keys(right).length && keys.every(key => Object.prototype.hasOwnProperty.call(right, key) && sameJson(left[key], right[key]));
}
type ControlUnknown = {id: number; instanceId: string; command: 'stop' | 'pause'; code: string; epoch: string; loadedRevision: string | null};
type ControlFact = {instanceId: string; name: string; state: string; epoch: string; loadedRevision: string | null};
type SavePending = {expectedEtag: string; submitted: ipc.Workspace; confirmPoints: string[]; reason: 'save_receipt_unknown' | 'save_commit_unknown' | 'runtime_task_receipt_unknown' | 'ipc_transport_unknown' | 'known_readback' | 'known_cleanup'; cleanupUnproven: boolean};
type PreviewRelease = {id: number; preview: ipc.Preview; related: boolean; state: 'inflight' | 'deferred'};
type PreviewUnknown = {id: number; kind: string; code: string};
function controlFacts(snapshot: ipc.RuntimeSnapshot, pending: ControlUnknown[]): ControlFact[] | null {
    if (snapshot.stale !== false || !Array.isArray(snapshot.instances)) return null;
    const facts: ControlFact[] = [];
    for (const instanceId of new Set(pending.map(item => item.instanceId))) {
        const matches = snapshot.instances.filter(row => row.instanceId === instanceId);
        const row = matches[0];
        if (matches.length !== 1 || typeof row.name !== 'string' || !['running', 'paused', 'stopped', 'load_failed'].includes(row.state) || typeof row.epoch !== 'string' || !/^\d+$/.test(row.epoch) || (row.loadedRevision !== null && (typeof row.loadedRevision !== 'string' || !row.loadedRevision)) || (['running', 'paused'].includes(row.state) && !row.loadedRevision)) return null;
        facts.push({instanceId, name: row.name, state: row.state, epoch: row.epoch, loadedRevision: row.loadedRevision});
    }
    return facts;
}
export function useDeviceSimulator() {
    const lastSavedRevision = ref<string | null>(null);
    const editing = ref(false), finishEditor = ref<null | (() => boolean)>(null), discardEditor = ref<null | (() => void)>(null);
    const busy = ref(false), refreshing = ref(false), error = ref<string | null>(null), unknown = ref(false), conflictEtag = ref<string | null>(null);
    const bootstrap = ref<ipc.Bootstrap | null>(null), configuration = ref<ipc.Configuration | null>(null), draft = ref<ipc.Workspace | null>(null), base = ref(''), snapshot = ref<ipc.RuntimeSnapshot | null>(null);
    const uncertainSave = shallowRef<SavePending | null>(null);
    const saveReview = shallowRef<{configuration: ipc.Configuration; matchesSubmitted: boolean; diffLocal: string | null} | null>(null);
    const checkingSave = ref(false), saveReviewError = ref<'read' | 'changed' | 'local' | null>(null);
    const uncertainControls = shallowRef<ControlUnknown[]>([]);
    const controlReview = shallowRef<{facts: ControlFact[]; generation: number} | null>(null);
    const checkingControls = ref(false), controlReviewError = ref<'read' | 'changed' | null>(null);
    const saving = ref(false), saveOutcome = ref<'saved' | 'unchanged' | null>(null), saveFailure = ref<string | null>(null), closeGate = ref(false);
    const previewReleases = shallowRef<PreviewRelease[]>([]), previewUnknowns = shallowRef<PreviewUnknown[]>([]);
    const instanceId = ref(''), dbId = ref(''), valueOffset = ref(0), valueLimit = ref(50), logs = ref<Awaited<ReturnType<typeof ipc.queryLogs>> | null>(null);
    const revisionOffset = ref(0);
    const dirty = computed(() => !!uncertainSave.value || !!uncertainControls.value.length || !!previewUnknowns.value.length || !!previewReleases.value.length || !!draft.value && JSON.stringify(draft.value) !== base.value);
    const selected = computed(() => draft.value?.instances.find(i => i.id === instanceId.value) || null);
    const selectedDb = computed(() => selected.value?.dbs.find(d => d.id === dbId.value) || null);
    const runtime = computed(() => snapshot.value?.instances.find(i => i.instanceId === instanceId.value) || null);
    function failure(e: unknown) { if (uncertainSave.value || uncertainControls.value.length || previewUnknowns.value.length) { restoreOutstanding(); return; } const f = e instanceof ipc.IpcFailure ? e : new ipc.IpcFailure('operation_failed'); error.value = f.code; unknown.value = f.unknown; conflictEtag.value = f.currentEtag; }
    let lastSafetyFailure: ipc.IpcFailure | null = null, controlGeneration = 0, controlSequence = 0, previewSequence = 0;
    function restoreOutstanding() {
        if (uncertainControls.value.length) { error.value = 'runtime_controls_unknown'; unknown.value = true; }
        else if (uncertainSave.value) { error.value = uncertainSave.value.reason === 'known_readback' ? 'saved_readback_unavailable' : uncertainSave.value.reason === 'known_cleanup' ? 'saved_cleanup_pending' : uncertainSave.value.reason; unknown.value = !['known_readback', 'known_cleanup'].includes(uncertainSave.value.reason) || !!previewUnknowns.value.length; }
        else if (previewUnknowns.value.length) { error.value = 'preview_release_unknown'; unknown.value = true; }
        else { error.value = lastSafetyFailure?.code ?? null; unknown.value = lastSafetyFailure?.unknown ?? false; conflictEtag.value = lastSafetyFailure?.currentEtag ?? null; lastSafetyFailure = null; }
    }
    function clearUncertainSave() { uncertainSave.value = null; saveReview.value = null; saveReviewError.value = null; restoreOutstanding(); }
    const saveCanResolve = computed(() => !!uncertainSave.value && !uncertainSave.value.cleanupUnproven && !['ipc_transport_unknown', 'runtime_task_receipt_unknown'].includes(uncertainSave.value.reason));
    let permitUncertainReload = false, saveReloadGuard: string | null = null, saveReceiptEtag: string | null = null;
    async function reload() { if (uncertainSave.value && !permitUncertainReload) throw new ipc.IpcFailure('save_receipt_unknown', null, true);
        const localBefore = uncertainSave.value || saveReloadGuard !== null ? JSON.stringify(draft.value) : null;
        if (saveReloadGuard !== null && (editing.value || localBefore !== saveReloadGuard)) throw new ipc.IpcFailure('save_receipt_unknown', null, true);
        const loaded = await ipc.getConfiguration(null, revisionOffset.value);
        if (localBefore !== null && (editing.value || JSON.stringify(draft.value) !== localBefore)) { saveReviewError.value = 'local'; throw new ipc.IpcFailure('save_receipt_unknown', null, true); }
        if (saveReloadGuard !== null && (!saveReceiptEtag || loaded.etag !== saveReceiptEtag)) { saveReviewError.value = 'changed'; throw new ipc.IpcFailure('saved_readback_unavailable'); }
        if (uncertainSave.value && (!saveReview.value || loaded.etag !== saveReview.value.configuration.etag || !sameJson(loaded.workspace, saveReview.value.configuration.workspace))) { saveReviewError.value = 'changed'; throw new ipc.IpcFailure('save_receipt_unknown', null, true); }
        configuration.value = loaded; draft.value = structuredClone(loaded.workspace); base.value = JSON.stringify(loaded.workspace); if (!loaded.workspace.instances.some(i => i.id === instanceId.value))
        instanceId.value = loaded.workspace.instances[0]?.id || ''; if (!selected.value?.dbs.some(d => d.id === dbId.value))
        dbId.value = selected.value?.dbs[0]?.id || ''; }
    let lastRefresh = 0;
    async function refresh() { const now = performance.now(); if (!ipc.desktopAvailable || refreshing.value || document.hidden || now - lastRefresh < 1000 && lastRefresh !== 0)
        return; lastRefresh = now; refreshing.value = true; try {
        if (!bootstrap.value)
            bootstrap.value = await ipc.getBootstrap();
        if (!configuration.value)
            await reload();
        const request = { instanceId: instanceId.value, offset: valueOffset.value, limit: valueLimit.value };
        const includeValues = snapshot.value?.instances.find(i => i.instanceId === request.instanceId)?.loadedRevision ? request.instanceId : null;
        const loaded = await ipc.getSnapshot(includeValues, request.offset, request.limit);
        if (!Array.isArray(loaded.instances))
            throw new ipc.IpcFailure('snapshot_format');
        if (request.instanceId === instanceId.value && request.offset === valueOffset.value && request.limit === valueLimit.value)
            snapshot.value = loaded;
    }
    catch (e) {
        // 只读快照失败不能清除另一个操作已有的未知回执。
        if (!unknown.value || uncertainSave.value || uncertainControls.value.length || previewUnknowns.value.length) failure(e);
        if (snapshot.value)
            snapshot.value.stale = true;
    }
    finally {
        refreshing.value = false;
    } }
    async function action<T>(work: () => Promise<T>, reloadAfter = false, control?: Omit<ControlUnknown, 'id' | 'code'>): Promise<T | undefined> {
        const related = !!control && !!(uncertainSave.value || uncertainControls.value.length || previewUnknowns.value.length);
        const resolvingReload = saveCanResolve.value && work === reload && !!saveReview.value && saveReview.value.diffLocal === JSON.stringify(draft.value) && !editing.value && !checkingSave.value;
        if (busy.value || ((uncertainSave.value || uncertainControls.value.length || previewUnknowns.value.length) && !resolvingReload && !control)) return;
        busy.value = true; if (!uncertainSave.value && !uncertainControls.value.length && !previewUnknowns.value.length) { error.value = null; unknown.value = false; lastSafetyFailure = null; }
        permitUncertainReload = resolvingReload;
        try {
        const result = await work();
        if (reloadAfter)
            await reload();
        if (resolvingReload) clearUncertainSave();
        await refresh();
        return result;
    }
    catch (e) {
        if (control && related) {
            const f = e instanceof ipc.IpcFailure ? e : new ipc.IpcFailure('operation_failed');
            if (f.unknown) { uncertainControls.value = [...uncertainControls.value, {...control, id: ++controlSequence, code: f.code}]; controlReview.value = null; controlGeneration++; }
            lastSafetyFailure = f;
            error.value = f.code; unknown.value = !!(uncertainSave.value || uncertainControls.value.length || previewUnknowns.value.length); conflictEtag.value = f.currentEtag;
        }
        else failure(e);
        return undefined;
    }
    finally {
        permitUncertainReload = false;
        busy.value = false;
    } }
    async function save(confirmPoints: string[] = []) { if (editing.value || busy.value || unknown.value || uncertainSave.value || uncertainControls.value.length || previewUnknowns.value.length || !draft.value || !configuration.value) return false;
        const expectedEtag = configuration.value.etag, submitted: ipc.Workspace = JSON.parse(JSON.stringify(draft.value)), submittedConfirmPoints = [...confirmPoints];
        const removed = configuration.value.workspace.instances.filter(old => !submitted.instances.some(i => i.id === old.id)).map(i => i.id);
        const receipt: {value: ipc.SaveResult | null} = {value: null};
        const markUncertain = (reason: SavePending['reason'], cleanupUnproven: boolean) => { uncertainSave.value = {expectedEtag, submitted, confirmPoints: submittedConfirmPoints, reason, cleanupUnproven}; saveReview.value = null; saveReviewError.value = null; lastSafetyFailure = null; };
        saving.value = true; saveOutcome.value = null; saveFailure.value = null;
        previewReleases.value = previewReleases.value.map(item => ({...item, related: true}));
        saveReloadGuard = JSON.stringify(submitted);
        let result;
        try { result = await action(async () => {
            try { const saved = await ipc.saveConfiguration(expectedEtag, submitted, submittedConfirmPoints); receipt.value = saved; saveReceiptEtag = saved.etag; saveOutcome.value = saved.result; return saved; }
            catch (e) { if (e instanceof ipc.IpcFailure && e.unknown) { const reason = ['save_receipt_unknown', 'save_commit_unknown', 'runtime_task_receipt_unknown'].includes(e.code) ? e.code as SavePending['reason'] : 'ipc_transport_unknown'; markUncertain(reason, !!removed.length); } else saveFailure.value = e instanceof ipc.IpcFailure ? e.code : 'operation_failed'; throw e; }
        }, true); } finally { saveReloadGuard = null; saveReceiptEtag = null; saving.value = false; }
        // 保存已知返回后，读取最新草稿失败也不能继续沿用旧 ETag。
        if (receipt.value && removed.length && (!Array.isArray(receipt.value.cleanupPending) || receipt.value.cleanupPending.length)) { markUncertain('known_cleanup', true); restoreOutstanding(); }
        else if (receipt.value && result === undefined) { markUncertain('known_readback', false); restoreOutstanding(); }
        return result !== undefined && !unknown.value && !uncertainSave.value && !uncertainControls.value.length && !previewUnknowns.value.length && !previewReleases.value.length;
    }
    async function commitCatalogImport(fileToken: string, preview: ipc.Preview) {
        if (editing.value || busy.value || unknown.value || dirty.value || !draft.value || !configuration.value || configuration.value.etag !== preview.expectedEtag) return false;
        const submitted: ipc.Workspace = JSON.parse(JSON.stringify(preview.workspace)), original = JSON.stringify(draft.value);
        const newId = submitted.instances.find(i => !draft.value!.instances.some(old => old.id === i.id))?.id;
        let receipt: ipc.SaveResult | null = null;
        const markPending = (reason: SavePending['reason']) => {
            if (!editing.value && JSON.stringify(draft.value) === original) {
                draft.value = structuredClone(submitted);
                if (newId) instanceId.value = newId;
            }
            uncertainSave.value = {expectedEtag: preview.expectedEtag, submitted, confirmPoints: [], reason, cleanupUnproven: false};
            saveReview.value = null; saveReviewError.value = null; lastSafetyFailure = null;
        };
        saving.value = true; saveOutcome.value = null; saveFailure.value = null; saveReloadGuard = original;
        let result;
        try { result = await action(async () => {
            try { const saved = await ipc.confirmCatalogImport(fileToken, preview); receipt = saved; saveReceiptEtag = saved.etag; saveOutcome.value = saved.result; return saved; }
            catch (e) { if (e instanceof ipc.IpcFailure && e.unknown) { const reason = ['save_receipt_unknown', 'save_commit_unknown', 'runtime_task_receipt_unknown'].includes(e.code) ? e.code as SavePending['reason'] : 'ipc_transport_unknown'; markPending(reason); } throw e; }
        }, true); } finally { saveReloadGuard = null; saveReceiptEtag = null; saving.value = false; }
        if (receipt && result === undefined) { markPending('known_readback'); restoreOutstanding(); }
        return result !== undefined && !unknown.value && !uncertainSave.value && !uncertainControls.value.length && !previewUnknowns.value.length && !previewReleases.value.length;
    }
    async function reviewUncertainSave() {
        const pending = uncertainSave.value;
        if (!pending || checkingSave.value || busy.value) return false;
        checkingSave.value = true; saveReview.value = null; saveReviewError.value = null;
        try {
            const loaded = await ipc.getConfiguration(null, revisionOffset.value);
            if (uncertainSave.value !== pending) return false;
            saveReview.value = {configuration: loaded, matchesSubmitted: sameJson(loaded.workspace, pending.submitted), diffLocal: null};
            return true;
        } catch { saveReviewError.value = 'read'; return false; }
        finally { checkingSave.value = false; }
    }
    async function acceptReviewedSave() {
        const pending = uncertainSave.value, review = saveReview.value;
        if (!pending || !review || !saveCanResolve.value || checkingSave.value || busy.value) return false;
        if (editing.value || !sameJson(draft.value, pending.submitted) || !review.matchesSubmitted) { saveReviewError.value = 'local'; return false; }
        checkingSave.value = true; saveReviewError.value = null;
        try {
            // 确认时重读：核对与确认间其他编辑的 ETag 变化不能解除冻结。
            const current = await ipc.getConfiguration(null, revisionOffset.value);
            if (uncertainSave.value !== pending || saveReview.value !== review) return false;
            if (current.etag !== review.configuration.etag || !sameJson(current.workspace, review.configuration.workspace)) {
                saveReview.value = {configuration: current, matchesSubmitted: sameJson(current.workspace, pending.submitted), diffLocal: null};
                saveReviewError.value = 'changed'; return false;
            }
            if (editing.value || !sameJson(draft.value, pending.submitted)) { saveReviewError.value = 'local'; return false; }
            configuration.value = current;
            base.value = JSON.stringify(draft.value);
            clearUncertainSave();
            return true;
        } catch { saveReviewError.value = 'read'; return false; }
        finally { checkingSave.value = false; }
    }
    function noteSaveDifferences() { if (saveReview.value) saveReview.value = {...saveReview.value, diffLocal: JSON.stringify(draft.value)}; }
    async function reviewUncertainControls() {
        if (!uncertainControls.value.length || checkingControls.value || busy.value) return false;
        const pending = uncertainControls.value, generation = controlGeneration;
        checkingControls.value = true; controlReview.value = null; controlReviewError.value = null;
        try {
            const facts = controlFacts(await ipc.getSnapshot(null, 0, 50), pending);
            if (uncertainControls.value !== pending || controlGeneration !== generation) { controlReviewError.value = 'changed'; return false; }
            if (!facts) { controlReviewError.value = 'read'; return false; }
            controlReview.value = {facts, generation}; return true;
        } catch { controlReviewError.value = 'read'; return false; }
        finally { checkingControls.value = false; }
    }
    async function acceptReviewedControls() {
        const pending = uncertainControls.value, review = controlReview.value;
        if (!pending.length || !review || checkingControls.value || busy.value) return false;
        checkingControls.value = true; controlReviewError.value = null;
        try {
            const facts = controlFacts(await ipc.getSnapshot(null, 0, 50), pending);
            if (uncertainControls.value !== pending || controlGeneration !== review.generation || !facts || !sameJson(facts, review.facts)) {
                controlReview.value = null; controlReviewError.value = 'changed'; return false;
            }
            // 用户确认的是两次一致的当前事实，不推断未知操作过去的结果。
            uncertainControls.value = []; controlReview.value = null; lastSafetyFailure = lastSafetyFailure?.unknown ? null : lastSafetyFailure;
            restoreOutstanding(); return true;
        } catch { controlReviewError.value = 'read'; return false; }
        finally { checkingControls.value = false; }
    }
    let revisionRequest = 0;
    // 只更新版本事实，不覆盖尚未保存的编辑稿；迟到的旧列表不覆盖新结果。
    async function refreshRevisions(offset = revisionOffset.value) {
        const current = configuration.value, request = ++revisionRequest;
        if (!current) return;
        const loaded = await ipc.getConfiguration(null, offset);
        if (request !== revisionRequest || configuration.value !== current) return;
        Object.assign(current, { revisions: loaded.revisions, revisionTotal: loaded.revisionTotal, latestRevision: loaded.latestRevision, selections: loaded.selections, draftMatchesLatest: loaded.draftMatchesLatest });
        revisionOffset.value = offset;
    }
    async function pageRevisions(offset: number) { await action(() => refreshRevisions(offset)); }
    // 取消是幂等票据释放，离开页面时也可执行；不受其它操作busy门禁阻止，不撤销已提交操作。
    async function releasePreview(preview: ipc.Preview, related = false) {
        const item: PreviewRelease = {id: ++previewSequence, preview, related: related || !!(saving.value || uncertainSave.value || uncertainControls.value.length || previewUnknowns.value.length || closeGate.value), state: closeGate.value ? 'deferred' : 'inflight'};
        previewReleases.value = [...previewReleases.value, item];
        if (item.state === 'deferred') return;
        let released = false;
        try { await ipc.cancelPreview(preview); released = true; }
        catch (e) {
            const current = previewReleases.value.find(entry => entry.id === item.id);
            if (e instanceof ipc.IpcFailure && e.unknown && (current?.related || closeGate.value)) {
                previewUnknowns.value = [...previewUnknowns.value, {id: item.id, kind: preview.kind, code: e.code}]; restoreOutstanding();
            } else failure(e);
        } finally { previewReleases.value = previewReleases.value.filter(entry => entry.id !== item.id); }
        if (released) { try { await refreshRevisions(); } catch (e) { failure(e); } }
    }
    function beginClose() { closeGate.value = true; }
    function cancelClose() {
        closeGate.value = false;
        const deferred = previewReleases.value.filter(item => item.state === 'deferred');
        previewReleases.value = previewReleases.value.filter(item => item.state !== 'deferred');
        for (const item of deferred) void releasePreview(item.preview, item.related);
    }
    function closeFingerprint() { return JSON.stringify({draft: draft.value, editing: editing.value, busy: busy.value, saving: saving.value, unknown: unknown.value, error: error.value, save: uncertainSave.value, controls: uncertainControls.value, releases: previewReleases.value.map(({id, state, related}) => ({id, state, related})), previewUnknowns: previewUnknowns.value, outcome: saveOutcome.value, failure: saveFailure.value}); }
    function newInstance() { if (!draft.value || draft.value.instances.length >= 8)
        return; const i: ipc.Instance = { id: crypto.randomUUID(), name: '', host: '127.0.0.1', port: 30102, rack: 0, slot: 1, callingTsap: 256, maxConnections: 16, maxHandshakes: 4, policy: {}, dbs: [], namesConfirmation: null }; return i; }
    async function control(row: ipc.RuntimeInstance, command: string, discardValues = false) {
        const safety: Omit<ControlUnknown, 'id' | 'code'> | undefined = command === 'stop' || command === 'pause' ? {instanceId: row.instanceId, command, epoch: row.epoch, loadedRevision: row.loadedRevision} : undefined;
        if (safety && (uncertainSave.value || uncertainControls.value.length || previewUnknowns.value.length)) { controlGeneration++; controlReview.value = null; }
        return action(() => ipc.controlInstance({ instanceId: row.instanceId, command, expectedLoadedRevision: row.loadedRevision, epoch: row.epoch, discardValues }), false, safety);
    }
    async function loadLogs(offset = 0, event: string | null = null) {
        const result = await action(() => ipc.queryLogs(offset, 50, event)); if (result)
        logs.value = result; }
    return { lastSavedRevision, revisionOffset, pageRevisions, refreshRevisions, releasePreview, previewReleases, previewUnknowns, saving, saveOutcome, saveFailure, closeGate, beginClose, cancelClose, closeFingerprint, editing, finishEditor, discardEditor, busy, refreshing, error, unknown, conflictEtag, bootstrap, configuration, draft, snapshot, instanceId, dbId, valueOffset, valueLimit, logs, dirty, selected, selectedDb, runtime, available: ipc.desktopAvailable, uncertainSave, saveCanResolve, saveReview, checkingSave, saveReviewError, reviewUncertainSave, acceptReviewedSave, noteSaveDifferences, uncertainControls, controlReview, checkingControls, controlReviewError, reviewUncertainControls, acceptReviewedControls, reload, refresh, action, save, commitCatalogImport, newInstance, control, loadLogs };
}
export type SimulatorConsole = UnwrapNestedRefs<ReturnType<typeof useDeviceSimulator>>;
export const simulatorKey: InjectionKey<SimulatorConsole> = Symbol('DS console');
