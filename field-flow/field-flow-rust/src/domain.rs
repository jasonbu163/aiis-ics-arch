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
        if self
            .expires_at_ms
            .checked_sub(self.issued_at_ms)
            .is_none_or(|ttl| ttl <= 0 || ttl > 60000)
            || self.issued_at_ms > now.saturating_add(1000)
            || now >= self.expires_at_ms
            || now
                .checked_sub(self.issued_at_ms)
                .is_none_or(|age| age > self.input_max_age_ms as i64)
        {
            return Err("input_stale".into());
        }
        Ok(())
    }
    pub fn deadline(&self) -> Instant {
        Instant::now()
            + Duration::from_millis(
                (self.expires_at_ms.min(
                    self.issued_at_ms
                        .saturating_add(self.input_max_age_ms as i64),
                ) - now_ms())
                .max(0) as u64,
            )
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
/// 同一任务的wall/OS monotonic锚点可随私有IPC传给child，排队不重置。
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ClockAnchor {
    wall: i64,
    mono_ms: i64,
    #[cfg(feature = "test-fixture")]
    test_wall: Option<std::path::PathBuf>,
}
fn monotonic_ms() -> Result<i64> {
    let mut t = std::mem::MaybeUninit::<libc::timespec>::uninit();
    if unsafe { libc::clock_gettime(libc::CLOCK_MONOTONIC, t.as_mut_ptr()) } != 0 {
        return Err("clock_invalid".into());
    }
    let t = unsafe { t.assume_init() };
    Ok(t.tv_sec * 1000 + t.tv_nsec / 1_000_000)
}
impl ClockAnchor {
    pub fn check(&self, wall: i64) -> Result<()> {
        #[cfg(feature = "test-fixture")]
        let wall = wall + test_wall_offset(self.test_wall.as_deref());
        let drift =
            wall as i128 - self.wall as i128 - (monotonic_ms()? as i128 - self.mono_ms as i128);
        if drift.abs() > 1000 {
            Err("clock_invalid".into())
        } else {
            Ok(())
        }
    }
}
pub struct Clock {
    anchor: ClockAnchor,
    pub invalid: bool,
}
impl Default for Clock {
    fn default() -> Self {
        let mono = monotonic_ms();
        Self {
            anchor: ClockAnchor {
                wall: now_ms(),
                mono_ms: mono.clone().unwrap_or(0),
                #[cfg(feature = "test-fixture")]
                test_wall: std::env::var_os("FF_TEST_CLOCK_FILE").map(Into::into),
            },
            invalid: mono.is_err(),
        }
    }
}
impl Clock {
    pub fn anchor(&self) -> ClockAnchor {
        self.anchor.clone()
    }
    pub fn invalidate(&mut self) {
        self.invalid = true;
    }
    pub fn check(&mut self, wall: i64) -> Result<()> {
        self.invalid |= self.anchor.check(wall).is_err();
        if self.invalid {
            Err("clock_invalid".into())
        } else {
            Ok(())
        }
    }
}
/// 仅合成回归的有界墙钟偏移；不修改宿主系统时钟或产品配置。
#[cfg(feature = "test-fixture")]
fn test_wall_offset(path: Option<&std::path::Path>) -> i64 {
    use std::io::Read;
    let mut text = String::new();
    path.and_then(|p| std::fs::File::open(p).ok())
        .and_then(|f| f.take(32).read_to_string(&mut text).ok())
        .and_then(|_| text.trim().parse::<i64>().ok())
        .unwrap_or(0)
}
