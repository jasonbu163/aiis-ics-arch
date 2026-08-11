//! File Path: /control-agent/src-tauri/src/infrastructure/plc_s7.rs
//! Description: Read-only PLC S7 protocol helper functions
//! Main Features:
//!   - Builds ISO-on-TCP and S7 read packets
//!   - Reads and parses ISO/S7 packet responses

use std::io::{Read, Write};
use std::net::TcpStream;

pub(crate) fn build_cotp_connect_request(rack: u16, slot: u16) -> Vec<u8> {
    let remote_tsap = 0x0100_u16 + rack * 0x20 + slot;

    vec![
        0x03,
        0x00,
        0x00,
        0x16,
        0x11,
        0xE0,
        0x00,
        0x00,
        0x00,
        0x01,
        0x00,
        0xC1,
        0x02,
        0x01,
        0x00,
        0xC2,
        0x02,
        (remote_tsap >> 8) as u8,
        remote_tsap as u8,
        0xC0,
        0x01,
        0x0A,
    ]
}

pub(crate) fn build_s7_setup_request() -> Vec<u8> {
    vec![
        0x03, 0x00, 0x00, 0x19, 0x02, 0xF0, 0x80, 0x32, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x08,
        0x00, 0x00, 0xF0, 0x00, 0x00, 0x01, 0x00, 0x01, 0x03, 0xC0,
    ]
}

pub(crate) fn build_s7_read_request(
    pdu_ref: u16,
    db_number: u16,
    offset: u32,
    size: u16,
) -> Vec<u8> {
    let bit_address = offset * 8;

    vec![
        0x03,
        0x00,
        0x00,
        0x1F,
        0x02,
        0xF0,
        0x80,
        0x32,
        0x01,
        0x00,
        0x00,
        (pdu_ref >> 8) as u8,
        pdu_ref as u8,
        0x00,
        0x0E,
        0x00,
        0x00,
        0x04,
        0x01,
        0x12,
        0x0A,
        0x10,
        0x02,
        (size >> 8) as u8,
        size as u8,
        (db_number >> 8) as u8,
        db_number as u8,
        0x84,
        ((bit_address >> 16) & 0xFF) as u8,
        ((bit_address >> 8) & 0xFF) as u8,
        (bit_address & 0xFF) as u8,
    ]
}

pub(crate) fn send_iso_packet(stream: &mut TcpStream, packet: &[u8]) -> Result<(), String> {
    stream
        .write_all(packet)
        .map_err(|error| format!("Failed to send PLC packet: {error}"))
}

pub(crate) fn read_iso_packet(stream: &mut TcpStream) -> Result<Vec<u8>, String> {
    let mut header = [0_u8; 4];
    stream
        .read_exact(&mut header)
        .map_err(|error| format!("Failed to read PLC packet header: {error}"))?;

    if header[0] != 0x03 || header[1] != 0x00 {
        return Err("Invalid TPKT header from PLC endpoint".to_string());
    }

    let packet_len = u16::from_be_bytes([header[2], header[3]]) as usize;

    if packet_len < header.len() {
        return Err("Invalid TPKT packet length from PLC endpoint".to_string());
    }

    let mut packet = header.to_vec();
    let mut payload = vec![0_u8; packet_len - header.len()];
    stream
        .read_exact(&mut payload)
        .map_err(|error| format!("Failed to read PLC packet payload: {error}"))?;
    packet.extend(payload);

    Ok(packet)
}

pub(crate) fn parse_s7_read_response(packet: &[u8]) -> Result<Vec<u8>, String> {
    let Some(header_start) = packet.iter().position(|byte| *byte == 0x32) else {
        return Err("S7 response header was not found".to_string());
    };

    if packet.len() < header_start + 10 {
        return Err("S7 response header is incomplete".to_string());
    }

    let rosctr = packet[header_start + 1];
    let header_len = if rosctr == 0x03 { 12 } else { 10 };

    if packet.len() < header_start + header_len {
        return Err("S7 response header is incomplete".to_string());
    }

    let param_len =
        u16::from_be_bytes([packet[header_start + 6], packet[header_start + 7]]) as usize;
    let data_len =
        u16::from_be_bytes([packet[header_start + 8], packet[header_start + 9]]) as usize;
    let data_start = header_start + header_len + param_len;

    if packet.len() < data_start + data_len || data_len < 4 {
        return Err("S7 response data section is incomplete".to_string());
    }

    let data = &packet[data_start..data_start + data_len];

    if data[0] != 0xFF {
        return Err(format!(
            "S7 read returned non-success code 0x{:02X}",
            data[0]
        ));
    }

    let payload_bit_len = u16::from_be_bytes([data[2], data[3]]) as usize;
    let payload_byte_len = payload_bit_len.div_ceil(8);

    if data.len() < 4 + payload_byte_len {
        return Err("S7 read payload is shorter than declared length".to_string());
    }

    Ok(data[4..4 + payload_byte_len].to_vec())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn builds_s7_read_request_for_db_offset() {
        let request = build_s7_read_request(3, 28, 20, 2);

        assert_eq!(request.len(), 31);
        assert_eq!(&request[0..4], &[0x03, 0x00, 0x00, 0x1F]);
        assert_eq!(&request[11..13], &[0x00, 0x03]);
        assert_eq!(&request[25..27], &[0x00, 0x1C]);
        assert_eq!(&request[28..31], &[0x00, 0x00, 0xA0]);
    }

    #[test]
    fn parses_ack_data_read_response() {
        let response = [
            0x03, 0x00, 0x00, 0x1B, 0x02, 0xF0, 0x80, 0x32, 0x03, 0x00, 0x00, 0x00, 0x02, 0x00,
            0x02, 0x00, 0x06, 0x00, 0x00, 0x04, 0x01, 0xFF, 0x04, 0x00, 0x10, 0x00, 0x02,
        ];

        let payload = parse_s7_read_response(&response).expect("response should parse");

        assert_eq!(payload, vec![0x00, 0x02]);
    }
}
