/** 本地模式唯一页面owner：草稿/CAS/激活/动作与1Hz轮询；切页仅改本地视图状态。 */
import { computed, watch, onMounted, onUnmounted, reactive, ref, type InjectionKey } from 'vue';
import { ElMessageBox } from 'element-plus';
import { useI18n } from 'vue-i18n';
import { bootstrap, localCall, LocalCommandError, type Configuration, type ConfigurationView, type Snapshot, type ImportPreview, type Source, type Offset, type Point, type History, type RawSample, type LogRow, type MigrationSummary, type Identification, type BlockMapping, type NameRequest, type NamePreview, previewPointNames, confirmPointNames } from '../../services/localAcquisition';
export const localConsoleKey: InjectionKey<LocalConsole> = Symbol('daa-local-owner');
export type LocalConsole = ReturnType<typeof useLocalAcquisitionConsole>;
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;
export function useLocalAcquisitionConsole() {
    const { t, te } = useI18n();
    const available = bootstrap.localStorage && ['native', 'fixture'].includes(bootstrap.origin);
    const migration = ref<MigrationSummary | null>(null);
    const view = ref<ConfigurationView | null>(null), draft = ref<Configuration | null>(null), snapshot = ref<Snapshot | null>(null), busy = ref(false), error = ref(''), notice = ref(''), selectedPlc = ref(''), selectedDb = ref(''), query = ref(''), pointPage = ref(1), preview = ref<ImportPreview | null>(null), offsets = ref<Offset[]>([]), sources = ref<Source[]>([]), history = ref<History | null>(null), raw = ref<RawSample | null>(null), logs = ref<LogRow[]>([]);
    const conflictVersion = ref(''), snapshotError = ref('');
    const identification = ref<Identification | null>(null), mappings = ref<BlockMapping[]>([]), importPage = ref(1), importPageSize = ref(10);
    const sourcePreviewOpen = ref(false), offsetPreviewOpen = ref(false), sourceStructureOpen = ref(false);
    const rawProofs = ref<Array<{ sha256: string; bytes: number }>>([]);
    const importRows = computed(() => (identification.value?.blocks ?? []).filter(b => b.blockKey.kind === 'DATA_BLOCK').map(b => ({ block: b, mapping: mappings.value.find(m => m.sourceIndex === b.sourceIndex && m.blockKey.name === b.blockKey.name)! })));
    const pagedImportRows = computed(() => importRows.value.slice((importPage.value - 1) * importPageSize.value, importPage.value * importPageSize.value));

    const selectedNameIds = ref<string[]>([]), namePreview = ref<NamePreview | null>(null), namePreviewOpen = ref(false), namePreviewBusy = ref(false), namePage = ref(1), namePageSize = ref(10), pointPageSize = ref(20);
    let nameInput: NameRequest | null = null, nameEpoch = 0;
    let nameTimer: ReturnType<typeof setTimeout> | undefined;
    const pagedNames = computed(() => namePreview.value?.rows.slice((namePage.value - 1) * namePageSize.value, namePage.value * namePageSize.value) ?? []);
    function invalidateNames() { nameEpoch++; namePreview.value = null; nameInput = null; namePreviewBusy.value = false; if (nameTimer) clearTimeout(nameTimer); }
    function closeNames() { namePreviewOpen.value = false; invalidateNames(); }
    function toggleNamePoint(id: string, selected: boolean) { invalidateNames(); selectedNameIds.value = selected ? [...new Set([...selectedNameIds.value, id])] : selectedNameIds.value.filter(p => p !== id); }
    async function previewNames() {
        await perform(async () => {
            invalidateNames(); if (!view.value || dirty.value || editing.value) throw new Error('unsaved_changes');
            const input: NameRequest = { expectedEtag: view.value.etag, plcId: selectedPlc.value, pointIds: [...selectedNameIds.value], intent: 'generate', patch: null };
            const result = await previewPointNames(input); nameInput = input; namePreview.value = result; namePage.value = 1; namePreviewOpen.value = true;
        });
    }
    function stagePointEdit(point: Point | null) {
        invalidateNames(); if (!point || !view.value || !available) return;
        const epoch = nameEpoch;
        const input: NameRequest = { expectedEtag: view.value.etag, plcId: point.plcId, pointIds: [point.id], intent: 'edit', patch: { name: point.name, comment: point.comment, enabled: point.enabled, groupId: point.groupId, address: clone(point.address) } };
        namePreviewBusy.value = true;
        nameTimer = setTimeout(async () => {
            try { const result = await previewPointNames(input); if (epoch === nameEpoch) { nameInput = input; namePreview.value = result; } }
            catch (e) { if (epoch === nameEpoch) error.value = String(e instanceof Error ? e.message : e); }
            finally { if (epoch === nameEpoch) namePreviewBusy.value = false; }
        }, 180);
    }
    async function confirmNames() {
        let saved = false;
        const input = nameInput, preview = namePreview.value;
        if (!input || !preview?.canConfirm || namePreviewBusy.value) return false;
        await perform(async () => {
            const result = await confirmPointNames(input, preview);
            invalidateNames(); namePreviewOpen.value = false; accept(result); notice.value = 'saved'; saved = true;
        });
        return saved;
    }
    const editing = ref(false);
    const selectedTargets = ref<string[]>([]);
    const historyFilter = reactive({ plcId: '', groupId: '', from: '', to: '', quality: '' });
    const historyPageSize = ref(20), historyPage = ref(1), historyCursors = ref<Array<number | null>>([null]), rawSampleId = ref('');
    let appliedHistoryFilter = { ...historyFilter };
    const historyPreviousAvailable = computed(() => !!history.value && historyCursors.value.length > 1);
    const historyNextAvailable = computed(() => !!history.value && history.value.items.length === historyPageSize.value && history.value.nextCursor !== null);
    const historyPreviousBounded = computed(() => !!history.value && historyPage.value > 1 && historyCursors.value.length === 1);
    let timer: ReturnType<typeof setInterval> | undefined;
    const label = (code: string | null | undefined) => {
        if (!code)
            return '—';
        const key = 'common.local.codes.' + code.split(':')[0];
        return te(key) ? t(key) : t('common.local.code', { code });
    };
    const plcs = computed(() => draft.value?.plcs ?? []), dbs = computed(() => draft.value?.dbs.filter(d => !selectedPlc.value || d.plcId === selectedPlc.value) ?? []), groups = computed(() => draft.value?.groups.filter(g => g.plcId === selectedPlc.value) ?? []);
    const points = computed(() => draft.value?.points.filter(p => (!selectedPlc.value || p.plcId === selectedPlc.value) && (!selectedDb.value || p.dbId === selectedDb.value) && [p.sourcePath, p.name, p.dataType, p.comment].some(v => v.toLowerCase().includes(query.value.toLowerCase()))) ?? []);
    const dirty = computed(() => !!draft.value && !!view.value && JSON.stringify(draft.value) !== JSON.stringify(view.value.draft));
    async function confirmAction(key: string, params: Record<string, string | number> = {}) {
        try {
            await ElMessageBox.confirm(t(key, params), t('common.operationDialog.title'), { confirmButtonText: t('common.operationDialog.confirm'), cancelButtonText: t('common.operationDialog.cancel'), appendTo: document.querySelector('#daa-feedback') as HTMLElement, closeOnClickModal: false });
            return true;
        } catch { return false; }
    }
    const pagedPoints = computed(() => points.value.slice((pointPage.value - 1) * pointPageSize.value, pointPage.value * pointPageSize.value));
    async function perform(fn: () => Promise<void>) {
        if (!available) { error.value = 'desktop_preview'; return; }
        if (busy.value)
            return;
        busy.value = true;
        error.value = '';
        conflictVersion.value = '';
        notice.value = '';
        try {
            await fn();
        }
        catch (e) {
            error.value = String(e instanceof Error ? e.message : e);
            if (e instanceof LocalCommandError)
                conflictVersion.value = e.currentEtag ?? '';
        }
        finally {
            busy.value = false;
        }
    }
    function accept(v: ConfigurationView) {
        invalidateNames();
        view.value = v;
        draft.value = clone(v.draft);
        if (!plcs.value.some(p => p.id === selectedPlc.value))
            selectedPlc.value = plcs.value[0]?.id ?? '';
        if (!dbs.value.some(d => d.id === selectedDb.value))
            selectedDb.value = dbs.value[0]?.id ?? '';
    }
    async function refresh() {
        if (!available || busy.value)
            return;
        try {
            snapshot.value = await localCall<Snapshot>('daa_get_local_snapshot');
            snapshotError.value = '';
            if (!draft.value)
                accept(snapshot.value.configuration);
        }
        catch (e) {
            snapshotError.value = String(e instanceof Error ? e.message : e);
        }
    }
    async function refreshMigration() {
        migration.value = null;
        migration.value = await localCall<MigrationSummary>('daa_get_yaml_migration');
    }
    async function reload() { invalidateNames(); await perform(async () => { accept(await localCall<ConfigurationView>('daa_get_configuration')); await refreshMigration(); preview.value = null; offsets.value = []; }); }
    async function retryMigration() {
        if (!view.value || !migration.value?.attemptId || dirty.value || editing.value) { error.value = 'yaml_unsaved_edits'; return; }
        const expectedEtag = view.value.etag, expectedAttemptId = migration.value.attemptId;
        await perform(async () => {
            const result = await localCall<MigrationSummary>('daa_retry_yaml_migration', { expectedEtag, expectedAttemptId });
            migration.value = result;
            if (result.statusPersistence === 'persisted') accept(await localCall<ConfigurationView>('daa_get_configuration'));
        });
    }
    // Candidate stays detached until Rust/CAS returns a committed configuration.
    async function saveCandidate(candidate: Configuration) {
        invalidateNames();
        let saved = false;
        await perform(async () => {
            if (!view.value) return;
            const result = await localCall<ConfigurationView>('daa_save_draft', { draft: clone(candidate), expectedEtag: view.value.etag });
            accept(result);
            preview.value = null;
            offsets.value = [];
            notice.value = 'saved';
            saved = true;
            try { await refreshMigration(); }
            catch { error.value = 'yaml_summary_after_save_unavailable'; }
        });
        return saved;
    }
    async function save() { if (draft.value) return saveCandidate(draft.value); return false; }
    async function activate(rollback = false) {
        await perform(async () => {
            if (!view.value)
                return;
            await localCall('daa_activate_configuration', { expectedEtag: view.value.etag, expectedActiveRevision: view.value.active, rollback });
            accept(await localCall<ConfigurationView>('daa_get_configuration'));
            notice.value = 'applied';
        });
        await refresh();
    }
    function addPlc() {
        if (!draft.value || plcs.value.length >= 4)
            return;
        const id = crypto.randomUUID();
        draft.value.plcs.push({ id, name: t('common.local.newPlc'), enabled: false, host: '', port: 102, rack: 0, slot: 1, connectTimeoutMs: 1000, ioTimeoutMs: 500, deadlineMs: 5000 });
        selectedPlc.value = id;
        selectedDb.value = '';
    }
    function removePlc(id: string) {
        if (!draft.value)
            return;
        draft.value.plcs = draft.value.plcs.filter(p => p.id !== id);
        draft.value.dbs = draft.value.dbs.filter(p => p.plcId !== id);
        draft.value.points = draft.value.points.filter(p => p.plcId !== id);
        draft.value.groups = draft.value.groups.filter(p => p.plcId !== id);
        draft.value.sources = draft.value.sources.filter(p => p.plcId !== id);
    }
    function addGroup() {
        if (!draft.value || !selectedPlc.value || groups.value.length >= 8)
            return;
        draft.value.groups.push({ id: crypto.randomUUID(), plcId: selectedPlc.value, name: t('common.local.newGroup'), enabled: false, intervalMs: 1000 });
    }
    function removeGroup(id: string) {
        if (!draft.value)
            return;
        draft.value.groups = draft.value.groups.filter(g => g.id !== id);
        for (const p of draft.value.points)
            if (p.groupId === id) {
                p.groupId = null;
                p.enabled = false;
            }
    }
    async function control(command: 'daa_set_connection' | 'daa_set_collection' | 'daa_test_connection' | 'daa_diagnose_point', ids: string[], desired = false, pointId?: string) {
        await perform(async () => {
            if (!view.value?.active)
                throw new Error('active_missing');
            const request = command === 'daa_test_connection' || command === 'daa_diagnose_point' ? { plcId: ids[0], pointId: pointId ?? null, expectedActiveRevision: view.value.active } : { plcIds: ids, desired, expectedActiveRevision: view.value.active };
            await localCall(command, request);
            notice.value = 'pending';
        });
        await refresh();
    }
    function invalidateImport() { preview.value = null; invalidateNames(); }
    function changeImportTarget(mapping: BlockMapping) {
        const db = dbs.value.find(d => d.id === mapping.targetId);
        if (db) mapping.dbNumber = db.number;
        invalidateImport();
    }
    async function readFiles(event: Event) {
        const input = event.target as HTMLInputElement, files = Array.from(input.files ?? []);
        if (!files.length) return; // Picker cancel preserves the previous input and saved configuration.
        await perform(async () => {
            if (dirty.value || editing.value) throw new Error('unsaved_changes');
            if (!selectedPlc.value || !view.value) throw new Error('plc_missing');
            if (files.some(f => f.size > 1048576) || files.reduce((n, f) => n + f.size, 0) > 4194304) throw new Error('source_limits');
            const chosen = await Promise.all(files.map(async f => {
                const bytes = await f.arrayBuffer();
                let content: string;
                try { content = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(bytes); }
                catch { throw new Error('source_utf8'); }
                const hash = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)), n => n.toString(16).padStart(2, '0')).join('');
                return { source: { id: '', name: f.name, content, sha256: hash, plcId: selectedPlc.value, dbNumber: null, diagnostics: [] } as Source, proof: { sha256: hash, bytes: bytes.byteLength } };
            }));
            preview.value = null; offsets.value = [];
            const nextSources = chosen.map(v => v.source), nextProofs = chosen.map(v => v.proof);
            const identified = await localCall<Identification>('daa_import_sources', { sources: nextSources, rawProofs: nextProofs, expectedEtag: view.value.etag, confirm: false, stage: 'identify', targetPlcId: selectedPlc.value });
            sources.value = nextSources; rawProofs.value = nextProofs; identification.value = identified;
            mappings.value = identified.blocks.filter(b => b.blockKey.kind === 'DATA_BLOCK').map(b => ({ sourceIndex: b.sourceIndex, blockKey: b.blockKey, selected: true, dbNumber: b.suggestedDbNumber, targetId: b.targetId }));
            importPage.value = 1;
        });
        input.value = '';
    }
    async function importSources(confirm = false) {
        await perform(async () => {
            if (dirty.value || editing.value) throw new Error('unsaved_changes');
            if (!view.value) return;
            if (confirm && !preview.value?.canConfirm) throw new Error('source_import_blocked');
            const result = await localCall<ImportPreview>('daa_import_sources', { sources: sources.value, rawProofs: rawProofs.value, mappings: mappings.value, targetPlcId: selectedPlc.value, expectedEtag: view.value.etag, confirm, stage: confirm ? 'confirm' : 'preview', previewToken: confirm ? preview.value?.previewToken : null });
            if (confirm) {
                notice.value = result.unchanged ? 'unchanged' : 'saved';
                preview.value = null; sourcePreviewOpen.value = false;
                try { accept(await localCall<ConfigurationView>('daa_get_configuration')); }
                catch { error.value = 'import_saved_reload_failed'; }
            } else { preview.value = result; sourcePreviewOpen.value = true; }
        });
    }
    async function infer(confirm = false) {
        invalidateNames();
        await perform(async () => {
            if (dirty.value || editing.value) throw new Error('unsaved_changes');
            if (!view.value || !selectedDb.value) return;
            if (confirm) {
                accept(await localCall<ConfigurationView>('daa_confirm_offsets', { dbId: selectedDb.value, pointIds: offsets.value.filter(o => !o.protectedManual).map(o => o.pointId), expectedEtag: view.value.etag, layoutDigest: offsets.value[0]?.layoutDigest }));
                offsets.value = []; offsetPreviewOpen.value = false;
            } else { offsets.value = await localCall<Offset[]>('daa_preview_offsets', { dbId: selectedDb.value, expectedEtag: view.value.etag }); offsetPreviewOpen.value = true; }
        });
    }
    watch(pointPageSize, () => { pointPage.value = 1; });
    watch(selectedPlc, () => { selectedNameIds.value = []; invalidateNames(); });
    watch(() => view.value?.etag, invalidateNames);
    watch(dirty, () => { if (!editing.value) invalidateNames(); });
    watch([sources, mappings, selectedPlc], invalidateImport, { deep: true });
    watch([dirty, editing, () => view.value?.etag, selectedDb], () => { preview.value = null; offsets.value = []; });
    function address(p: Point) {
        if (!p.address)
            p.address = { offset: 0, bit: p.dataType === 'BOOL' ? 0 : null, confirmed: false, origin: 'manual', reason: '' };
        return p.address;
    }
    function manual(p: Point) { address(p).origin = 'manual'; address(p).confirmed = false; }
    function bulk(groupId: string | null, enabled: boolean) {
        for (const p of points.value) {
            p.groupId = groupId;
            p.enabled = enabled;
        }
    }
    // Keep at most 64 cursor positions, never a growing cache of sample pages or a fabricated total.
    async function loadHistory(direction: boolean | 'previous' = false, pageSize = historyPageSize.value) {
        await perform(async () => {
            if (![10, 20, 50].includes(pageSize)) throw new Error('query_limits');
            if (direction === true && !historyNextAvailable.value || direction === 'previous' && !historyPreviousAvailable.value) return;
            const candidate = direction === false ? { ...historyFilter } : { ...appliedHistoryFilter };
            const from = candidate.from ? Date.parse(candidate.from) : null, to = candidate.to ? Date.parse(candidate.to) : null;
            if (from !== null && !Number.isFinite(from) || to !== null && !Number.isFinite(to)) throw new Error('query_limits');
            if (from !== null && to !== null && from > to) throw new Error('history_time_range');
            const cursors = direction === false ? [null] : [...historyCursors.value];
            let page = direction === false ? 1 : historyPage.value;
            if (direction === true) { cursors.push(history.value!.nextCursor); page++; if (cursors.length > 64) cursors.shift(); }
            if (direction === 'previous') { cursors.pop(); page--; }
            const filter = Object.fromEntries(Object.entries(candidate).map(([k, v]) => [k, v || null]));
            const result = await localCall<History>('daa_list_history', { ...filter, cursor: cursors[cursors.length - 1], limit: pageSize });
            history.value = result;
            historyPage.value = page;
            historyPageSize.value = pageSize;
            historyCursors.value = cursors;
            appliedHistoryFilter = candidate;
        });
    }
    async function inspect(sampleId: string) {
        let inspected = false;
        await perform(async () => {
            const item = await localCall<RawSample>('daa_get_sample', { sampleId });
            if (JSON.parse(item.payload).sampleId !== sampleId) throw new Error('payload_corrupt');
            let next = item.contextNextOffset;
            let chunks = 0;
            while (next !== null) {
                if (++chunks > 256)
                    throw new Error('query_limits');
                const page = await localCall<RawSample>('daa_get_sample', { sampleId, contextOffset: next });
                if (page.sha256 !== item.sha256 || page.contextSha256 !== item.contextSha256 || page.contextOffset !== next)
                    throw new Error('payload_corrupt');
                item.context += page.context;
                next = page.contextNextOffset;
            }
            item.contextNextOffset = null;
            raw.value = item;
            rawSampleId.value = sampleId;
            inspected = true;
        });
        return inspected;
    }
    async function loadLogs(reset = false) {
        await perform(async () => {
            const r = await localCall<{
                items: LogRow[];
            }>('daa_get_logs', { cursor: reset ? 0 : logs.value[logs.value.length - 1]?.cursor ?? 0, limit: 100 });
            logs.value = [...(reset ? [] : logs.value), ...r.items].slice(-200);
        });
    }
    const state = (id: string) => snapshot.value?.plcs.find(p => p.plcId === id);
    const formatBytes = (n: number | undefined) => n === undefined ? '—' : (n / 1048576).toFixed(2) + ' MiB';
    onMounted(() => {
        if (available) {
            void reload().then(refresh);
            timer = setInterval(() => { void refresh(); }, 1000);
        }
    });
    onUnmounted(() => {
        if (timer)
            clearInterval(timer);
        if (nameTimer) clearTimeout(nameTimer);
    });
    return reactive({ selectedNameIds, namePreview, namePreviewOpen, namePreviewBusy, namePage, namePageSize, pagedNames, pointPageSize, closeNames, invalidateNames, toggleNamePoint, previewNames, stagePointEdit, confirmNames, sourcePreviewOpen, offsetPreviewOpen, sourceStructureOpen, identification, mappings, importPage, importPageSize, importRows, pagedImportRows, invalidateImport, changeImportTarget, available, migration, retryMigration, editing, dirty, confirmAction, conflictVersion, snapshotError, selectedTargets, bootstrap, view, draft, snapshot, busy, error, notice, selectedPlc, selectedDb, query, pointPage, preview, offsets, sources, history, historyFilter, historyPage, historyPageSize, historyPreviousAvailable, historyNextAvailable, historyPreviousBounded, raw, rawSampleId, logs, label, plcs, dbs, groups, points, pagedPoints, perform, refresh, reload, save, saveCandidate, activate, addPlc, removePlc, addGroup, removeGroup, control, readFiles, importSources, infer, address, manual, bulk, loadHistory, inspect, loadLogs, state, formatBytes });
}
