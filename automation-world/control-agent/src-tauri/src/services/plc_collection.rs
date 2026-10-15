//! File Path: /control-agent/src-tauri/src/services/plc_collection.rs
//! Description: PLC DB block collection orchestration service
//! Main Features:
//!   - Reads PLC DB groups from the authoritative plc_points.yaml contract
//!   - Resolves each PLC endpoint through the shared runtime-contract policy
//!   - Decodes supported point values from rust-snap7 DB block reads
//!   - Writes raw/latest PLC snapshot rows through backend-owned database tables

use std::collections::{HashMap, HashSet};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex, OnceLock};
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant};

use chrono::Utc;
use serde_json::{json, Map, Value};

use crate::config::{parse_u64_or_default, AgentConfig};
use crate::domain::plc::{PlcEndpointProbeSnapshot, PlcRuntimeConfig, PlcRuntimeGroup};
use crate::domain::plc_collection::{
    MonitorCollectorStateSnapshot, NewMonitorCollectorState, NewPlcDbBlockSnapshot,
    PlcCollectionControlResult, PlcCollectionControlSmokeResult, PlcCollectionGateSnapshot,
    PlcCollectionLoopResult, PlcCollectionRunResult, PlcCollectionStatusSnapshot,
    PlcDbBlockGroupCollectResult, PlcRuntimeEndpointSnapshot, PlcRuntimeUnitSnapshot,
};
use crate::infrastructure::database::repositories::{
    read_plc_collection_database_status, PlcCollectionDatabaseWriter,
};
use crate::infrastructure::plc_client::{normalize_plc_driver, RUST_SNAP7_DRIVER};
use crate::infrastructure::plc_decode::{decode_sample_value, point_read_size};
use crate::infrastructure::plc_points::{load_runtime_contract, resolve_runtime_endpoints};
use crate::infrastructure::plc_snapshot_policy::{
    read_plc_snapshot_payload_policy_filter, read_plc_snapshot_policy_status,
    PlcSnapshotPayloadPolicyFilter,
};
use crate::infrastructure::rust_snap7_adapter;

#[derive(Clone)]
struct PlcRuntimeUnitState {
    desired_state: String,
    read_state: String,
    persistence_state: String,
    collection_state: String,
    runtime_state: String,
    sample_status: String,
    collection_status: String,
    groups_attempted: u32,
    groups_succeeded: u32,
    groups_failed: u32,
    last_success_at: String,
    last_error_at: String,
    failure_count: u32,
    last_error: String,
    last_sample_error: String,
    last_read_duration_ms: u128,
    cycle_degraded: bool,
}

impl Default for PlcRuntimeUnitState {
    fn default() -> Self {
        Self {
            desired_state: "stopped".to_string(),
            read_state: "stopped".to_string(),
            persistence_state: "paused".to_string(),
            collection_state: "stopped".to_string(),
            runtime_state: "stopped".to_string(),
            sample_status: "idle".to_string(),
            collection_status: "stopped".to_string(),
            groups_attempted: 0,
            groups_succeeded: 0,
            groups_failed: 0,
            last_success_at: String::new(),
            last_error_at: String::new(),
            failure_count: 0,
            last_error: String::new(),
            last_sample_error: String::new(),
            last_read_duration_ms: 0,
            cycle_degraded: false,
        }
    }
}

struct PlcWorkerHandle {
    stop_requested: Arc<AtomicBool>,
    thread: JoinHandle<()>,
}

#[derive(Default)]
struct PlcCollectionRuntime {
    workers: HashMap<String, PlcWorkerHandle>,
    states: Arc<Mutex<HashMap<String, PlcRuntimeUnitState>>>,
}

static PLC_COLLECTION_RUNTIME: OnceLock<Mutex<PlcCollectionRuntime>> = OnceLock::new();

fn plc_collection_runtime() -> &'static Mutex<PlcCollectionRuntime> {
    PLC_COLLECTION_RUNTIME.get_or_init(|| Mutex::new(PlcCollectionRuntime::default()))
}

enum PlcCollectionTarget {
    All,
    PlcKey(String),
}

impl PlcCollectionTarget {
    fn label(&self) -> String {
        match self {
            Self::All => "all".to_string(),
            Self::PlcKey(plc_key) => plc_key.clone(),
        }
    }
}

fn now_rfc3339() -> String {
    Utc::now().to_rfc3339()
}

fn disabled_result(
    enabled: bool,
    write_enabled: bool,
    driver: String,
    message: String,
) -> PlcCollectionRunResult {
    PlcCollectionRunResult {
        enabled,
        write_enabled,
        attempted: false,
        status: "disabled".to_string(),
        driver,
        latency_ms: 0,
        groups_attempted: 0,
        groups_succeeded: 0,
        raw_snapshots_written: 0,
        latest_snapshots_written: 0,
        groups: Vec::new(),
        message,
    }
}

fn failed_result(
    enabled: bool,
    write_enabled: bool,
    driver: String,
    latency_ms: u128,
    message: String,
) -> PlcCollectionRunResult {
    PlcCollectionRunResult {
        enabled,
        write_enabled,
        attempted: true,
        status: "failed".to_string(),
        driver,
        latency_ms,
        groups_attempted: 0,
        groups_succeeded: 0,
        raw_snapshots_written: 0,
        latest_snapshots_written: 0,
        groups: Vec::new(),
        message,
    }
}

fn decoded_value_from_text(data_type: &str, value: String) -> Value {
    match data_type {
        "Bool" => Value::Bool(value == "true"),
        "USInt" | "UInt" | "Word" | "UDInt" => value
            .parse::<u64>()
            .map(Value::from)
            .unwrap_or_else(|_| Value::String(value)),
        "Int" | "DInt" => value
            .parse::<i64>()
            .map(Value::from)
            .unwrap_or_else(|_| Value::String(value)),
        "Real" => value
            .parse::<f64>()
            .map(Value::from)
            .unwrap_or_else(|_| Value::String(value)),
        _ => Value::String(value),
    }
}

fn decode_group_payload(
    group: &PlcRuntimeGroup,
    raw_bytes: &[u8],
) -> (Value, Option<Value>, u32, u32) {
    let mut decoded = Map::new();
    let mut unsupported = Map::new();

    for point in &group.points {
        if point.readable == Some(false) {
            unsupported.insert(point.name.clone(), json!("readable=false"));
            continue;
        }

        let candidate = point.as_runtime_candidate(group.db_number);
        let read_size = point_read_size(&candidate);
        if read_size == 0 {
            unsupported.insert(
                point.name.clone(),
                json!(format!("unsupported type {}", point.data_type)),
            );
            continue;
        }

        if point.offset < group.start {
            unsupported.insert(
                point.name.clone(),
                json!(format!(
                    "offset {} is before group start {}",
                    point.offset, group.start
                )),
            );
            continue;
        }

        let relative_start = (point.offset - group.start) as usize;
        let relative_end = relative_start + read_size as usize;
        let Some(bytes) = raw_bytes.get(relative_start..relative_end) else {
            unsupported.insert(
                point.name.clone(),
                json!(format!(
                    "offset {} size {} exceeds group block size {}",
                    point.offset,
                    read_size,
                    raw_bytes.len()
                )),
            );
            continue;
        };

        match decode_sample_value(&candidate, bytes) {
            Ok(value) => {
                decoded.insert(
                    point.name.clone(),
                    decoded_value_from_text(&point.data_type, value),
                );
            }
            Err(error) => {
                unsupported.insert(point.name.clone(), json!(error));
            }
        }
    }

    let decoded_count = decoded.len() as u32;
    let unsupported_count = unsupported.len() as u32;
    let unsupported_payload = if unsupported.is_empty() {
        None
    } else {
        Some(Value::Object(unsupported))
    };

    (
        Value::Object(decoded),
        unsupported_payload,
        decoded_count,
        unsupported_count,
    )
}

enum SnapshotPayloadScope {
    Raw,
    Latest,
}

fn filter_payload_for_snapshot_policy(
    payload: &Value,
    policy_filter: Option<&PlcSnapshotPayloadPolicyFilter>,
    plc_key: &str,
    db_number: u16,
    group_name: &str,
    scope: SnapshotPayloadScope,
) -> Value {
    let Some(policy_filter) = policy_filter else {
        return payload.clone();
    };
    let Some(payload_object) = payload.as_object() else {
        return payload.clone();
    };

    let mut filtered = Map::new();
    for (point_name, value) in payload_object {
        let allowed = match scope {
            SnapshotPayloadScope::Raw => {
                policy_filter.allows_raw_point(plc_key, db_number, group_name, point_name)
            }
            SnapshotPayloadScope::Latest => {
                policy_filter.allows_latest_point(plc_key, db_number, group_name, point_name)
            }
        };

        if allowed {
            filtered.insert(point_name.clone(), value.clone());
        }
    }

    Value::Object(filtered)
}

fn filter_optional_payload_for_snapshot_policy(
    payload: &Option<Value>,
    policy_filter: Option<&PlcSnapshotPayloadPolicyFilter>,
    plc_key: &str,
    db_number: u16,
    group_name: &str,
    scope: SnapshotPayloadScope,
) -> Option<Value> {
    let filtered = filter_payload_for_snapshot_policy(
        payload.as_ref()?,
        policy_filter,
        plc_key,
        db_number,
        group_name,
        scope,
    );

    if filtered.as_object().map(|object| object.is_empty()) == Some(true) {
        None
    } else {
        Some(filtered)
    }
}

fn collection_device_id(config: &AgentConfig) -> i32 {
    parse_u64_or_default(
        &config.value_or_default("CONTROL_AGENT_PLC_COLLECTION_DEVICE_ID", "1"),
        1,
    )
    .min(i32::MAX as u64) as i32
}

fn collection_interval_ms(config: &AgentConfig) -> u64 {
    parse_u64_or_default(
        &config.value_or_default("CONTROL_AGENT_PLC_COLLECTION_INTERVAL_MS", "3000"),
        3000,
    )
    .clamp(250, 3_600_000)
}

fn collection_collector_key(config: &AgentConfig) -> String {
    config.value_or_default(
        "CONTROL_AGENT_PLC_COLLECTION_COLLECTOR_KEY",
        "control-agent-plc",
    )
}

fn parse_bool_value(value: &str) -> Option<bool> {
    match value.trim() {
        "1" | "true" | "TRUE" | "True" | "yes" | "YES" | "on" | "ON" => Some(true),
        "0" | "false" | "FALSE" | "False" | "no" | "NO" | "off" | "OFF" => Some(false),
        _ => None,
    }
}

fn resolve_bool_gate(
    config: &AgentConfig,
    canonical_key: &str,
    legacy_key: &str,
    default_value: bool,
) -> (bool, Vec<String>) {
    let canonical_raw = config.raw_value(canonical_key);
    let legacy_raw = config.raw_value(legacy_key);
    let canonical_value = canonical_raw.as_deref().and_then(parse_bool_value);
    let legacy_value = legacy_raw.as_deref().and_then(parse_bool_value);
    let mut errors = Vec::new();

    if canonical_raw.is_some() && canonical_value.is_none() {
        errors.push(format!("{canonical_key} has an invalid boolean value"));
    }
    if legacy_raw.is_some() && legacy_value.is_none() {
        errors.push(format!("{legacy_key} has an invalid boolean value"));
    }
    if let (Some(canonical), Some(legacy)) = (canonical_value, legacy_value) {
        if canonical != legacy {
            errors.push(format!(
                "env_conflict: {canonical_key} and {legacy_key} disagree"
            ));
        }
    }

    (
        canonical_value.or(legacy_value).unwrap_or(default_value),
        errors,
    )
}

fn resolve_autostart_mode(config: &AgentConfig) -> (String, Vec<String>) {
    let canonical_raw = config.raw_value("CONTROL_AGENT_PLC_AUTOSTART_MODE");
    let legacy_raw = config.raw_value("CONTROL_AGENT_PLC_COLLECTION_LOOP_AUTOSTART");
    let canonical_mode = canonical_raw
        .as_deref()
        .and_then(|value| match value.trim() {
            "stopped" | "read_only" | "collect" => Some(value.trim().to_string()),
            _ => None,
        });
    let legacy_mode = legacy_raw
        .as_deref()
        .and_then(parse_bool_value)
        .map(|enabled| if enabled { "collect" } else { "stopped" }.to_string());
    let mut errors = Vec::new();

    if canonical_raw.is_some() && canonical_mode.is_none() {
        errors.push(
            "CONTROL_AGENT_PLC_AUTOSTART_MODE must be stopped, read_only or collect".to_string(),
        );
    }
    if legacy_raw.is_some() && legacy_raw.as_deref().and_then(parse_bool_value).is_none() {
        errors.push(
            "CONTROL_AGENT_PLC_COLLECTION_LOOP_AUTOSTART has an invalid boolean value".to_string(),
        );
    }
    if let (Some(canonical), Some(legacy)) = (canonical_mode.as_deref(), legacy_mode.as_deref()) {
        if canonical != legacy {
            errors.push(
                "env_conflict: CONTROL_AGENT_PLC_AUTOSTART_MODE and CONTROL_AGENT_PLC_COLLECTION_LOOP_AUTOSTART disagree"
                    .to_string(),
            );
        }
    }

    (
        canonical_mode
            .or(legacy_mode)
            .unwrap_or_else(|| "stopped".to_string()),
        errors,
    )
}

fn collection_gate_snapshot(config: &AgentConfig) -> PlcCollectionGateSnapshot {
    let (plc_read_allowed, read_env_errors) = resolve_bool_gate(
        config,
        "CONTROL_AGENT_PLC_READ_ALLOWED",
        "CONTROL_AGENT_PLC_COLLECTION_ENABLED",
        false,
    );
    let (plc_write_allowed, write_env_errors) = resolve_bool_gate(
        config,
        "CONTROL_AGENT_PLC_WRITE_ALLOWED",
        "CONTROL_AGENT_PLC_COLLECTION_WRITE_ENABLED",
        false,
    );
    let (autostart_mode, autostart_errors) = resolve_autostart_mode(config);
    let mut env_errors = read_env_errors.clone();
    env_errors.extend(write_env_errors.clone());
    env_errors.extend(autostart_errors);
    let database_enabled = config.bool_or_default("CONTROL_AGENT_DATABASE_ENABLED", false);
    let database_configured = config.is_configured("CONTROL_AGENT_DATABASE_URL");
    let database_read_only = config.bool_or_default("CONTROL_AGENT_DATABASE_READ_ONLY", true);
    let driver = normalize_plc_driver(
        &config.value_or_default("CONTROL_AGENT_PLC_DRIVER", RUST_SNAP7_DRIVER),
    );
    let mut read_gate_errors = read_env_errors;
    if !plc_read_allowed {
        read_gate_errors.push("CONTROL_AGENT_PLC_READ_ALLOWED=false".to_string());
    }
    if driver != RUST_SNAP7_DRIVER {
        read_gate_errors.push(format!(
            "CONTROL_AGENT_PLC_DRIVER={} requires {}",
            driver, RUST_SNAP7_DRIVER
        ));
    }
    let mut write_gate_errors = write_env_errors;
    if !plc_write_allowed {
        write_gate_errors.push("CONTROL_AGENT_PLC_WRITE_ALLOWED=false".to_string());
    }
    if plc_write_allowed && !database_enabled {
        write_gate_errors
            .push("CONTROL_AGENT_DATABASE_ENABLED=false while write is enabled".to_string());
    }
    if plc_write_allowed && !database_configured {
        write_gate_errors
            .push("CONTROL_AGENT_DATABASE_URL is empty while write is enabled".to_string());
    }
    if plc_write_allowed && database_read_only {
        write_gate_errors
            .push("CONTROL_AGENT_DATABASE_READ_ONLY=true while write is enabled".to_string());
    }

    PlcCollectionGateSnapshot {
        plc_read_allowed,
        plc_write_allowed,
        autostart_mode,
        read_gate_errors,
        write_gate_errors,
        env_errors,
        collection_enabled: plc_read_allowed,
        write_enabled: plc_write_allowed,
        loop_enabled: config.bool_or_default("CONTROL_AGENT_PLC_COLLECTION_LOOP_ENABLED", false),
        database_enabled,
        database_configured,
        database_read_only,
        driver,
        interval_ms: collection_interval_ms(config),
        collector_key: collection_collector_key(config),
    }
}

pub(crate) fn plc_read_gate_errors(config: &AgentConfig) -> Vec<String> {
    collection_gate_snapshot(config).read_gate_errors
}

pub(crate) fn plc_write_gate_errors(config: &AgentConfig) -> Vec<String> {
    collection_gate_snapshot(config).write_gate_errors
}

pub(crate) fn plc_read_allowed(config: &AgentConfig) -> bool {
    plc_read_gate_errors(config).is_empty()
}

pub(crate) fn plc_sample_read_allowed(config: &AgentConfig) -> bool {
    if !plc_read_allowed(config) {
        return false;
    }

    config
        .raw_value("CONTROL_AGENT_PLC_SAMPLE_READ_ENABLED")
        .map(|value| parse_bool_value(&value).unwrap_or(false))
        .unwrap_or(false)
}

pub(crate) fn plc_write_allowed(config: &AgentConfig) -> bool {
    plc_write_gate_errors(config).is_empty()
}

pub(crate) fn plc_autostart_mode(config: &AgentConfig) -> String {
    collection_gate_snapshot(config).autostart_mode
}

pub(crate) fn plc_autostart_gate_errors(config: &AgentConfig) -> Vec<String> {
    collection_gate_snapshot(config).env_errors
}

fn local_collection_loop_running() -> bool {
    plc_collection_runtime()
        .lock()
        .map(|runtime| !runtime.workers.is_empty())
        .unwrap_or(false)
}

fn sorted_contract_keys(contract: &HashMap<String, PlcRuntimeConfig>) -> Vec<String> {
    let mut keys = contract.keys().cloned().collect::<Vec<_>>();
    keys.sort();
    keys
}

fn selected_plc_keys_for_target(
    contract: &HashMap<String, PlcRuntimeConfig>,
    target: &PlcCollectionTarget,
) -> Result<Vec<String>, String> {
    match target {
        PlcCollectionTarget::All => Ok(sorted_contract_keys(contract)),
        PlcCollectionTarget::PlcKey(plc_key) => {
            if contract.contains_key(plc_key) {
                Ok(vec![plc_key.clone()])
            } else {
                Err(format!("Unknown PLC key '{plc_key}' in plc_points.yaml"))
            }
        }
    }
}

pub(crate) fn validate_plc_key(plc_key: &str) -> Result<(), String> {
    let config = AgentConfig::load();
    let contract = load_runtime_contract(&config)?;
    selected_plc_keys_for_target(&contract, &PlcCollectionTarget::PlcKey(plc_key.to_string()))
        .map(|_| ())
}

fn collection_start_gate_errors(config: &AgentConfig) -> Vec<String> {
    let mut errors = plc_read_gate_errors(config);
    errors.extend(plc_write_gate_errors(config));
    errors
}

fn control_result(
    action: &str,
    target: &str,
    affected_plc_keys: Vec<String>,
    accepted: bool,
    running: bool,
    status: &str,
    message: &str,
    gate_errors: Vec<String>,
) -> PlcCollectionControlResult {
    PlcCollectionControlResult {
        action: action.to_string(),
        target: target.to_string(),
        affected_plc_keys,
        accepted,
        running,
        status: status.to_string(),
        message: message.to_string(),
        gate_errors,
    }
}

fn update_runtime_state(
    states: &Arc<Mutex<HashMap<String, PlcRuntimeUnitState>>>,
    plc_key: &str,
    update: impl FnOnce(&mut PlcRuntimeUnitState),
) {
    let Ok(mut guard) = states.lock() else {
        tracing::error!(
            event = "plc_runtime_state_update_failed",
            plc_key,
            result = "lock_poisoned",
        );
        return;
    };

    let state = guard.entry(plc_key.to_string()).or_default();
    update(state);
    refresh_collection_state(state);
}

fn refresh_collection_state(state: &mut PlcRuntimeUnitState) {
    state.runtime_state = state.read_state.clone();
    state.collection_state = match state.read_state.as_str() {
        "running" => {
            if state.cycle_degraded
                || matches!(state.persistence_state.as_str(), "blocked" | "failed")
            {
                "degraded"
            } else if state.persistence_state == "enabled" {
                "collecting"
            } else {
                "read_only"
            }
        }
        "failed" => "degraded",
        _ => "stopped",
    }
    .to_string();
}

fn group_error_summary(result: &PlcCollectionRunResult) -> String {
    if !result.message.is_empty() {
        return result.message.clone();
    }

    result
        .groups
        .iter()
        .filter(|group| !group.error_message.is_empty())
        .map(|group| format!("{}:{}", group.group_name, group.error_message))
        .collect::<Vec<_>>()
        .join("; ")
}

fn update_runtime_state_from_collection_result(
    states: &Arc<Mutex<HashMap<String, PlcRuntimeUnitState>>>,
    plc_key: &str,
    result: &PlcCollectionRunResult,
    persistence_enabled: bool,
    write_gate_errors: &[String],
) {
    let groups_failed = result
        .groups
        .iter()
        .filter(|group| group.plc_key == plc_key && group.quality == "failed")
        .count()
        .min(u32::MAX as usize) as u32;
    let succeeded = matches!(result.status.as_str(), "succeeded" | "partial");
    let cycle_degraded = result.status != "succeeded";
    let error_summary = group_error_summary(result);
    let timestamp = now_rfc3339();

    update_runtime_state(states, plc_key, |state| {
        state.desired_state = "running".to_string();
        state.read_state = "running".to_string();
        state.persistence_state = if persistence_enabled {
            if write_gate_errors.is_empty() {
                "enabled".to_string()
            } else {
                "blocked".to_string()
            }
        } else {
            "paused".to_string()
        };
        state.collection_status = result.status.clone();
        state.groups_attempted = result.groups_attempted;
        state.groups_succeeded = result.groups_succeeded;
        state.groups_failed = groups_failed;
        state.last_read_duration_ms = result.latency_ms;
        state.cycle_degraded = cycle_degraded || !write_gate_errors.is_empty();

        if succeeded {
            state.last_success_at = timestamp;
            if write_gate_errors.is_empty() {
                state.last_error.clear();
            } else {
                state.last_error = write_gate_errors.join("; ");
            }
        } else {
            state.failure_count = state.failure_count.saturating_add(1);
            state.last_error_at = timestamp;
            state.last_error = if write_gate_errors.is_empty() {
                error_summary
            } else {
                write_gate_errors.join("; ")
            };
        }
    });
}

pub(crate) fn record_plc_sample_read_result(
    plc_key: &str,
    succeeded: bool,
    _latency_ms: u128,
    error_message: &str,
) {
    let state_cache = plc_collection_runtime()
        .lock()
        .map(|runtime| Arc::clone(&runtime.states));

    let Ok(states) = state_cache else {
        tracing::error!(
            event = "plc_sample_state_update_failed",
            plc_key,
            result = "lock_poisoned",
        );
        return;
    };

    update_runtime_state(&states, plc_key, |state| {
        state.sample_status = if succeeded {
            "succeeded".to_string()
        } else {
            "failed".to_string()
        };
        state.last_sample_error = error_message.to_string();
    });
}

fn empty_collector_state(collector_key: String) -> MonitorCollectorStateSnapshot {
    MonitorCollectorStateSnapshot {
        loaded: false,
        collector_key,
        status: "missing".to_string(),
        worker_id: String::new(),
        mode: String::new(),
        target_interval_ms: 0,
        started_at: String::new(),
        last_heartbeat_at: String::new(),
        last_sample_at: String::new(),
        sample_count: 0,
        failure_count: 0,
        last_collect_duration_ms: 0,
        last_write_duration_ms: 0,
        last_loop_delay_ms: 0,
        last_error: String::new(),
    }
}

fn snapshot_state_cache() -> (
    HashMap<String, PlcRuntimeUnitState>,
    HashSet<String>,
    Option<String>,
) {
    let Ok(runtime) = plc_collection_runtime().lock() else {
        return (
            HashMap::new(),
            HashSet::new(),
            Some("plc runtime supervisor lock is poisoned".to_string()),
        );
    };

    let running_keys = runtime.workers.keys().cloned().collect::<HashSet<_>>();
    let states = runtime
        .states
        .lock()
        .map(|guard| guard.clone())
        .unwrap_or_default();

    (states, running_keys, None)
}

fn runtime_status_from_units(units: &[PlcRuntimeUnitSnapshot]) -> String {
    if units.is_empty() {
        return "unknown".to_string();
    }

    if units
        .iter()
        .all(|unit| unit.runtime_state.as_str() == "stopped")
    {
        return "stopped".to_string();
    }

    let degraded_count = units
        .iter()
        .filter(|unit| {
            matches!(unit.collection_state.as_str(), "degraded" | "failed")
                || unit.runtime_state.as_str() == "failed"
                || unit.collection_status.as_str() == "failed"
        })
        .count();

    if degraded_count == units.len() {
        return "failed".to_string();
    }

    if degraded_count > 0 {
        return "partial".to_string();
    }

    if units
        .iter()
        .all(|unit| unit.collection_status.as_str() == "succeeded")
    {
        "all_good".to_string()
    } else {
        "running".to_string()
    }
}

fn build_plc_runtime_units(config: &AgentConfig) -> (Vec<PlcRuntimeUnitSnapshot>, String) {
    let (states, running_keys, cache_error) = snapshot_state_cache();
    let contract = match load_runtime_contract(config) {
        Ok(contract) => contract,
        Err(error) => {
            tracing::warn!(
                event = "plc_runtime_units_contract_failed",
                error = %error,
            );
            return (Vec::new(), "unknown".to_string());
        }
    };
    let endpoints_result = resolve_runtime_endpoints(config, &contract);
    let endpoint_error = endpoints_result.as_ref().err().cloned();
    let endpoints = endpoints_result.unwrap_or_default();
    let mut keys = sorted_contract_keys(&contract);
    let mut units = Vec::new();

    for plc_key in keys.drain(..) {
        let Some(plc) = contract.get(&plc_key) else {
            continue;
        };
        let state = states.get(&plc_key).cloned().unwrap_or_else(|| {
            let mut state = PlcRuntimeUnitState::default();
            if running_keys.contains(&plc_key) {
                state.desired_state = "running".to_string();
                state.read_state = "running".to_string();
                refresh_collection_state(&mut state);
            }
            state
        });
        let endpoint = endpoints.get(&plc_key);
        let endpoint_snapshot = endpoint
            .map(|endpoint| PlcRuntimeEndpointSnapshot {
                host: endpoint.host.clone(),
                port: endpoint.port,
                rack: endpoint.rack,
                slot: endpoint.slot,
            })
            .unwrap_or_else(|| PlcRuntimeEndpointSnapshot {
                host: plc.ip.clone(),
                port: plc.port,
                rack: plc.rack,
                slot: plc.slot,
            });
        let point_count = plc
            .groups
            .iter()
            .map(|group| group.points.len())
            .sum::<usize>()
            .min(u32::MAX as usize) as u32;
        let mut last_error = state.last_error.clone();

        if last_error.is_empty() {
            if let Some(error) = endpoint_error.as_ref().or(cache_error.as_ref()) {
                last_error = error.clone();
            }
        }

        units.push(PlcRuntimeUnitSnapshot {
            plc_key: plc_key.clone(),
            endpoint: endpoint_snapshot,
            desired_state: state.desired_state,
            read_state: state.read_state,
            persistence_state: state.persistence_state,
            collection_state: state.collection_state,
            runtime_state: state.runtime_state,
            sample_status: state.sample_status,
            collection_status: state.collection_status,
            group_count: plc.groups.len().min(u32::MAX as usize) as u32,
            point_count,
            groups_attempted: state.groups_attempted,
            groups_succeeded: state.groups_succeeded,
            groups_failed: state.groups_failed,
            last_success_at: state.last_success_at,
            last_error_at: state.last_error_at,
            failure_count: state.failure_count,
            last_error,
            last_sample_error: state.last_sample_error,
            last_read_duration_ms: state.last_read_duration_ms,
        });
    }

    let runtime_status = runtime_status_from_units(&units);

    (units, runtime_status)
}

async fn read_plc_collection_status_async(
    config: &AgentConfig,
) -> Result<PlcCollectionStatusSnapshot, String> {
    let gates = collection_gate_snapshot(config);
    let collector_key = gates.collector_key.clone();
    let snapshot_policy = read_plc_snapshot_policy_status(config);
    let (plc_units, runtime_status) = build_plc_runtime_units(config);

    if !gates.database_enabled {
        return Ok(PlcCollectionStatusSnapshot {
            loaded: false,
            local_loop_running: local_collection_loop_running(),
            runtime_status,
            raw_snapshot_count: 0,
            latest_group_count: 0,
            gates,
            collector_state: empty_collector_state(collector_key),
            snapshot_policy,
            plc_units,
            latest_groups: Vec::new(),
            error_message: "Database access is disabled for collection status.".to_string(),
        });
    }

    if !gates.database_configured {
        return Ok(PlcCollectionStatusSnapshot {
            loaded: false,
            local_loop_running: local_collection_loop_running(),
            runtime_status,
            raw_snapshot_count: 0,
            latest_group_count: 0,
            gates,
            collector_state: empty_collector_state(collector_key),
            snapshot_policy,
            plc_units,
            latest_groups: Vec::new(),
            error_message: "Database URL is not configured for collection status.".to_string(),
        });
    }

    let database_url = config.value_or_default("CONTROL_AGENT_DATABASE_URL", "");
    let database_timeout_ms = parse_u64_or_default(
        &config.value_or_default("CONTROL_AGENT_DATABASE_CONNECT_TIMEOUT_MS", "1500"),
        1500,
    );
    let status_rows =
        read_plc_collection_database_status(&database_url, database_timeout_ms, &collector_key)
            .await?;
    let raw_snapshot_count = status_rows.raw_snapshot_count;
    let latest_groups = status_rows.latest_groups;
    let latest_group_count = latest_groups.len().min(u32::MAX as usize) as u32;

    Ok(PlcCollectionStatusSnapshot {
        loaded: true,
        local_loop_running: local_collection_loop_running(),
        runtime_status,
        raw_snapshot_count,
        latest_group_count,
        gates,
        collector_state: status_rows.collector_state,
        snapshot_policy,
        plc_units,
        latest_groups,
        error_message: String::new(),
    })
}

pub(crate) fn read_plc_collection_status(config: &AgentConfig) -> PlcCollectionStatusSnapshot {
    let gates = collection_gate_snapshot(config);
    let collector_key = gates.collector_key.clone();
    let (plc_units, runtime_status) = build_plc_runtime_units(config);

    match tauri::async_runtime::block_on(read_plc_collection_status_async(config)) {
        Ok(snapshot) => snapshot,
        Err(error) => PlcCollectionStatusSnapshot {
            loaded: false,
            local_loop_running: local_collection_loop_running(),
            runtime_status,
            raw_snapshot_count: 0,
            latest_group_count: 0,
            gates,
            collector_state: empty_collector_state(collector_key),
            snapshot_policy: read_plc_snapshot_policy_status(config),
            plc_units,
            latest_groups: Vec::new(),
            error_message: error,
        },
    }
}

fn collection_status_for_collector(result: &PlcCollectionRunResult) -> String {
    match result.status.as_str() {
        "succeeded" | "partial" => "running".to_string(),
        "disabled" => "stopped".to_string(),
        _ => "error".to_string(),
    }
}

fn collection_error_for_collector(result: &PlcCollectionRunResult) -> Option<String> {
    if !result.message.is_empty() {
        return Some(result.message.clone());
    }

    let errors = result
        .groups
        .iter()
        .filter(|group| !group.error_message.is_empty())
        .map(|group| format!("{}:{}", group.group_name, group.error_message))
        .collect::<Vec<_>>();

    if errors.is_empty() {
        None
    } else {
        Some(errors.join("; "))
    }
}

fn sleep_until_next_tick(stop_requested: &AtomicBool, interval_ms: u64, elapsed: Duration) {
    let elapsed_ms = elapsed.as_millis().min(u64::MAX as u128) as u64;
    let remaining_ms = interval_ms.saturating_sub(elapsed_ms);
    let mut slept_ms = 0_u64;

    while slept_ms < remaining_ms && !stop_requested.load(Ordering::Relaxed) {
        let step_ms = (remaining_ms - slept_ms).min(250);
        thread::sleep(Duration::from_millis(step_ms));
        slept_ms = slept_ms.saturating_add(step_ms);
    }
}

fn persistence_enabled_for_plc(
    states: &Arc<Mutex<HashMap<String, PlcRuntimeUnitState>>>,
    plc_key: &str,
) -> bool {
    states
        .lock()
        .ok()
        .and_then(|guard| {
            guard
                .get(plc_key)
                .map(|state| state.persistence_state == "enabled")
        })
        .unwrap_or(false)
}

fn run_plc_worker_thread(
    plc_key: String,
    stop_requested: Arc<AtomicBool>,
    states: Arc<Mutex<HashMap<String, PlcRuntimeUnitState>>>,
    persistence_on_start: bool,
) {
    let config = AgentConfig::load();
    let interval_ms = collection_interval_ms(&config);
    let max_consecutive_failures = parse_u64_or_default(
        &config.value_or_default(
            "CONTROL_AGENT_PLC_COLLECTION_MAX_CONSECUTIVE_FAILURES",
            "10",
        ),
        10,
    )
    .clamp(1, u32::MAX as u64) as u32;
    let mut ticks = 0_u32;
    let mut consecutive_failures = 0_u32;

    update_runtime_state(&states, &plc_key, |state| {
        state.desired_state = "running".to_string();
        state.read_state = "running".to_string();
        state.persistence_state = if persistence_on_start {
            "enabled".to_string()
        } else {
            "paused".to_string()
        };
        state.collection_status = "starting".to_string();
        state.cycle_degraded = false;
    });

    tracing::info!(
        event = "plc_collection_worker_started",
        plc_key = %plc_key,
        collector_key = %collection_collector_key(&config),
        interval_ms,
        result = "accepted",
    );

    while !stop_requested.load(Ordering::Relaxed) {
        let loop_started_at = Instant::now();
        let persistence_enabled = persistence_enabled_for_plc(&states, &plc_key);
        let write_gate_errors = if persistence_enabled {
            plc_write_gate_errors(&config)
        } else {
            Vec::new()
        };
        let result = match tauri::async_runtime::block_on(collect_plc_db_blocks_once_for_plc_async(
            &config,
            &plc_key,
            persistence_enabled,
        )) {
            Ok(result) => result,
            Err(error) => failed_result(
                true,
                persistence_enabled,
                normalize_plc_driver(
                    &config.value_or_default("CONTROL_AGENT_PLC_DRIVER", RUST_SNAP7_DRIVER),
                ),
                loop_started_at.elapsed().as_millis(),
                error,
            ),
        };

        ticks = ticks.saturating_add(1);
        if matches!(result.status.as_str(), "succeeded" | "partial") {
            consecutive_failures = 0;
        } else {
            consecutive_failures = consecutive_failures.saturating_add(1);
        }
        update_runtime_state_from_collection_result(
            &states,
            &plc_key,
            &result,
            persistence_enabled,
            &write_gate_errors,
        );

        tracing::info!(
            event = "plc_collection_worker_tick",
            plc_key = %plc_key,
            tick = ticks,
            status = %result.status,
            groups_attempted = result.groups_attempted,
            raw_snapshots_written = result.raw_snapshots_written,
            consecutive_failures,
        );

        if consecutive_failures >= max_consecutive_failures {
            tracing::warn!(
                event = "plc_collection_worker_degraded",
                plc_key = %plc_key,
                consecutive_failures,
                max_consecutive_failures,
            );
        }

        sleep_until_next_tick(&stop_requested, interval_ms, loop_started_at.elapsed());
    }

    update_runtime_state(&states, &plc_key, |state| {
        state.desired_state = "stopped".to_string();
        state.read_state = "stopped".to_string();
        state.persistence_state = "paused".to_string();
        state.collection_status = "stopped".to_string();
        state.cycle_degraded = false;
    });

    tracing::info!(
        event = "plc_collection_worker_stopped",
        plc_key = %plc_key,
        ticks,
        result = "stopped",
    );
}

fn start_plc_read_for_target(
    target: PlcCollectionTarget,
    persistence_on_start: bool,
    action_override: Option<&str>,
) -> PlcCollectionControlResult {
    let config = AgentConfig::load();
    let target_label = target.label();
    let action = action_override.unwrap_or(if persistence_on_start {
        "start_collection"
    } else {
        "start_read"
    });
    let gate_errors = if persistence_on_start {
        collection_start_gate_errors(&config)
    } else {
        plc_read_gate_errors(&config)
    };

    if !gate_errors.is_empty() {
        tracing::warn!(
            event = "plc_collection_ui_start_rejected",
            target = %target_label,
            gate_errors = ?gate_errors,
            result = "rejected",
        );

        return control_result(
            action,
            &target_label,
            Vec::new(),
            false,
            local_collection_loop_running(),
            "blocked",
            "blocked_by_runtime_gates",
            gate_errors,
        );
    }

    let contract = match load_runtime_contract(&config) {
        Ok(contract) => contract,
        Err(error) => {
            tracing::error!(
                event = "plc_collection_ui_start_failed",
                error = %error,
                target = %target_label,
                result = "contract_failed",
            );
            return control_result(
                action,
                &target_label,
                Vec::new(),
                false,
                local_collection_loop_running(),
                "failed",
                &error,
                Vec::new(),
            );
        }
    };
    let selected_keys = match selected_plc_keys_for_target(&contract, &target) {
        Ok(keys) => keys,
        Err(error) => {
            tracing::warn!(
                event = "plc_collection_ui_start_rejected",
                error = %error,
                target = %target_label,
                result = "unknown_plc",
            );
            return control_result(
                action,
                &target_label,
                Vec::new(),
                false,
                local_collection_loop_running(),
                "failed",
                &error,
                Vec::new(),
            );
        }
    };

    let Ok(mut runtime) = plc_collection_runtime().lock() else {
        tracing::error!(
            event = "plc_collection_ui_start_failed",
            target = %target_label,
            result = "lock_poisoned",
        );
        return control_result(
            action,
            &target_label,
            Vec::new(),
            false,
            false,
            "failed",
            "lock_failed",
            Vec::new(),
        );
    };

    let states = Arc::clone(&runtime.states);
    let mut affected_plc_keys = Vec::new();
    let mut spawn_errors = Vec::new();

    for plc_key in selected_keys {
        if runtime.workers.contains_key(&plc_key) {
            if persistence_on_start {
                update_runtime_state(&states, &plc_key, |state| {
                    state.persistence_state = "enabled".to_string();
                    state.cycle_degraded = false;
                });
                affected_plc_keys.push(plc_key);
            }
            continue;
        }

        update_runtime_state(&states, &plc_key, |state| {
            state.desired_state = "running".to_string();
            state.read_state = "starting".to_string();
            state.persistence_state = if persistence_on_start {
                "enabled".to_string()
            } else {
                "paused".to_string()
            };
            state.runtime_state = "starting".to_string();
            state.collection_status = "starting".to_string();
        });

        let stop_requested = Arc::new(AtomicBool::new(false));
        let thread_stop_requested = Arc::clone(&stop_requested);
        let thread_states = Arc::clone(&states);
        let thread_plc_key = plc_key.clone();
        let thread = match thread::Builder::new()
            .name(format!("plc-collection-{plc_key}"))
            .spawn(move || {
                run_plc_worker_thread(
                    thread_plc_key,
                    thread_stop_requested,
                    thread_states,
                    persistence_on_start,
                )
            }) {
            Ok(thread) => thread,
            Err(error) => {
                let message = format!("{plc_key}: spawn_failed: {error}");
                spawn_errors.push(message.clone());
                update_runtime_state(&states, &plc_key, |state| {
                    state.desired_state = "running".to_string();
                    state.read_state = "failed".to_string();
                    state.persistence_state = "paused".to_string();
                    state.runtime_state = "failed".to_string();
                    state.collection_status = "failed".to_string();
                    state.last_error = message;
                    state.last_error_at = now_rfc3339();
                    state.failure_count = state.failure_count.saturating_add(1);
                });
                continue;
            }
        };

        runtime.workers.insert(
            plc_key.clone(),
            PlcWorkerHandle {
                stop_requested,
                thread,
            },
        );
        affected_plc_keys.push(plc_key);
    }

    let running = !runtime.workers.is_empty();

    tracing::info!(
        event = "plc_collection_ui_start_accepted",
        target = %target_label,
        affected_plc_keys = ?affected_plc_keys,
        collector_key = %collection_collector_key(&config),
        interval_ms = collection_interval_ms(&config),
        result = "accepted",
    );

    if affected_plc_keys.is_empty() && spawn_errors.is_empty() {
        return control_result(
            action,
            &target_label,
            Vec::new(),
            false,
            running,
            "already_running",
            "already_running",
            Vec::new(),
        );
    }

    if !spawn_errors.is_empty() {
        let accepted = !affected_plc_keys.is_empty();
        return control_result(
            action,
            &target_label,
            affected_plc_keys,
            accepted,
            running,
            "partial",
            &spawn_errors.join("; "),
            Vec::new(),
        );
    }

    control_result(
        action,
        &target_label,
        affected_plc_keys,
        true,
        true,
        "started",
        "started",
        Vec::new(),
    )
}

pub(crate) fn start_plc_read_from_console() -> PlcCollectionControlResult {
    start_plc_read_for_target(PlcCollectionTarget::All, false, None)
}

pub(crate) fn start_plc_read_for_plc_from_console(plc_key: String) -> PlcCollectionControlResult {
    start_plc_read_for_target(PlcCollectionTarget::PlcKey(plc_key), false, None)
}

pub(crate) fn start_plc_collection_from_console() -> PlcCollectionControlResult {
    start_plc_read_for_target(PlcCollectionTarget::All, true, None)
}

pub(crate) fn start_plc_collection_for_plc_from_console(
    plc_key: String,
) -> PlcCollectionControlResult {
    start_plc_read_for_target(PlcCollectionTarget::PlcKey(plc_key), true, None)
}

pub(crate) fn start_plc_collection_loop_from_console() -> PlcCollectionControlResult {
    start_plc_read_for_target(PlcCollectionTarget::All, false, Some("start"))
}

pub(crate) fn start_plc_collection_loop_for_plc_from_console(
    plc_key: String,
) -> PlcCollectionControlResult {
    start_plc_read_for_target(PlcCollectionTarget::PlcKey(plc_key), false, Some("start"))
}

fn stop_plc_read_for_target(
    target: PlcCollectionTarget,
    action: &str,
) -> PlcCollectionControlResult {
    let target_label = target.label();
    let (handles, states, remaining_running) = {
        let Ok(mut runtime) = plc_collection_runtime().lock() else {
            tracing::error!(
                event = "plc_collection_ui_stop_failed",
                target = %target_label,
                result = "lock_poisoned",
            );
            return control_result(
                action,
                &target_label,
                Vec::new(),
                false,
                false,
                "failed",
                "lock_failed",
                Vec::new(),
            );
        };

        let selected_keys = match &target {
            PlcCollectionTarget::All => {
                let mut keys = runtime.workers.keys().cloned().collect::<Vec<_>>();
                keys.sort();
                keys
            }
            PlcCollectionTarget::PlcKey(plc_key) => vec![plc_key.clone()],
        };

        let states = Arc::clone(&runtime.states);
        let mut handles = Vec::new();

        for plc_key in selected_keys {
            if let Some(handle) = runtime.workers.remove(&plc_key) {
                update_runtime_state(&states, &plc_key, |state| {
                    state.desired_state = "stopped".to_string();
                    state.persistence_state = "paused".to_string();
                    state.read_state = "stopping".to_string();
                    state.runtime_state = "stopping".to_string();
                    state.collection_status = "stopping".to_string();
                });
                handles.push((plc_key, handle));
            }
        }

        let remaining_running = !runtime.workers.is_empty();

        (handles, states, remaining_running)
    };

    if handles.is_empty() {
        if let PlcCollectionTarget::PlcKey(plc_key) = &target {
            let config = AgentConfig::load();
            let target_error = load_runtime_contract(&config)
                .and_then(|contract| selected_plc_keys_for_target(&contract, &target).map(|_| ()))
                .err();

            if let Some(error) = target_error {
                tracing::warn!(
                    event = "plc_collection_ui_stop_rejected",
                    plc_key = %plc_key,
                    error = %error,
                    result = "unknown_plc",
                );
                return control_result(
                    action,
                    &target_label,
                    Vec::new(),
                    false,
                    local_collection_loop_running(),
                    "failed",
                    &error,
                    Vec::new(),
                );
            }
        }

        return control_result(
            action,
            &target_label,
            Vec::new(),
            false,
            local_collection_loop_running(),
            "not_running",
            "not_running",
            Vec::new(),
        );
    };

    let mut affected_plc_keys = Vec::new();
    let mut join_errors = Vec::new();

    for (plc_key, handle) in handles {
        handle.stop_requested.store(true, Ordering::Relaxed);
        if handle.thread.join().is_err() {
            let message = format!("{plc_key}: thread_join_failed");
            join_errors.push(message.clone());
            update_runtime_state(&states, &plc_key, |state| {
                state.desired_state = "stopped".to_string();
                state.persistence_state = "paused".to_string();
                state.read_state = "failed".to_string();
                state.runtime_state = "failed".to_string();
                state.collection_status = "failed".to_string();
                state.last_error = message;
                state.last_error_at = now_rfc3339();
                state.failure_count = state.failure_count.saturating_add(1);
            });
        } else {
            update_runtime_state(&states, &plc_key, |state| {
                state.desired_state = "stopped".to_string();
                state.persistence_state = "paused".to_string();
                state.read_state = "stopped".to_string();
                state.runtime_state = "stopped".to_string();
                state.collection_status = "stopped".to_string();
            });
        }
        affected_plc_keys.push(plc_key);
    }

    tracing::info!(
        event = "plc_collection_ui_stop_accepted",
        target = %target_label,
        affected_plc_keys = ?affected_plc_keys,
        result = "stopped",
    );

    if action != "stop_read" && !remaining_running && join_errors.is_empty() {
        if let Err(error) = mark_collector_stopped_from_console() {
            tracing::warn!(
                event = "plc_collection_ui_stop_state_write_failed",
                error = %error,
            );
        }
    }

    if !join_errors.is_empty() {
        tracing::warn!(
            event = "plc_collection_ui_stop_failed",
            target = %target_label,
            errors = ?join_errors,
            result = "thread_join_failed",
        );
        return control_result(
            action,
            &target_label,
            affected_plc_keys,
            false,
            local_collection_loop_running(),
            "failed",
            &join_errors.join("; "),
            Vec::new(),
        );
    }

    control_result(
        action,
        &target_label,
        affected_plc_keys,
        true,
        local_collection_loop_running(),
        "stopped",
        "stopped",
        Vec::new(),
    )
}

pub(crate) fn stop_plc_read_from_console() -> PlcCollectionControlResult {
    stop_plc_read_for_target(PlcCollectionTarget::All, "stop_read")
}

pub(crate) fn stop_plc_read_for_plc_from_console(plc_key: String) -> PlcCollectionControlResult {
    stop_plc_read_for_target(PlcCollectionTarget::PlcKey(plc_key), "stop_read")
}

pub(crate) fn stop_plc_collection_from_console() -> PlcCollectionControlResult {
    stop_plc_read_for_target(PlcCollectionTarget::All, "stop_collection")
}

pub(crate) fn stop_plc_collection_for_plc_from_console(
    plc_key: String,
) -> PlcCollectionControlResult {
    stop_plc_read_for_target(PlcCollectionTarget::PlcKey(plc_key), "stop_collection")
}

pub(crate) fn stop_plc_collection_loop_from_console() -> PlcCollectionControlResult {
    stop_plc_read_for_target(PlcCollectionTarget::All, "stop")
}

pub(crate) fn stop_plc_collection_loop_for_plc_from_console(
    plc_key: String,
) -> PlcCollectionControlResult {
    stop_plc_read_for_target(PlcCollectionTarget::PlcKey(plc_key), "stop")
}

fn set_plc_persistence_for_target(
    target: PlcCollectionTarget,
    enabled: bool,
) -> PlcCollectionControlResult {
    let config = AgentConfig::load();
    let target_label = target.label();
    let action = if enabled {
        "enable_persistence"
    } else {
        "pause_persistence"
    };

    if enabled {
        let gate_errors = plc_write_gate_errors(&config);
        if !gate_errors.is_empty() {
            return control_result(
                action,
                &target_label,
                Vec::new(),
                false,
                local_collection_loop_running(),
                "blocked",
                "blocked_by_write_gate",
                gate_errors,
            );
        }
    }

    let contract = match load_runtime_contract(&config) {
        Ok(contract) => contract,
        Err(error) => {
            return control_result(
                action,
                &target_label,
                Vec::new(),
                false,
                local_collection_loop_running(),
                "failed",
                &error,
                Vec::new(),
            )
        }
    };
    let selected_keys = match selected_plc_keys_for_target(&contract, &target) {
        Ok(keys) => keys,
        Err(error) => {
            return control_result(
                action,
                &target_label,
                Vec::new(),
                false,
                local_collection_loop_running(),
                "failed",
                &error,
                Vec::new(),
            )
        }
    };

    let Ok(runtime) = plc_collection_runtime().lock() else {
        return control_result(
            action,
            &target_label,
            Vec::new(),
            false,
            false,
            "failed",
            "lock_failed",
            Vec::new(),
        );
    };

    let states = Arc::clone(&runtime.states);
    let Ok(mut state_guard) = states.lock() else {
        return control_result(
            action,
            &target_label,
            Vec::new(),
            false,
            !runtime.workers.is_empty(),
            "failed",
            "state_lock_failed",
            Vec::new(),
        );
    };
    let mut affected_plc_keys = Vec::new();
    let mut rejections = Vec::new();

    for plc_key in selected_keys {
        let state = state_guard.entry(plc_key.clone()).or_default();
        if enabled {
            if !runtime.workers.contains_key(&plc_key) || state.read_state != "running" {
                rejections.push(format!("{plc_key}: read_not_running"));
                continue;
            }
            if state.persistence_state != "enabled" {
                state.persistence_state = "enabled".to_string();
                state.cycle_degraded = false;
                affected_plc_keys.push(plc_key);
            }
        } else {
            if state.persistence_state != "paused" {
                state.persistence_state = "paused".to_string();
                state.cycle_degraded = false;
                affected_plc_keys.push(plc_key);
            }
        }
        refresh_collection_state(state);
    }

    let running = !runtime.workers.is_empty();
    drop(state_guard);
    drop(runtime);

    if enabled && !rejections.is_empty() && affected_plc_keys.is_empty() {
        return control_result(
            action,
            &target_label,
            affected_plc_keys,
            false,
            running,
            "not_running",
            &rejections.join("; "),
            rejections,
        );
    }
    if !rejections.is_empty() {
        return control_result(
            action,
            &target_label,
            affected_plc_keys,
            true,
            running,
            "partial",
            &rejections.join("; "),
            rejections,
        );
    }

    let status = if affected_plc_keys.is_empty() {
        if enabled {
            "already_enabled"
        } else {
            "already_paused"
        }
    } else if enabled {
        "enabled"
    } else {
        "paused"
    };
    control_result(
        action,
        &target_label,
        affected_plc_keys,
        true,
        running,
        status,
        status,
        Vec::new(),
    )
}

pub(crate) fn enable_plc_persistence_from_console() -> PlcCollectionControlResult {
    set_plc_persistence_for_target(PlcCollectionTarget::All, true)
}

pub(crate) fn enable_plc_persistence_for_plc_from_console(
    plc_key: String,
) -> PlcCollectionControlResult {
    set_plc_persistence_for_target(PlcCollectionTarget::PlcKey(plc_key), true)
}

pub(crate) fn pause_plc_persistence_from_console() -> PlcCollectionControlResult {
    set_plc_persistence_for_target(PlcCollectionTarget::All, false)
}

pub(crate) fn pause_plc_persistence_for_plc_from_console(
    plc_key: String,
) -> PlcCollectionControlResult {
    set_plc_persistence_for_target(PlcCollectionTarget::PlcKey(plc_key), false)
}

fn mark_collector_stopped_from_console() -> Result<(), String> {
    let config = AgentConfig::load();

    if !plc_write_allowed(&config) {
        return Ok(());
    }

    tauri::async_runtime::block_on(mark_collector_stopped_async(&config))
}

async fn mark_collector_stopped_async(config: &AgentConfig) -> Result<(), String> {
    let database_url = config.value_or_default("CONTROL_AGENT_DATABASE_URL", "");
    let database_timeout_ms = parse_u64_or_default(
        &config.value_or_default("CONTROL_AGENT_DATABASE_CONNECT_TIMEOUT_MS", "1500"),
        1500,
    );
    let db = PlcCollectionDatabaseWriter::connect(&database_url, database_timeout_ms).await?;
    let now = db.database_now().await?;

    db.upsert_collector_state(NewMonitorCollectorState {
        collector_key: collection_collector_key(config),
        status: "stopped".to_string(),
        worker_id: Some(
            config.value_or_default("CONTROL_AGENT_EXECUTOR_ID", "control-agent-local"),
        ),
        mode: "plc".to_string(),
        device_id: collection_device_id(config),
        target_interval_ms: collection_interval_ms(config).min(i32::MAX as u64) as i32,
        last_heartbeat_at: now,
        last_sample_at: None,
        sample_succeeded: false,
        failure_count_increment: 0,
        last_collect_duration_ms: None,
        last_write_duration_ms: None,
        last_loop_delay_ms: None,
        last_error: None,
    })
    .await
}

pub(crate) fn smoke_plc_collection_loop_from_console() -> PlcCollectionControlSmokeResult {
    let config = AgentConfig::load();
    let requested_ticks = 2;
    let before = read_plc_collection_status(&config);
    let wait_ms = collection_interval_ms(&config)
        .saturating_mul(requested_ticks as u64)
        .saturating_add(1_000)
        .min(30_000);

    let start_result = start_plc_collection_from_console();
    if start_result.accepted {
        thread::sleep(Duration::from_millis(wait_ms));
    }
    let stop_result = stop_plc_collection_from_console();
    let after = read_plc_collection_status(&config);
    let raw_count_delta = after
        .raw_snapshot_count
        .saturating_sub(before.raw_snapshot_count);
    let collector_sample_delta = after
        .collector_state
        .sample_count
        .saturating_sub(before.collector_state.sample_count);
    let minimum_raw_delta = after
        .latest_group_count
        .max(1)
        .saturating_mul(requested_ticks);
    let succeeded = start_result.accepted
        && stop_result.accepted
        && raw_count_delta >= minimum_raw_delta
        && collector_sample_delta >= requested_ticks;

    let status = if succeeded { "succeeded" } else { "failed" };
    let message = if succeeded {
        "collection_loop_smoke_passed"
    } else if !start_result.accepted {
        "collection_loop_start_failed"
    } else if !stop_result.accepted {
        "collection_loop_stop_failed"
    } else {
        "collection_loop_did_not_reach_expected_ticks"
    };

    tracing::info!(
        event = "plc_collection_ui_loop_smoke",
        status,
        requested_ticks,
        wait_ms,
        raw_count_delta,
        collector_sample_delta,
    );

    PlcCollectionControlSmokeResult {
        status: status.to_string(),
        message: message.to_string(),
        requested_ticks,
        wait_ms,
        raw_count_before: before.raw_snapshot_count,
        raw_count_after: after.raw_snapshot_count,
        latest_count_before: before.latest_group_count,
        latest_count_after: after.latest_group_count,
        collector_sample_before: before.collector_state.sample_count,
        collector_sample_after: after.collector_state.sample_count,
        raw_count_delta,
        collector_sample_delta,
        start_result,
        stop_result,
    }
}

async fn write_collector_state(
    config: &AgentConfig,
    result: &PlcCollectionRunResult,
    write_duration_ms: Option<i32>,
    loop_delay_ms: Option<i32>,
) -> Result<(), String> {
    if !result.write_enabled || !plc_write_allowed(config) {
        return Ok(());
    }

    if config.bool_or_default("CONTROL_AGENT_DATABASE_READ_ONLY", true) {
        return Ok(());
    }

    let database_url = config.value_or_default("CONTROL_AGENT_DATABASE_URL", "");
    if database_url.trim().is_empty() {
        return Ok(());
    }

    let database_timeout_ms = parse_u64_or_default(
        &config.value_or_default("CONTROL_AGENT_DATABASE_CONNECT_TIMEOUT_MS", "1500"),
        1500,
    );
    let db = PlcCollectionDatabaseWriter::connect(&database_url, database_timeout_ms).await?;
    let now = db.database_now().await?;
    let sample_succeeded = matches!(result.status.as_str(), "succeeded" | "partial");

    db.upsert_collector_state(NewMonitorCollectorState {
        collector_key: collection_collector_key(config),
        status: collection_status_for_collector(result),
        worker_id: Some(
            config.value_or_default("CONTROL_AGENT_EXECUTOR_ID", "control-agent-local"),
        ),
        mode: "plc".to_string(),
        device_id: collection_device_id(config),
        target_interval_ms: collection_interval_ms(config).min(i32::MAX as u64) as i32,
        last_heartbeat_at: now,
        last_sample_at: if sample_succeeded { Some(now) } else { None },
        sample_succeeded,
        failure_count_increment: if sample_succeeded { 0 } else { 1 },
        last_collect_duration_ms: Some(result.latency_ms.min(i32::MAX as u128) as i32),
        last_write_duration_ms: write_duration_ms,
        last_loop_delay_ms: loop_delay_ms,
        last_error: collection_error_for_collector(result),
    })
    .await
}

async fn collect_plc_db_blocks_once_for_target_async(
    config: &AgentConfig,
    target: &PlcCollectionTarget,
    persistence_enabled: bool,
) -> Result<PlcCollectionRunResult, String> {
    let enabled = plc_read_allowed(config);
    let write_enabled = persistence_enabled;
    let driver = normalize_plc_driver(
        &config.value_or_default("CONTROL_AGENT_PLC_DRIVER", RUST_SNAP7_DRIVER),
    );

    if !enabled {
        return Ok(disabled_result(
            enabled,
            write_enabled,
            driver,
            "PLC DB block collection is disabled".to_string(),
        ));
    }

    if driver != RUST_SNAP7_DRIVER {
        return Ok(failed_result(
            enabled,
            write_enabled,
            driver,
            0,
            "PLC DB block collection currently requires CONTROL_AGENT_PLC_DRIVER=rust_snap7"
                .to_string(),
        ));
    }

    if write_enabled {
        let write_gate_errors = plc_write_gate_errors(config);
        if !write_gate_errors.is_empty() {
            return Ok(failed_result(
                enabled,
                write_enabled,
                driver,
                0,
                write_gate_errors.join("; "),
            ));
        }
    }

    let started_at = Instant::now();
    let mut contract = load_runtime_contract(config)?;
    let endpoints = resolve_runtime_endpoints(config, &contract)?;
    let selected_plc_keys = selected_plc_keys_for_target(&contract, target)?;
    let database_url = config.value_or_default("CONTROL_AGENT_DATABASE_URL", "");
    let database_timeout_ms = parse_u64_or_default(
        &config.value_or_default("CONTROL_AGENT_DATABASE_CONNECT_TIMEOUT_MS", "1500"),
        1500,
    );
    let db = if write_enabled {
        Some(PlcCollectionDatabaseWriter::connect(&database_url, database_timeout_ms).await?)
    } else {
        None
    };
    let snapshot_policy_filter = if write_enabled {
        read_plc_snapshot_payload_policy_filter(config)?
    } else {
        None
    };
    let device_id = parse_u64_or_default(
        &config.value_or_default("CONTROL_AGENT_PLC_COLLECTION_DEVICE_ID", "1"),
        1,
    )
    .min(i32::MAX as u64) as i32;
    let contract_version = config.value_or_default("CONTROL_AGENT_PLC_CONTRACT_VERSION", "local");
    let timeout_ms = parse_u64_or_default(
        &config.value_or_default("CONTROL_AGENT_PLC_CONNECT_TIMEOUT_MS", "500"),
        500,
    );
    let timeout = Duration::from_millis(timeout_ms);
    let mut groups = Vec::new();
    let mut groups_attempted = 0;
    let mut groups_succeeded = 0;
    let mut groups_partial = 0;
    let mut raw_snapshots_written = 0;
    let mut latest_snapshots_written = 0;
    let mut write_duration_ms = 0_u128;

    for plc_key in selected_plc_keys {
        let plc = contract
            .remove(&plc_key)
            .ok_or_else(|| format!("Missing PLC contract for configured key '{plc_key}'"))?;
        let resolved_endpoint = endpoints.get(&plc_key).ok_or_else(|| {
            format!("Missing resolved PLC endpoint for configured key '{plc_key}'")
        })?;
        let endpoint = PlcEndpointProbeSnapshot {
            host: resolved_endpoint.host.clone(),
            port: resolved_endpoint.port,
            rack: resolved_endpoint.rack,
            slot: resolved_endpoint.slot,
            enabled: true,
            reachable: false,
            latency_ms: 0,
            error_message: String::new(),
        };

        for group in plc.groups {
            groups_attempted += 1;
            let group_started_at = Instant::now();
            let collected_at = if let Some(db) = &db {
                db.database_now().await?
            } else {
                Utc::now().naive_utc()
            };

            let read_result = rust_snap7_adapter::read_db_block(
                &endpoint,
                group.db_number,
                group.start,
                group.size,
                timeout,
            );

            let (
                quality,
                raw_bytes,
                decoded_payload,
                unsupported_payload,
                decoded_count,
                unsupported_count,
                error_message,
            ) = match read_result {
                Ok(bytes) => {
                    let (decoded, unsupported, decoded_count, unsupported_count) =
                        decode_group_payload(&group, &bytes);
                    let quality = if unsupported_count == 0 {
                        "good"
                    } else {
                        "partial"
                    };
                    (
                        quality.to_string(),
                        Some(bytes),
                        decoded,
                        unsupported,
                        decoded_count,
                        unsupported_count,
                        None,
                    )
                }
                Err(error) => (
                    "failed".to_string(),
                    None,
                    json!({}),
                    None,
                    0,
                    0,
                    Some(error),
                ),
            };

            let read_duration_ms = group_started_at.elapsed().as_millis();
            let mut raw_snapshot_id = None;

            if let Some(db) = &db {
                let write_started_at = Instant::now();
                let raw_decoded_payload = filter_payload_for_snapshot_policy(
                    &decoded_payload,
                    snapshot_policy_filter.as_ref(),
                    &plc_key,
                    group.db_number,
                    &group.name,
                    SnapshotPayloadScope::Raw,
                );
                let raw_unsupported_payload = filter_optional_payload_for_snapshot_policy(
                    &unsupported_payload,
                    snapshot_policy_filter.as_ref(),
                    &plc_key,
                    group.db_number,
                    &group.name,
                    SnapshotPayloadScope::Raw,
                );
                let latest_decoded_payload = filter_payload_for_snapshot_policy(
                    &decoded_payload,
                    snapshot_policy_filter.as_ref(),
                    &plc_key,
                    group.db_number,
                    &group.name,
                    SnapshotPayloadScope::Latest,
                );
                let latest_unsupported_payload = filter_optional_payload_for_snapshot_policy(
                    &unsupported_payload,
                    snapshot_policy_filter.as_ref(),
                    &plc_key,
                    group.db_number,
                    &group.name,
                    SnapshotPayloadScope::Latest,
                );
                let snapshot = NewPlcDbBlockSnapshot {
                    plc_key: plc_key.clone(),
                    device_id,
                    db_number: group.db_number as i32,
                    group_name: group.name.clone(),
                    contract_version: contract_version.clone(),
                    collected_at,
                    driver: driver.clone(),
                    quality: quality.clone(),
                    read_duration_ms: read_duration_ms.min(i32::MAX as u128) as i32,
                    raw_bytes: raw_bytes.clone(),
                    decoded_payload: raw_decoded_payload,
                    unsupported_payload: raw_unsupported_payload,
                    latest_decoded_payload,
                    latest_unsupported_payload,
                    error_message: error_message.clone(),
                };
                let inserted_id = db.write_snapshot(snapshot).await?;
                write_duration_ms += write_started_at.elapsed().as_millis();
                raw_snapshot_id = Some(inserted_id);
                raw_snapshots_written += 1;
                latest_snapshots_written += 1;
            }

            if quality != "failed" {
                groups_succeeded += 1;
            }
            if quality == "partial" {
                groups_partial += 1;
            }

            groups.push(PlcDbBlockGroupCollectResult {
                plc_key: plc_key.clone(),
                group_name: group.name,
                db_number: group.db_number,
                quality,
                point_count: group.points.len() as u32,
                decoded_count,
                unsupported_count,
                read_duration_ms,
                raw_snapshot_id,
                error_message: error_message.unwrap_or_default(),
            });
        }
    }

    let status = if groups_attempted == 0 {
        "empty"
    } else if groups_partial > 0 {
        "partial"
    } else if groups_succeeded == groups_attempted {
        "succeeded"
    } else if groups_succeeded == 0 {
        "failed"
    } else {
        "partial"
    };

    let result = PlcCollectionRunResult {
        enabled,
        write_enabled,
        attempted: true,
        status: status.to_string(),
        driver,
        latency_ms: started_at.elapsed().as_millis(),
        groups_attempted,
        groups_succeeded,
        raw_snapshots_written,
        latest_snapshots_written,
        groups,
        message: String::new(),
    };

    write_collector_state(
        config,
        &result,
        Some(write_duration_ms.min(i32::MAX as u128) as i32),
        None,
    )
    .await?;

    Ok(result)
}

async fn collect_plc_db_blocks_once_async(
    config: &AgentConfig,
) -> Result<PlcCollectionRunResult, String> {
    collect_plc_db_blocks_once_for_target_async(
        config,
        &PlcCollectionTarget::All,
        plc_write_allowed(config),
    )
    .await
}

async fn collect_plc_db_blocks_once_for_plc_async(
    config: &AgentConfig,
    plc_key: &str,
    persistence_enabled: bool,
) -> Result<PlcCollectionRunResult, String> {
    collect_plc_db_blocks_once_for_target_async(
        config,
        &PlcCollectionTarget::PlcKey(plc_key.to_string()),
        persistence_enabled,
    )
    .await
}

pub(crate) fn collect_plc_db_blocks_once() -> PlcCollectionRunResult {
    let config = AgentConfig::load();

    match tauri::async_runtime::block_on(collect_plc_db_blocks_once_async(&config)) {
        Ok(result) => {
            tracing::info!(
                event = "plc_db_block_collect_once",
                status = %result.status,
                groups_attempted = result.groups_attempted,
                groups_succeeded = result.groups_succeeded,
                raw_snapshots_written = result.raw_snapshots_written,
                latest_snapshots_written = result.latest_snapshots_written,
            );
            result
        }
        Err(error) => {
            tracing::error!(event = "plc_db_block_collect_once", error = %error);
            failed_result(false, false, RUST_SNAP7_DRIVER.to_string(), 0, error)
        }
    }
}

async fn collect_plc_db_blocks_loop_async(config: &AgentConfig) -> PlcCollectionLoopResult {
    let loop_enabled = config.bool_or_default("CONTROL_AGENT_PLC_COLLECTION_LOOP_ENABLED", false);
    let collection_enabled = plc_read_allowed(config);
    let interval_ms = collection_interval_ms(config);
    let max_ticks = parse_u64_or_default(
        &config.value_or_default("CONTROL_AGENT_PLC_COLLECTION_LOOP_MAX_TICKS", "0"),
        0,
    )
    .min(u32::MAX as u64) as u32;
    let max_consecutive_failures = parse_u64_or_default(
        &config.value_or_default(
            "CONTROL_AGENT_PLC_COLLECTION_MAX_CONSECUTIVE_FAILURES",
            "10",
        ),
        10,
    )
    .clamp(1, u32::MAX as u64) as u32;

    if !loop_enabled {
        return PlcCollectionLoopResult {
            enabled: false,
            attempted: false,
            status: "disabled".to_string(),
            interval_ms,
            ticks: 0,
            max_ticks,
            consecutive_failures: 0,
            message: "PLC collection loop is disabled".to_string(),
        };
    }

    if !collection_enabled {
        return PlcCollectionLoopResult {
            enabled: true,
            attempted: false,
            status: "disabled".to_string(),
            interval_ms,
            ticks: 0,
            max_ticks,
            consecutive_failures: 0,
            message: "PLC DB block collection is disabled".to_string(),
        };
    }

    let mut ticks = 0_u32;
    let mut consecutive_failures = 0_u32;

    let last_status = loop {
        let loop_started_at = Instant::now();
        let result = match collect_plc_db_blocks_once_async(config).await {
            Ok(result) => result,
            Err(error) => failed_result(
                true,
                plc_write_allowed(config),
                normalize_plc_driver(
                    &config.value_or_default("CONTROL_AGENT_PLC_DRIVER", RUST_SNAP7_DRIVER),
                ),
                loop_started_at.elapsed().as_millis(),
                error,
            ),
        };

        ticks = ticks.saturating_add(1);
        if matches!(result.status.as_str(), "succeeded" | "partial") {
            consecutive_failures = 0;
        } else {
            consecutive_failures = consecutive_failures.saturating_add(1);
        }
        let tick_status = result.status.clone();

        tracing::info!(
            event = "plc_db_block_collect_loop_tick",
            tick = ticks,
            status = %result.status,
            groups_attempted = result.groups_attempted,
            raw_snapshots_written = result.raw_snapshots_written,
            consecutive_failures,
        );

        if max_ticks > 0 && ticks >= max_ticks {
            break tick_status;
        }

        if consecutive_failures >= max_consecutive_failures {
            tracing::warn!(
                event = "plc_db_block_collect_loop_degraded",
                consecutive_failures,
                max_consecutive_failures,
            );
        }

        thread::sleep(Duration::from_millis(interval_ms));
    };

    if plc_write_allowed(config) {
        if let Err(error) = mark_collector_stopped_async(config).await {
            tracing::warn!(
                event = "plc_db_block_collect_loop_stop_state_write_failed",
                error = %error,
            );
        }
    }

    PlcCollectionLoopResult {
        enabled: true,
        attempted: true,
        status: last_status,
        interval_ms,
        ticks,
        max_ticks,
        consecutive_failures,
        message: String::new(),
    }
}

pub(crate) fn collect_plc_db_blocks_loop() -> PlcCollectionLoopResult {
    let config = AgentConfig::load();

    tauri::async_runtime::block_on(collect_plc_db_blocks_loop_async(&config))
}

#[cfg(test)]
mod tests {
    use std::collections::HashMap;

    use super::*;
    use crate::domain::plc::{PlcRuntimeConfig, PlcRuntimeGroup, PlcRuntimePoint};

    fn runtime_plc(ip: &str) -> PlcRuntimeConfig {
        PlcRuntimeConfig {
            ip: ip.to_string(),
            port: 102,
            rack: 0,
            slot: 1,
            groups: Vec::new(),
        }
    }

    #[test]
    fn target_selection_supports_n_plcs_without_hardcoding_two() {
        let contract = HashMap::from([
            ("PLC_3".to_string(), runtime_plc("127.0.0.3")),
            ("PLC_1".to_string(), runtime_plc("127.0.0.1")),
            ("PLC_2".to_string(), runtime_plc("127.0.0.2")),
        ]);

        let keys = selected_plc_keys_for_target(&contract, &PlcCollectionTarget::All).unwrap();

        assert_eq!(keys, vec!["PLC_1", "PLC_2", "PLC_3"]);
    }

    #[test]
    fn target_selection_rejects_unknown_plc_key() {
        let contract = HashMap::from([("PLC_1".to_string(), runtime_plc("127.0.0.1"))]);

        let error = selected_plc_keys_for_target(
            &contract,
            &PlcCollectionTarget::PlcKey("PLC_X".to_string()),
        )
        .unwrap_err();

        assert!(error.contains("Unknown PLC key"));
    }

    #[test]
    fn read_only_start_does_not_require_database_write_gates() {
        let config = AgentConfig::from_values(HashMap::from([
            (
                "CONTROL_AGENT_PLC_COLLECTION_ENABLED".to_string(),
                "true".to_string(),
            ),
            (
                "CONTROL_AGENT_PLC_COLLECTION_LOOP_ENABLED".to_string(),
                "true".to_string(),
            ),
            (
                "CONTROL_AGENT_PLC_COLLECTION_WRITE_ENABLED".to_string(),
                "false".to_string(),
            ),
            (
                "CONTROL_AGENT_DATABASE_ENABLED".to_string(),
                "false".to_string(),
            ),
            (
                "CONTROL_AGENT_DATABASE_READ_ONLY".to_string(),
                "true".to_string(),
            ),
            (
                "CONTROL_AGENT_PLC_DRIVER".to_string(),
                RUST_SNAP7_DRIVER.to_string(),
            ),
        ]));

        assert!(plc_read_gate_errors(&config).is_empty());
        assert!(!collection_start_gate_errors(&config).is_empty());
    }

    #[test]
    fn write_enabled_collection_requires_database_write_gates() {
        let config = AgentConfig::from_values(HashMap::from([
            (
                "CONTROL_AGENT_PLC_COLLECTION_ENABLED".to_string(),
                "true".to_string(),
            ),
            (
                "CONTROL_AGENT_PLC_COLLECTION_LOOP_ENABLED".to_string(),
                "true".to_string(),
            ),
            (
                "CONTROL_AGENT_PLC_COLLECTION_WRITE_ENABLED".to_string(),
                "true".to_string(),
            ),
            (
                "CONTROL_AGENT_DATABASE_ENABLED".to_string(),
                "false".to_string(),
            ),
            (
                "CONTROL_AGENT_DATABASE_READ_ONLY".to_string(),
                "true".to_string(),
            ),
            (
                "CONTROL_AGENT_PLC_DRIVER".to_string(),
                RUST_SNAP7_DRIVER.to_string(),
            ),
        ]));

        let errors = collection_start_gate_errors(&config);

        assert!(errors
            .iter()
            .any(|error| error.contains("DATABASE_ENABLED=false")));
        assert!(errors
            .iter()
            .any(|error| error.contains("DATABASE_READ_ONLY=true")));
    }

    #[test]
    fn canonical_read_gate_is_independent_from_write_gate() {
        let config = AgentConfig::from_values(HashMap::from([
            (
                "CONTROL_AGENT_PLC_READ_ALLOWED".to_string(),
                "true".to_string(),
            ),
            (
                "CONTROL_AGENT_PLC_WRITE_ALLOWED".to_string(),
                "false".to_string(),
            ),
            (
                "CONTROL_AGENT_PLC_DRIVER".to_string(),
                RUST_SNAP7_DRIVER.to_string(),
            ),
        ]));

        assert!(plc_read_gate_errors(&config).is_empty());
        assert!(!plc_write_gate_errors(&config).is_empty());
    }

    #[test]
    fn conflicting_canonical_and_legacy_read_gates_fail_closed() {
        let config = AgentConfig::from_values(HashMap::from([
            (
                "CONTROL_AGENT_PLC_READ_ALLOWED".to_string(),
                "false".to_string(),
            ),
            (
                "CONTROL_AGENT_PLC_COLLECTION_ENABLED".to_string(),
                "true".to_string(),
            ),
            (
                "CONTROL_AGENT_PLC_DRIVER".to_string(),
                RUST_SNAP7_DRIVER.to_string(),
            ),
        ]));

        let errors = plc_read_gate_errors(&config);

        assert!(!plc_read_allowed(&config));
        assert!(errors.iter().any(|error| error.contains("env_conflict")));
    }

    #[test]
    fn conflicting_autostart_modes_are_reported_as_gate_errors() {
        let config = AgentConfig::from_values(HashMap::from([
            (
                "CONTROL_AGENT_PLC_AUTOSTART_MODE".to_string(),
                "read_only".to_string(),
            ),
            (
                "CONTROL_AGENT_PLC_COLLECTION_LOOP_AUTOSTART".to_string(),
                "false".to_string(),
            ),
        ]));

        let errors = plc_autostart_gate_errors(&config);

        assert!(errors.iter().any(|error| error.contains("env_conflict")));
    }

    #[test]
    fn sample_read_cannot_bypass_the_plc_read_gate() {
        let config = AgentConfig::from_values(HashMap::from([
            (
                "CONTROL_AGENT_PLC_SAMPLE_READ_ENABLED".to_string(),
                "true".to_string(),
            ),
            (
                "CONTROL_AGENT_PLC_DRIVER".to_string(),
                RUST_SNAP7_DRIVER.to_string(),
            ),
        ]));

        assert!(!plc_read_allowed(&config));
        assert!(!plc_sample_read_allowed(&config));
    }

    #[test]
    fn collection_state_matrix_distinguishes_read_only_and_collecting() {
        let mut state = PlcRuntimeUnitState {
            read_state: "running".to_string(),
            ..Default::default()
        };

        refresh_collection_state(&mut state);
        assert_eq!(state.collection_state, "read_only");

        state.persistence_state = "enabled".to_string();
        refresh_collection_state(&mut state);
        assert_eq!(state.collection_state, "collecting");

        state.cycle_degraded = true;
        refresh_collection_state(&mut state);
        assert_eq!(state.collection_state, "degraded");

        state.read_state = "stopped".to_string();
        refresh_collection_state(&mut state);
        assert_eq!(state.collection_state, "stopped");
    }

    #[test]
    fn runtime_status_marks_mixed_degraded_and_running_units_partial() {
        let units = vec![
            PlcRuntimeUnitSnapshot {
                plc_key: "PLC_1".to_string(),
                endpoint: PlcRuntimeEndpointSnapshot {
                    host: "127.0.0.1".to_string(),
                    port: 102,
                    rack: 0,
                    slot: 1,
                },
                desired_state: "running".to_string(),
                read_state: "running".to_string(),
                persistence_state: "paused".to_string(),
                collection_state: "read_only".to_string(),
                runtime_state: "running".to_string(),
                sample_status: "idle".to_string(),
                collection_status: "succeeded".to_string(),
                group_count: 1,
                point_count: 1,
                groups_attempted: 1,
                groups_succeeded: 1,
                groups_failed: 0,
                last_success_at: String::new(),
                last_error_at: String::new(),
                failure_count: 0,
                last_error: String::new(),
                last_sample_error: String::new(),
                last_read_duration_ms: 10,
            },
            PlcRuntimeUnitSnapshot {
                plc_key: "PLC_2".to_string(),
                endpoint: PlcRuntimeEndpointSnapshot {
                    host: "127.0.0.2".to_string(),
                    port: 102,
                    rack: 0,
                    slot: 1,
                },
                desired_state: "running".to_string(),
                read_state: "running".to_string(),
                persistence_state: "paused".to_string(),
                collection_state: "degraded".to_string(),
                runtime_state: "running".to_string(),
                sample_status: "idle".to_string(),
                collection_status: "failed".to_string(),
                group_count: 1,
                point_count: 1,
                groups_attempted: 1,
                groups_succeeded: 0,
                groups_failed: 1,
                last_success_at: String::new(),
                last_error_at: String::new(),
                failure_count: 1,
                last_error: "connect_failed".to_string(),
                last_sample_error: String::new(),
                last_read_duration_ms: 10,
            },
        ];

        assert_eq!(runtime_status_from_units(&units), "partial");
    }

    #[test]
    fn decodes_supported_points_from_group_block() {
        let group = PlcRuntimeGroup {
            name: "example_group".to_string(),
            db_number: 1,
            start: 0,
            size: 6,
            points: vec![
                PlcRuntimePoint {
                    name: "read_1".to_string(),
                    data_type: "Int".to_string(),
                    offset: 0,
                    bit: 0,
                    length: None,
                    readable: None,
                },
                PlcRuntimePoint {
                    name: "read_2".to_string(),
                    data_type: "Bool".to_string(),
                    offset: 2,
                    bit: 0,
                    length: None,
                    readable: None,
                },
                PlcRuntimePoint {
                    name: "status_word".to_string(),
                    data_type: "Word".to_string(),
                    offset: 4,
                    bit: 0,
                    length: None,
                    readable: None,
                },
            ],
        };

        let (decoded, unsupported, decoded_count, unsupported_count) =
            decode_group_payload(&group, &[0, 42, 1, 0, 0x12, 0x34]);

        assert_eq!(decoded["read_1"], json!(42));
        assert_eq!(decoded["read_2"], json!(true));
        assert_eq!(decoded["status_word"], json!(4660));
        assert!(unsupported.is_none());
        assert_eq!(decoded_count, 3);
        assert_eq!(unsupported_count, 0);
    }

    #[test]
    fn filters_raw_payload_to_policy_selected_points() {
        let policy = PlcSnapshotPayloadPolicyFilter::from_group_points_for_test(
            "PLC_1",
            1,
            "example_group",
            &["read_2"],
            &["read_1"],
        );
        let payload = json!({
            "read_1": 42,
            "read_2": true
        });

        let raw_filtered = filter_payload_for_snapshot_policy(
            &payload,
            Some(&policy),
            "PLC_1",
            1,
            "example_group",
            SnapshotPayloadScope::Raw,
        );
        let latest_filtered = filter_payload_for_snapshot_policy(
            &payload,
            Some(&policy),
            "PLC_1",
            1,
            "example_group",
            SnapshotPayloadScope::Latest,
        );
        let unfiltered = filter_payload_for_snapshot_policy(
            &payload,
            None,
            "PLC_1",
            1,
            "example_group",
            SnapshotPayloadScope::Raw,
        );

        assert_eq!(raw_filtered, json!({"read_2": true}));
        assert_eq!(latest_filtered, json!({"read_1": 42}));
        assert_eq!(unfiltered, payload);
    }

    #[test]
    fn decodes_string_points_from_group_block() {
        let group = PlcRuntimeGroup {
            name: "Recipe_Data".to_string(),
            db_number: 60,
            start: 0,
            size: 256,
            points: vec![PlcRuntimePoint {
                name: "CoilNumber".to_string(),
                data_type: "String".to_string(),
                offset: 0,
                bit: 0,
                length: Some(256),
                readable: None,
            }],
        };
        let mut raw = vec![0_u8; 256];
        raw[0] = 254;
        raw[1] = 7;
        raw[2..9].copy_from_slice(b"CN-0001");

        let (decoded, unsupported, decoded_count, unsupported_count) =
            decode_group_payload(&group, &raw);

        assert_eq!(decoded["CoilNumber"], json!("CN-0001"));
        assert!(unsupported.is_none());
        assert_eq!(decoded_count, 1);
        assert_eq!(unsupported_count, 0);
    }
}
