//! 单SQLite worker：1执行+4等待；请求超时不盲重试，锁在DB关闭后释放。
mod queries;
pub mod schema;
mod transactions;
use crate::{domain::configuration::Workspace, infrastructure::profile_lock::ProfileLock};
use serde::{Deserialize, Serialize};
use std::{
    path::Path,
    sync::{
        mpsc::{self, SyncSender},
        Mutex,
    },
    thread::{self, JoinHandle},
    time::{Duration, Instant},
};
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Snapshot {
    pub etag: String,
    pub workspace: Workspace,
    pub latest_revision: Option<String>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct SaveResult {
    pub result: String,
    pub etag: String,
    pub revision_id: Option<String>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Selection {
    pub instance_id: String,
    pub revision_id: String,
    pub slice_sha256: String,
    pub previous_revision_id: Option<String>,
    pub selection_etag: String,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct RevisionInfo {
    pub revision_id: String,
    pub saved_seq: String,
    pub sha256: String,
    pub created_utc: String,
}
type Reply<T> = mpsc::Sender<Result<T, String>>;
enum Job {
    Revisions(u32, Reply<Vec<RevisionInfo>>),
    RevisionSeq(String, Reply<u64>),
    Load(Reply<Snapshot>),
    Save(String, Workspace, Reply<SaveResult>),
    Revision(String, Reply<Workspace>),
    Selections(Reply<Vec<Selection>>),
    Select(String, String, Option<String>, Reply<Selection>),
    Stop(Reply<()>),
    #[cfg(feature = "test-automation")]
    TestFault(String, Reply<()>),
    #[cfg(feature = "test-automation")]
    TestCheckpoint(String, Reply<()>),
}
pub struct Store {
    sender: SyncSender<(Instant, Job)>,
    join: Mutex<Option<JoinHandle<()>>>,
    pub path: std::path::PathBuf,
    pub profile_id: String,
}
impl Store {
    pub fn open(profile: &Path) -> Result<Self, String> {
        let lock = ProfileLock::acquire(profile)?;
        let path = lock.database.clone();
        let (sender, receiver) = mpsc::sync_channel(4);
        let (ready_tx, ready_rx) = mpsc::channel();
        let join = thread::Builder::new()
            .name("ds-config-store".into())
            .spawn(move || {
                let mut c = match schema::open(&lock) {
                    Ok(c) => {
                        let id = c
                            .query_row(
                                "SELECT profile_id FROM workspace_metadata WHERE singleton=1",
                                [],
                                |r| r.get::<_, String>(0),
                            )
                            .map_err(|_| "storage_identity".to_owned());
                        match id {
                            Ok(id) => {
                                let _ = ready_tx.send(Ok(id));
                                c
                            }
                            Err(e) => {
                                let _ = ready_tx.send(Err(e));
                                return;
                            }
                        }
                    }
                    Err(e) => {
                        let _ = ready_tx.send(Err(e));
                        return;
                    }
                };
                while let Ok((admitted, job)) = receiver.recv() {
                    let deadline: Instant = admitted + Duration::from_secs(1);
                    unsafe extern "C" fn progress(
                        context: *mut std::ffi::c_void,
                    ) -> std::ffi::c_int {
                        let deadline = &*(context as *const Instant);
                        (Instant::now() >= *deadline) as std::ffi::c_int
                    }
                    let remaining = deadline.saturating_duration_since(Instant::now());
                    let _ = c.busy_timeout(remaining.min(Duration::from_millis(1000)));
                    // 指针只在本线程当前job内有效；回调不分配、不等待I/O、不访问owner。
                    unsafe {
                        rusqlite::ffi::sqlite3_progress_handler(
                            c.handle(),
                            512,
                            Some(progress),
                            &deadline as *const Instant as *mut std::ffi::c_void,
                        );
                    }
                    match job {
                        Job::Revisions(offset, reply) => {
                            let _ = reply.send(queries::revisions(&c, offset));
                        }
                        Job::RevisionSeq(id, reply) => {
                            let _ = reply.send(queries::revision_seq(&c, &id));
                        }
                        Job::Load(reply) => {
                            let _ = reply.send(queries::load(&c));
                        }
                        Job::Save(etag, w, reply) => {
                            let _ = reply.send(transactions::save(&mut c, &lock, &etag, w));
                        }
                        Job::Revision(id, reply) => {
                            let _ = reply.send(queries::revision(&c, &id));
                        }
                        Job::Selections(reply) => {
                            let _ = reply.send(queries::selections(&c));
                        }
                        Job::Select(id, revision, expected, reply) => {
                            let _ = reply.send(transactions::select(
                                &mut c, &lock, &id, &revision, expected,
                            ));
                        }
                        #[cfg(feature = "test-automation")]
                        Job::TestFault(point, reply) => {
                            TEST_FAULT.with(|fault| *fault.borrow_mut() = Some(point));
                            let _ = reply.send(Ok(()));
                        }
                        #[cfg(feature = "test-automation")]
                        Job::TestCheckpoint(point, reply) => {
                            let _ = reply.send(test_checkpoint(&point));
                        }
                        Job::Stop(reply) => {
                            let result = c.close().map_err(|_| "storage_close".into());
                            drop(lock);
                            let _ = reply.send(result);
                            return;
                        }
                    }
                    unsafe {
                        rusqlite::ffi::sqlite3_progress_handler(
                            c.handle(),
                            0,
                            None,
                            std::ptr::null_mut(),
                        );
                    }
                }
            })
            .map_err(|_| "storage_thread")?;
        match ready_rx.recv_timeout(Duration::from_secs(1)) {
            Ok(Ok(profile_id)) => Ok(Self {
                sender,
                join: Mutex::new(Some(join)),
                path,
                profile_id,
            }),
            Ok(Err(e)) => {
                let _ = join.join();
                Err(e)
            }
            Err(_) => {
                drop(sender);
                Err("storage_open_timeout".into())
            }
        }
    }
    fn request<T>(&self, make: impl FnOnce(Reply<T>) -> Job, unknown: &str) -> Result<T, String> {
        let (tx, rx) = mpsc::channel();
        self.sender
            .try_send((Instant::now(), make(tx)))
            .map_err(|_| "storage_busy_or_closed")?;
        rx.recv_timeout(Duration::from_secs(1))
            .map_err(|_| unknown.to_owned())?
    }
    pub fn revisions(&self, offset: u32) -> Result<Vec<RevisionInfo>, String> {
        self.request(|r| Job::Revisions(offset, r), "storage_query_timeout")
    }
    pub fn revision_seq(&self, id: &str) -> Result<u64, String> {
        self.request(|r| Job::RevisionSeq(id.into(), r), "storage_query_timeout")
    }
    pub fn load(&self) -> Result<Snapshot, String> {
        self.request(Job::Load, "storage_query_timeout")
    }
    pub fn save(&self, expected: &str, w: Workspace) -> Result<SaveResult, String> {
        self.request(|r| Job::Save(expected.into(), w, r), "save_receipt_unknown")
    }
    pub fn revision(&self, id: &str) -> Result<Workspace, String> {
        self.request(|r| Job::Revision(id.into(), r), "storage_query_timeout")
    }
    pub fn selections(&self) -> Result<Vec<Selection>, String> {
        self.request(Job::Selections, "storage_query_timeout")
    }
    pub fn select(
        &self,
        id: &str,
        revision: &str,
        expected: Option<String>,
    ) -> Result<Selection, String> {
        self.request(
            |r| Job::Select(id.into(), revision.into(), expected, r),
            "selection_receipt_unknown",
        )
    }
    /// 非默认测试功能：每个真实SQLite worker独立、一次性且固定白名单故障点。
    #[cfg(feature = "test-automation")]
    pub fn test_fault(&self, point: &str) -> Result<(), String> {
        if ![
            "insufficient_space",
            "before_save_commit",
            "after_save_commit",
            "before_select_commit",
            "after_select_commit",
            "before_install",
            "after_install",
        ]
        .contains(&point)
        {
            return Err("test_fault_point".into());
        }
        self.request(
            |reply| Job::TestFault(point.into(), reply),
            "test_fault_timeout",
        )
    }
    #[cfg(feature = "test-automation")]
    pub fn test_checkpoint(&self, point: &str) -> Result<(), String> {
        self.request(
            |reply| Job::TestCheckpoint(point.into(), reply),
            "test_fault_timeout",
        )
    }
    pub fn shutdown(&self) -> Result<(), String> {
        if self.join.lock().unwrap().is_none() {
            return Ok(());
        }
        let result = self.request(Job::Stop, "storage_close_timeout");
        if result.is_ok() {
            if let Some(join) = self.join.lock().unwrap().take() {
                join.join().map_err(|_| "storage_thread_panicked")?;
            }
        }
        result
    }
}

#[cfg(feature = "test-automation")]
thread_local! {
    static TEST_FAULT: std::cell::RefCell<Option<String>> = const { std::cell::RefCell::new(None) };
}
#[cfg(feature = "test-automation")]
pub(super) fn test_checkpoint(point: &str) -> Result<(), String> {
    TEST_FAULT.with(|fault| {
        let mut armed = fault.borrow_mut();
        if armed.as_deref() == Some(point) {
            armed.take();
            Err("test_fault".into())
        } else {
            Ok(())
        }
    })
}
