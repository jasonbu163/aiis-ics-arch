//! File Path: /control-agent/src-tauri/src/domain/plc.rs
//! Description: PLC diagnostics domain structures
//! Main Features:
//!   - Defines PLC point contract snapshot payloads
//!   - Defines PLC endpoint probe payloads
//!   - Defines resolved PLC endpoint values for collection and diagnostics
//!   - Defines read-only PLC sample payloads

use serde::{Deserialize, Serialize};

#[derive(Serialize)]
pub(crate) struct PointTypeCount {
    pub(crate) data_type: String,
    pub(crate) count: u32,
}

#[derive(Serialize)]
pub(crate) struct PlcPointContractSnapshot {
    pub(crate) configured_path: String,
    pub(crate) resolved_path: String,
    pub(crate) exists: bool,
    pub(crate) loaded: bool,
    pub(crate) plc_count: u32,
    pub(crate) group_count: u32,
    pub(crate) point_count: u32,
    pub(crate) readable_count: u32,
    pub(crate) writable_count: u32,
    pub(crate) missing_required_count: u32,
    pub(crate) unsupported_type_count: u32,
    pub(crate) endpoint_ip: String,
    pub(crate) endpoint_port: u16,
    pub(crate) endpoint_rack: u16,
    pub(crate) endpoint_slot: u16,
    pub(crate) type_counts: Vec<PointTypeCount>,
    pub(crate) error_message: String,
}

#[derive(Serialize)]
pub(crate) struct PlcEndpointProbeSnapshot {
    pub(crate) host: String,
    pub(crate) port: u16,
    pub(crate) rack: u16,
    pub(crate) slot: u16,
    pub(crate) enabled: bool,
    pub(crate) reachable: bool,
    pub(crate) latency_ms: u128,
    pub(crate) error_message: String,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct ResolvedPlcEndpoint {
    pub(crate) host: String,
    pub(crate) port: u16,
    pub(crate) rack: u16,
    pub(crate) slot: u16,
}

#[derive(Serialize)]
pub(crate) struct PlcSampleValue {
    pub(crate) name: String,
    pub(crate) db_number: u16,
    pub(crate) offset: u32,
    pub(crate) bit: u8,
    pub(crate) data_type: String,
    pub(crate) value: String,
}

#[derive(Serialize)]
pub(crate) struct PlcSampleReadSnapshot {
    pub(crate) enabled: bool,
    pub(crate) autostart: bool,
    pub(crate) plc_key: String,
    pub(crate) driver: String,
    pub(crate) attempted: bool,
    pub(crate) succeeded: bool,
    pub(crate) sample_count: u32,
    pub(crate) latency_ms: u128,
    pub(crate) values: Vec<PlcSampleValue>,
    pub(crate) error_message: String,
}

#[derive(Default)]
pub(crate) struct RuntimePointCandidate {
    pub(crate) name: String,
    pub(crate) data_type: String,
    pub(crate) db_number: u16,
    pub(crate) offset: Option<u32>,
    pub(crate) bit: u8,
    pub(crate) length: Option<u16>,
    pub(crate) readable: Option<bool>,
}

#[derive(Clone, Debug, Deserialize)]
pub(crate) struct PlcRuntimeConfig {
    pub(crate) ip: String,
    #[serde(default)]
    pub(crate) port: u16,
    #[serde(default)]
    pub(crate) rack: u16,
    #[serde(default)]
    pub(crate) slot: u16,
    #[serde(default)]
    pub(crate) groups: Vec<PlcRuntimeGroup>,
}

#[derive(Clone, Debug, Deserialize)]
pub(crate) struct PlcRuntimeGroup {
    pub(crate) name: String,
    pub(crate) db_number: u16,
    pub(crate) start: u32,
    pub(crate) size: u32,
    #[serde(default)]
    pub(crate) points: Vec<PlcRuntimePoint>,
}

#[derive(Clone, Debug, Deserialize)]
pub(crate) struct PlcRuntimePoint {
    pub(crate) name: String,
    #[serde(rename = "type")]
    pub(crate) data_type: String,
    pub(crate) offset: u32,
    #[serde(default)]
    pub(crate) bit: u8,
    #[serde(default)]
    pub(crate) length: Option<u16>,
    #[serde(default)]
    pub(crate) readable: Option<bool>,
}

impl PlcRuntimePoint {
    pub(crate) fn as_runtime_candidate(&self, db_number: u16) -> RuntimePointCandidate {
        RuntimePointCandidate {
            name: self.name.clone(),
            data_type: self.data_type.clone(),
            db_number,
            offset: Some(self.offset),
            bit: self.bit,
            length: self.length,
            readable: self.readable,
        }
    }
}
