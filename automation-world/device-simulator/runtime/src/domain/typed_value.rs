//! DS完整标量编码：所有typed/raw写在提交前共享范围、有限数和完整包校验。
use serde_json::{json, Value};

pub fn width(kind: &str) -> Result<usize, String> {
    aiis_tia_import_core::width(kind)
        .map(|n| n as usize)
        .ok_or_else(|| "unsupported_type".into())
}

pub fn default_value(kind: &str) -> Result<Value, String> {
    width(kind)?;
    Ok(match kind {
        "BOOL" => json!(false),
        "CHAR" => json!("\0"),
        "REAL" => json!(0.0),
        k if k.starts_with("STRING[") => json!(""),
        _ => json!(0),
    })
}

fn unsigned(value: &Value, max: u64) -> Result<u64, String> {
    value
        .as_u64()
        .filter(|n| *n <= max)
        .ok_or_else(|| "value_range".into())
}
fn signed(value: &Value, min: i64, max: i64) -> Result<i64, String> {
    value
        .as_i64()
        .filter(|n| (min..=max).contains(n))
        .ok_or_else(|| "value_range".into())
}

pub fn encode(kind: &str, value: &Value) -> Result<Vec<u8>, String> {
    let size = width(kind)?;
    Ok(match kind {
        "BOOL" => vec![u8::from(value.as_bool().ok_or("value_type")?)],
        "BYTE" | "USINT" => vec![unsigned(value, 255)? as u8],
        "CHAR" => {
            let s = value.as_str().ok_or("value_type")?;
            if s.len() != 1 || !s.is_ascii() {
                return Err("value_ascii".into());
            }
            s.as_bytes().to_vec()
        }
        "WORD" | "UINT" => (unsigned(value, 65535)? as u16).to_be_bytes().to_vec(),
        "INT" => (signed(value, -32768, 32767)? as i16)
            .to_be_bytes()
            .to_vec(),
        "DWORD" | "UDINT" => (unsigned(value, 4294967295)? as u32).to_be_bytes().to_vec(),
        "DINT" => (signed(value, -2147483648, 2147483647)? as i32)
            .to_be_bytes()
            .to_vec(),
        "REAL" => {
            let f = value.as_f64().ok_or("value_type")? as f32;
            if !f.is_finite() {
                return Err("value_finite".into());
            }
            f.to_be_bytes().to_vec()
        }
        _ => {
            let text = value.as_str().ok_or("value_type")?;
            if !text.is_ascii() {
                return Err("value_ascii".into());
            }
            if text.len() > size - 2 {
                return Err("value_length".into());
            }
            let mut bytes = vec![0; size];
            bytes[0] = (size - 2) as u8;
            bytes[1] = text.len() as u8;
            bytes[2..2 + text.len()].copy_from_slice(text.as_bytes());
            bytes
        }
    })
}

pub fn decode(kind: &str, bytes: &[u8]) -> Result<Value, String> {
    if bytes.len() != width(kind)? {
        return Err("value_length".into());
    }
    Ok(match kind {
        "BOOL" => {
            if bytes[0] > 1 {
                return Err("value_bool".into());
            }
            json!(bytes[0] != 0)
        }
        "BYTE" | "USINT" => json!(bytes[0]),
        "CHAR" => {
            if bytes[0] > 127 {
                return Err("value_ascii".into());
            }
            json!(String::from_utf8(bytes.to_vec()).unwrap())
        }
        "WORD" | "UINT" => json!(u16::from_be_bytes(bytes.try_into().unwrap())),
        "INT" => json!(i16::from_be_bytes(bytes.try_into().unwrap())),
        "DWORD" | "UDINT" => json!(u32::from_be_bytes(bytes.try_into().unwrap())),
        "DINT" => json!(i32::from_be_bytes(bytes.try_into().unwrap())),
        "REAL" => {
            let f = f32::from_be_bytes(bytes.try_into().unwrap());
            if !f.is_finite() {
                return Err("value_finite".into());
            }
            json!(f)
        }
        _ => {
            let n = bytes.len() - 2;
            let length = bytes[1] as usize;
            if bytes[0] as usize != n || length > n {
                return Err("string_header".into());
            }
            if !bytes[2..2 + length].is_ascii() || bytes[2 + length..].iter().any(|v| *v != 0) {
                return Err("string_payload".into());
            }
            json!(std::str::from_utf8(&bytes[2..2 + length]).unwrap())
        }
    })
}

pub fn numeric_bounds(kind: &str) -> Option<(f64, f64)> {
    Some(match kind {
        "BOOL" => (0., 1.),
        "BYTE" | "USINT" => (0., 255.),
        "WORD" | "UINT" => (0., 65535.),
        "INT" => (-32768., 32767.),
        "DWORD" | "UDINT" => (0., 4294967295.),
        "DINT" => (-2147483648., 2147483647.),
        "REAL" => (-(f32::MAX as f64), f32::MAX as f64),
        _ => return None,
    })
}
