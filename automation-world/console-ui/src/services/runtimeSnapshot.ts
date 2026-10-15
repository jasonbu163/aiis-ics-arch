/**
 * File Path: /control-agent/src/services/runtimeSnapshot.ts
 * Description: Read-only runtime snapshot loader for the Control Agent console
 * Main Features:
 *   - Calls the Tauri runtime snapshot command when available
 *   - Provides browser-dev fallback data
 *   - Probes backend reachability without mutating backend state
 */
import { invoke } from '@tauri-apps/api/core'

export interface PointTypeCount {
  dataType: string
  count: number
}

export interface PlcPointContractSnapshot {
  configuredPath: string
  resolvedPath: string
  exists: boolean
  loaded: boolean
  plcCount: number
  groupCount: number
  pointCount: number
  readableCount: number
  writableCount: number
  missingRequiredCount: number
  unsupportedTypeCount: number
  endpointIp: string
  endpointPort: number
  endpointRack: number
  endpointSlot: number
  typeCounts: PointTypeCount[]
  errorMessage: string
}

export type PlcCollectionTarget = 'all' | string

export interface PlcEndpointProbeSnapshot {
  host: string
  port: number
  rack: number
  slot: number
  enabled: boolean
  reachable: boolean
  latencyMs: number
  errorMessage: string
}

export interface PlcSampleValue {
  name: string
  dbNumber: number
  offset: number
  bit: number
  dataType: string
  value: string
}

export interface PlcSampleReadSnapshot {
  enabled: boolean
  autostart: boolean
  plcKey: string
  driver: string
  attempted: boolean
  succeeded: boolean
  sampleCount: number
  latencyMs: number
  values: PlcSampleValue[]
  errorMessage: string
}

export interface PlcCollectionGateSnapshot {
  plcReadAllowed: boolean
  plcWriteAllowed: boolean
  autostartMode: string
  readGateErrors: string[]
  writeGateErrors: string[]
  envErrors: string[]
  collectionEnabled: boolean
  writeEnabled: boolean
  loopEnabled: boolean
  databaseEnabled: boolean
  databaseConfigured: boolean
  databaseReadOnly: boolean
  driver: string
  intervalMs: number
  collectorKey: string
}

export interface MonitorCollectorStateSnapshot {
  loaded: boolean
  collectorKey: string
  status: string
  workerId: string
  mode: string
  targetIntervalMs: number
  startedAt: string
  lastHeartbeatAt: string
  lastSampleAt: string
  sampleCount: number
  failureCount: number
  lastCollectDurationMs: number
  lastWriteDurationMs: number
  lastLoopDelayMs: number
  lastError: string
}

export interface PlcLatestGroupSnapshot {
  plcKey: string
  dbNumber: number
  groupName: string
  quality: string
  collectedAt: string
  rawSnapshotId: number
  decodedCount: number
  unsupportedCount: number
  readDurationMs: number
  errorMessage: string
}

export interface PlcSnapshotPolicyStatusSnapshot {
  configuredPath: string
  resolvedPath: string
  exists: boolean
  loaded: boolean
  version: string
  latestMode: string
  rawHotRetentionDays: number
  fullDecodedPointCount: number
  policyPointCount: number
  selectedPointCount: number
  rawSelectedPointCount: number
  latestSelectedPointCount: number
  everySampleCount: number
  onChangeCount: number
  missingPolicyPointCount: number
  unknownPointCount: number
  invalidPolicyCount: number
  errorMessage: string
}

export interface PlcRuntimeEndpointSnapshot {
  host: string
  port: number
  rack: number
  slot: number
}

export interface PlcRuntimeUnitSnapshot {
  plcKey: string
  endpoint: PlcRuntimeEndpointSnapshot
  desiredState: string
  readState: string
  persistenceState: string
  collectionState: string
  runtimeState: string
  sampleStatus: string
  collectionStatus: string
  groupCount: number
  pointCount: number
  groupsAttempted: number
  groupsSucceeded: number
  groupsFailed: number
  lastSuccessAt: string
  lastErrorAt: string
  failureCount: number
  lastError: string
  lastSampleError: string
  lastReadDurationMs: number
}

export interface PlcCollectionStatusSnapshot {
  loaded: boolean
  localLoopRunning: boolean
  runtimeStatus: string
  rawSnapshotCount: number
  latestGroupCount: number
  gates: PlcCollectionGateSnapshot
  collectorState: MonitorCollectorStateSnapshot
  snapshotPolicy: PlcSnapshotPolicyStatusSnapshot
  plcUnits: PlcRuntimeUnitSnapshot[]
  latestGroups: PlcLatestGroupSnapshot[]
  errorMessage: string
}

export interface PlcCollectionControlResult {
  action: string
  target: string
  affectedPlcKeys: string[]
  accepted: boolean
  running: boolean
  status: string
  message: string
  gateErrors: string[]
}

export interface AgentHeartbeatSnapshot {
  status: string
  executorId: string
  processStartedAtUnixSeconds: number
  lastSeenUnixSeconds: number
  uptimeSeconds: number
  mode: string
}

export interface AuthorizationSelfTestSnapshot {
  attempted: boolean
  passed: boolean
  provider: string
  operatorId: string
  actionScope: string
  resourceId: string
  payloadHash: string
  temporaryTokenPresent: boolean
  approvalId: string
  expiresAtUnixSeconds: number
  result: string
  errorMessage: string
}

export interface AuthorizationGateSnapshot {
  enabled: boolean
  highRiskAuthRequired: boolean
  upperSystemUrlConfigured: boolean
  timeoutMs: number
  failClosed: boolean
  localOperatorRequired: boolean
  selfTest: AuthorizationSelfTestSnapshot
}

export interface RuntimeSnapshot {
  agentName: string
  version: string
  mode: string
  accessMode: string
  backendBaseUrl: string
  backendProbePath: string
  databaseEnabled: boolean
  databaseConfigured: boolean
  generatedAtUnixSeconds: number
  agentHeartbeat: AgentHeartbeatSnapshot
  plcPointContract: PlcPointContractSnapshot
  plcEndpointProbe: PlcEndpointProbeSnapshot
  plcSampleRead: PlcSampleReadSnapshot
  plcCollectionStatus: PlcCollectionStatusSnapshot
  authorizationGate: AuthorizationGateSnapshot
}

export interface BackendProbeResult {
  status: 'online' | 'offline' | 'skipped'
  latencyMs: number | null
}

interface PlcSampleReadSnapshotWire {
  enabled: boolean
  autostart: boolean
  plc_key: string
  driver: string
  attempted: boolean
  succeeded: boolean
  sample_count: number
  latency_ms: number
  values: Array<{
    name: string
    db_number: number
    offset: number
    bit: number
    data_type: string
    value: string
  }>
  error_message: string
}

interface RuntimeSnapshotWire {
  agent_name: string
  version: string
  mode: string
  access_mode: string
  backend_base_url: string
  backend_probe_path: string
  database_enabled: boolean
  database_configured: boolean
  generated_at_unix_seconds: number
  agent_heartbeat: {
    status: string
    executor_id: string
    process_started_at_unix_seconds: number
    last_seen_unix_seconds: number
    uptime_seconds: number
    mode: string
  }
  plc_point_contract: {
    configured_path: string
    resolved_path: string
    exists: boolean
    loaded: boolean
    plc_count: number
    group_count: number
    point_count: number
    readable_count: number
    writable_count: number
    missing_required_count: number
    unsupported_type_count: number
    endpoint_ip: string
    endpoint_port: number
    endpoint_rack: number
    endpoint_slot: number
    type_counts: Array<{
      data_type: string
      count: number
    }>
    error_message: string
  }
  plc_endpoint_probe: {
    host: string
    port: number
    rack: number
    slot: number
    enabled: boolean
    reachable: boolean
    latency_ms: number
    error_message: string
  }
  plc_sample_read: PlcSampleReadSnapshotWire
  plc_collection_status: {
    loaded: boolean
    local_loop_running: boolean
    runtime_status: string
    raw_snapshot_count: number
    latest_group_count: number
    gates: {
      plc_read_allowed: boolean
      plc_write_allowed: boolean
      autostart_mode: string
      read_gate_errors: string[]
      write_gate_errors: string[]
      env_errors: string[]
      collection_enabled: boolean
      write_enabled: boolean
      loop_enabled: boolean
      database_enabled: boolean
      database_configured: boolean
      database_read_only: boolean
      driver: string
      interval_ms: number
      collector_key: string
    }
    collector_state: {
      loaded: boolean
      collector_key: string
      status: string
      worker_id: string
      mode: string
      target_interval_ms: number
      started_at: string
      last_heartbeat_at: string
      last_sample_at: string
      sample_count: number
      failure_count: number
      last_collect_duration_ms: number
      last_write_duration_ms: number
      last_loop_delay_ms: number
      last_error: string
    }
    plc_units: Array<{
      plc_key: string
      endpoint: {
        host: string
        port: number
        rack: number
        slot: number
      }
      desired_state: string
      read_state: string
      persistence_state: string
      collection_state: string
      runtime_state: string
      sample_status: string
      collection_status: string
      group_count: number
      point_count: number
      groups_attempted: number
      groups_succeeded: number
      groups_failed: number
      last_success_at: string
      last_error_at: string
      failure_count: number
      last_error: string
      last_sample_error: string
      last_read_duration_ms: number
    }>
    latest_groups: Array<{
      plc_key: string
      db_number: number
      group_name: string
      quality: string
      collected_at: string
      raw_snapshot_id: number
      decoded_count: number
      unsupported_count: number
      read_duration_ms: number
      error_message: string
    }>
    snapshot_policy: {
      configured_path: string
      resolved_path: string
      exists: boolean
      loaded: boolean
      version: string
      latest_mode: string
      raw_hot_retention_days: number
      full_decoded_point_count: number
      policy_point_count: number
      selected_point_count: number
      raw_selected_point_count: number
      latest_selected_point_count: number
      every_sample_count: number
      on_change_count: number
      missing_policy_point_count: number
      unknown_point_count: number
      invalid_policy_count: number
      error_message: string
    }
    error_message: string
  }
  authorization_gate: {
    enabled: boolean
    high_risk_auth_required: boolean
    upper_system_url_configured: boolean
    timeout_ms: number
    fail_closed: boolean
    local_operator_required: boolean
    self_test: {
      attempted: boolean
      passed: boolean
      provider: string
      operator_id: string
      action_scope: string
      resource_id: string
      payload_hash: string
      temporary_token_present: boolean
      approval_id: string
      expires_at_unix_seconds: number
      result: string
      error_message: string
    }
  }
}

interface PlcCollectionControlResultWire {
  action: string
  target: string
  affected_plc_keys: string[]
  accepted: boolean
  running: boolean
  status: string
  message: string
  gate_errors: string[]
}

declare global {
  interface Window {
    __TAURI_INTERNALS__?: unknown
  }
}

const viteEnv = import.meta.env

function viteEnvOrDefault(key: string, defaultValue: string): string {
  const value = viteEnv[key]

  return typeof value === 'string' && value.length > 0 ? value : defaultValue
}

export const fallbackSnapshot: RuntimeSnapshot = {
  agentName: 'aiis-ics-control-agent',
  version: '0.1.0',
  mode: 'plc_collection',
  accessMode: 'database',
  backendBaseUrl: viteEnvOrDefault(
    'VITE_CONTROL_AGENT_BACKEND_BASE_URL',
    'http://127.0.0.1:8000'
  ),
  backendProbePath: viteEnvOrDefault('VITE_CONTROL_AGENT_BACKEND_PROBE_PATH', '/health'),
  databaseEnabled: false,
  databaseConfigured: false,
  generatedAtUnixSeconds: Math.floor(Date.now() / 1000),
  agentHeartbeat: {
    status: 'alive',
    executorId: 'control-agent-local',
    processStartedAtUnixSeconds: Math.floor(Date.now() / 1000),
    lastSeenUnixSeconds: Math.floor(Date.now() / 1000),
    uptimeSeconds: 0,
    mode: 'browser_fallback'
  },
  plcPointContract: {
    configuredPath: 'config/plc_points.yaml',
    resolvedPath: '',
    exists: false,
    loaded: false,
    plcCount: 0,
    groupCount: 0,
    pointCount: 0,
    readableCount: 0,
    writableCount: 0,
    missingRequiredCount: 0,
    unsupportedTypeCount: 0,
    endpointIp: '',
    endpointPort: 0,
    endpointRack: 0,
    endpointSlot: 0,
    typeCounts: [],
    errorMessage: 'Browser development mode does not load the Rust point contract scanner.'
  },
  plcEndpointProbe: {
    host: '',
    port: 0,
    rack: 0,
    slot: 0,
    enabled: false,
    reachable: false,
    latencyMs: 0,
    errorMessage: 'Browser development mode does not run the Rust TCP endpoint probe.'
  },
  plcSampleRead: {
    enabled: false,
    autostart: false,
    plcKey: '',
    driver: 'browser_fallback',
    attempted: false,
    succeeded: false,
    sampleCount: 0,
    latencyMs: 0,
    values: [],
    errorMessage: 'Browser development mode does not run the Rust S7 sample reader.'
  },
  plcCollectionStatus: {
    loaded: false,
    localLoopRunning: false,
    runtimeStatus: 'unknown',
    rawSnapshotCount: 0,
    latestGroupCount: 0,
    gates: {
      plcReadAllowed: false,
      plcWriteAllowed: false,
      autostartMode: 'stopped',
      readGateErrors: [],
      writeGateErrors: [],
      envErrors: [],
      collectionEnabled: false,
      writeEnabled: false,
      loopEnabled: false,
      databaseEnabled: false,
      databaseConfigured: false,
      databaseReadOnly: true,
      driver: 'browser_fallback',
      intervalMs: 3000,
      collectorKey: 'control-agent-plc'
    },
    collectorState: {
      loaded: false,
      collectorKey: 'control-agent-plc',
      status: 'missing',
      workerId: '',
      mode: '',
      targetIntervalMs: 0,
      startedAt: '',
      lastHeartbeatAt: '',
      lastSampleAt: '',
      sampleCount: 0,
      failureCount: 0,
      lastCollectDurationMs: 0,
      lastWriteDurationMs: 0,
      lastLoopDelayMs: 0,
      lastError: ''
    },
    snapshotPolicy: {
      configuredPath: 'config/plc_snapshot_policy.yaml',
      resolvedPath: '',
      exists: false,
      loaded: false,
      version: '',
      latestMode: 'policy_scoped',
      rawHotRetentionDays: 7,
      fullDecodedPointCount: 0,
      policyPointCount: 0,
      selectedPointCount: 0,
      rawSelectedPointCount: 0,
      latestSelectedPointCount: 0,
      everySampleCount: 0,
      onChangeCount: 0,
      missingPolicyPointCount: 0,
      unknownPointCount: 0,
      invalidPolicyCount: 0,
      errorMessage: 'Browser development mode does not load the Rust snapshot policy scanner.'
    },
    plcUnits: [],
    latestGroups: [],
    errorMessage: 'Browser development mode does not read PLC collection database snapshots.'
  },
  authorizationGate: {
    enabled: false,
    highRiskAuthRequired: true,
    upperSystemUrlConfigured: false,
    timeoutMs: 2000,
    failClosed: true,
    localOperatorRequired: true,
    selfTest: {
      attempted: true,
      passed: true,
      provider: 'local_mock',
      operatorId: 'local-self-test',
      actionScope: 'authorization.self_test',
      resourceId: 'control-agent',
      payloadHash: 'sha256:self-test-payload',
      temporaryTokenPresent: false,
      approvalId: 'local-self-test-approval',
      expiresAtUnixSeconds: Math.floor(Date.now() / 1000) + 300,
      result: 'approved',
      errorMessage: ''
    }
  }
}

function normalizeSnapshot(snapshot: RuntimeSnapshotWire): RuntimeSnapshot {
  return {
    agentName: snapshot.agent_name,
    version: snapshot.version,
    mode: snapshot.mode,
    accessMode: snapshot.access_mode,
    backendBaseUrl: snapshot.backend_base_url,
    backendProbePath: snapshot.backend_probe_path,
    databaseEnabled: snapshot.database_enabled,
    databaseConfigured: snapshot.database_configured,
    generatedAtUnixSeconds: snapshot.generated_at_unix_seconds,
    agentHeartbeat: {
      status: snapshot.agent_heartbeat.status,
      executorId: snapshot.agent_heartbeat.executor_id,
      processStartedAtUnixSeconds: snapshot.agent_heartbeat.process_started_at_unix_seconds,
      lastSeenUnixSeconds: snapshot.agent_heartbeat.last_seen_unix_seconds,
      uptimeSeconds: snapshot.agent_heartbeat.uptime_seconds,
      mode: snapshot.agent_heartbeat.mode
    },
    plcPointContract: {
      configuredPath: snapshot.plc_point_contract.configured_path,
      resolvedPath: snapshot.plc_point_contract.resolved_path,
      exists: snapshot.plc_point_contract.exists,
      loaded: snapshot.plc_point_contract.loaded,
      plcCount: snapshot.plc_point_contract.plc_count,
      groupCount: snapshot.plc_point_contract.group_count,
      pointCount: snapshot.plc_point_contract.point_count,
      readableCount: snapshot.plc_point_contract.readable_count,
      writableCount: snapshot.plc_point_contract.writable_count,
      missingRequiredCount: snapshot.plc_point_contract.missing_required_count,
      unsupportedTypeCount: snapshot.plc_point_contract.unsupported_type_count,
      endpointIp: snapshot.plc_point_contract.endpoint_ip,
      endpointPort: snapshot.plc_point_contract.endpoint_port,
      endpointRack: snapshot.plc_point_contract.endpoint_rack,
      endpointSlot: snapshot.plc_point_contract.endpoint_slot,
      typeCounts: snapshot.plc_point_contract.type_counts.map((item) => ({
        dataType: item.data_type,
        count: item.count
      })),
      errorMessage: snapshot.plc_point_contract.error_message
    },
    plcEndpointProbe: {
      host: snapshot.plc_endpoint_probe.host,
      port: snapshot.plc_endpoint_probe.port,
      rack: snapshot.plc_endpoint_probe.rack,
      slot: snapshot.plc_endpoint_probe.slot,
      enabled: snapshot.plc_endpoint_probe.enabled,
      reachable: snapshot.plc_endpoint_probe.reachable,
      latencyMs: snapshot.plc_endpoint_probe.latency_ms,
      errorMessage: snapshot.plc_endpoint_probe.error_message
    },
    plcSampleRead: normalizePlcSampleRead(snapshot.plc_sample_read),
    plcCollectionStatus: {
      loaded: snapshot.plc_collection_status.loaded,
      localLoopRunning: snapshot.plc_collection_status.local_loop_running,
      runtimeStatus: snapshot.plc_collection_status.runtime_status,
      rawSnapshotCount: snapshot.plc_collection_status.raw_snapshot_count,
      latestGroupCount: snapshot.plc_collection_status.latest_group_count,
      gates: {
        plcReadAllowed: snapshot.plc_collection_status.gates.plc_read_allowed,
        plcWriteAllowed: snapshot.plc_collection_status.gates.plc_write_allowed,
        autostartMode: snapshot.plc_collection_status.gates.autostart_mode,
        readGateErrors: snapshot.plc_collection_status.gates.read_gate_errors,
        writeGateErrors: snapshot.plc_collection_status.gates.write_gate_errors,
        envErrors: snapshot.plc_collection_status.gates.env_errors,
        collectionEnabled: snapshot.plc_collection_status.gates.collection_enabled,
        writeEnabled: snapshot.plc_collection_status.gates.write_enabled,
        loopEnabled: snapshot.plc_collection_status.gates.loop_enabled,
        databaseEnabled: snapshot.plc_collection_status.gates.database_enabled,
        databaseConfigured: snapshot.plc_collection_status.gates.database_configured,
        databaseReadOnly: snapshot.plc_collection_status.gates.database_read_only,
        driver: snapshot.plc_collection_status.gates.driver,
        intervalMs: snapshot.plc_collection_status.gates.interval_ms,
        collectorKey: snapshot.plc_collection_status.gates.collector_key
      },
      collectorState: {
        loaded: snapshot.plc_collection_status.collector_state.loaded,
        collectorKey: snapshot.plc_collection_status.collector_state.collector_key,
        status: snapshot.plc_collection_status.collector_state.status,
        workerId: snapshot.plc_collection_status.collector_state.worker_id,
        mode: snapshot.plc_collection_status.collector_state.mode,
        targetIntervalMs: snapshot.plc_collection_status.collector_state.target_interval_ms,
        startedAt: snapshot.plc_collection_status.collector_state.started_at,
        lastHeartbeatAt: snapshot.plc_collection_status.collector_state.last_heartbeat_at,
        lastSampleAt: snapshot.plc_collection_status.collector_state.last_sample_at,
        sampleCount: snapshot.plc_collection_status.collector_state.sample_count,
        failureCount: snapshot.plc_collection_status.collector_state.failure_count,
        lastCollectDurationMs:
          snapshot.plc_collection_status.collector_state.last_collect_duration_ms,
        lastWriteDurationMs: snapshot.plc_collection_status.collector_state.last_write_duration_ms,
        lastLoopDelayMs: snapshot.plc_collection_status.collector_state.last_loop_delay_ms,
        lastError: snapshot.plc_collection_status.collector_state.last_error
      },
      plcUnits: (snapshot.plc_collection_status.plc_units ?? []).map((unit) => ({
        plcKey: unit.plc_key,
        endpoint: {
          host: unit.endpoint.host,
          port: unit.endpoint.port,
          rack: unit.endpoint.rack,
          slot: unit.endpoint.slot
        },
        desiredState: unit.desired_state,
        readState: unit.read_state,
        persistenceState: unit.persistence_state,
        collectionState: unit.collection_state,
        runtimeState: unit.runtime_state,
        sampleStatus: unit.sample_status,
        collectionStatus: unit.collection_status,
        groupCount: unit.group_count,
        pointCount: unit.point_count,
        groupsAttempted: unit.groups_attempted,
        groupsSucceeded: unit.groups_succeeded,
        groupsFailed: unit.groups_failed,
        lastSuccessAt: unit.last_success_at,
        lastErrorAt: unit.last_error_at,
        failureCount: unit.failure_count,
        lastError: unit.last_error,
        lastSampleError: unit.last_sample_error,
        lastReadDurationMs: unit.last_read_duration_ms
      })),
      latestGroups: snapshot.plc_collection_status.latest_groups.map((item) => ({
        plcKey: item.plc_key,
        dbNumber: item.db_number,
        groupName: item.group_name,
        quality: item.quality,
        collectedAt: item.collected_at,
        rawSnapshotId: item.raw_snapshot_id,
        decodedCount: item.decoded_count,
        unsupportedCount: item.unsupported_count,
        readDurationMs: item.read_duration_ms,
        errorMessage: item.error_message
      })),
      snapshotPolicy: {
        configuredPath: snapshot.plc_collection_status.snapshot_policy.configured_path,
        resolvedPath: snapshot.plc_collection_status.snapshot_policy.resolved_path,
        exists: snapshot.plc_collection_status.snapshot_policy.exists,
        loaded: snapshot.plc_collection_status.snapshot_policy.loaded,
        version: snapshot.plc_collection_status.snapshot_policy.version,
        latestMode: snapshot.plc_collection_status.snapshot_policy.latest_mode,
        rawHotRetentionDays:
          snapshot.plc_collection_status.snapshot_policy.raw_hot_retention_days,
        fullDecodedPointCount:
          snapshot.plc_collection_status.snapshot_policy.full_decoded_point_count,
        policyPointCount: snapshot.plc_collection_status.snapshot_policy.policy_point_count,
        selectedPointCount: snapshot.plc_collection_status.snapshot_policy.selected_point_count,
        rawSelectedPointCount:
          snapshot.plc_collection_status.snapshot_policy.raw_selected_point_count,
        latestSelectedPointCount:
          snapshot.plc_collection_status.snapshot_policy.latest_selected_point_count,
        everySampleCount: snapshot.plc_collection_status.snapshot_policy.every_sample_count,
        onChangeCount: snapshot.plc_collection_status.snapshot_policy.on_change_count,
        missingPolicyPointCount:
          snapshot.plc_collection_status.snapshot_policy.missing_policy_point_count,
        unknownPointCount: snapshot.plc_collection_status.snapshot_policy.unknown_point_count,
        invalidPolicyCount: snapshot.plc_collection_status.snapshot_policy.invalid_policy_count,
        errorMessage: snapshot.plc_collection_status.snapshot_policy.error_message
      },
      errorMessage: snapshot.plc_collection_status.error_message
    },
    authorizationGate: {
      enabled: snapshot.authorization_gate.enabled,
      highRiskAuthRequired: snapshot.authorization_gate.high_risk_auth_required,
      upperSystemUrlConfigured: snapshot.authorization_gate.upper_system_url_configured,
      timeoutMs: snapshot.authorization_gate.timeout_ms,
      failClosed: snapshot.authorization_gate.fail_closed,
      localOperatorRequired: snapshot.authorization_gate.local_operator_required,
      selfTest: {
        attempted: snapshot.authorization_gate.self_test.attempted,
        passed: snapshot.authorization_gate.self_test.passed,
        provider: snapshot.authorization_gate.self_test.provider,
        operatorId: snapshot.authorization_gate.self_test.operator_id,
        actionScope: snapshot.authorization_gate.self_test.action_scope,
        resourceId: snapshot.authorization_gate.self_test.resource_id,
        payloadHash: snapshot.authorization_gate.self_test.payload_hash,
        temporaryTokenPresent: snapshot.authorization_gate.self_test.temporary_token_present,
        approvalId: snapshot.authorization_gate.self_test.approval_id,
        expiresAtUnixSeconds: snapshot.authorization_gate.self_test.expires_at_unix_seconds,
        result: snapshot.authorization_gate.self_test.result,
        errorMessage: snapshot.authorization_gate.self_test.error_message
      }
    }
  }
}

function normalizePlcSampleRead(snapshot: PlcSampleReadSnapshotWire): PlcSampleReadSnapshot {
  return {
    enabled: snapshot.enabled,
    autostart: snapshot.autostart,
    plcKey: snapshot.plc_key,
    driver: snapshot.driver,
    attempted: snapshot.attempted,
    succeeded: snapshot.succeeded,
    sampleCount: snapshot.sample_count,
    latencyMs: snapshot.latency_ms,
    values: snapshot.values.map((item) => ({
      name: item.name,
      dbNumber: item.db_number,
      offset: item.offset,
      bit: item.bit,
      dataType: item.data_type,
      value: item.value
    })),
    errorMessage: snapshot.error_message
  }
}

function normalizeCollectionControlResult(
  result: PlcCollectionControlResultWire
): PlcCollectionControlResult {
  return {
    action: result.action,
    target: result.target,
    affectedPlcKeys: result.affected_plc_keys,
    accepted: result.accepted,
    running: result.running,
    status: result.status,
    message: result.message,
    gateErrors: result.gate_errors
  }
}

function browserCollectionControlResult(
  action: string,
  target: string
): PlcCollectionControlResult {
  return {
    action,
    target,
    affectedPlcKeys: [],
    accepted: false,
    running: false,
    status: 'browser_fallback',
    message: 'PLC collection controls require the Tauri runtime.',
    gateErrors: []
  }
}

async function invokePlcControl(
  command: string,
  targetedCommand: string,
  action: string,
  target: PlcCollectionTarget
): Promise<PlcCollectionControlResult> {
  if (!window.__TAURI_INTERNALS__) {
    return browserCollectionControlResult(action, target)
  }

  const result =
    target === 'all'
      ? await invoke<PlcCollectionControlResultWire>(command)
      : await invoke<PlcCollectionControlResultWire>(targetedCommand, {
          plcKey: target
        })

  return normalizeCollectionControlResult(result)
}

export async function loadRuntimeSnapshot(): Promise<RuntimeSnapshot> {
  if (!window.__TAURI_INTERNALS__) {
    return fallbackSnapshot
  }

  const snapshot = await invoke<RuntimeSnapshotWire>('get_runtime_snapshot')

  return normalizeSnapshot(snapshot)
}

export async function startPlcCollectionLoop(
  target: 'all' | string = 'all'
): Promise<PlcCollectionControlResult> {
  return startPlcRead(target)
}

export async function stopPlcCollectionLoop(
  target: 'all' | string = 'all'
): Promise<PlcCollectionControlResult> {
  return stopPlcRead(target)
}

export function startPlcRead(target: PlcCollectionTarget = 'all') {
  return invokePlcControl(
    'start_plc_read',
    'start_plc_read_for_plc',
    'start_read',
    target
  )
}

export function stopPlcRead(target: PlcCollectionTarget = 'all') {
  return invokePlcControl('stop_plc_read', 'stop_plc_read_for_plc', 'stop_read', target)
}

export function enablePlcPersistence(target: PlcCollectionTarget = 'all') {
  return invokePlcControl(
    'enable_plc_persistence',
    'enable_plc_persistence_for_plc',
    'enable_persistence',
    target
  )
}

export function pausePlcPersistence(target: PlcCollectionTarget = 'all') {
  return invokePlcControl(
    'pause_plc_persistence',
    'pause_plc_persistence_for_plc',
    'pause_persistence',
    target
  )
}

export function startPlcCollection(target: PlcCollectionTarget = 'all') {
  return invokePlcControl(
    'start_plc_collection',
    'start_plc_collection_for_plc',
    'start_collection',
    target
  )
}

export function stopPlcCollection(target: PlcCollectionTarget = 'all') {
  return invokePlcControl(
    'stop_plc_collection',
    'stop_plc_collection_for_plc',
    'stop_collection',
    target
  )
}

export async function readPlcSamplesOnceForPlc(plcKey: string): Promise<PlcSampleReadSnapshot> {
  if (!window.__TAURI_INTERNALS__) {
    return {
      ...fallbackSnapshot.plcSampleRead,
      plcKey,
      errorMessage: 'PLC sample reads require the Tauri runtime.'
    }
  }

  const result = await invoke<PlcSampleReadSnapshotWire>('read_plc_samples_once_for_plc', {
    plcKey
  })

  return normalizePlcSampleRead(result)
}

export async function probeBackend(snapshot: RuntimeSnapshot): Promise<BackendProbeResult> {
  const baseUrl = snapshot.backendBaseUrl.replace(/\/$/, '')
  const probePath = snapshot.backendProbePath.startsWith('/')
    ? snapshot.backendProbePath
    : `/${snapshot.backendProbePath}`
  const startedAt = performance.now()
  const controller = new AbortController()
  const timeoutId = window.setTimeout(() => controller.abort(), 2000)

  try {
    const response = await fetch(`${baseUrl}${probePath}`, {
      method: 'GET',
      signal: controller.signal
    })

    return {
      status: response.ok ? 'online' : 'offline',
      latencyMs: Math.round(performance.now() - startedAt)
    }
  } catch {
    return {
      status: 'offline',
      latencyMs: null
    }
  } finally {
    window.clearTimeout(timeoutId)
  }
}
