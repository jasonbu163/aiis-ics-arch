//! DS配置值对象：UUID身份、层级策略、显式确认与有界拓扑；不依赖SQL或UI。
use super::{
    rule::RuleSpec,
    source::{PathSegment, SourceBinding, SourceVersion},
    typed_value,
};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::collections::BTreeSet;

pub fn uuid() -> String {
    uuid::Uuid::new_v4().to_string()
}
pub fn digest<T: Serialize + ?Sized>(value: &T) -> String {
    hash_bytes(&serde_json::to_vec(value).expect("serializable configuration"))
}
pub fn hash_bytes(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}
fn yes() -> bool {
    true
}
fn default_c() -> u8 {
    16
}
fn default_h() -> u8 {
    4
}
fn loopback() -> String {
    "127.0.0.1".into()
}
fn default_calling() -> u16 {
    256
}
fn default_slot() -> u8 {
    1
}

#[derive(Clone, Copy, Default, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Mode {
    #[default]
    Hold,
    Fixed,
    Ramp,
    Sine,
    Random,
    Toggle,
}
#[derive(Clone, Copy, Default, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum WriteOwner {
    #[default]
    None,
    Client,
    Ui,
    Rule,
}
#[derive(Clone, Default, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct PolicyOverrides {
    pub mode: Option<Mode>,
    pub owner: Option<WriteOwner>,
    pub client_read: Option<bool>,
    pub client_write: Option<bool>,
    pub ui_write: Option<bool>,
    pub ui_maintenance: Option<bool>,
    pub initial: Option<Value>,
    pub rule: Option<RuleSpec>,
}
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct EffectivePolicy {
    pub mode: Mode,
    pub owner: WriteOwner,
    pub client_read: bool,
    pub client_write: bool,
    pub ui_write: bool,
    pub ui_maintenance: bool,
    pub initial: Value,
    pub rule: Option<RuleSpec>,
    pub inherited_from: std::collections::BTreeMap<String, String>,
}
impl EffectivePolicy {
    pub fn new(kind: &str) -> Result<Self, String> {
        Ok(Self {
            mode: Mode::Hold,
            owner: WriteOwner::None,
            client_read: true,
            client_write: false,
            ui_write: false,
            ui_maintenance: false,
            initial: typed_value::default_value(kind)?,
            rule: None,
            inherited_from: [
                "mode",
                "owner",
                "client_read",
                "client_write",
                "ui_write",
                "ui_maintenance",
                "initial",
                "rule",
            ]
            .into_iter()
            .map(|key| (key.into(), "default".into()))
            .collect(),
        })
    }
    pub fn overlay(&mut self, p: &PolicyOverrides, level: &str) {
        macro_rules! apply { ($($field:ident),+) => { $(if let Some(value)=&p.$field { self.$field=value.clone();self.inherited_from.insert(stringify!($field).into(),level.into()); })+ }; }
        apply!(
            mode,
            owner,
            client_read,
            client_write,
            ui_write,
            ui_maintenance,
            initial
        );
        if let Some(rule) = &p.rule {
            self.rule = Some(rule.clone());
            self.inherited_from.insert("rule".into(), level.into());
        }
    }
}
#[derive(Clone, Default, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Confirmations {
    pub initial: Option<String>,
    pub policy: Option<String>,
}
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct PointConfig {
    pub id: String,
    pub name: String,
    #[serde(default)]
    pub display_name: String,
    pub data_type: String,
    #[serde(default = "yes")]
    pub enabled: bool,
    #[serde(default)]
    pub source_path: String,
    #[serde(default)]
    pub segments: Vec<PathSegment>,
    #[serde(default)]
    pub byte: Option<u32>,
    #[serde(default)]
    pub bit: Option<u8>,
    #[serde(default)]
    pub manual_reason: String,
    #[serde(default)]
    pub manual: bool,
    #[serde(default)]
    pub policy: PolicyOverrides,
    #[serde(default)]
    pub confirmations: Confirmations,
}
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct RegionPolicy {
    pub id: String,
    pub first_bit: u32,
    pub bit_length: u32,
    pub policy: PolicyOverrides,
}
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct AddressConfirmation {
    pub structure_sha256: String,
    pub layout_sha256: String,
    pub method: String,
    pub reason: String,
}
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct DbConfig {
    pub id: String,
    pub name: String,
    pub number: u16,
    pub length: u32,
    #[serde(default = "yes")]
    pub enabled: bool,
    #[serde(default)]
    pub manual: bool,
    #[serde(default)]
    pub binding: Option<SourceBinding>,
    #[serde(default)]
    pub points: Vec<PointConfig>,
    #[serde(default)]
    pub policy: PolicyOverrides,
    #[serde(default)]
    pub regions: Vec<RegionPolicy>,
    #[serde(default)]
    pub address_confirmation: Option<AddressConfirmation>,
}
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct InstanceConfig {
    pub id: String,
    pub name: String,
    #[serde(default = "loopback")]
    pub host: String,
    pub port: u16,
    #[serde(default)]
    pub rack: u8,
    #[serde(default = "default_slot")]
    pub slot: u8,
    #[serde(default = "default_calling")]
    pub calling_tsap: u16,
    #[serde(default = "default_c")]
    pub max_connections: u8,
    #[serde(default = "default_h")]
    pub max_handshakes: u8,
    #[serde(default)]
    pub policy: PolicyOverrides,
    #[serde(default)]
    pub dbs: Vec<DbConfig>,
    #[serde(default)]
    pub names_confirmation: Option<String>,
}
impl InstanceConfig {
    pub fn called_tsap(&self) -> u16 {
        0x100 | ((self.rack as u16) << 5) | self.slot as u16
    }
}
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Workspace {
    pub schema_version: u32,
    #[serde(default)]
    pub instances: Vec<InstanceConfig>,
    #[serde(default)]
    pub source_versions: Vec<SourceVersion>,
}
impl Default for Workspace {
    fn default() -> Self {
        Self {
            schema_version: 1,
            instances: vec![],
            source_versions: vec![],
        }
    }
}

pub fn validate(workspace: &Workspace) -> Result<(), String> {
    if workspace.schema_version != 1
        || workspace.instances.len() > 8
        || serde_json::to_vec(workspace)
            .map_err(|_| "configuration_format")?
            .len()
            > 16 * 1024 * 1024
    {
        return Err("configuration_capacity".into());
    }
    let mut ids = BTreeSet::new();
    let mut take_id = |id: &str| -> Result<(), String> {
        if !uuid::Uuid::parse_str(id).is_ok_and(|value| value.to_string() == id)
            || !ids.insert(id.to_owned())
        {
            Err("configuration_identity".into())
        } else {
            Ok(())
        }
    };
    for source in &workspace.source_versions {
        take_id(&source.version_id)?;
        if uuid::Uuid::parse_str(&source.lineage_id).is_err()
            || source.bytes.len() > 1024 * 1024
            || hash_bytes(&source.bytes) != source.blob_sha256
            || std::str::from_utf8(&source.bytes).is_err()
        {
            return Err("source_identity".into());
        }
    }
    for instance in &workspace.instances {
        take_id(&instance.id)?;
        if instance.name.trim().is_empty()
            || instance.name.len() > 100
            || !instance
                .host
                .parse::<std::net::Ipv4Addr>()
                .is_ok_and(|a| a.is_loopback())
            || instance.port == 0
            || instance.rack > 7
            || instance.slot > 31
            || !(1..=64).contains(&instance.max_connections)
            || !(1..=16).contains(&instance.max_handshakes)
            || instance.dbs.len() > 32
        {
            return Err("instance_parameters".into());
        }
        if instance.dbs.iter().map(|d| d.points.len()).sum::<usize>() > 4096 {
            return Err("point_capacity".into());
        }
        let mut numbers = BTreeSet::new();
        for db in &instance.dbs {
            take_id(&db.id)?;
            if db.number == 0
                || !numbers.insert(db.number)
                || !(1..=65536).contains(&db.length)
                || db.name.trim().is_empty()
                || db.name.len() > 100
            {
                return Err("db_parameters".into());
            }
            if db.binding.is_none() && !db.manual {
                return Err("manual_structure_required".into());
            }
            for point in &db.points {
                take_id(&point.id)?;
                typed_value::width(&point.data_type)?;
                if point.name.len() > 100
                    || point.display_name.len() > 200
                    || point.manual_reason.len() > 1000
                    || point.bit.is_some_and(|b| b > 7)
                {
                    return Err("point_parameters".into());
                }
            }
            for region in &db.regions {
                take_id(&region.id)?;
                if region.bit_length == 0
                    || region
                        .first_bit
                        .checked_add(region.bit_length)
                        .is_none_or(|end| end > db.length * 8)
                {
                    return Err("policy_region".into());
                }
            }
        }
    }
    Ok(())
}
