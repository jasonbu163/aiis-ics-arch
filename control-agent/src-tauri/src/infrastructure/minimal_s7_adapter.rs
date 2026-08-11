//! File Path: /control-agent/src-tauri/src/infrastructure/minimal_s7_adapter.rs
//! Description: Minimal read-only S7 diagnostic sample reader
//! Main Features:
//!   - Uses the local ISO-on-TCP/S7 diagnostic packet helper
//!   - Reads configured DB sample points without PLC writes
//!   - Provides a fallback while the production Snap7 driver is validated

use std::net::{TcpStream, ToSocketAddrs};
use std::time::Duration;

use crate::domain::plc::{PlcEndpointProbeSnapshot, PlcSampleValue, RuntimePointCandidate};
use crate::infrastructure::plc_client::{sample_value_from_point, PlcSampleReader};
use crate::infrastructure::plc_decode::{decode_sample_value, point_read_size};
use crate::infrastructure::plc_s7::{
    build_cotp_connect_request, build_s7_read_request, build_s7_setup_request,
    parse_s7_read_response, read_iso_packet, send_iso_packet,
};

pub(crate) struct MinimalS7SampleReader;

impl PlcSampleReader for MinimalS7SampleReader {
    fn read_samples(
        &self,
        endpoint: &PlcEndpointProbeSnapshot,
        points: &[RuntimePointCandidate],
        timeout: Duration,
    ) -> Result<Vec<PlcSampleValue>, String> {
        let address = format!("{}:{}", endpoint.host, endpoint.port);
        let resolved_address = match address.to_socket_addrs() {
            Ok(mut addresses) => addresses.next(),
            Err(error) => return Err(format!("Failed to resolve PLC endpoint: {error}")),
        };

        let Some(socket_address) = resolved_address else {
            return Err("PLC endpoint did not resolve to a socket address".to_string());
        };

        let mut stream = TcpStream::connect_timeout(&socket_address, timeout).map_err(|error| {
            format!("Failed to connect PLC endpoint for S7 sample read: {error}")
        })?;

        let stream_timeout = Some(timeout);
        let _ = stream.set_read_timeout(stream_timeout);
        let _ = stream.set_write_timeout(stream_timeout);

        send_iso_packet(
            &mut stream,
            &build_cotp_connect_request(endpoint.rack, endpoint.slot),
        )
        .and_then(|_| read_iso_packet(&mut stream).map(|_| ()))
        .and_then(|_| send_iso_packet(&mut stream, &build_s7_setup_request()))
        .and_then(|_| read_iso_packet(&mut stream).map(|_| ()))?;

        let mut values = Vec::new();

        for (index, point) in points.iter().enumerate() {
            let Some(offset) = point.offset else {
                continue;
            };

            let request = build_s7_read_request(
                (index + 2) as u16,
                point.db_number,
                offset,
                point_read_size(point),
            );
            let value = send_iso_packet(&mut stream, &request)
                .and_then(|_| read_iso_packet(&mut stream))
                .and_then(|packet| parse_s7_read_response(&packet))
                .and_then(|bytes| decode_sample_value(point, &bytes))?;

            if let Some(sample_value) = sample_value_from_point(point, value) {
                values.push(sample_value);
            }
        }

        Ok(values)
    }
}
