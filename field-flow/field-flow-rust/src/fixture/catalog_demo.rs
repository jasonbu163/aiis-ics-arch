//! 文件：src/fixture/catalog_demo.rs；固定双S7/HTTP合成夹具，原始TPKT观察、一次发布及真实join/wait。
use crate::{
    domain::{id, now_ms},
    Result,
};
use serde_json::{json, Value};
use std::{
    fs,
    io::{BufRead, BufReader, Read, Write},
    net::{Shutdown, TcpListener, TcpStream},
    path::Path,
    process::{Child, Command, Stdio},
    sync::{
        atomic::{AtomicBool, AtomicU64, Ordering},
        Arc, Condvar, Mutex,
    },
    thread::{self, JoinHandle},
    time::{Duration, Instant},
};
#[derive(Clone, Default)]
pub struct Options {
    pub b_off: bool,
    pub slow_setup: bool,
    pub io_delay_ms: u64,
    pub http_delay_ms: u64,
    pub short_write_ack_once: bool,
}
struct Trace {
    rows: [Vec<Value>; 2],
    bytes: usize,
    truncated: bool,
}
struct Shared {
    start: Instant,
    seq: AtomicU64,
    trace: Mutex<Trace>,
    body: Mutex<Value>,
    issued: AtomicBool,
    short_ack_used: AtomicBool,
    gets: AtomicU64,
    reads: [AtomicU64; 2],
    writes: [AtomicU64; 2],
    sessions: [AtomicU64; 2],
    stop: AtomicBool,
    sockets: Mutex<Vec<TcpStream>>,
    a_complete: (Mutex<bool>, Condvar),
    options: Options,
    b_observer: Mutex<Option<std::sync::Weak<crate::runtime::Owner>>>,
}
impl Shared {
    fn record(&self, plc: usize, mut v: Value) {
        v["sequence"] = json!(self.seq.fetch_add(1, Ordering::SeqCst));
        v["elapsed_us"] = json!(self.start.elapsed().as_micros() as u64);
        let size = serde_json::to_vec(&v).unwrap().len();
        let mut t = self.trace.lock().unwrap();
        if t.rows[plc].len() >= 2000 || t.bytes + size > 4194304 {
            t.truncated = true;
        } else {
            t.bytes += size;
            t.rows[plc].push(v);
        }
    }
    fn socket(&self, s: &TcpStream) {
        self.sockets.lock().unwrap().push(s.try_clone().unwrap());
    }
    fn pause(&self, ms: u64) -> bool {
        let end = Instant::now() + Duration::from_millis(ms);
        while Instant::now() < end {
            if self.stop.load(Ordering::Acquire) {
                return false;
            }
            thread::sleep(Duration::from_millis(2));
        }
        true
    }
}
struct Native {
    child: Child,
    output: BufReader<std::process::ChildStdout>,
    index: usize,
}
pub struct CatalogFixture {
    shared: Arc<Shared>,
    threads: Vec<JoinHandle<Result<()>>>,
    children: Vec<Native>,
    pids: Vec<u32>,
    final_memory: Vec<Value>,
    closed: bool,
    close_result: Option<Result<()>>,
}
fn hex(b: &[u8]) -> String {
    b.iter().map(|b| format!("{b:02x}")).collect()
}
fn frame(s: &mut TcpStream) -> std::io::Result<Vec<u8>> {
    let mut h = [0; 4];
    s.read_exact(&mut h)?;
    let n = u16::from_be_bytes([h[2], h[3]]) as usize;
    if h[..2] != [3, 0] || !(4..=4096).contains(&n) {
        return Err(std::io::ErrorKind::InvalidData.into());
    }
    let mut b = vec![0; n];
    b[..4].copy_from_slice(&h);
    s.read_exact(&mut b[4..])?;
    Ok(b)
}
fn configured(listener: &TcpListener) -> Result<()> {
    listener
        .set_nonblocking(true)
        .map_err(|_| "fixture_listener".into())
}
impl CatalogFixture {
    pub fn start(executable: &Path) -> Result<Self> {
        Self::start_with(executable, Options::default())
    }
    pub fn start_with(executable: &Path, options: Options) -> Result<Self> {
        if options.io_delay_ms > 300 || options.http_delay_ms > 1200 {
            return Err("fixture_budget".into());
        }
        // Reserve all five ports before creating any child. Conflict is never resolved by killing/renumbering.
        let mut listeners = Vec::new();
        for p in [34102, 34103, 34112, 34113, 34880] {
            listeners
                .push(TcpListener::bind(("127.0.0.1", p)).map_err(|_| "fixture_port_conflict")?);
        }
        let http = listeners.pop().unwrap();
        let bnative = listeners.pop().unwrap();
        let bproxy = listeners.pop().unwrap();
        let anative = listeners.pop().unwrap();
        let aproxy = listeners.pop().unwrap();
        drop(anative);
        drop(bnative);
        let shared = Arc::new(Shared {
            start: Instant::now(),
            seq: AtomicU64::new(0),
            trace: Mutex::new(Trace {
                rows: [Vec::new(), Vec::new()],
                bytes: 0,
                truncated: false,
            }),
            body: Mutex::new(
                json!({"schema_version":1,"source_id":"demo01-feed","ready":false,"command_id":null,"value":null,"issued_at_ms":null,"expires_at_ms":null}),
            ),
            issued: AtomicBool::new(false),
            short_ack_used: AtomicBool::new(false),
            gets: AtomicU64::new(0),
            reads: [AtomicU64::new(0), AtomicU64::new(0)],
            writes: [AtomicU64::new(0), AtomicU64::new(0)],
            sessions: [AtomicU64::new(0), AtomicU64::new(0)],
            stop: AtomicBool::new(false),
            sockets: Mutex::new(Vec::new()),
            a_complete: (Mutex::new(false), Condvar::new()),
            options,
            b_observer: Mutex::new(None),
        });
        let mut f = Self {
            shared,
            threads: Vec::new(),
            children: Vec::new(),
            pids: Vec::new(),
            final_memory: Vec::new(),
            closed: false,
            close_result: None,
        };
        for i in 0..if f.shared.options.b_off { 1 } else { 2 } {
            let mut child = Command::new(executable)
                .args(["__catalog_native", if i == 0 { "a" } else { "b" }])
                .stdin(Stdio::piped())
                .stdout(Stdio::piped())
                .spawn()
                .map_err(|_| "fixture_spawn")?;
            let pid = child.id();
            f.pids.push(pid);
            let output = BufReader::new(child.stdout.take().ok_or("fixture_output")?);
            f.children.push(Native {
                child,
                output,
                index: i,
            });
            let n = f.children.last_mut().unwrap();
            use std::os::fd::AsRawFd;
            let fd = n.output.get_ref().as_raw_fd();
            let flags = unsafe { libc::fcntl(fd, libc::F_GETFL) };
            if flags < 0 || unsafe { libc::fcntl(fd, libc::F_SETFL, flags | libc::O_NONBLOCK) } < 0
            {
                return Err("fixture_output".into());
            }
            let end = Instant::now() + Duration::from_secs(3);
            let mut line = String::new();
            loop {
                match n.output.read_line(&mut line) {
                    Ok(_) => {}
                    Err(e) if e.kind() == std::io::ErrorKind::WouldBlock => {}
                    Err(_) => return Err("fixture_ready".into()),
                }
                if line.ends_with('\n') {
                    break;
                }
                if n.child.try_wait().map_err(|_| "fixture_wait")?.is_some()
                    || Instant::now() >= end
                {
                    return Err("fixture_ready_deadline".into());
                }
                thread::sleep(Duration::from_millis(2));
            }
            if unsafe { libc::fcntl(fd, libc::F_SETFL, flags) } < 0 || line.trim() != "ready" {
                return Err("fixture_ready".into());
            }
        }
        for (i, listener) in [(0, aproxy), (1, bproxy)] {
            if i == 1 && f.shared.options.b_off {
                drop(listener);
                continue;
            }
            configured(&listener)?;
            let s = f.shared.clone();
            f.threads.push(thread::spawn(move || {
                let mut clients = Vec::new();
                while !s.stop.load(Ordering::Acquire) {
                    match listener.accept() {
                        Ok((front, _)) => {
                            let s = s.clone();
                            clients.push(thread::spawn(move || proxy(front, i, s)));
                        }
                        Err(e) if e.kind() == std::io::ErrorKind::WouldBlock => {
                            thread::sleep(Duration::from_millis(2))
                        }
                        Err(_) => return Err("fixture_accept".into()),
                    }
                }
                for t in clients {
                    t.join().map_err(|_| "fixture_join")??;
                }
                Ok(())
            }));
        }
        configured(&http)?;
        let s = f.shared.clone();
        f.threads.push(thread::spawn(move||{let mut clients=Vec::new();while !s.stop.load(Ordering::Acquire){match http.accept(){Ok((mut front,_))=>{let s=s.clone();s.socket(&front);front.set_nonblocking(false).map_err(|_|"fixture_socket")?;front.set_read_timeout(Some(Duration::from_secs(10))).map_err(|_|"fixture_socket")?;front.set_write_timeout(Some(Duration::from_secs(1))).map_err(|_|"fixture_socket")?;clients.push(thread::spawn(move||{let mut buf=Vec::new();let mut one=[0];while buf.len()<4096&&front.read_exact(&mut one).is_ok(){buf.push(one[0]);if buf.ends_with(b"\r\n\r\n"){break;}}
            let body=s.body.lock().unwrap().clone();s.gets.fetch_add(1,Ordering::SeqCst);s.record(0,json!({"event":"http_enter","ready":body["ready"]}));if s.pause(s.options.http_delay_ms){let b=serde_json::to_vec(&body).unwrap();let header=format!("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n",b.len());let sent=front.write_all(header.as_bytes()).and_then(|_|front.write_all(&b)).is_ok();s.record(0,json!({"event":"http_complete","sent":sent,"body":body}));}}));},Err(e)if e.kind()==std::io::ErrorKind::WouldBlock=>thread::sleep(Duration::from_millis(2)),Err(_)=>return Err("fixture_accept".into())}}for t in clients{t.join().map_err(|_|"fixture_join")?;}Ok(())}));
        Ok(f)
    }
    pub fn observe_b(&self, owner: &Arc<crate::runtime::Owner>) {
        *self.shared.b_observer.lock().unwrap() = Some(Arc::downgrade(owner));
    }
    pub fn issue_once(&self) -> Result<Value> {
        if self.shared.issued.swap(true, Ordering::SeqCst) {
            return Err("fixture_already_issued".into());
        }
        let now = now_ms();
        let body = json!({"schema_version":1,"source_id":"demo01-feed","ready":true,"command_id":format!("catalog-{}",id()),"value":42,"issued_at_ms":now,"expires_at_ms":now+60000});
        *self.shared.body.lock().unwrap() = body.clone();
        self.shared.record(0, json!({"event":"issue","body":body}));
        Ok(body)
    }
    pub fn snapshot(&self) -> Value {
        let t = self.shared.trace.lock().unwrap();
        json!({"gets":self.shared.gets.load(Ordering::SeqCst),"reads":self.shared.reads.iter().map(|x|x.load(Ordering::SeqCst)).collect::<Vec<_>>(),"writes":self.shared.writes.iter().map(|x|x.load(Ordering::SeqCst)).collect::<Vec<_>>(),"sessions":self.shared.sessions.iter().map(|x|x.load(Ordering::SeqCst)).collect::<Vec<_>>(),"trace":t.rows,"trace_bytes":t.bytes,"trace_truncated":t.truncated,"native_pids":self.pids,"final_memory":self.final_memory,"closed":self.closed,"close_result":self.close_result})
    }
    pub fn close(&mut self) -> Result<()> {
        if self.closed {
            return self.close_result.clone().unwrap_or(Ok(()));
        }
        self.closed = true;
        let result = self.close_inner();
        self.close_result = Some(result.clone());
        result
    }
    fn close_inner(&mut self) -> Result<()> {
        self.shared.stop.store(true, Ordering::Release);
        self.shared.a_complete.1.notify_all();
        for s in self.shared.sockets.lock().unwrap().drain(..) {
            let _ = s.shutdown(Shutdown::Both);
        }
        let mut failure = None;
        for t in self.threads.drain(..) {
            if t.join()
                .map_err(|_| "fixture_join".to_string())
                .and_then(|r| r)
                .is_err()
            {
                failure = Some("fixture_join".to_string());
            }
        }
        for mut n in self.children.drain(..) {
            let sent = n
                .child
                .stdin
                .as_mut()
                .is_some_and(|s| s.write_all(b"stop\n").is_ok());
            drop(n.child.stdin.take());
            let end = Instant::now() + Duration::from_secs(3);
            let status = loop {
                if let Some(status) = n.child.try_wait().map_err(|_| "fixture_wait")? {
                    break status;
                }
                if Instant::now() >= end {
                    n.child.kill().map_err(|_| "fixture_kill")?;
                    n.child.wait().map_err(|_| "fixture_wait")?;
                    return Err("fixture_forced_cleanup".into());
                }
                thread::sleep(Duration::from_millis(5));
            };
            let mut rest = String::new();
            n.output
                .read_to_string(&mut rest)
                .map_err(|_| "fixture_output")?;
            let memory =
                serde_json::from_str::<Value>(rest.trim()).map_err(|_| "fixture_memory")?;
            self.final_memory.push(
                json!({"plc":n.index,"pid":n.child.id(),"exit_code":status.code(),"memory":memory}),
            );
            if !status.success() || !sent {
                failure = Some("fixture_exit".into());
            }
        }
        for p in [34102, 34103, 34112, 34113, 34880] {
            drop(TcpListener::bind(("127.0.0.1", p)).map_err(|_| "fixture_port_release")?);
        }
        if let Some(e) = failure {
            Err(e)
        } else {
            Ok(())
        }
    }
}
impl Drop for CatalogFixture {
    fn drop(&mut self) {
        if !self.closed {
            let _ = self.close();
        }
    }
}
fn proxy(mut front: TcpStream, i: usize, s: Arc<Shared>) -> Result<()> {
    front.set_nonblocking(false).map_err(|_| "fixture_socket")?;
    front
        .set_read_timeout(Some(Duration::from_secs(10)))
        .map_err(|_| "fixture_socket")?;
    front
        .set_write_timeout(Some(Duration::from_secs(1)))
        .map_err(|_| "fixture_socket")?;
    s.socket(&front);
    let mut back = TcpStream::connect(("127.0.0.1", if i == 0 { 34103 } else { 34113 }))
        .map_err(|_| "fixture_native")?;
    back.set_read_timeout(Some(Duration::from_secs(2)))
        .map_err(|_| "fixture_socket")?;
    back.set_write_timeout(Some(Duration::from_secs(1)))
        .map_err(|_| "fixture_socket")?;
    s.socket(&back);
    let session = s.sessions[i].fetch_add(1, Ordering::SeqCst) + 1;
    while let Ok(request) = frame(&mut front) {
        let job = request.get(7..9) == Some(&[0x32, 1]);
        let op = if job {
            request.get(17).copied().unwrap_or(0)
        } else {
            0
        };
        let began = s.start.elapsed().as_micros() as u64;
        if back.write_all(&request).is_err() {
            break;
        }
        let Ok(mut response) = frame(&mut back) else {
            break;
        };
        if i == 1 && op == 0xf0 && s.options.slow_setup {
            s.record(i, json!({"event":"setup_gate_wait","session":session}));
            let end = Instant::now() + Duration::from_millis(1200);
            let mut done = s.a_complete.0.lock().unwrap();
            while !*done && !s.stop.load(Ordering::Acquire) {
                let remaining = end.saturating_duration_since(Instant::now());
                if remaining.is_zero() {
                    return Err("fixture_setup_gate_deadline".into());
                }
                done = s.a_complete.1.wait_timeout(done, remaining).unwrap().0;
            }
        }
        if (op == 4 || op == 5) && !s.pause(s.options.io_delay_ms) {
            break;
        }
        let original_response = response.clone();
        if op == 5
            && s.options.short_write_ack_once
            && !s.short_ack_used.swap(true, Ordering::SeqCst)
        {
            response.truncate(17);
            let n = response.len() as u16;
            response[2..4].copy_from_slice(&n.to_be_bytes());
        }
        if front.write_all(&response).is_err() {
            break;
        }
        let mut row = json!({"event":"response_complete","session":session,"operation":op,"started_us":began,"request_hex":hex(&request),"response_hex":hex(&response),"original_response_hex":hex(&original_response)});
        if i == 0 && op == 4 {
            if let Some(owner) = s
                .b_observer
                .lock()
                .unwrap()
                .as_ref()
                .and_then(std::sync::Weak::upgrade)
            {
                row["b_owner_state"] = json!(owner.health().state);
            }
        }
        if op == 4 || op == 5 {
            if request.len() < 31 {
                return Err("fixture_raw_shape".into());
            }
            let db = u16::from_be_bytes([request[25], request[26]]);
            let bits =
                ((request[28] as u32) << 16) | ((request[29] as u32) << 8) | request[30] as u32;
            row["db"] = json!(db);
            row["byte_offset"] = json!(bits / 8);
            row["length"] = json!(u16::from_be_bytes([request[23], request[24]]));
            if op == 4 {
                s.reads[i].fetch_add(1, Ordering::SeqCst);
                row["wire_value"] = json!(response
                    .get(25..27)
                    .map(|x| i16::from_be_bytes([x[0], x[1]])));
            } else {
                s.writes[i].fetch_add(1, Ordering::SeqCst);
                row["wire_value"] = json!(request
                    .get(35..37)
                    .map(|x| i16::from_be_bytes([x[0], x[1]])));
            }
        }
        s.record(i, row);
        if i == 0 && op == 4 {
            *s.a_complete.0.lock().unwrap() = true;
            s.a_complete.1.notify_all();
        }
    }
    let _ = front.shutdown(Shutdown::Both);
    let _ = back.shutdown(Shutdown::Both);
    Ok(())
}
pub fn native(which: &str) -> Result<()> {
    use rust_snap7::{AreaCode, InternalParam as P, InternalParamValue as V, S7Server};
    let a = which == "a";
    if !a && which != "b" {
        return Err("fixture_arguments".into());
    }
    let mut db1 = [0xa5; 16];
    let mut db2 = [0xa5; 16];
    db1[..2].copy_from_slice(&(if a { 12i16 } else { 34i16 }).to_be_bytes());
    if a {
        db1[2..4].copy_from_slice(&1i16.to_be_bytes());
        db2[..2].copy_from_slice(&56i16.to_be_bytes());
    }
    let server = S7Server::create();
    server
        .set_param(P::LocalPort, V::U16(if a { 34103 } else { 34113 }))
        .map_err(|_| "fixture_server")?;
    server
        .register_area(AreaCode::S7AreaDB, 1, &mut db1)
        .map_err(|_| "fixture_memory")?;
    if a {
        server
            .register_area(AreaCode::S7AreaDB, 2, &mut db2)
            .map_err(|_| "fixture_memory")?;
    }
    server.start_to("127.0.0.1").map_err(|_| "fixture_server")?;
    println!("ready");
    std::io::stdout().flush().map_err(|_| "fixture_ready")?;
    let mut line = String::new();
    std::io::stdin()
        .read_line(&mut line)
        .map_err(|_| "fixture_stdin")?;
    server.stop().map_err(|_| "fixture_stop")?;
    drop(server);
    println!(
        "{}",
        json!({"db1":hex(&db1),"db2":if a{Some(hex(&db2))}else{None}})
    );
    Ok(())
}
pub fn manual(dir: &Path) -> Result<()> {
    fs::create_dir(dir).map_err(|_| "fixture_new_directory")?;
    let mut f = CatalogFixture::start(&std::env::current_exe().map_err(|_| "fixture_executable")?)?;
    println!(
        "{}",
        json!({"event":"fixture_ready","native_pids":f.pids,"published":false})
    );
    std::io::stdout().flush().map_err(|_| "fixture_ready")?;
    for line in std::io::stdin().lock().lines() {
        let line = line.map_err(|_| "fixture_stdin")?;
        if line.is_empty() {
            break;
        }
        if line == "issue" {
            match f.issue_once() {
                Ok(body) => println!(
                    "{}",
                    json!({"event":"fixture_issued","command_id":body["command_id"]})
                ),
                Err(e) => println!("{}", json!({"event":"fixture_rejected","error_key":e})),
            }
        } else {
            println!(
                "{}",
                json!({"event":"fixture_rejected","error_key":"fixture_stdin_command"})
            );
        }
    }
    let result = f.close();
    fs::write(
        dir.join("protocol.json"),
        serde_json::to_vec_pretty(&f.snapshot()).unwrap(),
    )
    .map_err(|_| "fixture_evidence")?;
    result
}
