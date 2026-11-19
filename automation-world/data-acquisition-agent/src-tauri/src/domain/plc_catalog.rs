//! 逐 PLC 交换目录的封闭解析和全点布局校验；不读取文件、连接设备或写存储。
use super::{
    local_configuration::{Configuration, PointDisplayNames},
    local_sample::digest,
};
use serde::{Deserialize, Deserializer, Serialize};
use std::collections::{BTreeMap, BTreeSet};

fn present<'de, D, T>(d: D) -> Result<Option<T>, D::Error>
where
    D: Deserializer<'de>,
    T: Deserialize<'de>,
{
    T::deserialize(d).map(Some)
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub(crate) struct Catalog {
    pub format: String,
    pub schema_version: u32,
    pub origin: Origin,
    pub export: Export,
    pub plc: CatalogPlc,
    pub dbs: Vec<CatalogDb>,
}
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq, Eq, PartialOrd, Ord)]
#[serde(deny_unknown_fields)]
pub(crate) struct Origin {
    pub kind: String,
    pub profile_id: String,
    pub plc_id: String,
}
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub(crate) struct Export {
    pub producer: String,
    pub profile_id: String,
    pub config_state: String,
    pub revision_id: String,
    pub payload_sha256: String,
    pub exported_at: String,
}
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub(crate) struct CatalogPlc {
    pub name: String,
    pub protocol: String,
    pub connection: Connection,
}
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub(crate) struct Connection {
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
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub(crate) struct CatalogDb {
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
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub(crate) struct CatalogPoint {
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
    pub display_names: Option<PointDisplayNames>,
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

/// 配置只保存身份绑定；源事实以归档的完整原文为准。
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct CatalogBinding {
    pub local_db_id: String,
    pub source_id: String,
    pub source_sha256: String,
    pub source_kind: String,
    pub origin_db_id: String,
    pub point_mappings: Vec<PointMapping>,
}
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct PointMapping {
    pub local_point_id: String,
    pub catalog_point_id: String,
}

pub(crate) fn canonical_id(value: &str) -> bool {
    uuid::Uuid::parse_str(value)
        .map(|id| {
            id.get_version_num() == 4
                && id.get_variant() == uuid::Variant::RFC4122
                && id.to_string() == value
        })
        .unwrap_or(false)
}

/// 拒绝通配、多播、保留网段及非规范文本；loopback 是有效的同机目标。
pub(crate) fn valid_connection(c: &Connection) -> bool {
    let Ok(ip) = c.host.parse::<std::net::Ipv4Addr>() else {
        return false;
    };
    let first = ip.octets()[0];
    ip.to_string() == c.host
        && first != 0
        && first < 224
        && c.port != 0
        && c.rack <= 7
        && c.slot <= 31
        && c.local_tsap.unwrap_or(0x0100) == 0x0100
        && c.remote_tsap
            .unwrap_or(0x0100 + u16::from(c.rack) * 32 + u16::from(c.slot))
            == 0x0100 + u16::from(c.rack) * 32 + u16::from(c.slot)
}

fn depth_ok(bytes: &[u8]) -> bool {
    let (mut depth, mut string, mut escaped) = (0usize, false, false);
    for byte in bytes {
        if string {
            if escaped {
                escaped = false;
            } else if *byte == b'\\' {
                escaped = true;
            } else if *byte == b'"' {
                string = false;
            }
        } else {
            match byte {
                b'"' => string = true,
                b'{' | b'[' => {
                    depth += 1;
                    if depth > 16 {
                        return false;
                    }
                }
                b'}' | b']' => match depth.checked_sub(1) {
                    Some(n) => depth = n,
                    None => return false,
                },
                _ => {}
            }
        }
    }
    depth == 0 && !string
}

/// 返回解析后的合同、原始 UTF-8 文本与输入原字节摘要。导出方 payload 摘要仅作声明保留。
pub(crate) fn parse(bytes: &[u8]) -> Result<(Catalog, String, String), String> {
    if bytes.is_empty() || bytes.len() > 1024 * 1024 {
        return Err("catalog_size_invalid".into());
    }
    if bytes.starts_with(&[0xef, 0xbb, 0xbf]) {
        return Err("catalog_encoding_invalid".into());
    }
    let raw = std::str::from_utf8(bytes).map_err(|_| "catalog_encoding_invalid")?;
    if !depth_ok(bytes) {
        return Err("catalog_depth_invalid".into());
    }
    let c: Catalog = serde_json::from_str(raw).map_err(|_| "catalog_format_invalid")?;
    c.validate()?;
    Ok((c, raw.to_owned(), digest(raw)))
}

impl Catalog {
    pub(crate) fn validate(&self) -> Result<(), String> {
        if self.format != "aiis.plc_points"
            || self.schema_version != 1
            || !matches!(
                self.origin.kind.as_str(),
                "device_simulator" | "data_acquisition_agent"
            )
            || !matches!(
                (
                    self.export.producer.as_str(),
                    self.export.config_state.as_str()
                ),
                ("device_simulator", "saved_revision")
                    | ("data_acquisition_agent", "saved_draft" | "active_revision")
            )
            || !canonical_id(&self.origin.profile_id)
            || !canonical_id(&self.origin.plc_id)
            || !canonical_id(&self.export.profile_id)
            || !canonical_id(&self.export.revision_id)
            || self.export.payload_sha256.len() != 64
            || !self
                .export
                .payload_sha256
                .bytes()
                .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
            || !self.export.exported_at.ends_with("+08:00")
            || chrono::DateTime::parse_from_rfc3339(&self.export.exported_at).is_err()
            || self.plc.name.trim().is_empty()
            || self.plc.name.len() > 100
            || self.plc.protocol != "s7"
            || self.dbs.is_empty()
            || self.dbs.len() > 32
        {
            return Err("catalog_metadata_invalid".into());
        }
        if !valid_connection(&self.plc.connection) {
            return Err("catalog_connection_invalid".into());
        }
        let mut ids = BTreeSet::from([self.origin.plc_id.as_str()]);
        let mut db_numbers = BTreeSet::new();
        let mut names = BTreeSet::new();
        let mut count = 0usize;
        for db in &self.dbs {
            if !canonical_id(&db.id)
                || !ids.insert(&db.id)
                || db.name.trim().is_empty()
                || db.name.len() > 100
                || db.number == 0
                || !db_numbers.insert(db.number)
                || !(1..=65536).contains(&db.size_bytes)
                || db.points.is_empty()
                || (self.export.producer == "device_simulator") != db.source_enabled.is_some()
            {
                return Err("catalog_db_invalid".into());
            }
            let mut occupied = vec![0u8; db.size_bytes as usize];
            for p in &db.points {
                count += 1;
                if count > 4096
                    || !canonical_id(&p.id)
                    || !ids.insert(&p.id)
                    || aiis_tia_import_core::validate_manual_name(&p.name).is_err()
                    || !names.insert(&p.name)
                    || p.display_name
                        .as_ref()
                        .map(|v| v.len() > 256)
                        .unwrap_or(false)
                    || p.display_names
                        .as_ref()
                        .map(|v| !v.valid())
                        .unwrap_or(false)
                    || p.description
                        .as_ref()
                        .map(|v| v.len() > 500)
                        .unwrap_or(false)
                    || p.source_path
                        .as_ref()
                        .map(|v| v.len() > 512)
                        .unwrap_or(false)
                {
                    return Err("catalog_point_invalid".into());
                }
                let width = super::local_configuration::width(&p.data_type)
                    .ok_or("catalog_type_invalid")?;
                if p.data_type.starts_with("STRING[")
                    && p.data_type != format!("STRING[{}]", width - 2)
                {
                    return Err("catalog_type_invalid".into());
                }
                if p.byte_offset
                    .checked_add(width)
                    .map(|n| n > db.size_bytes)
                    .unwrap_or(true)
                    || (p.data_type == "BOOL" && p.bit.map(|n| n > 7).unwrap_or(true))
                    || (p.data_type != "BOOL" && p.bit.is_some())
                {
                    return Err("catalog_address_invalid".into());
                }
                for byte in p.byte_offset..p.byte_offset + width {
                    let mask = if p.data_type == "BOOL" {
                        1 << p.bit.unwrap()
                    } else {
                        0xff
                    };
                    let slot = &mut occupied[byte as usize];
                    if *slot & mask != 0 {
                        return Err("catalog_address_overlap".into());
                    }
                    *slot |= mask;
                }
            }
        }
        Ok(())
    }
}

/// 在保存、激活和重启时重验目录原文、单一来源及完整的一一绑定。
pub(crate) fn verify_bindings(c: &Configuration) -> Result<BTreeSet<String>, String> {
    let mut by_source: BTreeMap<&str, Vec<&CatalogBinding>> = BTreeMap::new();
    let mut db_ids = BTreeSet::new();
    let mut identity_counts = BTreeMap::<&str, usize>::new();
    for id in c
        .plcs
        .iter()
        .map(|v| v.id.as_str())
        .chain(c.dbs.iter().map(|v| v.id.as_str()))
        .chain(c.points.iter().map(|v| v.id.as_str()))
        .chain(c.groups.iter().map(|v| v.id.as_str()))
        .chain(c.sources.iter().map(|v| v.id.as_str()))
    {
        *identity_counts.entry(id).or_default() += 1;
    }
    for binding in &c.catalog_bindings {
        if binding.source_kind != "exchange_json" || !db_ids.insert(binding.local_db_id.clone()) {
            return Err("catalog_binding_invalid".into());
        }
        by_source
            .entry(&binding.source_id)
            .or_default()
            .push(binding);
    }
    let mut origins = BTreeSet::new();
    let mut catalog_points = BTreeSet::new();
    for (source_id, bindings) in by_source {
        let sources: Vec<_> = c.sources.iter().filter(|s| s.id == source_id).collect();
        if sources.len() != 1 {
            return Err("catalog_source_invalid".into());
        }
        let src = sources[0];
        let (catalog, _, sha) = parse(src.content.as_bytes())?;
        let local_plcs: Vec<_> = c.plcs.iter().filter(|p| p.id == src.plc_id).collect();
        let remapped = src.plc_id != catalog.origin.plc_id;
        let external_ids: BTreeSet<_> = std::iter::once(catalog.origin.plc_id.as_str())
            .chain(catalog.dbs.iter().map(|d| d.id.as_str()))
            .chain(
                catalog
                    .dbs
                    .iter()
                    .flat_map(|d| d.points.iter().map(|p| p.id.as_str())),
            )
            .collect();
        let mut local_ids = BTreeSet::from([src.plc_id.as_str(), src.id.as_str()]);
        let mut mapped_dbs = BTreeSet::new();
        if src.sha256 != sha
            || src.db_number.is_some()
            || src.lineage_id.is_some()
            || !canonical_id(&src.plc_id)
            || !canonical_id(&src.id)
            || local_ids.len() != 2
            || (remapped && external_ids.contains(src.plc_id.as_str()))
            || external_ids.contains(src.id.as_str())
            || local_plcs.len() != 1
            || !origins.insert(catalog.origin.clone())
            || bindings.len() != catalog.dbs.len()
            || c.dbs.iter().filter(|d| d.source_id == source_id).count() != bindings.len()
        {
            return Err("catalog_source_invalid".into());
        }
        let local = local_plcs[0];
        if !valid_connection(&Connection {
            host: local.host.clone(),
            port: local.port,
            rack: local.rack,
            slot: local.slot,
            local_tsap: None,
            remote_tsap: None,
        }) {
            return Err("catalog_connection_invalid".into());
        }
        for b in bindings {
            let dbs: Vec<_> = c.dbs.iter().filter(|d| d.id == b.local_db_id).collect();
            let source_db = catalog
                .dbs
                .iter()
                .find(|d| d.id == b.origin_db_id)
                .ok_or("catalog_binding_invalid")?;
            if dbs.len() != 1
                || b.source_sha256 != sha
                || !canonical_id(&b.local_db_id)
                || !local_ids.insert(b.local_db_id.as_str())
                || !mapped_dbs.insert(b.origin_db_id.as_str())
                || (if remapped {
                    external_ids.contains(b.local_db_id.as_str())
                } else {
                    b.local_db_id != b.origin_db_id
                })
            {
                return Err("catalog_binding_invalid".into());
            }
            let db = dbs[0];
            if db.plc_id != src.plc_id
                || db.source_id != src.id
                || db.name != source_db.name
                || db.number != source_db.number
                || db.length != source_db.size_bytes
                || !db.complete
                || !db.tree.is_empty()
                || db.import_binding.is_some()
                || b.point_mappings.len() != source_db.points.len()
                || c.points.iter().filter(|p| p.db_id == db.id).count() != source_db.points.len()
            {
                return Err("catalog_binding_invalid".into());
            }
            let mut mapped = BTreeSet::new();
            for mapping in &b.point_mappings {
                let point = c
                    .points
                    .iter()
                    .find(|p| p.id == mapping.local_point_id)
                    .ok_or("catalog_binding_invalid")?;
                let source_point = source_db
                    .points
                    .iter()
                    .find(|p| p.id == mapping.catalog_point_id)
                    .ok_or("catalog_binding_invalid")?;
                let address = point.address.as_ref().ok_or("catalog_binding_invalid")?;
                if !canonical_id(&mapping.local_point_id)
                    || !local_ids.insert(mapping.local_point_id.as_str())
                    || (if remapped {
                        external_ids.contains(mapping.local_point_id.as_str())
                    } else {
                        mapping.local_point_id != mapping.catalog_point_id
                    })
                    || !mapped.insert(mapping.catalog_point_id.as_str())
                    || !catalog_points.insert(point.id.clone())
                    || point.plc_id != src.plc_id
                    || point.db_id != db.id
                    || point.name != source_point.name
                    || point.data_type != source_point.data_type
                    || point.source_path != source_point.source_path.as_deref().unwrap_or("")
                    || address.offset != source_point.byte_offset
                    || address.bit != source_point.bit
                    || !address.confirmed
                    || address.origin != "catalog"
                    || address.reason.trim().is_empty()
                    || c.point_legacy_display_names.get(&point.id)
                        != source_point.display_name.as_ref()
                {
                    return Err("catalog_binding_invalid".into());
                }
            }
        }
        if local_ids
            .iter()
            .any(|id| identity_counts.get(id) != Some(&1))
        {
            return Err("catalog_binding_invalid".into());
        }
    }
    if c.points.iter().any(|p| {
        p.address
            .as_ref()
            .map(|a| a.origin == "catalog")
            .unwrap_or(false)
            && !catalog_points.contains(&p.id)
    }) || c
        .point_legacy_display_names
        .keys()
        .any(|id| !catalog_points.contains(id))
    {
        return Err("catalog_binding_invalid".into());
    }
    Ok(db_ids)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::{json, Value};
    const VALID: &[u8] = include_bytes!("../../../tests/fixtures/plc-catalog-v1.json");

    fn rejected(value: Value) {
        assert!(parse(serde_json::to_string(&value).unwrap().as_bytes()).is_err());
    }

    #[test]
    fn catalog_import_rejects_non_rfc_uuid_variants() {
        let base: Value = serde_json::from_slice(VALID).unwrap();
        let mut disabled_point = base.clone();
        disabled_point["dbs"][0]["points"][2]["id"] = json!("ca21fc06-a489-4948-03fc-08b8e798168e");
        assert_eq!(
            parse(serde_json::to_string(&disabled_point).unwrap().as_bytes())
                .err()
                .as_deref(),
            Some("catalog_point_invalid")
        );

        for (path, expected) in [
            ("/origin/profile_id", "catalog_metadata_invalid"),
            ("/origin/plc_id", "catalog_metadata_invalid"),
            ("/export/profile_id", "catalog_metadata_invalid"),
            ("/export/revision_id", "catalog_metadata_invalid"),
            ("/dbs/0/id", "catalog_db_invalid"),
            ("/dbs/0/points/0/id", "catalog_point_invalid"),
        ] {
            for variant in ['0', 'c', 'e'] {
                let mut value = base.clone();
                *value.pointer_mut(path).unwrap() =
                    json!(format!("ca21fc06-a489-4948-{variant}3fc-08b8e798168e"));
                assert_eq!(
                    parse(serde_json::to_string(&value).unwrap().as_bytes())
                        .err()
                        .as_deref(),
                    Some(expected),
                    "{path}: {variant}"
                );
            }
        }

        for variant in ['8', '9', 'a', 'b'] {
            let mut value = base.clone();
            value["dbs"][0]["points"][0]["id"] =
                json!(format!("ca21fc06-a489-4948-{variant}3fc-08b8e798168e"));
            assert!(parse(serde_json::to_string(&value).unwrap().as_bytes()).is_ok());
        }
    }

    #[test]
    fn catalog_import_parser_preserves_bytes_and_all_points() {
        let (catalog, raw, sha) = parse(VALID).unwrap();
        assert_eq!(raw.as_bytes(), VALID);
        assert_eq!(sha, digest(std::str::from_utf8(VALID).unwrap()));
        assert_eq!(catalog.dbs.len(), 2);
        assert_eq!(catalog.dbs.iter().map(|d| d.points.len()).sum::<usize>(), 5);
        assert_eq!(
            catalog.dbs[0].points[0].display_name.as_deref(),
            Some("未标记")
        );
        assert_eq!(
            catalog.dbs[0].points[1]
                .display_names
                .as_ref()
                .unwrap()
                .en_us,
            ""
        );
        assert!(!catalog.dbs[0].points[2].source_enabled);
        assert_eq!(catalog.dbs[0].points[3].data_type, "STRING[4]");
    }

    #[test]
    fn catalog_import_explicit_ds_export() {
        let Ok(path) = std::env::var("DAA017_DS_EXPORT") else {
            return;
        };
        let expected = std::env::var("DAA017_DS_EXPORT_SHA256").unwrap();
        let bytes = std::fs::read(path).unwrap();
        let (catalog, raw, sha) = parse(&bytes).unwrap();
        assert_eq!(sha, expected);
        assert_eq!(raw.as_bytes(), bytes);
        let types: BTreeSet<_> = catalog
            .dbs
            .iter()
            .flat_map(|db| db.points.iter().map(|point| point.data_type.as_str()))
            .collect();
        assert!(["BOOL", "INT", "REAL"].iter().all(|t| types.contains(t)));
    }

    #[test]
    fn catalog_import_parser_rejects_invalid_json_and_field_contract() {
        assert!(parse(&[0xef, 0xbb, 0xbf, b'{', b'}']).is_err());
        assert!(parse(&[0xff]).is_err());
        assert!(parse(&vec![b' '; 1024 * 1024 + 1]).is_err());
        let text = std::str::from_utf8(VALID).unwrap();
        assert!(parse(
            text.replace(
                "\"schema_version\": 1",
                "\"schema_version\": 1, \"schema_version\": 1"
            )
            .as_bytes()
        )
        .is_err());
        assert!(parse(
            text.replace("\"schema_version\": 1", "\"schema_version\": 1.0")
                .as_bytes()
        )
        .is_err());
        assert!(!depth_ok(
            format!("{}0{}", "[".repeat(17), "]".repeat(17)).as_bytes()
        ));
        let base: Value = serde_json::from_slice(VALID).unwrap();
        for (pointer, replacement) in [
            ("/schema_version", json!(2)),
            ("/export/producer", json!("data_acquisition_agent")),
            (
                "/origin/plc_id",
                json!("22222222-2222-4222-8222-22222222222A"),
            ),
            ("/dbs/0/source_enabled", Value::Null),
            ("/dbs/0/points/0/display_names", Value::Null),
            ("/dbs/0/points/0/display_name", Value::Null),
            ("/dbs/0/points/0/description", Value::Null),
            ("/dbs/0/points/0/source_path", Value::Null),
            ("/dbs/0/points/0/bit", Value::Null),
            ("/plc/connection/host", json!("0.0.0.0")),
            ("/plc/connection/host", json!("224.0.0.1")),
            ("/plc/connection/port", json!(0)),
        ] {
            let mut value = base.clone();
            *value.pointer_mut(pointer).unwrap() = replacement;
            rejected(value);
        }
        let mut value = base.clone();
        value["plc"]["connection"]["remote_tsap"] = json!(0x1234);
        rejected(value);
        let mut value = base.clone();
        value["dbs"][0]["points"][0]["display_names"]["extra"] = json!("");
        rejected(value);
        let mut value = base.clone();
        value["dbs"][0]["points"][0]["display_names"]
            .as_object_mut()
            .unwrap()
            .remove("en-US");
        rejected(value);
    }

    #[test]
    fn daa019_producer_controls_db_enabled_presence() {
        let mut value: Value = serde_json::from_slice(VALID).unwrap();
        value["export"]["producer"] = json!("data_acquisition_agent");
        value["export"]["config_state"] = json!("saved_draft");
        for db in value["dbs"].as_array_mut().unwrap() {
            db.as_object_mut().unwrap().remove("source_enabled");
        }
        assert!(parse(serde_json::to_string(&value).unwrap().as_bytes()).is_ok());
        value["export"]["config_state"] = json!("active_revision");
        assert!(parse(serde_json::to_string(&value).unwrap().as_bytes()).is_ok());
        let mut bad = value.clone();
        bad["dbs"][0]["source_enabled"] = json!(false);
        rejected(bad);
        let mut bad = value.clone();
        bad["dbs"][0]["source_enabled"] = Value::Null;
        rejected(bad);
        let mut bad = value.clone();
        bad["dbs"][0]["points"][0]
            .as_object_mut()
            .unwrap()
            .remove("source_enabled");
        rejected(bad);
        let mut bad = value;
        bad["export"]["producer"] = json!("device_simulator");
        bad["export"]["config_state"] = json!("saved_revision");
        rejected(bad);
    }

    #[test]
    fn catalog_import_parser_checks_disabled_points_layout_and_identity() {
        let base: Value = serde_json::from_slice(VALID).unwrap();
        let mut same_db_name = base.clone();
        same_db_name["dbs"][1]["name"] = json!("First");
        assert!(parse(serde_json::to_string(&same_db_name).unwrap().as_bytes()).is_ok());
        for (pointer, replacement) in [
            ("/dbs/0/points/2/data_type", json!("LREAL")),
            ("/dbs/0/points/3/data_type", json!("STRING[0]")),
            ("/dbs/0/points/3/data_type", json!("STRING[255]")),
            ("/dbs/0/points/3/data_type", json!("STRING[04]")),
            ("/dbs/0/points/3/data_type", json!("STRING[+4]")),
            ("/dbs/0/points/3/byte_offset", json!(28)),
            ("/dbs/0/points/2/byte_offset", json!(2)),
            ("/dbs/0/points/0/bit", json!(8)),
            (
                "/dbs/0/points/1/id",
                json!("55555555-5555-4555-8555-555555555555"),
            ),
            ("/dbs/1/id", json!("22222222-2222-4222-8222-222222222222")),
            ("/dbs/1/number", json!(21)),
            ("/dbs/1/points/0/name", json!("DB21_ready_Bool")),
        ] {
            let mut value = base.clone();
            *value.pointer_mut(pointer).unwrap() = replacement;
            rejected(value);
        }
        let mut value = base.clone();
        value["dbs"][0]["points"][1]["bit"] = json!(0);
        rejected(value);
    }
}
