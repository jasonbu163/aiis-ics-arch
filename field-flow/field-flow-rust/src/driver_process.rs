//! 文件：src/driver_process.rs；单PLC常驻子进程、私有有界IPC与总deadline内真实回收。
use crate::{
    config::Plc,
    domain::{now_ms, ClockAnchor, Intent},
    infrastructure::posix::{socket_bounds, Gate},
    Result,
};
use serde::{Deserialize, Serialize};
use std::{
    fs::File,
    io::{Read, Write},
    os::{
        fd::{AsRawFd, FromRawFd},
        unix::{net::UnixStream as StdStream, process::CommandExt},
    },
    path::PathBuf,
    sync::{
        atomic::{AtomicBool, Ordering},
        Arc,
    },
    thread,
    time::Duration,
};
use tokio::{
    io::{AsyncReadExt, AsyncWriteExt},
    net::UnixStream,
    process::{Child, Command},
    time::{timeout_at, Instant},
};
#[derive(Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Wire {
    pub kind: String,
    pub generation: u64,
    pub request_id: String,
    pub flow_id: String,
    pub db: u16,
    pub offset: u32,
    pub value: Option<i16>,
    pub intent: Option<Intent>,
    pub clock: Option<ClockAnchor>,
    pub remaining_ms: u64,
    pub plc: Option<Plc>,
    pub gate: Option<PathBuf>,
    pub result: String,
    pub sample: Option<i16>,
    pub write_ack: Option<crate::infrastructure::s7_int_pdu::ValidatedWriteAck>,
    pub retire: bool,
}
impl Wire {
    pub fn new(kind: &str, generation: u64, request_id: &str) -> Self {
        Self {
            kind: kind.into(),
            generation,
            request_id: request_id.into(),
            flow_id: String::new(),
            db: 1,
            offset: 0,
            value: None,
            intent: None,
            clock: None,
            remaining_ms: 5000,
            plc: None,
            gate: None,
            result: String::new(),
            sample: None,
            write_ack: None,
            retire: false,
        }
    }
}
fn encode(w: &Wire) -> Result<Vec<u8>> {
    let b = serde_json::to_vec(w).map_err(|_| "ipc_schema")?;
    if b.len() > 4096 {
        return Err("ipc_size".into());
    }
    Ok(b)
}
fn read_sync(s: &mut StdStream) -> Result<Wire> {
    let mut h = [0; 4];
    s.read_exact(&mut h).map_err(|_| "ipc_closed")?;
    let n = u32::from_be_bytes(h) as usize;
    if n == 0 || n > 4096 {
        return Err("ipc_size".into());
    }
    let mut b = vec![0; n];
    s.read_exact(&mut b).map_err(|_| "ipc_closed")?;
    serde_json::from_slice(&b).map_err(|_| "ipc_schema".into())
}
fn write_sync(s: &mut StdStream, w: &Wire) -> Result<()> {
    let b = encode(w)?;
    s.write_all(&(b.len() as u32).to_be_bytes())
        .and_then(|_| s.write_all(&b))
        .map_err(|_| "ipc_closed".into())
}
async fn send(s: &mut UnixStream, w: &Wire, deadline: Instant) -> Result<()> {
    let b = encode(w)?;
    timeout_at(deadline, async {
        s.write_u32(b.len() as u32).await?;
        s.write_all(&b).await
    })
    .await
    .map_err(|_| "driver_deadline")?
    .map_err(|_| "ipc_closed".into())
}
async fn receive(s: &mut UnixStream, deadline: Instant) -> Result<Wire> {
    timeout_at(deadline, async {
        let n = s.read_u32().await.map_err(|_| "ipc_closed")? as usize;
        if n == 0 || n > 4096 {
            return Err("ipc_size".into());
        }
        let mut b = vec![0; n];
        s.read_exact(&mut b).await.map_err(|_| "ipc_closed")?;
        serde_json::from_slice(&b).map_err(|_| "ipc_schema".into())
    })
    .await
    .map_err(|_| "driver_deadline")?
}

/// 隐藏入口只可由父进程继承的FD3/4/5启动；同步client只在此线程调用。
pub fn child_main() -> i32 {
    let mut control = unsafe { StdStream::from_raw_fd(3) };
    let mut live = unsafe { StdStream::from_raw_fd(4) };
    let _lock = unsafe { File::from_raw_fd(5) };
    let mut logs = unsafe { StdStream::from_raw_fd(6) };
    logs.set_write_timeout(Some(Duration::from_millis(50))).ok();
    let normal = Arc::new(AtomicBool::new(false));
    let done = normal.clone();
    let observer = thread::spawn(move || {
        live.set_read_timeout(Some(Duration::from_millis(100))).ok();
        let mut b = [0; 1];
        loop {
            if done.load(Ordering::Acquire) {
                return;
            }
            match live.read(&mut b) {
                Ok(0) => {
                    #[cfg(feature = "test-fixture")]
                    if std::env::var_os("FF_TEST_PARENT_LOST_DELAY_MS").is_some() {
                        thread::sleep(Duration::from_millis(100));
                    }
                    unsafe { libc::_exit(1) }
                }
                Ok(_) => unsafe { libc::_exit(1) },
                Err(e)
                    if matches!(
                        e.kind(),
                        std::io::ErrorKind::WouldBlock | std::io::ErrorKind::TimedOut
                    ) => {}
                Err(_) => unsafe { libc::_exit(1) },
            }
        }
    });
    control
        .set_write_timeout(Some(Duration::from_millis(100)))
        .ok();
    let outcome = (|| -> Result<()> {
        let emit = |logs: &mut StdStream, event: &str| -> Result<()> {
            let bytes =
                serde_json::to_vec(&serde_json::json!({"result":event,"pid":std::process::id()}))
                    .map_err(|_| "driver_log_schema")?;
            logs.write_all(&(bytes.len() as u32).to_be_bytes())
                .and_then(|_| logs.write_all(&bytes))
                .map_err(|_| "driver_log_backpressure".into())
        };
        emit(&mut logs, "starting")?;
        let boot = read_sync(&mut control)?;
        if boot.kind != "bootstrap" {
            return Err("ipc_bootstrap".into());
        }
        let generation = boot.generation;
        let plc = boot.plc.ok_or("ipc_schema")?;
        let gate = Gate::open(boot.gate.ok_or("ipc_schema")?)?;
        let client = rust_snap7::S7Client::create();
        use rust_snap7::{InternalParam as P, InternalParamValue as V};
        client
            .set_param(P::RemotePort, V::U16(plc.port))
            .map_err(|_| "driver_config")?;
        for p in [P::PingTimeout, P::SendTimeout, P::RecvTimeout] {
            client
                .set_param(p, V::I32(plc.io_timeout_ms as i32))
                .map_err(|_| "driver_config")?;
        }
        client
            .connect_to(&plc.host, plc.rack as i32, plc.slot as i32)
            .map_err(|e| format!("plc_connect:{e}"))?;
        emit(&mut logs, "connected")?;
        write_sync(&mut control, &Wire::new("ready", generation, "connect"))?;
        let mut session = crate::infrastructure::s7_int_pdu::Session::default();
        #[cfg(feature = "test-fixture")]
        if std::env::var_os("FF_TEST_REF_NEAR_END").is_some() {
            session = crate::infrastructure::s7_int_pdu::Session::test_near_end();
        }
        loop {
            let mut request = read_sync(&mut control)?;
            if request.generation != generation {
                return Err("ipc_generation".into());
            }
            if request.kind == "stop" {
                client.disconnect().map_err(|_| "plc_disconnect")?;
                drop(client);
                emit(&mut logs, "client_closed")?;
                write_sync(&mut control, &Wire::new("stopped", generation, "stop"))?;
                break;
            }
            if !matches!(request.kind.as_str(), "read" | "write") {
                return Err("ipc_operation".into());
            }
            let kind = request.kind.clone();
            let expiry = std::time::Instant::now() + Duration::from_millis(request.remaining_ms);
            write_sync(
                &mut control,
                &Wire::new("prepared", generation, &request.request_id),
            )?;
            let permit = read_sync(&mut control)?;
            if permit.kind != "start"
                || permit.generation != generation
                || permit.request_id != request.request_id
            {
                return Err("ipc_permit".into());
            }
            #[cfg(feature = "test-fixture")]
            if kind == "write" && std::env::var_os("FF_TEST_CHILD_BARRIER").is_some() {
                while !gate.with(|closed| Ok(closed))? {
                    thread::sleep(Duration::from_millis(5));
                }
            }
            #[cfg(feature = "test-fixture")]
            if kind == "write" {
                if let Some(path) = std::env::var_os("FF_TEST_CHILD_RELEASE_FILE") {
                    while !std::path::Path::new(&path).exists()
                        && !gate.with(|closed| Ok(closed))?
                    {
                        thread::sleep(Duration::from_millis(5));
                    }
                }
            }
            let admitted = gate.with(|closed| {
                if (closed && kind == "write") || permit.result == "stop" {
                    return Ok(false);
                }
                if std::time::Instant::now() >= expiry {
                    return Ok(false);
                }
                if let Some(i) = &request.intent {
                    if request
                        .clock
                        .as_ref()
                        .is_none_or(|c| c.check(now_ms()).is_err())
                    {
                        request.result = "clock_invalid".into();
                        return Ok(false);
                    }
                    if i.validate_time(now_ms()).is_err() {
                        return Ok(false);
                    }
                }
                write_sync(
                    &mut control,
                    &Wire::new("started", generation, &request.request_id),
                )?;
                Ok(true)
            })?;
            request.kind = "result".into();
            request.plc = None;
            request.gate = None;
            if !admitted {
                if request.result != "clock_invalid" {
                    request.result = "canceled".into();
                }
                write_sync(&mut control, &request)?;
                continue;
            }
            use crate::infrastructure::s7_int_pdu::{Operation, Validated};
            let operation = if kind == "write" {
                Operation::Write(request.value.ok_or("ipc_value")?)
            } else {
                Operation::Read
            };
            request.write_ack = None;
            match session.exchange(&client, request.db, request.offset, operation) {
                Ok(Validated::Read(value)) => {
                    request.result = "ok".into();
                    request.sample = Some(value.value());
                }
                Ok(Validated::Write(ack)) => {
                    request.result = "ok".into();
                    request.write_ack = Some(ack);
                }
                Err(error) => request.result = error,
            }
            request.retire = session.exhausted();
            if request.result != "ok" {
                emit(&mut logs, "plc_io_error")?;
            }
            write_sync(&mut control, &request)?;
        }
        Ok(())
    })();
    if let Err(ref error) = outcome {
        let bytes = serde_json::to_vec(
            &serde_json::json!({"result":"child_error","error_key":error,"pid":std::process::id()}),
        )
        .unwrap();
        let _ = logs
            .write_all(&(bytes.len() as u32).to_be_bytes())
            .and_then(|_| logs.write_all(&bytes));
    }
    normal.store(true, Ordering::Release);
    let joined = observer.join().is_ok();
    if outcome.is_ok() && joined {
        0
    } else {
        1
    }
}

pub struct Driver {
    child: Child,
    stream: UnixStream,
    _live: StdStream,
    pub generation: u64,
    pub pid: u32,
    pub forced: bool,
    pub reaped: bool,
    logs: Option<tokio::task::JoinHandle<Result<()>>>,
}
impl Driver {
    pub async fn spawn(
        executable: &std::path::Path,
        plc: &Plc,
        generation: u64,
        gate: PathBuf,
        lock: &File,
        state: crate::infrastructure::state::State,
    ) -> Result<Self> {
        let start = Instant::now();
        let end = start + Duration::from_millis(plc.connect_timeout_ms);
        let work = end - Duration::from_millis(400);
        let (parent, child) = StdStream::pair().map_err(|_| "ipc_create")?;
        let (live_parent, live_child) = StdStream::pair().map_err(|_| "ipc_create")?;
        let (logs_parent, logs_child) = StdStream::pair().map_err(|_| "ipc_create")?;
        socket_bounds(logs_parent.as_raw_fd()).map_err(|_| "ipc_buffer")?;
        socket_bounds(logs_child.as_raw_fd()).map_err(|_| "ipc_buffer")?;
        parent.set_nonblocking(true).map_err(|_| "ipc_create")?;
        logs_parent
            .set_nonblocking(true)
            .map_err(|_| "ipc_create")?;
        let stream = UnixStream::from_std(parent).map_err(|_| "ipc_create")?;
        let mut logs = UnixStream::from_std(logs_parent).map_err(|_| "ipc_create")?;
        socket_bounds(stream.as_raw_fd()).map_err(|_| "ipc_buffer")?;
        socket_bounds(child.as_raw_fd()).map_err(|_| "ipc_buffer")?;
        let raw_control = child.as_raw_fd();
        let raw_live = live_child.as_raw_fd();
        let raw_lock = lock.as_raw_fd();
        // 先复制到高FD，避免dup2目标3/4/5覆盖其它来源FD。
        let copies = [raw_control, raw_live, raw_lock, logs_child.as_raw_fd()]
            .map(|fd| unsafe { libc::fcntl(fd, libc::F_DUPFD_CLOEXEC, 64) });
        if copies.iter().any(|f| *f < 0) {
            for fd in copies.into_iter().filter(|fd| *fd >= 0) {
                unsafe {
                    libc::close(fd);
                }
            }
            return Err("ipc_dup".into());
        }
        let mut command = Command::new(executable);
        command
            .arg("__driver")
            .stdin(std::process::Stdio::null())
            .stdout(std::process::Stdio::null())
            .stderr(std::process::Stdio::null())
            .kill_on_drop(true);
        unsafe {
            command.as_std_mut().pre_exec(move || {
                for (src, dst) in copies.into_iter().zip([3, 4, 5, 6]) {
                    if libc::dup2(src, dst) < 0 {
                        return Err(std::io::Error::last_os_error());
                    }
                }
                Ok(())
            });
        }
        let spawned = command.spawn();
        for fd in copies {
            unsafe {
                libc::close(fd);
            }
        }
        drop(child);
        drop(live_child);
        drop(logs_child);
        let mut child = spawned.map_err(|_| "driver_spawn")?;
        let Some(pid) = child.id() else {
            child
                .start_kill()
                .map_err(|_| "driver_cleanup_incomplete")?;
            timeout_at(end, child.wait())
                .await
                .map_err(|_| "driver_cleanup_incomplete")?
                .map_err(|_| "driver_cleanup_incomplete")?;
            return Err("driver_spawn".into());
        };
        let logs_task = tokio::spawn(async move {
            loop {
                let n = match logs.read_u32().await {
                    Ok(n) => n as usize,
                    Err(e) if e.kind() == std::io::ErrorKind::UnexpectedEof => return Ok(()),
                    Err(_) => return Err("driver_log_ipc".into()),
                };
                if n == 0 || n > 4096 {
                    return Err("driver_log_size".into());
                }
                let mut bytes = vec![0; n];
                logs.read_exact(&mut bytes)
                    .await
                    .map_err(|_| "driver_log_ipc")?;
                let event: serde_json::Value =
                    serde_json::from_slice(&bytes).map_err(|_| "driver_log_schema")?;
                state.log("driver_child_event", event).await?;
            }
        });
        let mut driver = Self {
            child,
            stream,
            _live: live_parent,
            generation,
            pid,
            forced: false,
            reaped: false,
            logs: Some(logs_task),
        };
        let mut boot = Wire::new("bootstrap", generation, "connect");
        boot.plc = Some(plc.clone());
        boot.gate = Some(gate);
        let ready: Result<()> = async {
            send(&mut driver.stream, &boot, work).await?;
            let r = receive(&mut driver.stream, work).await?;
            if r.kind != "ready" || r.generation != generation {
                return Err("plc_connect".into());
            }
            Ok(())
        }
        .await;
        if let Err(e) = ready {
            driver.force(end).await?;
            return Err(format!("forced_driver_stop:{e}"));
        }
        Ok(driver)
    }
    pub async fn call<F, Fut>(
        &mut self,
        mut request: Wire,
        stop: &AtomicBool,
        deadline: Instant,
        on_started: F,
    ) -> Result<(Wire, bool)>
    where
        F: FnOnce() -> Fut,
        Fut: std::future::Future<Output = Result<()>>,
    {
        let work = deadline - Duration::from_millis(400);
        let mut started = false;
        let result: Result<(Wire, bool)> = async {
            if deadline.saturating_duration_since(Instant::now()) < Duration::from_millis(400) {
                return Err("expired".into());
            }
            request.generation = self.generation;
            request.remaining_ms =
                work.saturating_duration_since(Instant::now()).as_millis() as u64;
            send(&mut self.stream, &request, work).await?;
            let r = receive(&mut self.stream, work).await?;
            if r.kind != "prepared"
                || r.request_id != request.request_id
                || r.generation != self.generation
            {
                return Err("ipc_mismatch".into());
            }
            // 父stop和child gate均闭合；给child明确取消结果而不是虚构未开始。
            let mut permit = Wire::new("start", self.generation, &request.request_id);
            permit.result = if stop.load(Ordering::Acquire) {
                "stop".into()
            } else {
                String::new()
            };
            send(&mut self.stream, &permit, work).await?;
            let mut r = receive(&mut self.stream, work).await?;
            if r.kind == "started" {
                if r.request_id != request.request_id || r.generation != self.generation {
                    return Err("ipc_mismatch".into());
                }
                started = true;
                timeout_at(work, on_started())
                    .await
                    .map_err(|_| "driver_deadline")??;
                r = receive(&mut self.stream, work).await?;
            }
            if r.kind != "result"
                || r.request_id != request.request_id
                || r.generation != self.generation
            {
                return Err("ipc_mismatch".into());
            }
            if r.result == "clock_invalid" && started {
                return Err("ipc_mismatch".into());
            }
            if r.result == "ok"
                && request.kind == "write"
                && r.write_ack.as_ref().is_none_or(|a| a.reference() == 0)
            {
                return Err("ipc_ack_proof".into());
            }
            Ok((r, started))
        }
        .await;
        match result {
            Ok(r) => Ok(r),
            Err(e) => {
                self.force(deadline).await?;
                Err(format!("forced_driver_stop:{e}"))
            }
        }
    }
    async fn join_logs(&mut self, end: Instant) -> Result<()> {
        if let Some(mut task) = self.logs.take() {
            match timeout_at(end, &mut task).await {
                Ok(result) => result.map_err(|_| "driver_log_join")?,
                Err(_) => {
                    task.abort();
                    let _ = task.await;
                    Err("driver_log_join".into())
                }
            }
        } else {
            Ok(())
        }
    }
    pub async fn force(&mut self, end: Instant) -> Result<()> {
        self.forced = true;
        if !self.reaped {
            unsafe {
                libc::kill(self.pid as i32, libc::SIGTERM);
            }
            let term = (Instant::now() + Duration::from_millis(200)).min(end);
            if let Ok(Ok(_)) = timeout_at(term, self.child.wait()).await {
                self.reaped = true;
            }
            if !self.reaped {
                self.child
                    .start_kill()
                    .map_err(|_| "driver_cleanup_incomplete")?;
                timeout_at(end, self.child.wait())
                    .await
                    .map_err(|_| "driver_cleanup_incomplete")?
                    .map_err(|_| "driver_cleanup_incomplete")?;
                self.reaped = true;
            }
        }
        self.join_logs(end).await
    }
    pub async fn close(&mut self, end: Instant) -> Result<()> {
        let work = end - Duration::from_millis(400);
        let stop = Wire::new("stop", self.generation, "stop");
        let result: Result<()> = async {
            send(&mut self.stream, &stop, work).await?;
            let r = receive(&mut self.stream, work).await?;
            if r.kind != "stopped" {
                return Err("driver_stop".into());
            }
            let status = timeout_at(work, self.child.wait())
                .await
                .map_err(|_| "driver_deadline")?
                .map_err(|_| "driver_wait")?;
            self.reaped = true;
            if !status.success() {
                return Err("driver_exit".into());
            }
            Ok(())
        }
        .await;
        if result.is_err() {
            self.force(end).await?;
            return Err("forced_driver_stop:stop".into());
        }
        self.join_logs(end).await
    }
}
