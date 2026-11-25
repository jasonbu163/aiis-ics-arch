//! File Path: /automation-world/semantic-mapping-agent/src-tauri/src/services/http_mapping/fixture.rs
//! Description: SMA 应用服务验收所用的临时 SQLite profile 和可观察的本机 HTTP 夹具。

use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use std::time::Duration;
use std::{collections::BTreeMap, io};

use serde::Serialize;
use serde_json::{json, Value};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::{TcpListener, TcpStream};
use tokio::task::JoinHandle;

use super::{HttpMappingService, LocalConfigurationService, SchedulerSide};
use crate::{contracts::local_configuration::ChangeIntent, domain::runtime::ManagedRuntimeState};

pub(super) struct Profile {
    directory: PathBuf,
    pub path: PathBuf,
    pub config: LocalConfigurationService,
    pub runtime: HttpMappingService,
}

impl Profile {
    pub fn new() -> Self {
        let directory = std::env::temp_dir().join(format!("sma001-r3-{}", uuid::Uuid::new_v4()));
        let path = directory.join("configuration.sqlite3");
        let config = LocalConfigurationService::new(Ok(path.clone()));
        let runtime = HttpMappingService::new(config.clone());
        Self {
            directory,
            path,
            config,
            runtime,
        }
    }

    pub fn merge(&self, document: Value) -> u64 {
        let revision = self.revision();
        let intent = intent("merge", "configuration", None, document);
        let preview = self.config.preview(revision, intent.clone()).unwrap();
        assert!(preview.errors.is_empty(), "{:?}", preview.errors);
        self.config
            .apply(revision, intent, &preview.token, true, &idle())
            .unwrap()
            .revision
    }

    pub fn update(&self, resource: &str, id: &str, value: Value) -> u64 {
        self.config
            .change(
                self.revision(),
                intent("upsert", resource, Some(id), value),
                &idle(),
            )
            .unwrap()
            .revision
    }

    pub fn revision(&self) -> u64 {
        self.config.load().unwrap().revision
    }
}

impl Drop for Profile {
    fn drop(&mut self) {
        self.runtime.begin_shutdown();
        let _ = std::fs::remove_dir_all(&self.directory);
    }
}

fn idle() -> ManagedRuntimeState {
    ManagedRuntimeState::new("api_first_mapping")
}

fn intent(kind: &str, resource: &str, id: Option<&str>, payload: Value) -> ChangeIntent {
    ChangeIntent {
        kind: kind.into(),
        resource: resource.into(),
        id: id.map(str::to_owned),
        payload,
    }
}

#[derive(Clone)]
pub(super) struct Reply {
    pub status: u16,
    pub content: Option<String>,
    pub wait: Duration,
}

impl Reply {
    pub fn new(status: u16, content: &str) -> Self {
        Self {
            status,
            content: Some(content.into()),
            wait: Duration::ZERO,
        }
    }

    pub fn json(content: Value) -> Self {
        Self::new(200, &content.to_string())
    }

    pub fn slow(mut self, delay_ms: u64) -> Self {
        self.wait = Duration::from_millis(delay_ms);
        self
    }

    pub fn close_connection() -> Self {
        Self {
            status: 0,
            content: None,
            wait: Duration::ZERO,
        }
    }
}

#[derive(Clone, Debug)]
pub(super) struct Request {
    pub method: String,
    pub path: String,
    pub body: Option<Value>,
}

#[derive(Clone, Copy, Debug, Default, Serialize)]
pub(super) struct Traffic {
    pub inflight: usize,
    pub peak: usize,
    pub completed: usize,
}

impl Traffic {
    fn start(&mut self) {
        self.inflight += 1;
        self.peak = self.peak.max(self.inflight);
    }

    fn stop(&mut self) {
        self.inflight -= 1;
        self.completed += 1;
    }
}

#[derive(Default)]
struct Server {
    replies: BTreeMap<String, Reply>,
    requests: Vec<Request>,
    by_method: BTreeMap<String, Traffic>,
    by_path: BTreeMap<String, Traffic>,
}

pub(super) struct ServerFixture {
    pub base: String,
    server: Arc<Mutex<Server>>,
    handle: JoinHandle<()>,
}

impl ServerFixture {
    pub async fn start() -> Self {
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let base = format!("http://{}", listener.local_addr().unwrap());
        let server = Arc::new(Mutex::new(Server::default()));
        let state = server.clone();
        let handle = tokio::spawn(async move {
            while let Ok((stream, _)) = listener.accept().await {
                let state = state.clone();
                tokio::spawn(async move {
                    let _ = serve(stream, state).await;
                });
            }
        });
        Self {
            base,
            server,
            handle,
        }
    }

    pub fn set(&self, path: &str, reply: Reply) {
        self.server
            .lock()
            .unwrap()
            .replies
            .insert(path.into(), reply);
    }

    pub fn count(&self, method: &str) -> usize {
        self.server
            .lock()
            .unwrap()
            .requests
            .iter()
            .filter(|r| r.method == method)
            .count()
    }

    pub fn requests(&self, method: &str) -> Vec<Request> {
        self.server
            .lock()
            .unwrap()
            .requests
            .iter()
            .filter(|r| r.method == method)
            .cloned()
            .collect()
    }

    pub fn traffic(&self) -> (BTreeMap<String, Traffic>, BTreeMap<String, Traffic>) {
        let server = self.server.lock().unwrap();
        (server.by_method.clone(), server.by_path.clone())
    }
}

impl Drop for ServerFixture {
    fn drop(&mut self) {
        self.handle.abort();
    }
}

async fn serve(mut stream: TcpStream, state: Arc<Mutex<Server>>) -> io::Result<()> {
    let request = read_request(&mut stream).await?;
    let path = request.path.split('?').next().unwrap().to_owned();
    let method = request.method.clone();
    let reply = {
        let mut state = state.lock().unwrap();
        state.requests.push(request);
        state.by_method.entry(method.clone()).or_default().start();
        state.by_path.entry(path.clone()).or_default().start();
        state
            .replies
            .get(&path)
            .cloned()
            .unwrap_or_else(|| Reply::new(404, "{}"))
    };
    tokio::time::sleep(reply.wait).await;
    {
        let mut state = state.lock().unwrap();
        state.by_method.get_mut(&method).unwrap().stop();
        state.by_path.get_mut(&path).unwrap().stop();
    }
    if let Some(content) = reply.content {
        let response = format!("HTTP/1.1 {} Fixture\r\nContent-Length: {}\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n{content}", reply.status, content.len());
        stream.write_all(response.as_bytes()).await?;
    }
    Ok(())
}

async fn read_request(stream: &mut TcpStream) -> io::Result<Request> {
    let mut bytes = Vec::new();
    let mut chunk = [0; 4096];
    let (method, path, length, start) = loop {
        let count = stream.read(&mut chunk).await?;
        if count == 0 || bytes.len() > 64 * 1024 {
            return Err(io::ErrorKind::InvalidData.into());
        }
        bytes.extend_from_slice(&chunk[..count]);
        if let Some(separator) = bytes.windows(4).position(|part| part == b"\r\n\r\n") {
            let text = String::from_utf8_lossy(&bytes[..separator]);
            let mut line = text.split_ascii_whitespace();
            let method = line.next().unwrap_or_default().to_owned();
            let path = line.next().unwrap_or_default().to_owned();
            let length = text
                .lines()
                .filter_map(|row| row.split_once(':'))
                .find_map(|(key, value)| {
                    key.eq_ignore_ascii_case("Content-Length")
                        .then(|| value.trim().parse::<usize>().ok())
                        .flatten()
                })
                .unwrap_or_default();
            break (method, path, length, separator + 4);
        }
    };
    if bytes.len() < start + length {
        let current = bytes.len();
        bytes.resize(start + length, 0);
        stream.read_exact(&mut bytes[current..]).await?;
    }
    let body = serde_json::from_slice(&bytes[start..start + length]).ok();
    Ok(Request { method, path, body })
}

pub(super) fn source(key: &str, url: &str, points: Vec<Value>) -> Value {
    json!({"name":key,"sourceKey":key,"url":url,"query":{},"enabled":true,"points":points,"intervalMs":120,"timeoutMs":120})
}

pub(super) fn point(name: &str, data_type: &str, path: &str) -> Value {
    json!({"pointKey":name,"name":name,"dataType":data_type,"path":path})
}

pub(super) fn target(key: &str, url: &str, template: Value, parameters: Vec<Value>) -> Value {
    json!({"apiKey":key,"name":key,"httpMethod":"POST","path":"/unused","url":url,"timeoutMs":90,
        "schemaSource":"manual","operationId":null,"bodyTemplate":template,"parameterSchema":parameters,
        "idempotencySupported":false,"enabled":true,"receipt":{"path":"/code","equals":200}})
}

pub(super) fn parameter(key: &str, path: &str, data_type: &str, required: bool) -> Value {
    let name = key
        .strip_prefix("body:")
        .expect("fixture body parameter key");
    json!({"parameterKey":key,"location":"body","name":name,"jsonPath":path,"dataType":data_type,"required":required})
}

pub(super) fn mapping(key: &str, target: &str, bindings: Value) -> Value {
    json!({"mappingKey":key,"name":key,"sourceKey":null,"targetApiKey":target,"bindings":bindings,
        "intervalMs":60_000,"maxAgeMs":60_000,"enabled":true})
}

pub(super) fn fact(source: &str, point: &str) -> Value {
    json!({"kind":"fact","sourceKey":source,"factName":point,"value":null,"valueRuleKey":null})
}

pub(super) fn fixed(value: Value) -> Value {
    json!({"kind":"constant","sourceKey":null,"factName":null,"value":value,"valueRuleKey":null})
}

pub(super) async fn wait_for(description: &str, predicate: impl Fn() -> bool) {
    tokio::time::timeout(Duration::from_secs(6), async {
        while !predicate() {
            tokio::time::sleep(Duration::from_millis(10)).await;
        }
    })
    .await
    .unwrap_or_else(|error| panic!("{description}: {error}"));
}

pub(super) async fn stop(runtime: &HttpMappingService, side: SchedulerSide) {
    runtime.stop(side);
    wait_for("scheduler drains", || {
        runtime.scheduler.status(side).phase
            == crate::services::http_scheduler::SchedulerPhase::Stopped
    })
    .await;
}
