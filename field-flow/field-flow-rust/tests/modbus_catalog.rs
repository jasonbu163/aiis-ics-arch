//! 文件：tests/modbus_catalog.rs；Modbus仅结构校验、严格codec声明和启动前零副作用能力拒绝。
#![cfg(feature = "test-fixture")]
mod catalog_support;
use catalog_support::*;
use field_flow::config::catalog::Catalog;
use serde_json::{json, Value};
use std::{collections::BTreeMap, fs, path::Path};
fn hashes(p: &Path) -> BTreeMap<String, String> {
    use sha2::{Digest, Sha256};
    let mut m = BTreeMap::new();
    for e in fs::read_dir(p).unwrap() {
        let e = e.unwrap();
        if e.file_type().unwrap().is_file() {
            m.insert(
                e.file_name().to_string_lossy().into(),
                format!("{:x}", Sha256::digest(fs::read(e.path()).unwrap())),
            );
        }
    }
    m
}
#[test]
fn declarations_and_preflight_no_effects() {
    let root = root("modbus_catalog");
    let p = config(&root);
    let mb = p.parent().unwrap().join("plcs/modbus-example.json");
    let base = value(&mb);
    assert!(!Catalog::load(&mb).unwrap().compatible);
    let out = cli(&["config", "validate", "--plc-file", mb.to_str().unwrap()]);
    assert_eq!(out.status.code(), Some(0));
    let result: Value = serde_json::from_slice(&out.stdout).unwrap();
    assert_eq!(result["format_valid"], true);
    assert_eq!(result["runtime_compatible"], false);
    for (label, v) in [
        ("unit0", {
            let mut v = base.clone();
            v["connection"]["unit_id"] = json!(0);
            v
        }),
        ("rack", {
            let mut v = base.clone();
            v["connection"]["rack"] = json!(0);
            v
        }),
        ("wrong_fc", {
            let mut v = base.clone();
            v["tables"][0]["points"][0]["functions"]["read"] = json!(3);
            v
        }),
        ("input_write", {
            let mut v = base.clone();
            v["tables"][1]["points"][0]["functions"]["write"] = json!(5);
            v
        }),
        ("word_missing", {
            let mut v = base.clone();
            v["tables"][3]["points"][0]
                .as_object_mut()
                .unwrap()
                .remove("word_order");
            v
        }),
        ("word_extra", {
            let mut v = base.clone();
            v["tables"][2]["points"][0]["word_order"] = json!("high_word_first");
            v
        }),
        ("width_overflow", {
            let mut v = base.clone();
            v["tables"][3]["points"][0]["pdu_address"] = json!(65535);
            v
        }),
        ("scale0", {
            let mut v = base.clone();
            v["tables"][3]["points"][0]["scale"]["factor"] = json!(0);
            v
        }),
        ("scale_bool", {
            let mut v = base.clone();
            v["tables"][0]["points"][0]["scale"] = json!({"factor":1,"offset":0});
            v
        }),
        ("duplicate_point", {
            let mut v = base.clone();
            v["tables"][1]["points"][0]["id"] = json!("request");
            v
        }),
    ] {
        put(&mb, &v);
        assert!(Catalog::load(&mb).is_err(), "{label}");
    }
    put(&mb, &base);
    let mut main = value(&p);
    main["plc_files"]
        .as_array_mut()
        .unwrap()
        .push(json!("plcs/modbus-example.json"));
    let mut budget = main["plc_runtime"][0].clone();
    budget["device_id"] = json!("modbus_station");
    main["plc_runtime"].as_array_mut().unwrap().push(budget);
    put(&p, &main);
    let missing = root.join("missing-state");
    let init = root.join("initialized");
    let out = cli(&[
        "state",
        "init",
        "--synthetic",
        "--mode",
        "execute",
        "--state-dir",
        init.to_str().unwrap(),
        "--instance-id",
        "ff-rust-catalog-demo",
    ]);
    assert!(out.status.success());
    let loaded = field_flow::config::runtime_v2::Loaded::load(&p).unwrap();
    let rt = tokio::runtime::Runtime::new().unwrap();
    rt.block_on(async {
        let (st, task) = field_flow::infrastructure::state::State::open(
            &init,
            "execute",
            &loaded.config.instance_id,
            &field_flow::domain::id(),
        )
        .unwrap();
        let now = field_flow::domain::now_ms();
        let intent = field_flow::domain::Input {
            schema_version: 1,
            source_id: "demo01-feed".into(),
            ready: true,
            command_id: Some("unrecovered".into()),
            value: Some(42),
            issued_at_ms: Some(now),
            expires_at_ms: Some(now + 60000),
        }
        .intent(&loaded.config.flows[0], &loaded.config.plcs[0])
        .unwrap()
        .unwrap();
        st.admit(intent.clone()).await.unwrap();
        st.dispatch(intent, "unstarted-request".into())
            .await
            .unwrap();
        drop(st);
        task.join().await.unwrap();
    });
    assert_eq!(
        field_flow::infrastructure::state::inspect(&init).unwrap()["counts"],
        json!({"in_flight":1})
    );
    let before = hashes(&init);
    let validate = cli(&["config", "validate", "--config", p.to_str().unwrap()]);
    assert!(validate.status.success());
    assert_eq!(
        serde_json::from_slice::<Value>(&validate.stdout).unwrap()["runtime_compatible"],
        false
    );
    for state in [&missing, &init] {
        let out = cli(&[
            "run",
            "--config",
            p.to_str().unwrap(),
            "--state-dir",
            state.to_str().unwrap(),
            "--execute",
        ]);
        assert_eq!(out.status.code(), Some(2));
        assert!(out.stdout.is_empty());
        assert!(String::from_utf8(out.stderr)
            .unwrap()
            .contains("unsupported_protocol"));
    }
    assert!(!missing.exists());
    assert_eq!(hashes(&init), before);
    // Every file is checked, including unreferenced disabled declarations; non-default TSAP is structural only.
    let mut disabled = base.clone();
    for t in disabled["tables"].as_array_mut().unwrap() {
        t["enabled"] = json!(false);
    }
    put(&mb, &disabled);
    let out = cli(&[
        "run",
        "--config",
        p.to_str().unwrap(),
        "--state-dir",
        missing.to_str().unwrap(),
    ]);
    assert_eq!(out.status.code(), Some(2));
    assert!(!missing.exists());
    let a = p.parent().unwrap().join("plcs/s7-a.json");
    let mut av = value(&a);
    av["connection"]["local_tsap"] = json!(512);
    put(&a, &av);
    assert_eq!(
        field_flow::config::runtime_v2::Loaded::load(&p)
            .unwrap()
            .capability()
            .unwrap_err(),
        "unsupported_protocol"
    );
    let mut s7main = main.clone();
    s7main["plc_files"].as_array_mut().unwrap().pop();
    s7main["plc_runtime"].as_array_mut().unwrap().pop();
    put(&p, &s7main);
    let a = p.parent().unwrap().join("plcs/s7-a.json");
    let mut av = value(&a);
    av["connection"]["local_tsap"] = json!(512);
    put(&a, &av);
    let out = cli(&["config", "validate", "--config", p.to_str().unwrap()]);
    assert!(out.status.success());
    assert_eq!(
        serde_json::from_slice::<Value>(&out.stdout).unwrap()["runtime_compatible"],
        false
    );
    let out = cli(&[
        "run",
        "--config",
        p.to_str().unwrap(),
        "--state-dir",
        init.to_str().unwrap(),
        "--execute",
    ]);
    assert_eq!(out.status.code(), Some(2));
    assert!(String::from_utf8(out.stderr)
        .unwrap()
        .contains("unsupported_connection"));
    assert_eq!(hashes(&init), before);
    fs::write(root.join("preflight.json"),serde_json::to_vec_pretty(&json!({"before":before,"after":hashes(&init),"missing_state_absent":!missing.exists(),"single_validate":result})).unwrap()).unwrap();
    preflight();
}
