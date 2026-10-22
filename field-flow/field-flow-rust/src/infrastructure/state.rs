//! 文件：src/infrastructure/state.rs；显式schema和单线程SQLite/持久审计actor。
use crate::{
    domain::{hash, id, Intent, Resource},
    infrastructure::{
        audit::Audit,
        posix::{disk_available, InstanceLock},
    },
    Result,
};
use rusqlite::{params, Connection, OpenFlags, OptionalExtension};
use serde_json::{json, Value};
use std::{
    fs::{self, File},
    path::{Path, PathBuf},
    sync::{
        atomic::{AtomicBool, Ordering},
        Arc, Mutex,
    },
    thread,
    time::Duration,
};
use tokio::sync::{mpsc, oneshot};
const SCHEMA: &str = r#"
PRAGMA page_size=4096; PRAGMA journal_mode=DELETE; PRAGMA synchronous=FULL; PRAGMA foreign_keys=ON; PRAGMA max_page_count=16384;
CREATE TABLE store_meta(schema_version INTEGER NOT NULL,implementation TEXT NOT NULL,mode TEXT NOT NULL CHECK(mode IN ('dry_run','execute')),instance_id TEXT NOT NULL,store_uuid TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT(strftime('%Y-%m-%dT%H:%M:%fZ','now')));
CREATE TABLE commands(source_id TEXT NOT NULL,command_id TEXT NOT NULL,flow_id TEXT NOT NULL,target_key TEXT NOT NULL,config_identity_hash TEXT NOT NULL,payload_hash TEXT NOT NULL,value_i16 INTEGER NOT NULL CHECK(value_i16 BETWEEN -32768 AND 32767),issued_at_ms INTEGER NOT NULL,expires_at_ms INTEGER NOT NULL,state TEXT NOT NULL CHECK(state IN('pending','in_flight','confirmed','unknown','expired','canceled','simulated')),dispatch_count INTEGER NOT NULL CHECK(dispatch_count IN(0,1)),run_id TEXT NOT NULL,request_id TEXT,last_error_key TEXT,ack_kind TEXT,created_at TEXT NOT NULL DEFAULT(strftime('%Y-%m-%dT%H:%M:%fZ','now')),updated_at TEXT NOT NULL DEFAULT(strftime('%Y-%m-%dT%H:%M:%fZ','now')),PRIMARY KEY(source_id,command_id));
CREATE TABLE command_events(seq INTEGER PRIMARY KEY AUTOINCREMENT,source_id TEXT NOT NULL,command_id TEXT NOT NULL,run_id TEXT NOT NULL,request_id TEXT,from_state TEXT,to_state TEXT NOT NULL,reason_key TEXT NOT NULL,summary TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT(strftime('%Y-%m-%dT%H:%M:%fZ','now')),FOREIGN KEY(source_id,command_id) REFERENCES commands(source_id,command_id));
CREATE TRIGGER immutable_intent BEFORE UPDATE OF source_id,command_id,flow_id,target_key,config_identity_hash,payload_hash,value_i16,issued_at_ms,expires_at_ms ON commands BEGIN SELECT RAISE(ABORT,'immutable_intent'); END;
CREATE TRIGGER preserve_commands BEFORE DELETE ON commands BEGIN SELECT RAISE(ABORT,'preserve_commands'); END;
CREATE TRIGGER append_events_update BEFORE UPDATE ON command_events BEGIN SELECT RAISE(ABORT,'append_only'); END;
CREATE TRIGGER append_events_delete BEFORE DELETE ON command_events BEGIN SELECT RAISE(ABORT,'append_only'); END;
"#;
fn err(_: rusqlite::Error) -> String {
    "state_io".into()
}
pub fn init(dir: &Path, mode: &str, instance: &str) -> Result<()> {
    if !matches!(mode, "dry_run" | "execute") || !crate::domain::valid_id(instance) {
        return Err("state_arguments".into());
    }
    fs::create_dir(dir).map_err(|_| "state_exists_or_parent_missing")?;
    let result = (|| {
        File::create(dir.join("instance.lock")).map_err(|_| "state_init")?;
        let c = Connection::open(dir.join("state.sqlite")).map_err(err)?;
        c.execute_batch(SCHEMA).map_err(err)?;
        c.execute("INSERT INTO store_meta(schema_version,implementation,mode,instance_id,store_uuid)VALUES(1,'rust',?1,?2,?3)",params![mode,instance,id()]).map_err(err)?;
        Ok(())
    })();
    result
}
pub fn inspect(dir: &Path) -> Result<Value> {
    let c = Connection::open_with_flags(dir.join("state.sqlite"), OpenFlags::SQLITE_OPEN_READ_ONLY)
        .map_err(err)?;
    let meta=c.query_row("SELECT schema_version,implementation,mode,instance_id,store_uuid FROM store_meta",[],|r|Ok(json!({"schema_version":r.get::<_,i64>(0)?,"implementation":r.get::<_,String>(1)?,"mode":r.get::<_,String>(2)?,"instance_id":r.get::<_,String>(3)?,"store_uuid":r.get::<_,String>(4)?}))).map_err(err)?;
    let mut stmt = c
        .prepare("SELECT state,count(*) FROM commands GROUP BY state")
        .map_err(err)?;
    let rows = stmt
        .query_map([], |r| Ok((r.get::<_, String>(0)?, r.get::<_, u64>(1)?)))
        .map_err(err)?;
    let mut counts = serde_json::Map::new();
    for row in rows {
        let (k, n) = row.map_err(err)?;
        counts.insert(k, json!(n));
    }
    Ok(json!({"meta":meta,"counts":counts}))
}
type Job = Box<dyn FnOnce(&mut Store) -> Result<Value> + Send>;
struct Message {
    job: Job,
    reply: oneshot::Sender<Result<Value>>,
}
struct Store {
    c: Connection,
    audit: Audit,
    dir: PathBuf,
    mode: String,
    run_id: String,
    command_limit: u64,
    event_limit: u64,
    finalized: bool,
    #[cfg(feature = "test-fixture")]
    fail_t3: bool,
}
#[derive(Clone)]
pub struct State {
    tx: mpsc::Sender<Message>,
    pub healthy: Arc<AtomicBool>,
    pub lock: Arc<File>,
    gates: Arc<Mutex<Vec<Arc<crate::infrastructure::posix::Gate>>>>,
}
pub struct StateTask {
    join: thread::JoinHandle<Result<()>>,
}
impl StateTask {
    pub async fn join(self) -> Result<()> {
        tokio::task::spawn_blocking(move || self.join.join().map_err(|_| "state_join")?)
            .await
            .map_err(|_| "state_join")?
    }
}
impl State {
    pub fn open(dir: &Path, mode: &str, instance: &str, run_id: &str) -> Result<(Self, StateTask)> {
        if fs::symlink_metadata(dir)
            .map_err(|_| "state_missing")?
            .file_type()
            .is_symlink()
        {
            return Err("state_symlink".into());
        }
        let lock = Arc::new(InstanceLock::acquire(dir)?.0);
        let c = Connection::open_with_flags(
            dir.join("state.sqlite"),
            OpenFlags::SQLITE_OPEN_READ_WRITE,
        )
        .map_err(err)?;
        c.busy_timeout(Duration::from_millis(500)).map_err(err)?;
        c.execute_batch("PRAGMA foreign_keys=ON;PRAGMA journal_mode=DELETE;PRAGMA synchronous=FULL;PRAGMA max_page_count=16384;").map_err(err)?;
        let meta: (i64, String, String, String) = c
            .query_row(
                "SELECT schema_version,implementation,mode,instance_id FROM store_meta",
                [],
                |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?, r.get(3)?)),
            )
            .map_err(err)?;
        if meta != (1, "rust".into(), mode.into(), instance.into()) {
            return Err("state_identity".into());
        }
        if c.query_row("SELECT count(*)FROM store_meta", [], |r| r.get::<_, u64>(0))
            .map_err(err)?
            != 1
        {
            return Err("state_identity".into());
        }
        let audit = Audit::open(dir, run_id, instance)?;
        let mut store = Store {
            c,
            audit,
            dir: dir.to_owned(),
            mode: mode.into(),
            run_id: run_id.into(),
            command_limit: 10000,
            event_limit: 90000,
            finalized: false,
            #[cfg(feature = "test-fixture")]
            fail_t3: false,
        };
        // 恢复在建立任何PLC连接前执行。保守in_flight->unknown，不制造可重发身份。
        let existing = {
            let mut s = store
                .c
                .prepare("SELECT source_id,command_id FROM commands WHERE state='in_flight'")
                .map_err(err)?;
            let rows = s
                .query_map([], |r| Ok((r.get::<_, String>(0)?, r.get::<_, String>(1)?)))
                .map_err(err)?;
            rows.collect::<std::result::Result<Vec<_>, _>>()
                .map_err(err)?
        };
        for (source, command) in existing {
            store.transition(&source, &command, "unknown", "recovered_in_flight", None)?;
        }
        store.audit.emit("process_start", json!({"result":"ok"}))?;
        let (tx, mut rx) = mpsc::channel::<Message>(16);
        let healthy = Arc::new(AtomicBool::new(true));
        let h = healthy.clone();
        let gates = Arc::new(Mutex::new(
            Vec::<Arc<crate::infrastructure::posix::Gate>>::new(),
        ));
        let error_gates = gates.clone();
        let join = thread::spawn(move || {
            while let Some(m) = rx.blocking_recv() {
                let result = (m.job)(&mut store);
                if result.as_ref().is_err_and(|e| {
                    matches!(
                        e.as_str(),
                        "state_io"
                            | "audit_persist"
                            | "audit_stdout"
                            | "audit_sync"
                            | "audit_rotate"
                    )
                }) {
                    h.store(false, Ordering::Release);
                    for gate in error_gates.lock().unwrap().iter() {
                        let _ = gate.close();
                    }
                }
                let _ = m.reply.send(result);
            }
            store.c.close().map_err(|_| "state_close")?;
            if store.finalized {
                store
                    .audit
                    .emit("resources_released", json!({"result":"normal"}))?;
                store
                    .audit
                    .emit("shutdown_complete", json!({"result":"normal"}))?;
            }
            store.audit.flush()?;
            Ok(())
        });
        Ok((
            Self {
                tx,
                healthy,
                lock,
                gates,
            },
            StateTask { join },
        ))
    }
    pub fn register_gates(&self, gates: Vec<Arc<crate::infrastructure::posix::Gate>>) {
        self.gates.lock().unwrap().extend(gates);
    }
    async fn call(&self, job: Job) -> Result<Value> {
        let (reply, rx) = oneshot::channel();
        tokio::time::timeout(Duration::from_millis(1000), async {
            self.tx
                .send(Message { job, reply })
                .await
                .map_err(|_| "state_closed")?;
            rx.await.map_err(|_| "state_closed")?
        })
        .await
        .map_err(|_| {
            self.healthy.store(false, Ordering::Release);
            for gate in self.gates.lock().unwrap().iter() {
                let _ = gate.close();
            }
            "state_deadline".to_string()
        })?
    }
    pub async fn log(&self, event: &str, c: Value) -> Result<()> {
        let event = event.to_owned();
        self.call(Box::new(move |s| {
            s.audit.emit(&event, c)?;
            Ok(Value::Null)
        }))
        .await
        .map(|_| ())
    }
    pub async fn admit(&self, i: Intent) -> Result<String> {
        if !self.healthy.load(Ordering::Acquire) {
            return Err("audit_unhealthy".into());
        }
        let v = self.call(Box::new(move |s| s.admit(&i))).await?;
        Ok(v.as_str().unwrap().into())
    }
    pub async fn dispatch(&self, i: Intent, request: String) -> Result<()> {
        if !self.healthy.load(Ordering::Acquire) {
            return Err("audit_unhealthy".into());
        }
        self.call(Box::new(move |s| {
            s.capacity(false)?;
            s.ensure_not_blocked(&i.target)?;
            s.transition(
                &i.source_id,
                &i.command_id,
                "in_flight",
                "dispatch_permit",
                Some(&request),
            )?;
            Ok(Value::Null)
        }))
        .await
        .map(|_| ())
    }
    pub async fn finish(&self, i: Intent, new: &str, reason: &str) -> Result<()> {
        let new = new.to_owned();
        let reason = reason.to_owned();
        self.call(Box::new(move |s| {
            s.transition(&i.source_id, &i.command_id, &new, &reason, None)?;
            Ok(Value::Null)
        }))
        .await
        .map(|_| ())
    }
    pub async fn finalize(&self) -> Result<()> {
        self.call(Box::new(|s| {
            s.finalized = true;
            Ok(Value::Null)
        }))
        .await
        .map(|_| ())
    }
    pub async fn command_status(&self, i: Intent) -> Result<String> {
        let value = self
            .call(Box::new(move |s| {
                s.c.query_row(
                    "SELECT state FROM commands WHERE source_id=?1 AND command_id=?2",
                    params![i.source_id, i.command_id],
                    |r| r.get::<_, String>(0),
                )
                .map(|v| json!(v))
                .map_err(err)
            }))
            .await?;
        Ok(value.as_str().ok_or("state_schema")?.into())
    }
    pub async fn snapshot(&self) -> Result<Value> {
        self.call(Box::new(|s|{let mut m=serde_json::Map::new();let mut st=s.c.prepare("SELECT state,count(*)FROM commands GROUP BY state").map_err(err)?;for r in st.query_map([],|r|Ok((r.get::<_,String>(0)?,r.get::<_,u64>(1)?))).map_err(err)?{let(k,n)=r.map_err(err)?;m.insert(k,json!(n));}Ok(json!({"commands":m,"log_writable":s.audit.writable,"capacity":s.capacity(false).is_ok()}))})).await
    }
    #[cfg(feature = "test-fixture")]
    pub async fn test_fault(&self, kind: &str) -> Result<()> {
        let kind = kind.to_owned();
        self.call(Box::new(move |s| {
            if kind == "t3" {
                s.fail_t3 = true;
            } else {
                s.audit.test_fail();
                s.audit.emit("test_fault", json!({}))?;
            }
            Ok(Value::Null)
        }))
        .await
        .map(|_| ())
    }
    #[cfg(feature = "test-fixture")]
    pub async fn test_limits(&self, commands: u64, events: u64, log: u64) -> Result<()> {
        self.call(Box::new(move |s| {
            s.command_limit = commands.min(10000);
            s.event_limit = events.min(90000);
            s.audit.test_limit(log);
            Ok(Value::Null)
        }))
        .await
        .map(|_| ())
    }
}
impl Store {
    fn capacity(&self, new: bool) -> Result<()> {
        let commands = self
            .c
            .query_row("SELECT count(*)FROM commands", [], |r| r.get::<_, u64>(0))
            .map_err(err)?;
        let events = self
            .c
            .query_row("SELECT count(*)FROM command_events", [], |r| {
                r.get::<_, u64>(0)
            })
            .map_err(err)?;
        let size = fs::metadata(self.dir.join("state.sqlite"))
            .map_err(|_| "state_stat")?
            .len();
        let journal = fs::metadata(self.dir.join("state.sqlite-journal"))
            .map(|m| m.len())
            .unwrap_or(0);
        if (new && commands >= self.command_limit)
            || events >= self.event_limit
            || size >= 48 * 1024 * 1024
            || size + journal >= 128 * 1024 * 1024
            || disk_available(&self.dir)? < 256 * 1024 * 1024
        {
            return Err("capacity_paused".into());
        }
        Ok(())
    }
    fn ensure_not_blocked(&self, target: &Resource) -> Result<()> {
        let mut s = self
            .c
            .prepare("SELECT target_key FROM commands WHERE state='unknown'")
            .map_err(err)?;
        for r in s.query_map([], |r| r.get::<_, String>(0)).map_err(err)? {
            let t: Resource = serde_json::from_str(&r.map_err(err)?).map_err(|_| "state_target")?;
            if t.overlaps(target) {
                return Err("target_unknown".into());
            }
        }
        Ok(())
    }
    fn admit(&mut self, i: &Intent) -> Result<Value> {
        let digest = hash(i);
        let existing: Option<(String, String)> = self
            .c
            .query_row(
                "SELECT payload_hash,state FROM commands WHERE source_id=?1 AND command_id=?2",
                params![i.source_id, i.command_id],
                |r| Ok((r.get(0)?, r.get(1)?)),
            )
            .optional()
            .map_err(err)?;
        if let Some((h, state)) = existing {
            if h != digest {
                self.audit.emit("identity_conflict",json!({"flow_id":i.flow_id,"command_id":i.command_id,"error_key":"identity_conflict"}))?;
                return Err("identity_conflict".into());
            }
            return Ok(json!(state));
        }
        self.capacity(true)?;
        self.ensure_not_blocked(&i.target)?;
        let state = if self.mode == "execute" {
            "pending"
        } else {
            "simulated"
        };
        let t = self.c.transaction().map_err(err)?;
        t.execute("INSERT INTO commands(source_id,command_id,flow_id,target_key,config_identity_hash,payload_hash,value_i16,issued_at_ms,expires_at_ms,state,dispatch_count,run_id)VALUES(?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,0,?11)",params![i.source_id,i.command_id,i.flow_id,serde_json::to_string(&i.target).unwrap(),i.config_identity_hash,digest,i.value,i.issued_at_ms,i.expires_at_ms,state,self.run_id]).map_err(err)?;
        t.execute("INSERT INTO command_events(source_id,command_id,run_id,from_state,to_state,reason_key,summary)VALUES(?1,?2,?3,NULL,?4,'intent',?5)",params![i.source_id,i.command_id,self.run_id,state,digest]).map_err(err)?;
        t.commit().map_err(err)?;
        self.audit.emit("intent",json!({"flow_id":i.flow_id,"command_id":i.command_id,"new":state,"state":state,"result":"durable"}))?;
        Ok(json!(state))
    }
    fn transition(
        &mut self,
        source: &str,
        command: &str,
        new: &str,
        reason: &str,
        request: Option<&str>,
    ) -> Result<()> {
        #[cfg(feature = "test-fixture")]
        if new == "confirmed" && self.fail_t3 {
            return Err("state_io".into());
        }
        let (old, dispatch): (String, u8) = self
            .c
            .query_row(
                "SELECT state,dispatch_count FROM commands WHERE source_id=?1 AND command_id=?2",
                params![source, command],
                |r| Ok((r.get(0)?, r.get(1)?)),
            )
            .map_err(err)?;
        let legal = match (old.as_str(), new) {
            ("pending", "in_flight") => dispatch == 0,
            ("pending", "expired" | "canceled") => true,
            ("in_flight", "confirmed" | "unknown" | "expired" | "canceled") => true,
            _ => false,
        };
        if !legal {
            return Err("state_transition".into());
        }
        let t = self.c.transaction().map_err(err)?;
        let changed=t.execute("UPDATE commands SET state=?1,dispatch_count=?2,request_id=COALESCE(?3,request_id),last_error_key=?4,ack_kind=?5,updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE source_id=?6 AND command_id=?7 AND state=?8",params![new,if new=="in_flight"{1}else{dispatch},request,if new=="unknown"{Some(reason)}else{None},if new=="confirmed"{Some("s7_protocol")}else{None},source,command,old]).map_err(err)?;
        if changed != 1 {
            return Err("state_cas".into());
        }
        t.execute("INSERT INTO command_events(source_id,command_id,run_id,request_id,from_state,to_state,reason_key,summary)VALUES(?1,?2,?3,?4,?5,?6,?7,'{}')",params![source,command,self.run_id,request,old,new,reason]).map_err(err)?;
        t.commit().map_err(err)?;
        self.audit.emit(if new=="confirmed"{"ack"}else{new},json!({"command_id":command,"request_id":request.unwrap_or(""),"old":old,"new":new,"state":new,"result":reason}))
    }
}
