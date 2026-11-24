//! 单节点测试的目标解析、执行确认、调用和审计记录。
use super::ca_workspace::{point_kind, Pending, Workspace};
use crate::domain::plc::PlcEndpointProbeSnapshot;
use crate::domain::{
    ca_catalog::Connection,
    ca_flow::{id, valid_path, Document, Kind, Literal, Method, Node, NodeBody, Operand},
};
use crate::infrastructure::rust_snap7_adapter::read_db_block;
use chrono::{FixedOffset, Utc};
use reqwest::{blocking::Client, redirect::Policy, Url};
use serde::Deserialize;
use serde_json::{json, Value};
use std::{
    collections::BTreeMap,
    io::Read,
    time::{Duration, Instant},
};
use uuid::Uuid;

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct Intent {
    pub flow_id: String,
    pub revision: u32,
    pub node: Node,
    pub document: Document,
    #[serde(default)]
    pub real: bool,
    pub timeout_ms: u32,
    #[serde(default)]
    pub inputs: BTreeMap<String, Literal>,
    pub sample: Option<Literal>,
    pub fake_outcome: Option<FakeOutcome>,
}
#[derive(Clone, Copy, Deserialize)]
#[serde(rename_all = "snake_case")]
pub(crate) enum FakeOutcome {
    Success,
    BeforeSend,
    Unknown,
}
enum Request {
    Simulate(Value),
    Http {
        method: Method,
        url: Url,
        headers: BTreeMap<String, String>,
        body: Option<Value>,
    },
    Read {
        connection: Connection,
        db: u16,
        byte: u32,
    },
}
pub(crate) struct Prepared {
    generation: u64,
    request: Request,
    summary: Value,
    outcome: FakeOutcome,
    timeout: Duration,
}
fn operand(value: &Operand, inputs: &BTreeMap<String, Literal>) -> Result<Literal, String> {
    let literal = match value {
        Operand::Value(literal) => literal,
        Operand::Ref(r) => inputs
            .get(&format!("{}.{}", r.node_id, r.field))
            .ok_or("test_input_missing")?,
    };
    if !literal.kind.valid(&literal.value) {
        return Err("test_input_invalid".into());
    }
    Ok(literal.clone())
}
fn values(
    values: &BTreeMap<String, Operand>,
    inputs: &BTreeMap<String, Literal>,
) -> Result<BTreeMap<String, Value>, String> {
    if values.len() > 64 || values.keys().any(|key| key.is_empty() || key.len() > 100) {
        return Err("test_parameters_invalid".into());
    }
    values
        .iter()
        .map(|(key, value)| Ok((key.clone(), operand(value, inputs)?.value)))
        .collect()
}
fn check_refs(intent: &Intent) -> Result<(), String> {
    let refs: Vec<_> = match &intent.node.body {
        NodeBody::Http(node) => node.query.values().chain(node.body.values()).collect(),
        NodeBody::Compare(node) => vec![&node.left],
        NodeBody::Write(node) => vec![&node.value],
        _ => Vec::new(),
    };
    let mut upstream = None;
    for r in refs.into_iter().filter_map(|operand| match operand {
        Operand::Ref(r) => Some(r),
        _ => None,
    }) {
        let expected = upstream
            .get_or_insert_with(|| {
                intent
                    .document
                    .flow
                    .guaranteed_upstream_nodes(&intent.node.id)
            })
            .get(r.node_id.as_str())
            .and_then(|node| node.output(&r.field))
            .ok_or("test_reference_invalid")?;
        if intent
            .inputs
            .get(&format!("{}.{}", r.node_id, r.field))
            .is_some_and(|value| value.kind != expected)
        {
            return Err("test_input_invalid".into());
        }
    }
    Ok(())
}
fn stamp() -> String {
    Utc::now()
        .with_timezone(&FixedOffset::east_opt(8 * 3600).expect("UTC+8"))
        .to_rfc3339()
}
pub(crate) fn preview(workspace: &Workspace, intent: Intent) -> Result<Value, String> {
    if !id(&intent.flow_id)
        || !id(&intent.node.id)
        || intent.node.version != 1
        || intent.revision == 0
        || !(100..=10_000).contains(&intent.timeout_ms)
        || intent.inputs.len() > 64
        || (!workspace.fake && intent.fake_outcome.is_some())
    {
        return Err("test_intent_invalid".into());
    }
    if intent.document.flow.flow_id != intent.flow_id
        || intent.document.flow.revision != intent.revision
        || intent.document.flow.nodes.len() > 256
        || intent.document.flow.edges.len() > 512
        || !intent
            .document
            .flow
            .nodes
            .iter()
            .any(|node| node == &intent.node)
    {
        return Err("test_intent_invalid".into());
    }
    check_refs(&intent)?;
    let data = workspace.snapshot()?;
    let mut summary = json!({
        "flow_id":intent.flow_id,"revision":intent.revision,"node_id":intent.node.id,"node_version":intent.node.version,
        "mode":if !intent.real {"simulate"} else if workspace.fake {"fake"} else {"real"},
        "confirmation_required":intent.real,"actual_io":false,
        "timeout_ms":intent.timeout_ms,"side_effect":false,"inputs":intent.inputs
    });
    let request = match &intent.node.body {
        NodeBody::Http(h) => {
            if !valid_path(&h.path)
                || !id(&h.endpoint_ref)
                || (h.method == Method::Get && !h.body.is_empty())
            {
                return Err("test_parameters_invalid".into());
            }
            let bind = data
                .http
                .get(&h.endpoint_ref)
                .ok_or("test_binding_missing")?;
            let base = Url::parse(&bind.base_url).map_err(|_| "test_target_invalid")?;
            let mut url = base.join(&h.path).map_err(|_| "test_target_invalid")?;
            if url.origin() != base.origin()
                || !url.username().is_empty()
                || url.password().is_some()
            {
                return Err("test_target_invalid".into());
            }
            let query = values(&h.query, &intent.inputs)?;
            for (key, value) in &query {
                url.query_pairs_mut().append_pair(
                    key,
                    &value
                        .as_str()
                        .map(str::to_owned)
                        .unwrap_or_else(|| value.to_string()),
                );
            }
            let body = if h.method == Method::Post {
                Some(json!(values(&h.body, &intent.inputs)?))
            } else {
                None
            };
            let target = format!("{}{}", base.origin().ascii_serialization(), url.path());
            summary["target"] = json!({"resource":h.endpoint_ref,"url":target,"method":h.method,
                "query":query,"body":body,"header_names":bind.headers.keys().collect::<Vec<_>>()});
            summary["side_effect"] = json!(h.method == Method::Post);
            if intent.real {
                Request::Http {
                    method: h.method,
                    url,
                    headers: bind.headers.clone(),
                    body,
                }
            } else {
                Request::Simulate(json!({"status":200,"response":null,"quality":"good"}))
            }
        }
        NodeBody::Read(read) => {
            let plc = data
                .catalogs
                .iter()
                .find(|record| record.id == read.plc_ref)
                .ok_or("test_binding_missing")?;
            let (db, point) = plc.point(&read.point_ref).ok_or("test_point_missing")?;
            if point_kind(&point.data_type) != Some(read.value_type) {
                return Err("test_input_invalid".into());
            }
            summary["target"] = json!({"resource":read.plc_ref,"point":point.name,"db":db.number,"byte":point.byte_offset,
                "bit":point.bit,"type":point.data_type,"connection":plc.binding});
            if intent.real {
                if point.data_type != "INT" || !plc.catalog.plc.connection.default_tsap() {
                    return Err("test_point_runtime_unsupported".into());
                }
                let connection = plc.binding.clone().ok_or("test_binding_missing")?;
                Request::Read {
                    connection,
                    db: db.number,
                    byte: point.byte_offset,
                }
            } else {
                let sample = intent.sample.ok_or("test_input_missing")?;
                if sample.kind != read.value_type || !sample.kind.valid(&sample.value) {
                    return Err("test_input_invalid".into());
                }
                Request::Simulate(json!({"value":sample.value,"type":sample.kind,"quality":"good"}))
            }
        }
        NodeBody::Write(write) => {
            if intent.real {
                return Err("test_plc_write_unsupported".into());
            }
            let plc = data
                .catalogs
                .iter()
                .find(|record| record.id == write.plc_ref)
                .ok_or("test_binding_missing")?;
            let (db, point) = plc.point(&write.point_ref).ok_or("test_point_missing")?;
            let value = operand(&write.value, &intent.inputs)?;
            if value.kind != write.value_type || point_kind(&point.data_type) != Some(value.kind) {
                return Err("test_input_invalid".into());
            }
            summary["target"] = json!({"resource":write.plc_ref,"point":write.point_ref,"db":db.number,
                "byte":point.byte_offset,"bit":point.bit,"type":point.data_type});
            Request::Simulate(json!({"simulated_value":value.value}))
        }
        NodeBody::Compare(condition) => {
            if intent.real {
                return Err("test_mode_unsupported".into());
            }
            let left = operand(&condition.left, &intent.inputs)?;
            let right = &condition.right;
            if left.kind != right.kind || !right.kind.valid(&right.value) {
                return Err("test_input_invalid".into());
            }
            let matched = if left.kind == Kind::Real {
                left.value.as_f64() == right.value.as_f64()
            } else {
                left.value == right.value
            };
            Request::Simulate(json!({"matched":matched}))
        }
        NodeBody::End(end) => {
            if intent.real {
                return Err("test_mode_unsupported".into());
            }
            Request::Simulate(json!({"result":end.result}))
        }
    };
    let generation = data.generation;
    drop(data);
    let token = workspace.issue(Pending::Test(Prepared {
        generation,
        request,
        summary: summary.clone(),
        outcome: intent.fake_outcome.unwrap_or(FakeOutcome::Success),
        timeout: Duration::from_millis(u64::from(intent.timeout_ms)),
    }))?;
    summary["token"] = json!(token);
    Ok(summary)
}

type Outcome = Result<Value, (&'static str, &'static str)>;
trait Transport {
    fn call(&self, request: &Request, timeout: Duration) -> Outcome;
}
struct Native;
impl Transport for Native {
    fn call(&self, request: &Request, timeout: Duration) -> Outcome {
        match request {
            Request::Simulate(output) => Ok(output.clone()),
            Request::Read {
                connection,
                db,
                byte,
            } => {
                let endpoint = PlcEndpointProbeSnapshot {
                    host: connection.host.clone(),
                    port: connection.port,
                    rack: u16::from(connection.rack),
                    slot: u16::from(connection.slot),
                    enabled: true,
                    reachable: false,
                    latency_ms: 0,
                    error_message: String::new(),
                };
                let output = read_db_block(&endpoint, *db, *byte, 2, timeout)
                    .map_err(|_| ("failed", "s7_read_failed"))?;
                decode_int(output)
            }
            Request::Http {
                method,
                url,
                headers,
                body,
            } => {
                let client = Client::builder()
                    .redirect(Policy::none())
                    .retry(reqwest::retry::never())
                    .no_proxy()
                    .timeout(timeout)
                    .build()
                    .map_err(|_| ("failed_before_send", "http_client_failed"))?;
                let mut builder = client.request(
                    if *method == Method::Post {
                        reqwest::Method::POST
                    } else {
                        reqwest::Method::GET
                    },
                    url.clone(),
                );
                for (key, value) in headers {
                    builder = builder.header(key, value)
                }
                if let Some(body) = body {
                    builder = builder
                        .header("content-type", "application/json")
                        .body(body.to_string())
                }
                let request = builder
                    .build()
                    .map_err(|_| ("failed_before_send", "http_request_invalid"))?;
                let response = client.execute(request).map_err(|err| {
                    (
                        if err.is_connect() {
                            "failed_before_send"
                        } else if *method == Method::Post {
                            "unknown"
                        } else {
                            "failed"
                        },
                        if err.is_timeout() {
                            "http_timeout"
                        } else {
                            "http_transport_failed"
                        },
                    )
                })?;
                let status = response.status();
                if status.is_redirection() {
                    return Ok(json!({"status":status.as_u16(),"error":"http_redirect_blocked"}));
                }
                let mut raw = Vec::new();
                let output = response.take(32_769).read_to_end(&mut raw);
                Ok(if output.is_err() {
                    json!({"status":status.as_u16(),"error":"http_response_unreadable"})
                } else if raw.len() > 32_768 {
                    json!({"status":status.as_u16(),"error":"http_response_too_large"})
                } else {
                    let text = String::from_utf8_lossy(&raw);
                    let redacted = headers
                        .values()
                        .filter(|value| !value.is_empty())
                        .fold(text.into_owned(), |text, value| {
                            text.replace(value, "[redacted]")
                        });
                    json!({"status":status.as_u16(),"response":redacted})
                })
            }
        }
    }
}
fn decode_int(output: Vec<u8>) -> Outcome {
    let bytes: [u8; 2] = output
        .try_into()
        .map_err(|_| ("failed", "s7_read_size_invalid"))?;
    Ok(json!({"value":i16::from_be_bytes(bytes),"type":"int16","quality":"good"}))
}
struct Fake(FakeOutcome);
impl Transport for Fake {
    fn call(&self, request: &Request, _timeout: Duration) -> Outcome {
        match self.0 {
            FakeOutcome::BeforeSend => Err(("failed_before_send", "fake_before_send")),
            FakeOutcome::Unknown => Err((
                if matches!(
                    request,
                    Request::Http {
                        method: Method::Post,
                        ..
                    }
                ) {
                    "unknown"
                } else {
                    "failed"
                },
                "fake_timeout",
            )),
            FakeOutcome::Success => match request {
                Request::Read { .. } => decode_int(vec![0, 1]),
                Request::Http {
                    method, url, body, ..
                } => Ok(
                    json!({"status":200,"response":{"method":method,"path":url.path(),"body":body}}),
                ),
                Request::Simulate(output) => Ok(output.clone()),
            },
        }
    }
}

pub(crate) fn run(workspace: &Workspace, token: &str, confirmed: bool) -> Result<Value, String> {
    let Pending::Test(prepared) = workspace.consume(token)? else {
        return Err("preview_mismatch".into());
    };
    let real = !matches!(prepared.request, Request::Simulate(_));
    if real && !confirmed {
        return Err("test_confirmation_required".into());
    }
    let action = Uuid::new_v4().to_string();
    let mut result = prepared.summary;
    result["id"] = json!(action);
    result["started_at"] = json!(stamp());
    result["status"] = json!(if matches!(
        prepared.request,
        Request::Http {
            method: Method::Post,
            ..
        }
    ) {
        "sending"
    } else {
        "running"
    });
    result["actual_io"] = json!(real && !workspace.fake);
    workspace.update(|data| {
        if data.generation != prepared.generation {
            return Err("preview_stale".into());
        }
        if data.tests.len() >= 2048 {
            return Err("test_capacity".into());
        }
        data.tests.push(result.clone());
        Ok(())
    })?;
    let start = Instant::now();
    let outcome = match &prepared.request {
        Request::Simulate(output) => Ok(output.clone()),
        _ if workspace.fake => Fake(prepared.outcome).call(&prepared.request, prepared.timeout),
        _ => Native.call(&prepared.request, prepared.timeout),
    };
    result["elapsed_ms"] = json!(start.elapsed().as_millis());
    match outcome {
        Ok(output) => {
            result["status"] = json!(if matches!(prepared.request, Request::Http { .. }) {
                "response_received"
            } else {
                "completed"
            });
            result["output"] = output;
        }
        Err((status, error)) => {
            result["status"] = json!(status);
            result["error"] = json!(error);
            if status == "failed_before_send" {
                result["actual_io"] = json!(false)
            }
        }
    }
    workspace.update(|data| {
        let saved = data
            .tests
            .iter_mut()
            .find(|r| r["id"] == action)
            .ok_or("test_not_found")?;
        *saved = result.clone();
        Ok(())
    })?;
    Ok(result)
}

#[cfg(test)]
#[path = "../../tests/arch_aw009/node_tests.rs"]
mod tests;
