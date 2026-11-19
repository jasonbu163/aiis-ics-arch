/** 正常IPC facade及严格字段类型；草稿/版本/加载分离，browser不返回mock成功。 */
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
    displayNames?: { 'zh-CN': string; 'en-US': string };
    description?: string;
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
    protection: { reason: 'latest' | 'selected' | 'loaded' | 'previous' | 'preview'; instanceId: string | null }[];
    canDelete: boolean;
}
export interface RollbackRelease { instanceId: string; revisionId: string; selectionEtag: string; }
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
    draftMatchesLatest: boolean;
    revisions: Revision[];
    revisionTotal: number;
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
export interface SaveResult {
    result: 'saved' | 'unchanged';
    etag: string;
    revisionId: string | null;
    cleanupPending?: string[];
}
export class IpcFailure extends Error {
    constructor(public code: string, public currentEtag: string | null = null, public unknown = false) { super(code); }
}
export const desktopAvailable = isTauri();
async function call<T>(command: string, request?: unknown, arguments_: Record<string, unknown> = {}): Promise<T> { if (!desktopAvailable)
    throw new IpcFailure('desktop_unavailable'); let response: Response<T>; try {
    response = await invoke(command, request === undefined ? arguments_ : { request, ...arguments_ });
}
catch {
    throw new IpcFailure('ipc_transport_unknown', null, true);
} if (response.result !== 'ok' || response.data === null)
    throw new IpcFailure(response.errorCode || 'operation_failed', response.currentEtag, response.receiptState === 'unknown'); return response.data; }
const operation = <T>(payload: T) => ({ operationId: crypto.randomUUID(), payload });
export const getBootstrap = () => call<Bootstrap>('ds_get_bootstrap');
export const getSnapshot = (instanceId: string | null = null, offset = 0, limit = 50) => call<RuntimeSnapshot>('ds_get_runtime_snapshot', { instanceId, offset, limit });
export const getConfiguration = (revisionId: string | null = null, revisionOffset = 0) => call<Configuration>('ds_get_configuration', { revisionId, revisionOffset });
export const saveConfiguration = (expectedEtag: string, workspace: Workspace, confirmPoints: string[]) => call<SaveResult>('ds_save_configuration', operation({ expectedEtag, workspace, confirmPoints }));
export interface DeclarationRef { inputId: string; declarationIndex: number; }
export interface DependencyIssue { code: string; path: string; typeName: string; candidates: DeclarationRef[]; }
export const previewImport = (payload: unknown, analyzeOnly = false) => call<{
    declarations: {
        inputId: string;
        declarationIndex: number;
        name: string;
        db: boolean;
        issues: string[];
        udtClosure: DeclarationRef[];
        dependencyIssues: DependencyIssue[];
    }[];
    preview: Preview | null;
    initializerNotice: boolean;
}>('ds_preview_import', operation(payload), { analyzeOnly });
export const previewLayout = (payload: unknown) => call<Preview>('ds_preview_layout', operation(payload));
export const previewNames = (payload: unknown) => call<Preview>('ds_preview_names', operation(payload));
export const previewApply = (payload: unknown) => call<Preview>('ds_preview_apply', operation(payload));
export const confirmPreview = (kind: 'import' | 'layout' | 'names', preview: Preview) => call('ds_confirm_' + kind, operation({ expectedEtag: preview.expectedEtag, token: preview.token, candidateSha256: preview.candidateSha256 }));
export const applyRevision = (instanceId: string, preview: Preview) => call('ds_apply_revision', operation({ instanceId, expectedEtag: preview.expectedEtag, token: preview.token, candidateSha256: preview.candidateSha256, impactSha256: preview.details.impactSha256 }));
export const previewPublishRevision = (expectedEtag: string) => call<Preview>('ds_preview_publish_revision', operation({ expectedEtag, revisionId: null }));
export const previewDeleteRevisions = (expectedEtag: string, revisionIds: string[]) => call<Preview>('ds_preview_delete_revision', operation({ expectedEtag, revisionIds }));
export const commitVersion = (preview: Preview, releaseRollback = false) => call<{ result: string; revisionId: string | null }>(preview.kind === 'publish_revision' ? 'ds_publish_revision' : 'ds_delete_revisions', operation({ expectedEtag: preview.expectedEtag, token: preview.token, candidateSha256: preview.candidateSha256, releaseRollback }));
export const cancelPreview = (preview: Preview) => call('ds_cancel_preview', operation({ token: preview.token }));
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

/** DS-003 只读保存版本及短期导出票据；目标目录只能由原生选择器提供。 */
export interface CatalogInstance {
    instanceId: string; name: string; host: string; port: number; rack: number; slot: number;
    localTsap: number; remoteTsap: number; selectedRevision: string | null; loadedRevision: string | null;
    dbCount: number; pointCount: number;
}
export interface CatalogTarget {
    instanceId: string; host: string; port: number; rack: number; slot: number;
    connectionConfirmed: boolean; loadedDifferenceConfirmed: boolean;
}
export interface CatalogPoint {
    id: string; name: string; displayName: string; displayNames: {'zh-CN': string; 'en-US': string} | null;
    description: string | null; dataType: string; sourcePath: string; byte: number | null; bit: number | null; enabled: boolean;
}
export interface CatalogDb { id: string; name: string; number: number; length: number; enabled: boolean; points: CatalogPoint[]; }
export interface CatalogRow {
    instanceId: string; name: string; filename: string; selectedRevision: string | null; loadedRevision: string | null;
    loadedDiffers: boolean; loopback: boolean; nonDefaultTsap: boolean; localTsap: number; remoteTsap: number;
    dbCount: number; pointCount: number; dbs: CatalogDb[]; document: Record<string, unknown> | null;
    issues: {code: string; dbId: string | null; pointId: string | null}[]; byteCount: number | null; fileSha256: string | null;
}
export interface CatalogRevision { revisionId: string; savedSeq: string; createdUtc: string; sha256: string; }
export interface CatalogPreview { token: string; revision: CatalogRevision; rows: CatalogRow[]; }
export interface CatalogFilenameErrors { filenameErrors: {instanceId: string; code: string}[]; }
export interface CatalogFile { instanceId: string; name: string; filename: string; }
export interface CatalogDirectory { rows: (CatalogFile & {conflict: boolean; valid: boolean})[]; }
export interface CatalogResultRow extends CatalogFile {
    result: 'written' | 'failed' | 'unknown';
    errorCode: string | null;
    cleanupPending: string | null;
    fileSha256: string | null;
    issues?: CatalogRow['issues'];
}
export interface CatalogResult { rows: CatalogResultRow[]; }
export const catalogRevision = (revisionId: string) => call<{revision: CatalogRevision; instances: CatalogInstance[]}>('ds_catalog_revision', operation({revisionId}));
export const catalogPreview = (revisionId: string, targets: CatalogTarget[], filenames: Record<string, string>) => call<CatalogPreview | CatalogFilenameErrors>('ds_catalog_preview', operation({revisionId, targets, filenames}));
export const catalogChooseDirectory = (token: string) => call<CatalogDirectory | 'cancelled'>('ds_catalog_choose_directory', operation({token}));
export const catalogCommit = (token: string) => call<CatalogResult>('ds_catalog_commit', operation({token}));
export const catalogCancel = (token: string) => call('ds_catalog_cancel', operation({token}));

/** 仅原生选择器提供目录文件；票据绑定原字节、监听参数及草稿。 */
export interface ImportCatalogPoint { id:string; name:string; display_name?:string; display_names?:{'zh-CN':string;'en-US':string}; description?:string; source_path?:string; data_type:string; byte_offset:number; bit?:number; source_enabled:boolean; }
export interface ImportCatalogDb { id:string; name:string; number:number; size_bytes:number; source_enabled?:boolean; points:ImportCatalogPoint[]; }
export interface ImportCatalogDocument {
    origin:{kind:string; profile_id:string; plc_id:string};
    export:{producer:string; profile_id:string; config_state:string; revision_id:string; payload_sha256:string; exported_at:string};
    plc:{name:string; protocol:string; connection:{host:string;port:number;rack:number;slot:number;local_tsap?:number;remote_tsap?:number}};
    dbs:ImportCatalogDb[];
}
export interface ImportCatalogFile {fileToken:string;fileName:string;byteCount:number;fileSha256:string;document:ImportCatalogDocument;}
export const chooseCatalogImport = () => call<ImportCatalogFile | 'cancelled'>('ds_catalog_import_choose', operation({}));
export const previewCatalogImport = (payload:{fileToken:string;expectedEtag:string;host:string;port:number;rack:number;slot:number;connectionConfirmed:boolean}) => call<Preview>('ds_catalog_import_preview', operation(payload));
export const confirmCatalogImport = (fileToken:string, preview:Preview) => call<SaveResult>('ds_catalog_import_confirm', operation({fileToken, token:preview.token, expectedEtag:preview.expectedEtag, candidateSha256:preview.candidateSha256}));
export const cancelCatalogImport = (fileToken:string) => call('ds_catalog_import_cancel', operation({fileToken}));
