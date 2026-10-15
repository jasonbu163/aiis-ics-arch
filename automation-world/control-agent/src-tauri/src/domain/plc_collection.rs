//! File Path: /control-agent/src-tauri/src/domain/plc_collection.rs
//! Description: PLC DB block collection domain structures
//! Main Features:
//!   - Defines one-shot collection result payloads
//!   - Defines database snapshot write payloads
//!   - Keeps collection orchestration independent from SeaORM models

use chrono::NaiveDateTime;
use serde::Serialize;
use serde_json::Value;

#[derive(Clone)]
pub(crate) struct NewPlcDbBlockSnapshot {
    pub(crate) plc_key: String,
    pub(crate) device_id: i32,
    pub(crate) db_number: i32,
    pub(crate) group_name: String,
    pub(crate) contract_version: String,
    pub(crate) collected_at: NaiveDateTime,
    pub(crate) driver: String,
    pub(crate) quality: String,
    pub(crate) read_duration_ms: i32,
    pub(crate) raw_bytes: Option<Vec<u8>>,
    pub(crate) decoded_payload: Value,
    pub(crate) unsupported_payload: Option<Value>,
    pub(crate) latest_decoded_payload: Value,
    pub(crate) latest_unsupported_payload: Option<Value>,
    pub(crate) error_message: Option<String>,
}

pub(crate) struct NewMonitorCollectorState {
    pub(crate) collector_key: String,
    pub(crate) status: String,
    pub(crate) worker_id: Option<String>,
    pub(crate) mode: String,
    pub(crate) device_id: i32,
    pub(crate) target_interval_ms: i32,
    pub(crate) last_heartbeat_at: NaiveDateTime,
    pub(crate) last_sample_at: Option<NaiveDateTime>,
    pub(crate) sample_succeeded: bool,
    pub(crate) failure_count_increment: i32,
    pub(crate) last_collect_duration_ms: Option<i32>,
    pub(crate) last_write_duration_ms: Option<i32>,
    pub(crate) last_loop_delay_ms: Option<i32>,
    pub(crate) last_error: Option<String>,
}

#[derive(Serialize)]
pub(crate) struct PlcCollectionGateSnapshot {
    pub(crate) plc_read_allowed: bool,
    pub(crate) plc_write_allowed: bool,
    pub(crate) autostart_mode: String,
    pub(crate) read_gate_errors: Vec<String>,
    pub(crate) write_gate_errors: Vec<String>,
    pub(crate) env_errors: Vec<String>,
    // Legacy fields remain in the wire contract during the compatibility period.
    pub(crate) collection_enabled: bool,
    pub(crate) write_enabled: bool,
    pub(crate) loop_enabled: bool,
    pub(crate) database_enabled: bool,
    pub(crate) database_configured: bool,
    pub(crate) database_read_only: bool,
    pub(crate) driver: String,
    pub(crate) interval_ms: u64,
    pub(crate) collector_key: String,
}

#[derive(Serialize)]
pub(crate) struct MonitorCollectorStateSnapshot {
    pub(crate) loaded: bool,
    pub(crate) collector_key: String,
    pub(crate) status: String,
    pub(crate) worker_id: String,
    pub(crate) mode: String,
    pub(crate) target_interval_ms: u32,
    pub(crate) started_at: String,
    pub(crate) last_heartbeat_at: String,
    pub(crate) last_sample_at: String,
    pub(crate) sample_count: u32,
    pub(crate) failure_count: u32,
    pub(crate) last_collect_duration_ms: u32,
    pub(crate) last_write_duration_ms: u32,
    pub(crate) last_loop_delay_ms: u32,
    pub(crate) last_error: String,
}

#[derive(Serialize)]
pub(crate) struct PlcLatestGroupSnapshot {
    pub(crate) plc_key: String,
    pub(crate) db_number: i32,
    pub(crate) group_name: String,
    pub(crate) quality: String,
    pub(crate) collected_at: String,
    pub(crate) raw_snapshot_id: u32,
    pub(crate) decoded_count: u32,
    pub(crate) unsupported_count: u32,
    pub(crate) read_duration_ms: u32,
    pub(crate) error_message: String,
}

#[derive(Serialize)]
pub(crate) struct PlcSnapshotPolicyStatusSnapshot {
    pub(crate) configured_path: String,
    pub(crate) resolved_path: String,
    pub(crate) exists: bool,
    pub(crate) loaded: bool,
    pub(crate) version: String,
    pub(crate) latest_mode: String,
    pub(crate) raw_hot_retention_days: u32,
    pub(crate) full_decoded_point_count: u32,
    pub(crate) policy_point_count: u32,
    pub(crate) selected_point_count: u32,
    pub(crate) raw_selected_point_count: u32,
    pub(crate) latest_selected_point_count: u32,
    pub(crate) every_sample_count: u32,
    pub(crate) on_change_count: u32,
    pub(crate) missing_policy_point_count: u32,
    pub(crate) unknown_point_count: u32,
    pub(crate) invalid_policy_count: u32,
    pub(crate) error_message: String,
}

#[derive(Clone, Serialize)]
pub(crate) struct PlcRuntimeEndpointSnapshot {
    pub(crate) host: String,
    pub(crate) port: u16,
    pub(crate) rack: u16,
    pub(crate) slot: u16,
}

#[derive(Clone, Serialize)]
pub(crate) struct PlcRuntimeUnitSnapshot {
    pub(crate) plc_key: String,
    pub(crate) endpoint: PlcRuntimeEndpointSnapshot,
    pub(crate) desired_state: String,
    pub(crate) read_state: String,
    pub(crate) persistence_state: String,
    pub(crate) collection_state: String,
    pub(crate) runtime_state: String,
    pub(crate) sample_status: String,
    pub(crate) collection_status: String,
    pub(crate) group_count: u32,
    pub(crate) point_count: u32,
    pub(crate) groups_attempted: u32,
    pub(crate) groups_succeeded: u32,
    pub(crate) groups_failed: u32,
    pub(crate) last_success_at: String,
    pub(crate) last_error_at: String,
    pub(crate) failure_count: u32,
    pub(crate) last_error: String,
    pub(crate) last_sample_error: String,
    pub(crate) last_read_duration_ms: u128,
}

#[derive(Serialize)]
pub(crate) struct PlcCollectionStatusSnapshot {
    pub(crate) loaded: bool,
    pub(crate) local_loop_running: bool,
    pub(crate) runtime_status: String,
    pub(crate) raw_snapshot_count: u32,
    pub(crate) latest_group_count: u32,
    pub(crate) gates: PlcCollectionGateSnapshot,
    pub(crate) collector_state: MonitorCollectorStateSnapshot,
    pub(crate) snapshot_policy: PlcSnapshotPolicyStatusSnapshot,
    pub(crate) plc_units: Vec<PlcRuntimeUnitSnapshot>,
    pub(crate) latest_groups: Vec<PlcLatestGroupSnapshot>,
    pub(crate) error_message: String,
}

#[derive(Serialize)]
pub(crate) struct PlcCollectionControlResult {
    pub(crate) action: String,
    pub(crate) target: String,
    pub(crate) affected_plc_keys: Vec<String>,
    pub(crate) accepted: bool,
    pub(crate) running: bool,
    pub(crate) status: String,
    pub(crate) message: String,
    pub(crate) gate_errors: Vec<String>,
}

#[derive(Serialize)]
pub(crate) struct PlcCollectionControlSmokeResult {
    pub(crate) status: String,
    pub(crate) message: String,
    pub(crate) requested_ticks: u32,
    pub(crate) wait_ms: u64,
    pub(crate) raw_count_before: u32,
    pub(crate) raw_count_after: u32,
    pub(crate) latest_count_before: u32,
    pub(crate) latest_count_after: u32,
    pub(crate) collector_sample_before: u32,
    pub(crate) collector_sample_after: u32,
    pub(crate) raw_count_delta: u32,
    pub(crate) collector_sample_delta: u32,
    pub(crate) start_result: PlcCollectionControlResult,
    pub(crate) stop_result: PlcCollectionControlResult,
}

#[derive(Serialize)]
pub(crate) struct PlcDbBlockGroupCollectResult {
    pub(crate) plc_key: String,
    pub(crate) group_name: String,
    pub(crate) db_number: u16,
    pub(crate) quality: String,
    pub(crate) point_count: u32,
    pub(crate) decoded_count: u32,
    pub(crate) unsupported_count: u32,
    pub(crate) read_duration_ms: u128,
    pub(crate) raw_snapshot_id: Option<i32>,
    pub(crate) error_message: String,
}

#[derive(Serialize)]
pub(crate) struct PlcCollectionRunResult {
    pub(crate) enabled: bool,
    pub(crate) write_enabled: bool,
    pub(crate) attempted: bool,
    pub(crate) status: String,
    pub(crate) driver: String,
    pub(crate) latency_ms: u128,
    pub(crate) groups_attempted: u32,
    pub(crate) groups_succeeded: u32,
    pub(crate) raw_snapshots_written: u32,
    pub(crate) latest_snapshots_written: u32,
    pub(crate) groups: Vec<PlcDbBlockGroupCollectResult>,
    pub(crate) message: String,
}

#[derive(Serialize)]
pub(crate) struct PlcCollectionLoopResult {
    pub(crate) enabled: bool,
    pub(crate) attempted: bool,
    pub(crate) status: String,
    pub(crate) interval_ms: u64,
    pub(crate) ticks: u32,
    pub(crate) max_ticks: u32,
    pub(crate) consecutive_failures: u32,
    pub(crate) message: String,
}
