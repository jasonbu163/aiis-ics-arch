//! 本地SQLite双库与公平有界执行队列：统一串行数据库工作，不在PLC/UI等待中持有事务。
pub(crate) mod capacity;
mod configuration;
#[cfg(test)]
mod point_naming_tests;
mod runtime;
mod schema;
#[cfg(test)]
mod source_import_tests;
#[cfg(test)]
mod tests;
mod yaml_migration;
use crate::domain::local_configuration::{id, Configuration, LocalResult};
use crate::domain::local_sample::encode;
use rusqlite::Connection;
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
    #[cfg(test)]
    pub test_after_cleanup_free: Option<u64>,
    #[cfg(test)]
    pub test_meter: Option<(
        Arc<std::sync::atomic::AtomicU64>,
        Arc<std::sync::atomic::AtomicU64>,
    )>,
}
/// 无持久写的合同探测；RO连接不使用immutable，也不允许SQLite恢复异常journal。
#[derive(Debug, PartialEq, Eq)]
pub(crate) struct ProfilePreflight(Vec<(PathBuf, String)>);
fn unsupported(reason: impl std::fmt::Display) -> String {
    format!("time_profile_unsupported:{reason}")
}
pub(crate) fn preflight(dir: &Path) -> LocalResult<ProfilePreflight> {
    use sha2::{Digest, Sha256};
    use std::io::Read;
    if dir.is_symlink() {
        return Err(unsupported("profile_symlink"));
    }
    if !dir.exists() {
        return Ok(ProfilePreflight(vec![]));
    }
    let a = dir.join("config.sqlite");
    let b = dir.join("runtime.sqlite");
    if !a.exists() && !b.exists() {
        if std::fs::read_dir(dir)
            .map_err(unsupported)?
            .next()
            .is_some()
        {
            return Err(unsupported("directory_not_empty"));
        }
        return Ok(ProfilePreflight(vec![]));
    }
    if a.exists() != b.exists() {
        return Err(unsupported("missing_database"));
    }
    let mut identities = vec![];
    let mut files = vec![];
    for (path, app, table) in [
        (&a, schema::CONFIG_APP, "instance_metadata"),
        (&b, schema::RUNTIME_APP, "runtime_metadata"),
    ] {
        for suffix in ["", "-journal", "-wal", "-shm"] {
            let file = PathBuf::from(format!("{}{suffix}", path.display()));
            if file.is_symlink() {
                return Err(unsupported("profile_symlink"));
            }
            if !file.exists() {
                continue;
            }
            if suffix == "-wal" || suffix == "-shm" {
                return Err(unsupported("unexpected_wal_material"));
            }
            let mut reader = std::fs::File::open(&file).map_err(unsupported)?;
            let mut hash = Sha256::new();
            let mut buffer = [0u8; 65536];
            loop {
                let n = reader.read(&mut buffer).map_err(unsupported)?;
                if n == 0 {
                    break;
                }
                hash.update(&buffer[..n]);
            }
            files.push((file, format!("{:x}", hash.finalize())));
        }
        // SQLite read-only WAL connections may create shared-memory sidecars. Reject the
        // WAL header before SQLite sees the file; do not rely only on sidecar existence.
        let mut header = [0u8; 100];
        std::fs::File::open(path)
            .map_err(unsupported)?
            .read_exact(&mut header)
            .map_err(unsupported)?;
        if &header[..16] != b"SQLite format 3\0" || header[18] != 1 || header[19] != 1 {
            return Err(unsupported("unsupported_database_header"));
        }
        let c = Connection::open_with_flags(
            path,
            rusqlite::OpenFlags::SQLITE_OPEN_READ_ONLY | rusqlite::OpenFlags::SQLITE_OPEN_NO_MUTEX,
        )
        .map_err(unsupported)?;
        for (key, want) in [("application_id", app), ("user_version", 2)] {
            let got: i64 = c
                .query_row(&format!("PRAGMA {key}"), [], |r| r.get(0))
                .map_err(unsupported)?;
            if got != want {
                return Err(unsupported(format!("{key}_mismatch")));
            }
        }
        let (identity, version, profile): (String, i64, String) = c
            .query_row(
                &format!("SELECT instance_id,schema_version,time_profile FROM {table} WHERE id=1"),
                [],
                |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?)),
            )
            .map_err(unsupported)?;
        if version != 2
            || profile != crate::domain::business_time::TIME_PROFILE
            || !crate::domain::local_configuration::valid_id(&identity)
        {
            return Err(unsupported("metadata_mismatch"));
        }
        identities.push(identity);
    }
    if identities[0] != identities[1] {
        return Err(unsupported("instance_mismatch"));
    }
    Ok(ProfilePreflight(files))
}
impl ProfilePreflight {
    pub(crate) fn recheck(&self, dir: &Path) -> LocalResult<()> {
        if &preflight(dir)? != self {
            return Err(unsupported("profile_changed"));
        }
        Ok(())
    }
}
fn connect(p: &Path, new: bool, app: i64) -> LocalResult<Connection> {
    for suffix in ["-wal", "-shm"] {
        if PathBuf::from(format!("{}{suffix}", p.display())).exists() {
            return Err("unexpected_wal_material".into());
        }
    }
    let c = Connection::open(p).map_err(sql_error)?;
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
        for (key, want) in [("application_id", app), ("user_version", 2)] {
            let got: i64 = c
                .query_row(&format!("PRAGMA {key}"), [], |r| r.get(0))
                .map_err(sql_error)?;
            if got != want {
                return Err("schema_mismatch".into());
            }
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
impl Stores {
    pub fn open(dir: &Path) -> LocalResult<Self> {
        let before = preflight(dir)?;
        before.recheck(dir)?;
        std::fs::create_dir_all(dir).map_err(|_| "profile_io")?;
        let a = dir.join("config.sqlite");
        let b = dir.join("runtime.sqlite");
        if a.exists() != b.exists() {
            return Err("missing_database".into());
        }
        if dir.is_symlink() || a.is_symlink() || b.is_symlink() {
            return Err("profile_symlink".into());
        }
        let new = !a.exists();
        if new
            && std::fs::read_dir(dir)
                .map_err(|_| "profile_io")?
                .next()
                .is_some()
        {
            return Err("directory_not_empty".into());
        }
        let mut config = connect(&a, new, schema::CONFIG_APP)?;
        let mut runtime = connect(&b, new, schema::RUNTIME_APP)?;
        if new {
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
            let tx = runtime.transaction().map_err(sql_error)?;
            tx.execute_batch(&schema::runtime_sql())
                .map_err(sql_error)?;
            tx.execute(
                "INSERT INTO runtime_metadata VALUES(1,?1,2,1,NULL,'asia-shanghai-rfc3339-ms-v1')",
                [&instance],
            )
            .map_err(sql_error)?;
            tx.execute_batch(&format!(
                "PRAGMA application_id={}; PRAGMA user_version=2;",
                schema::RUNTIME_APP
            ))
            .map_err(sql_error)?;
            tx.commit().map_err(sql_error)?;
        }
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
            dir: dir.into(),
            instance,
            busy_count: 0,
            cleanup_cursor: 0,
            last_maintenance: std::time::Instant::now(),
            #[cfg(test)]
            test_after_cleanup_free: None,
            #[cfg(test)]
            test_meter: None,
        };
        s.recover_activation()?;
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
