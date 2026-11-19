//! 逐 PLC 交换合同：从已保存配置验证完整声明，保留停用点和独立语言字段。
use crate::domain::{
    configuration::{hash_bytes, InstanceConfig, Workspace},
    layout, typed_value,
};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::{
    collections::{BTreeSet, HashMap},
    net::Ipv4Addr,
};

// 无效或缺失的客户端数值保留为不可用哨兵，交逐实例校验；绝不转成合法默认端点。
fn invalid_number() -> u32 {
    u32::MAX
}
fn endpoint_number<'de, D: serde::Deserializer<'de>>(d: D) -> Result<u32, D::Error> {
    let value = Value::deserialize(d)?;
    Ok(value
        .as_u64()
        .and_then(|value| u32::try_from(value).ok())
        .unwrap_or_else(invalid_number))
}

#[derive(Clone, Debug, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Target {
    pub instance_id: String,
    pub host: String,
    #[serde(default = "invalid_number", deserialize_with = "endpoint_number")]
    pub port: u32,
    #[serde(default = "invalid_number", deserialize_with = "endpoint_number")]
    pub rack: u32,
    #[serde(default = "invalid_number", deserialize_with = "endpoint_number")]
    pub slot: u32,
    pub connection_confirmed: bool,
    pub loaded_difference_confirmed: bool,
}
#[derive(Clone, Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct Issue {
    pub code: String,
    pub db_id: Option<String>,
    pub point_id: Option<String>,
}
fn valid_id(id: &str) -> bool {
    uuid::Uuid::parse_str(id).is_ok_and(|u| {
        u.to_string() == id && u.get_version_num() == 4 && u.get_variant() == uuid::Variant::RFC4122
    })
}
fn valid_type(kind: &str) -> Option<usize> {
    let width = typed_value::width(kind).ok()?;
    if kind.starts_with("STRING[") && kind != format!("STRING[{}]", width - 2) {
        return None;
    }
    Some(width)
}
fn valid_host(host: &str) -> bool {
    host.parse::<Ipv4Addr>().is_ok_and(|ip| {
        let first = ip.octets()[0];
        host == ip.to_string() && first != 0 && first < 224 && !ip.is_unspecified()
    })
}
/// 保持常规文件的既有缩进；接近上限时使用等价紧凑 JSON，不省略任何字段。
pub fn encode_document(doc: &Value) -> Result<Vec<u8>, String> {
    let pretty = serde_json::to_vec_pretty(doc).map_err(|_| "catalog_format_invalid")?;
    if pretty.len() <= 1024 * 1024 {
        return Ok(pretty);
    }
    let compact = serde_json::to_vec(doc).map_err(|_| "catalog_format_invalid")?;
    if compact.len() > 1024 * 1024 {
        return Err("catalog_capacity".into());
    }
    Ok(compact)
}
/// 所有问题均关联实例下的 DB/点；输出对象只包含合同字段，不含规则/源文件/运行值。
pub fn build(
    workspace: &Workspace,
    instance: &InstanceConfig,
    profile_id: &str,
    revision_id: &str,
    payload: &[u8],
    exported_at: &str,
    target: &Target,
) -> Result<Value, Vec<Issue>> {
    let mut issues = Vec::new();
    let mut add = |code: &str, db: Option<&str>, point: Option<&str>| {
        issues.push(Issue {
            code: code.into(),
            db_id: db.map(str::to_owned),
            point_id: point.map(str::to_owned),
        })
    };
    if !valid_id(profile_id) || !valid_id(revision_id) || !valid_id(&instance.id) {
        add("catalog_identity", None, None);
    }
    if instance.name.trim().is_empty() || instance.name.len() > 100 {
        add("catalog_plc_name", None, None);
    }
    if !target.connection_confirmed
        || !valid_host(&target.host)
        || !(1..=65535).contains(&target.port)
        || target.rack > 7
        || target.slot > 31
        || instance.calling_tsap == 0
    {
        add("catalog_connection", None, None);
    }
    if instance.names_confirmation.as_ref() != Some(&layout::names_signature(instance)) {
        add("catalog_names_unconfirmed", None, None);
    }
    if instance.dbs.is_empty()
        || instance.dbs.len() > 32
        || instance.dbs.iter().map(|d| d.points.len()).sum::<usize>() > 4096
    {
        add("catalog_capacity", None, None);
    }
    let catalog = instance.catalog.as_ref().and_then(|binding| {
        workspace
            .source_versions
            .iter()
            .find(|s| s.version_id == binding.source_version_id)
            .and_then(|s| parse(&s.bytes).ok())
    });
    let verified_catalog =
        instance.catalog.is_some() && catalog.is_some() && verify_bindings(workspace).is_ok();
    if instance.catalog.is_some() && !verified_catalog {
        add("catalog_source_unverified", None, None);
    }
    let origin = catalog.as_ref().map(|c| json!(c.origin)).unwrap_or_else(
        || json!({"kind":"device_simulator","profile_id":profile_id,"plc_id":instance.id}),
    );
    let mut ids = BTreeSet::from([origin["plc_id"].as_str().unwrap_or("").to_string()]);
    let mut numbers = BTreeSet::new();
    let mut names = BTreeSet::new();
    let mut dbs = Vec::new();
    for db in &instance.dbs {
        let d = Some(db.id.as_str());
        let mapping = instance
            .catalog
            .as_ref()
            .and_then(|c| c.dbs.iter().find(|m| m.local_db_id == db.id));
        let external_db_id = mapping.map(|m| m.catalog_db_id.as_str()).unwrap_or(&db.id);
        if !valid_id(external_db_id)
            || !ids.insert(external_db_id.to_string())
            || db.number == 0
            || !numbers.insert(db.number)
            || db.name.trim().is_empty()
            || db.name.len() > 100
            || !(1..=65536).contains(&db.length)
            || db.points.is_empty()
        {
            add("catalog_db_invalid", d, None);
        }
        if db.address_confirmation.as_ref().is_none_or(|c| {
            c.structure_sha256 != layout::structure_signature(db)
                || c.layout_sha256 != layout::layout_signature(db)
        }) {
            add("catalog_layout_unconfirmed", d, None);
        }
        let leaves = db.binding.as_ref().map(|binding| {
            let tree = binding
                .tree
                .iter()
                .map(aiis_tia_import_core::FieldNode::from)
                .collect::<Vec<_>>();
            aiis_tia_import_core::structured_leaves(&tree)
        });
        if let Some(binding) = &db.binding {
            if !binding.standard
                || leaves.as_ref().is_none_or(|v| v.len() != db.points.len())
                || !workspace
                    .source_versions
                    .iter()
                    .any(|v| v.version_id == binding.declaration.version_id)
            {
                add("catalog_source_unverified", d, None);
            }
        } else if !db.manual && mapping.is_none() {
            add("catalog_source_unverified", d, None);
        }
        let mut spans = Vec::new();
        let mut points = Vec::new();
        let external_points = mapping
            .map(|m| {
                m.points
                    .iter()
                    .map(|p| (p.local_point_id.as_str(), p.catalog_point_id.as_str()))
                    .collect::<HashMap<_, _>>()
            })
            .unwrap_or_default();
        let original_points = catalog
            .as_ref()
            .and_then(|c| c.dbs.iter().find(|d| d.id == external_db_id))
            .map(|d| {
                d.points
                    .iter()
                    .map(|p| (p.id.as_str(), p))
                    .collect::<HashMap<_, _>>()
            })
            .unwrap_or_default();
        for p in &db.points {
            let point = Some(p.id.as_str());
            let external_point_id = external_points.get(p.id.as_str()).copied().unwrap_or(&p.id);
            let original = original_points.get(external_point_id).copied();
            if !valid_id(external_point_id) || !ids.insert(external_point_id.to_string()) {
                add("catalog_identity", d, point);
            }
            if aiis_tia_import_core::validate_manual_name(&p.name).is_err()
                || !names.insert(p.name.clone())
            {
                add("catalog_point_name", d, point);
            }
            let width = valid_type(&p.data_type);
            if width.is_none() {
                add("catalog_type", d, point);
            }
            let source_ok = if mapping.is_some() && catalog.is_some() {
                verified_catalog
            } else if let Some(leaves) = &leaves {
                leaves
                    .iter()
                    .filter(|leaf| {
                        leaf.path == p.source_path
                            && leaf.data_type == p.data_type
                            && leaf
                                .segments
                                .iter()
                                .map(crate::domain::source::PathSegment::from)
                                .collect::<Vec<_>>()
                                == p.segments
                    })
                    .count()
                    == 1
            } else {
                p.source_path.is_empty() && p.segments.is_empty()
            };
            if !source_ok || p.source_path.len() > 512 {
                add("catalog_source_unverified", d, point);
            }
            let zh = p
                .display_names
                .as_ref()
                .map(|v| v.zh_cn.as_str())
                .unwrap_or("");
            let en = p
                .display_names
                .as_ref()
                .map(|v| v.en_us.as_str())
                .unwrap_or("");
            let description = p.description.as_deref().unwrap_or("");
            if p.display_name.len() > 256
                || zh.len() > 256
                || en.len() > 256
                || description.len() > 500
            {
                add("catalog_text_limit", d, point);
            }
            if let (Some(byte), Some(width)) = (p.byte, width) {
                let valid_bit = if p.data_type == "BOOL" {
                    p.bit.is_some_and(|bit| bit < 8)
                } else {
                    p.bit.is_none()
                };
                if !valid_bit
                    || byte
                        .checked_add(width as u32)
                        .is_none_or(|end| end > db.length)
                {
                    add("catalog_address", d, point);
                } else {
                    let first = byte * 8 + u32::from(p.bit.unwrap_or(0));
                    spans.push((
                        first,
                        first
                            + if p.data_type == "BOOL" {
                                1
                            } else {
                                width as u32 * 8
                            },
                        p.id.clone(),
                    ));
                }
            } else {
                add("catalog_address", d, point);
            }
            let mut item = json!({"id":external_point_id,"name":p.name,"display_names":{"zh-CN":zh,"en-US":en},
                "description":description,"data_type":p.data_type,"byte_offset":p.byte,"source_enabled":p.enabled});
            if !p.display_name.is_empty() || original.is_some_and(|v| v.display_name.is_some()) {
                item["display_name"] = json!(p.display_name);
            }
            if source_ok
                && (!p.source_path.is_empty() || original.is_some_and(|v| v.source_path.is_some()))
            {
                item["source_path"] = json!(p.source_path);
            }
            if let Some(bit) = p.bit {
                item["bit"] = json!(bit);
            }
            points.push(item);
        }
        spans.sort_by_key(|v| v.0);
        for pair in spans.windows(2) {
            if pair[0].1 > pair[1].0 {
                add("catalog_overlap", d, Some(&pair[1].2));
            }
        }
        dbs.push(
            json!({"id":external_db_id,"name":db.name,"number":db.number,"size_bytes":db.length,
            "source_enabled":db.enabled,"points":points}),
        );
    }
    if !issues.is_empty() {
        return Err(issues);
    }
    let default_remote = 0x100 + target.rack * 32 + target.slot;
    let mut connection =
        json!({"host":target.host,"port":target.port,"rack":target.rack,"slot":target.slot});
    if instance.calling_tsap != 0x100 {
        connection["local_tsap"] = json!(instance.calling_tsap);
    }
    if u32::from(instance.called_tsap()) != default_remote {
        connection["remote_tsap"] = json!(instance.called_tsap());
    }
    let doc = json!({"format":"aiis.plc_points","schema_version":1,
        "origin":origin,
        "export":{"producer":"device_simulator","profile_id":profile_id,"config_state":"saved_revision",
            "revision_id":revision_id,"payload_sha256":hash_bytes(payload),"exported_at":exported_at},
        "plc":{"name":instance.name,"protocol":"s7","connection":connection},"dbs":dbs});
    if encode_document(&doc).is_err() {
        return Err(vec![Issue {
            code: "catalog_capacity".into(),
            db_id: None,
            point_id: None,
        }]);
    }
    Ok(doc)
}

// 目录原文保持为 source_versions 中唯一的不可变来源；绑定只保存本地与外部身份。
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct CatalogBinding {
    pub source_version_id: String,
    pub source_sha256: String,
    pub dbs: Vec<CatalogDbMapping>,
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct CatalogDbMapping {
    pub local_db_id: String,
    pub catalog_db_id: String,
    pub points: Vec<CatalogPointMapping>,
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct CatalogPointMapping {
    pub local_point_id: String,
    pub catalog_point_id: String,
}
fn present<'de, D: serde::Deserializer<'de>, T: Deserialize<'de>>(
    d: D,
) -> Result<Option<T>, D::Error> {
    T::deserialize(d).map(Some)
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord)]
#[serde(deny_unknown_fields)]
pub struct CatalogOrigin {
    pub kind: String,
    pub profile_id: String,
    pub plc_id: String,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CatalogExport {
    pub producer: String,
    pub profile_id: String,
    pub config_state: String,
    pub revision_id: String,
    pub payload_sha256: String,
    pub exported_at: String,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CatalogConnection {
    pub host: String,
    pub port: u16,
    pub rack: u8,
    pub slot: u8,
    #[serde(
        default,
        deserialize_with = "present",
        skip_serializing_if = "Option::is_none"
    )]
    pub local_tsap: Option<u16>,
    #[serde(
        default,
        deserialize_with = "present",
        skip_serializing_if = "Option::is_none"
    )]
    pub remote_tsap: Option<u16>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CatalogPlc {
    pub name: String,
    pub protocol: String,
    pub connection: CatalogConnection,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CatalogPoint {
    pub id: String,
    pub name: String,
    #[serde(
        default,
        deserialize_with = "present",
        skip_serializing_if = "Option::is_none"
    )]
    pub display_name: Option<String>,
    #[serde(
        default,
        deserialize_with = "present",
        skip_serializing_if = "Option::is_none"
    )]
    pub display_names: Option<super::configuration::DisplayNames>,
    #[serde(
        default,
        deserialize_with = "present",
        skip_serializing_if = "Option::is_none"
    )]
    pub description: Option<String>,
    #[serde(
        default,
        deserialize_with = "present",
        skip_serializing_if = "Option::is_none"
    )]
    pub source_path: Option<String>,
    pub data_type: String,
    pub byte_offset: u32,
    #[serde(
        default,
        deserialize_with = "present",
        skip_serializing_if = "Option::is_none"
    )]
    pub bit: Option<u8>,
    pub source_enabled: bool,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CatalogDb {
    pub id: String,
    pub name: String,
    pub number: u16,
    pub size_bytes: u32,
    #[serde(
        default,
        deserialize_with = "present",
        skip_serializing_if = "Option::is_none"
    )]
    pub source_enabled: Option<bool>,
    pub points: Vec<CatalogPoint>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CatalogDocument {
    pub format: String,
    pub schema_version: u32,
    pub origin: CatalogOrigin,
    pub export: CatalogExport,
    pub plc: CatalogPlc,
    pub dbs: Vec<CatalogDb>,
}

fn valid_time(s: &str) -> bool {
    let b = s.as_bytes();
    if b.len() < 25
        || !s.ends_with("+08:00")
        || b.get(4) != Some(&b'-')
        || b.get(7) != Some(&b'-')
        || !matches!(b.get(10), Some(b'T' | b't'))
        || b.get(13) != Some(&b':')
        || b.get(16) != Some(&b':')
    {
        return false;
    }
    let number = |a: usize, z: usize| -> Option<u32> {
        let x = b.get(a..z)?;
        if !x.iter().all(u8::is_ascii_digit) {
            return None;
        }
        std::str::from_utf8(x).ok()?.parse().ok()
    };
    let (Some(y), Some(m), Some(d), Some(h), Some(min), Some(sec)) = (
        number(0, 4),
        number(5, 7),
        number(8, 10),
        number(11, 13),
        number(14, 16),
        number(17, 19),
    ) else {
        return false;
    };
    let mdays = match m {
        1 | 3 | 5 | 7 | 8 | 10 | 12 => 31,
        4 | 6 | 9 | 11 => 30,
        2 if y % 4 == 0 && (y % 100 != 0 || y % 400 == 0) => 29,
        2 => 28,
        _ => return false,
    };
    let fraction = &b[19..b.len() - 6];
    d > 0
        && d <= mdays
        && h < 24
        && min < 60
        && sec <= 60
        && (fraction.is_empty()
            || (fraction.len() > 1
                && fraction[0] == b'.'
                && fraction[1..].iter().all(u8::is_ascii_digit)))
}
fn depth_ok(bytes: &[u8]) -> bool {
    let (mut depth, mut string, mut escaped) = (0usize, false, false);
    for b in bytes {
        if string {
            if escaped {
                escaped = false;
            } else if *b == b'\\' {
                escaped = true;
            } else if *b == b'"' {
                string = false;
            }
        } else {
            match b {
                b'"' => string = true,
                b'{' | b'[' => {
                    depth += 1;
                    if depth > 16 {
                        return false;
                    }
                }
                b'}' | b']' => {
                    let Some(n) = depth.checked_sub(1) else {
                        return false;
                    };
                    depth = n;
                }
                _ => {}
            }
        }
    }
    depth == 0 && !string
}
/// 对整份交换文件严格校验，包括停用点；导出 payload 摘要是来源声明，不是文件摘要。
pub fn parse(bytes: &[u8]) -> Result<CatalogDocument, String> {
    if bytes.is_empty() || bytes.len() > 1024 * 1024 {
        return Err("catalog_size_invalid".into());
    }
    if bytes.starts_with(&[0xef, 0xbb, 0xbf]) || std::str::from_utf8(bytes).is_err() {
        return Err("catalog_encoding_invalid".into());
    }
    if !depth_ok(bytes) {
        return Err("catalog_depth_invalid".into());
    }
    let c: CatalogDocument = serde_json::from_slice(bytes).map_err(|_| "catalog_format_invalid")?;
    let e = &c.export;
    let conn = &c.plc.connection;
    if c.format != "aiis.plc_points"
        || c.schema_version != 1
        || !matches!(
            c.origin.kind.as_str(),
            "device_simulator" | "data_acquisition_agent"
        )
        || !valid_id(&c.origin.profile_id)
        || !valid_id(&c.origin.plc_id)
        || !valid_id(&e.profile_id)
        || !valid_id(&e.revision_id)
        || !match e.producer.as_str() {
            "device_simulator" => e.config_state == "saved_revision",
            "data_acquisition_agent" => {
                matches!(e.config_state.as_str(), "saved_draft" | "active_revision")
            }
            _ => false,
        }
        || e.payload_sha256.len() != 64
        || !e
            .payload_sha256
            .bytes()
            .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
        || !valid_time(&e.exported_at)
        || c.plc.name.trim().is_empty()
        || c.plc.name.len() > 100
        || c.plc.protocol != "s7"
        || c.dbs.is_empty()
        || c.dbs.len() > 32
    {
        return Err("catalog_metadata_invalid".into());
    }
    if !valid_host(&conn.host)
        || conn.port == 0
        || conn.rack > 7
        || conn.slot > 31
        || conn.local_tsap == Some(0)
        || conn.remote_tsap == Some(0)
    {
        return Err("catalog_connection_invalid".into());
    }
    let mut ids = BTreeSet::from([c.origin.plc_id.clone()]);
    let mut numbers = BTreeSet::new();
    let mut names = BTreeSet::new();
    let mut count = 0usize;
    for db in &c.dbs {
        if !valid_id(&db.id)
            || !ids.insert(db.id.clone())
            || db.number == 0
            || !numbers.insert(db.number)
            || db.name.trim().is_empty()
            || db.name.len() > 100
            || !(1..=65536).contains(&db.size_bytes)
            || db.points.is_empty()
            || (e.producer == "device_simulator" && db.source_enabled.is_none())
            || (e.producer == "data_acquisition_agent" && db.source_enabled.is_some())
        {
            return Err("catalog_db_invalid".into());
        }
        let mut spans = Vec::new();
        for p in &db.points {
            count += 1;
            if count > 4096
                || !valid_id(&p.id)
                || !ids.insert(p.id.clone())
                || aiis_tia_import_core::validate_manual_name(&p.name).is_err()
                || !names.insert(p.name.clone())
                || p.display_name.as_ref().is_some_and(|v| v.len() > 256)
                || p.display_names
                    .as_ref()
                    .is_some_and(|v| v.zh_cn.len() > 256 || v.en_us.len() > 256)
                || p.description.as_ref().is_some_and(|v| v.len() > 500)
                || p.source_path.as_ref().is_some_and(|v| v.len() > 512)
            {
                return Err("catalog_point_invalid".into());
            }
            let width = valid_type(&p.data_type).ok_or("catalog_type_invalid")? as u32;
            if p.byte_offset
                .checked_add(width)
                .is_none_or(|n| n > db.size_bytes)
                || (p.data_type == "BOOL" && !p.bit.is_some_and(|n| n < 8))
                || (p.data_type != "BOOL" && p.bit.is_some())
            {
                return Err("catalog_address_invalid".into());
            }
            let first = p.byte_offset * 8 + u32::from(p.bit.unwrap_or(0));
            spans.push((
                first,
                first + if p.data_type == "BOOL" { 1 } else { width * 8 },
            ));
        }
        spans.sort();
        if spans.windows(2).any(|w| w[0].1 > w[1].0) {
            return Err("catalog_address_overlap".into());
        }
    }
    Ok(c)
}

/// 重验原字节、全部 DB/点和映射；本地显示元数据与启用/策略可独立调整。
pub fn verify_bindings(w: &Workspace) -> Result<(), String> {
    let mut origins = BTreeSet::new();
    let mut sources = BTreeSet::new();
    for i in &w.instances {
        let Some(binding) = &i.catalog else { continue };
        let source = w
            .source_versions
            .iter()
            .find(|s| s.version_id == binding.source_version_id)
            .ok_or("catalog_source_invalid")?;
        if source.import_profile != "plc_catalog_v1"
            || source.blob_sha256 != binding.source_sha256
            || hash_bytes(&source.bytes) != binding.source_sha256
            || !sources.insert(&source.version_id)
        {
            return Err("catalog_source_invalid".into());
        }
        let c = parse(&source.bytes)?;
        if !origins.insert(c.origin.clone())
            || i.dbs.len() != c.dbs.len()
            || binding.dbs.len() != c.dbs.len()
        {
            return Err("catalog_binding_invalid".into());
        }
        let mut local = BTreeSet::new();
        let mut external = BTreeSet::new();
        for map in &binding.dbs {
            let db = i
                .dbs
                .iter()
                .find(|d| d.id == map.local_db_id)
                .ok_or("catalog_binding_invalid")?;
            let src = c
                .dbs
                .iter()
                .find(|d| d.id == map.catalog_db_id)
                .ok_or("catalog_binding_invalid")?;
            if !local.insert(&map.local_db_id)
                || !external.insert(&map.catalog_db_id)
                || db.binding.is_some()
                || db.manual
                || db.name != src.name
                || db.number != src.number
                || db.length != src.size_bytes
                || db.points.len() != src.points.len()
                || map.points.len() != src.points.len()
            {
                return Err("catalog_binding_invalid".into());
            }
            let mut lp = BTreeSet::new();
            let mut ep = BTreeSet::new();
            let local_points = db
                .points
                .iter()
                .map(|p| (p.id.as_str(), p))
                .collect::<HashMap<_, _>>();
            let source_points = src
                .points
                .iter()
                .map(|p| (p.id.as_str(), p))
                .collect::<HashMap<_, _>>();
            for point_map in &map.points {
                let p = local_points
                    .get(point_map.local_point_id.as_str())
                    .ok_or("catalog_binding_invalid")?;
                let original = source_points
                    .get(point_map.catalog_point_id.as_str())
                    .ok_or("catalog_binding_invalid")?;
                if !lp.insert(&point_map.local_point_id)
                    || !ep.insert(&point_map.catalog_point_id)
                    || p.name != original.name
                    || p.data_type != original.data_type
                    || p.byte != Some(original.byte_offset)
                    || p.bit != original.bit
                    || p.source_path != original.source_path.as_deref().unwrap_or("")
                    || !p.segments.is_empty()
                    || p.manual
                {
                    return Err("catalog_binding_invalid".into());
                }
            }
        }
    }
    Ok(())
}
