/** 唯一宿主状态owner：编辑副本与快照分开，显式保存/应用；可见时每秒最多一次快照。 */
import { ref, computed, type InjectionKey, type UnwrapNestedRefs } from 'vue';
import * as ipc from '../../services/deviceSimulator';
export function useDeviceSimulator() {
    const editing = ref(false), finishEditor = ref<null | (() => boolean)>(null), discardEditor = ref<null | (() => void)>(null);
    const busy = ref(false), refreshing = ref(false), error = ref<string | null>(null), unknown = ref(false), conflictEtag = ref<string | null>(null);
    const bootstrap = ref<ipc.Bootstrap | null>(null), configuration = ref<ipc.Configuration | null>(null), draft = ref<ipc.Workspace | null>(null), base = ref(''), snapshot = ref<ipc.RuntimeSnapshot | null>(null);
    const instanceId = ref(''), dbId = ref(''), valueOffset = ref(0), valueLimit = ref(50), logs = ref<Awaited<ReturnType<typeof ipc.queryLogs>> | null>(null);
    const dirty = computed(() => !!draft.value && JSON.stringify(draft.value) !== base.value);
    const selected = computed(() => draft.value?.instances.find(i => i.id === instanceId.value) || null);
    const selectedDb = computed(() => selected.value?.dbs.find(d => d.id === dbId.value) || null);
    const runtime = computed(() => snapshot.value?.instances.find(i => i.instanceId === instanceId.value) || null);
    function failure(e: unknown) { const f = e instanceof ipc.IpcFailure ? e : new ipc.IpcFailure('operation_failed'); error.value = f.code; unknown.value = f.unknown; conflictEtag.value = f.currentEtag; }
    async function reload() { const loaded = await ipc.getConfiguration(); configuration.value = loaded; draft.value = structuredClone(loaded.workspace); base.value = JSON.stringify(loaded.workspace); if (!loaded.workspace.instances.some(i => i.id === instanceId.value))
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
        failure(e);
        if (snapshot.value)
            snapshot.value.stale = true;
    }
    finally {
        refreshing.value = false;
    } }
    async function action<T>(work: () => Promise<T>, reloadAfter = false): Promise<T | undefined> { if (busy.value)
        return; busy.value = true; error.value = null; unknown.value = false; try {
        const result = await work();
        if (reloadAfter)
            await reload();
        await refresh();
        return result;
    }
    catch (e) {
        failure(e);
        return undefined;
    }
    finally {
        busy.value = false;
    } }
    async function save(confirmPoints: string[] = []) { if (!draft.value || !configuration.value)
        return false; const result = await action(() => ipc.saveConfiguration(configuration.value!.etag, JSON.parse(JSON.stringify(draft.value)), confirmPoints), true); return result !== undefined; }
    function newInstance() { if (!draft.value || draft.value.instances.length >= 8)
        return; const i: ipc.Instance = { id: crypto.randomUUID(), name: '', host: '127.0.0.1', port: 30102, rack: 0, slot: 1, callingTsap: 256, maxConnections: 16, maxHandshakes: 4, policy: {}, dbs: [], namesConfirmation: null }; return i; }
    async function control(row: ipc.RuntimeInstance, command: string, discardValues = false) { return action(() => ipc.controlInstance({ instanceId: row.instanceId, command, expectedLoadedRevision: row.loadedRevision, epoch: row.epoch, discardValues })); }
    async function loadLogs(offset = 0, event: string | null = null) { const result = await action(() => ipc.queryLogs(offset, 50, event)); if (result)
        logs.value = result; }
    return { editing, finishEditor, discardEditor, busy, refreshing, error, unknown, conflictEtag, bootstrap, configuration, draft, snapshot, instanceId, dbId, valueOffset, valueLimit, logs, dirty, selected, selectedDb, runtime, available: ipc.desktopAvailable, reload, refresh, action, save, newInstance, control, loadLogs };
}
export type SimulatorConsole = UnwrapNestedRefs<ReturnType<typeof useDeviceSimulator>>;
export const simulatorKey: InjectionKey<SimulatorConsole> = Symbol('DS console');
