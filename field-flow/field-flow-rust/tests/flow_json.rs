//! 文件：tests/flow_json.rs；独立回环验收、冻结配置、边界预检及原手写流共存。
#![cfg(feature = "test-fixture")]
mod flow_json_support;
use field_flow::{domain::now_ms, fixture::catalog_demo::CatalogFixture, infrastructure::state};
use flow_json_support::*;
use serde_json::{json, Value};
use std::{
    fs,
    net::TcpListener,
    os::unix::fs::symlink,
    path::{Path, PathBuf},
    time::{Duration, Instant},
};

const SAMPLE: &str = include_str!("../flows/demo01.json");
const INSTANCE: &str = "ff-rust-flow-json";
const FIXTURE: &str = env!("CARGO_BIN_EXE_ff-fixture");

fn config(dir: &Path, origin: &str) -> (PathBuf, PathBuf) {
    let flows = dir.join("flows");
    fs::create_dir(&flows).unwrap();
    fs::write(flows.join("demo01.json"), SAMPLE).unwrap();
    let config = dir.join("run.yaml");
    let mut v: Value = serde_yaml::from_str(include_str!("../config/flow-json.yaml")).unwrap();
    v["flow_http_endpoints"][0]["base_url"] = json!(origin);
    v["flow_files"] = json!(["demo01.json"]);
    v["http"]["total_timeout_ms"] = json!(250);
    v["http"]["connect_timeout_ms"] = json!(200);
    v["http"]["pool_wait_ms"] = json!(200);
    write(&config, &v);
    (config, flows)
}

fn spec() -> Value {
    serde_json::from_str(SAMPLE).unwrap()
}

fn ready(ready: bool) -> Value {
    let (id, value, issued, expires) = if ready {
        let now = now_ms();
        (
            json!("test-006"),
            json!(-128),
            json!(now),
            json!(now + 60000),
        )
    } else {
        (Value::Null, Value::Null, Value::Null, Value::Null)
    };
    json!({"schema_version":1,"source_id":"demo01-feed","ready":ready,"command_id":id,
        "value":value,"issued_at_ms":issued,"expires_at_ms":expires})
}

fn validate(dir: &Path, cfg: &Path, flows: &Path) -> (i32, Value) {
    let out = cli(
        &[
            "config",
            "validate",
            "--config",
            cfg.to_str().unwrap(),
            "--flows-dir",
            flows.to_str().unwrap(),
        ],
        dir,
    );
    assert!(
        out.stderr.is_empty(),
        "{}",
        String::from_utf8_lossy(&out.stderr)
    );
    (
        out.status.code().unwrap(),
        serde_json::from_slice(&out.stdout).unwrap(),
    )
}

fn rounds(dir: &Path, label: &str) -> Vec<Value> {
    events(&dir.join(format!("{label}.jsonl")))
        .into_iter()
        .filter(|v| v["event"] == "flow_json_round")
        .map(|v| v["context"].clone())
        .collect()
}

fn finish(dir: &Path, state_dir: &Path, product: Product, label: &str, signal: i32) {
    product.close(signal);
    assert!(events(&dir.join(format!("{label}.jsonl")))
        .iter()
        .any(|v| v["event"] == "runtime_tasks_joined"));
    assert_eq!(state::inspect(state_dir).unwrap()["counts"], json!({}));
    assert!(!fs::read_dir(state_dir).unwrap().any(|entry| entry
        .unwrap()
        .file_name()
        .to_string_lossy()
        .starts_with("gate-")));
}

#[test]
fn shape_selection_and_read_only_preflight() {
    let dir = root();
    let (cfg, flows) = config(&dir, "http://127.0.0.1:34880");
    let sample = flows.join("demo01.json");
    let state_dir = fixture_state(&dir, INSTANCE);
    let before = fs::read(state_dir.join("state.sqlite")).unwrap();
    let absent = cli(
        &["config", "validate", "--config", cfg.to_str().unwrap()],
        &dir,
    );
    assert_eq!(absent.status.code(), Some(2));
    let (code, report) = validate(&dir, &cfg, &flows);
    assert_eq!(code, 0);
    assert_eq!(report["scope"], "main");
    assert_eq!(report["flow_files"][0]["revision"], 1);
    let elsewhere = dir.join("elsewhere");
    fs::create_dir(&elsewhere).unwrap();
    assert_eq!(validate(&elsewhere, &cfg, &flows), (0, report));

    let mut reordered = spec();
    reordered.as_object_mut().unwrap().remove("layout");
    reordered["flow"]["nodes"].as_array_mut().unwrap().reverse();
    reordered["flow"]["edges"].as_array_mut().unwrap().reverse();
    write(&sample, &reordered);
    assert_eq!(validate(&dir, &cfg, &flows).0, 0);

    type Variant = (&'static str, &'static str, fn(&mut Value));
    let variants: &[Variant] = &[
        ("config_flow_node", "flow.entry_node_id", |v| {
            v["flow"]["entry_node_id"] = json!("missing")
        }),
        ("config_fields", "flow.entry_node_id", |v| {
            v["flow"].as_object_mut().unwrap().remove("entry_node_id");
        }),
        ("config_flow_node_type", "flow.edges[2].to_node_id", |v| {
            v["flow"]["edges"][2]["to_node_id"] = json!("fetch")
        }),
        (
            "config_flow_edge",
            "flow.nodes[check].outputs[false]",
            |v| {
                v["flow"]["edges"].as_array_mut().unwrap().pop();
            },
        ),
        ("config_flow_edge", "flow.nodes[fetch].outputs[next]", |v| {
            v["flow"]["edges"].as_array_mut().unwrap().remove(0);
        }),
        ("config_flow_edge", "flow.edges[0].to_node_id", |v| {
            v["flow"]["edges"][0]["to_node_id"] = json!("missing")
        }),
        ("config_flow_edge", "flow.edges[2].to_node_id", |v| {
            v["flow"]["edges"][2]["to_node_id"] = json!("missing")
        }),
        ("config_flow_edge", "flow.edges[1].from_node_id", |v| {
            v["flow"]["edges"][1]["from_node_id"] = json!("missing")
        }),
        ("config_flow_terminal", "flow.edges[2].to_node_id", |v| {
            v["flow"]["edges"][2]["to_node_id"] = json!("yes")
        }),
        (
            "config_flow_terminal",
            "flow.nodes[no].config.result",
            |v| v["flow"]["nodes"][3]["config"]["result"] = json!("matched"),
        ),
        ("config_flow_edge", "flow.edges[2].from_port", |v| {
            v["flow"]["edges"][2]["from_port"] = json!("wrong")
        }),
        (
            "config_flow_condition",
            "flow.nodes[check].config.left.node_id",
            |v| v["flow"]["nodes"][1]["config"]["left"]["node_id"] = json!("yes"),
        ),
        (
            "config_flow_condition",
            "flow.nodes[check].config.right.value",
            |v| v["flow"]["nodes"][1]["config"]["right"]["value"] = json!(1),
        ),
        (
            "config_flow_condition",
            "flow.nodes[check].config.right.type",
            |v| v["flow"]["nodes"][1]["config"]["right"]["type"] = json!("int16"),
        ),
        (
            "config_flow_node_version",
            "flow.nodes[fetch].version",
            |v| v["flow"]["nodes"][0]["version"] = json!(2),
        ),
        ("config_flow_version", "schema_version", |v| {
            v["schema_version"] = json!(2)
        }),
        (
            "config_flow_endpoint",
            "flow.nodes[fetch].config.endpoint_ref",
            |v| v["flow"]["nodes"][0]["config"]["endpoint_ref"] = json!("missing"),
        ),
        ("config_fields", "flow", |v| {
            v["flow"]["extra"] = json!(true)
        }),
    ];
    for (key, path, edit) in variants {
        let mut value = spec();
        edit(&mut value);
        write(&sample, &value);
        let (code, info) = validate(&dir, &cfg, &flows);
        assert_eq!(code, 2, "{path}: {info}");
        assert_eq!(
            info["issues"][0],
            json!({"error_key":key,"path":format!("flow_files[demo01.json].{path}")}),
            "{path}"
        );
    }
    let mut ca_shape = spec();
    ca_shape["flow"]["nodes"][0]["type"] = json!("plc.read");
    ca_shape["flow"]["nodes"]
        .as_array_mut()
        .unwrap()
        .push(json!({"id":"extra","type":"end","version":1,"config":{}}));
    write(&sample, &ca_shape);
    let (_, report) = validate(&dir, &cfg, &flows);
    assert_eq!(
        report["issues"][0],
        json!({"error_key":"config_flow_node_type", "path":"flow_files[demo01.json].flow.nodes[fetch].type"})
    );

    for invalid in [
        "{\"format\":\"aiis.flow\",\"format\":\"aiis.flow\"}".to_string(),
        " ".repeat(65537),
    ] {
        fs::write(&sample, invalid).unwrap();
        assert_eq!(validate(&dir, &cfg, &flows).0, 2);
    }
    fs::remove_file(&sample).unwrap();
    assert_eq!(validate(&dir, &cfg, &flows).0, 2);
    let external = dir.join("external.json");
    fs::write(&external, SAMPLE).unwrap();
    symlink(&external, &sample).unwrap();
    assert_eq!(validate(&dir, &cfg, &flows).0, 2);
    fs::remove_file(&sample).unwrap();
    fs::write(&sample, SAMPLE).unwrap();
    let alias = dir.join("alias");
    symlink(&flows, &alias).unwrap();
    assert_eq!(validate(&dir, &cfg, &alias).0, 2);
    let original: Value = serde_yaml::from_slice(&fs::read(&cfg).unwrap()).unwrap();
    for names in [
        json!(["../external.json"]),
        json!(["demo01.json", "demo01.json"]),
    ] {
        let mut bad = original.clone();
        bad["flow_files"] = names;
        write(&cfg, &bad);
        assert_eq!(validate(&dir, &cfg, &flows).0, 2);
    }
    fs::write(flows.join("other.json"), SAMPLE).unwrap();
    let mut duplicate_id = original;
    duplicate_id["flow_files"] = json!(["demo01.json", "other.json"]);
    write(&cfg, &duplicate_id);
    assert_eq!(validate(&dir, &cfg, &flows).0, 2);
    let output = cli(
        &[
            "run",
            "--config",
            cfg.to_str().unwrap(),
            "--flows-dir",
            flows.to_str().unwrap(),
            "--state-dir",
            state_dir.to_str().unwrap(),
        ],
        &dir,
    );
    assert_eq!(output.status.code(), Some(2));
    assert_eq!(fs::read(state_dir.join("state.sqlite")).unwrap(), before);
    assert!(!state_dir.join("runtime.jsonl").exists());
    fs::remove_dir_all(dir).unwrap();
}

#[test]
fn cli_refreshes_input_and_freezes_revision_until_restart() {
    let dir = root();
    let fixture = HttpFixture::new(vec![
        Response::json(ready(false)),
        Response::json(ready(true)),
    ]);
    let (cfg, flows) = config(&dir, &format!("http://{}", fixture.address));
    let state_dir = dir.join("state");
    let initialized = cli(
        &[
            "state",
            "init",
            "--synthetic",
            "--mode",
            "dry_run",
            "--state-dir",
            state_dir.to_str().unwrap(),
            "--instance-id",
            INSTANCE,
        ],
        &dir,
    );
    assert!(
        initialized.status.success(),
        "{}",
        String::from_utf8_lossy(&initialized.stderr)
    );
    let prod = Product::start(&dir, &cfg, &flows, &state_dir, "first");
    until(|| !rounds(&dir, "first").is_empty());
    let mut updated = spec();
    updated["flow"]["revision"] = json!(2);
    updated["flow"]["nodes"][1]["config"]["right"]["value"] = json!(false);
    updated["flow"]["nodes"].as_array_mut().unwrap().reverse();
    updated.as_object_mut().unwrap().remove("layout");
    write(&flows.join("demo01.json"), &updated);
    until(|| rounds(&dir, "first").len() >= 2);
    let observed = rounds(&dir, "first");
    assert_eq!(observed[0]["result"], "not_matched");
    assert_eq!(observed[1]["result"], "matched");
    assert_ne!(observed[0]["round_id"], observed[1]["round_id"]);
    assert_eq!(observed[0]["sha256"], observed[1]["sha256"]);
    assert_eq!(observed[1]["revision"], 1);
    assert!(observed[1]["observed_at"]
        .as_str()
        .unwrap()
        .ends_with("+08:00"));
    {
        let track = fixture.requests.lock().unwrap();
        assert_eq!(track[0].line, "GET /demo01/command HTTP/1.1");
        assert_eq!(track[1].line, "GET /demo01/command HTTP/1.1");
        assert!(
            track[1]
                .started
                .duration_since(track[0].reply_started.unwrap())
                >= Duration::from_millis(490)
        );
    }
    finish(&dir, &state_dir, prod, "first", libc::SIGTERM);
    let prod = Product::start(&dir, &cfg, &flows, &state_dir, "restart");
    until(|| !rounds(&dir, "restart").is_empty());
    let reloaded = rounds(&dir, "restart");
    assert_eq!(reloaded[0]["result"], "not_matched");
    assert_eq!(reloaded[0]["revision"], 2);
    assert_ne!(reloaded[0]["sha256"], observed[0]["sha256"]);
    finish(&dir, &state_dir, prod, "restart", libc::SIGINT);

    let mut equivalent = spec();
    equivalent["flow"]["nodes"]
        .as_array_mut()
        .unwrap()
        .reverse();
    equivalent["flow"]["edges"]
        .as_array_mut()
        .unwrap()
        .reverse();
    equivalent.as_object_mut().unwrap().remove("layout");
    write(&flows.join("demo01.json"), &equivalent);
    let prod = Product::start(&dir, &cfg, &flows, &state_dir, "equivalent");
    until(|| !rounds(&dir, "equivalent").is_empty());
    let reordered = rounds(&dir, "equivalent");
    assert_eq!(reordered[0]["result"], observed[1]["result"]);
    assert_ne!(reordered[0]["sha256"], observed[1]["sha256"]);
    finish(&dir, &state_dir, prod, "equivalent", libc::SIGTERM);

    assert!(!events(&dir.join("first.jsonl"))
        .iter()
        .any(|v| v["event"].as_str().unwrap_or("").starts_with("plc_")));
    fixture.close();
    println!(
        "FF-006 branch evidence: {observed:?}; reloaded: {reloaded:?}; equivalent: {reordered:?}"
    );
    fs::remove_dir_all(dir).unwrap();
}

#[test]
fn input_errors_are_not_false_and_next_normal_round_recovers() {
    let dir = root();
    let mut responses = Vec::new();
    let mut missing = ready(false);
    missing.as_object_mut().unwrap().remove("value");
    responses.push(Response::json(missing));
    let mut duplicate = Response::json(ready(false));
    duplicate.body = duplicate.body.replacen('{', "{\"ready\":true,", 1);
    responses.push(duplicate);
    for (key, value) in [
        ("source_id", json!("wrong")),
        ("ready", json!(1)),
        ("value", json!(32768)),
        ("command_id", Value::Null),
    ] {
        let mut v = ready(true);
        v[key] = value;
        responses.push(Response::json(v));
    }
    let mut old = ready(true);
    let now = now_ms();
    old["issued_at_ms"] = json!(now - 10000);
    old["expires_at_ms"] = json!(now - 1);
    responses.push(Response::json(old));
    let mut status = Response::json(ready(false));
    status.status = 503;
    responses.push(status);
    let mut html = Response::json(ready(false));
    html.content_type = "text/html";
    responses.push(html);
    let mut timeout = Response::json(ready(false));
    timeout.delay = Duration::from_millis(400);
    responses.push(timeout);
    let expected_count = responses.len();
    responses.push(Response::json(ready(true)));
    let fixture = HttpFixture::new(responses);
    let (cfg, flows) = config(&dir, &format!("http://{}", fixture.address));
    let mut value = spec();
    value["flow"]["trigger"]["interval_ms"] = json!(100);
    write(&flows.join("demo01.json"), &value);
    let state_dir = fixture_state(&dir, INSTANCE);
    let product = Product::start(&dir, &cfg, &flows, &state_dir, "errors");
    until(|| rounds(&dir, "errors").len() > expected_count);
    let observed = rounds(&dir, "errors");
    for row in &observed[..expected_count] {
        assert!(
            row["result"].is_null() && row["error_key"].is_string(),
            "{row}"
        );
    }
    assert_eq!(observed[6]["error_key"], "input_stale");
    assert_eq!(observed[7]["error_key"], "http_status");
    assert_eq!(observed[8]["error_key"], "input_content_type");
    assert!(matches!(
        observed[9]["error_key"].as_str(),
        Some("http_timeout" | "http_communication")
    ));
    assert_eq!(observed[expected_count]["result"], "matched");
    finish(&dir, &state_dir, product, "errors", libc::SIGTERM);
    fixture.close();
    println!("FF-006 rejection/recovery evidence: {observed:?}");
    fs::remove_dir_all(dir).unwrap();
}

#[test]
fn mixed_handwritten_demo_pushes_progress_while_graph_waits() {
    let dir = root();
    for port in [34102, 34103, 34112, 34113, 34880] {
        drop(TcpListener::bind(("127.0.0.1", port)).expect("fixture port available"));
    }
    let mut plc = CatalogFixture::start(Path::new(FIXTURE)).unwrap();
    let command = plc.issue_once().unwrap();
    assert!(command.is_object());
    let mut slow = Response::json(ready(false));
    slow.delay = Duration::from_millis(900);
    let fixture = HttpFixture::new(vec![slow]);
    let (cfg, flows) = config(&dir, &format!("http://{}", fixture.address));
    let original: Value =
        serde_yaml::from_str(include_str!("../config/catalog-demo.yaml")).unwrap();
    fs::create_dir(dir.join("plcs")).unwrap();
    fs::write(
        dir.join("plcs/s7-a.json"),
        include_str!("../config/plcs/s7-a.json"),
    )
    .unwrap();
    let mut combined: Value = serde_yaml::from_slice(&fs::read(&cfg).unwrap()).unwrap();
    combined["plc_files"] = json!(["plcs/s7-a.json"]);
    combined["plc_runtime"] = json!([original["plc_runtime"][0]]);
    let manual = original["flows"]
        .as_array()
        .unwrap()
        .iter()
        .find(|f| f["kind"] == "demo01")
        .unwrap();
    combined["flows"] = json!([manual]);
    combined["http"]["total_timeout_ms"] = json!(1500);
    write(&cfg, &combined);

    let state_dir = fixture_state(&dir, INSTANCE);
    let prod = Product::start(&dir, &cfg, &flows, &state_dir, "mixed");
    let log = dir.join("mixed.jsonl");
    let end = Instant::now() + Duration::from_secs(6);
    let overlap = loop {
        let rows = events(&log);
        let hand = rows.iter().any(|v| {
            v["event"] == "simulated"
                || v["context"]["result"] == "simulated"
                || v["context"]["new"] == "simulated"
        });
        let called = fixture.requests.lock().unwrap().first().is_some();
        if hand && called {
            break rounds(&dir, "mixed").is_empty();
        }
        assert!(
            Instant::now() < end,
            "handwritten command failed to advance; {rows:?}"
        );
        std::thread::sleep(Duration::from_millis(5));
    };
    assert!(
        overlap,
        "manual flow should advance before delayed JSON response"
    );
    until(|| !rounds(&dir, "mixed").is_empty());
    assert_eq!(rounds(&dir, "mixed")[0]["result"], "not_matched");
    prod.close(libc::SIGTERM);
    assert_eq!(
        state::inspect(&state_dir).unwrap()["counts"],
        json!({"simulated":1})
    );
    let report = plc.snapshot();
    println!(
        "FF-006 mixed fixture evidence: GETs {}, sessions {}, reads {}, writes {}",
        report["gets"], report["sessions"], report["reads"], report["writes"]
    );
    assert_eq!(report["writes"], json!([0, 0]));
    assert_eq!(report["reads"], json!([0, 0]));
    assert_eq!(report["sessions"], json!([1, 0]));
    fixture.close();
    plc.close().unwrap();
    fs::remove_dir_all(dir).unwrap();
}
