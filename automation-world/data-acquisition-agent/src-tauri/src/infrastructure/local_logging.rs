//! 本模式独立有界JSON Lines：轮转仅限自有文件；记录状态/失败，避免每轮点值噪声。
use crate::domain::local_configuration::LocalResult;
use serde_json::json;
use std::{
    fs::{self, OpenOptions},
    io::Write,
    path::PathBuf,
    sync::{
        atomic::{AtomicBool, Ordering},
        Mutex,
    },
};
pub(crate) struct LocalLog {
    dir: PathBuf,
    lock: Mutex<()>,
    failed: AtomicBool,
}
impl LocalLog {
    pub fn new(dir: PathBuf) -> LocalResult<Self> {
        fs::create_dir_all(&dir).map_err(|_| "log_io")?;
        let _ = tracing_subscriber::fmt()
            .with_timer(ShanghaiTimer)
            .json()
            .with_target(false)
            .try_init();
        Ok(Self {
            dir,
            lock: Mutex::new(()),
            failed: AtomicBool::new(false),
        })
    }
    pub fn event(&self, event: &str, resource: &str, result: &str) -> LocalResult<()> {
        self.record(event, resource, result, None)
    }
    pub fn health(&self) -> LocalResult<()> {
        if self.failed.load(Ordering::SeqCst) {
            Err("log_io_unknown_interval".into())
        } else {
            Ok(())
        }
    }
    pub fn maintenance_failed(&self, error: &str) -> LocalResult<()> {
        self.record(
            "maintenance_failed",
            "storage_maintenance",
            if error == "capacity_paused" {
                "deferred"
            } else {
                "failed"
            },
            Some(error.split(':').next().unwrap_or("storage_error")),
        )
    }
    fn record(
        &self,
        event: &str,
        resource: &str,
        result: &str,
        error_code: Option<&str>,
    ) -> LocalResult<()> {
        let persisted = self.append(event, resource, result, error_code);
        match &persisted {
            Ok(()) if error_code.is_some() => {
                tracing::warn!(
                    event,
                    resource,
                    result,
                    error_code,
                    process = "daa-local",
                    persistence = "persisted"
                )
            }
            Ok(()) => tracing::info!(
                event,
                resource,
                result,
                error_code,
                process = "daa-local",
                persistence = "persisted"
            ),
            Err(_) => {
                self.failed.store(true, Ordering::SeqCst);
                tracing::error!(
                    event,
                    resource,
                    result,
                    error_code,
                    process = "daa-local",
                    persistence = "failed"
                );
                tracing::error!(
                    event = "local_log_failed",
                    process = "daa-local",
                    resource,
                    result = "unknown_interval",
                    error_code = "log_io"
                );
            }
        }
        persisted
    }
    fn append(
        &self,
        event: &str,
        resource: &str,
        result: &str,
        error_code: Option<&str>,
    ) -> LocalResult<()> {
        let _guard = self.lock.lock().map_err(|_| "log_io")?;
        let path = self.dir.join("runtime.jsonl");
        if fs::metadata(&path)
            .map(|m| m.len() > 4 * 1024 * 1024 - 4096)
            .unwrap_or(false)
        {
            let old = self.dir.join("runtime.7.jsonl");
            if old.exists() {
                fs::remove_file(old).map_err(|_| "log_io")?;
            }
            for n in (1..7).rev() {
                let from = self.dir.join(format!("runtime.{n}.jsonl"));
                if from.exists() {
                    fs::rename(from, self.dir.join(format!("runtime.{}.jsonl", n + 1)))
                        .map_err(|_| "log_io")?
                }
            }
            fs::rename(&path, self.dir.join("runtime.1.jsonl")).map_err(|_| "log_io")?;
        }
        let line=json!({"event":event,"process":"daa-local","resource":resource,"result":result,"error_code":error_code,"at":crate::domain::local_sample::now()}).to_string();
        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(path)
            .map_err(|_| "log_io")?;
        writeln!(file, "{line}").map_err(|_| "log_io")?;
        file.flush().map_err(|_| "log_io")?;
        Ok(())
    }
}

/// stdout保留纳秒诊断精度；文件at沿用业务毫秒helper。
pub(crate) struct ShanghaiTimer;
impl tracing_subscriber::fmt::time::FormatTime for ShanghaiTimer {
    fn format_time(&self, w: &mut tracing_subscriber::fmt::format::Writer<'_>) -> std::fmt::Result {
        write!(w, "{}", crate::domain::business_time::diagnostic_now())
    }
}
