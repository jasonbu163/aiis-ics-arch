//! 文件：src/infrastructure/audit.rs；tracing JSONL格式化及有失败回执的同步持久审计。
use crate::Result;
use serde_json::Value;
use std::{
    fs::{File, OpenOptions},
    io::{self, Write},
    path::{Path, PathBuf},
    sync::{Arc, Mutex},
    time::{Duration, Instant},
};
#[derive(Clone)]
struct Buffer(Arc<Mutex<Vec<u8>>>);
impl Write for Buffer {
    fn write(&mut self, b: &[u8]) -> io::Result<usize> {
        self.0.lock().unwrap().extend_from_slice(b);
        Ok(b.len())
    }
    fn flush(&mut self) -> io::Result<()> {
        Ok(())
    }
}
impl<'a> tracing_subscriber::fmt::MakeWriter<'a> for Buffer {
    type Writer = Self;
    fn make_writer(&'a self) -> Self {
        self.clone()
    }
}
pub struct Audit {
    file: File,
    path: PathBuf,
    run_id: String,
    instance_id: String,
    pub writable: bool,
    limit: u64,
    #[cfg(feature = "test-fixture")]
    fail: bool,
}
impl Audit {
    pub fn open(dir: &Path, run_id: &str, instance_id: &str) -> Result<Self> {
        let path = dir.join("runtime.jsonl");
        let file = OpenOptions::new()
            .append(true)
            .create(true)
            .open(&path)
            .map_err(|_| "audit_open")?;
        unsafe {
            let f = libc::fcntl(1, libc::F_GETFL);
            if f < 0 || libc::fcntl(1, libc::F_SETFL, f | libc::O_NONBLOCK) < 0 {
                return Err("audit_stdout".into());
            }
        }
        Ok(Self {
            file,
            path,
            run_id: run_id.into(),
            instance_id: instance_id.into(),
            writable: true,
            limit: 5 * 1024 * 1024,
            #[cfg(feature = "test-fixture")]
            fail: false,
        })
    }
    #[cfg(feature = "test-fixture")]
    pub fn test_limit(&mut self, n: u64) {
        self.limit = n.min(5 * 1024 * 1024)
    }
    #[cfg(feature = "test-fixture")]
    pub fn test_fail(&mut self) {
        self.fail = true;
    }
    pub fn emit(&mut self, event: &str, context: Value) -> Result<()> {
        #[cfg(feature = "test-fixture")]
        if self.fail {
            self.writable = false;
            return Err("audit_persist".into());
        }
        let r = self.write(event, context);
        if r.is_err() {
            self.writable = false;
        }
        r
    }
    fn write(&mut self, event: &str, c: Value) -> Result<()> {
        let buffer = Buffer(Arc::new(Mutex::new(Vec::new())));
        let subscriber = tracing_subscriber::fmt()
            .json()
            .flatten_event(true)
            .with_ansi(false)
            .with_current_span(false)
            .with_span_list(false)
            .with_writer(buffer.clone())
            .finish();
        let s = |k| c.get(k).and_then(Value::as_str).unwrap_or("");
        tracing::subscriber::with_default(
            subscriber,
            || tracing::info!(event=event,implementation="rust",run_id=self.run_id,instance_id=self.instance_id,flow_id=s("flow_id"),target_id=s("target_id"),command_id=s("command_id"),request_id=s("request_id"),state=s("state"),old=s("old"),new=s("new"),result=s("result"),duration_ms=c.get("duration_ms").and_then(|v| v.as_u64()).unwrap_or(0),error_key=s("error_key"),context=%c),
        );
        let line = buffer.0.lock().unwrap().clone();
        if line.len() > 4096 || line.len() as u64 > self.limit {
            return Err("audit_line_size".into());
        }
        if self.file.metadata().map_err(|_| "audit_stat")?.len() + line.len() as u64 > self.limit {
            self.file.sync_all().map_err(|_| "audit_sync")?;
            let backup = |n| self.path.with_extension(format!("jsonl.{n}"));
            if backup(4).exists() {
                std::fs::remove_file(backup(4)).map_err(|_| "audit_rotate")?;
            }
            for n in (1..4).rev() {
                if backup(n).exists() {
                    std::fs::rename(backup(n), backup(n + 1)).map_err(|_| "audit_rotate")?;
                }
            }
            std::fs::rename(&self.path, backup(1)).map_err(|_| "audit_rotate")?;
            self.file = OpenOptions::new()
                .append(true)
                .create_new(true)
                .open(&self.path)
                .map_err(|_| "audit_rotate")?;
        }
        self.file
            .write_all(&line)
            .and_then(|_| self.file.flush())
            .and_then(|_| self.file.sync_data())
            .map_err(|_| "audit_persist")?;
        let deadline = Instant::now() + Duration::from_millis(100);
        let mut offset = 0;
        while offset < line.len() {
            let n = unsafe { libc::write(1, line[offset..].as_ptr().cast(), line.len() - offset) };
            if n > 0 {
                offset += n as usize;
            } else {
                if Instant::now() >= deadline {
                    return Err("audit_stdout".into());
                }
                let e = io::Error::last_os_error();
                if !matches!(
                    e.kind(),
                    io::ErrorKind::WouldBlock | io::ErrorKind::Interrupted
                ) {
                    return Err("audit_stdout".into());
                }
                std::thread::sleep(Duration::from_millis(1));
            }
        }
        Ok(())
    }
    pub fn flush(&mut self) -> Result<()> {
        self.file
            .flush()
            .and_then(|_| self.file.sync_all())
            .map_err(|_| "audit_sync".into())
    }
}
