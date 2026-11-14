/** 投递具名IPC facade；浏览器无桥不制造能力/ACK，所有业务状态归Rust/SQLite。 */
import { localCall } from './localAcquisition'
export interface SourceBinding { instanceId: string; plcId: string; dbNumber: number; sourceGeneration: string }
export interface ReportingBinding { localPlcId: string; instanceId: string; plcId: string; sourceGeneration: string }
export interface DeliverySettings { schemaVersion: 1; settingsRevision: string; origin: string | null; path: string; intervalSeconds: number; identityMode: 'per_plc'; bindings: ReportingBinding[]; disabledLocalPlcs: string[] }
export interface SourceMaterial { schemaVersion: 1; contractVersion: string; sources: SourceBinding[]; localSources: Array<{ localPlcId: string; name: string; dbNumbers: number[] }> }
export interface DeliverySnapshot { schemaVersion: 1; available: boolean; running: boolean; state: string; origin?: string | null; pending?: number; acknowledged?: number; historicalV1Acknowledged?: number; sampleCounts?: { pending: number; unknown: number; needsProcessing: number; acknowledged: number }; lastAcknowledgedAt?: string | null; lastError?: string | null; needsReason?: string | null }
export interface DeliveryRow { event?: string; order: number; batchId: string; plcId?: string; dbNumber?: number; state: string; attempt: number; createdAt: string; lastError: string | null }
export interface DeliveryPage { schemaVersion: 1; items: DeliveryRow[]; nextCursor: number | null }
export const getDeliverySettings = () => localCall<DeliverySettings>('daa_get_delivery_settings')
export const saveDeliverySettings = (settings: DeliverySettings, expectedRevision: string) => localCall<DeliverySettings>('daa_save_delivery_settings', { settings, expectedRevision })
export const getDeliverySnapshot = () => localCall<DeliverySnapshot>('daa_get_delivery_snapshot')
export const setDelivery = (action: 'start' | 'pause' | 'resume', settingsRevision?: string, sources?: SourceBinding[]) => localCall<DeliverySnapshot>('daa_set_delivery', { action, ...(settingsRevision && sources ? { settingsRevision, sources } : {}) })
export const rebindDelivery = (sampleId: string, oldUrl: string, settingsRevision: string, sources: SourceBinding[]) => localCall<DeliverySnapshot>('daa_set_delivery', { action: 'rebind', sampleId, oldUrl, settingsRevision, sources })
export const listDeliveries = (cursor: number | null, limit = 20, kind: 'batches' | 'events' = 'batches', state?: string) => localCall<DeliveryPage>('daa_list_deliveries', { cursor, limit, kind, ...(state ? { state } : {}) })
export const getDelivery = (batchId: string) => localCall<Record<string, unknown>>('daa_get_delivery', { batchId })
export const previewDelivery = (cycleId: string) => localCall<Record<string, unknown>>('daa_preview_delivery', { cycleId })
export const testFactsEndpoint = (plcId: string, query: { mode?: string; from?: string | null; to?: string | null; cursor?: string | null; page?: number } = {}) => localCall<Record<string, unknown>>('daa_test_facts_endpoint', { plcId, ...query })
export const getFactsSourceMaterial = () => localCall<SourceMaterial>('daa_get_facts_source_material')
