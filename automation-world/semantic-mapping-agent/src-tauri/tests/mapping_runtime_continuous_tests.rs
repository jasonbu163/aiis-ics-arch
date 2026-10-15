//! File Path: /automation-world/semantic-mapping-agent/src-tauri/tests/mapping_runtime_continuous_tests.rs
//! Description: Pure and HTTP fixture tests for the interval API-first continuous Mapping runtime.
//! Main Features:
//!   - Verifies fresh per-cycle facts and repeated deliveries without value-change gates
//!   - Verifies strict app-open JSON preferences including the Mapping facts polling interval
//!   - Guards the r3 HTTP-only runtime against Bound Changes, cursor, direct database, and projection fallback

use std::collections::BTreeMap;
use std::fs;

use aiis_semantic_mapping_agent_lib::config::runtime_startup::{
    self, ApiMappingRuntimeAutoStart, CollectionFactSimulationAutoStart,
    RuntimeAutoStartPreferences, RuntimeStartupPreferences,
    DEFAULT_MAPPING_FACTS_POLLING_INTERVAL_MS,
};
use aiis_semantic_mapping_agent_lib::domain::mapping_runtime::{
    delivery_fingerprint, evaluate_snapshot, mapping_runtime_snapshot_from_facts,
    ApiFirstMappingRuntimeStartRequest, BackendFactSnapshot, BackendMappingRuntimeConfiguration,
    OutboundRequest,
};
use serde_json::json;

fn configuration() -> BackendMappingRuntimeConfiguration {
    serde_json::from_value(configuration_json()).unwrap()
}

fn configuration_json() -> serde_json::Value {
    json!({
        "mapping": {
            "id": "mapping-1",
            "mappingKey": "mapping-1",
            "name": "Mapping 1",
            "sourceKey": null,
            "targetApiId": "target-1",
            "targetApiKey": "target-1",
            "bindings": {
                "body:position": {
                    "kind": "fact",
                    "value": null,
                    "sourceKey": "line-a",
                    "factName": "position",
                    "valueRuleKey": null
                },
                "body:ignored": {
                    "kind": "fact",
                    "value": null,
                    "sourceKey": "line-b",
                    "factName": "ignored",
                    "valueRuleKey": null
                }
            },
            "intervalMs": 1000,
            "enabled": true,
            "rowVersion": "mapping-version-1"
        },
        "targetApi": {
            "id": "target-1",
            "apiKey": "target-1",
            "name": "Target 1",
            "httpMethod": "POST",
            "path": "/controlled-target",
            "bodyTemplate": {"position": "", "ignored": ""},
            "parameterSchema": [{
                "parameterKey": "body:position",
                "location": "body",
                "name": "position",
                "jsonPath": "position",
                "dataType": "string",
                "required": true
            }, {
                "parameterKey": "body:ignored",
                "location": "body",
                "name": "ignored",
                "jsonPath": "ignored",
                "dataType": "string",
                "required": true
            }],
            "enabled": true,
            "rowVersion": "target-version-1"
        },
        "points": [
            {"sourceKey": "line-a", "name": "position"},
            {"sourceKey": "line-b", "name": "ignored"}
        ],
        "valueRules": [],
        "state": {
            "mappingConfigId": "mapping-1",
            "mappingRowVersion": "mapping-version-1",
            "targetApiId": "target-1",
            "targetApiRowVersion": "target-version-1",
            "status": "idle",
            "lastResult": null,
            "errorCode": null,
            "lastSuccessRequestFingerprint": null
        }
    })
}

fn snapshot(value_for_position: &str, position_row_version: &str) -> BackendFactSnapshot {
    serde_json::from_value(json!({
        "items": [
            {
                "sourceKey": "line-a",
                "name": "position",
                "found": true,
                "factKind": "current",
                "dataType": "string",
                "value": value_for_position,
                "contractVersion": "collection-facts.v1",
                "updatedAt": "2026-08-28T00:00:00Z",
                "rowVersion": position_row_version
            },
            {
                "sourceKey": "line-b",
                "name": "ignored",
                "found": true,
                "factKind": "current",
                "dataType": "string",
                "value": "unused",
                "contractVersion": "collection-facts.v1",
                "updatedAt": "2026-08-28T00:00:00Z",
                "rowVersion": "AAAAAAAAAAI"
            }
        ]
    }))
    .expect("snapshot fixture must deserialize")
}

#[test]
fn fresh_snapshot_is_strict_and_builds_only_bound_values() {
    let mapping = configuration();
    let runtime_snapshot =
        mapping_runtime_snapshot_from_facts(&mapping, snapshot("A02", "same")).unwrap();
    let request = evaluate_snapshot(&runtime_snapshot)
        .unwrap()
        .request
        .unwrap();
    assert_eq!(request.body, json!({"position":"A02", "ignored":"unused"}));
    let mut incomplete = snapshot("A02", "same");
    incomplete.items.pop();
    assert!(mapping_runtime_snapshot_from_facts(&mapping, incomplete).is_err());
    let mut duplicate = snapshot("A02", "same");
    duplicate.items.push(duplicate.items[0].clone());
    assert!(mapping_runtime_snapshot_from_facts(&mapping, duplicate).is_err());
}

#[test]
fn delivery_fingerprint_is_stable_for_equivalent_request_collections() {
    let mut path_parameters = BTreeMap::new();
    path_parameters.insert("deviceId".to_string(), "device-01".to_string());
    let request = OutboundRequest {
        method: "POST".to_string(),
        path: "/devices/{deviceId}".to_string(),
        path_parameters,
        query: vec![
            ("second".to_string(), "2".to_string()),
            ("first".to_string(), "1".to_string()),
        ],
        headers: vec![
            ("X-Second".to_string(), "2".to_string()),
            ("X-First".to_string(), "1".to_string()),
        ],
        body: json!({"position": "B05"}),
    };
    let equivalent = OutboundRequest {
        query: request.query.iter().cloned().rev().collect(),
        headers: request.headers.iter().cloned().rev().collect(),
        ..request.clone()
    };
    assert_eq!(
        delivery_fingerprint(&request, "mapping-version-1", "target-version-1"),
        delivery_fingerprint(&equivalent, "mapping-version-1", "target-version-1"),
    );
    assert_ne!(
        delivery_fingerprint(&request, "mapping-version-1", "target-version-1"),
        delivery_fingerprint(&request, "mapping-version-2", "target-version-1"),
    );
}

#[test]
fn runtime_start_input_and_local_preference_json_are_strict_and_value_free() {
    let request: ApiFirstMappingRuntimeStartRequest = serde_json::from_value(json!({
        "backendBaseUrl": "http://127.0.0.1:8144"
    }))
    .unwrap();
    assert_eq!(request.backend_base_url, "http://127.0.0.1:8144");
    assert!(
        serde_json::from_value::<ApiFirstMappingRuntimeStartRequest>(json!({
            "backendBaseUrl": "http://127.0.0.1:8144",
            "factsPollingIntervalMs": 1000,
            "cursor": "not-allowed"
        }))
        .is_err()
    );

    let directory = std::env::temp_dir().join(format!(
        "tss-mapping-runtime-startup-{}-{:?}",
        std::process::id(),
        std::thread::current().id()
    ));
    let path = directory.join("runtime-startup.json");
    let preferences = RuntimeStartupPreferences {
        schema_version: 1,
        runtime_auto_start: RuntimeAutoStartPreferences {
            collection_fact_simulation: CollectionFactSimulationAutoStart {
                enabled: true,
                source_key: Some("line-a".to_string()),
            },
            api_mapping_runtime: ApiMappingRuntimeAutoStart {
                enabled: true,
                facts_polling_interval_ms: 2_500,
            },
        },
    };
    runtime_startup::save_to_path(&path, &preferences).unwrap();
    assert_eq!(runtime_startup::load_from_path(&path).unwrap(), preferences);
    let text = fs::read_to_string(&path).unwrap();
    assert!(!text.contains("password"));
    assert!(!text.contains("cursor"));

    let legacy = serde_json::from_value::<RuntimeStartupPreferences>(json!({
        "schemaVersion": 1,
        "runtimeAutoStart": {
            "collectionFactSimulation": {"enabled": false, "sourceKey": null},
            "apiMappingRuntime": {"enabled": true}
        }
    }))
    .unwrap();
    assert_eq!(
        legacy
            .runtime_auto_start
            .api_mapping_runtime
            .facts_polling_interval_ms,
        DEFAULT_MAPPING_FACTS_POLLING_INTERVAL_MS,
    );
    assert!(runtime_startup::save_to_path(
        &path,
        &RuntimeStartupPreferences {
            runtime_auto_start: RuntimeAutoStartPreferences {
                collection_fact_simulation: CollectionFactSimulationAutoStart {
                    enabled: true,
                    source_key: None,
                },
                api_mapping_runtime: ApiMappingRuntimeAutoStart {
                    enabled: true,
                    facts_polling_interval_ms: 0,
                },
            },
            ..preferences
        },
    )
    .is_err());
    let _ = fs::remove_dir_all(directory);
}

#[test]
fn continuous_runtime_is_http_only_and_uses_fresh_snapshot_without_changes_cursor() {
    let service = include_str!("../src/services/mapping_runtime/mod.rs");
    for required in [
        "runtime_configurations",
        "mapping_runtime_snapshot_from_facts",
        "snapshot_facts",
        "chunks(BOUND_FACTS_MAX_COUNT)",
        "MappingTickOutcome::ReadFailed",
        "request_ambiguous",
        "Policy::none",
        "retry::never",
    ] {
        assert!(service.contains(required), "missing {required}");
    }
    for forbidden in [
        "collection-facts\", \"changes",
        "bound_changes",
        "changed_fact_identities",
        "skipped_unchanged",
        "facts_polling_interval_ms",
        "next_change_token",
        "input_cursor",
        "ConnectionProfile",
        "tiberius",
        "projection",
        "service_mapping",
        "MSSQL",
    ] {
        assert!(
            !service.contains(forbidden),
            "forbidden continuous fallback {forbidden}"
        );
    }
}

// The fixture binds an ephemeral loopback port and never reads saved connection settings.
use aiis_semantic_mapping_agent_lib::services::mapping_runtime::{
    self, ApiFirstMappingRuntimeState,
};
use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};
use std::sync::{
    atomic::{AtomicBool, Ordering},
    Arc, Mutex,
};
use std::time::{Duration, Instant};

#[derive(Default)]
struct HttpEvidence {
    reads: Vec<Instant>,
    targets: Vec<serde_json::Value>,
    completions: Vec<serde_json::Value>,
    claims: usize,
}

#[derive(Default)]
struct FixtureOptions {
    fail_read: Option<usize>,
    missing_read: Option<usize>,
    read_delay_ms: u64,
    target_delay_ms: u64,
    target_failure: bool,
    target_ambiguous: bool,
    lease_denied: bool,
    static_mapping: bool,
}

struct HttpFixture {
    url: String,
    evidence: Arc<Mutex<HttpEvidence>>,
    stop: Arc<AtomicBool>,
    thread: Option<std::thread::JoinHandle<()>>,
}

impl HttpFixture {
    fn new(options: FixtureOptions) -> Self {
        let listener = TcpListener::bind("127.0.0.1:0").unwrap();
        let url = format!("http://{}", listener.local_addr().unwrap());
        listener.set_nonblocking(true).unwrap();
        let evidence = Arc::new(Mutex::new(HttpEvidence::default()));
        let stop = Arc::new(AtomicBool::new(false));
        let (log, shutdown) = (evidence.clone(), stop.clone());
        let thread = std::thread::spawn(move || {
            let mut workers = Vec::new();
            let options = Arc::new(options);
            while !shutdown.load(Ordering::SeqCst) {
                match listener.accept() {
                    Ok((stream, _)) => {
                        let (log, options) = (log.clone(), options.clone());
                        workers.push(std::thread::spawn(move || {
                            fixture_request(stream, log, &options)
                        }));
                    }
                    Err(error) if error.kind() == std::io::ErrorKind::WouldBlock => {
                        std::thread::sleep(Duration::from_millis(2));
                    }
                    Err(error) => panic!("fixture accept failed: {error}"),
                }
            }
            for worker in workers {
                worker.join().unwrap();
            }
        });
        Self {
            url,
            evidence,
            stop,
            thread: Some(thread),
        }
    }

    async fn start(&self) -> ApiFirstMappingRuntimeState {
        let state = ApiFirstMappingRuntimeState::default();
        mapping_runtime::start_api_first_mapping_runtime(
            &state,
            ApiFirstMappingRuntimeStartRequest {
                backend_base_url: self.url.clone(),
            },
        )
        .await
        .unwrap();
        state
    }

    async fn until(&self, ready: impl Fn(&HttpEvidence) -> bool) {
        let deadline = Instant::now() + Duration::from_secs(5);
        loop {
            if ready(&self.evidence.lock().unwrap()) {
                return;
            }
            assert!(Instant::now() < deadline, "fixture timed out");
            tokio::time::sleep(Duration::from_millis(5)).await;
        }
    }
}

impl Drop for HttpFixture {
    fn drop(&mut self) {
        self.stop.store(true, Ordering::SeqCst);
        if let Some(thread) = self.thread.take() {
            let result = thread.join();
            if !std::thread::panicking() {
                result.unwrap();
            }
        }
    }
}

fn fixture_request(
    mut stream: TcpStream,
    evidence: Arc<Mutex<HttpEvidence>>,
    options: &FixtureOptions,
) {
    stream.set_nonblocking(false).unwrap();
    stream
        .set_read_timeout(Some(Duration::from_secs(3)))
        .unwrap();
    let mut bytes = Vec::new();
    let (header_end, length) = loop {
        let mut buffer = [0; 4096];
        let size = stream.read(&mut buffer).unwrap();
        if size == 0 {
            return;
        }
        bytes.extend_from_slice(&buffer[..size]);
        if let Some(index) = bytes.windows(4).position(|part| part == b"\r\n\r\n") {
            let header = String::from_utf8_lossy(&bytes[..index]);
            let length = header
                .lines()
                .find_map(|line| {
                    let (key, value) = line.split_once(':')?;
                    key.eq_ignore_ascii_case("content-length")
                        .then(|| value.trim().parse::<usize>().unwrap())
                })
                .unwrap_or(0);
            break (index + 4, length);
        }
    };
    while bytes.len() < header_end + length {
        let mut buffer = [0; 4096];
        let size = stream.read(&mut buffer).unwrap();
        assert!(size > 0);
        bytes.extend_from_slice(&buffer[..size]);
    }
    let header = String::from_utf8_lossy(&bytes[..header_end]);
    let path = header
        .lines()
        .next()
        .unwrap()
        .split_whitespace()
        .nth(1)
        .unwrap();
    let body: serde_json::Value = if length == 0 {
        json!(null)
    } else {
        serde_json::from_slice(&bytes[header_end..header_end + length]).unwrap()
    };
    let mut configuration = configuration_json();
    configuration["mapping"]["intervalMs"] = json!(70);
    if options.static_mapping {
        configuration["mapping"]["bindings"] = json!({
            "body:position":{"kind":"constant","value":"A02"},
            "body:ignored":{"kind":"constant","value":"unused"}
        });
        configuration["points"] = json!([]);
    }
    // Even a matching prior successful fingerprint must never suppress delivery.
    let snapshot = mapping_runtime_snapshot_from_facts(
        &self_configuration(&configuration),
        if options.static_mapping {
            BackendFactSnapshot { items: vec![] }
        } else {
            snapshot("A02", "same")
        },
    )
    .unwrap();
    let request = evaluate_snapshot(&snapshot).unwrap().request.unwrap();
    configuration["state"]["lastSuccessRequestFingerprint"] = json!(delivery_fingerprint(
        &request,
        "mapping-version-1",
        "target-version-1"
    ));
    let mut status = 200;
    let data = match path {
        "/api/tss/v1/mapping-runtime/configurations" => json!([configuration]),
        "/api/integration/v1/collection-facts/snapshot" => {
            assert_eq!(body["points"], configuration["points"]);
            let count = {
                let mut log = evidence.lock().unwrap();
                log.reads.push(Instant::now());
                log.reads.len()
            };
            std::thread::sleep(Duration::from_millis(options.read_delay_ms));
            if options.fail_read == Some(count) {
                status = 503;
                json!(null)
            } else {
                json!({"items":[
                    {"sourceKey":"line-a","name":"position","found": options.missing_read != Some(count),
                     "dataType":"string","value": if count < 3 {"A02"} else {"A01"},"rowVersion":"same"},
                    {"sourceKey":"line-b","name":"ignored","found":true,"dataType":"string","value":"unused","rowVersion":"same"}
                ]})
            }
        }
        "/api/tss/v1/mapping-runtime/mapping-1/claim" => {
            evidence.lock().unwrap().claims += 1;
            assert_eq!(body["expectedMappingRowVersion"], "mapping-version-1");
            assert_eq!(body["expectedTargetApiRowVersion"], "target-version-1");
            json!({"claimed":!options.lease_denied,"errorCode": if options.lease_denied { json!("tss_mapping_runtime_lease_held") } else {json!(null)}, "state":configuration["state"]})
        }
        "/api/tss/v1/mapping-runtime/mapping-1/complete" => {
            evidence.lock().unwrap().completions.push(body.clone());
            assert!(!body["runtimeId"].as_str().unwrap().is_empty());
            let mut state = configuration["state"].clone();
            state["lastResult"] = body["status"].clone();
            match body["status"].as_str().unwrap() {
                "succeeded" => {
                    assert_eq!(body["deliveryFingerprint"].as_str().unwrap().len(), 16);
                }
                "preflight_rejected" => {
                    assert_eq!(body["errorCode"], "tss_mapping_runtime_required_unresolved");
                }
                "request_failed" | "request_ambiguous" => {
                    state["status"] = json!("blocked");
                }
                other => panic!("unexpected receipt: {other}"),
            }
            state
        }
        "/controlled-target" => {
            evidence.lock().unwrap().targets.push(body);
            std::thread::sleep(Duration::from_millis(options.target_delay_ms));
            if options.target_ambiguous {
                return;
            }
            if options.target_failure {
                status = 500;
            }
            json!({})
        }
        other => panic!("unexpected fixture endpoint: {other}"),
    };
    let body = json!({"code": status, "message":"fixture", "data":data}).to_string();
    let response = format!("HTTP/1.1 {status} Fixture\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{body}", body.len());
    let _ = stream.write_all(response.as_bytes());
}

fn self_configuration(value: &serde_json::Value) -> BackendMappingRuntimeConfiguration {
    serde_json::from_value(value.clone()).unwrap()
}

#[tokio::test]
async fn interval_reads_fresh_facts_and_delivers_same_value_again() {
    let fixture = HttpFixture::new(FixtureOptions::default());
    let state = fixture.start().await;
    fixture.until(|log| log.completions.len() >= 3).await;
    mapping_runtime::stop_api_first_mapping_runtime(&state)
        .await
        .unwrap();
    let log = fixture.evidence.lock().unwrap();
    assert_eq!(
        log.targets[..3]
            .iter()
            .map(|body| body["position"].as_str().unwrap())
            .collect::<Vec<_>>(),
        ["A02", "A02", "A01"]
    );
    assert_eq!(log.reads.len(), log.targets.len());
    assert_eq!(log.claims, log.targets.len());
    assert_eq!(
        log.completions[0]["deliveryFingerprint"],
        log.completions[1]["deliveryFingerprint"]
    );
}

#[tokio::test]
async fn failed_read_never_reuses_previous_value_and_retries_next_interval() {
    let fixture = HttpFixture::new(FixtureOptions {
        fail_read: Some(2),
        ..Default::default()
    });
    let state = fixture.start().await;
    fixture.until(|log| log.completions.len() >= 2).await;
    mapping_runtime::stop_api_first_mapping_runtime(&state)
        .await
        .unwrap();
    let log = fixture.evidence.lock().unwrap();
    assert_eq!(log.reads.len(), 3);
    assert_eq!(log.targets.len(), 2);
    assert_eq!(log.targets[1]["position"], "A01");
    assert!(log.reads[2].duration_since(log.reads[1]) >= Duration::from_millis(70));
}

#[tokio::test]
async fn missing_required_fact_rejects_cycle_without_post() {
    let fixture = HttpFixture::new(FixtureOptions {
        missing_read: Some(2),
        ..Default::default()
    });
    let state = fixture.start().await;
    fixture.until(|log| log.completions.len() >= 3).await;
    mapping_runtime::stop_api_first_mapping_runtime(&state)
        .await
        .unwrap();
    let log = fixture.evidence.lock().unwrap();
    assert_eq!(log.targets.len(), 2);
    assert_eq!(log.completions[1]["status"], "preflight_rejected");
}

#[tokio::test]
async fn pause_and_stop_during_read_do_not_send_and_resume_reads_again() {
    let fixture = HttpFixture::new(FixtureOptions {
        read_delay_ms: 130,
        ..Default::default()
    });
    let state = fixture.start().await;
    fixture.until(|log| log.reads.len() == 1).await;
    mapping_runtime::pause_api_first_mapping_runtime(&state)
        .await
        .unwrap();
    assert_eq!(fixture.evidence.lock().unwrap().targets.len(), 0);
    mapping_runtime::resume_api_first_mapping_runtime(&state).unwrap();
    fixture.until(|log| log.reads.len() == 2).await;
    mapping_runtime::stop_api_first_mapping_runtime(&state)
        .await
        .unwrap();
    assert_eq!(fixture.evidence.lock().unwrap().targets.len(), 0);
}

#[tokio::test]
async fn slow_io_finishes_before_interval_and_duplicate_start_is_rejected() {
    let fixture = HttpFixture::new(FixtureOptions {
        read_delay_ms: 60,
        target_delay_ms: 90,
        ..Default::default()
    });
    let state = fixture.start().await;
    assert!(mapping_runtime::start_api_first_mapping_runtime(
        &state,
        ApiFirstMappingRuntimeStartRequest {
            backend_base_url: fixture.url.clone()
        }
    )
    .await
    .is_err());
    fixture.until(|log| log.completions.len() >= 2).await;
    mapping_runtime::stop_api_first_mapping_runtime(&state)
        .await
        .unwrap();
    let log = fixture.evidence.lock().unwrap();
    assert!(log.reads[1].duration_since(log.reads[0]) >= Duration::from_millis(220));
}

#[tokio::test]
async fn lease_and_target_failures_block_without_replay() {
    for options in [
        FixtureOptions {
            lease_denied: true,
            ..Default::default()
        },
        FixtureOptions {
            target_failure: true,
            ..Default::default()
        },
        FixtureOptions {
            target_ambiguous: true,
            ..Default::default()
        },
    ] {
        let lease_denied = options.lease_denied;
        let fixture = HttpFixture::new(options);
        let state = fixture.start().await;
        let deadline = Instant::now() + Duration::from_secs(5);
        while state.0.snapshot().status != "blocked" {
            assert!(Instant::now() < deadline);
            tokio::time::sleep(Duration::from_millis(5)).await;
        }
        tokio::time::sleep(Duration::from_millis(120)).await;
        let log = fixture.evidence.lock().unwrap();
        assert_eq!(log.reads.len(), 1);
        assert_eq!(log.targets.len(), if lease_denied { 0 } else { 1 });
    }
}

#[tokio::test]
async fn static_mapping_sends_each_interval_without_fake_fact_reads() {
    let fixture = HttpFixture::new(FixtureOptions {
        static_mapping: true,
        ..Default::default()
    });
    let state = fixture.start().await;
    fixture.until(|log| log.completions.len() >= 2).await;
    mapping_runtime::stop_api_first_mapping_runtime(&state)
        .await
        .unwrap();
    let log = fixture.evidence.lock().unwrap();
    assert!(log.reads.is_empty());
    assert_eq!(log.targets.len(), 2);
}
