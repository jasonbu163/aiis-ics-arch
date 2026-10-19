/** 本地IPC v1合同与bootstrap；浏览器无桥仅桌面预览，不创建假本地保存桥。 */
import { invoke, isTauri } from '@tauri-apps/api/core';
export interface Bootstrap {
    schemaVersion: number;
    mode: 'local_sqlite';
    version?: string;
    identity?: string;
    ignoredKeys: string[];
    origin: string;
    localStorage: boolean;
    readAllowed: boolean;
    uploadAvailable: false;
}
export let bootstrap: Bootstrap = { schemaVersion: 1, mode: 'local_sqlite', origin: 'browser', localStorage: false, readAllowed: false, uploadAvailable: false, ignoredKeys: [] };
export let bootstrapError = '';
export async function initializeBootstrap() {
    if (!isTauri()) return;
    try { bootstrap = await invoke<Bootstrap>('daa_get_bootstrap'); }
    catch { bootstrapError = 'bootstrap_failed'; bootstrap.origin = 'bootstrap_error'; }
}
export interface MigrationSummary {
    status: string; statusPersistence: string; attemptId: string | null; committedEtag: string | null;
    committedAt: string | null; counts: { plcs: number; dbs: number; groups: number; points: number; policyPlcs: number; policyGroups: number; policyPoints: number };
    sources: Array<{ kind: string; path: string; origin: string; bytes: number | null; sha256: string | null; hashUnavailable: string | null }>;
    diagnostics: Issue[]; diagnosticTotal: number; diagnosticOmitted: number; errorCode: string | null; retryAllowed: boolean;
}
export interface Plc {
    id: string;
    name: string;
    enabled: boolean;
    host: string;
    port: number;
    rack: number;
    slot: number;
    connectTimeoutMs: number;
    ioTimeoutMs: number;
    deadlineMs: number;
}
export interface Address {
    offset: number;
    bit: number | null;
    confirmed: boolean;
    origin: string;
    reason: string;
}
export interface Point {
    id: string;
    plcId: string;
    dbId: string;
    sourcePath: string;
    name: string;
    dataType: string;
    comment: string;
    enabled: boolean;
    groupId: string | null;
    address: Address | null;
}
export interface Group {
    id: string;
    plcId: string;
    name: string;
    enabled: boolean;
    intervalMs: number;
}
export interface Field {
    name: string;
    path: string;
    dataType: string;
    line: number;
    comment: string;
    lower: number | null;
    upper: number | null;
    children: Field[];
}
export interface Db {
    id: string;
    plcId: string;
    sourceId: string;
    name: string;
    number: number;
    length: number;
    complete: boolean;
    flat: boolean;
    tree: Field[];
    importBinding?: { blockKey: BlockKey; lineageId: string; udtSourceIds: string[] };
}
export interface Issue {
    code: string;
    file: string;
    line: number;
    path: string;
}
export interface Source {
    id: string;
    name: string;
    content: string;
    sha256: string;
    plcId: string;
    dbNumber: number | null;
    lineageId?: string;
    diagnostics: Issue[];
}
export interface Configuration {
    schemaVersion: 1;
    plcs: Plc[];
    dbs: Db[];
    points: Point[];
    groups: Group[];
    sources: Source[];
    storage: {
        quotaBytes: number;
        retentionDays: number;
    };
}
export interface ConfigurationView {
    schemaVersion: 1;
    draft: Configuration;
    etag: string;
    active: string | null;
    previous: string | null;
    loaded: string | null;
    used: string | null;
    phase: string;
    issues: Issue[];
}
export interface Operation {
    operationId: string;
    plcId: string;
    action: string;
    phase: string;
    reason: string | null;
    result: unknown;
}
export interface PlcState {
    plcId: string;
    desiredConnection: boolean;
    desiredCollection: boolean;
    connected: boolean;
    phase: string;
    admission: string;
    error: string | null;
    savedCycles: number;
    usedRevision: string | null;
    groups: {
        groupId: string;
        intervalMs: number;
        durationMs: number;
        missedTicks: number;
    }[];
}
export interface Capacity {
    mainBytes: number;
    journalBytes: number;
    configBytes: number;
    configJournalBytes: number;
    logBytes: number;
    freeBytes: number;
    quotaBytes: number;
    reservedBytes: number;
    pageCount: number;
    freelistCount: number;
    pendingCount: number;
    pendingBytes: number;
    oldestPending: string | null;
    state: string;
    admission: boolean;
    busyCount: number;
}
export interface Snapshot {
    schemaVersion: 1;
    mode: string;
    origin: string;
    generatedAt: string;
    configuration: ConfigurationView;
    plcs: PlcState[];
    operations: Operation[];
    capacity: Capacity;
}
export interface HistoryRow {
    order: number;
    sampleId: string;
    cycleId: string;
    plcId: string;
    groupId: string;
    sourceSeq: string;
    revision: string;
    quality: string;
    savedAt: string;
    dbNumber: number;
    sha256: string;
}
export interface History {
    schemaVersion: 1;
    items: HistoryRow[];
    nextCursor: number | null;
}
export interface RawSample {
    payload: string;
    sha256: string;
    manifest: string;
    manifestSha256: string;
    context: string;
    contextOffset: number;
    contextNextOffset: number | null;
    contextBytes: number;
    contextSha256: string;
    deliveryState: string;
}
export interface LogRow {
    cursor: number;
    event: string;
    resource: string;
    result: string;
    createdAt: string;
}
export interface BlockKey { kind: 'DATA_BLOCK' | 'TYPE'; name: string; }
export interface BlockMapping { sourceIndex: number; blockKey: BlockKey; selected: boolean; dbNumber: number | null; targetId: string | null; }
export interface IdentifiedBlock { sourceIndex: number; blockKey: BlockKey; file: string; line: number; leafCount: number; issues: Issue[]; suggestedDbNumber: number | null; targetId: string | null; }
export interface Identification { blocks: IdentifiedBlock[]; fileCount: number; dbCount: number; udtCount: number; }
export interface DbDelta { dbId: string; blockName: string; number: number; status: string; addedPaths: string[]; typeChangedPaths: string[]; removedPaths: string[]; layoutChanged: boolean; commentsChanged: boolean; preservedPoints: number; preservedManual: number; invalidatedConfirmations: number; isolatedUdtVersions: boolean; }
export interface ImportPreview {
    configuration: Configuration;
    changes: string[];
    readiness: Issue[]; deltas: DbDelta[]; canConfirm: boolean; unchanged: boolean; previewToken: string | null; inputDigest: string; etag: string;
    issues: Issue[];
}
export interface Offset {
    pointId: string;
    old: Address | null;
    proposed: Address;
    protectedManual: boolean;
    manualConflict: boolean; profile: string; layoutDigest: string;
    dbLength: number;
}
export class LocalCommandError extends Error {
    currentEtag?: string;
    currentActiveRevision?: string | null;
}
export function localCall<T>(command: string, request: unknown = {}): Promise<T> {
    if (!isTauri() || !bootstrap.localStorage)
        return Promise.reject(new Error('desktop_preview'));
    return invoke<T>(command, { request }).catch((reason: unknown) => { const body = typeof reason === 'object' && reason !== null ? reason as {
        errorCode?: string;
        currentEtag?: string;
        currentActiveRevision?: string | null;
    } : null; const error = new LocalCommandError(body?.errorCode ?? String(reason)); error.currentEtag = body?.currentEtag; error.currentActiveRevision = body?.currentActiveRevision; throw error; });
}
