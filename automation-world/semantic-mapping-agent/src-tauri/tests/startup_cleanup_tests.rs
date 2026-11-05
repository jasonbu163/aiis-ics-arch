//! SMA-002 v1惰性兼容、破损保护和公共时间回归；仅自有临时fixture。
use aiis_semantic_mapping_agent_lib::config::runtime_startup::{self, RuntimeStartupPreferences};
use serde_json::{json, Value};
use std::fs;

#[test]
fn v1_mapping_survives_and_legacy_segment_is_inert_and_preserved() {
    let directory = std::env::temp_dir().join(format!("sma-002-startup-{}", std::process::id()));
    fs::create_dir_all(&directory).unwrap();
    let path = directory.join("runtime-startup.json");
    let original = json!({"schemaVersion":1,"runtimeAutoStart":{
        "collectionFactSimulation":{"enabled":true,"sourceKey":"old-source","opaque":[1,2]},
        "apiMappingRuntime":{"enabled":true,"factsPollingIntervalMs":3456}
    }});
    let bytes = serde_json::to_vec_pretty(&original).unwrap();
    fs::write(&path, &bytes).unwrap();
    let mut preferences = runtime_startup::load_from_path(&path).unwrap();
    assert!(preferences.runtime_auto_start.api_mapping_runtime.enabled);
    assert_eq!(
        preferences
            .runtime_auto_start
            .api_mapping_runtime
            .facts_polling_interval_ms,
        3456
    );
    assert_eq!(
        fs::read(&path).unwrap(),
        bytes,
        "load must not modify existing bytes"
    );
    let ipc = serde_json::to_value(&preferences).unwrap();
    assert!(ipc["runtimeAutoStart"]
        .get("collectionFactSimulation")
        .is_none());
    preferences.runtime_auto_start.api_mapping_runtime.enabled = false;
    runtime_startup::save_to_path(&path, &preferences).unwrap();
    let saved: Value = serde_json::from_slice(&fs::read(&path).unwrap()).unwrap();
    assert_eq!(
        saved["runtimeAutoStart"]["collectionFactSimulation"],
        original["runtimeAutoStart"]["collectionFactSimulation"]
    );
    assert_eq!(
        saved["runtimeAutoStart"]["apiMappingRuntime"],
        json!({"enabled":false,"factsPollingIntervalMs":3456})
    );
    for invalid in [
        "{broken",
        r#"{"schemaVersion":2,"runtimeAutoStart":{"collectionFactSimulation":{"enabled":true},"apiMappingRuntime":{"enabled":true}}}"#,
    ] {
        fs::write(&path, invalid).unwrap();
        assert!(runtime_startup::load_from_path(&path).is_err());
        assert!(runtime_startup::save_to_path(&path, &preferences).is_err());
        assert_eq!(fs::read_to_string(&path).unwrap(), invalid);
    }
    fs::remove_file(&path).unwrap();
    let missing = runtime_startup::load_from_path(&path).unwrap();
    assert_eq!(missing, RuntimeStartupPreferences::default());
    assert!(
        !path.exists(),
        "load of a missing preference must not create it"
    );
    runtime_startup::save_to_path(&path, &missing).unwrap();
    let neutral: Value = serde_json::from_slice(&fs::read(&path).unwrap()).unwrap();
    assert_eq!(
        neutral["runtimeAutoStart"]["collectionFactSimulation"],
        json!({"enabled":false,"sourceKey":null})
    );
    fs::remove_dir_all(directory).unwrap();
}

#[test]
fn runtime_calendar_time_has_shanghai_offset_and_retains_milliseconds() {
    let value = aiis_semantic_mapping_agent_lib::domain::runtime::business_now_string();
    let parsed = chrono::DateTime::parse_from_rfc3339(&value).unwrap();
    assert_eq!(parsed.offset().local_minus_utc(), 8 * 3600);
    assert_eq!(value.len(), 29);
    assert!(value.ends_with("+08:00"));
}

#[test]
fn disabled_gate_blocks_saved_mapping_before_http() {
    // 子进程单独覆盖环境，不能让并行loopback fixture的gate与本例互相污染。
    if std::env::var("SMA_002_GATE_CHILD").as_deref() == Ok("1") {
        let runtime = tokio::runtime::Runtime::new().unwrap();
        let result = runtime.block_on(
            aiis_semantic_mapping_agent_lib::commands::mapping_runtime::run_mapping_manual_once(
                "fixture".into(),
                "version".into(),
                std::env::var("SMA_002_FIXTURE_URL").unwrap(),
            ),
        );
        assert_eq!(
            result.unwrap_err(),
            "SMA_LOCAL_CONFIGURATION_EXECUTION_NOT_AVAILABLE"
        );
        return;
    }
    let listener = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
    listener.set_nonblocking(true).unwrap();
    for enabled in ["false", "true"] {
        let status = std::process::Command::new(std::env::current_exe().unwrap())
            .args(["--exact", "disabled_gate_blocks_saved_mapping_before_http"])
            .env("SMA_002_GATE_CHILD", "1")
            .env(
                "SMA_002_FIXTURE_URL",
                format!("http://{}", listener.local_addr().unwrap()),
            )
            .env("SMA_HTTP_ENABLED", enabled)
            .env(
                "SMA_ENV_FILE",
                std::env::temp_dir().join("sma-002-no-real-env"),
            )
            .status()
            .unwrap();
        assert!(status.success());
    }
    assert_eq!(
        listener.accept().unwrap_err().kind(),
        std::io::ErrorKind::WouldBlock
    );
}
