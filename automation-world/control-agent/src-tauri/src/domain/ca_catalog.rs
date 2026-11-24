//! Closed, offline consumer of the shared aiis.plc_points v1 exchange file.
use super::ca_flow::{checked_json, sha};
use serde::{Deserialize, Deserializer, Serialize};
use std::collections::BTreeSet;
use std::net::Ipv4Addr;

fn present<'de, D: Deserializer<'de>, T: Deserialize<'de>>(d: D) -> Result<Option<T>, D::Error> {
    T::deserialize(d).map(Some)
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct Catalog {
    pub format: String,
    pub schema_version: u32,
    pub origin: Origin,
    pub export: Export,
    pub plc: Plc,
    pub dbs: Vec<Db>,
}
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct Origin {
    pub kind: String,
    pub profile_id: String,
    pub plc_id: String,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct Export {
    pub producer: String,
    pub profile_id: String,
    pub config_state: String,
    pub revision_id: String,
    pub payload_sha256: String,
    pub exported_at: String,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct Plc {
    pub name: String,
    pub protocol: String,
    pub connection: Connection,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
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
impl Connection {
    pub fn default_tsap(&self) -> bool {
        self.local_tsap.is_none_or(|v| v == 0x0100)
            && self
                .remote_tsap
                .is_none_or(|v| v == 0x0100 + u16::from(self.rack) * 32 + u16::from(self.slot))
    }
    pub fn valid(&self) -> bool {
        self.host
            .parse::<Ipv4Addr>()
            .is_ok_and(|ip| ip.to_string() == self.host && (1..224).contains(&ip.octets()[0]))
            && self.port > 0
            && self.rack <= 7
            && self.slot <= 31
            && self.local_tsap != Some(0)
            && self.remote_tsap != Some(0)
    }
}
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct Db {
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
    pub points: Vec<Point>,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct Names {
    #[serde(rename = "zh-CN")]
    pub zh: String,
    #[serde(rename = "en-US")]
    pub en: String,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct Point {
    pub id: String,
    pub name: String,
    pub data_type: String,
    pub byte_offset: u32,
    pub source_enabled: bool,
    #[serde(
        default,
        deserialize_with = "present",
        skip_serializing_if = "Option::is_none"
    )]
    pub bit: Option<u8>,
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
    pub display_names: Option<Names>,
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
}
pub(crate) fn width(t: &str) -> Option<u32> {
    match t {
        "BOOL" | "BYTE" | "USINT" | "CHAR" => Some(1),
        "INT" | "UINT" | "WORD" => Some(2),
        "DINT" | "UDINT" | "DWORD" | "REAL" => Some(4),
        _ => t
            .strip_prefix("STRING[")
            .and_then(|s| s.strip_suffix(']'))
            .and_then(|s| s.parse::<u32>().ok())
            .filter(|v| (1..=254).contains(v) && t == format!("STRING[{v}]"))
            .map(|v| v + 2),
    }
}
fn valid_uuid(s: &str) -> bool {
    uuid::Uuid::parse_str(s).is_ok_and(|u| {
        u.get_version_num() == 4 && u.get_variant() == uuid::Variant::RFC4122 && u.to_string() == s
    })
}
fn text(s: &str, limit: usize) -> bool {
    s.len() <= limit && !s.contains('\0')
}
fn technical(s: &str) -> bool {
    let mut b = s.bytes();
    s.len() <= 100
        && b.next()
            .is_some_and(|x| x.is_ascii_alphabetic() || x == b'_')
        && b.all(|x| x.is_ascii_alphanumeric() || x == b'_')
}

impl Catalog {
    pub fn parse(raw: &[u8]) -> Result<(Self, String), String> {
        let c: Self = checked_json(raw)?;
        c.validate()?;
        Ok((c, sha(raw)))
    }
    fn validate(&self) -> Result<(), String> {
        let export = &self.export;
        let origin = &self.origin;
        if self.format != "aiis.plc_points"
            || self.schema_version != 1
            || !matches!(
                origin.kind.as_str(),
                "device_simulator" | "data_acquisition_agent"
            )
            || !matches!(
                (export.producer.as_str(), export.config_state.as_str()),
                ("device_simulator", "saved_revision")
                    | ("data_acquisition_agent", "saved_draft" | "active_revision")
            )
            || ![
                &origin.profile_id,
                &origin.plc_id,
                &export.profile_id,
                &export.revision_id,
            ]
            .iter()
            .all(|s| valid_uuid(s))
            || export.payload_sha256.len() != 64
            || !export
                .payload_sha256
                .bytes()
                .all(|x| x.is_ascii_digit() || (b'a'..=b'f').contains(&x))
            || !export.exported_at.ends_with("+08:00")
            || chrono::DateTime::parse_from_rfc3339(&export.exported_at).is_err()
            || self.plc.protocol != "s7"
            || !text(&self.plc.name, 100)
            || self.plc.name.trim().is_empty()
            || self.dbs.is_empty()
            || self.dbs.len() > 32
        {
            return Err("catalog_metadata_invalid".into());
        }
        if !self.plc.connection.valid() {
            return Err("catalog_connection_invalid".into());
        }
        let mut ids = BTreeSet::from([origin.plc_id.as_str()]);
        let mut numbers = BTreeSet::new();
        let mut names = BTreeSet::new();
        let mut count = 0usize;
        for db in &self.dbs {
            if !valid_uuid(&db.id)
                || !ids.insert(&db.id)
                || db.number == 0
                || !numbers.insert(db.number)
                || !text(&db.name, 100)
                || db.name.trim().is_empty()
                || !(1..=65536).contains(&db.size_bytes)
                || db.points.is_empty()
                || ((export.producer == "device_simulator") != db.source_enabled.is_some())
            {
                return Err(format!("catalog_db_invalid: DB{}", db.number));
            }
            let mut taken = vec![0u8; db.size_bytes as usize];
            for point in &db.points {
                count += 1;
                let at = || format!("DB{}.{}", db.number, point.name);
                if count > 4096
                    || !valid_uuid(&point.id)
                    || !ids.insert(&point.id)
                    || !technical(&point.name)
                    || !names.insert(&point.name)
                    || point.display_name.as_ref().is_some_and(|s| !text(s, 256))
                    || point
                        .display_names
                        .as_ref()
                        .is_some_and(|n| !text(&n.zh, 256) || !text(&n.en, 256))
                    || point.description.as_ref().is_some_and(|s| !text(s, 500))
                    || point.source_path.as_ref().is_some_and(|s| !text(s, 512))
                {
                    return Err(format!("catalog_point_invalid: {}", at()));
                }
                let w = width(&point.data_type)
                    .ok_or_else(|| format!("catalog_type_invalid: {}", at()))?;
                let end = point
                    .byte_offset
                    .checked_add(w)
                    .filter(|n| *n <= db.size_bytes)
                    .ok_or_else(|| format!("catalog_offset_invalid: {}", at()))?;
                let mask = match (point.data_type.as_str(), point.bit) {
                    ("BOOL", Some(n)) if n < 8 => 1u8 << n,
                    (t, None) if t != "BOOL" => 0xff,
                    _ => return Err(format!("catalog_bit_invalid: {}", at())),
                };
                for b in &mut taken[point.byte_offset as usize..end as usize] {
                    if *b & mask != 0 {
                        return Err(format!("catalog_overlap: {}", at()));
                    }
                    *b |= mask;
                }
            }
        }
        Ok(())
    }
}
