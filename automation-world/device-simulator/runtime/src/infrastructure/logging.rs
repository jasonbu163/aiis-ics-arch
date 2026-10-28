//! DS运行时职责：Bounded in-memory evidence handoff. JSON encoding and sinks run outside owner locks.
use super::clock;
use serde_json::{json, Value};
use std::collections::VecDeque;
use std::sync::{Arc, Mutex};
// 一次Evidence drain最多4096条；文件worker可容纳两批，另受16MiB字节门约束。
const FILE_QUEUE_LINES: usize = 8192;
fn stamp_calendar_time(event: &mut Value) {
    if event.get("timestamp").is_none() {
        if let Some(timestamp) = clock::calendar_timestamp() {
            event["timestamp"] = json!(timestamp);
            event["time_zone"] = json!(clock::BUSINESS_TIME_ZONE);
        }
    }
}
#[derive(Clone, Default)]
pub struct Evidence(Arc<Mutex<Buffer>>, Arc<SinkHealth>);
#[derive(Default)]
struct SinkHealth {
    file_errors: std::sync::atomic::AtomicU64,
    file_dropped_bytes: std::sync::atomic::AtomicU64,
    stdout_errors: std::sync::atomic::AtomicU64,
    stdout_dropped_bytes: std::sync::atomic::AtomicU64,
    rotations: std::sync::atomic::AtomicU64,
    queued_bytes: std::sync::atomic::AtomicU64,
    queue_peak: std::sync::atomic::AtomicU64,
    queue_dropped: std::sync::atomic::AtomicU64,
    serialization_peak: std::sync::atomic::AtomicU64,
    parsed_event_peak: std::sync::atomic::AtomicU64,
    drain_peak: std::sync::atomic::AtomicU64,
    pending_peak: std::sync::atomic::AtomicU64,
    history_peak: std::sync::atomic::AtomicU64,
    event_peak: std::sync::atomic::AtomicU64,
}
fn value_bytes(value: &Value) -> usize {
    std::mem::size_of::<Value>()
        + match value {
            Value::String(s) => s.capacity(),
            Value::Array(a) => {
                a.capacity() * std::mem::size_of::<Value>()
                    + a.iter().map(value_bytes).sum::<usize>()
            }
            Value::Object(o) => o
                .iter()
                .map(|(k, v)| k.capacity() + 96 + value_bytes(v))
                .sum(),
            _ => 0,
        }
}
#[derive(Default)]
struct Buffer {
    pending: VecDeque<Value>,
    history: VecDeque<Value>,
    lost: u64,
    pending_lost: u64,
    pending_bytes: usize,
    history_bytes: usize,
}
impl Evidence {
    pub fn put(&self, mut v: Value) {
        stamp_calendar_time(&mut v);
        let mut g = self.0.lock().unwrap_or_else(|e| e.into_inner());
        let bytes = value_bytes(&v) + 256;
        self.1.event_peak.fetch_max(bytes as u64, Ordering::Relaxed);
        if bytes > 256 * 1024
            || g.pending.len() >= 4096
            || g.pending_bytes + bytes > 8 * 1024 * 1024
        {
            g.lost += 1;
            g.pending_lost += 1;
            return;
        }
        v["clock_id"] = json!(clock::CLOCK_ID);
        v["monotonic_ns"] = json!(clock::ns());
        while !g.history.is_empty()
            && (g.history.len() >= 4096 || g.history_bytes + bytes > 8 * 1024 * 1024)
        {
            let old = g.history.pop_front().unwrap();
            g.history_bytes = g.history_bytes.saturating_sub(value_bytes(&old));
        }
        g.history_bytes += value_bytes(&v);
        g.pending_bytes += bytes;
        self.1
            .pending_peak
            .fetch_max(g.pending_bytes as u64, Ordering::Relaxed);
        self.1
            .history_peak
            .fetch_max(g.history_bytes as u64, Ordering::Relaxed);
        g.history.push_back(v.clone());
        g.pending.push_back(v)
    }
    pub fn query(&self, offset: usize, limit: usize, event: Option<&str>) -> Value {
        let g = self.0.lock().unwrap_or_else(|e| e.into_inner());
        let rows = g
            .history
            .iter()
            .rev()
            .filter(|v| event.is_none_or(|e| v["event"].as_str() == Some(e)))
            .skip(offset.min(4096))
            .take(limit.min(100))
            .cloned()
            .collect::<Vec<_>>();
        json!({"rows":rows,"retained":g.history.len(),"lost":g.lost.to_string(),"observabilityDegraded":g.lost>0 || self.1.file_errors.load(Ordering::Relaxed)>0 || self.1.stdout_errors.load(Ordering::Relaxed)>0 || self.1.queue_dropped.load(Ordering::Relaxed)>0,"fileWriteErrors":self.1.file_errors.load(Ordering::Relaxed).to_string(),"fileDroppedBytes":self.1.file_dropped_bytes.load(Ordering::Relaxed).to_string(),"stdoutWriteErrors":self.1.stdout_errors.load(Ordering::Relaxed).to_string(),"stdoutDroppedBytes":self.1.stdout_dropped_bytes.load(Ordering::Relaxed).to_string(),"fileRotations":self.1.rotations.load(Ordering::Relaxed).to_string(),"pendingBytesUpper":g.pending_bytes,"historyBytesUpper":g.history_bytes,"fileQueueDroppedLines":self.1.queue_dropped.load(Ordering::Relaxed).to_string(),"peaks":{"eventHeapUpper":self.1.event_peak.load(Ordering::Relaxed),"pendingHeapUpper":self.1.pending_peak.load(Ordering::Relaxed),"historyHeapUpper":self.1.history_peak.load(Ordering::Relaxed),"drainHeapUpper":self.1.drain_peak.load(Ordering::Relaxed),"fileQueueActualBytes":self.1.queue_peak.load(Ordering::Relaxed),"serializedVecCapacity":self.1.serialization_peak.load(Ordering::Relaxed),"parsedSinkValueHeapUpper":self.1.parsed_event_peak.load(Ordering::Relaxed)}})
    }
    pub fn take(&self) -> Vec<Value> {
        let mut g = self.0.lock().unwrap_or_else(|e| e.into_inner());
        self.1
            .drain_peak
            .fetch_max(g.pending_bytes as u64, Ordering::Relaxed);
        let mut v = g.pending.drain(..).collect::<Vec<_>>();
        g.pending_bytes = 0;
        if g.pending_lost > 0 {
            v.push(json!({"event":"evidence_lost","count":g.pending_lost,"total":g.lost}));
            g.pending_lost = 0
        }
        v
    }
}
use std::{
    io::Write,
    path::Path,
    sync::atomic::{AtomicBool, Ordering},
    thread::{self, JoinHandle},
    time::Duration,
};
use tracing_subscriber::{prelude::*, Layer};
#[derive(Default)]
struct StdoutLoss {
    dropped_lines: u64,
    dropped_bytes: u64,
    partial_writes: u64,
    write_errors: u64,
}
fn stdout_write(fd: libc::c_int, line: &[u8], loss: &mut StdoutLoss) -> Option<Value> {
    // 单次非阻塞syscall：不重试、不让owner或退出等待观察端读取。
    let n = unsafe { libc::write(fd, line.as_ptr().cast(), line.len()) };
    if n == line.len() as isize {
        return None;
    }
    let error = if n < 0 {
        std::io::Error::last_os_error().raw_os_error()
    } else {
        None
    };
    let written = n.max(0) as usize;
    loss.dropped_lines += 1;
    loss.dropped_bytes += (line.len() - written) as u64;
    loss.partial_writes += u64::from(n >= 0);
    loss.write_errors += u64::from(n < 0);
    Some(json!({"event":"observability_degraded","sink":"stdout",
        "attempted_bytes":line.len(),"written_bytes":written,"errno":error,
        "dropped_lines":loss.dropped_lines,"dropped_bytes":loss.dropped_bytes,
        "partial_writes":loss.partial_writes,"write_errors":loss.write_errors}))
}
struct Sink {
    stdout_fd: libc::c_int,
    stdout_loss: Mutex<StdoutLoss>,
    writer: Mutex<tracing_appender::non_blocking::NonBlocking>,
    run: String,
    health: Arc<SinkHealth>,
}
impl Sink {
    fn file_line(&self, writer: &mut tracing_appender::non_blocking::NonBlocking, line: &[u8]) {
        let size = line.len() as u64;
        if size > 256 * 1024
            || self
                .health
                .queued_bytes
                .fetch_update(Ordering::SeqCst, Ordering::SeqCst, |old| {
                    old.checked_add(size).filter(|n| *n <= 16 * 1024 * 1024)
                })
                .is_err()
        {
            self.health.queue_dropped.fetch_add(1, Ordering::Relaxed);
            return;
        }
        self.health.queue_peak.fetch_max(
            self.health.queued_bytes.load(Ordering::SeqCst),
            Ordering::Relaxed,
        );
        let before = writer.error_counter().dropped_lines();
        if writer.write_all(line).is_err() || writer.error_counter().dropped_lines() > before {
            let _ =
                self.health
                    .queued_bytes
                    .fetch_update(Ordering::SeqCst, Ordering::SeqCst, |old| {
                        Some(old.saturating_sub(size))
                    });
            self.health.queue_dropped.fetch_add(1, Ordering::Relaxed);
        }
    }
}
struct JsonVisitor(Value);
impl tracing::field::Visit for JsonVisitor {
    fn record_debug(&mut self, f: &tracing::field::Field, v: &dyn std::fmt::Debug) {
        if f.name() == "json" {
            let s = format!("{v:?}");
            if let Ok(v) = serde_json::from_str(&s) {
                self.0 = v
            }
        }
    }
    fn record_str(&mut self, f: &tracing::field::Field, v: &str) {
        if f.name() == "json" {
            if let Ok(v) = serde_json::from_str(v) {
                self.0 = v
            }
        }
    }
}
impl<S: tracing::Subscriber> Layer<S> for Sink {
    fn on_event(&self, event: &tracing::Event<'_>, _: tracing_subscriber::layer::Context<'_, S>) {
        let mut v = JsonVisitor(json!({}));
        event.record(&mut v);
        stamp_calendar_time(&mut v.0);
        self.health
            .parsed_event_peak
            .fetch_max(value_bytes(&v.0) as u64, Ordering::Relaxed);
        v.0["run_id"] = json!(self.run);
        v.0["pid"] = json!(std::process::id());
        v.0["level"] = json!(event.metadata().level().as_str());
        v.0["service"] = json!("device-simulator");
        if v.0.get("monotonic_ns").is_none() {
            v.0["monotonic_ns"] = json!(clock::ns());
            v.0["clock_id"] = json!(clock::CLOCK_ID)
        }
        if let Ok(mut line) = serde_json::to_vec(&v.0) {
            line.push(b'\n');
            self.health
                .serialization_peak
                .fetch_max(line.capacity() as u64, Ordering::Relaxed);
            let degraded =
                stdout_write(self.stdout_fd, &line, &mut self.stdout_loss.lock().unwrap());
            let mut writer = self.writer.lock().unwrap();
            self.file_line(&mut writer, &line);
            if let Some(mut report) = degraded {
                self.health.stdout_errors.store(
                    report["dropped_lines"].as_u64().unwrap_or(0),
                    Ordering::Relaxed,
                );
                self.health.stdout_dropped_bytes.store(
                    report["dropped_bytes"].as_u64().unwrap_or(0),
                    Ordering::Relaxed,
                );
                // 独立file通道记录真实失败/部分写结果；不递归写已降级stdout。
                report["run_id"] = json!(self.run);
                report["pid"] = json!(std::process::id());
                report["service"] = json!("device-simulator");
                report["clock_id"] = json!(clock::CLOCK_ID);
                report["monotonic_ns"] = json!(clock::ns());
                stamp_calendar_time(&mut report);
                if let Ok(mut bytes) = serde_json::to_vec(&report) {
                    bytes.push(b'\n');
                    self.file_line(&mut writer, &bytes);
                }
            }
        }
    }
}
// 文件I/O仅在独立appender worker；四个8MiB文件有界，真实写/轮转失败计数后降级。
struct RollingFile {
    root: std::path::PathBuf,
    file: std::fs::File,
    bytes: u64,
    limit: u64,
    health: Arc<SinkHealth>,
}
impl RollingFile {
    fn open(root: &Path, health: Arc<SinkHealth>, limit: u64) -> std::io::Result<Self> {
        let file = std::fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(root.join("events.jsonl"))?;
        let bytes = file.metadata()?.len();
        Ok(Self {
            root: root.into(),
            file,
            bytes,
            limit,
            health,
        })
    }
    fn rotate(&mut self) -> std::io::Result<()> {
        self.file.flush()?;
        let oldest = self.root.join("events.3.jsonl");
        if oldest.exists() {
            std::fs::remove_file(oldest)?;
        }
        for index in (1..3).rev() {
            let old = self.root.join(format!("events.{index}.jsonl"));
            if old.exists() {
                std::fs::rename(old, self.root.join(format!("events.{}.jsonl", index + 1)))?;
            }
        }
        std::fs::rename(
            self.root.join("events.jsonl"),
            self.root.join("events.1.jsonl"),
        )?;
        self.file = std::fs::OpenOptions::new()
            .create_new(true)
            .write(true)
            .open(self.root.join("events.jsonl"))?;
        self.bytes = 0;
        self.health.rotations.fetch_add(1, Ordering::Relaxed);
        Ok(())
    }
    fn lost(&self, bytes: usize) {
        self.health.file_errors.fetch_add(1, Ordering::Relaxed);
        self.health
            .file_dropped_bytes
            .fetch_add(bytes as u64, Ordering::Relaxed);
    }
}
impl Write for RollingFile {
    fn write(&mut self, bytes: &[u8]) -> std::io::Result<usize> {
        let result = (|| {
            if bytes.len() > 256 * 1024
                || self.bytes + bytes.len() as u64 > self.limit && self.rotate().is_err()
            {
                self.lost(bytes.len());
                return Ok(bytes.len());
            }
            match self.file.write(bytes) {
                Ok(n) => {
                    self.bytes += n as u64;
                    if n < bytes.len() {
                        self.lost(bytes.len() - n)
                    }
                    Ok(bytes.len())
                }
                Err(_) => {
                    self.lost(bytes.len());
                    Ok(bytes.len())
                }
            }
        })();
        let _ = self
            .health
            .queued_bytes
            .fetch_update(Ordering::SeqCst, Ordering::SeqCst, |old| {
                Some(old.saturating_sub(bytes.len() as u64))
            });
        result
    }

    fn flush(&mut self) -> std::io::Result<()> {
        if self.file.flush().is_err() {
            self.lost(0)
        }
        Ok(())
    }
}
pub struct LogThread {
    finish: Arc<AtomicBool>,
    handle: Option<JoinHandle<()>>,
    _guard: tracing_appender::non_blocking::WorkerGuard,
}
impl LogThread {
    pub fn stop(mut self) {
        self.finish.store(true, Ordering::SeqCst);
        if let Some(h) = self.handle.take() {
            let _ = h.join();
        }
    }
}
pub fn start_sink(events: Evidence, root: &Path) -> Result<LogThread, String> {
    // Own stdout must not make shutdown wait for a non-draining observer.
    unsafe {
        let flags = libc::fcntl(libc::STDOUT_FILENO, libc::F_GETFL);
        if flags < 0
            || libc::fcntl(libc::STDOUT_FILENO, libc::F_SETFL, flags | libc::O_NONBLOCK) < 0
        {
            return Err(std::io::Error::last_os_error().to_string());
        }
    }
    let f =
        RollingFile::open(root, events.1.clone(), 8 * 1024 * 1024).map_err(|e| e.to_string())?;
    let (writer, guard) = tracing_appender::non_blocking::NonBlockingBuilder::default()
        .buffered_lines_limit(FILE_QUEUE_LINES)
        .lossy(true)
        .finish(f);
    let errors = writer.error_counter();
    let subscriber = tracing_subscriber::registry().with(Sink {
        stdout_fd: libc::STDOUT_FILENO,
        stdout_loss: Mutex::new(StdoutLoss::default()),
        writer: Mutex::new(writer),
        health: events.1.clone(),
        run: root
            .file_name()
            .unwrap_or_default()
            .to_string_lossy()
            .into_owned(),
    });
    tracing::subscriber::set_global_default(subscriber).map_err(|e| e.to_string())?;
    let finish = Arc::new(AtomicBool::new(false));
    let flag = finish.clone();
    let h = thread::spawn(move || {
        let mut next = 0;
        let mut lost = 0;
        loop {
            if clock::ns() >= next {
                events.put(super::resource_sample::sample());
                let errors = events.1.file_errors.load(Ordering::Relaxed);
                if errors > 0 {
                    events.put(json!({"event":"observability_degraded","sink":"file","write_errors":errors,"dropped_bytes":events.1.file_dropped_bytes.load(Ordering::Relaxed)}));
                }
                next = clock::ns() + 1_000_000_000
            }
            for value in events.take() {
                let s = value.to_string();
                tracing::info!(json = s.as_str());
            }
            let e = errors.dropped_lines();
            if e != lost {
                lost = e;
                tracing::warn!(
                    json = json!({"event":"observability_degraded","dropped":lost})
                        .to_string()
                        .as_str()
                );
            }
            if flag.load(Ordering::SeqCst) {
                // stop可能恰好发生在本轮take之后；真实join前最后排空已入环事件。
                // producer在shutdown中已结束，不把最终退出证据遗留在无人消费的环里。
                for value in events.take() {
                    let s = value.to_string();
                    tracing::info!(json = s.as_str());
                }
                break;
            }
            thread::sleep(Duration::from_millis(5));
        }
    });
    Ok(LogThread {
        finish,
        handle: Some(h),
        _guard: guard,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    #[cfg(feature = "test-automation")]
    fn maximum_protocol_snapshot_preserves_complete_heap_and_both_sink_lines() {
        use crate::{
            app::App,
            domain::configuration::{uuid, Workspace},
            infrastructure::native_ffi::Descriptor,
            services::lifecycle::Connection,
            testing::hooks,
        };
        use std::os::fd::AsRawFd;
        let root = std::path::PathBuf::from(
            std::env::var_os("DS_TEST_RUN_ROOT").expect("owned test root"),
        )
        .join(format!("maximum-snapshot-{}", uuid()));
        std::fs::create_dir_all(&root).unwrap();
        let app = App::open(&root).unwrap();
        let w: Workspace = serde_json::from_str(include_str!(
            "../../../tests/fixtures/protocol-workspace.json"
        ))
        .unwrap();
        hooks::prepare_workspace(&app, w.clone()).unwrap();
        let instance = app.instance(&w.instances[0].id).unwrap();
        let context = &instance.context;
        {
            let mut t = context.transport.lock().unwrap();
            for index in 0..20u64 {
                t.connections.insert(
                    u64::MAX - index,
                    Connection {
                        fd: -1,
                        peer_port: 65535,
                        established: index < 16,
                        closing: false,
                        inflight: true,
                        reason: i32::MAX,
                        pdu: u64::MAX,
                        epoch: u64::MAX,
                        revision: u64::MAX,
                        accepted: u64::MAX,
                        established_at: u64::MAX,
                        last_recv: u64::MAX,
                        last_send: u64::MAX,
                        admitted: u64::MAX,
                        count: 4,
                        refs: 1,
                        desc: [Descriptor::default(); 4],
                    },
                );
            }
        }
        let mut value = context.owner.test_snapshot();
        for (k, v) in context.snapshot().as_object().unwrap() {
            value[k] = v.clone()
        }
        context.transport.lock().unwrap().connections.clear(); // synthetic metadata only; no socket/native worker existed
        for field in ["epoch", "revision", "seq", "tick", "next_tick_ns"] {
            value[field] = json!(u64::MAX)
        }
        for point in value["points"].as_array_mut().unwrap() {
            point["last_seq"] = json!(u64::MAX);
            point["updated_at"] = json!(u64::MAX)
        }
        for db in value["dbs"].as_object_mut().unwrap().values_mut() {
            for point in db["points"].as_array_mut().unwrap() {
                point["last_seq"] = json!(u64::MAX);
                point["updated_at"] = json!(u64::MAX)
            }
        }
        value["event"] = json!("control_result");
        value["command"] = json!("snapshot");
        value["ticket"] = json!(u64::MAX);
        value["request_id"] = json!(u64::MAX);
        value["ok"] = json!(true);
        assert_eq!(value["points"].as_array().unwrap().len(), 63);
        assert_eq!(value["connections"].as_array().unwrap().len(), 20);
        assert_eq!(value["c"], 16);
        assert_eq!(value["h"], 4);
        let events = Evidence::default();
        events.put(value.clone());
        let heap = events.query(0, 0, None)["peaks"]["eventHeapUpper"]
            .as_u64()
            .unwrap();
        assert!(heap <= 256 * 1024 && heap > 128 * 1024);
        let stdout = std::fs::File::create(root.join("probe-stdout.jsonl")).unwrap();
        let rolling = RollingFile::open(&root, events.1.clone(), 8 * 1024 * 1024).unwrap();
        let (writer, guard) = tracing_appender::non_blocking::NonBlockingBuilder::default()
            .buffered_lines_limit(FILE_QUEUE_LINES)
            .lossy(true)
            .finish(rolling);
        let subscriber = tracing_subscriber::registry().with(Sink {
            stdout_fd: stdout.as_raw_fd(),
            stdout_loss: Mutex::new(StdoutLoss::default()),
            writer: Mutex::new(writer),
            run: "maximum-snapshot-probe".into(),
            health: events.1.clone(),
        });
        let mut drain_string_capacity = 0;
        tracing::subscriber::with_default(subscriber, || {
            for event in events.take() {
                let s = event.to_string();
                drain_string_capacity = s.capacity();
                tracing::info!(json = s.as_str())
            }
        });
        drop(guard);
        drop(stdout);
        let stdout_bytes = std::fs::read(root.join("probe-stdout.jsonl")).unwrap();
        let file_bytes = std::fs::read(root.join("events.jsonl")).unwrap();
        assert_eq!(stdout_bytes, file_bytes);
        let saved: Value = serde_json::from_slice(&file_bytes).unwrap();
        assert_eq!(saved["points"], value["points"]);
        assert_eq!(saved["dbs"], value["dbs"]);
        assert_eq!(saved["connections"], value["connections"]);
        assert_eq!(saved["image"].as_str().unwrap().len(), 2048);
        assert_eq!(saved["marker"].as_str().unwrap().len(), 128);
        assert_eq!(events.query(0, 0, None)["observabilityDegraded"], false);
        let metrics = json!({"event":"maximum_snapshot_probe","root":root,"method":"actual product owner+Context snapshot and normal Evidence/Sink/RollingFile paths; synthetic C16/H4 metadata without sockets/listeners","points":63,"dbs":2,"connections":20,"c":16,"h":4,"longIdentifiersAndCounters":"valid UUID36, u64MAX20 digits, max port/reason, full actual DB bytes","eventHeapUpper":heap,"serializedLineBytes":file_bytes.len(),"drainStringCapacity":drain_string_capacity,"log":events.query(0,0,None),"fileQueueLineLimit":FILE_QUEUE_LINES,"conservativeLogTotal":46*1024*1024+256*1024});
        std::fs::write(
            root.join("metrics.json"),
            serde_json::to_vec_pretty(&metrics).unwrap(),
        )
        .unwrap();
        println!("{}", metrics);
        assert!(app.shutdown());
    }

    #[test]
    fn file_queue_count_budget_is_bounded_and_saturation_is_observable() {
        struct HeldWriter {
            release: Arc<AtomicBool>,
            entered: Arc<AtomicBool>,
            writes: Arc<std::sync::atomic::AtomicU64>,
            health: Arc<SinkHealth>,
        }
        impl Write for HeldWriter {
            fn write(&mut self, line: &[u8]) -> std::io::Result<usize> {
                self.entered.store(true, Ordering::SeqCst);
                let deadline = std::time::Instant::now() + Duration::from_secs(3);
                while !self.release.load(Ordering::SeqCst) {
                    assert!(
                        std::time::Instant::now() < deadline,
                        "probe release deadline"
                    );
                    thread::sleep(Duration::from_millis(1));
                }
                self.writes.fetch_add(1, Ordering::SeqCst);
                self.health
                    .queued_bytes
                    .fetch_sub(line.len() as u64, Ordering::SeqCst);
                Ok(line.len())
            }
            fn flush(&mut self) -> std::io::Result<()> {
                Ok(())
            }
        }
        let health = Arc::new(SinkHealth::default());
        let release = Arc::new(AtomicBool::new(false));
        let entered = Arc::new(AtomicBool::new(false));
        let writes = Arc::new(std::sync::atomic::AtomicU64::new(0));
        let (writer, guard) = tracing_appender::non_blocking::NonBlockingBuilder::default()
            .buffered_lines_limit(FILE_QUEUE_LINES)
            .lossy(true)
            .finish(HeldWriter {
                release: release.clone(),
                entered: entered.clone(),
                writes: writes.clone(),
                health: health.clone(),
            });
        let sink = Sink {
            stdout_fd: -1,
            stdout_loss: Mutex::new(StdoutLoss::default()),
            writer: Mutex::new(writer),
            run: "bounded-file-queue-probe".into(),
            health: health.clone(),
        };
        let mut writer = sink.writer.lock().unwrap();
        sink.file_line(&mut writer, b"{}\n");
        let deadline = std::time::Instant::now() + Duration::from_secs(1);
        while !entered.load(Ordering::SeqCst) {
            assert!(std::time::Instant::now() < deadline, "worker did not start");
            thread::sleep(Duration::from_millis(1));
        }
        // 真正占住worker后精确填满channel；不是估算“可能满了”。
        for _ in 0..FILE_QUEUE_LINES {
            sink.file_line(&mut writer, b"{}\n");
        }
        assert_eq!(writer.error_counter().dropped_lines(), 0);
        sink.file_line(&mut writer, b"{}\n");
        assert_eq!(writer.error_counter().dropped_lines(), 1);
        assert_eq!(health.queue_dropped.load(Ordering::SeqCst), 1);
        assert_eq!(
            health.queued_bytes.load(Ordering::SeqCst),
            3 * (FILE_QUEUE_LINES as u64 + 1)
        );
        release.store(true, Ordering::SeqCst);
        drop(writer);
        let deadline = std::time::Instant::now() + Duration::from_secs(2);
        while health.queued_bytes.load(Ordering::SeqCst) != 0 {
            assert!(std::time::Instant::now() < deadline, "worker did not drain");
            thread::sleep(Duration::from_millis(1));
        }
        drop(guard);
        assert_eq!(writes.load(Ordering::SeqCst), FILE_QUEUE_LINES as u64 + 1);
        println!(
            "{}",
            json!({"event":"file_queue_count_probe","lineLimit":FILE_QUEUE_LINES,"heldWorker":true,"acceptedIncludingActive":writes.load(Ordering::SeqCst),"actualDroppedLines":health.queue_dropped.load(Ordering::SeqCst),"queuedBytesAfter":health.queued_bytes.load(Ordering::SeqCst),"peakQueuedBytes":health.queue_peak.load(Ordering::SeqCst),"channelMetadataReservationBytes":2*1024*1024,"method":"real lossy appender channel at its count limit, one active blocked test writer, normal Sink::file_line reservation/rollback; worker released and genuinely drained"})
        );
    }

    #[test]
    #[cfg(feature = "test-automation")]
    fn real_file_sink_accepts_one_full_drain_burst_and_sustained_offered_rate() {
        use std::os::fd::AsRawFd;
        let root = std::path::PathBuf::from(
            std::env::var_os("DS_TEST_RUN_ROOT").expect("owned test root"),
        )
        .join(format!(
            "file-burst-{}",
            crate::domain::configuration::uuid()
        ));
        std::fs::create_dir_all(&root).unwrap();
        let health = Arc::new(SinkHealth::default());
        let stdout = std::fs::File::create(root.join("stdout.jsonl")).unwrap();
        let file = RollingFile::open(&root, health.clone(), 8 * 1024 * 1024).unwrap();
        let (writer, guard) = tracing_appender::non_blocking::NonBlockingBuilder::default()
            .buffered_lines_limit(FILE_QUEUE_LINES)
            .lossy(true)
            .finish(file);
        let errors = writer.error_counter();
        let subscriber = tracing_subscriber::registry().with(Sink {
            stdout_fd: stdout.as_raw_fd(),
            stdout_loss: Mutex::new(StdoutLoss::default()),
            writer: Mutex::new(writer),
            run: "file-burst-probe".into(),
            health: health.clone(),
        });
        let began = std::time::Instant::now();
        tracing::subscriber::with_default(subscriber, || {
            for index in 0..4096 {
                tracing::info!(
                    json = json!({"event":"real_sink_burst","index":index,"text":"x".repeat(128)})
                        .to_string()
                        .as_str()
                );
            }
            let start = std::time::Instant::now();
            for index in 0..2048 {
                let due = start + Duration::from_millis(index);
                if let Some(wait) = due.checked_duration_since(std::time::Instant::now()) {
                    thread::sleep(wait);
                }
                tracing::info!(
                    json =
                        json!({"event":"real_sink_sustained","index":index,"text":"x".repeat(128)})
                            .to_string()
                            .as_str()
                );
            }
        });
        drop(guard);
        drop(stdout);
        let a = std::fs::read(root.join("stdout.jsonl")).unwrap();
        let b = std::fs::read(root.join("events.jsonl")).unwrap();
        assert_eq!(a, b);
        assert_eq!(a.iter().filter(|c| **c == b'\n').count(), 6144);
        assert_eq!(errors.dropped_lines(), 0);
        assert_eq!(health.queue_dropped.load(Ordering::SeqCst), 0);
        assert_eq!(health.file_errors.load(Ordering::SeqCst), 0);
        assert_eq!(health.queued_bytes.load(Ordering::SeqCst), 0);
        let result = json!({"event":"file_burst_rate_probe","root":root,"burstOffered":4096,"sustainedOffered":2048,"sustainedRatePerSecond":1000,"completedBothSinks":6144,"bytesEachSink":a.len(),"droppedLines":errors.dropped_lines(),"peakQueueBytes":health.queue_peak.load(Ordering::SeqCst),"queueBytesAfter":health.queued_bytes.load(Ordering::SeqCst),"elapsedNs":began.elapsed().as_nanos().to_string(),"method":"real normal Sink/regular stdout/RollingFile plus genuinely drained worker; absolute 1ms offered schedule, not protocol throughput proof"});
        std::fs::write(
            root.join("metrics.json"),
            serde_json::to_vec_pretty(&result).unwrap(),
        )
        .unwrap();
        println!("{}", result);
    }

    #[test]
    fn byte_bounded_ring_rotation_and_real_file_failure_are_observable() {
        let events = Evidence::default();
        for index in 0..5000 {
            events.put(json!({"event":"bounded_probe","index":index,"text":"x".repeat(4096)}));
        }
        let status = events.query(0, 100, None);
        assert!(status["lost"].as_str().unwrap().parse::<u64>().unwrap() > 0);
        assert!(status["pendingBytesUpper"].as_u64().unwrap() <= 8 * 1024 * 1024);
        assert!(status["historyBytesUpper"].as_u64().unwrap() <= 8 * 1024 * 1024);
        assert_eq!(status["observabilityDegraded"], true);
        let root = std::env::temp_dir().join(format!(
            "ds-r5-log-{}",
            crate::domain::configuration::uuid()
        ));
        std::fs::create_dir(&root).unwrap();
        let health = Arc::new(SinkHealth::default());
        let mut writer = RollingFile::open(&root, health.clone(), 64).unwrap();
        for _ in 0..10 {
            writer.write_all(&[b'a'; 64]).unwrap();
        }
        writer.flush().unwrap();
        assert_eq!(health.rotations.load(Ordering::Relaxed), 9);
        let bytes = std::fs::read_dir(&root)
            .unwrap()
            .map(|e| e.unwrap().metadata().unwrap().len())
            .sum::<u64>();
        assert_eq!(bytes, 4 * 64);
        writer.file = std::fs::File::open(root.join("events.jsonl")).unwrap();
        writer.limit = 1024;
        let start = std::time::Instant::now();
        assert_eq!(writer.write(b"actual read-only fd failure").unwrap(), 27);
        assert_eq!(health.file_errors.load(Ordering::Relaxed), 1);
        assert_eq!(health.file_dropped_bytes.load(Ordering::Relaxed), 27);
        assert!(start.elapsed() < Duration::from_secs(1));
        println!(
            "{}",
            json!({"event":"bounded_log_probe","ring":status,"root":root,"rotations":9,"retained_bytes":bytes,"real_file_errors":1,"dropped_bytes":27})
        );
    }
    #[test]
    fn non_draining_observer_counts_real_error_and_partial_bytes() {
        unsafe {
            let mut fds = [0; 2];
            assert_eq!(libc::pipe(fds.as_mut_ptr()), 0);
            assert_eq!(libc::fcntl(fds[1], libc::F_SETFL, libc::O_NONBLOCK), 0);
            let mut loss = StdoutLoss::default();
            let data = vec![b'x'; 1_048_576];
            let partial = stdout_write(fds[1], &data, &mut loss).unwrap();
            assert!(partial["written_bytes"].as_u64().unwrap() > 0);
            assert_eq!(loss.partial_writes, 1);
            let blocked = stdout_write(fds[1], &data, &mut loss).unwrap();
            assert_eq!(blocked["written_bytes"], 0);
            assert_eq!(blocked["errno"], libc::EAGAIN);
            assert_eq!(loss.write_errors, 1);
            assert_eq!(loss.dropped_lines, 2);
            assert_eq!(
                loss.dropped_bytes,
                2 * data.len() as u64 - partial["written_bytes"].as_u64().unwrap()
            );
            let path =
                std::env::temp_dir().join(format!("ds-stdout-loss-{}.jsonl", std::process::id()));
            let file = std::fs::OpenOptions::new()
                .write(true)
                .create_new(true)
                .open(&path)
                .unwrap();
            let (writer, guard) = tracing_appender::non_blocking::NonBlockingBuilder::default()
                .buffered_lines_limit(4096)
                .lossy(true)
                .finish(file);
            let started = std::time::Instant::now();
            let subscriber = tracing_subscriber::registry().with(Sink {
                stdout_fd: fds[1],
                stdout_loss: Mutex::new(StdoutLoss::default()),
                writer: Mutex::new(writer),
                run: "stdout-failure-probe".into(),
                health: Arc::new(SinkHealth::default()),
            });
            tracing::subscriber::with_default(subscriber, || {
                tracing::info!(json = "{\"event\":\"sink_failure_probe\"}");
            });
            drop(guard); // 真实file worker flush/join，再核独立降级记录。
            let records = std::fs::read_to_string(&path)
                .unwrap()
                .lines()
                .map(|s| serde_json::from_str::<Value>(s).unwrap())
                .collect::<Vec<_>>();
            assert_eq!(records.len(), 2);
            let report = &records[1];
            assert_eq!(report["event"], "observability_degraded");
            assert_eq!(report["sink"], "stdout");
            assert_eq!(report["write_errors"], 1);
            assert_eq!(report["written_bytes"], 0);
            assert_eq!(report["errno"], libc::EAGAIN);
            assert_eq!(report["dropped_lines"], 1);
            assert!(report["dropped_bytes"].as_u64().unwrap() > 0);
            assert!(started.elapsed() < Duration::from_secs(5));
            println!(
                "{}",
                json!({"event":"stdout_failure_probe_verified", "file":path,
                "file_report":report,"partial_write_report":partial,
                "elapsed_ns":started.elapsed().as_nanos()})
            );
            libc::close(fds[0]);
            libc::close(fds[1]);
        }
    }
}
