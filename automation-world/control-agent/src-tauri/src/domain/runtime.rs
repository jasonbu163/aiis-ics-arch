//! File Path: /control-agent/src-tauri/src/domain/runtime.rs
//! Description: Runtime snapshot domain structures
//! Main Features:
//!   - Defines the full read-only runtime snapshot payload
//!   - Keeps Tauri serialization models away from runtime bootstrap code

use serde::Serialize;

use crate::domain::authorization::AuthorizationGateSnapshot;
use crate::domain::plc::{
    PlcEndpointProbeSnapshot, PlcPointContractSnapshot, PlcSampleReadSnapshot,
};
use crate::domain::plc_collection::PlcCollectionStatusSnapshot;

#[derive(Serialize)]
pub(crate) struct AgentHeartbeatSnapshot {
    pub(crate) status: String,
    pub(crate) executor_id: String,
    pub(crate) process_started_at_unix_seconds: u64,
    pub(crate) last_seen_unix_seconds: u64,
    pub(crate) uptime_seconds: u64,
    pub(crate) mode: String,
}

#[derive(Serialize)]
pub(crate) struct RuntimeSnapshot {
    pub(crate) agent_name: String,
    pub(crate) version: String,
    pub(crate) mode: String,
    pub(crate) access_mode: String,
    pub(crate) backend_base_url: String,
    pub(crate) backend_probe_path: String,
    pub(crate) database_enabled: bool,
    pub(crate) database_configured: bool,
    pub(crate) generated_at_unix_seconds: u64,
    pub(crate) agent_heartbeat: AgentHeartbeatSnapshot,
    pub(crate) plc_point_contract: PlcPointContractSnapshot,
    pub(crate) plc_endpoint_probe: PlcEndpointProbeSnapshot,
    pub(crate) plc_sample_read: PlcSampleReadSnapshot,
    pub(crate) plc_collection_status: PlcCollectionStatusSnapshot,
    pub(crate) authorization_gate: AuthorizationGateSnapshot,
}
