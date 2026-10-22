//! 文件：src/config.rs；拒绝未知字段与隐式类型的配置/资源边界校验。
use crate::{domain::valid_id, Result};
use serde::{Deserialize, Serialize};
use std::{collections::HashSet, net::Ipv4Addr, path::Path};
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Config {
    pub schema_version: u8,
    pub instance_id: String,
    pub plcs: Vec<Plc>,
    pub flows: Vec<Flow>,
    pub http: Http,
    pub shutdown_timeout_ms: u64,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Plc {
    pub id: String,
    pub host: String,
    pub port: u16,
    pub rack: u16,
    pub slot: u16,
    pub connect_timeout_ms: u64,
    pub io_timeout_ms: u64,
    pub queue_capacity: usize,
    pub queue_wait_ms: u64,
    pub ready_wait_ms: u64,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Flow {
    pub id: String,
    pub kind: String,
    pub business_name: String,
    pub interval_ms: u64,
    pub source_id: String,
    pub get_url: String,
    pub target: Target,
    pub input_max_age_ms: u64,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Target {
    pub plc_id: String,
    pub db_number: u16,
    pub db_size_bytes: u32,
    pub byte_offset: u32,
    #[serde(rename = "type")]
    pub data_type: String,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Http {
    pub connect_timeout_ms: u64,
    pub total_timeout_ms: u64,
    pub pool_wait_ms: u64,
    pub max_connections: usize,
    pub max_body_bytes: usize,
}
fn range(x: u64, min: u64, max: u64) -> Result<()> {
    if x < min || x > max {
        Err("config_range".into())
    } else {
        Ok(())
    }
}
impl Config {
    pub fn load(p: &Path) -> Result<Self> {
        let b = std::fs::read(p).map_err(|_| "config_read")?;
        if b.len() > 65536 {
            return Err("config_size".into());
        }
        let c: Self = serde_yaml::from_slice(&b).map_err(|_| "config_schema")?;
        c.validate()?;
        Ok(c)
    }
    pub fn validate(&self) -> Result<()> {
        if self.schema_version != 1
            || !valid_id(&self.instance_id)
            || self.plcs.is_empty()
            || self.plcs.len() > 4
            || self.flows.is_empty()
            || self.flows.len() > 8
        {
            return Err("config_schema".into());
        }
        let mut ids = HashSet::new();
        let mut endpoints = HashSet::new();
        let mut largest = self.http.total_timeout_ms;
        for p in &self.plcs {
            if !valid_id(&p.id)
                || !ids.insert(p.id.clone())
                || p.host.parse::<Ipv4Addr>().is_err()
                || p.port == 0
                || p.rack > 7
                || p.slot > 31
                || !endpoints.insert((p.host.clone(), p.port))
            {
                return Err("config_plc".into());
            }
            range(p.connect_timeout_ms, 500, 3000)?;
            range(p.io_timeout_ms, 500, 5000)?;
            range(p.queue_capacity as u64, 1, 16)?;
            range(p.queue_wait_ms, 100, 5000)?;
            range(p.ready_wait_ms, 100, 5000)?;
            largest = largest.max(p.connect_timeout_ms).max(p.io_timeout_ms);
        }
        ids.clear();
        let mut targets = Vec::new();
        for f in &self.flows {
            if !valid_id(&f.id)
                || !valid_id(&f.source_id)
                || !valid_id(&f.business_name)
                || !ids.insert(f.id.clone())
                || f.kind != "demo01"
            {
                return Err("config_flow".into());
            }
            range(f.interval_ms, 100, 10000)?;
            range(f.input_max_age_ms, 1, 60000)?;
            let url = reqwest::Url::parse(&f.get_url).map_err(|_| "config_url")?;
            if !matches!(url.scheme(), "http" | "https")
                || !url.username().is_empty()
                || url.password().is_some()
                || url.fragment().is_some()
            {
                return Err("config_url".into());
            }
            let t = &f.target;
            let p = self
                .plcs
                .iter()
                .find(|p| p.id == t.plc_id)
                .ok_or("config_target")?;
            if t.db_number == 0
                || t.db_size_bytes < 2
                || t.db_size_bytes > 65536
                || t.byte_offset > 65534
                || t.byte_offset + 2 > t.db_size_bytes
                || t.data_type != "INT"
            {
                return Err("config_target".into());
            }
            let key = (p.host.clone(), p.port, p.rack, p.slot, t.db_number);
            if targets
                .iter()
                .any(|(k, o): &((String, u16, u16, u16, u16), u32)| {
                    *k == key && t.byte_offset < *o + 2 && *o < t.byte_offset + 2
                })
            {
                return Err("config_overlap".into());
            }
            targets.push((key, t.byte_offset));
        }
        range(self.http.connect_timeout_ms, 100, 1500)?;
        range(self.http.pool_wait_ms, 100, 1500)?;
        range(self.http.total_timeout_ms, 100, 5000)?;
        range(self.http.max_connections as u64, 1, 8)?;
        range(self.http.max_body_bytes as u64, 1, 4096)?;
        if self.http.connect_timeout_ms > self.http.total_timeout_ms
            || self.http.pool_wait_ms > self.http.total_timeout_ms
        {
            return Err("config_http".into());
        }
        range(self.shutdown_timeout_ms, 5000, 20000)?;
        if self.shutdown_timeout_ms < largest + 5500 {
            return Err("config_shutdown".into());
        }
        Ok(())
    }
}
