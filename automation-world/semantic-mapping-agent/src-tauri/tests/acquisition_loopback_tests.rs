//! SMA-008 r3：真实原生服务与一次提交、复制回执及保守的只读回读。
use aiis_semantic_mapping_agent_lib::{
    contracts::{
        acquisition::{LoopbackConfig, Point},
        local_configuration::ChangeIntent,
    },
    domain::{acquisition as domain, runtime::ManagedRuntimeState},
    services::{acquisition as flow, local_configuration::LocalConfigurationService},
};
use serde::{Deserialize, Serialize};
use serde_json::{
    json,
    value::{to_raw_value, RawValue},
    Value,
};
use std::{
    io::{BufRead, BufReader, Read, Write},
    net::{TcpListener, TcpStream},
    path::PathBuf,
    sync::{Arc, Mutex},
};

const SOURCE: &str = "fixture-external";
const FROM: &str = "2026-11-20T12:00:00+08:00";
const TO: &str = "2026-11-20T12:02:00+08:00";
const OLD: &str = "2026-11-20T12:00:10.123456+08:00";
const NEW: &str = "2026-11-20T12:00:30.000000+08:00";
const BELOW: &str = "340282356779733661637539395458142568447";
const MIDPOINT: &str = "340282356779733661637539395458142568448";
const ABOVE: &str = "340282356779733661637539395458142568449";

fn raw(value: &impl Serialize) -> Box<RawValue> {
    to_raw_value(value).unwrap()
}

fn real(id: &str, number: &str) -> Point {
    Point {
        point_id: id.into(),
        name: id.into(),
        data_type: "REAL".into(),
        value: RawValue::from_string(number.into()).unwrap(),
        quality: "good".into(),
        reason: None,
        observed_at: OLD.into(),
    }
}

fn fixture_points() -> Vec<Point> {
    let mut result: Vec<Point> = points()
        .iter()
        .map(|point| serde_json::from_str(&point.to_string()).unwrap())
        .collect();
    result.extend([
        real("edge-positive", BELOW),
        real("edge-negative", &format!("-{BELOW}")),
        real("signed-zero", "-0"),
    ]);
    result
}

#[derive(Serialize)]
struct PointsData<'a> {
    #[serde(flatten)]
    summary: Value,
    points: &'a [Point],
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct LatestPoint {
    #[serde(flatten)]
    point: Point,
    sample_id: &'static str,
    source_type: &'static str,
}

#[derive(Serialize)]
struct ItemsData<T> {
    items: Vec<T>,
}

#[derive(Serialize)]
struct FixtureEnvelope {
    code: u16,
    data: Box<RawValue>,
}

fn configuration(material: &str) -> LoopbackConfig {
    serde_json::from_value(json!({
        "materialKey":material,"plcId":SOURCE,"dbNumber":21,"pointIds":["temp","switch","edge-positive","edge-negative","signed-zero"],
        "target":{"plcId":SOURCE,"dbNumber":61421,"instanceId":"sma-fixture","sourceGeneration":"gen-fixture"},
        "moves":[{"from":"temp","to":"test-temp","name":"Test temperature"}],
        "groupId":"mapping-fixture","configRevision":null
    })).unwrap()
}

fn points() -> Vec<Value> {
    vec![
        json!({"pointId":"temp","name":"Temperature","value":0,"dataType":"DINT","quality":"good","observedAt":OLD}),
        json!({"pointId":"switch","name":"Switch","value":false,"dataType":"BOOL","quality":"good","observedAt":OLD}),
        json!({"pointId":"invalid","name":"Unavailable","value":null,"dataType":"REAL","quality":"bad","reason":"fixture stale","observedAt":NEW}),
    ]
}

#[test]
fn sequence_type_numeric_precision_and_target_rules_fail_closed() {
    assert!(domain::sequence("1"));
    assert!(domain::sequence("9223372036854775806"));
    for value in ["", "0", "+1", "01", "-1", "1.0", "9223372036854775807"] {
        assert!(!domain::sequence(value));
    }
    let mut cfg = configuration("fixture");
    let mut invalid = points();
    invalid[1]["value"] = json!("false");
    assert!(domain::point_data(&invalid.iter().map(raw).collect::<Vec<_>>()).is_err());
    cfg.target.db_number = cfg.db_number;
    assert_eq!(
        domain::validate_config(&cfg).unwrap_err(),
        "SMA_ACQUISITION_TARGET_EQUALS_SOURCE"
    );
    cfg.target.db_number = 61421;
    cfg.point_ids = vec!["temp".into()];
    let long = "12.3456789012345678901234";
    let sample = domain::body(
        &cfg,
        domain::point_data(&[raw(&real("temp", long))]).unwrap(),
        "fixture-id",
        "5",
    )
    .unwrap();
    assert!(String::from_utf8_lossy(&sample.bytes).contains(long));
    assert_eq!(sample.sampled_at, OLD);
}

#[test]
fn real_binary32_rounds_directly_and_keeps_number_tokens() {
    let mut cfg = configuration("fixture");
    cfg.point_ids.clear();
    let accepted = [
        real("pos", BELOW),
        real("neg", &format!("-{BELOW}")),
        real("negative-zero", "-0"),
    ];
    let parsed = domain::point_data(&accepted.iter().map(raw).collect::<Vec<_>>()).unwrap();
    let sample = domain::body(&cfg, parsed, "fixture-id", "5").unwrap();
    let wire: Captured = serde_json::from_slice(&sample.bytes).unwrap();
    for (sent, source) in wire.points.iter().zip(&accepted) {
        assert_eq!(sent.value.get(), source.value.get());
    }
    for out_of_range in [MIDPOINT, ABOVE] {
        for number in [out_of_range.to_string(), format!("-{out_of_range}")] {
            assert!(
                domain::point_data(&[raw(&real("overflow", &number))]).is_err(),
                "{number}"
            );
        }
    }
}

struct Profile(PathBuf);
impl Drop for Profile {
    fn drop(&mut self) {
        let _ = std::fs::remove_dir_all(&self.0);
    }
}

#[derive(Default)]
struct FixtureState {
    posted: Vec<Vec<u8>>,
    target: Option<Captured>,
    mode: String,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct Captured {
    sample_id: String,
    source_seq: String,
    points: Vec<Point>,
}

fn request(connection: &mut TcpStream) -> (String, Vec<u8>) {
    let mut reader = BufReader::new(connection);
    let mut first = String::new();
    reader.read_line(&mut first).unwrap();
    let mut len = 0;
    loop {
        let mut header = String::new();
        reader.read_line(&mut header).unwrap();
        if header == "\r\n" || header.is_empty() {
            break;
        }
        let lowered = header.to_ascii_lowercase();
        assert!(!lowered.starts_with("authorization:"));
        if let Some(value) = lowered.strip_prefix("content-length:") {
            len = value.trim().parse::<usize>().unwrap();
        }
    }
    let mut body = vec![0; len];
    reader.read_exact(&mut body).unwrap();
    (first, body)
}

fn serve(listener: TcpListener, state: Arc<Mutex<FixtureState>>) {
    for stream in listener.incoming() {
        let mut stream = stream.unwrap();
        let (first, body) = request(&mut stream);
        let mut state = state.lock().unwrap();
        let data = if first.starts_with("GET /api/v1/acquisition-data/options ") {
            raw(&json!({"items":[{"plcId":SOURCE,"dbNumbers":[21]}]}))
        } else if first.starts_with("GET /api/v1/acquisition-data/latest?") {
            let items = fixture_points()
                .into_iter()
                .enumerate()
                .map(|(index, point)| LatestPoint {
                    point,
                    sample_id: if index == 2 { "later" } else { "earlier" },
                    source_type: "external",
                })
                .collect();
            raw(&ItemsData { items })
        } else if first.starts_with("GET /api/v1/acquisition-data/history/1 ") {
            raw(&PointsData {
                summary: json!({"id":"1","sampleId":"manual-source","plcId":SOURCE,"dbNumber":21,"instanceId":"fixture-source","sampledAt":NEW,
                    "pointCount":6,"sourceType":"external"}),
                points: &fixture_points(),
            })
        } else if first.starts_with("GET /api/v1/acquisition-data/history/2 ") {
            let target = state.target.as_ref().unwrap();
            raw(&PointsData {
                summary: json!({"id":"2","sampleId":target.sample_id,"plcId":SOURCE,"dbNumber":61421,"instanceId":"sma-fixture",
                    "sampledAt":OLD,"pointCount":5,"sourceType":"external"}),
                points: &target.points,
            })
        } else if first.starts_with("GET /api/v1/acquisition-data/history?") {
            let row = if first.contains("dbNumber=61421") {
                assert!(
                    first.contains("12%3A00%3A09") && first.contains("12%3A00%3A11"),
                    "{first}"
                );
                let target = state.target.as_ref().unwrap();
                json!({"id":"2","sampleId":target.sample_id,"plcId":SOURCE,"dbNumber":61421,"instanceId":"sma-fixture","sampledAt":OLD,"pointCount":5})
            } else {
                json!({"id":"1","sampleId":"manual-source","plcId":SOURCE,"dbNumber":21,"instanceId":"fixture-source","sampledAt":NEW,"pointCount":6})
            };
            raw(&json!({"items":[row],"page":1,"total":1,"totalPages":1}))
        } else if first.starts_with("POST /api/v1/integration/plc-facts/samples ") {
            let input: Captured = serde_json::from_slice(&body).unwrap();
            if state.mode == "reject" {
                state.posted.push(body);
                let error =
                    "{\"code\":409,\"data\":null,\"errorCode\":\"plc_facts_v2.identity_conflict\"}";
                write!(stream,"HTTP/1.1 409 Conflict\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{error}",error.len()).unwrap();
                continue;
            }
            let outcome = if state.posted.is_empty() {
                "created"
            } else {
                "duplicate"
            };
            let receipt = raw(
                &json!({"contractVersion":"plc-facts/v2","instanceId":"sma-fixture","sampleId":input.sample_id,"status":"committed","outcome":outcome}),
            );
            state.posted.push(body);
            state.target = Some(input);
            if state.posted.len() == 1 {
                // Store the first attempt, then drop the connection before its receipt.
                continue;
            }
            receipt
        } else {
            panic!("unexpected fixture request: {first}");
        };
        let reply = serde_json::to_string(&FixtureEnvelope { code: 200, data }).unwrap();
        write!(
            stream,
            "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{reply}",
            reply.len()
        )
        .unwrap();
    }
}

#[tokio::test]
async fn options_history_selected_oldest_write_once_retry_readback_and_sqlite() {
    let listener = TcpListener::bind("127.0.0.1:0").unwrap();
    let port = listener.local_addr().unwrap().port();
    let state = Arc::new(Mutex::new(FixtureState::default()));
    let worker = state.clone();
    std::thread::spawn(move || serve(listener, worker));
    let profile =
        Profile(std::env::temp_dir().join(format!("sma008-test-{}", uuid::Uuid::new_v4())));
    std::fs::create_dir(&profile.0).unwrap();
    let env = profile.0.join("fixture.env");
    std::fs::write(&env, "SMA_HTTP_ENABLED=true\n").unwrap();
    std::env::set_var("SMA_ENV_FILE", &env);
    std::env::remove_var("SMA_HTTP_ENABLED");
    let log_path = profile.0.join("service.log");
    let writer = std::fs::File::create(&log_path).unwrap();
    let subscriber = tracing_subscriber::fmt()
        .with_ansi(false)
        .with_writer(writer)
        .finish();
    let _trace = tracing::subscriber::set_default(subscriber);
    let database = profile.0.join("configuration.sqlite3");
    let local = LocalConfigurationService::new(Ok(database.clone()));
    let old_json = local.export().unwrap();
    assert!(!old_json.contains("acquisitionLoopback"));
    let runtime = ManagedRuntimeState::new("api_first_mapping");
    local
        .change(
            0,
            ChangeIntent {
                kind: "connection".into(),
                resource: "connection".into(),
                id: None,
                payload: json!({"scheme":"http","host":"127.0.0.1","port":port}),
            },
            &runtime,
        )
        .unwrap();
    let catalog = ChangeIntent {
        kind: "catalog".into(),
        resource: "catalog".into(),
        id: None,
        payload: json!([{
            "method":"GET","path":domain::LATEST,"summary":"Latest","operationId":"latest","operationSnapshot":{},
            "requestContract":[],"bodyTemplate":{},"normalizationStatus":"ready","normalizationErrorCode":null,
            "jsonTemplate":"{}","contentHash":"fixture","sourceLocator":"file:fixture.json"
        }]),
    };
    let token = local.preview(1, catalog.clone()).unwrap();
    local
        .apply(1, catalog, &token.token, false, &runtime)
        .unwrap();
    let selected = local
        .change(
            2,
            ChangeIntent {
                kind: "selection".into(),
                resource: "materials".into(),
                id: None,
                payload: json!([format!("GET {}", domain::LATEST)]),
            },
            &runtime,
        )
        .unwrap();
    let key = selected.document.materials[0]["materialKey"]
        .as_str()
        .unwrap();
    let cfg = configuration(key);
    let snapshot = local.save_acquisition_loopback(3, cfg.clone()).unwrap();
    let revision = snapshot.revision;
    let bytes_before = std::fs::read(&database).unwrap();
    let session = flow::AcquisitionSession::default();
    assert_eq!(
        flow::options(&snapshot).await.unwrap()["items"][0]["dbNumbers"][0],
        21
    );
    let latest = flow::latest(&snapshot, key, SOURCE, 21, &[]).await.unwrap();
    assert_eq!(latest["items"][0]["valueText"], "0");
    assert_eq!(latest["items"][1]["valueText"], "false");
    assert_eq!(latest["items"][2]["quality"], "bad");
    assert_eq!(latest["items"][3]["valueText"], BELOW);
    assert_eq!(latest["items"][4]["valueText"], format!("-{BELOW}"));
    assert_eq!(latest["items"][5]["valueText"], "-0");
    assert_eq!(
        flow::latest(&snapshot, key, SOURCE, 21, &["switch".into()])
            .await
            .unwrap()["items"]
            .as_array()
            .unwrap()
            .len(),
        1
    );
    assert!(state.lock().unwrap().posted.is_empty());
    assert!(flow::push(&session, &local, "missing").await.is_err());
    assert_eq!(
        flow::history(&snapshot, key, SOURCE, 21, FROM, TO, 1)
            .await
            .unwrap()["items"][0]["id"],
        "1"
    );
    let detail = flow::sample(&snapshot, key, "1", SOURCE, 21).await.unwrap();
    assert_eq!(detail["sampleId"], "manual-source");
    assert_eq!(detail["points"][3]["valueText"], BELOW);
    assert_eq!(detail["points"][4]["valueText"], format!("-{BELOW}"));
    assert_eq!(detail["points"][5]["valueText"], "-0");
    let pending = flow::preview(&session, &local, "1", "9223372036854775806", revision)
        .await
        .unwrap();
    let pending: Value = serde_json::to_value(pending).unwrap();
    assert_eq!(pending["sampledAt"], OLD);
    assert!(state.lock().unwrap().posted.is_empty());
    let handle = pending["id"].as_str().unwrap();
    let id = pending["sampleId"].as_str().unwrap();
    assert!(
        flow::push(&session, &local, handle)
            .await
            .unwrap_err()
            .unknown
    );
    assert!(
        flow::push(&flow::AcquisitionSession::default(), &local, handle)
            .await
            .is_err()
    );
    let ack = flow::push(&session, &local, handle).await.unwrap();
    assert_eq!(ack["receipt"]["outcome"], "duplicate");
    let read = flow::readback(&session, &local, handle).await.unwrap();
    assert_eq!(read["sampleId"], id);
    assert_eq!(read["points"][0]["pointId"], "test-temp");
    assert_eq!(read["points"][1]["valueText"], "false");
    assert_eq!(read["points"][2]["valueText"], BELOW);
    assert_eq!(read["points"][3]["valueText"], format!("-{BELOW}"));
    assert_eq!(read["points"][4]["valueText"], "-0");
    assert_eq!(read["points"][1]["observedAt"], OLD);
    {
        let state = state.lock().unwrap();
        assert_eq!(state.posted.len(), 2);
        assert_eq!(state.posted[0], state.posted[1]);
        assert_eq!(
            state.posted[0],
            pending["body"].as_str().unwrap().as_bytes()
        );
        let stored = state.target.as_ref().unwrap();
        assert_eq!(stored.source_seq, "9223372036854775806");
        assert_eq!(stored.points[2].value.get(), BELOW);
        assert_eq!(stored.points[3].value.get(), format!("-{BELOW}"));
        assert_eq!(stored.points[4].value.get(), "-0");
    }
    assert!(flow::push(&session, &local, handle).await.is_err());
    assert_eq!(bytes_before, std::fs::read(&database).unwrap());
    let exported = local.export().unwrap();
    assert!(!exported.contains(id) && !exported.contains(OLD) && !exported.contains("committed"));
    let logs = std::fs::read_to_string(log_path).unwrap();
    assert!(logs.contains("sma_configuration_open"));
    assert!(!logs.contains(id) && !logs.contains(OLD) && !logs.contains("contractVersion"));
    assert_eq!(
        LocalConfigurationService::new(Ok(database.clone()))
            .load()
            .unwrap(),
        snapshot
    );

    let stale = serde_json::to_value(
        flow::preview(&session, &local, "1", "2", revision)
            .await
            .unwrap(),
    )
    .unwrap();
    let stale_id = stale["id"].as_str().unwrap();
    let mut changed = cfg;
    changed.config_revision = Some("changed".into());
    let saved = local.save_acquisition_loopback(revision, changed).unwrap();
    assert!(flow::push(&session, &local, stale_id).await.is_err());
    assert_eq!(state.lock().unwrap().posted.len(), 2);

    state.lock().unwrap().mode = "reject".into();
    let rejected = serde_json::to_value(
        flow::preview(&session, &local, "1", "1", saved.revision)
            .await
            .unwrap(),
    )
    .unwrap();
    let handle = rejected["id"].as_str().unwrap();
    let rejected = flow::push(&session, &local, handle).await.unwrap_err();
    assert_eq!(rejected.status, Some(409));
    assert!(!rejected.unknown);
    assert!(flow::push(&session, &local, handle).await.is_err());
    std::fs::write(&env, "SMA_HTTP_ENABLED=false\n").unwrap();
    assert!(flow::options(&snapshot).await.is_err());
    assert_eq!(state.lock().unwrap().posted.len(), 3);
}

#[tokio::test]
#[ignore = "requires the existing local dev API and its manually prepared test source; GET only"]
async fn dev_get_only() {
    let config = serde_json::from_value(json!({
        "schemaVersion":1, "revision":0, "updatedAt":"2026-11-20T00:00:00+08:00",
        "document":{"connection":{"scheme":"http","host":"127.0.0.1","port":8000},
        "catalog":[],"materials":[{"materialKey":"native-dev-get","httpMethod":"GET","path":domain::LATEST}],
        "targetApis":[],"mappingValueRules":[],"mappings":[],"sourceMetadata":[]}
    })).unwrap();
    let plc = "PLC-BE012-DEV-441247C3";
    let key = "native-dev-get";
    let result = flow::options(&config).await.unwrap();
    assert!(result["items"]
        .as_array()
        .unwrap()
        .iter()
        .any(|option| option["plcId"] == plc
            && option["dbNumbers"].as_array().unwrap().contains(&json!(21))));
    let all = flow::latest(&config, key, plc, 21, &[]).await.unwrap();
    assert!(all["items"].as_array().unwrap().len() >= 2);
    let one = flow::latest(&config, key, plc, 21, &["heating_ready".into()])
        .await
        .unwrap();
    assert_eq!(one["items"][0]["valueText"], "false");
    let two = flow::latest(
        &config,
        key,
        plc,
        21,
        &["furnace_temp".into(), "heating_ready".into()],
    )
    .await
    .unwrap();
    assert_eq!(two["items"].as_array().unwrap().len(), 2);
    let history = flow::history(
        &config,
        key,
        plc,
        21,
        "2026-11-10T21:55:00+08:00",
        "2026-11-10T22:00:00+08:00",
        1,
    )
    .await
    .unwrap();
    assert!(history["items"]
        .as_array()
        .unwrap()
        .iter()
        .any(|row| row["id"] == "1"));
    let item = flow::sample(&config, key, "1", plc, 21).await.unwrap();
    assert_eq!(item["sampleId"], "be012-dev-441247c3-102");
    assert_eq!(item["points"].as_array().unwrap().len(), 2);
}
