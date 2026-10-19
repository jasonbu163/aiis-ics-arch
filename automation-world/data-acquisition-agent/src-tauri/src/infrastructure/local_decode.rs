//! 本地类型化大端解码：有限REAL、ASCII CHAR/STRING、错误null与明确质量；不格式化丢精度。
use crate::domain::local_configuration::{width, Point};
use serde_json::{json, Value};
pub(crate) fn decode(p: &Point, b: &[u8]) -> Result<Value, String> {
    let n = width(&p.data_type).ok_or("unsupported_type")? as usize;
    if b.len() != n {
        return Err("bad_length".into());
    }
    Ok(match p.data_type.as_str() {
        "BOOL" => json!(
            (b[0]
                & (1 << p
                    .address
                    .as_ref()
                    .and_then(|a| a.bit)
                    .ok_or("bad_address")?))
                != 0
        ),
        "BYTE" | "USINT" => json!(b[0]),
        "CHAR" => {
            if b[0] > 127 {
                return Err("bad_encoding".into());
            }
            json!((b[0] as char).to_string())
        }
        "INT" => json!(i16::from_be_bytes([b[0], b[1]])),
        "WORD" | "UINT" => json!(u16::from_be_bytes([b[0], b[1]])),
        "DINT" => json!(i32::from_be_bytes(b.try_into().unwrap())),
        "DWORD" | "UDINT" => json!(u32::from_be_bytes(b.try_into().unwrap())),
        "REAL" => {
            let v = f32::from_be_bytes(b.try_into().unwrap());
            if !v.is_finite() {
                return Err("bad_non_finite".into());
            }
            json!(v as f64)
        }
        _ => {
            let declared = n - 2;
            let len = b[1] as usize;
            if b[0] as usize != declared || len > declared {
                return Err("bad_string_length".into());
            }
            if b[2..2 + len].iter().any(|b| *b > 127) {
                return Err("bad_encoding".into());
            }
            json!(std::str::from_utf8(&b[2..2 + len]).map_err(|_| "bad_encoding")?)
        }
    })
}
