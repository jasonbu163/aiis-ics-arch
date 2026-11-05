//! 文件：src/config/catalog.rs；冻结单PLC原字节、严格JSON及协议声明校验，不执行网络或状态IO。
use crate::{domain::valid_id, Result};
use serde::de::{self, DeserializeSeed, MapAccess, SeqAccess, Visitor};
use serde_json::{Map, Value};
use sha2::{Digest, Sha256};
use std::{
    collections::{HashMap, HashSet},
    fmt, fs,
    io::Read,
    net::Ipv4Addr,
    path::{Component, Path, PathBuf},
};

// Value的默认反序列化会覆盖重复键；这里在每层构造前拒绝，且限制嵌套。
struct Strict(u8);
impl<'de> DeserializeSeed<'de> for Strict {
    type Value = Value;
    fn deserialize<D: de::Deserializer<'de>>(self, d: D) -> std::result::Result<Value, D::Error> {
        if self.0 > 16 {
            return Err(de::Error::custom("depth"));
        }
        d.deserialize_any(self)
    }
}
impl<'de> Visitor<'de> for Strict {
    type Value = Value;
    fn expecting(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.write_str("strict value")
    }
    fn visit_bool<E: de::Error>(self, v: bool) -> std::result::Result<Value, E> {
        Ok(v.into())
    }
    fn visit_i64<E: de::Error>(self, v: i64) -> std::result::Result<Value, E> {
        Ok(v.into())
    }
    fn visit_u64<E: de::Error>(self, v: u64) -> std::result::Result<Value, E> {
        Ok(v.into())
    }
    fn visit_f64<E: de::Error>(self, v: f64) -> std::result::Result<Value, E> {
        serde_json::Number::from_f64(v)
            .map(Value::Number)
            .ok_or_else(|| E::custom("finite"))
    }
    fn visit_str<E: de::Error>(self, v: &str) -> std::result::Result<Value, E> {
        Ok(v.into())
    }
    fn visit_string<E: de::Error>(self, v: String) -> std::result::Result<Value, E> {
        Ok(v.into())
    }
    fn visit_unit<E: de::Error>(self) -> std::result::Result<Value, E> {
        Ok(Value::Null)
    }
    fn visit_none<E: de::Error>(self) -> std::result::Result<Value, E> {
        Ok(Value::Null)
    }
    fn visit_seq<A: SeqAccess<'de>>(self, mut a: A) -> std::result::Result<Value, A::Error> {
        let mut v = Vec::new();
        while let Some(x) = a.next_element_seed(Strict(self.0 + 1))? {
            v.push(x);
        }
        Ok(Value::Array(v))
    }
    fn visit_map<A: MapAccess<'de>>(self, mut a: A) -> std::result::Result<Value, A::Error> {
        let mut v = Map::new();
        while let Some(k) = a.next_key::<String>()? {
            if v.contains_key(&k) {
                return Err(de::Error::custom("duplicate_key"));
            }
            let x = a.next_value_seed(Strict(self.0 + 1))?;
            v.insert(k, x);
        }
        Ok(Value::Object(v))
    }
}
// Source-only gate: serde_yaml still owns YAML syntax and scalar semantics.
// Quotes start a quoted scalar only at a node boundary, never inside a plain scalar.
fn reject_yaml_aliases(s: &str) -> Result<()> {
    #[derive(Clone, Copy)]
    enum Scalar {
        None,
        Plain {
            parent: usize,
            start: usize,
        },
        Quoted(u8),
        Block {
            parent: usize,
            content: Option<usize>,
        },
    }
    let mut scalar = Scalar::None;
    let mut depth = 0usize;
    let mut node_start = true;
    let mut parent = 0;
    let mut last_start = 0;
    let mut quoted_end = false;
    // Match the locked YAML parser's line boundaries for source scanning only.
    // Parsing and source hashes still use the original bytes (including scalar line breaks).
    let lines = s
        .replace("\r\n", "\n")
        .replace(['\r', '\u{85}', '\u{2028}', '\u{2029}'], "\n");
    for line in lines.split_inclusive('\n') {
        let b = line.as_bytes();
        let indent = b.iter().take_while(|c| **c == b' ').count();
        let blank = b[indent..].iter().all(u8::is_ascii_whitespace);
        if let Scalar::Block {
            parent: base,
            content,
        } = scalar
        {
            if blank {
                continue;
            }
            let required = content.unwrap_or(indent.max(base + 1));
            if indent >= required {
                scalar = Scalar::Block {
                    parent: base,
                    content: Some(required),
                };
                continue;
            }
            scalar = Scalar::None;
        }
        if let Scalar::Plain { parent: base, .. } = scalar {
            if depth == 0 && !blank && indent <= base {
                scalar = Scalar::None;
            }
        }
        if matches!(scalar, Scalar::None) && depth == 0 {
            node_start = true;
            parent = indent;
            quoted_end = false;
        }
        let mut at = indent;
        while at < b.len() {
            let c = b[at];
            let next = b.get(at + 1).copied();
            let separated =
                next.is_none_or(|n| n.is_ascii_whitespace() || depth > 0 && b"[]{},".contains(&n));
            let prior_space = at == 0 || b[at - 1].is_ascii_whitespace();
            if let Scalar::Quoted(q) = scalar {
                if q == b'"' && c == b'\\' {
                    at += 2;
                    continue;
                }
                if c == q {
                    if q == b'\'' && next == Some(q) {
                        at += 2;
                        continue;
                    }
                    scalar = Scalar::None;
                    node_start = false;
                    quoted_end = true;
                }
                at += 1;
                continue;
            }
            if let Scalar::Plain { start, .. } = scalar {
                if c == b'#' && prior_space {
                    break;
                }
                if c == b':' && separated {
                    scalar = Scalar::None;
                    last_start = start;
                } else if depth > 0 && b"[]{},".contains(&c) {
                    scalar = Scalar::None;
                } else {
                    at += 1;
                    continue;
                }
            }
            if c.is_ascii_whitespace() {
                at += 1;
                continue;
            }
            if c == b'#' && prior_space {
                break;
            }
            if at == 0 && c == b'%' {
                break;
            }
            if at == 0
                && (b.starts_with(b"---") || b.starts_with(b"..."))
                && b.get(3).is_none_or(u8::is_ascii_whitespace)
            {
                at += 3;
                node_start = true;
                continue;
            }
            // In flow mappings a quoted key permits JSON-style `"key":value`.
            // Plain scalars retain their separate colon/separation rule above.
            let quoted_key_separator = c == b':' && depth > 0 && quoted_end;
            quoted_end = false;
            match c {
                b':' if separated || quoted_key_separator => {
                    parent = last_start;
                    node_start = true;
                }
                b'[' | b'{' => {
                    depth += 1;
                    node_start = true;
                }
                b']' | b'}' => {
                    depth = depth.saturating_sub(1);
                    node_start = false;
                }
                b',' if depth > 0 => {
                    node_start = true;
                }
                b'-' | b'?' if node_start && next.is_none_or(|n| n.is_ascii_whitespace()) => {
                    parent = at;
                }
                b'!' if node_start => {
                    at += 1;
                    if b.get(at) == Some(&b'<') {
                        while at < b.len() && b[at] != b'>' {
                            at += 1;
                        }
                        at += 1;
                    } else {
                        while at < b.len() && !b[at].is_ascii_whitespace() {
                            at += 1;
                        }
                    }
                    continue;
                }
                b'&' | b'*' if node_start => return Err("config_yaml_alias".into()),
                b'|' | b'>' if node_start && depth == 0 => {
                    let explicit = b[at + 1..]
                        .iter()
                        .take_while(|n| !n.is_ascii_whitespace())
                        .find(|n| (b'1'..=b'9').contains(n))
                        .map(|n| parent + (n - b'0') as usize);
                    scalar = Scalar::Block {
                        parent,
                        content: explicit,
                    };
                    break;
                }
                b'\'' | b'"' if node_start => {
                    last_start = at;
                    scalar = Scalar::Quoted(c);
                    node_start = false;
                }
                _ => {
                    last_start = at;
                    scalar = Scalar::Plain { parent, start: at };
                    node_start = false;
                }
            }
            at += 1;
        }
    }
    Ok(())
}

pub fn parse(bytes: &[u8], yaml: bool) -> Result<Value> {
    let s = std::str::from_utf8(bytes).map_err(|_| "config_utf8")?;
    if s.starts_with('\u{feff}') {
        return Err("config_bom".into());
    }
    if yaml {
        reject_yaml_aliases(s)?;
        Strict(0)
            .deserialize(serde_yaml::Deserializer::from_str(s))
            .map_err(|_| "config_schema".into())
    } else {
        let mut d = serde_json::Deserializer::from_slice(bytes);
        let v = Strict(0).deserialize(&mut d).map_err(|_| "config_schema")?;
        d.end().map_err(|_| "config_schema")?;
        Ok(v)
    }
}
pub fn check_path(path: &Path) -> Result<()> {
    let absolute = if path.is_absolute() {
        path.to_owned()
    } else {
        std::env::current_dir()
            .map_err(|_| "config_path")?
            .join(path)
    };
    let mut walked = PathBuf::new();
    for c in absolute.components() {
        walked.push(c);
        if fs::symlink_metadata(&walked)
            .map_err(|_| "config_read")?
            .file_type()
            .is_symlink()
        {
            return Err("config_symlink".into());
        }
    }
    Ok(())
}
pub fn read_file(path: &Path, max: u64) -> Result<Vec<u8>> {
    check_path(path)?;
    let meta = fs::metadata(path).map_err(|_| "config_read")?;
    if !meta.is_file() {
        return Err("config_file".into());
    }
    if meta.len() > max {
        return Err("config_size".into());
    }
    let f = fs::File::open(path).map_err(|_| "config_read")?;
    let m = f.metadata().map_err(|_| "config_read")?;
    if !m.is_file() {
        return Err("config_file".into());
    }
    if m.len() > max {
        return Err("config_size".into());
    }
    let mut b = Vec::new();
    f.take(max + 1)
        .read_to_end(&mut b)
        .map_err(|_| "config_read")?;
    if b.len() as u64 > max {
        return Err("config_size".into());
    }
    Ok(b)
}
pub fn relative(base: &Path, s: &str) -> Result<PathBuf> {
    if s.is_empty()
        || s.len() > 255
        || s.contains(['\\', ':', '*', '?', '$', '~', '[', ']'])
        || s.split('/').any(|s| s.is_empty() || s == "." || s == "..")
        || Path::new(s)
            .components()
            .any(|c| !matches!(c, Component::Normal(_)))
    {
        return Err("config_path".into());
    }
    Ok(base.join(s))
}
pub fn object<'a>(
    v: &'a Value,
    required: &[&str],
    optional: &[&str],
) -> Result<&'a Map<String, Value>> {
    let m = v.as_object().ok_or("config_object")?;
    if required.iter().any(|k| !m.contains_key(*k))
        || m.keys()
            .any(|k| !required.contains(&k.as_str()) && !optional.contains(&k.as_str()))
    {
        return Err("config_fields".into());
    }
    Ok(m)
}
pub fn text(v: &Value, max: usize) -> Result<&str> {
    let s = v.as_str().ok_or("config_string")?;
    if s.is_empty() || s.len() > max {
        return Err("config_string".into());
    }
    Ok(s)
}
pub fn identifier(v: &Value) -> Result<&str> {
    let s = text(v, 64)?;
    if !valid_id(s) {
        return Err("config_id".into());
    }
    Ok(s)
}
pub fn integer(v: &Value, lo: u64, hi: u64) -> Result<u64> {
    let n = v.as_u64().ok_or("config_integer")?;
    if n < lo || n > hi {
        return Err("config_range".into());
    }
    Ok(n)
}
pub fn array(v: &Value, lo: usize, hi: usize) -> Result<&Vec<Value>> {
    let a = v.as_array().ok_or("config_array")?;
    if a.len() < lo || a.len() > hi {
        return Err("config_capacity".into());
    }
    Ok(a)
}
fn enabled(m: &Map<String, Value>) -> Result<bool> {
    m.get("enabled")
        .map(|v| v.as_bool().ok_or("config_bool".into()))
        .unwrap_or(Ok(true))
}
fn descriptions(m: &Map<String, Value>, fields: &[(&str, usize)]) -> Result<()> {
    for (k, n) in fields {
        if let Some(v) = m.get(*k) {
            text(v, *n)?;
        }
    }
    Ok(())
}
fn time(v: &Value) -> Result<()> {
    let s = text(v, 64)?;
    let t = chrono::DateTime::parse_from_rfc3339(s).map_err(|_| "config_time")?;
    if !s.ends_with("+08:00") || t.offset().local_minus_utc() != 28800 {
        return Err("config_time".into());
    }
    Ok(())
}
fn revision(v: &Value) -> Result<()> {
    let m = object(v, &["id", "saved_seq", "payload_sha256"], &[])?;
    let s = text(&m["id"], 36)?;
    if s.len() != 36
        || s.bytes().enumerate().any(|(i, c)| {
            if [8, 13, 18, 23].contains(&i) {
                c != b'-'
            } else {
                !c.is_ascii_digit() && !(b'a'..=b'f').contains(&c)
            }
        })
    {
        return Err("config_revision".into());
    }
    integer(&m["saved_seq"], 1, 9007199254740991)?;
    let s = text(&m["payload_sha256"], 64)?;
    if s.len() != 64
        || !s
            .bytes()
            .all(|c| c.is_ascii_digit() || (b'a'..=b'f').contains(&c))
    {
        return Err("config_sha256".into());
    }
    Ok(())
}
fn source(v: &Value, id: &str) -> Result<()> {
    match v["kind"].as_str() {
        Some("manual") => {
            let m = object(v, &["kind"], &["note"])?;
            descriptions(m, &[("note", 512)])?;
        }
        Some("device_simulator") => {
            let m = object(
                v,
                &[
                    "kind",
                    "export_mode",
                    "instance_id",
                    "revision",
                    "exporter_version",
                    "generated_at",
                ],
                &["runtime_observation"],
            )?;
            if m["export_mode"] != "saved_revision" || identifier(&m["instance_id"])? != id {
                return Err("config_source".into());
            }
            revision(&m["revision"])?;
            text(&m["exporter_version"], 64)?;
            time(&m["generated_at"])?;
            if let Some(o) = m.get("runtime_observation") {
                let o = object(
                    o,
                    &["observed_at", "selected_revision", "loaded_revision"],
                    &[],
                )?;
                time(&o["observed_at"])?;
                for k in ["selected_revision", "loaded_revision"] {
                    if !o[k].is_null() {
                        revision(&o[k])?;
                    }
                }
            }
        }
        _ => return Err("config_source".into()),
    }
    Ok(())
}
#[derive(Debug, Clone)]
pub struct Point {
    pub id: String,
    pub db: u16,
    pub size: u32,
    pub offset: u32,
    pub enabled: bool,
}
#[derive(Debug, Clone)]
pub struct Catalog {
    pub path: PathBuf,
    pub sha256: String,
    pub id: String,
    pub protocol: String,
    pub host: String,
    pub port: u16,
    pub rack: u16,
    pub slot: u16,
    pub compatible: bool,
    pub points: Vec<Point>,
    pub declared: HashMap<String, bool>,
}
impl Catalog {
    pub fn load(path: &Path) -> Result<Self> {
        let b = read_file(path, 1048576)?;
        Self::from_bytes(path, &b)
    }
    pub fn from_bytes(path: &Path, b: &[u8]) -> Result<Self> {
        if b.len() > 1048576 {
            return Err("config_size".into());
        }
        let v = parse(b, false)?;
        let m = object(
            &v,
            &[
                "format",
                "schema_version",
                "id",
                "protocol",
                "source",
                "connection",
            ],
            &[
                "name",
                "display_name",
                "description",
                "metadata",
                "dbs",
                "tables",
            ],
        )?;
        if m["format"] != "ff.plc" || integer(&m["schema_version"], 1, 1)? != 1 {
            return Err("config_format".into());
        }
        let id = identifier(&m["id"])?;
        source(&m["source"], id)?;
        descriptions(
            m,
            &[("name", 128), ("display_name", 256), ("description", 1024)],
        )?;
        if let Some(v) = m.get("metadata") {
            let m = object(v, &[], &["brand", "model", "firmware"])?;
            descriptions(m, &[("brand", 128), ("model", 128), ("firmware", 128)])?;
        }
        let protocol = text(&m["protocol"], 16)?;
        let conn = &m["connection"];
        let c = match protocol {
            "s7" => object(
                conn,
                &["host", "port", "rack", "slot"],
                &["local_tsap", "remote_tsap"],
            ),
            "modbus_tcp" => object(conn, &["host", "port", "unit_id"], &[]),
            _ => Err("config_protocol".into()),
        }?;
        let host = text(&c["host"], 15)?;
        let ip = host.parse::<Ipv4Addr>().map_err(|_| "config_host")?;
        if ip.to_string() != host
            || ip.is_unspecified()
            || ip.is_broadcast()
            || ip.is_multicast()
            || ip.octets()[0] == 0
            || ip.octets()[0] >= 240
        {
            return Err("config_host".into());
        }
        let port = integer(&c["port"], 1, 65535)? as u16;
        let (mut rack, mut slot, mut compatible) = (0, 0, protocol == "s7");
        let mut points = Vec::new();
        let mut declared = HashMap::new();
        let mut ids = HashSet::new();
        let mut groups = HashSet::new();
        let info = [
            ("name", 128),
            ("display_name", 256),
            ("source_name", 256),
            ("source_path", 1024),
            ("source_native_type", 32),
        ];
        let common = [
            "enabled",
            "name",
            "display_name",
            "source_name",
            "source_path",
            "source_native_type",
        ];
        if protocol == "s7" {
            if m.contains_key("tables") {
                return Err("config_protocol_fields".into());
            }
            rack = integer(&c["rack"], 0, 7)? as u16;
            slot = integer(&c["slot"], 0, 31)? as u16;
            for (k, default) in [
                ("local_tsap", 256),
                ("remote_tsap", 256 + rack as u64 * 32 + slot as u64),
            ] {
                if let Some(v) = c.get(k) {
                    compatible &= integer(v, 1, 65535)? == default;
                }
            }
            for db in array(m.get("dbs").ok_or("config_fields")?, 1, 64)? {
                let d = object(db, &["number", "size_bytes", "points"], &["enabled"])?;
                let n = integer(&d["number"], 1, 65535)? as u16;
                let size = integer(&d["size_bytes"], 2, 65536)? as u32;
                let on = enabled(d)?;
                if !groups.insert(n) {
                    return Err("config_duplicate_db".into());
                }
                let mut occupied = Vec::new();
                for p in array(&d["points"], 1, 4096)? {
                    let p = object(p, &["id", "data_type", "byte_offset"], &common)?;
                    let pid = identifier(&p["id"])?;
                    if !ids.insert(pid.to_string()) {
                        return Err("config_duplicate_point".into());
                    }
                    descriptions(p, &info)?;
                    if p["data_type"] != "int16" {
                        return Err("config_data_type".into());
                    }
                    let o = integer(&p["byte_offset"], 0, 65534)? as u32;
                    if o + 2 > size {
                        return Err("config_address".into());
                    }
                    if occupied.iter().any(|x: &u32| o < *x + 2 && *x < o + 2) {
                        return Err("config_overlap".into());
                    }
                    declared.insert(pid.to_string(), on && enabled(p)?);
                    occupied.push(o);
                    points.push(Point {
                        id: pid.into(),
                        db: n,
                        size,
                        offset: o,
                        enabled: on && enabled(p)?,
                    });
                }
            }
        } else {
            if m.contains_key("dbs") {
                return Err("config_protocol_fields".into());
            }
            integer(&c["unit_id"], 1, 255)?;
            let mut tables = HashSet::new();
            for t in array(m.get("tables").ok_or("config_fields")?, 1, 4)? {
                let t = object(t, &["table", "points"], &["enabled"])?;
                let table_on = enabled(t)?;
                let name = text(&t["table"], 32)?;
                let read = match name {
                    "coils" => 1,
                    "discrete_inputs" => 2,
                    "holding_registers" => 3,
                    "input_registers" => 4,
                    _ => return Err("config_table".into()),
                };
                if !tables.insert(name) {
                    return Err("config_duplicate_table".into());
                }
                let mut occupied = Vec::new();
                for p in array(&t["points"], 1, 4096)? {
                    let mut opt = common.to_vec();
                    opt.extend(["word_order", "scale"]);
                    let p = object(p, &["id", "pdu_address", "data_type", "functions"], &opt)?;
                    let pid = identifier(&p["id"])?;
                    if !ids.insert(pid.to_string()) {
                        return Err("config_duplicate_point".into());
                    }
                    enabled(p)?;
                    descriptions(p, &info)?;
                    let ty = text(&p["data_type"], 16)?;
                    let boolean = read <= 2;
                    let width = if boolean {
                        if ty != "bool" {
                            return Err("config_data_type".into());
                        }
                        1
                    } else {
                        match ty {
                            "int16" | "uint16" => 1,
                            "int32" | "uint32" | "float32" => 2,
                            _ => return Err("config_data_type".into()),
                        }
                    };
                    if width == 2 {
                        if !matches!(
                            p.get("word_order").and_then(Value::as_str),
                            Some("high_word_first" | "low_word_first")
                        ) {
                            return Err("config_word_order".into());
                        }
                    } else if p.contains_key("word_order") {
                        return Err("config_word_order".into());
                    }
                    if let Some(s) = p.get("scale") {
                        if boolean {
                            return Err("config_scale".into());
                        }
                        let s = object(s, &["factor", "offset"], &[])?;
                        for k in ["factor", "offset"] {
                            let n = s[k].as_f64().ok_or("config_scale")?;
                            if !n.is_finite() || n.abs() > 1e9 || k == "factor" && n == 0.0 {
                                return Err("config_scale".into());
                            }
                        }
                    }
                    let f = object(&p["functions"], &["read", "write"], &[])?;
                    integer(&f["read"], read, read)?;
                    if !f["write"].is_null() {
                        let w = if read == 1 {
                            5
                        } else if read == 3 && width == 1 {
                            6
                        } else {
                            return Err("config_functions".into());
                        };
                        integer(&f["write"], w, w)?;
                    }
                    let o = integer(&p["pdu_address"], 0, 65535)?;
                    if o + width > 65536 {
                        return Err("config_address".into());
                    }
                    if occupied
                        .iter()
                        .any(|(a, w): &(u64, u64)| o < *a + *w && *a < o + width)
                    {
                        return Err("config_overlap".into());
                    }
                    declared.insert(pid.to_string(), table_on && enabled(p)?);
                    occupied.push((o, width));
                }
            }
        }
        if ids.len() > 4096 {
            return Err("config_capacity".into());
        }
        Ok(Self {
            path: if path.is_absolute() {
                path.to_owned()
            } else {
                std::env::current_dir()
                    .map_err(|_| "config_path")?
                    .join(path)
            },
            sha256: format!("{:x}", Sha256::digest(b)),
            id: id.into(),
            protocol: protocol.into(),
            host: host.into(),
            port,
            rack,
            slot,
            compatible,
            points,
            declared,
        })
    }
    pub fn point(&self, id: &str) -> Result<&Point> {
        self.points
            .iter()
            .find(|p| p.id == id && p.enabled)
            .ok_or("config_point".into())
    }
    pub fn file_summary(&self) -> Value {
        serde_json::json!({"path":self.path,"id":self.id,"protocol":self.protocol,"sha256":self.sha256})
    }
    pub fn capability(&self) -> Result<()> {
        if self.protocol != "s7" {
            Err("unsupported_protocol".into())
        } else if !self.compatible {
            Err("unsupported_connection".into())
        } else {
            Ok(())
        }
    }
}
