//! 文件：src/domain.rs；严格命令、物理INT资源、来源时间及身份摘要。
use crate::{
    config::{Flow, Plc},
    Result,
};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::{
    sync::atomic::{AtomicU64, Ordering},
    time::{Duration, Instant, SystemTime, UNIX_EPOCH},
};
pub fn now_ms() -> i64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_millis() as i64
}
pub fn id() -> String {
    static N: AtomicU64 = AtomicU64::new(0);
    format!(
        "{}-{}-{}",
        now_ms(),
        std::process::id(),
        N.fetch_add(1, Ordering::Relaxed)
    )
}
pub fn valid_id(x: &str) -> bool {
    !x.is_empty()
        && x.len() <= 64
        && x.bytes()
            .all(|b| b.is_ascii_alphanumeric() || b == b'_' || b == b'-')
}
pub fn hash<T: Serialize>(v: &T) -> String {
    format!("{:x}", Sha256::digest(serde_json::to_vec(v).unwrap()))
}
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Input {
    pub schema_version: u8,
    pub source_id: String,
    pub ready: bool,
    pub command_id: Option<String>,
    pub value: Option<i16>,
    pub issued_at_ms: Option<i64>,
    pub expires_at_ms: Option<i64>,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Intent {
    pub source_id: String,
    pub command_id: String,
    pub flow_id: String,
    pub target: Resource,
    pub config_identity_hash: String,
    pub value: i16,
    pub issued_at_ms: i64,
    pub expires_at_ms: i64,
    pub input_max_age_ms: u64,
}
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Resource {
    pub host: String,
    pub port: u16,
    pub rack: u16,
    pub slot: u16,
    pub db: u16,
    pub offset: u32,
    pub length: u8,
}
impl Resource {
    pub fn overlaps(&self, b: &Self) -> bool {
        self.host == b.host
            && self.port == b.port
            && self.rack == b.rack
            && self.slot == b.slot
            && self.db == b.db
            && self.offset < b.offset + b.length as u32
            && b.offset < self.offset + self.length as u32
    }
}
impl Intent {
    pub fn validate_time(&self, now: i64) -> Result<()> {
        if self.expires_at_ms <= self.issued_at_ms
            || self.expires_at_ms - self.issued_at_ms > 60000
            || self.issued_at_ms > now + 1000
            || now >= self.expires_at_ms
            || now - self.issued_at_ms > self.input_max_age_ms as i64
        {
            return Err("input_stale".into());
        }
        Ok(())
    }
    pub fn deadline(&self) -> Instant {
        Instant::now() + Duration::from_millis((self.expires_at_ms - now_ms()).max(0) as u64)
    }
}
impl Input {
    pub fn intent(self, f: &Flow, p: &Plc) -> Result<Option<Intent>> {
        if self.schema_version != 1 || self.source_id != f.source_id {
            return Err("input_schema".into());
        }
        if !self.ready {
            return if self.command_id.is_none()
                && self.value.is_none()
                && self.issued_at_ms.is_none()
                && self.expires_at_ms.is_none()
            {
                Ok(None)
            } else {
                Err("input_schema".into())
            };
        }
        let command_id = self
            .command_id
            .filter(|x| valid_id(x))
            .ok_or("input_schema")?;
        let intent = Intent {
            source_id: self.source_id,
            command_id,
            flow_id: f.id.clone(),
            target: Resource {
                host: p.host.clone(),
                port: p.port,
                rack: p.rack,
                slot: p.slot,
                db: f.target.db_number,
                offset: f.target.byte_offset,
                length: 2,
            },
            config_identity_hash: hash(&(f, &f.target, p.host.as_str(), p.port, p.rack, p.slot)),
            value: self.value.ok_or("input_schema")?,
            issued_at_ms: self.issued_at_ms.ok_or("input_schema")?,
            expires_at_ms: self.expires_at_ms.ok_or("input_schema")?,
            input_max_age_ms: f.input_max_age_ms,
        };
        intent.validate_time(now_ms())?;
        Ok(Some(intent))
    }
}
pub struct Clock {
    wall: i64,
    mono: Instant,
    pub invalid: bool,
}
impl Default for Clock {
    fn default() -> Self {
        Self {
            wall: now_ms(),
            mono: Instant::now(),
            invalid: false,
        }
    }
}
impl Clock {
    pub fn check(&mut self, wall: i64) -> Result<()> {
        if (wall - self.wall - self.mono.elapsed().as_millis() as i64).abs() > 1000 {
            self.invalid = true;
        }
        if self.invalid {
            Err("clock_invalid".into())
        } else {
            Ok(())
        }
    }
}
