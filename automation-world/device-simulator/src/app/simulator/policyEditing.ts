/** 草稿策略展示与编辑预校验；仅解释既有覆盖/类型合同，不执行规则，Rust仍作最终准入。 */
import type { Db, Instance, Json, Point, Policy, Rule } from '../../services/deviceSimulator';
export const policyFields = ['mode', 'owner', 'clientRead', 'clientWrite', 'uiWrite', 'uiMaintenance', 'initial', 'rule'] as const;
export type PolicyField = typeof policyFields[number];
export type BatchPatch = Partial<Record<PolicyField, { action: 'keep' | 'set' | 'inherit'; value?: unknown }>>;
export interface DraftRow { db: Db; point: Point; }
export interface Effective { policy: Policy; sources: Record<PolicyField, string>; errors: string[]; }
export const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value));
const bounds: Record<string, [number, number]> = { BOOL: [0, 1], BYTE: [0, 255], USINT: [0, 255], WORD: [0, 65535], UINT: [0, 65535], INT: [-32768, 32767], DWORD: [0, 4294967295], UDINT: [0, 4294967295], DINT: [-2147483648, 2147483647], REAL: [-3.4028234663852886e38, 3.4028234663852886e38] };
export function defaultScalar(type: string): Json { return type === 'BOOL' ? false : type === 'CHAR' ? '\0' : type.startsWith('STRING[') ? '' : 0; }
export function scalarError(type: string, value: unknown): string | null {
    if (type === 'BOOL') return typeof value === 'boolean' ? null : 'value_bool';
    if (type === 'CHAR' || /^STRING\[\d+\]$/.test(type)) {
        if (typeof value !== 'string') return 'value_type';
        if (!/^[\x00-\x7f]*$/.test(value)) return 'value_ascii';
        const length = type === 'CHAR' ? 1 : Number(type.slice(7, -1));
        return (type === 'CHAR' ? value.length === 1 : length >= 1 && length <= 254 && value.length <= length) ? null : 'value_length';
    }
    const range = bounds[type];
    if (!range) return 'unsupported_type';
    if (typeof value !== 'number' || !Number.isFinite(value)) return 'value_type';
    return value < range[0] || value > range[1] || type !== 'REAL' && !Number.isInteger(value) ? 'value_range' : null;
}
export function parseScalar(type: string | undefined, text: string): Json {
    let value: Json;
    if (type === 'CHAR' || type?.startsWith('STRING[')) value = text;
    else if (type === 'BOOL') {
        if (!['true', 'false', '0', '1'].includes(text)) throw Error('value_bool');
        value = text === 'true' || text === '1';
    } else {
        // 不把空白、十六进制或未完成数字静默转成0。
        if (!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/.test(text.trim())) throw Error('typed_value_invalid');
        value = Number(text);
    }
    const error = type ? scalarError(type, value) : null;
    if (error || typeof value === 'number' && !Number.isFinite(value)) throw Error(error || 'value_finite');
    return value;
}
export function newRule(mode: Rule['kind'], type?: string): Rule {
    return { kind: mode, fixedValue: defaultScalar(type || 'INT'), min: 0, max: 1, periodMs: 1000, phase: 0, seed: '', halfPeriodMs: 500 };
}
export function modeChange(mode: NonNullable<Policy['mode']>, type?: string): Policy {
    return { mode, owner: mode === 'hold' ? 'none' : 'rule', clientWrite: false, uiWrite: false, uiMaintenance: false, rule: mode === 'hold' ? null : newRule(mode, type) };
}
function width(type: string): number {
    if (['BOOL', 'BYTE', 'USINT', 'CHAR'].includes(type)) return 1;
    if (['WORD', 'UINT', 'INT'].includes(type)) return 2;
    if (['DWORD', 'UDINT', 'DINT', 'REAL'].includes(type)) return 4;
    if (/^STRING\[\d+\]$/.test(type)) return Number(type.slice(7, -1)) + 2;
    return 0;
}
export function effectivePolicy(instance: Instance, db: Db, point: Point): Effective {
    const policy: Policy = { mode: 'hold', owner: 'none', clientRead: true, clientWrite: false, uiWrite: false, uiMaintenance: false, initial: defaultScalar(point.dataType), rule: null };
    const sources = Object.fromEntries(policyFields.map(field => [field, 'default'])) as Effective['sources'];
    const errors: string[] = [];
    function overlay(value: Policy, source: string) {
        for (const field of policyFields) if (value[field] !== null && value[field] !== undefined) {
            Object.assign(policy, { [field]: value[field] }); sources[field] = source;
        }
    }
    overlay(instance.policy, 'instance'); overlay(db.policy, 'db');
    const regions = [...db.regions].sort((a, b) => a.firstBit - b.firstBit);
    if (regions.some((r, n) => r.firstBit < 0 || r.bitLength <= 0 || r.firstBit + r.bitLength > db.length * 8 || n > 0 && regions[n - 1]!.firstBit + regions[n - 1]!.bitLength > r.firstBit)) errors.push('policy_region_overlap');
    if (point.byte !== null) {
        const begin = point.byte * 8 + (point.bit || 0), end = begin + (point.dataType === 'BOOL' ? 1 : width(point.dataType) * 8);
        for (const region of regions) if (begin < region.firstBit + region.bitLength && end > region.firstBit) {
            if (begin < region.firstBit || end > region.firstBit + region.bitLength) errors.push('policy_split_field');
            else overlay(region.policy, 'region:' + region.id);
        }
    }
    overlay(point.policy, 'point');
    if (policy.mode === 'hold') {
        if (policy.owner === 'rule') errors.push('policy_owner');
        policy.rule = null;
    } else {
        if (policy.owner !== 'rule' || policy.clientWrite || policy.uiWrite || policy.uiMaintenance) errors.push('policy_owner');
        const r = policy.rule;
        if (!r) errors.push('rule_missing');
        else {
            if (r.kind !== policy.mode) errors.push('rule_mode');
            if (!Number.isInteger(r.periodMs) || !Number.isInteger(r.halfPeriodMs) || r.periodMs < 100 || r.halfPeriodMs < 100 || r.periodMs > 4294967295 || r.halfPeriodMs > 4294967295 || !Number.isFinite(r.phase) || new TextEncoder().encode(r.seed).length > 100) errors.push('rule_parameters');
            if (r.kind === 'fixed') { const e = scalarError(point.dataType, r.fixedValue); if (e) errors.push(e); }
            else if (r.kind === 'toggle') { if (point.dataType !== 'BOOL') errors.push('rule_type'); }
            else {
                const range = bounds[point.dataType];
                if (!range) errors.push('rule_type');
                else if (!Number.isFinite(r.min) || !Number.isFinite(r.max) || r.min > r.max || r.min < range[0] || r.max > range[1] || point.dataType !== 'REAL' && (!Number.isInteger(r.min) || !Number.isInteger(r.max))) errors.push('rule_range');
            }
        }
    }
    if (policy.clientWrite && policy.owner !== 'client' || policy.uiWrite && policy.owner !== 'ui' || policy.uiMaintenance && !['none', 'client'].includes(policy.owner!)) errors.push('policy_owner');
    const initialError = scalarError(point.dataType, policy.initial); if (initialError) errors.push(initialError);
    return { policy, sources, errors: [...new Set(errors)] };
}
export function draftRows(instance: Instance | null, dbIds: string[]): DraftRow[] {
    return instance ? [...instance.dbs].filter(db => !dbIds.length || dbIds.includes(db.id)).sort((a, b) => a.number - b.number || a.id.localeCompare(b.id)).flatMap(db => [...db.points].sort((a, b) => (a.byte ?? Infinity) - (b.byte ?? Infinity) || (a.bit ?? 0) - (b.bit ?? 0) || a.id.localeCompare(b.id)).map(point => ({ db, point }))) : [];
}
export function selectedIds(rows: DraftRow[], ids: ReadonlySet<string>): string[] { return rows.filter(row => ids.has(row.point.id)).map(row => row.point.id); }
export function draftBaseline(instance: Instance | null, dbIds: string[], etag = ''): string { return JSON.stringify([etag, dbIds, instance]); }
export function invalidateConfirmations(before: Instance, after: Instance): void {
    for (const db of after.dbs) for (const point of db.points) {
        const oldDb = before.dbs.find(d => d.id === db.id), old = oldDb?.points.find(p => p.id === point.id);
        if (!oldDb || !old) { point.confirmations = { initial: null, policy: null }; continue; }
        const a = effectivePolicy(before, oldDb, old), b = effectivePolicy(after, db, point);
        if (a.errors.length || b.errors.length || JSON.stringify(a.policy.initial) !== JSON.stringify(b.policy.initial)) point.confirmations.initial = null;
        const { initial: ai, ...ap } = a.policy, { initial: bi, ...bp } = b.policy;
        if (a.errors.length || b.errors.length || JSON.stringify(ap) !== JSON.stringify(bp)) point.confirmations.policy = null;
    }
}
export interface BatchIssue { db: number; pointId: string; name: string; type: string; code: string; }
export function batchCandidate(instance: Instance, ids: string[], patch: BatchPatch, baseline: string, currentBaseline: string) {
    const issues: BatchIssue[] = [], candidate = clone(instance), changes: { db: number; pointId: string; name: string; before: Effective; after: Effective; overrides: Policy }[] = [];
    if (!ids.length || baseline !== currentBaseline || new Set(ids).size !== ids.length) return { candidate: null, issues, changes, error: 'staleSelection', noop: false };
    const active = policyFields.filter(field => patch[field] && patch[field]!.action !== 'keep');
    if (!active.length) return { candidate: null, issues, changes, error: null, noop: true };
    for (const id of ids) {
        const db = candidate.dbs.find(d => d.points.some(p => p.id === id)), point = db?.points.find(p => p.id === id);
        if (!db || !point) return { candidate: null, issues, changes, error: 'staleSelection', noop: false };
        const before = effectivePolicy(instance, instance.dbs.find(d => d.id === db.id)!, point);
        try {
            // 必要mode联动先构造；用户启用的其它字段随后明确覆盖，冲突会整批阻断。
            if (patch.mode?.action === 'set') Object.assign(point.policy, modeChange(patch.mode.value as NonNullable<Policy['mode']>, point.dataType));
            for (const field of active) {
                const change = patch[field]!;
                if (change.action === 'inherit') Object.assign(point.policy, { [field]: null });
                else {
                    let value = change.value;
                    if (field === 'initial') value = parseScalar(point.dataType, String(value ?? ''));
                    if (field === 'rule' && value) {
                        const rule = clone(value as Rule);
                        if (rule.kind === 'fixed') rule.fixedValue = parseScalar(point.dataType, String(rule.fixedValue ?? ''));
                        value = rule;
                    }
                    Object.assign(point.policy, { [field]: value });
                }
            }
            const after = effectivePolicy(candidate, db, point);
            for (const code of after.errors) issues.push({ db: db.number, pointId: id, name: point.name || point.sourcePath, type: point.dataType, code });
            changes.push({ db: db.number, pointId: id, name: point.name || point.sourcePath, before, after, overrides: clone(point.policy) });
        } catch (error) { issues.push({ db: db.number, pointId: id, name: point.name || point.sourcePath, type: point.dataType, code: error instanceof Error ? error.message : 'typed_value_invalid' }); }
    }
    if (issues.length) return { candidate: null, issues, changes, error: null, noop: false };
    invalidateConfirmations(instance, candidate);
    return { candidate, issues, changes, error: null, noop: JSON.stringify(instance) === JSON.stringify(candidate) };
}
