//! File Path: /automation-world/semantic-mapping-agent/src-tauri/tests/collection_simulation_tests.rs
//! Description: Focused Backend-HTTP collection Simulation tests.
//! Main Features:
//!   - Covers typed sequence values and datetime-only current-time-zone generation
//!   - Locks the active command to Backend URL plus sourceKey without SQL Repository input

use std::path::Path;

use aiis_semantic_mapping_agent_lib::services::simulation::{
    generator::{
        current_time_value_at, should_update, validate_current_time_rule, validate_value, value,
    },
    model::{CollectionSimulationHttpStartRequest, SimulationFact, SimulationRule},
};
use chrono::{TimeZone, Utc};
use serde_json::json;

fn fact(name: &str, kind: &str, data_type: &str) -> SimulationFact {
    SimulationFact {
        source_key: "wincc-line-01".to_string(),
        name: name.to_string(),
        fact_kind: kind.to_string(),
        data_type: data_type.to_string(),
        value_text: None,
        contract_version: "collection-facts.v1".to_string(),
    }
}

fn rule(name: &str, sequence: Vec<serde_json::Value>, interval_ms: u64) -> SimulationRule {
    SimulationRule {
        fact_name: name.to_string(),
        sequence,
        interval_ms,
        enabled: true,
        write_current_time: false,
        current_time_mode: "utc".to_string(),
        current_time_zone: None,
    }
}

#[test]
fn sequence_values_normalize_all_approved_json_types() {
    let cases = [
        (
            fact("line.position", "current", "string"),
            json!("B05"),
            "B05",
        ),
        (fact("line.count", "current", "integer"), json!(12), "12"),
        (
            fact("line.temperature", "incremental", "number"),
            json!(20.5),
            "20.5",
        ),
        (
            fact("line.ready", "current", "boolean"),
            json!(true),
            "true",
        ),
        (
            fact("line.observed_at", "incremental", "datetime"),
            json!("2026-08-14T12:00:00.000Z"),
            "2026-08-14T12:00:00.000Z",
        ),
        (
            fact("line.local_observed_at", "incremental", "datetime"),
            json!("2026-08-14T20:00:00.000+08:00"),
            "2026-08-14T20:00:00.000+08:00",
        ),
    ];
    for (fact, item, expected) in cases {
        assert_eq!(
            value(&rule(&fact.name, vec![item], 100), &fact, 0).unwrap(),
            expected
        );
    }
}

#[test]
fn current_time_is_generated_only_for_datetime_at_runtime_tick() {
    let datetime = fact("line.observed_at", "current", "datetime");
    let now = Utc
        .with_ymd_and_hms(2026, 8, 26, 7, 30, 0)
        .single()
        .unwrap();
    let generated = current_time_value_at(
        &current_time_rule("line.observed_at", "utc", None),
        &datetime,
        now,
    )
    .unwrap();
    assert_eq!(generated, "2026-08-26T07:30:00.000Z");
    assert!(current_time_value_at(
        &current_time_rule("line.position", "utc", None),
        &fact("line.position", "current", "string"),
        now,
    )
    .unwrap_err()
    .starts_with("COLLECTION_SIMULATION_CURRENT_TIME_DATETIME_REQUIRED"));
}

#[test]
fn current_time_custom_timezone_uses_the_tick_date_offset() {
    let datetime = fact("line.observed_at", "current", "datetime");
    let rule = current_time_rule("line.observed_at", "custom", Some("America/New_York"));
    let winter = Utc
        .with_ymd_and_hms(2026, 1, 15, 12, 30, 0)
        .single()
        .unwrap();
    let summer = Utc
        .with_ymd_and_hms(2026, 7, 15, 12, 30, 0)
        .single()
        .unwrap();

    assert_eq!(
        current_time_value_at(&rule, &datetime, winter).unwrap(),
        "2026-01-15T07:30:00.000-05:00"
    );
    assert_eq!(
        current_time_value_at(&rule, &datetime, summer).unwrap(),
        "2026-07-15T08:30:00.000-04:00"
    );
}

#[test]
fn current_time_system_timezone_uses_an_explicit_runtime_host_offset() {
    let datetime = fact("line.observed_at", "current", "datetime");
    let generated = current_time_value_at(
        &current_time_rule("line.observed_at", "system", None),
        &datetime,
        Utc.with_ymd_and_hms(2026, 8, 26, 7, 30, 0)
            .single()
            .unwrap(),
    )
    .unwrap();
    assert!(generated.contains('T'));
    assert!(!generated.ends_with('Z'));
    assert!(chrono::DateTime::parse_from_rfc3339(&generated).is_ok());
}

#[test]
fn current_time_rejects_invalid_saved_strategy_without_utc_fallback() {
    let datetime = fact("line.observed_at", "current", "datetime");
    assert_eq!(
        validate_current_time_rule(
            &current_time_rule("line.observed_at", "custom", None),
            &datetime,
        )
        .unwrap_err(),
        "COLLECTION_SIMULATION_CURRENT_TIME_ZONE_REQUIRED:line.observed_at"
    );
    assert_eq!(
        validate_current_time_rule(
            &current_time_rule("line.observed_at", "custom", Some("Not/AZone")),
            &datetime,
        )
        .unwrap_err(),
        "COLLECTION_SIMULATION_CURRENT_TIME_ZONE_INVALID:line.observed_at"
    );
    assert_eq!(
        validate_current_time_rule(
            &current_time_rule("line.observed_at", "utc", Some("Asia/Shanghai")),
            &datetime,
        )
        .unwrap_err(),
        "COLLECTION_SIMULATION_CURRENT_TIME_ZONE_UNEXPECTED:line.observed_at"
    );
}

#[test]
fn invalid_json_types_fail_before_values_api_write() {
    let integer = fact("line.count", "current", "integer");
    assert_eq!(
        value(&rule(&integer.name, vec![json!("1")], 100), &integer, 0).unwrap_err(),
        "COLLECTION_SIMULATION_TYPE_INVALID:line.count"
    );
    assert_eq!(
        validate_value(&integer, "1.5").unwrap_err(),
        "COLLECTION_SIMULATION_TYPE_INVALID:line.count"
    );
    let mut position = fact("line.position", "current", "string");
    position.value_text = Some("B05".to_string());
    assert!(!should_update(&position, "B05"));
    let mut append = fact("line.temperature", "incremental", "number");
    append.value_text = Some("20".to_string());
    assert!(should_update(&append, "20"));
}

#[test]
fn active_start_request_accepts_only_backend_url_and_source_key() {
    let request: CollectionSimulationHttpStartRequest = serde_json::from_value(json!({
        "backendBaseUrl": "http://127.0.0.1:8144",
        "sourceKey": "wincc-line-01"
    }))
    .unwrap();
    assert_eq!(request.backend_base_url, "http://127.0.0.1:8144");
    assert_eq!(request.source_key, "wincc-line-01");
    assert!(
        serde_json::from_value::<CollectionSimulationHttpStartRequest>(json!({
            "backendBaseUrl": "http://127.0.0.1:8144",
            "sourceKey": "wincc-line-01",
            "rules": []
        }))
        .is_err()
    );
}

#[test]
fn http_scheduler_batches_values_and_has_no_simulation_sql_repository() {
    let scheduler = include_str!("../src/services/simulation/collection.rs");
    let model = include_str!("../src/services/simulation/model.rs");
    let active_start = &scheduler[scheduler.find("pub async fn start_http(").unwrap()
        ..scheduler.find("/// Compatibility adapter").unwrap()];
    assert!(active_start.contains("CollectionSimulationHttpStartRequest"));
    assert!(!active_start.contains("ConnectionProfile"));
    assert!(!active_start.contains("rules"));
    for required in [
        "api/integration/v1/collection-facts",
        "api/tss/v1/simulation-rules",
        "VALUES_API_MAX_COUNT",
        "write_due_values",
        "write_current_time",
        "current_time_value",
    ] {
        assert!(scheduler.contains(required), "missing {required}");
    }
    for required in ["current_time_mode", "current_time_zone"] {
        assert!(model.contains(required), "missing {required}");
    }
    assert!(!scheduler.contains("endpoint(\"api/integration/v1/collection-facts/\")?;"));
    assert!(!scheduler.contains("repository::"));
    assert!(!Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("src/services/simulation/repository.rs")
        .exists());
}

fn current_time_rule(
    name: &str,
    current_time_mode: &str,
    current_time_zone: Option<&str>,
) -> SimulationRule {
    SimulationRule {
        write_current_time: true,
        current_time_mode: current_time_mode.to_string(),
        current_time_zone: current_time_zone.map(ToString::to_string),
        ..rule(name, vec![], 100)
    }
}
