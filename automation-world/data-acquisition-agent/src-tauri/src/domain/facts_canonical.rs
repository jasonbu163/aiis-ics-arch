//! pf-json/v1无损解析与域摘要；拒绝重复键、深层结构和非有限数，不经binary float。
use serde_json::{Map, Number, Value};
use sha2::{Digest, Sha256};
use std::str::FromStr;
pub(crate) type Result<T> = std::result::Result<T, String>;
pub(crate) fn sha(bytes: &[u8]) -> String {
    format!("sha256:{:x}", Sha256::digest(bytes))
}
pub(crate) fn decimal(token: &str) -> Result<String> {
    let (negative, raw) = match token.strip_prefix('-') {
        Some(s) => (true, s),
        None => (false, token),
    };
    let mut split = raw.split(['e', 'E']);
    let mantissa = split.next().ok_or("invalid_number")?;
    let exponent: i32 = split
        .next()
        .map(|s| s.parse().map_err(|_| "invalid_number"))
        .transpose()?
        .unwrap_or(0);
    if split.next().is_some() || exponent.unsigned_abs() > 1000 {
        return Err("invalid_number".into());
    }
    let mut dot = mantissa.split('.');
    let integer = dot.next().unwrap_or("");
    let fraction = dot.next().unwrap_or("");
    if dot.next().is_some()
        || integer.is_empty()
        || !integer
            .bytes()
            .chain(fraction.bytes())
            .all(|b| b.is_ascii_digit())
    {
        return Err("invalid_number".into());
    }
    let digits = format!("{integer}{fraction}");
    let significant = digits.trim_start_matches('0');
    if significant.len() > 256 || (exponent - fraction.len() as i32).unsigned_abs() > 1000 {
        return Err("invalid_number".into());
    }
    if significant.is_empty() {
        return Ok("0".into());
    }
    let offset = integer.len() as i32 + exponent;
    let mut out = if offset <= 0 {
        format!("0.{}{}", "0".repeat((-offset) as usize), digits)
    } else if offset as usize >= digits.len() {
        format!("{}{}", digits, "0".repeat(offset as usize - digits.len()))
    } else {
        format!(
            "{}.{}",
            &digits[..offset as usize],
            &digits[offset as usize..]
        )
    };
    if out.contains('.') {
        out = out.trim_end_matches('0').trim_end_matches('.').into();
    }
    let trimmed = out.trim_start_matches('0');
    out = if trimmed.starts_with('.') {
        format!("0{trimmed}")
    } else {
        trimmed.into()
    };
    Ok(if negative { format!("-{out}") } else { out })
}
struct Parser<'a> {
    bytes: &'a [u8],
    at: usize,
}
impl Parser<'_> {
    fn space(&mut self) {
        while self
            .bytes
            .get(self.at)
            .map(|b| b" \t\r\n".contains(b))
            .unwrap_or(false)
        {
            self.at += 1;
        }
    }
    fn string(&mut self) -> Result<String> {
        let start = self.at;
        self.at += 1;
        let mut escaped = false;
        while let Some(&b) = self.bytes.get(self.at) {
            self.at += 1;
            if escaped {
                escaped = false;
            } else if b == b'\\' {
                escaped = true;
            } else if b == b'"' {
                return serde_json::from_slice(&self.bytes[start..self.at])
                    .map_err(|_| "invalid_json".into());
            }
        }
        Err("invalid_json".into())
    }
    fn value(&mut self, depth: u8) -> Result<Value> {
        self.space();
        let byte = *self.bytes.get(self.at).ok_or("invalid_json")?;
        if (byte == b'{' || byte == b'[') && depth > 20 {
            return Err("json_depth".into());
        }
        match byte {
            b'"' => Ok(Value::String(self.string()?)),
            b'{' => {
                self.at += 1;
                self.space();
                let mut map = Map::new();
                if self.bytes.get(self.at) == Some(&b'}') {
                    self.at += 1;
                    return Ok(Value::Object(map));
                }
                loop {
                    self.space();
                    if self.bytes.get(self.at) != Some(&b'"') {
                        return Err("invalid_json".into());
                    }
                    let key = self.string()?;
                    self.space();
                    if self.bytes.get(self.at) != Some(&b':') {
                        return Err("invalid_json".into());
                    }
                    self.at += 1;
                    let value = self.value(depth + 1)?;
                    if map.insert(key, value).is_some() {
                        return Err("duplicate_key".into());
                    }
                    self.space();
                    match self.bytes.get(self.at) {
                        Some(b'}') => {
                            self.at += 1;
                            break;
                        }
                        Some(b',') => self.at += 1,
                        _ => return Err("invalid_json".into()),
                    }
                }
                Ok(Value::Object(map))
            }
            b'[' => {
                self.at += 1;
                self.space();
                let mut list = vec![];
                if self.bytes.get(self.at) == Some(&b']') {
                    self.at += 1;
                    return Ok(Value::Array(list));
                }
                loop {
                    list.push(self.value(depth + 1)?);
                    self.space();
                    match self.bytes.get(self.at) {
                        Some(b']') => {
                            self.at += 1;
                            break;
                        }
                        Some(b',') => self.at += 1,
                        _ => return Err("invalid_json".into()),
                    }
                }
                Ok(Value::Array(list))
            }
            _ => {
                let start = self.at;
                while self
                    .bytes
                    .get(self.at)
                    .map(|b| !b" \t\r\n,]}".contains(b))
                    .unwrap_or(false)
                {
                    self.at += 1;
                }
                let s =
                    std::str::from_utf8(&self.bytes[start..self.at]).map_err(|_| "invalid_utf8")?;
                match s {
                    "null" => Ok(Value::Null),
                    "true" => Ok(Value::Bool(true)),
                    "false" => Ok(Value::Bool(false)),
                    _ => {
                        let n = Number::from_str(s).map_err(|_| "invalid_number")?;
                        decimal(s)?;
                        Ok(Value::Number(n))
                    }
                }
            }
        }
    }
}
pub(crate) fn parse(bytes: &[u8], maximum: usize) -> Result<Value> {
    if bytes.len() > maximum {
        return Err("payload_too_large".into());
    }
    std::str::from_utf8(bytes).map_err(|_| "invalid_utf8")?;
    let mut p = Parser { bytes, at: 0 };
    let result = p.value(1)?;
    p.space();
    if p.at != bytes.len() || !result.is_object() {
        return Err("invalid_json".into());
    }
    Ok(result)
}
pub(crate) fn canonical(value: &Value) -> Result<Vec<u8>> {
    fn write(v: &Value, out: &mut String) -> Result<()> {
        match v {
            Value::Null => out.push_str("null"),
            Value::Bool(b) => out.push_str(if *b { "true" } else { "false" }),
            Value::Number(n) => out.push_str(&decimal(&n.to_string())?),
            Value::String(s) => {
                out.push('"');
                for c in s.chars() {
                    match c {
                        '"' => out.push_str("\\\""),
                        '\\' => out.push_str("\\\\"),
                        c if (c as u32) < 32 => out.push_str(&format!("\\u{:04x}", c as u32)),
                        c => out.push(c),
                    }
                }
                out.push('"');
            }
            Value::Array(a) => {
                out.push('[');
                for (i, v) in a.iter().enumerate() {
                    if i > 0 {
                        out.push(',')
                    }
                    write(v, out)?;
                }
                out.push(']');
            }
            Value::Object(m) => {
                out.push('{');
                let mut keys = m.keys().collect::<Vec<_>>();
                keys.sort_by(|a, b| a.as_bytes().cmp(b.as_bytes()));
                for (i, k) in keys.iter().enumerate() {
                    if i > 0 {
                        out.push(',')
                    }
                    write(&Value::String((*k).clone()), out)?;
                    out.push(':');
                    write(&m[*k], out)?;
                }
                out.push('}');
            }
        }
        Ok(())
    }
    let mut text = String::new();
    write(value, &mut text)?;
    Ok(text.into_bytes())
}
pub(crate) fn digest(domain: &str, value: &Value) -> Result<String> {
    let mut input = format!("plc-facts/v1\0{domain}\0").into_bytes();
    input.extend(canonical(value)?);
    Ok(sha(&input))
}
#[cfg(test)]
#[path = "facts_canonical_tests.rs"]
mod tests;
