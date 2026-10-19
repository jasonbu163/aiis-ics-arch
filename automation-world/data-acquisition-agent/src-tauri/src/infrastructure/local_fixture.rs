//! 仅测试/非默认debug验证编入的冻结内存transport；无网络、SQL或ACK写通道。
use super::managed_s7::Transport;
use crate::domain::local_configuration::{LocalResult, Plc};
use serde::Deserialize;
use std::{
    collections::BTreeMap,
    path::Path,
    sync::{Arc, OnceLock},
    time::Duration,
};
#[derive(Clone, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct FixtureSet {
    pub schema_version: u32,
    pub endpoints: BTreeMap<String, FixtureEndpoint>,
    pub fail_at: Option<String>,
}
#[derive(Clone, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub(crate) struct FixtureEndpoint {
    pub dbs: BTreeMap<u16, Vec<u8>>,
    #[serde(default)]
    pub fail_dbs: Vec<u16>,
    #[serde(default)]
    pub delay_ms: u64,
    #[serde(default)]
    pub connect_failure: bool,
}
static FAIL: OnceLock<Option<String>> = OnceLock::new();
impl FixtureSet {
    pub fn load(path: &Path) -> LocalResult<Arc<Self>> {
        let bytes = std::fs::read(path).map_err(|_| "fixture_io")?;
        if bytes.len() > 4 * 1024 * 1024 {
            return Err("fixture_limits".into());
        }
        let f: Self = serde_json::from_slice(&bytes).map_err(|_| "fixture_invalid")?;
        if f.schema_version != 1
            || f.endpoints.len() > 4
            || f.endpoints.values().any(|p| {
                p.delay_ms > 5500 || p.dbs.len() > 32 || p.dbs.values().any(|b| b.len() > 65536)
            })
        {
            return Err("fixture_limits".into());
        }
        if f.fail_at
            .as_deref()
            .map(|s| {
                ![
                    "activation_prepared",
                    "activation_context",
                    "activation_selected",
                    "activation_loaded",
                    "activation_applied",
                    "cycle_before_commit",
                    "cycle_after_commit",
                    "cycle_hot_journal",
                ]
                .contains(&s)
            })
            .unwrap_or(false)
        {
            return Err("fixture_failpoint".into());
        }
        let _ = FAIL.set(f.fail_at.clone());
        Ok(Arc::new(f))
    }
}
#[cfg(feature = "local-validation")]
pub(crate) fn failpoint(name: &str) {
    if FAIL.get().and_then(|v| v.as_deref()) == Some(name) {
        std::process::abort()
    }
}
pub(crate) struct FixtureTransport {
    pub set: Arc<FixtureSet>,
    key: Option<String>,
}
impl FixtureTransport {
    pub fn new(set: Arc<FixtureSet>) -> Self {
        Self { set, key: None }
    }
}
impl Transport for FixtureTransport {
    fn connect(&mut self, p: &Plc) -> LocalResult<()> {
        let key = p.endpoint();
        let f = self
            .set
            .endpoints
            .get(&key)
            .ok_or("fixture_endpoint_missing")?;
        if f.connect_failure {
            return Err("connection_failed".into());
        }
        self.key = Some(key);
        Ok(())
    }
    fn read(&mut self, db: u16, start: u32, size: u32) -> LocalResult<Vec<u8>> {
        let p = self
            .set
            .endpoints
            .get(self.key.as_deref().ok_or("disconnected")?)
            .ok_or("fixture_endpoint_missing")?;
        std::thread::sleep(Duration::from_millis(p.delay_ms));
        if p.fail_dbs.contains(&db) {
            return Err("read_failed".into());
        }
        let b = p.dbs.get(&db).ok_or("bad_db")?;
        let end = start.checked_add(size).ok_or("bad_address")?;
        b.get(start as usize..end as usize)
            .map(|s| s.to_vec())
            .ok_or_else(|| "bad_length".into())
    }
    fn read_bounded(
        &mut self,
        db: u16,
        start: u32,
        size: u32,
        remaining: Duration,
    ) -> LocalResult<Vec<u8>> {
        let p = self
            .set
            .endpoints
            .get(self.key.as_deref().ok_or("disconnected")?)
            .ok_or("fixture_endpoint_missing")?;
        if Duration::from_millis(p.delay_ms) > remaining {
            std::thread::sleep(remaining);
            return Err("bad_timeout".into());
        }
        self.read(db, start, size)
    }
    fn connected(&self) -> bool {
        self.key.is_some()
    }
    fn disconnect(&mut self) {
        self.key = None
    }
}

#[cfg(feature = "local-validation")]
pub(crate) fn before_cycle_commit(connection: &rusqlite::Connection) {
    if FAIL.get().and_then(|v| v.as_deref()) == Some("cycle_hot_journal") {
        if connection.cache_flush().is_err() {
            eprintln!("{{\"event\":\"cycle_hot_flush_failed\"}}");
            std::process::abort()
        }
        eprintln!("{{\"event\":\"cycle_hot_ready\"}}");
        std::thread::sleep(Duration::from_secs(10));
        std::process::abort()
    }
    failpoint("cycle_before_commit");
}
