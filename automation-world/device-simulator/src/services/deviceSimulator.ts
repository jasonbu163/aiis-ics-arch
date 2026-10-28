/** 正常16项IPC facade及严格字段类型；browser不可用时不返回mock成功。 */
import { invoke, isTauri } from '@tauri-apps/api/core';
export type Scalar = null | boolean | number | string;
// 来源树/诊断为服务所有的opaque JSON，不在前端递归重建业务模型。
export type Json = Scalar | unknown[] | Record<string, unknown>;
export interface Rule {
    kind: 'fixed' | 'ramp' | 'sine' | 'random' | 'toggle';
    fixedValue: Json;
    min: number;
    max: number;
    periodMs: number;
    phase: number;
    seed: string;
    halfPeriodMs: number;
}
export interface Policy {
    mode?: 'hold' | 'fixed' | 'ramp' | 'sine' | 'random' | 'toggle' | null;
    owner?: 'none' | 'client' | 'ui' | 'rule' | null;
    clientRead?: boolean | null;
    clientWrite?: boolean | null;
    uiWrite?: boolean | null;
    uiMaintenance?: boolean | null;
    initial?: Json;
    rule?: Rule | null;
}
export interface Segment {
    kind: 'field' | 'index';
    value: string | number;
}
export interface Point {
    id: string;
    name: string;
    displayName: string;
    dataType: string;
    enabled: boolean;
    sourcePath: string;
    segments: Segment[];
    byte: number | null;
    bit: number | null;
    manualReason: string;
    manual: boolean;
    policy: Policy;
    confirmations: {
        initial: string | null;
        policy: string | null;
    };
}
export interface Region {
    id: string;
    firstBit: number;
    bitLength: number;
    policy: Policy;
}
export interface Db {
    id: string;
    name: string;
    number: number;
    length: number;
    enabled: boolean;
    manual: boolean;
    binding: Json;
    points: Point[];
    policy: Policy;
    regions: Region[];
    addressConfirmation: {
        structureSha256: string;
        layoutSha256: string;
        method: string;
        reason: string;
    } | null;
}
export interface Instance {
    id: string;
    name: string;
    host: string;
    port: number;
    rack: number;
    slot: number;
    callingTsap: number;
    maxConnections: number;
    maxHandshakes: number;
    policy: Policy;
    dbs: Db[];
    namesConfirmation: string | null;
}
export interface SourceVersion {
    versionId: string;
    lineageId: string;
    blobSha256: string;
    logicalName: string;
    importProfile: string;
    bytes: number[];
}
export interface Workspace {
    schemaVersion: 1;
    instances: Instance[];
    sourceVersions: SourceVersion[];
}
export interface Revision {
    revisionId: string;
    savedSeq: string;
    sha256: string;
    createdUtc: string;
}
export interface Issue {
    code: string;
    instanceId: string;
    dbId: string | null;
    pointId: string | null;
}
export interface Configuration {
    etag: string;
    workspace: Workspace;
    latestRevision: string | null;
    revisions: Revision[];
    selections: {
        instanceId: string;
        revisionId: string;
        selectionEtag: string;
    }[];
    issues: Issue[];
}
export interface RuntimeInstance {
    instanceId: string;
    name: string;
    endpoint: string;
    state: string;
    c: number;
    h: number;
    tcp: number;
    closing: number;
    epoch: string;
    seq: string;
    loadedRevision: string | null;
    selectedRevision: string | null;
    savedRevision: string | null;
    protocolWaiting: number;
    ruleWaiting: number;
    uiWaiting: number;
    errorCode: string | null;
    connections?: Connection[];
}
export interface Connection {
    connection: string;
    peer: string;
    phase: string;
    accepted_ns: string;
    established_ns: string;
    last_receive_complete_ns: string;
    last_send_complete_ns: string;
    executing_pdu: number;
    waiting_pdu: number;
    bytes: number;
    reason: number;
}
export interface RuntimePoint {
    pointId: string;
    dbNumber: number;
    byte: number;
    bit: number | null;
    name: string;
    dataType: string;
    value: Json;
    pointSeq: string;
    source: number;
    updatedNs: string;
    updatedAt: string | null;
    effective: Policy & {
        inheritedFrom: Record<string, string>;
    };
}
export interface RuntimeSnapshot {
    instances: RuntimeInstance[];
    etag: string;
    stale: boolean;
    values?: {
        instanceId: string;
        loadedRevision: string;
        epoch: string;
        seq: string;
        rows: RuntimePoint[];
        total: number;
        stale: boolean;
    };
}
export interface Bootstrap {
    version: string;
    product: string;
    profileDir: string;
    nativeEnabled: boolean;
    schemaVersion: number;
}
export interface Preview {
    token: string;
    expectedEtag: string;
    kind: string;
    candidateSha256: string;
    details: Record<string, Json>;
    workspace: Workspace;
}
export interface Response<T> {
    result: 'ok' | 'error' | 'unknown';
    errorCode: string | null;
    committed: boolean | null;
    receiptState: 'known' | 'unknown';
    currentEtag: string | null;
    data: T | null;
}
export class IpcFailure extends Error {
    constructor(public code: string, public currentEtag: string | null = null, public unknown = false) { super(code); }
}
export const desktopAvailable = isTauri();
async function call<T>(command: string, request?: unknown): Promise<T> { if (!desktopAvailable)
    throw new IpcFailure('desktop_unavailable'); let response: Response<T>; try {
    response = await invoke(command, request === undefined ? {} : { request });
}
catch {
    throw new IpcFailure('ipc_transport_unknown', null, true);
} if (response.result !== 'ok' || response.data === null)
    throw new IpcFailure(response.errorCode || 'operation_failed', response.currentEtag, response.receiptState === 'unknown'); return response.data; }
const operation = <T>(payload: T) => ({ operationId: crypto.randomUUID(), payload });
export const getBootstrap = () => call<Bootstrap>('ds_get_bootstrap');
export const getSnapshot = (instanceId: string | null = null, offset = 0, limit = 50) => call<RuntimeSnapshot>('ds_get_runtime_snapshot', { instanceId, offset, limit });
export const getConfiguration = (revisionId: string | null = null, revisionOffset = 0) => call<Configuration>('ds_get_configuration', { revisionId, revisionOffset });
export const saveConfiguration = (expectedEtag: string, workspace: Workspace, confirmPoints: string[]) => call('ds_save_configuration', operation({ expectedEtag, workspace, confirmPoints }));
export const previewImport = (payload: unknown) => call<{
    declarations: {
        inputId: string;
        declarationIndex: number;
        name: string;
        db: boolean;
        issues: string[];
    }[];
    preview: Preview | null;
    initializerNotice: boolean;
}>('ds_preview_import', operation(payload));
export const previewLayout = (payload: unknown) => call<Preview>('ds_preview_layout', operation(payload));
export const previewNames = (payload: unknown) => call<Preview>('ds_preview_names', operation(payload));
export const previewApply = (payload: unknown) => call<Preview>('ds_preview_apply', operation(payload));
export const confirmPreview = (kind: 'import' | 'layout' | 'names', preview: Preview) => call('ds_confirm_' + kind, operation({ expectedEtag: preview.expectedEtag, token: preview.token, candidateSha256: preview.candidateSha256 }));
export const applyRevision = (instanceId: string, preview: Preview) => call('ds_apply_revision', operation({ instanceId, expectedEtag: preview.expectedEtag, token: preview.token, candidateSha256: preview.candidateSha256, impactSha256: preview.details.impactSha256 }));
export const controlInstance = (payload: unknown) => call('ds_control_instance', operation(payload));
export const writePoint = (payload: unknown) => call('ds_write_point', operation(payload));
export const closeConnection = (payload: unknown) => call('ds_close_connection', operation(payload));
export const queryLogs = (offset = 0, limit = 50, event: string | null = null) => call<{
    rows: Record<string, Json>[];
    retained: number;
    lost: string;
    stdoutWriteErrors: string;
    stdoutDroppedBytes: string;
    fileWriteErrors: string;
    fileDroppedBytes: string;
    fileQueueDroppedLines: string;
    fileRotations: string;
    observabilityDegraded: boolean;
    configurationPath: string;
    storageBytes: string | null;
}>('ds_query_logs', { offset, limit, event });
