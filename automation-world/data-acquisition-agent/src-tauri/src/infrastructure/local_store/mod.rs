//! 本地SQLite双库与公平有界执行队列：统一串行数据库工作，不在PLC/UI等待中持有事务。
pub(crate) mod capacity;
mod configuration;
pub(crate) mod delivery;
#[cfg(test)]
pub(crate) mod delivery_tests;
#[cfg(test)]
mod point_naming_tests;
mod profile_contract;
#[cfg(test)]
pub(crate) use profile_contract::preflight;
#[cfg(all(test, unix))]
mod profile_contract_tests;
mod runtime;
mod schema;
#[cfg(test)]
mod source_import_tests;
#[cfg(test)]
mod tests;
mod yaml_migration;
use crate::domain::facts_wire::text;
use crate::domain::local_configuration::{id, Configuration, LocalResult};
use crate::domain::local_delivery::DeliverySettings;
use crate::domain::local_sample::encode;
use delivery::event;
use rusqlite::{params, Connection};
use serde_json::Value;
use std::{
    collections::VecDeque,
    path::{Path, PathBuf},
    sync::{
        atomic::{AtomicBool, AtomicUsize, Ordering},
        mpsc::{self, SyncSender},
        Arc, Mutex,
    },
    thread,
    time::Duration,
};
pub(crate) fn sql_error(e: rusqlite::Error) -> String {
    match e.sqlite_error_code() {
        Some(rusqlite::ErrorCode::DatabaseBusy) | Some(rusqlite::ErrorCode::DatabaseLocked) => {
            "storage_busy".into()
        }
        Some(rusqlite::ErrorCode::OperationInterrupted) => "storage_timeout".into(),
        _ => format!("storage_error:{e}"),
    }
}
pub(crate) struct Stores {
    pub log: Arc<crate::infrastructure::local_logging::LocalLog>,
    pub config: Connection,
    pub runtime: Connection,
    pub dir: PathBuf,
    pub instance: String,
    pub busy_count: u64,
    pub cleanup_cursor: i64,
    pub last_maintenance: std::time::Instant,
    _profile_lock: LockedProfile,
    #[cfg(test)]
    pub test_after_cleanup_free: Option<u64>,
    #[cfg(test)]
    pub test_meter: Option<(
        Arc<std::sync::atomic::AtomicU64>,
        Arc<std::sync::atomic::AtomicU64>,
    )>,
}
#[derive(Debug)]
pub(super) enum ProbeFailure {
    Sqlite(&'static str, rusqlite::Error),
    Other(String),
}
impl ProbeFailure {
    pub fn message(self) -> String {
        match self {
            Self::Sqlite(_, e) => unsupported(e),
            Self::Other(s) => s,
        }
    }
}
fn unsupported(reason: impl std::fmt::Display) -> String {
    format!("time_profile_unsupported:{reason}")
}
/// 只记录本进程在用profile，避免重入hash的close释放同进程SQLite锁；OS排他仍归原ProfileLock。
pub(super) struct ProcessClaim(PathBuf);
static PROCESS_PROFILES: std::sync::OnceLock<
    Mutex<std::collections::BTreeMap<PathBuf, Option<(u64, u64)>>>,
> = std::sync::OnceLock::new();
impl ProcessClaim {
    fn identity(path: &Path) -> Option<(u64, u64)> {
        #[cfg(unix)]
        {
            use std::os::unix::fs::MetadataExt;
            let m = std::fs::symlink_metadata(path).ok()?;
            if m.is_dir() && !m.file_type().is_symlink() {
                Some((m.dev(), m.ino()))
            } else {
                None
            }
        }
        #[cfg(not(unix))]
        {
            let _ = path;
            None
        }
    }
    fn new(profile: &Path) -> LocalResult<Self> {
        let identity = Self::identity(profile);
        let mut profiles = PROCESS_PROFILES
            .get_or_init(Default::default)
            .lock()
            .map_err(|_| "profile_locked")?;
        if profiles.contains_key(profile)
            || (identity.is_some() && profiles.values().any(|v| *v == identity))
        {
            return Err("profile_locked".into());
        }
        profiles.insert(profile.into(), identity);
        Ok(Self(profile.into()))
    }
    fn refresh(&self) -> LocalResult<()> {
        let identity = Self::identity(&self.0);
        let mut profiles = PROCESS_PROFILES
            .get_or_init(Default::default)
            .lock()
            .map_err(|_| "profile_locked")?;
        if identity.is_some()
            && profiles
                .iter()
                .any(|(path, id)| path != &self.0 && *id == identity)
        {
            return Err("profile_locked".into());
        }
        profiles.insert(self.0.clone(), identity);
        Ok(())
    }
}
impl Drop for ProcessClaim {
    fn drop(&mut self) {
        if let Ok(mut profiles) = PROCESS_PROFILES.get_or_init(Default::default).lock() {
            profiles.remove(&self.0);
        }
    }
}
pub(super) struct LockedProfile {
    _os: crate::infrastructure::local_profile_lock::ProfileLock,
    _process: ProcessClaim,
}
pub(super) fn inspect_one(dir: &Path, role: &'static str) -> Result<(String, u32), ProbeFailure> {
    let c = Connection::open_with_flags(
        dir.join(format!("{role}.sqlite")),
        rusqlite::OpenFlags::SQLITE_OPEN_READ_ONLY | rusqlite::OpenFlags::SQLITE_OPEN_NO_MUTEX,
    )
    .map_err(|e| ProbeFailure::Sqlite(role, e))?;
    let checked = (|| {
        let sql = |e| ProbeFailure::Sqlite(role, e);
        let bad = |s: &str| ProbeFailure::Other(unsupported(s));
        c.busy_timeout(Duration::from_millis(1000)).map_err(sql)?;
        c.execute_batch("PRAGMA trusted_schema=OFF; PRAGMA query_only=ON;")
            .map_err(sql)?;
        let app: i64 = c
            .query_row("PRAGMA application_id", [], |r| r.get(0))
            .map_err(sql)?;
        let version: u32 = c
            .query_row("PRAGMA user_version", [], |r| r.get(0))
            .map_err(sql)?;
        if (role == "config" && (app != schema::CONFIG_APP || version != 2))
            || (role == "runtime" && (app != schema::RUNTIME_APP || ![2, 3].contains(&version)))
        {
            return Err(bad("schema_version_mismatch"));
        }
        let table = if role == "config" {
            "instance_metadata"
        } else {
            "runtime_metadata"
        };
        let (instance, v, time): (String, u32, String) = c
            .query_row(
                &format!("SELECT instance_id,schema_version,time_profile FROM {table} WHERE id=1"),
                [],
                |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?)),
            )
            .map_err(sql)?;
        let migration: u32 = c
            .query_row("SELECT max(version) FROM schema_migrations", [], |r| {
                r.get(0)
            })
            .map_err(sql)?;
        if v != version
            || migration != version
            || time != crate::domain::business_time::TIME_PROFILE
            || !crate::domain::local_configuration::valid_id(&instance)
        {
            return Err(bad("metadata_mismatch"));
        }
        let ddl = if role == "config" {
            schema::config_sql()
        } else if version == 3 {
            schema::runtime_v3_sql()
        } else {
            schema::runtime_sql()
        };
        schema::verify_structure(&c, &ddl).map_err(|e| ProbeFailure::Other(unsupported(e)))?;
        if role == "runtime" && version == 3 {
            delivery::verify_schema(&c).map_err(|e| ProbeFailure::Other(unsupported(e)))?;
        }
        Ok((instance, version))
    })();
    let closed = c.close().map_err(|(_, e)| ProbeFailure::Sqlite(role, e));
    let value = checked?;
    closed?;
    Ok(value)
}
pub(super) fn inspect_sql(dir: &Path) -> Result<Option<String>, ProbeFailure> {
    let a = dir.join("config.sqlite");
    let b = dir.join("runtime.sqlite");
    if !a.exists() && !b.exists() {
        if dir.exists()
            && std::fs::read_dir(dir)
                .map_err(|e| ProbeFailure::Other(unsupported(e)))?
                .next()
                .is_some()
        {
            return Err(ProbeFailure::Other(unsupported("directory_not_empty")));
        }
        return Ok(None);
    }
    if a.exists() != b.exists() {
        return Err(ProbeFailure::Other(unsupported("missing_database")));
    }
    let config = inspect_one(dir, "config")?;
    let runtime = inspect_one(dir, "runtime")?;
    if config.0 != runtime.0 {
        return Err(ProbeFailure::Other(unsupported("instance_mismatch")));
    }
    Ok(Some(config.0))
}
fn connect(p: &Path, new: bool, app: i64) -> LocalResult<Connection> {
    for suffix in ["-wal", "-shm"] {
        if PathBuf::from(format!("{}{suffix}", p.display())).exists() {
            return Err("unexpected_wal_material".into());
        }
    }
    let c = Connection::open_with_flags(
        p,
        rusqlite::OpenFlags::SQLITE_OPEN_READ_WRITE | rusqlite::OpenFlags::SQLITE_OPEN_NO_MUTEX,
    )
    .map_err(sql_error)?;
    if new {
        c.execute_batch(
            "PRAGMA page_size=4096; PRAGMA auto_vacuum=INCREMENTAL; PRAGMA journal_mode=DELETE;",
        )
        .map_err(sql_error)?;
    }
    let mode: String = c
        .query_row("PRAGMA journal_mode", [], |r| r.get(0))
        .map_err(sql_error)?;
    if mode != "delete" {
        return Err("wrong_journal_mode".into());
    }
    c.execute_batch("PRAGMA synchronous=EXTRA; PRAGMA foreign_keys=ON; PRAGMA busy_timeout=1000; PRAGMA trusted_schema=OFF; PRAGMA mmap_size=0;").map_err(sql_error)?;
    for (key, want) in [
        ("page_size", 4096),
        ("auto_vacuum", 2),
        ("synchronous", 3),
        ("foreign_keys", 1),
        ("busy_timeout", 1000),
    ] {
        let got: i64 = c
            .query_row(&format!("PRAGMA {key}"), [], |r| r.get(0))
            .map_err(sql_error)?;
        if got != want {
            return Err("sqlite_parameters".into());
        }
    }
    if !new {
        for (key, want) in [("application_id", app)] {
            let got: i64 = c
                .query_row(&format!("PRAGMA {key}"), [], |r| r.get(0))
                .map_err(sql_error)?;
            if got != want {
                return Err("schema_mismatch".into());
            }
        }
        let version: i64 = c
            .query_row("PRAGMA user_version", [], |r| r.get(0))
            .map_err(sql_error)?;
        if (app == schema::CONFIG_APP && version != 2)
            || (app == schema::RUNTIME_APP && ![2, 3].contains(&version))
        {
            return Err("schema_mismatch".into());
        }
        let check: String = c
            .query_row("PRAGMA integrity_check", [], |r| r.get(0))
            .map_err(sql_error)?;
        if check != "ok" {
            return Err("storage_corrupt".into());
        }
    }
    Ok(c)
}
pub(super) fn initialize_pair(dir: &Path) -> LocalResult<()> {
    let a = dir.join("config.sqlite");
    let b = dir.join("runtime.sqlite");
    let new = true;
    let mut config = connect(&a, new, schema::CONFIG_APP)?;
    let mut runtime = match connect(&b, new, schema::RUNTIME_APP) {
        Ok(c) => c,
        Err(e) => {
            config.close().map_err(|(_, e)| sql_error(e))?;
            return Err(e);
        }
    };
    let initialized: LocalResult<()> = (|| {
        let instance = id();
        let payload = encode(&Configuration::default())?;
        let tx = config.transaction().map_err(sql_error)?;
        tx.execute_batch(&schema::config_sql()).map_err(sql_error)?;
        tx.execute(
            "INSERT INTO instance_metadata VALUES(1,?1,2,'asia-shanghai-rfc3339-ms-v1')",
            [&instance],
        )
        .map_err(sql_error)?;
        tx.execute(
            "INSERT INTO configuration_draft VALUES(1,?1,?2,'[]')",
            rusqlite::params![id(), payload],
        )
        .map_err(sql_error)?;
        tx.execute_batch(&format!(
            "PRAGMA application_id={}; PRAGMA user_version=2;",
            schema::CONFIG_APP
        ))
        .map_err(sql_error)?;
        tx.commit().map_err(sql_error)?;
        profile_contract::checkpoint("config_committed", dir)?;
        let tx = runtime.transaction().map_err(sql_error)?;
        tx.execute_batch(&schema::runtime_v3_sql())
            .map_err(sql_error)?;
        tx.execute(
            "INSERT INTO runtime_metadata VALUES(1,?1,3,1,NULL,'asia-shanghai-rfc3339-ms-v1')",
            [&instance],
        )
        .map_err(sql_error)?;
        tx.execute_batch(&format!(
            "PRAGMA application_id={}; PRAGMA user_version=3;",
            schema::RUNTIME_APP
        ))
        .map_err(sql_error)?;
        let settings = crate::domain::local_delivery::DeliverySettings::default();
        tx.execute(
            "INSERT INTO delivery_settings(id,settings_revision,payload) VALUES(1,?1,?2)",
            rusqlite::params![settings.settings_revision, encode(&settings)?],
        )
        .map_err(sql_error)?;
        tx.commit().map_err(sql_error)?;
        profile_contract::checkpoint("runtime_committed", dir)?;
        Ok(())
    })();
    let config_closed = config.close().map_err(|(_, e)| sql_error(e));
    let runtime_closed = runtime.close().map_err(|(_, e)| sql_error(e));
    initialized?;
    config_closed?;
    runtime_closed?;
    profile_contract::checkpoint("sqlite_close", dir)?;
    Ok(())
}
impl Stores {
    pub fn open(dir: &Path) -> LocalResult<Self> {
        let lock = profile_contract::admit(dir)?;
        let dir = profile_contract::canonical(dir)?;
        let config = connect(&dir.join("config.sqlite"), false, schema::CONFIG_APP)?;
        let runtime = connect(&dir.join("runtime.sqlite"), false, schema::RUNTIME_APP)?;
        let instance: String = config
            .query_row(
                "SELECT instance_id FROM instance_metadata WHERE id=1",
                [],
                |r| r.get(0),
            )
            .map_err(sql_error)?;
        let other: String = runtime
            .query_row(
                "SELECT instance_id FROM runtime_metadata WHERE id=1",
                [],
                |r| r.get(0),
            )
            .map_err(sql_error)?;
        if instance != other {
            return Err("instance_mismatch".into());
        }
        let mut s = Self {
            log: Arc::new(crate::infrastructure::local_logging::LocalLog::new(
                dir.join("logs"),
            )?),
            config,
            runtime,
            dir: dir.clone(),
            instance,
            busy_count: 0,
            cleanup_cursor: 0,
            last_maintenance: std::time::Instant::now(),
            _profile_lock: lock,
            #[cfg(test)]
            test_after_cleanup_free: None,
            #[cfg(test)]
            test_meter: None,
        };
        s.recover_activation()?;
        if s.delivery_available()? {
            s.recover_delivery()?;
        }
        let clean: i64 = s
            .runtime
            .query_row(
                "SELECT clean_exit FROM runtime_metadata WHERE id=1",
                [],
                |r| r.get(0),
            )
            .map_err(sql_error)?;
        if clean == 0 {
            s.event("uncertain_gap", "instance", "restart")?;
        }
        s.runtime
            .execute("UPDATE runtime_metadata SET clean_exit=0 WHERE id=1", [])
            .map_err(sql_error)?;
        Ok(s)
    }
    pub fn event(&mut self, event: &str, resource: &str, result: &str) -> LocalResult<()> {
        let tx = self.runtime.transaction().map_err(sql_error)?;
        tx.execute(
            "INSERT INTO runtime_events(event,resource,result,created_at) VALUES(?1,?2,?3,?4)",
            rusqlite::params![event, resource, result, crate::domain::local_sample::now()],
        )
        .map_err(sql_error)?;
        tx.execute(
            "DELETE FROM runtime_events WHERE id < (SELECT max(id) FROM runtime_events)-499",
            [],
        )
        .map_err(sql_error)?;
        tx.commit().map_err(sql_error)
    }
    pub fn clean_exit(&mut self) -> LocalResult<()> {
        self.runtime
            .execute("UPDATE runtime_metadata SET clean_exit=1 WHERE id=1", [])
            .map_err(sql_error)?;
        Ok(())
    }
}
type Work = Box<dyn FnOnce(&mut Stores) + Send>;
struct Job {
    query: bool,
    run: Work,
}
#[derive(Clone)]
pub(crate) struct StoreHandle {
    log: Arc<crate::infrastructure::local_logging::LocalLog>,
    sender: SyncSender<Job>,
    writes: Arc<AtomicUsize>,
    queries: Arc<AtomicUsize>,
    closed: Arc<AtomicBool>,
    join: Arc<Mutex<Option<thread::JoinHandle<()>>>>,
}
impl StoreHandle {
    pub fn start(stores: Stores) -> Self {
        let log = stores.log.clone();
        let (tx, rx) = mpsc::sync_channel::<Job>(8);
        let writes = Arc::new(AtomicUsize::new(0));
        let queries = Arc::new(AtomicUsize::new(0));
        let closed = Arc::new(AtomicBool::new(false));
        let (w, q, end) = (writes.clone(), queries.clone(), closed.clone());
        let join = thread::spawn(move || {
            let mut s = stores;
            let (mut ws, mut qs) = (VecDeque::new(), VecDeque::new());
            let mut burst = 0;
            loop {
                while let Ok(j) = rx.try_recv() {
                    if j.query {
                        qs.push_back(j)
                    } else {
                        ws.push_back(j)
                    }
                }
                if ws.is_empty() && qs.is_empty() {
                    if end.load(Ordering::SeqCst) {
                        break;
                    }
                    match rx.recv_timeout(Duration::from_millis(20)) {
                        Ok(j) => {
                            if j.query {
                                qs.push_back(j)
                            } else {
                                ws.push_back(j)
                            }
                        }
                        Err(_) => continue,
                    }
                }
                let j = if !qs.is_empty() && (burst >= 4 || ws.is_empty()) {
                    burst = 0;
                    qs.pop_front()
                } else {
                    burst += 1;
                    ws.pop_front()
                };
                if let Some(j) = j {
                    let is_query = j.query;
                    (j.run)(&mut s);
                    if s.last_maintenance.elapsed() >= Duration::from_secs(60)
                        && s.log.health().is_ok()
                    {
                        s.last_maintenance = std::time::Instant::now();
                        let result = s.maintain();
                        if let Err(e) = result {
                            // This is the writer itself: never call back through Engine/storage.call.
                            // The shared logger reports and latches an unknown interval if persistence fails.
                            let _ = s.log.maintenance_failed(&e);
                        }
                    }
                    if is_query {
                        q.fetch_sub(1, Ordering::SeqCst);
                    } else {
                        w.fetch_sub(1, Ordering::SeqCst);
                    }
                }
            }
            let _ = s.clean_exit();
        });
        Self {
            log,
            sender: tx,
            writes,
            queries,
            closed,
            join: Arc::new(Mutex::new(Some(join))),
        }
    }
    pub fn call<T: Send + 'static>(
        &self,
        query: bool,
        f: impl FnOnce(&mut Stores) -> LocalResult<T> + Send + 'static,
    ) -> LocalResult<T> {
        if !query {
            self.log.health()?;
        }
        if self.closed.load(Ordering::SeqCst) {
            return Err("storage_closed".into());
        }
        let counter = if query { &self.queries } else { &self.writes };
        let max = if query { 5 } else { 4 };
        if counter.fetch_add(1, Ordering::SeqCst) >= max {
            counter.fetch_sub(1, Ordering::SeqCst);
            return Err("storage_busy".into());
        }
        let deadline = std::time::Instant::now() + Duration::from_millis(1000);
        let (tx, rx) = mpsc::sync_channel(1);
        let j = Job {
            query,
            run: Box::new(move |s| {
                if query && std::time::Instant::now() >= deadline {
                    let _ = tx.send(Err("storage_timeout".into()));
                    return;
                }
                let mut timer = None;
                let mut cancel = None;
                if query {
                    let a = s.config.get_interrupt_handle();
                    let b = s.runtime.get_interrupt_handle();
                    let (tx, rx) = mpsc::channel();
                    cancel = Some(tx);
                    timer = Some(thread::spawn(move || {
                        if rx
                            .recv_timeout(
                                deadline.saturating_duration_since(std::time::Instant::now()),
                            )
                            .is_err()
                        {
                            a.interrupt();
                            b.interrupt();
                        }
                    }));
                }
                let r = f(s);
                if r.as_ref()
                    .err()
                    .map(|e| e == "storage_busy")
                    .unwrap_or(false)
                {
                    s.busy_count = s.busy_count.saturating_add(1);
                }
                if let Some(tx) = cancel {
                    let _ = tx.send(());
                }
                if let Some(j) = timer {
                    let _ = j.join();
                }
                let _ = tx.send(r);
            }),
        };
        if self.sender.try_send(j).is_err() {
            counter.fetch_sub(1, Ordering::SeqCst);
            return Err("storage_busy".into());
        }
        rx.recv_timeout(if query {
            deadline.saturating_duration_since(std::time::Instant::now())
        } else {
            Duration::from_secs(10)
        })
        .map_err(|_| {
            if query {
                "storage_timeout"
            } else {
                "storage_pending"
            }
            .to_string()
        })?
    }
    pub fn shutdown(&self) {
        self.closed.store(true, Ordering::SeqCst);
        if let Some(j) = self.join.lock().unwrap().take() {
            let _ = j.join();
        }
    }
}

impl Drop for StoreHandle {
    fn drop(&mut self) {
        if Arc::strong_count(&self.join) == 1 {
            self.shutdown();
        }
    }
}

// Independent delivery settings CAS and physical accounting use the same serial Store owner.
impl Stores {
    pub fn delivery_settings(&self) -> LocalResult<DeliverySettings> {
        self.delivery_guard()?;
        let raw: String = self
            .runtime
            .query_row(
                "SELECT payload FROM delivery_settings WHERE id=1",
                [],
                |r| r.get(0),
            )
            .map_err(sql_error)?;
        serde_json::from_str(&raw).map_err(|_| "delivery_settings_corrupt".into())
    }
    pub fn save_delivery_settings(
        &mut self,
        mut settings: DeliverySettings,
        expected: String,
    ) -> LocalResult<DeliverySettings> {
        self.delivery_guard()?;
        settings.validate()?;
        let old = self.delivery_settings()?;
        if old.settings_revision != expected {
            return Err("settings_conflict".into());
        }
        let count:i64=self.runtime.query_row("SELECT count(*) FROM delivery_batches WHERE state!='acknowledged' AND state!='rejected' AND NOT(state='blocked' AND body IS NULL AND request_digest='' AND body_sha='' AND attempt=0 AND parent_id IS NULL AND last_error='source_adoption_required')",[],|r|r.get(0)).map_err(sql_error)?;
        if count > 0
            && (old.target_id != settings.target_id
                || old.origin != settings.origin
                || old.adoption_reference != settings.adoption_reference
                || old.contract_pins != settings.contract_pins
                || serde_json::to_value(&old.sources).unwrap()
                    != serde_json::to_value(&settings.sources).unwrap())
        {
            return Err(format!("delivery_target_unresolved:{count}"));
        }
        let mut resolved = vec![];
        if old.target_id == settings.target_id
            && old.origin == settings.origin
            && old.contract_pins == settings.contract_pins
        {
            let diagnostics=self.runtime.prepare("SELECT batch_id,members FROM delivery_batches WHERE state='blocked' AND body IS NULL AND request_digest='' AND body_sha='' AND attempt=0 AND parent_id IS NULL AND last_error='source_adoption_required'").map_err(sql_error)?.query_map([],|r|Ok((r.get::<_,String>(0)?,r.get::<_,String>(1)?))).map_err(sql_error)?.take(100).collect::<std::result::Result<Vec<_>,_>>().map_err(sql_error)?;
            for (batch, members) in diagnostics {
                let v: Value = serde_json::from_str(&members).map_err(|_| "delivery_corrupt")?;
                let cycle = text(&v, "cycleId")?;
                if let Ok(built) = self.build_delivery_cycle(cycle) {
                    if Self::source_admitted(&settings, &built) {
                        resolved.push((batch, cycle.to_string()));
                    }
                }
            }
        }
        settings.settings_revision = id();
        let quota = self.delivery_quota()?;
        self.admit_maintenance(quota)?;
        let tx = self.runtime.transaction().map_err(sql_error)?;
        let n=tx.execute("UPDATE delivery_settings SET settings_revision=?1,payload=?2 WHERE id=1 AND settings_revision=?3",params![settings.settings_revision,encode(&settings)?,expected]).map_err(sql_error)?;
        if n != 1 {
            return Err("settings_conflict".into());
        }
        for (batch, cycle) in resolved {
            tx.execute(
                "DELETE FROM sample_references WHERE reference_id=?1",
                [format!("delivery-blocked:{cycle}")],
            )
            .map_err(sql_error)?;
            tx.execute("DELETE FROM delivery_batches WHERE batch_id=?1 AND state='blocked' AND body IS NULL AND request_digest='' AND body_sha='' AND attempt=0 AND parent_id IS NULL AND last_error='source_adoption_required'",[&batch]).map_err(sql_error)?;
            event(
                &tx,
                "delivery_recovered",
                &batch,
                "source_material_rechecked",
            )?;
        }
        tx.commit().map_err(sql_error)?;
        Ok(settings)
    }
    pub(super) fn delivery_quota(&self) -> LocalResult<u64> {
        let view = self.configuration()?;
        Ok(match view.active {
            Some(r) => self.revision(&r)?.storage.quota_bytes,
            None => 1024 * 1024 * 1024,
        })
    }
    pub fn delivery_bytes(&self) -> LocalResult<(u64, u64, u64)> {
        let req: u64 = self
            .runtime
            .query_row(
                "SELECT coalesce(sum(length(CAST(body AS BLOB))),0) FROM delivery_batches",
                [],
                |r| r.get(0),
            )
            .map_err(sql_error)?;
        let ack:u64=self.runtime.query_row("SELECT coalesce(sum(length(CAST(response_utf8 AS BLOB))),0) FROM delivery_receipts",[],|r|r.get(0)).map_err(sql_error)?;
        let metadata:u64=self.runtime.query_row("SELECT (SELECT coalesce(sum(length(CAST(wire AS BLOB))),0) FROM delivery_cycles)+(SELECT coalesce(sum(length(CAST(members AS BLOB))),0) FROM delivery_batches)+(SELECT coalesce(sum(length(CAST(payload AS BLOB))),0) FROM delivery_settings)+(SELECT coalesce(sum(length(CAST(point_ids AS BLOB))),0) FROM delivery_parts)",[],|r|r.get(0)).map_err(sql_error)?;
        Ok((req, ack, metadata))
    }
}

impl Stores {
    pub fn read_result(&mut self, plc: &str, result: &str) -> LocalResult<()> {
        self.delivery_guard()?;
        let tx = self.runtime.transaction().map_err(sql_error)?;
        event(&tx, "read_result", plc, result)?;
        tx.commit().map_err(sql_error)?;
        self.log.event("read_result", plc, result)
    }
}

impl Stores {
    pub fn delivery_schedule(&self) -> LocalResult<Vec<(String, String)>> {
        self.delivery_guard()?;
        let rows=self.runtime.prepare("SELECT batch_id,next_attempt_at FROM delivery_batches WHERE state='prepared' OR state='unknown' OR state='retry_wait' ORDER BY created_order LIMIT 9").map_err(sql_error)?.query_map([],|r|Ok((r.get(0)?,r.get(1)?))).map_err(sql_error)?.collect::<std::result::Result<Vec<_>,_>>().map_err(sql_error)?;
        if rows.len() > 8 {
            return Err("delivery_queue_limit".into());
        }
        Ok(rows)
    }
    #[cfg(test)]
    pub fn next_delivery(&mut self) -> LocalResult<Option<delivery::Frozen>> {
        let now = delivery::db_now(&self.runtime)?;
        let due=self.runtime.prepare("SELECT batch_id FROM delivery_batches WHERE state='prepared' OR ((state='unknown' OR state='retry_wait') AND next_attempt_at<=?1) ORDER BY created_order LIMIT 8").map_err(sql_error)?.query_map([now],|r|r.get(0)).map_err(sql_error)?.collect::<std::result::Result<Vec<_>,_>>().map_err(sql_error)?;
        self.next_delivery_ready(due)
    }
}

impl Stores {
    pub fn recover_delivery(&mut self) -> LocalResult<()> {
        self.delivery_guard()?;
        let tx = self.runtime.transaction().map_err(sql_error)?;
        let now = delivery::db_now(&tx)?;
        tx.execute("UPDATE delivery_batches SET state='unknown',last_error='process_restarted',next_attempt_at=?1 WHERE state='inflight'",[&now]).map_err(sql_error)?;
        let rows=tx.prepare("SELECT batch_id,next_attempt_at FROM delivery_batches WHERE state='prepared' OR state='unknown' OR state='retry_wait' ORDER BY created_order LIMIT 9").map_err(sql_error)?.query_map([],|r|Ok((r.get::<_,String>(0)?,r.get::<_,String>(1)?))).map_err(sql_error)?.collect::<std::result::Result<Vec<_>,_>>().map_err(sql_error)?;
        if rows.len() > 8 {
            return Err("delivery_queue_limit".into());
        }
        for (id, at) in rows {
            let delay = (crate::domain::facts_wire::time(&at)?
                - crate::domain::facts_wire::time(&now)?)
            .num_seconds()
            .clamp(1, 300);
            let next = (crate::domain::facts_wire::time(&now)? + chrono::Duration::seconds(delay))
                .to_rfc3339_opts(chrono::SecondsFormat::Millis, true);
            tx.execute(
                "UPDATE delivery_batches SET next_attempt_at=?1 WHERE batch_id=?2",
                params![next, id],
            )
            .map_err(sql_error)?;
        }
        tx.commit().map_err(sql_error)
    }
}

use rusqlite::ToSql;
use serde_json::json;
pub(super) fn str_at(row: &Value, index: usize) -> LocalResult<&str> {
    row[index]
        .as_str()
        .ok_or_else(|| "profile_ledger_invalid".into())
}
pub(super) fn number(row: &Value, index: usize) -> LocalResult<i64> {
    row[index]
        .as_i64()
        .ok_or_else(|| "profile_ledger_invalid".into())
}
pub(super) fn record(c: &Connection, sql: &str, args: &[&dyn ToSql]) -> LocalResult<Value> {
    c.query_row(sql, args, |r| {
        let mut fields = vec![];
        for i in 0..r.as_ref().column_count() {
            fields.push(match r.get_ref(i)? {
                rusqlite::types::ValueRef::Null => Value::Null,
                rusqlite::types::ValueRef::Integer(n) => json!(n),
                rusqlite::types::ValueRef::Text(_) => json!(r.get::<_, String>(i)?),
                v => {
                    return Err(rusqlite::Error::InvalidColumnType(
                        i,
                        String::new(),
                        v.data_type(),
                    ))
                }
            });
        }
        Ok(Value::Array(fields))
    })
    .map_err(sql_error)
}
pub(super) fn count(c: &Connection, sql: &str, args: &[&dyn ToSql]) -> LocalResult<i64> {
    number(&record(c, sql, args)?, 0)
}

pub(super) fn require(ok: bool) -> LocalResult<()> {
    if ok {
        Ok(())
    } else {
        Err("profile_ledger_invalid".into())
    }
}
