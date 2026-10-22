//! 本地配置v1：稳定身份、完整结构、唯一启用与跨DB采集组准入；不依赖设备或SQL。
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};
pub(crate) type LocalResult<T> = Result<T, String>;
pub(crate) fn id() -> String {
    uuid::Uuid::new_v4().to_string()
}
pub(crate) fn valid_id(s: &str) -> bool {
    uuid::Uuid::parse_str(s)
        .map(|v| v.get_version_num() == 4)
        .unwrap_or(false)
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct Configuration {
    pub schema_version: u32,
    pub plcs: Vec<Plc>,
    pub dbs: Vec<Db>,
    pub points: Vec<Point>,
    pub groups: Vec<Group>,
    pub sources: Vec<SourceDocument>,
    pub storage: StoragePolicy,
}
impl Default for Configuration {
    fn default() -> Self {
        Self {
            schema_version: 1,
            plcs: vec![],
            dbs: vec![],
            points: vec![],
            groups: vec![],
            sources: vec![],
            storage: StoragePolicy::default(),
        }
    }
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct Plc {
    pub id: String,
    pub name: String,
    pub enabled: bool,
    pub host: String,
    pub port: u16,
    pub rack: u8,
    pub slot: u8,
    pub connect_timeout_ms: u32,
    pub io_timeout_ms: u32,
    pub deadline_ms: u32,
}
impl Plc {
    pub fn endpoint(&self) -> String {
        format!("{}:{}:{}/{}", self.host, self.port, self.rack, self.slot)
    }
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct StoragePolicy {
    pub quota_bytes: u64,
    pub retention_days: u32,
}
impl Default for StoragePolicy {
    fn default() -> Self {
        Self {
            quota_bytes: 1024 * 1024 * 1024,
            retention_days: 7,
        }
    }
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct SourceDocument {
    pub id: String,
    pub name: String,
    pub content: String,
    pub sha256: String,
    pub plc_id: String,
    pub db_number: Option<u16>,
    pub diagnostics: Vec<Issue>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub lineage_id: Option<String>,
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct FieldNode {
    pub name: String,
    pub path: String,
    pub data_type: String,
    pub line: usize,
    pub comment: String,
    pub lower: Option<i32>,
    pub upper: Option<i32>,
    pub children: Vec<FieldNode>,
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct Db {
    pub id: String,
    pub plc_id: String,
    pub source_id: String,
    pub name: String,
    pub number: u16,
    pub length: u32,
    pub complete: bool,
    pub flat: bool,
    pub tree: Vec<FieldNode>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub import_binding: Option<super::source_import::ImportBinding>,
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct Address {
    pub offset: u32,
    pub bit: Option<u8>,
    pub confirmed: bool,
    pub origin: String,
    pub reason: String,
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct Point {
    pub id: String,
    pub plc_id: String,
    pub db_id: String,
    pub source_path: String,
    pub name: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub name_mode: Option<super::point_naming::NameMode>,
    pub data_type: String,
    pub comment: String,
    pub enabled: bool,
    pub group_id: Option<String>,
    pub address: Option<Address>,
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct Group {
    pub id: String,
    pub plc_id: String,
    pub name: String,
    pub enabled: bool,
    pub interval_ms: u64,
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub(crate) struct Issue {
    pub code: String,
    pub path: String,
    pub line: usize,
    pub file: String,
}
pub(crate) fn issue(code: &str, path: &str) -> Issue {
    Issue {
        code: code.into(),
        path: path.into(),
        line: 0,
        file: String::new(),
    }
}
pub(crate) fn width(t: &str) -> Option<u32> {
    match t {
        "BOOL" | "BYTE" | "USINT" | "CHAR" => Some(1),
        "INT" | "UINT" | "WORD" => Some(2),
        "DINT" | "UDINT" | "DWORD" | "REAL" => Some(4),
        _ => t
            .strip_prefix("STRING[")
            .and_then(|v| v.strip_suffix(']'))
            .and_then(|v| v.parse::<u32>().ok())
            .filter(|n| *n >= 1 && *n <= 254)
            .map(|n| n + 2),
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct Segment {
    pub db_number: u16,
    pub start: u32,
    pub size: u32,
}
pub(crate) fn segments(c: &Configuration, g: &Group) -> LocalResult<Vec<Segment>> {
    let mut intervals: BTreeMap<u16, Vec<(u32, u32)>> = BTreeMap::new();
    for p in c
        .points
        .iter()
        .filter(|p| p.enabled && p.group_id.as_deref() == Some(&g.id))
    {
        let a = p.address.as_ref().ok_or("address_required")?;
        let d = c.dbs.iter().find(|d| d.id == p.db_id).ok_or("db_missing")?;
        let end = a
            .offset
            .checked_add(width(&p.data_type).ok_or("unsupported_type")?)
            .ok_or("address_invalid")?;
        if end > 65536 {
            return Err("address_invalid".into());
        }
        intervals.entry(d.number).or_default().push((a.offset, end));
    }
    let mut out = vec![];
    for (db, mut ranges) in intervals {
        ranges.sort();
        let mut merged: Vec<(u32, u32)> = vec![];
        for (s, e) in ranges {
            if let Some(last) = merged.last_mut() {
                if s <= last.1 {
                    last.1 = last.1.max(e);
                    continue;
                }
            }
            merged.push((s, e));
        }
        for (mut s, e) in merged {
            while s < e {
                let size = (e - s).min(200);
                out.push(Segment {
                    db_number: db,
                    start: s,
                    size,
                });
                s += size;
            }
        }
    }
    Ok(out)
}
fn leaf_matches(nodes: &[FieldNode], path: &str, typ: &str) -> bool {
    nodes.iter().any(|n| {
        if n.children.is_empty() {
            n.path == path && n.data_type == typ
        } else {
            leaf_matches(&n.children, path, typ)
        }
    })
}
pub(crate) fn validate(c: &Configuration) -> Vec<Issue> {
    let mut out = vec![];
    let mut err = |code: &str, path: &str| out.push(issue(code, path));
    if c.schema_version != 1
        || c.plcs.len() > 4
        || c.storage.quota_bytes < 128 * 1024 * 1024
        || c.storage.quota_bytes > 64 * 1024 * 1024 * 1024
        || !(1..=30).contains(&c.storage.retention_days)
    {
        err("configuration_limits", "");
    }
    let mut ids = BTreeSet::new();
    let mut endpoints = BTreeSet::new();
    for p in &c.plcs {
        if !valid_id(&p.id) || !ids.insert(p.id.clone()) {
            err("duplicate_or_invalid_id", &p.id)
        }
        if p.name.is_empty()
            || p.name.len() > 100
            || p.host.parse::<std::net::Ipv4Addr>().is_err()
            || p.port == 0
            || p.rack > 7
            || p.slot > 31
            || p.connect_timeout_ms != 1000
            || p.io_timeout_ms != 500
            || p.deadline_ms != 5000
        {
            err("plc_invalid", &p.id)
        }
        if !endpoints.insert(p.endpoint()) {
            err("duplicate_endpoint", &p.id)
        }
        if c.dbs.iter().filter(|d| d.plc_id == p.id).count() > 32
            || c.points.iter().filter(|d| d.plc_id == p.id).count() > 4096
            || c.groups.iter().filter(|d| d.plc_id == p.id).count() > 8
        {
            err("plc_limits", &p.id)
        }
    }
    for g in &c.groups {
        if !valid_id(&g.id)
            || !ids.insert(g.id.clone())
            || !c.plcs.iter().any(|p| p.id == g.plc_id)
            || !(500..=3_600_000).contains(&g.interval_ms)
            || g.name.len() > 100
        {
            err("group_invalid", &g.id)
        }
        let ps: Vec<_> = c
            .points
            .iter()
            .filter(|p| p.enabled && p.group_id.as_deref() == Some(&g.id))
            .collect();
        if ps.len() > 256 {
            err("group_limits", &g.id)
        }
        if let Ok(s) = segments(c, g) {
            if s.len() > 32 || s.iter().map(|s| s.size).sum::<u32>() > 6400 {
                err("read_budget", &g.id)
            }
        }
        // Conservative encoded upper bound includes duplicated point definitions, maximum ASCII values and manifest keys.
        let encoded = ps
            .iter()
            .map(|p| {
                serde_json::to_vec(p)
                    .map(|b| {
                        b.len() * 2
                            + if p.data_type.starts_with("STRING[") {
                                254 * 6 + 1024
                            } else {
                                1024
                            }
                    })
                    .unwrap_or(usize::MAX / 512)
            })
            .sum::<usize>()
            + 8192;
        if encoded > 512 * 1024 {
            err("encoding_budget", &g.id)
        }
    }

    for src in &c.sources {
        if !valid_id(&src.id)
            || !ids.insert(src.id.clone())
            || !c.plcs.iter().any(|p| p.id == src.plc_id)
            || src.content.len() > 1024 * 1024
            || src
                .lineage_id
                .as_deref()
                .map(|l| !valid_id(l))
                .unwrap_or(false)
            || src.sha256 != super::local_sample::digest(&src.content)
        {
            err("source_invalid", &src.id)
        }
    }
    let mut dbnums = BTreeSet::new();
    for d in &c.dbs {
        if !valid_id(&d.id)
            || !ids.insert(d.id.clone())
            || !c.plcs.iter().any(|p| p.id == d.plc_id)
            || d.number == 0
            || d.length == 0
            || d.length > 65536
            || !c.sources.iter().any(|s| {
                s.id == d.source_id
                    && s.plc_id == d.plc_id
                    && (d
                        .import_binding
                        .as_ref()
                        .map(|b| {
                            b.lineage_id == s.lineage_id.as_deref().unwrap_or(&s.id)
                                && b.block_key.kind == "DATA_BLOCK"
                                && b.block_key.name == d.name
                                && b.udt_source_ids.iter().all(|i| {
                                    c.sources.iter().any(|u| u.id == *i && u.plc_id == d.plc_id)
                                })
                        })
                        .unwrap_or(false)
                        || s.db_number == Some(d.number)
                        || s.name.ends_with(".yaml")
                        || s.name.ends_with(".yml"))
            })
            || !dbnums.insert((d.plc_id.clone(), d.number))
        {
            err("db_invalid", &d.id)
        }
    }
    let mut occupied: BTreeMap<(String, u32, u8), String> = BTreeMap::new();
    for p in &c.points {
        if !valid_id(&p.id)
            || !ids.insert(p.id.clone())
            || p.name.len() > 100
            || p.comment.len() > 500
            || p.source_path.len() > 512
        {
            err("point_invalid", &p.id)
        }
        let db = c
            .dbs
            .iter()
            .find(|d| d.id == p.db_id && d.plc_id == p.plc_id);
        if db.is_none() {
            err("db_missing", &p.id)
        }
        if let Some(g) = &p.group_id {
            if !c.groups.iter().any(|x| x.id == *g && x.plc_id == p.plc_id) {
                err("cross_plc_group", &p.id)
            }
        }
        if p.enabled && p.group_id.is_none() {
            err("group_required", &p.id)
        }
        if let Some(mode) = &p.name_mode {
            use super::point_naming::NameMode;
            if *mode == NameMode::Pending {
                if !p.name.is_empty() {
                    err("point_name_invalid", &p.id)
                }
                if p.enabled {
                    err("point_name_pending", &p.id)
                }
            } else if aiis_tia_import_core::validate_manual_name(&p.name).is_err() {
                err("point_name_invalid", &p.id)
            }
            if !p.name.is_empty()
                && c.points.iter().any(|other| {
                    other.id != p.id && other.plc_id == p.plc_id && other.name == p.name
                })
            {
                err("point_name_conflict", &p.id)
            }
        }
        if !p.enabled {
            continue;
        }
        let Some(w) = width(&p.data_type) else {
            err("unsupported_type", &p.id);
            continue;
        };
        if db.map(|d| !d.complete).unwrap_or(true) {
            err("incomplete_source", &p.id)
        }
        if !db
            .map(|d| leaf_matches(&d.tree, &p.source_path, &p.data_type))
            .unwrap_or(false)
        {
            err("point_source_mismatch", &p.id)
        }
        let Some(a) = &p.address else {
            err("address_required", &p.id);
            continue;
        };
        if !a.confirmed
            || a.reason.trim().is_empty()
            || !matches!(a.origin.as_str(), "manual" | "inferred")
            || a.offset
                .checked_add(w)
                .map(|e| e > 65536 || db.map(|d| e > d.length).unwrap_or(true))
                .unwrap_or(true)
            || (p.data_type == "BOOL" && a.bit.map(|b| b > 7).unwrap_or(true))
            || (p.data_type != "BOOL" && a.bit.is_some())
        {
            err("address_invalid", &p.id);
            continue;
        }
        for byte in a.offset..a.offset + w {
            for bit in 0..8 {
                if p.data_type == "BOOL" && a.bit != Some(bit) {
                    continue;
                }
                if occupied
                    .insert((p.db_id.clone(), byte, bit), p.id.clone())
                    .is_some()
                {
                    err("address_overlap", &p.id)
                }
            }
        }
    }
    out
}
