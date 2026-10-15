//! File Path: /automation-world/semantic-mapping-agent/src-tauri/tests/mapping_runtime_manual_run_tests.rs
//! Description: Controlled-fixture tests for one saved Mapping manual HTTP run.
//! Main Features:
//!   - Verifies one Backend claim, at most one fixture target request, and one safe completion
//!   - Verifies null-rule typed facts, optional omission, required rule rejection, and no retry
//!   - Uses an in-process loopback fixture only; it never contacts a business Target API

use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};
use std::sync::{Arc, Mutex};
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant};

use aiis_semantic_mapping_agent_lib::services::mapping_runtime::run_mapping_manual_once;
use serde_json::{json, Value};

#[derive(Debug)]
struct CapturedRequest {
    method: String,
    path: String,
    headers: Vec<(String, String)>,
    body: Vec<u8>,
}

#[derive(Clone, Copy)]
enum FixtureScenario {
    OptionalOmission,
    RequiredRuleRejected,
}

fn spawn_fixture(
    scenario: FixtureScenario,
    expected_requests: usize,
) -> (String, Arc<Mutex<Vec<CapturedRequest>>>, JoinHandle<()>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("fixture must bind a loopback port");
    listener
        .set_nonblocking(true)
        .expect("fixture must be nonblocking");
    let address = listener.local_addr().expect("fixture address must exist");
    let captured = Arc::new(Mutex::new(Vec::new()));
    let captured_for_thread = Arc::clone(&captured);
    let handle = thread::spawn(move || {
        let deadline = Instant::now() + Duration::from_secs(3);
        while captured_for_thread.lock().expect("fixture lock").len() < expected_requests {
            match listener.accept() {
                Ok((mut stream, _)) => {
                    let request = read_request(&mut stream);
                    let response = fixture_response(scenario, &request);
                    captured_for_thread
                        .lock()
                        .expect("fixture lock")
                        .push(request);
                    write_response(&mut stream, response.0, response.1);
                }
                Err(error) if error.kind() == std::io::ErrorKind::WouldBlock => {
                    assert!(
                        Instant::now() < deadline,
                        "fixture timed out waiting for request"
                    );
                    thread::sleep(Duration::from_millis(5));
                }
                Err(error) => panic!("fixture accept failed: {error}"),
            }
        }
    });
    (format!("http://{address}"), captured, handle)
}

fn fixture_response(scenario: FixtureScenario, request: &CapturedRequest) -> (u16, Value) {
    match request.path.as_str() {
        "/api/tss/v1/mappings/mapping-1/manual-runs/claim" => {
            (200, backend_envelope(claim_response(scenario)))
        }
        "/api/tss/v1/mapping-manual-runs/run-1/complete" => {
            let completion: Value =
                serde_json::from_slice(&request.body).expect("completion body must be JSON");
            let status = completion["status"]
                .as_str()
                .expect("completion status")
                .to_string();
            let error_code = completion["errorCode"].as_str().map(str::to_string);
            let http_status_class = completion["httpStatusClass"].as_str().map(str::to_string);
            let response_summary = completion["responseSummary"].as_str().map(str::to_string);
            let resolved_parameter_keys = completion["resolvedParameterKeys"]
                .as_array()
                .cloned()
                .unwrap_or_default();
            let unresolved_parameter_keys = completion["unresolvedParameterKeys"]
                .as_array()
                .cloned()
                .unwrap_or_default();
            (
                200,
                backend_envelope(manual_run(
                    &status,
                    error_code.as_deref(),
                    http_status_class.as_deref(),
                    response_summary.as_deref(),
                    resolved_parameter_keys,
                    unresolved_parameter_keys,
                )),
            )
        }
        "/controlled-target" if matches!(scenario, FixtureScenario::OptionalOmission) => {
            (201, json!({"fixture": "accepted"}))
        }
        path => panic!("fixture received unexpected request path: {path}"),
    }
}

fn backend_envelope(data: Value) -> Value {
    json!({"code": 200, "message": "ok", "data": data})
}

fn claim_response(scenario: FixtureScenario) -> Value {
    json!({
        "claimed": true,
        "errorCode": null,
        "run": manual_run("in_progress", None, None, None, vec![], vec![]),
        "snapshot": snapshot(scenario),
    })
}

fn manual_run(
    status: &str,
    error_code: Option<&str>,
    http_status_class: Option<&str>,
    response_summary: Option<&str>,
    resolved_parameter_keys: Vec<Value>,
    unresolved_parameter_keys: Vec<Value>,
) -> Value {
    let resolved_parameter_count = resolved_parameter_keys.len();
    let unresolved_parameter_count = unresolved_parameter_keys.len();
    let completed_at = if status == "in_progress" {
        Value::Null
    } else {
        Value::String("2026-08-28T00:00:01".to_string())
    };
    json!({
        "runId": "run-1",
        "mappingConfigId": "mapping-1",
        "mappingRowVersion": "mapping-version-1",
        "targetApiId": "target-1",
        "targetApiRowVersion": "target-version-1",
        "snapshotId": "snapshot-1",
        "status": status,
        "errorCode": error_code,
        "httpStatusClass": http_status_class,
        "responseSummary": response_summary,
        "resolvedParameterKeys": resolved_parameter_keys,
        "unresolvedParameterKeys": unresolved_parameter_keys,
        "resolvedParameterCount": resolved_parameter_count,
        "unresolvedParameterCount": unresolved_parameter_count,
        "leaseExpiresAt": "2026-08-28T00:02:00",
        "startedAt": "2026-08-28T00:00:00",
        "completedAt": completed_at,
    })
}

fn snapshot(scenario: FixtureScenario) -> Value {
    match scenario {
        FixtureScenario::OptionalOmission => json!({
            "snapshotId": "snapshot-1",
            "mapping": {
                "id": "mapping-1",
                "mappingKey": "saved-mapping",
                "name": "Saved Mapping",
                "sourceKey": null,
                "targetApiId": "target-1",
                "targetApiKey": "target-1",
                "bindings": {
                    "body:required": {"kind": "fact", "value": null, "sourceKey": "line-01", "factName": "required", "valueRuleKey": null},
                    "body:optionalBody": {"kind": "fact", "value": null, "sourceKey": "line-01", "factName": "optional-body", "valueRuleKey": null},
                    "query:optionalQuery": {"kind": "fact", "value": null, "sourceKey": "line-01", "factName": "optional-query", "valueRuleKey": null},
                    "header:X-Optional": {"kind": "fact", "value": null, "sourceKey": "line-01", "factName": "optional-header", "valueRuleKey": null}
                },
                "intervalMs": 1000,
                "enabled": true,
                "rowVersion": "mapping-version-1"
            },
            "targetApi": {
                "id": "target-1",
                "apiKey": "target-1",
                "name": "Controlled Target",
                "httpMethod": "POST",
                "path": "/controlled-target",
                "bodyTemplate": {"required": "", "optionalBody": ""},
                "parameterSchema": [
                    {"parameterKey": "body:required", "location": "body", "name": "required", "jsonPath": "required", "dataType": "string", "required": true},
                    {"parameterKey": "body:optionalBody", "location": "body", "name": "optionalBody", "jsonPath": "optionalBody", "dataType": "string", "required": false},
                    {"parameterKey": "query:optionalQuery", "location": "query", "name": "optionalQuery", "jsonPath": null, "dataType": "string", "required": false},
                    {"parameterKey": "header:X-Optional", "location": "header", "name": "X-Optional", "jsonPath": null, "dataType": "string", "required": false}
                ],
                "enabled": true,
                "rowVersion": "target-version-1"
            },
            "facts": [
                {"sourceKey": "line-01", "name": "required", "dataType": "string", "value": "A01"},
                {"sourceKey": "line-01", "name": "optional-header", "dataType": "string", "value": null}
            ],
            "valueRules": []
        }),
        FixtureScenario::RequiredRuleRejected => json!({
            "snapshotId": "snapshot-1",
            "mapping": {
                "id": "mapping-1",
                "mappingKey": "saved-mapping",
                "name": "Saved Mapping",
                "sourceKey": "line-01",
                "targetApiId": "target-1",
                "targetApiKey": "target-1",
                "bindings": {
                    "body:state": {"kind": "fact", "value": null, "sourceKey": "line-01", "factName": "state", "valueRuleKey": "allowed-state"}
                },
                "intervalMs": 1000,
                "enabled": true,
                "rowVersion": "mapping-version-1"
            },
            "targetApi": {
                "id": "target-1",
                "apiKey": "target-1",
                "name": "Controlled Target",
                "httpMethod": "POST",
                "path": "/controlled-target",
                "bodyTemplate": {"state": ""},
                "parameterSchema": [
                    {"parameterKey": "body:state", "location": "body", "name": "state", "jsonPath": "state", "dataType": "string", "required": true}
                ],
                "enabled": true,
                "rowVersion": "target-version-1"
            },
            "facts": [
                {"sourceKey": "line-01", "name": "state", "dataType": "string", "value": "A01"}
            ],
            "valueRules": [
                {"valueRuleKey": "allowed-state", "dataType": "string", "values": ["B05"]}
            ]
        }),
    }
}

fn read_request(stream: &mut TcpStream) -> CapturedRequest {
    stream
        .set_read_timeout(Some(Duration::from_secs(2)))
        .expect("fixture must set a read timeout");
    let mut bytes = Vec::new();
    let mut buffer = [0_u8; 4096];
    let header_end = loop {
        let read = stream
            .read(&mut buffer)
            .expect("fixture request must be readable");
        assert!(read > 0, "fixture request ended before headers");
        bytes.extend_from_slice(&buffer[..read]);
        if let Some(index) = find_header_end(&bytes) {
            break index;
        }
    };
    let header_text = String::from_utf8_lossy(&bytes[..header_end]);
    let mut lines = header_text.lines();
    let request_line = lines.next().expect("fixture request line");
    let mut request_parts = request_line.split_whitespace();
    let method = request_parts
        .next()
        .expect("fixture request method")
        .to_string();
    let path = request_parts
        .next()
        .expect("fixture request path")
        .to_string();
    let headers = lines
        .filter_map(|line| line.split_once(':'))
        .map(|(name, value)| (name.trim().to_ascii_lowercase(), value.trim().to_string()))
        .collect::<Vec<_>>();
    let content_length = headers
        .iter()
        .find(|(name, _)| name == "content-length")
        .and_then(|(_, value)| value.parse::<usize>().ok())
        .unwrap_or(0);
    let body_start = header_end + 4;
    while bytes.len().saturating_sub(body_start) < content_length {
        let read = stream
            .read(&mut buffer)
            .expect("fixture body must be readable");
        assert!(read > 0, "fixture request ended before its body");
        bytes.extend_from_slice(&buffer[..read]);
    }
    CapturedRequest {
        method,
        path,
        headers,
        body: bytes[body_start..body_start + content_length].to_vec(),
    }
}

fn find_header_end(bytes: &[u8]) -> Option<usize> {
    bytes.windows(4).position(|window| window == b"\r\n\r\n")
}

fn write_response(stream: &mut TcpStream, status: u16, body: Value) {
    let body = serde_json::to_vec(&body).expect("fixture response JSON must serialize");
    let reason = if (200..300).contains(&status) {
        "OK"
    } else {
        "Error"
    };
    write!(
        stream,
        "HTTP/1.1 {status} {reason}\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n",
        body.len()
    )
    .expect("fixture response headers must write");
    stream
        .write_all(&body)
        .expect("fixture response body must write");
    stream.flush().expect("fixture response must flush");
}

#[tokio::test]
async fn saved_null_rule_fact_sends_once_and_omits_optional_unresolved_parameters() {
    let (base_url, captured, fixture) = spawn_fixture(FixtureScenario::OptionalOmission, 3);

    let result = run_mapping_manual_once(
        "mapping-1".to_string(),
        "mapping-version-1".to_string(),
        base_url,
    )
    .await
    .expect("controlled run must complete");
    fixture.join().expect("fixture must finish");

    assert_eq!(result.status, "succeeded");
    assert_eq!(result.http_status_class.as_deref(), Some("2xx"));
    assert_eq!(result.resolved_parameter_keys, vec!["body:required"]);
    assert_eq!(
        result.unresolved_parameter_keys,
        vec![
            "body:optionalBody",
            "query:optionalQuery",
            "header:X-Optional",
        ]
    );
    let captured = captured.lock().expect("fixture lock");
    let target_requests = captured
        .iter()
        .filter(|request| request.path.starts_with("/controlled-target"))
        .collect::<Vec<_>>();
    assert_eq!(
        target_requests.len(),
        1,
        "only one target attempt is permitted"
    );
    let target = target_requests[0];
    assert_eq!(target.method, "POST");
    assert_eq!(target.path, "/controlled-target");
    assert!(
        !target.headers.iter().any(|(name, _)| name == "x-optional"),
        "optional unresolved headers must be omitted"
    );
    assert_eq!(
        serde_json::from_slice::<Value>(&target.body).expect("target body JSON"),
        json!({"required": "A01"}),
        "valueRuleKey=null must use the typed fact while optional body values are omitted"
    );
}

#[tokio::test]
async fn required_rule_rejection_completes_preflight_without_target_request() {
    let (base_url, captured, fixture) = spawn_fixture(FixtureScenario::RequiredRuleRejected, 2);

    let result = run_mapping_manual_once(
        "mapping-1".to_string(),
        "mapping-version-1".to_string(),
        base_url,
    )
    .await
    .expect("preflight rejection must be auditable");
    fixture.join().expect("fixture must finish");

    assert_eq!(result.status, "preflight_rejected");
    assert_eq!(
        result.error_code.as_deref(),
        Some("tss_mapping_manual_run_required_unresolved")
    );
    assert_eq!(result.unresolved_parameter_keys, vec!["body:state"]);
    assert_eq!(
        result.diagnostics[0].error_code,
        "tss_mapping_manual_run_value_rule_rejected"
    );
    let captured = captured.lock().expect("fixture lock");
    assert_eq!(
        captured
            .iter()
            .filter(|request| request.path.starts_with("/controlled-target"))
            .count(),
        0,
        "required unresolved parameters must suppress all target requests"
    );
}
