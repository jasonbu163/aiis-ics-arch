//! File Path: /control-agent/src-tauri/src/infrastructure/plc_client.rs
//! Description: PLC sample reader abstraction for selectable S7 drivers
//! Main Features:
//!   - Defines the read-only PLC sample reader trait
//!   - Normalizes configured PLC driver names
//!   - Builds sample values from runtime point candidates

use std::time::Duration;

use crate::domain::plc::{PlcEndpointProbeSnapshot, PlcSampleValue, RuntimePointCandidate};

pub(crate) const MINIMAL_S7_DRIVER: &str = "minimal_s7";
pub(crate) const RUST_SNAP7_DRIVER: &str = "rust_snap7";

pub(crate) trait PlcSampleReader {
    fn read_samples(
        &self,
        endpoint: &PlcEndpointProbeSnapshot,
        points: &[RuntimePointCandidate],
        timeout: Duration,
    ) -> Result<Vec<PlcSampleValue>, String>;
}

pub(crate) fn normalize_plc_driver(value: &str) -> String {
    match value.trim().to_ascii_lowercase().as_str() {
        "" | "minimal" | "minimal_s7" | "diagnostic" | "minimal_s7_diagnostic" => {
            MINIMAL_S7_DRIVER.to_string()
        }
        "snap7" | "rust_snap7" | "rust-snap7" => RUST_SNAP7_DRIVER.to_string(),
        other => other.to_string(),
    }
}

pub(crate) fn sample_value_from_point(
    point: &RuntimePointCandidate,
    value: String,
) -> Option<PlcSampleValue> {
    point.offset.map(|offset| PlcSampleValue {
        name: point.name.clone(),
        db_number: point.db_number,
        offset,
        bit: point.bit,
        data_type: point.data_type.clone(),
        value,
    })
}
