//! File Path: /control-agent/src-tauri/src/infrastructure/rust_snap7_adapter.rs
//! Description: Optional rust-snap7 PLC sample reader adapter
//! Main Features:
//!   - Wraps rust-snap7 behind the rust-snap7-driver Cargo feature
//!   - Reads configured DB sample points through Snap7 client APIs
//!   - Returns a clear disabled-feature error when the adapter is not compiled

use std::time::Duration;

use crate::domain::plc::{PlcEndpointProbeSnapshot, PlcSampleValue, RuntimePointCandidate};
use crate::infrastructure::plc_client::PlcSampleReader;

pub(crate) struct RustSnap7SampleReader;

#[cfg(feature = "rust-snap7-driver")]
pub(crate) fn read_db_block(
    endpoint: &PlcEndpointProbeSnapshot,
    db_number: u16,
    start: u32,
    size: u32,
    timeout: Duration,
) -> Result<Vec<u8>, String> {
    use rust_snap7::{InternalParam, InternalParamValue, S7Client};

    let timeout_ms = timeout.as_millis().min(i32::MAX as u128) as i32;
    let client = S7Client::create();

    client
        .set_param(
            InternalParam::RemotePort,
            InternalParamValue::U16(endpoint.port),
        )
        .map_err(|error| format!("rust-snap7 failed to set remote port: {error}"))?;
    client
        .set_param(
            InternalParam::PingTimeout,
            InternalParamValue::I32(timeout_ms),
        )
        .map_err(|error| format!("rust-snap7 failed to set ping timeout: {error}"))?;
    client
        .set_param(
            InternalParam::SendTimeout,
            InternalParamValue::I32(timeout_ms),
        )
        .map_err(|error| format!("rust-snap7 failed to set send timeout: {error}"))?;
    client
        .set_param(
            InternalParam::RecvTimeout,
            InternalParamValue::I32(timeout_ms),
        )
        .map_err(|error| format!("rust-snap7 failed to set receive timeout: {error}"))?;

    client
        .connect_to(&endpoint.host, endpoint.rack as i32, endpoint.slot as i32)
        .map_err(|error| format!("rust-snap7 failed to connect PLC endpoint: {error}"))?;

    let mut bytes = vec![0_u8; size as usize];
    let result = client
        .db_read(db_number as i32, start as i32, size as i32, &mut bytes)
        .map(|_| bytes)
        .map_err(|error| {
            format!("rust-snap7 failed to read DB{db_number} start {start} size {size}: {error}")
        });
    let _ = client.disconnect();

    result
}

#[cfg(not(feature = "rust-snap7-driver"))]
pub(crate) fn read_db_block(
    _endpoint: &PlcEndpointProbeSnapshot,
    _db_number: u16,
    _start: u32,
    _size: u32,
    _timeout: Duration,
) -> Result<Vec<u8>, String> {
    Err(
        "rust_snap7 PLC driver was requested, but this binary was built without the rust-snap7-driver feature"
            .to_string(),
    )
}

#[cfg(feature = "rust-snap7-driver")]
impl PlcSampleReader for RustSnap7SampleReader {
    fn read_samples(
        &self,
        endpoint: &PlcEndpointProbeSnapshot,
        points: &[RuntimePointCandidate],
        timeout: Duration,
    ) -> Result<Vec<PlcSampleValue>, String> {
        use rust_snap7::{InternalParam, InternalParamValue, S7Client};

        let timeout_ms = timeout.as_millis().min(i32::MAX as u128) as i32;
        let client = S7Client::create();

        client
            .set_param(
                InternalParam::RemotePort,
                InternalParamValue::U16(endpoint.port),
            )
            .map_err(|error| format!("rust-snap7 failed to set remote port: {error}"))?;
        client
            .set_param(
                InternalParam::PingTimeout,
                InternalParamValue::I32(timeout_ms),
            )
            .map_err(|error| format!("rust-snap7 failed to set ping timeout: {error}"))?;
        client
            .set_param(
                InternalParam::SendTimeout,
                InternalParamValue::I32(timeout_ms),
            )
            .map_err(|error| format!("rust-snap7 failed to set send timeout: {error}"))?;
        client
            .set_param(
                InternalParam::RecvTimeout,
                InternalParamValue::I32(timeout_ms),
            )
            .map_err(|error| format!("rust-snap7 failed to set receive timeout: {error}"))?;

        client
            .connect_to(&endpoint.host, endpoint.rack as i32, endpoint.slot as i32)
            .map_err(|error| format!("rust-snap7 failed to connect PLC endpoint: {error}"))?;

        let result = read_connected_samples(&client, points);
        let _ = client.disconnect();

        result
    }
}

#[cfg(feature = "rust-snap7-driver")]
fn read_connected_samples(
    client: &rust_snap7::S7Client,
    points: &[RuntimePointCandidate],
) -> Result<Vec<PlcSampleValue>, String> {
    use crate::infrastructure::plc_client::sample_value_from_point;
    use crate::infrastructure::plc_decode::{decode_sample_value, point_read_size};

    let mut values = Vec::new();

    for point in points {
        let Some(offset) = point.offset else {
            continue;
        };

        let size = point_read_size(point);
        let mut bytes = vec![0_u8; size as usize];
        client
            .db_read(
                point.db_number as i32,
                offset as i32,
                size as i32,
                &mut bytes,
            )
            .map_err(|error| {
                format!(
                    "rust-snap7 failed to read {} DB{} offset {}: {error}",
                    point.name, point.db_number, offset
                )
            })?;

        let value = decode_sample_value(point, &bytes)?;

        if let Some(sample_value) = sample_value_from_point(point, value) {
            values.push(sample_value);
        }
    }

    Ok(values)
}

#[cfg(not(feature = "rust-snap7-driver"))]
impl PlcSampleReader for RustSnap7SampleReader {
    fn read_samples(
        &self,
        _endpoint: &PlcEndpointProbeSnapshot,
        _points: &[RuntimePointCandidate],
        _timeout: Duration,
    ) -> Result<Vec<PlcSampleValue>, String> {
        Err(
            "rust_snap7 PLC driver was requested, but this binary was built without the rust-snap7-driver feature"
                .to_string(),
        )
    }
}
