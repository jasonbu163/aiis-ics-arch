//! File Path: /control-agent/src-tauri/src/services/runtime_snapshot.rs
//! Description: Runtime snapshot assembly service
//! Main Features:
//!   - Builds the read-only Control Agent runtime snapshot
//!   - Coordinates PLC diagnostics and collection status services

use std::sync::OnceLock;
use std::time::{SystemTime, UNIX_EPOCH};

use crate::config::AgentConfig;
use crate::domain::runtime::{AgentHeartbeatSnapshot, RuntimeSnapshot};
use crate::infrastructure::logging::emit_runtime_snapshot_event;
use crate::infrastructure::plc_points::read_plc_point_contract;
use crate::services::authorization_gate::build_authorization_gate_snapshot;
use crate::services::plc_collection::read_plc_collection_status;
use crate::services::plc_diagnostics::{idle_plc_endpoint_probe, idle_plc_sample_read};

static STARTED_AT_UNIX_SECONDS: OnceLock<u64> = OnceLock::new();

fn now_unix_seconds() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|duration| duration.as_secs())
        .unwrap_or_default()
}

fn process_started_at_unix_seconds() -> u64 {
    *STARTED_AT_UNIX_SECONDS.get_or_init(now_unix_seconds)
}

fn build_agent_heartbeat(
    config: &AgentConfig,
    last_seen_unix_seconds: u64,
) -> AgentHeartbeatSnapshot {
    let started_at = process_started_at_unix_seconds();

    AgentHeartbeatSnapshot {
        status: "alive".to_string(),
        executor_id: config.value_or_default("CONTROL_AGENT_EXECUTOR_ID", "control-agent-local"),
        process_started_at_unix_seconds: started_at,
        last_seen_unix_seconds,
        uptime_seconds: last_seen_unix_seconds.saturating_sub(started_at),
        mode: "plc_collection".to_string(),
    }
}

pub(crate) fn build_runtime_snapshot() -> RuntimeSnapshot {
    let config = AgentConfig::load();
    let generated_at_unix_seconds = now_unix_seconds();
    let plc_point_contract = read_plc_point_contract(&config);
    let plc_endpoint_probe = idle_plc_endpoint_probe(&config, &plc_point_contract);
    let plc_sample_read = idle_plc_sample_read(&config);
    let plc_collection_status = read_plc_collection_status(&config);
    let authorization_gate = build_authorization_gate_snapshot(&config, generated_at_unix_seconds);

    let snapshot = RuntimeSnapshot {
        agent_name: "aiis-ics-control-agent".to_string(),
        version: env!("CARGO_PKG_VERSION").to_string(),
        mode: "plc_collection".to_string(),
        access_mode: config.value_or_default("CONTROL_AGENT_ACCESS_MODE", "database"),
        backend_base_url: config
            .value_or_default("CONTROL_AGENT_BACKEND_BASE_URL", "http://127.0.0.1:8000"),
        backend_probe_path: config.value_or_default("CONTROL_AGENT_BACKEND_PROBE_PATH", "/health"),
        database_enabled: config.bool_or_default("CONTROL_AGENT_DATABASE_ENABLED", false),
        database_configured: config.is_configured("CONTROL_AGENT_DATABASE_URL"),
        generated_at_unix_seconds,
        agent_heartbeat: build_agent_heartbeat(&config, generated_at_unix_seconds),
        plc_point_contract,
        plc_endpoint_probe,
        plc_sample_read,
        plc_collection_status,
        authorization_gate,
    };

    emit_runtime_snapshot_event(&config, &snapshot);

    snapshot
}
