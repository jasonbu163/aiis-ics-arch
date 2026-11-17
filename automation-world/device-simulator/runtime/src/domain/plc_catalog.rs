//! 逐 PLC 交换合同：从已保存配置验证完整声明，保留停用点和独立语言字段。
use crate::domain::{
    configuration::{hash_bytes, InstanceConfig, Workspace},
    layout, typed_value,
};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::{collections::BTreeSet, net::Ipv4Addr};

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
    let mut ids = BTreeSet::new();
    let mut numbers = BTreeSet::new();
    let mut names = BTreeSet::new();
    let mut dbs = Vec::new();
    for db in &instance.dbs {
        let d = Some(db.id.as_str());
        if !valid_id(&db.id)
            || !ids.insert(db.id.clone())
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
        } else if !db.manual {
            add("catalog_source_unverified", d, None);
        }
        let mut spans = Vec::new();
        let mut points = Vec::new();
        for p in &db.points {
            let point = Some(p.id.as_str());
            if !valid_id(&p.id) || !ids.insert(p.id.clone()) {
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
            let source_ok = if let Some(leaves) = &leaves {
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
            let mut item = json!({"id":p.id,"name":p.name,"display_names":{"zh-CN":zh,"en-US":en},
                "description":description,"data_type":p.data_type,"byte_offset":p.byte,"source_enabled":p.enabled});
            if !p.display_name.is_empty() {
                item["display_name"] = json!(p.display_name);
            }
            if !p.source_path.is_empty() && source_ok {
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
            json!({"id":db.id,"name":db.name,"number":db.number,"size_bytes":db.length,
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
        "origin":{"kind":"device_simulator","profile_id":profile_id,"plc_id":instance.id},
        "export":{"producer":"device_simulator","profile_id":profile_id,"config_state":"saved_revision",
            "revision_id":revision_id,"payload_sha256":hash_bytes(payload),"exported_at":exported_at},
        "plc":{"name":instance.name,"protocol":"s7","connection":connection},"dbs":dbs});
    if serde_json::to_vec_pretty(&doc).map_or(true, |bytes| bytes.len() > 1024 * 1024) {
        return Err(vec![Issue {
            code: "catalog_capacity".into(),
            db_id: None,
            point_id: None,
        }]);
    }
    Ok(doc)
}
