//! 文件：tests/multi_plc.rs；真实CLI分阶段双PLC、并发隔离、慢HTTP及只读服务身份观察。
#![cfg(feature = "test-fixture")]
mod catalog_support;
use catalog_support::*;
use field_flow::{
    config::runtime_v2::Loaded,
    domain::id,
    fixture::catalog_demo::{CatalogFixture, Options},
    infrastructure::state,
    runtime::Runtime,
};
use serde_json::{json, Value};
use std::{
    collections::HashMap,
    fs,
    path::Path,
    time::{Duration, Instant},
};
fn stats(trace: &Value) -> (usize, u64) {
    let times: Vec<_> = trace
        .as_array()
        .unwrap()
        .iter()
        .filter(|r| r["operation"] == 4)
        .map(|r| r["elapsed_us"].as_u64().unwrap())
        .collect();
    let gap = times.windows(2).map(|w| w[1] - w[0]).max().unwrap_or(0);
    (times.len(), gap)
}
#[test]
fn catalog_cli_matrix() {
    let all = Instant::now();
    let root = root("multi_plc");
    for mode in ["dry_run", "execute"] {
        let mut s = Scene::new(&root, mode, mode, |_| {});
        s.start_fixture(Options::default());
        s.start(mode == "execute");
        until(7, || s.wire_round(&[12, 1, 56, 34]));
        assert_eq!(counts(&s), json!({}));
        let before = s.snapshot();
        assert_eq!(before["writes"], json!([0, 0]));
        assert!(before["gets"].as_u64().unwrap() >= 1);
        assert!(before["trace"][0].as_array().unwrap().iter().filter(|r|r["event"]=="http_complete").all(|r|r["body"]==json!({"schema_version":1,"source_id":"demo01-feed","ready":false,"command_id":null,"value":null,"issued_at_ms":null,"expires_at_ms":null})));
        let body = s.fixture.as_ref().unwrap().issue_once().unwrap();
        assert!(s.fixture.as_ref().unwrap().issue_once().is_err());
        let gets = before["gets"].as_u64().unwrap();
        until(7, || s.snapshot()["gets"].as_u64().unwrap() >= gets + 10);
        until(2, || {
            counts(&s) == json!({if mode=="execute"{"confirmed"}else{"simulated"}:1})
        });
        if mode == "execute" {
            until(3, || s.wire_round(&[42, 1, 56, 34]));
        }
        until(3, || {
            s.rows().iter().any(|r| {
                r["event"] == "points_health"
                    && r["context"]["successful_reads"]
                        .as_u64()
                        .is_some_and(|n| n >= 4)
            })
        });
        let after = s.snapshot();
        assert_eq!(
            after["writes"],
            json!([if mode == "execute" { 1 } else { 0 }, 0])
        );
        let issued = body["issued_at_ms"].as_i64().unwrap();
        assert!(field_flow::domain::now_ms() - issued < 10000);
        let seen: Vec<_> = after["trace"][0]
            .as_array()
            .unwrap()
            .iter()
            .filter(|r| r["event"] == "http_complete" && r["body"]["ready"] == true)
            .collect();
        assert!(seen.len() >= 10);
        assert!(seen.iter().all(|r| r["body"] == body));
        check_raw(&after);
        s.report["pre_issue"] = before;
        s.report["post_issue"] = after;
        s.report["input"] = body;
        s.stop(0);
        s.finish();
        let memory = &s.report["fixture"]["final_memory"];
        assert_eq!(
            memory[0]["memory"]["db1"],
            format!(
                "{}0001{}",
                if mode == "execute" { "002a" } else { "000c" },
                "a5".repeat(12)
            )
        );
        assert_eq!(
            memory[0]["memory"]["db2"],
            format!("0038{}", "a5".repeat(14))
        );
        assert_eq!(
            memory[1]["memory"]["db1"],
            format!("0022{}", "a5".repeat(14))
        );
        s.save();
    }
    for variant in [
        "three_readers",
        "b_off",
        "slow_setup",
        "parallel_io",
        "slow_http",
    ] {
        let mut s = Scene::new(&root, variant, "dry_run", |v| {
            let a = read_flow(
                "a_only",
                json!(["s7_a"]),
                json!([{"device_id":"s7_a","point_id":"value"}]),
            );
            match variant {
                "three_readers" => {
                    v["flows"] = json!((0..3)
                        .map(|i| read_flow(
                            &format!("reader{i}"),
                            json!(["s7_a"]),
                            json!([{"device_id":"s7_a","point_id":"value"}])
                        ))
                        .collect::<Vec<_>>());
                }
                "b_off" | "slow_setup" => {
                    v["flows"] = json!([v["flows"][0].clone(), a]);
                }
                "parallel_io" => {
                    v["flows"] = json!([
                        a,
                        read_flow(
                            "b_only",
                            json!(["s7_b"]),
                            json!([{"device_id":"s7_b","point_id":"value"}])
                        )
                    ]);
                }
                _ => {
                    v["flows"] = json!([v["flows"][1].clone(), a]);
                }
            }
        });
        s.start_fixture(Options {
            b_off: variant == "b_off",
            slow_setup: variant == "slow_setup",
            io_delay_ms: if variant == "parallel_io" { 120 } else { 0 },
            http_delay_ms: if variant == "slow_http" { 1200 } else { 0 },
            short_write_ack_once: false,
        });
        s.start(false);
        until(7, || {
            let rows = s.rows();
            let expected: Vec<String> = if variant == "three_readers" {
                (0..3).map(|i| format!("reader{i}")).collect()
            } else {
                vec!["a_only".into()]
            };
            expected.iter().all(|flow| {
                rows.iter().any(|r| {
                    r["event"] == "points_health"
                        && r["context"]["flow_id"] == *flow
                        && r["context"]["successful_reads"]
                            .as_u64()
                            .is_some_and(|n| n >= 20)
                })
            })
        });
        if matches!(variant, "b_off" | "slow_setup" | "slow_http") {
            let end = Instant::now() + Duration::from_secs(3);
            while Instant::now() < end {
                std::thread::sleep(Duration::from_millis(5));
            }
        }
        let snap = s.snapshot();
        assert_eq!(snap["writes"], json!([0, 0]));
        let (n, gap) = stats(&snap["trace"][0]);
        assert!(n >= 20);
        if variant != "parallel_io" {
            assert!(gap <= 500000, "gap {gap}");
        }
        if variant == "three_readers" {
            let rows = s.rows();
            for i in 0..3 {
                assert!(rows.iter().any(|r| r["event"] == "points_health"
                    && r["context"]["flow_id"] == format!("reader{i}")
                    && r["context"]["successful_reads"]
                        .as_u64()
                        .is_some_and(|n| n >= 20)));
            }
            assert_eq!(snap["sessions"][0], 1);
        }
        if variant == "b_off" {
            s.normal = false;
            assert_eq!(snap["reads"][1], 0);
            assert_eq!(snap["sessions"][1], 0);
            assert!(s.rows().iter().any(|r| r["event"] == "flow_health"
                && r["context"]["flow_id"] == "read_pair"
                && r["context"]["error_key"] == "plc_unavailable"));
        }
        if variant == "slow_setup" {
            let a = snap["trace"][0]
                .as_array()
                .unwrap()
                .iter()
                .find(|r| r["operation"] == 4)
                .unwrap()["sequence"]
                .as_u64()
                .unwrap();
            let b = snap["trace"][1]
                .as_array()
                .unwrap()
                .iter()
                .find(|r| r["operation"] == 240)
                .unwrap()["sequence"]
                .as_u64()
                .unwrap();
            assert!(a < b);
            assert!(s
                .rows()
                .iter()
                .any(|r| r["event"] == "driver_ready" && r["context"]["target_id"] == "s7_b"));
        }
        if variant == "parallel_io" {
            let ta = snap["trace"][0].as_array().unwrap();
            let tb = snap["trace"][1].as_array().unwrap();
            assert!(ta.iter().filter(|r| r["operation"] == 4).any(|a| tb
                .iter()
                .filter(|r| r["operation"] == 4)
                .any(
                    |b| a["started_us"].as_u64().unwrap() < b["elapsed_us"].as_u64().unwrap()
                        && b["started_us"].as_u64().unwrap() < a["elapsed_us"].as_u64().unwrap()
                )));
        }
        if variant == "slow_http" {
            let t = snap["trace"][0].as_array().unwrap();
            let start = t.iter().find(|r| r["event"] == "http_enter").unwrap()["elapsed_us"]
                .as_u64()
                .unwrap();
            let end = t.iter().find(|r| r["event"] == "http_complete").unwrap()["elapsed_us"]
                .as_u64()
                .unwrap();
            assert!(t.iter().any(|r| r["operation"] == 4
                && r["elapsed_us"]
                    .as_u64()
                    .is_some_and(|n| n > start && n < end)));
        }
        s.report["product_window"] = snap;
        s.stop(if variant == "b_off" { 1 } else { 0 });
        if variant == "b_off" {
            let rows = s.rows();
            let forced_rows: Vec<_> = rows
                .iter()
                .filter(|r| {
                    forced(r) && r["event"] != "health" && r["event"] != "shutdown_incomplete"
                })
                .collect();
            assert!(!forced_rows.is_empty());
            assert!(forced_rows
                .iter()
                .all(|r| r["context"]["target_id"] == "s7_b"));
            assert!(
                !rows
                    .iter()
                    .any(|r| r["event"] == "forced_driver_stop"
                        && r["context"]["target_id"] == "s7_a")
            );
        }
        s.finish();
    }
    assert!(all.elapsed() < Duration::from_secs(600));
}
#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn bounded_service_identities_and_connecting_state() {
    let root = root("service_identities");
    let config = config(&root);
    let mut v = value(&config);
    v["flows"] = json!((0..3)
        .map(|i| read_flow(
            &format!("reader{i}"),
            json!(["s7_a"]),
            json!([{"device_id":"s7_a","point_id":"value"}])
        ))
        .collect::<Vec<_>>());
    put(&config, &v);
    let c = Loaded::load(&config).unwrap();
    let dir = root.join("state");
    state::init(&dir, "dry_run", &c.config.instance_id).unwrap();
    preflight();
    let mut fixture = CatalogFixture::start_with(
        Path::new(FIXTURE),
        Options {
            slow_setup: true,
            ..Default::default()
        },
    )
    .unwrap();
    let (state, task) = state::State::open(&dir, "dry_run", &c.config.instance_id, &id()).unwrap();
    let mut rt = Runtime::start(&c.config, &dir, Path::new(PRODUCT), state.clone()).unwrap();
    let b_probe = std::sync::Arc::new(rt.owners["s7_b"].clone());
    fixture.observe_b(&b_probe);
    let connecting_deadline = Instant::now() + Duration::from_secs(2);
    while rt.owners["s7_b"].health().state != "connecting" {
        assert!(Instant::now() < connecting_deadline);
        tokio::time::sleep(Duration::from_millis(1)).await;
    }
    rt.launch_catalog(&c).await.unwrap();
    let end = Instant::now() + Duration::from_secs(8);
    let mut identities: HashMap<String, Vec<Value>> = HashMap::new();
    let mut connecting = false;
    loop {
        connecting |= rt.owners["s7_b"].health().state == "connecting"
            && rt.owners["s7_a"].health().state == "ready";
        for i in 0..3 {
            let flow = format!("reader{i}");
            if let Some(s) = rt.points_snapshot(&flow) {
                if let Some(sample) = s.items.first().and_then(|i| i.sample.as_ref()) {
                    let row = json!({"request_id":sample.request_id,"flow_id":sample.flow_id,"received_at":sample.received_at,"generation":sample.generation});
                    let list = identities.entry(flow).or_default();
                    if list.last() != Some(&row) {
                        list.push(row);
                    }
                }
            }
        }
        if identities.len() == 3 && identities.values().all(|v| v.len() >= 20) {
            break;
        }
        assert!(Instant::now() < end);
        tokio::time::sleep(Duration::from_millis(1)).await;
    }
    assert!(connecting);
    let trace = fixture.snapshot();
    assert_eq!(
        trace["trace"][0]
            .as_array()
            .unwrap()
            .iter()
            .find(|r| r["operation"] == 4)
            .unwrap()["b_owner_state"],
        "connecting"
    );
    let mut all = std::collections::HashSet::new();
    for rows in identities.values() {
        for row in rows {
            assert!(all.insert(row["request_id"].as_str().unwrap()));
            assert!(row["received_at"].as_str().unwrap().ends_with("+08:00"));
            assert_eq!(row["generation"], 1);
        }
    }
    rt.health().await.unwrap();
    rt.shutdown(15000).await.unwrap();
    drop(b_probe);
    state.finalize().await.unwrap();
    drop(state);
    task.join().await.unwrap();
    fixture.close().unwrap();
    preflight();
    fs::write(root.join("identities.json"),serde_json::to_vec_pretty(&json!({"samples":identities,"connecting_observed":connecting,"fixture":fixture.snapshot()})).unwrap()).unwrap();
}

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn failed_round_has_no_stale_or_fabricated_samples() {
    let root = root("failed_round");
    let path = config(&root);
    let mut v = value(&path);
    v["flows"] = json!([read_flow(
        "failure",
        json!(["s7_a", "s7_b"]),
        json!([{"device_id":"s7_a","point_id":"value"},{"device_id":"s7_b","point_id":"value"},{"device_id":"s7_a","point_id":"result"}])
    )]);
    put(&path, &v);
    let c = Loaded::load(&path).unwrap();
    let dir = root.join("state");
    state::init(&dir, "dry_run", &c.config.instance_id).unwrap();
    preflight();
    let mut f = CatalogFixture::start_with(
        Path::new(FIXTURE),
        Options {
            b_off: true,
            ..Default::default()
        },
    )
    .unwrap();
    let (st, task) = state::State::open(&dir, "dry_run", &c.config.instance_id, &id()).unwrap();
    let mut rt = Runtime::start(&c.config, &dir, Path::new(PRODUCT), st.clone()).unwrap();
    rt.launch_catalog(&c).await.unwrap();
    let end = Instant::now() + Duration::from_secs(5);
    let snapshot = loop {
        let s = rt.points_snapshot("failure").unwrap();
        if s.status == "failed" {
            break s;
        }
        assert!(Instant::now() < end);
        tokio::time::sleep(Duration::from_millis(1)).await;
    };
    assert_eq!(snapshot.items.len(), 3);
    assert_eq!(snapshot.items[0].status, "success");
    assert_eq!(snapshot.items[0].sample.as_ref().unwrap().value, 12);
    assert_eq!(snapshot.items[1].status, "error");
    assert!(snapshot.items[1].sample.is_none());
    assert_eq!(snapshot.items[2].status, "not_attempted");
    assert!(snapshot.items[2].sample.is_none());
    assert!(snapshot.items[2].error_key.is_none());
    assert!(rt.shutdown(15000).await.is_err());
    drop(st);
    task.join().await.unwrap();
    f.close().unwrap();
    preflight();
    fs::write(
        root.join("failure.json"),
        serde_json::to_vec_pretty(&json!({"round":snapshot,"fixture":f.snapshot()})).unwrap(),
    )
    .unwrap();
}
