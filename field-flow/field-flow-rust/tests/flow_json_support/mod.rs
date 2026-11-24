//! 文件：tests/flow_json_support/mod.rs；仅回环 HTTP 响应及自有产品进程证据。
use field_flow::{domain::id, infrastructure::state};
use serde_json::Value;
use std::{
    fs::{self, File},
    io::{Read, Write},
    net::{SocketAddr, TcpListener},
    path::{Path, PathBuf},
    process::{Child, Command, Stdio},
    sync::{
        atomic::{AtomicBool, Ordering},
        Arc, Mutex,
    },
    thread::{self, JoinHandle},
    time::{Duration, Instant},
};

pub fn root() -> PathBuf {
    let directory = std::env::temp_dir()
        .canonicalize()
        .unwrap()
        .join(format!("ff-006-r1-{}", id()));
    fs::create_dir(&directory).unwrap();
    directory
}

pub fn binary() -> PathBuf {
    std::env::var_os("FF006_PRODUCT")
        .map(PathBuf::from)
        .unwrap_or_else(|| env!("CARGO_BIN_EXE_field-flow").into())
}

pub fn cli(args: &[&str], cwd: &Path) -> std::process::Output {
    Command::new(binary())
        .current_dir(cwd)
        .args(args)
        .output()
        .unwrap()
}

pub fn write(path: &Path, value: &Value) {
    fs::write(path, serde_json::to_vec_pretty(value).unwrap()).unwrap();
}

pub fn fixture_state(dir: &Path, instance: &str) -> PathBuf {
    let path = dir.join("state");
    state::init(&path, "dry_run", instance).unwrap();
    path
}

pub fn until(mut ready: impl FnMut() -> bool) {
    let end = Instant::now() + Duration::from_secs(10);
    while !ready() {
        assert!(Instant::now() < end, "bounded observation deadline");
        thread::sleep(Duration::from_millis(5));
    }
}

pub fn events(path: &Path) -> Vec<Value> {
    fs::read_to_string(path)
        .unwrap_or_default()
        .lines()
        .filter_map(|row| serde_json::from_str::<Value>(row).ok())
        .map(|mut row| {
            if let Some(context) = row["context"].as_str() {
                row["context"] = serde_json::from_str(context).unwrap();
            }
            row
        })
        .collect()
}

pub struct Product(Child);

impl Product {
    pub fn start(dir: &Path, cfg: &Path, flows: &Path, state: &Path, label: &str) -> Self {
        Self(
            Command::new(binary())
                .current_dir(dir)
                .args(["run", "--config"])
                .arg(cfg)
                .arg("--flows-dir")
                .arg(flows)
                .arg("--state-dir")
                .arg(state)
                .stdout(File::create(dir.join(format!("{label}.jsonl"))).unwrap())
                .stderr(File::create(dir.join(format!("{label}.stderr"))).unwrap())
                .stdin(Stdio::null())
                .spawn()
                .unwrap(),
        )
    }

    pub fn pid(&self) -> u32 {
        self.0.id()
    }

    pub fn close(mut self, signal: i32) {
        let pid = self.pid() as i32;
        assert_eq!(unsafe { libc::kill(pid, signal) }, 0);
        let mut status = None;
        until(|| {
            status = self.0.try_wait().unwrap();
            status.is_some()
        });
        assert!(status.unwrap().success());
        assert_eq!(unsafe { libc::kill(pid, 0) }, -1);
        assert_eq!(
            std::io::Error::last_os_error().raw_os_error(),
            Some(libc::ESRCH)
        );
    }
}

impl Drop for Product {
    fn drop(&mut self) {
        if matches!(self.0.try_wait(), Ok(None)) {
            let _ = self.0.kill();
            let _ = self.0.wait();
        }
    }
}

#[derive(Clone)]
pub struct Response {
    pub status: u16,
    pub content_type: &'static str,
    pub body: String,
    pub delay: Duration,
}
impl Response {
    pub fn json(body: Value) -> Self {
        Self {
            status: 200,
            content_type: "application/json",
            body: body.to_string(),
            delay: Duration::ZERO,
        }
    }
}

#[derive(Debug, Clone)]
pub struct Request {
    pub line: String,
    pub started: Instant,
    pub reply_started: Option<Instant>,
}

pub struct HttpFixture {
    pub address: SocketAddr,
    pub requests: Arc<Mutex<Vec<Request>>>,
    stop: Arc<AtomicBool>,
    worker: Option<JoinHandle<()>>,
}

impl HttpFixture {
    pub fn new(responses: Vec<Response>) -> Self {
        assert!(!responses.is_empty());
        let listener = TcpListener::bind("127.0.0.1:0").unwrap();
        listener.set_nonblocking(true).unwrap();
        let address = listener.local_addr().unwrap();
        let requests = Arc::new(Mutex::new(Vec::<Request>::new()));
        let trace = requests.clone();
        let stop = Arc::new(AtomicBool::new(false));
        let signal = stop.clone();
        let worker = thread::spawn(move || {
            let mut clients = Vec::new();
            while !signal.load(Ordering::Acquire) {
                let mut socket = match listener.accept() {
                    Ok((socket, _)) => socket,
                    Err(e) if e.kind() == std::io::ErrorKind::WouldBlock => {
                        thread::sleep(Duration::from_millis(3));
                        continue;
                    }
                    Err(e) => panic!("accept: {e}"),
                };
                socket.set_nonblocking(false).unwrap();
                socket
                    .set_read_timeout(Some(Duration::from_secs(1)))
                    .unwrap();
                socket
                    .set_write_timeout(Some(Duration::from_secs(1)))
                    .unwrap();
                let mut bytes = Vec::new();
                let mut buffer = [0u8; 256];
                while bytes.len() < 4096 && !bytes.ends_with(b"\r\n\r\n") {
                    let Ok(count) = socket.read(&mut buffer) else {
                        break;
                    };
                    if count == 0 {
                        break;
                    }
                    bytes.extend_from_slice(&buffer[..count]);
                }
                if !bytes.ends_with(b"\r\n\r\n") {
                    continue;
                }
                let line = String::from_utf8_lossy(&bytes)
                    .lines()
                    .next()
                    .unwrap()
                    .into();
                let index = {
                    let mut requests = trace.lock().unwrap();
                    requests.push(Request {
                        line,
                        started: Instant::now(),
                        reply_started: None,
                    });
                    requests.len() - 1
                };
                let response = responses[index.min(responses.len() - 1)].clone();
                let trace = trace.clone();
                clients.push(thread::spawn(move || {
                    thread::sleep(response.delay);
                    trace.lock().unwrap()[index].reply_started = Some(Instant::now());
                    let _ = write!(socket, "HTTP/1.1 {} fixture\r\nContent-Type: {}\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
                        response.status, response.content_type, response.body.len(), response.body);
                }));
            }
            for client in clients {
                client.join().unwrap();
            }
        });
        Self {
            address,
            requests,
            stop,
            worker: Some(worker),
        }
    }
    pub fn close(mut self) {
        self.stop_worker();
        drop(TcpListener::bind(self.address).expect("owned fixture port must be reusable"));
    }
    fn stop_worker(&mut self) {
        self.stop.store(true, Ordering::Release);
        if let Some(worker) = self.worker.take() {
            worker.join().unwrap();
        }
    }
}
impl Drop for HttpFixture {
    fn drop(&mut self) {
        self.stop_worker();
    }
}
