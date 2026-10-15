//! File Path: /control-agent/src-tauri/src/infrastructure/plc_decode.rs
//! Description: PLC sample value decoding helpers shared by S7 drivers
//! Main Features:
//!   - Maps supported point data types to read byte sizes
//!   - Decodes raw PLC bytes into diagnostic string values
//!   - Keeps protocol adapters separate from point value interpretation

use crate::domain::plc::RuntimePointCandidate;

pub(crate) fn point_read_size(point: &RuntimePointCandidate) -> u16 {
    match point.data_type.as_str() {
        "Bool" | "USInt" => 1,
        "Int" | "UInt" | "Word" => 2,
        "DInt" | "UDInt" | "Real" => 4,
        "String" => point.length.unwrap_or(0),
        _ => 0,
    }
}

pub(crate) fn decode_sample_value(
    point: &RuntimePointCandidate,
    bytes: &[u8],
) -> Result<String, String> {
    match point.data_type.as_str() {
        "Bool" => {
            let Some(byte) = bytes.first() else {
                return Err(format!("{} returned no bytes", point.name));
            };

            Ok(((*byte >> point.bit) & 1 == 1).to_string())
        }
        "USInt" => bytes
            .first()
            .map(|value| value.to_string())
            .ok_or_else(|| format!("{} returned no bytes", point.name)),
        "Int" => {
            if bytes.len() < 2 {
                return Err(format!("{} returned fewer than 2 bytes", point.name));
            }

            Ok(i16::from_be_bytes([bytes[0], bytes[1]]).to_string())
        }
        "UInt" | "Word" => {
            if bytes.len() < 2 {
                return Err(format!("{} returned fewer than 2 bytes", point.name));
            }

            Ok(u16::from_be_bytes([bytes[0], bytes[1]]).to_string())
        }
        "DInt" => {
            if bytes.len() < 4 {
                return Err(format!("{} returned fewer than 4 bytes", point.name));
            }

            Ok(i32::from_be_bytes([bytes[0], bytes[1], bytes[2], bytes[3]]).to_string())
        }
        "UDInt" => {
            if bytes.len() < 4 {
                return Err(format!("{} returned fewer than 4 bytes", point.name));
            }

            Ok(u32::from_be_bytes([bytes[0], bytes[1], bytes[2], bytes[3]]).to_string())
        }
        "Real" => {
            if bytes.len() < 4 {
                return Err(format!("{} returned fewer than 4 bytes", point.name));
            }

            let value =
                f32::from_bits(u32::from_be_bytes([bytes[0], bytes[1], bytes[2], bytes[3]]));

            Ok(format!("{value:.3}"))
        }
        "String" => decode_s7_string(point, bytes),
        _ => Err(format!(
            "{} has unsupported type {}",
            point.name, point.data_type
        )),
    }
}

fn decode_s7_string(point: &RuntimePointCandidate, bytes: &[u8]) -> Result<String, String> {
    if bytes.len() < 2 {
        return Err(format!("{} returned fewer than 2 bytes", point.name));
    }

    let max_len = bytes[0] as usize;
    let current_len = bytes[1] as usize;
    if max_len == 0 {
        return Ok(String::new());
    }

    if current_len > max_len {
        return Err(format!(
            "{} S7 string length {} exceeds max {}",
            point.name, current_len, max_len
        ));
    }

    let value_end = 2 + current_len;
    if bytes.len() < value_end {
        return Err(format!(
            "{} returned fewer than declared S7 string length {}",
            point.name, current_len
        ));
    }

    Ok(String::from_utf8_lossy(&bytes[2..value_end]).to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn point(name: &str, data_type: &str, length: Option<u16>) -> RuntimePointCandidate {
        RuntimePointCandidate {
            name: name.to_string(),
            data_type: data_type.to_string(),
            db_number: 60,
            offset: Some(0),
            bit: 0,
            length,
            readable: None,
        }
    }

    #[test]
    fn string_read_size_uses_declared_storage_length() {
        assert_eq!(
            point_read_size(&point("CoilNumber", "String", Some(256))),
            256
        );
    }

    #[test]
    fn word_read_size_and_decode_use_unsigned_16_bit_value() {
        let point = point("StatusWord", "Word", None);

        assert_eq!(point_read_size(&point), 2);
        assert_eq!(
            decode_sample_value(&point, &[0x12, 0x34]).expect("Word should decode"),
            "4660"
        );
    }

    #[test]
    fn decodes_s7_string_payload() {
        let mut bytes = vec![0_u8; 256];
        bytes[0] = 254;
        bytes[1] = 8;
        bytes[2..10].copy_from_slice(b"COIL-001");

        let value = decode_sample_value(&point("CoilNumber", "String", Some(256)), &bytes)
            .expect("S7 string should decode");

        assert_eq!(value, "COIL-001");
    }

    #[test]
    fn rejects_s7_string_length_overflow() {
        let bytes = [4, 5, b'a', b'b', b'c', b'd'];

        let error = decode_sample_value(&point("CoilNumber", "String", Some(6)), &bytes)
            .expect_err("invalid S7 string length should fail");

        assert!(error.contains("exceeds max"));
    }
}
