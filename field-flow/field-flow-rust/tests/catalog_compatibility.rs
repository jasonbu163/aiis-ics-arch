//! 文件：tests/catalog_compatibility.rs；旧typed身份、真实confirmed续跑和原State恢复unknown物理保护。
#![cfg(feature = "test-fixture")]
mod catalog_support;
use catalog_support::*;
use field_flow::{
    config::runtime_v2::Loaded,
    domain::{id, Input},
    infrastructure::state,
};
use serde_json::{json, Value};
use std::{
    fs,
    path::Path,
    time::{Duration, Instant},
};
fn intent(c: &Loaded, command: &str) -> field_flow::domain::Intent {
    let now = field_flow::domain::now_ms();
    Input {
        schema_version: 1,
        source_id: c.config.flows[0].source_id.clone(),
        ready: true,
        command_id: Some(command.into()),
        value: Some(42),
        issued_at_ms: Some(now),
        expires_at_ms: Some(now + 60000),
    }
    .intent(&c.config.flows[0], &c.config.plcs[0])
    .unwrap()
    .unwrap()
}
fn schema(dir: &Path) -> Value {
    let c = rusqlite::Connection::open(dir.join("state.sqlite")).unwrap();
    let mut stmt = c
        .prepare("SELECT type,name,sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name")
        .unwrap();
    json!(stmt
        .query_map([], |r| Ok((
            r.get::<_, String>(0)?,
            r.get::<_, String>(1)?,
            r.get::<_, String>(2)?
        )))
        .unwrap()
        .map(|r| r.unwrap())
        .collect::<Vec<_>>())
}
#[test]
fn old_identity_and_confirmed_restart() {
    let root = root("catalog_compatibility");
    let mut s = Scene::new(&root, "confirmed", "execute", |v| {
        v["flows"][1]["interval_ms"] = json!(100);
    });
    let c = Loaded::load(&s.config).unwrap();
    let original = intent(&c, "hash-probe");
    let legacy = s.dir.join("legacy.yaml");
    fs::write(&legacy, serde_yaml::to_string(&c.config).unwrap()).unwrap();
    let old = field_flow::config::Config::load(&legacy).unwrap();
    assert_eq!(
        serde_json::to_value(&old.flows[0]).unwrap(),
        serde_json::to_value(&c.config.flows[0]).unwrap()
    );
    let mut old_input = Input {
        schema_version: 1,
        source_id: original.source_id.clone(),
        ready: true,
        command_id: Some(original.command_id.clone()),
        value: Some(42),
        issued_at_ms: Some(original.issued_at_ms),
        expires_at_ms: Some(original.expires_at_ms),
    }
    .intent(&old.flows[0], &old.plcs[0])
    .unwrap()
    .unwrap();
    assert_eq!(
        old_input.config_identity_hash,
        original.config_identity_hash
    );
    assert_eq!(old_input.target, original.target);
    let a = s.config.parent().unwrap().join("plcs/s7-a.json");
    let mut av = value(&a);
    av["display_name"] = json!("changed label");
    av["source"] = json!({"kind":"manual","note":"changed provenance"});
    put(&a, &av);
    fs::rename(&a, a.with_file_name("renamed.json")).unwrap();
    let mut mv = value(&s.config);
    mv["plc_files"][0] = json!("plcs/renamed.json");
    put(&s.config, &mv);
    let renamed = Loaded::load(&s.config).unwrap();
    let mut renamed_input = intent(&renamed, "hash-probe");
    renamed_input.issued_at_ms = original.issued_at_ms;
    renamed_input.expires_at_ms = original.expires_at_ms;
    assert_eq!(
        original.config_identity_hash,
        renamed_input.config_identity_hash
    );
    assert_eq!(original.target, renamed_input.target);
    let before_schema = schema(&s.state);
    s.start_fixture(Default::default());
    s.start_path(true, legacy);
    until(3, || s.snapshot()["gets"].as_u64().unwrap() >= 1);
    let body = s.fixture.as_ref().unwrap().issue_once().unwrap();
    let issued = Instant::now();
    until(3, || counts(&s) == json!({"confirmed":1}));
    s.stop(0);
    let first = s.snapshot();
    assert_eq!(first["writes"], json!([1, 0]));
    let gets = first["gets"].as_u64().unwrap();
    s.start(true);
    until(3, || s.snapshot()["gets"].as_u64().unwrap() >= gets + 10);
    assert_eq!(counts(&s), json!({"confirmed":1}));
    assert_eq!(s.snapshot()["writes"], json!([1, 0]));
    assert!(issued.elapsed() < Duration::from_secs(8));
    s.report["original_body"] = body;
    s.report["restart_window"] = s.snapshot();
    s.stop(0);
    let before_conflict = counts(&s);
    let mut changed = value(&s.config);
    changed["flows"][1]["business_name"] = json!("changed_business");
    put(&s.config, &changed);
    s.start(true);
    until(2, || {
        s.rows().iter().any(|r| {
            r["event"] == "flow_health" && r["context"]["error_key"] == "identity_conflict"
        })
    });
    assert_eq!(counts(&s), before_conflict);
    assert_eq!(s.snapshot()["writes"], json!([1, 0]));
    assert!(issued.elapsed() < Duration::from_secs(8));
    s.report["live_identity_conflict"] = json!(true);
    s.stop(0);
    s.finish();
    assert_eq!(schema(&s.state), before_schema);
    s.save();
    // Changed old semantics are a real identity conflict while the original input is still fresh.
    let state_dir = root.join("identity-state");
    state::init(&state_dir, "execute", &c.config.instance_id).unwrap();
    let rt = tokio::runtime::Runtime::new().unwrap();
    rt.block_on(async {
        let (st, task) =
            state::State::open(&state_dir, "execute", &c.config.instance_id, &id()).unwrap();
        st.admit(original.clone()).await.unwrap();
        for kind in ["offset", "db", "size", "business"] {
            let mut changed = c.clone();
            match kind {
                "offset" => changed.config.flows[0].target.byte_offset = 2,
                "db" => changed.config.flows[0].target.db_number = 2,
                "size" => changed.config.flows[0].target.db_size_bytes = 18,
                _ => changed.config.flows[0].business_name = "changed".into(),
            };
            let mut i = intent(&changed, "hash-probe");
            i.issued_at_ms = original.issued_at_ms;
            i.expires_at_ms = original.expires_at_ms;
            i.validate_time(field_flow::domain::now_ms()).unwrap();
            assert_ne!(i.config_identity_hash, original.config_identity_hash);
            assert_eq!(st.admit(i).await.unwrap_err(), "identity_conflict");
        }
        assert_eq!(
            st.command_status(old_input.clone()).await.unwrap(),
            "pending"
        );
        st.finalize().await.unwrap();
        drop(st);
        task.join().await.unwrap();
    });
    old_input.value = 43;
    assert_ne!(original.value, old_input.value);
}
#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn inflight_unknown_and_alias_protection() {
    let root = root("unknown_compatibility");
    for alias in [false, true] {
        let mut s = Scene::new(
            &root,
            if alias { "alias" } else { "same" },
            "execute",
            |v| {
                v["flows"][1]["interval_ms"] = json!(100);
            },
        );
        let c = Loaded::load(&s.config).unwrap();
        let i = intent(&c, "original-inflight");
        let (st, task) =
            state::State::open(&s.state, "execute", &c.config.instance_id, &id()).unwrap();
        st.admit(i.clone()).await.unwrap();
        st.dispatch(i.clone(), "original-request".into())
            .await
            .unwrap();
        drop(st);
        task.join().await.unwrap();
        assert_eq!(counts(&s), json!({"in_flight":1}));
        let original_schema = schema(&s.state);
        if alias {
            let a = s.config.parent().unwrap().join("plcs/s7-a.json");
            let mut v = value(&a);
            v["dbs"][0]["points"][0]["id"] = json!("alias_value");
            put(&a, &v);
            let mut v = value(&s.config);
            v["flows"][0]["reads"][0]["point_id"] = json!("alias_value");
            v["flows"][1]["target"]["point_id"] = json!("alias_value");
            v["flows"][1]["id"] = json!("new_flow");
            put(&s.config, &v);
        }
        s.start_fixture(Default::default());
        s.start(true);
        until(7, || s.wire_round(&[12, 1, 56, 34]));
        s.fixture.as_ref().unwrap().issue_once().unwrap();
        until(3, || {
            s.rows().iter().any(|r| {
                r["event"] == "flow_health" && r["context"]["error_key"] == "target_unknown"
            })
        });
        assert_eq!(counts(&s), json!({"unknown":1}));
        assert_eq!(s.snapshot()["writes"], json!([0, 0]));
        s.report["inspect_blocked"] = state::inspect(&s.state).unwrap();
        s.stop(0);
        s.finish();
        assert_eq!(schema(&s.state), original_schema);
        let (st, task) =
            state::State::open(&s.state, "execute", &c.config.instance_id, &id()).unwrap();
        assert_eq!(st.command_status(i.clone()).await.unwrap(), "unknown");
        let mut other = i.clone();
        other.source_id = "other_source".into();
        other.flow_id = "other_flow".into();
        other.command_id = "other_command".into();
        assert_eq!(st.admit(other).await.unwrap_err(), "target_unknown");
        st.finalize().await.unwrap();
        drop(st);
        task.join().await.unwrap();
        s.save();
    }
}

#[test]
fn reading_applied_42_does_not_confirm_unknown() {
    let root = root("unknown_readback");
    let mut s = Scene::new(&root, "truncated_ack", "execute", |v| {
        v["flows"][1]["interval_ms"] = json!(100);
    });
    s.start_fixture(field_flow::fixture::catalog_demo::Options {
        short_write_ack_once: true,
        ..Default::default()
    });
    s.start(true);
    until(2, || s.wire_round(&[12, 1, 56, 34]));
    s.fixture.as_ref().unwrap().issue_once().unwrap();
    until(3, || counts(&s) == json!({"unknown":1}));
    until(2, || s.wire_round(&[42, 1, 56, 34]));
    s.stop(1);
    let first_rows = s.rows();
    assert!(!first_rows.iter().any(forced));
    assert_eq!(s.snapshot()["writes"], json!([1, 0]));
    s.start(true);
    until(2, || {
        s.rows()
            .iter()
            .filter(|r| {
                r["event"] == "flow_health" && r["context"]["error_key"] == "target_unknown"
            })
            .count()
            >= 1
    });
    let read_before = s.snapshot()["reads"][0].as_u64().unwrap();
    until(2, || {
        s.snapshot()["reads"][0].as_u64().unwrap() >= read_before + 12
    });
    assert_eq!(counts(&s), json!({"unknown":1}));
    assert_eq!(s.snapshot()["writes"], json!([1, 0]));
    s.stop(0);
    s.finish();
    assert_eq!(
        s.report["fixture"]["final_memory"][0]["memory"]["db1"],
        format!("002a0001{}", "a5".repeat(12))
    );
    s.report["expected_first_protocol_fault_exit"] = json!(1);
    s.report["restart_normal_exit_unknown_retained"] = json!(true);
    s.save();
}
