/** 投递具名IPC facade；浏览器无桥不制造能力/ACK，所有业务状态归Rust/SQLite。 */
import { localCall } from './localAcquisition'
export interface SourceAdoption { plcId: string; sourceGeneration: string; definitionSetDigest: string; contextSha256: string; sequenceFrom: string; sequenceThrough: string; reference: string }
export interface DeliverySettings { schemaVersion: 1; settingsRevision: string; targetId: string | null; origin: string | null; intervalSeconds: number; adoptionReference: string; contractPins: Record<string, string>; sources: SourceAdoption[] }
export interface SourceMaterial { schemaVersion: 1; instanceId: string; sources: Array<{ plcId: string; sourceGeneration: string | null; nextSourceSeq: string | null; definitionSetDigest: string; contextSha256: string }> }
export interface DeliverySnapshot { schemaVersion: 1; available: boolean; running: boolean; state: string; origin?: string | null; targetId?: string | null; pending?: number; acknowledged?: number; counts?: Record<string, number>; sampleCounts?: { unfrozen: number; frozen: number; needsProcessing: number; acknowledged: number }; lastAcknowledgedAt?: string | null; lastError?: string | null; requestBytes?: number; receiptBytes?: number; metadataBytes?: number }
export interface DeliveryRow { event?: string; order: number; batchId: string; state: string; attempt: number; nextAttemptAt: string; createdAt: string; lastError: string | null; requestDigest: string; bodySha256: string; targetId: string }
export interface DeliveryPage { schemaVersion: 1; items: DeliveryRow[]; nextCursor: number | null }
export const CONTRACT_PINS = { openapiSha256: 'bec51c468ff64a8d34dbb0a2faab2fda76d2b33769ee5ef066dc81e8bca274ee', schemaSha256: '60d0e285bebb1c6d24588f4d5f90e7bdd85ed0befdeab9d0b93445a94f45d4b3', vectorsSha256: '9a5ae0e90a006a7e450ec12557868e9eda20690f4853b6ae29aea2bdf714e782' } as const
export const getDeliverySettings = () => localCall<DeliverySettings>('daa_get_delivery_settings')
export const saveDeliverySettings = (settings: DeliverySettings, expectedRevision: string) => localCall<DeliverySettings>('daa_save_delivery_settings', { settings, expectedRevision })
export const getDeliverySnapshot = () => localCall<DeliverySnapshot>('daa_get_delivery_snapshot')
export const setDelivery = (action: 'start' | 'pause' | 'resume') => localCall<DeliverySnapshot>('daa_set_delivery', { action })
export const listDeliveries = (cursor: number | null, limit = 20, kind: 'batches' | 'events' = 'batches') => localCall<DeliveryPage>('daa_list_deliveries', { cursor, limit, kind })
export const getDelivery = (batchId: string) => localCall<Record<string, unknown>>('daa_get_delivery', { batchId })
export const previewDelivery = (cycleId: string) => localCall<Record<string, unknown>>('daa_preview_delivery', { cycleId })
export const testFactsEndpoint = (plcId: string, query: { mode?: string; from?: string | null; to?: string | null; cursor?: string | null; page?: number } = {}) => localCall<Record<string, unknown>>('daa_test_facts_endpoint', { plcId, ...query })
export const getFactsSourceMaterial = () => localCall<SourceMaterial>('daa_get_facts_source_material')
