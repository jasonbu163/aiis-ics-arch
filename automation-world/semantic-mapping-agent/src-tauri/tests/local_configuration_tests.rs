//! SMA-004隔离SQLite/全图/事务/CAS/纯预览回归；仅自有临时库与专用loopback。
use aiis_semantic_mapping_agent_lib::{
    contracts::local_configuration::*,
    domain::{
        local_configuration as domain,
        runtime::{ManagedRuntimeState, RuntimeStartRequest},
    },
    services::local_configuration::LocalConfigurationService,
};
use serde_json::{json, Value};
use std::{
    path::PathBuf,
    sync::{
        atomic::{AtomicU64, Ordering},
        Arc, Barrier,
    },
};
static NEXT: AtomicU64 = AtomicU64::new(0);
struct Fixture {
    dir: PathBuf,
}
impl Fixture {
    fn new() -> Self {
        let dir = PathBuf::from(format!(
            "/private/tmp/sma004-test-{}-{}",
            std::process::id(),
            NEXT.fetch_add(1, Ordering::SeqCst)
        ));
        std::fs::create_dir(&dir).unwrap();
        Self { dir }
    }
    fn path(&self) -> PathBuf {
        self.dir.join("configuration.sqlite3")
    }
    fn service(&self) -> LocalConfigurationService {
        LocalConfigurationService::new(Ok(self.path()))
    }
}
impl Drop for Fixture {
    fn drop(&mut self) {
        std::fs::remove_dir_all(&self.dir).unwrap();
    }
}
fn idle() -> ManagedRuntimeState {
    ManagedRuntimeState::new("api_first_mapping")
}
fn intent(kind: &str, resource: &str, payload: Value) -> ChangeIntent {
    ChangeIntent {
        kind: kind.into(),
        resource: resource.into(),
        id: None,
        payload,
    }
}
fn target(key: &str) -> Value {
    json!({"apiKey":key,"name":key,"httpMethod":"POST","path":"/fixture","schemaSource":"manual","operationId":null,"bodyTemplate":{"v":null},"parameterSchema":[{"parameterKey":"body:v","location":"body","name":"v","jsonPath":"v","dataType":"integer","required":true}],"idempotencySupported":false,"enabled":true})
}
fn rule() -> Value {
    json!({"valueRuleKey":"rule","name":"rule","dataType":"integer","values":[1,2],"originSourceKey":null,"originFactName":null,"enabled":true})
}
fn mapping() -> Value {
    json!({"mappingKey":"mapping","name":"mapping","sourceKey":null,"targetApiKey":"target","bindings":{"body:v":{"kind":"fact","value":null,"sourceKey":"unknown-source","factName":"unknown-fact","valueRuleKey":null}},"intervalMs":2500,"enabled":true})
}
fn seed(s: &LocalConfigurationService) {
    s.change(0, intent("upsert", "targetApis", target("target")), &idle())
        .unwrap();
    s.change(1, intent("upsert", "mappingValueRules", rule()), &idle())
        .unwrap();
    s.change(2, intent("upsert", "mappings", mapping()), &idle())
        .unwrap();
}
#[test]
fn sqlite_cas_two_clients_reopen_and_profile_isolation() {
    let f = Fixture::new();
    let s = Arc::new(f.service());
    let barrier = Arc::new(Barrier::new(3));
    let mut threads = vec![];
    for name in ["a", "b"] {
        let s = s.clone();
        let b = barrier.clone();
        threads.push(std::thread::spawn(move || {
            b.wait();
            s.change(0, intent("upsert", "targetApis", target(name)), &idle())
        }));
    }
    barrier.wait();
    let results: Vec<_> = threads.into_iter().map(|t| t.join().unwrap()).collect();
    assert_eq!(results.iter().filter(|r| r.is_ok()).count(), 1);
    assert_eq!(
        results
            .iter()
            .filter_map(|r| r.as_ref().err())
            .next()
            .unwrap(),
        "SMA_CONFIGURATION_CONFLICT"
    );
    let saved = s.load().unwrap();
    assert_eq!(saved.revision, 1);
    assert!(saved.updated_at.ends_with("+08:00"));
    drop(s);
    assert_eq!(f.service().load().unwrap(), saved);
    let other = Fixture::new();
    assert_eq!(other.service().load().unwrap().revision, 0);
}
#[test]
fn import_preview_is_read_only_content_and_revision_bound_and_unchanged_is_noop() {
    let f = Fixture::new();
    let s = f.service();
    let i = intent("import", "targetApis", json!([target("target")]));
    let before = s.load().unwrap();
    let p = s.preview(0, i.clone()).unwrap();
    assert!(p.errors.is_empty());
    assert_eq!(s.load().unwrap(), before);
    let changed = intent("import", "targetApis", json!([target("different")]));
    assert_eq!(
        s.apply(0, changed, &p.token, false, &idle()).unwrap_err(),
        "SMA_CONFIGURATION_PREVIEW_CHANGED"
    );
    s.apply(0, i.clone(), &p.token, false, &idle()).unwrap();
    let p = s.preview(1, i.clone()).unwrap();
    assert_eq!(p.unchanged_keys.len(), 4);
    let same = s.apply(1, i, &p.token, false, &idle()).unwrap();
    assert_eq!(same.revision, 1);
    let duplicate = intent("import", "targetApis", json!([target("x"), target("x")]));
    let p = s.preview(1, duplicate).unwrap();
    assert!(!p.errors.is_empty());
    assert_eq!(s.load().unwrap(), same);
}
#[test]
fn backup_restore_whole_graph_confirmation_deletions_and_monotonic_revision() {
    let f = Fixture::new();
    let s = f.service();
    seed(&s);
    let backup: Value = serde_json::from_str(&s.export().unwrap()).unwrap();
    let second = Fixture::new();
    let other = second.service();
    other
        .change(
            0,
            intent("upsert", "targetApis", target("to-delete")),
            &idle(),
        )
        .unwrap();
    let restore = intent("restore", "configuration", backup.clone());
    let p = other.preview(1, restore.clone()).unwrap();
    assert!(p.deleted_keys.iter().any(|k| k.contains("to-delete")));
    assert_eq!(
        other
            .apply(1, restore.clone(), &p.token, false, &idle())
            .unwrap_err(),
        "SMA_CONFIGURATION_RESTORE_CONFIRMATION_REQUIRED"
    );
    assert_eq!(other.load().unwrap().revision, 1);
    other.apply(1, restore, &p.token, true, &idle()).unwrap();
    assert_eq!(other.load().unwrap().revision, 2);
    assert_eq!(other.load().unwrap().document, s.load().unwrap().document);
    assert_eq!(s.load().unwrap().revision, 3);
    let serialized = other.export().unwrap();
    for key in [
        "runtimeAutoStart",
        "externalIoEnabled",
        "lease",
        "latest",
        "cursor",
        "localStorage",
    ] {
        assert!(!serialized.contains(key));
    }
    let mut invalid = backup;
    invalid["schemaVersion"] = json!(2);
    assert!(!other
        .preview(2, intent("restore", "configuration", invalid))
        .unwrap()
        .errors
        .is_empty());
}
#[test]
fn missing_sources_stay_unverified_saved_preview_is_snapshot_only() {
    let f = Fixture::new();
    let s = f.service();
    seed(&s);
    let saved = s.load().unwrap();
    let preview = s.saved_preview("mappings:mapping", 3).unwrap();
    assert!(preview["request"].is_null());
    assert_eq!(preview["sourceReferences"][0]["status"], "unverified");
    assert_eq!(
        preview["diagnostics"][0]["errorCode"],
        "tss_mapping_manual_run_fact_missing"
    );
    assert_eq!(s.load().unwrap(), saved);
    drop(s);
    let s = f.service();
    assert_eq!(s.saved_preview("mappings:mapping", 3).unwrap(), preview);
    let mut m = mapping();
    m["sourceKey"] = json!("legacy");
    m["bindings"]["body:v"]["sourceKey"] = Value::Null;
    let normalized = domain::transform(
        &saved.document,
        &intent("import", "mappings", json!([m.clone()])),
    )
    .unwrap();
    assert_eq!(
        normalized.mappings[0]["bindings"]["body:v"]["sourceKey"],
        "legacy"
    );
    m["bindings"]["body:v"]["sourceKey"] = json!("conflict");
    assert!(
        domain::transform(&saved.document, &intent("import", "mappings", json!([m])))
            .unwrap_err()
            .contains("LEGACY_SOURCE_CONFLICT")
    );
    let mut wrong = mapping();
    wrong["bindings"]["body:v"]["factId"] = json!("invented");
    assert!(domain::transform(
        &saved.document,
        &intent("import", "mappings", json!([wrong]))
    )
    .is_err());
}
#[test]
fn references_and_type_changes_are_atomic_and_disabled_preserves_references() {
    let f = Fixture::new();
    let s = f.service();
    seed(&s);
    let original = s.load().unwrap();
    let mut delete = intent("delete", "targetApis", Value::Null);
    delete.id = Some("targetApis:target".into());
    let err = s.change(3, delete.clone(), &idle()).unwrap_err();
    assert!(err.contains("mapping"));
    assert_eq!(s.load().unwrap(), original);
    let mut m = mapping();
    m["bindings"]["body:v"]["valueRuleKey"] = json!("rule");
    s.change(
        3,
        intent("import-forbidden", "mappings", json!([m.clone()])),
        &idle(),
    )
    .unwrap_err();
    let p = s
        .preview(3, intent("import", "mappings", json!([m.clone()])))
        .unwrap();
    s.apply(
        3,
        intent("import", "mappings", json!([m])),
        &p.token,
        false,
        &idle(),
    )
    .unwrap();
    let mut dr = intent("delete", "mappingValueRules", Value::Null);
    dr.id = Some("mappingValueRules:rule".into());
    assert!(s.change(4, dr, &idle()).unwrap_err().contains("mapping"));
    let mut t = target("target");
    t["parameterSchema"][0]["dataType"] = json!("string");
    let mut update = intent("upsert", "targetApis", t);
    update.id = Some("targetApis:target".into());
    assert!(s.change(4, update, &idle()).is_err());
    let mut m = mapping();
    m["enabled"] = json!(false);
    let mut update = intent("upsert", "mappings", m);
    update.id = Some("mappings:mapping".into());
    s.change(4, update, &idle()).unwrap();
    assert!(s.change(5, delete.clone(), &idle()).is_err());
    let mut dm = intent("delete", "mappings", Value::Null);
    dm.id = Some("mappings:mapping".into());
    s.change(5, dm, &idle()).unwrap();
    s.change(6, delete, &idle()).unwrap();
}
#[test]
fn runtime_busy_blocks_all_writes_and_stop_allows_retry() {
    let f = Fixture::new();
    let s = f.service();
    let rt = idle();
    let i = intent("import", "targetApis", json!([target("target")]));
    let p = s.preview(0, i.clone()).unwrap();
    rt.start(
        &RuntimeStartRequest {
            channel: "both".into(),
            source_key: "x".into(),
            stream_key: "x".into(),
            interval_ms: 1000,
        },
        "fixture".into(),
    )
    .unwrap();
    assert_eq!(
        s.change(0, intent("upsert", "targetApis", target("x")), &rt)
            .unwrap_err(),
        "SMA_CONFIGURATION_RUNTIME_BUSY"
    );
    assert_eq!(
        s.apply(0, i.clone(), &p.token, false, &rt).unwrap_err(),
        "SMA_CONFIGURATION_RUNTIME_BUSY"
    );
    rt.set_running();
    rt.request_pause().unwrap();
    assert!(s.apply(0, i.clone(), &p.token, false, &rt).is_err());
    rt.request_stop().unwrap();
    assert!(s.apply(0, i.clone(), &p.token, false, &rt).is_err());
    rt.finish("stopped");
    s.apply(0, i, &p.token, false, &rt).unwrap();
}
#[test]
fn sqlite_abort_and_busy_leave_logical_snapshot_unchanged() {
    let f = Fixture::new();
    let s = f.service();
    seed(&s);
    let before = s.load().unwrap();
    let db = rusqlite::Connection::open(f.path()).unwrap();
    db.execute_batch("CREATE TRIGGER reject_update BEFORE UPDATE ON configuration BEGIN SELECT RAISE(ABORT, 'fixture failure'); END;").unwrap();
    assert!(s
        .change(3, intent("upsert", "targetApis", target("extra")), &idle())
        .is_err());
    assert_eq!(s.load().unwrap(), before);
    db.execute_batch("DROP TRIGGER reject_update; BEGIN IMMEDIATE;")
        .unwrap();
    assert_eq!(
        s.change(3, intent("upsert", "targetApis", target("extra")), &idle())
            .unwrap_err(),
        "SMA_CONFIGURATION_BUSY"
    );
    assert_eq!(s.load().unwrap(), before);
    db.execute_batch("ROLLBACK;").unwrap();
    assert_eq!(
        s.change(3, intent("upsert", "targetApis", target("extra")), &idle())
            .unwrap()
            .revision,
        4
    );
}
#[test]
fn corrupt_unknown_unavailable_and_relative_profiles_do_not_fallback() {
    let f = Fixture::new();
    std::fs::write(f.path(), b"not a sqlite file").unwrap();
    assert!(f.service().load().is_err());
    assert_eq!(std::fs::read(f.path()).unwrap(), b"not a sqlite file");
    assert!(
        LocalConfigurationService::new(Ok(PathBuf::from("relative.sqlite3")))
            .load()
            .is_err()
    );
    let g = Fixture::new();
    let s = g.service();
    drop(s);
    let db = rusqlite::Connection::open(g.path()).unwrap();
    db.execute_batch("PRAGMA user_version=99").unwrap();
    assert_eq!(
        g.service().load().unwrap_err(),
        "SMA_CONFIGURATION_SCHEMA_UNSUPPORTED"
    );
    let bad = Fixture::new();
    std::fs::create_dir(bad.path()).unwrap();
    assert!(bad.service().load().is_err());
}
#[test]
fn final_document_and_actual_pretty_backup_limits_cannot_be_bypassed() {
    let f = Fixture::new();
    let s = f.service();
    let mut t = target("first");
    t["name"] = json!("a".repeat(5 * 1024 * 1024));
    s.change(0, intent("upsert", "targetApis", t), &idle())
        .unwrap();
    let before = s.load().unwrap();
    let mut t = target("second");
    t["name"] = json!("b".repeat(5 * 1024 * 1024));
    assert_eq!(
        s.change(1, intent("upsert", "targetApis", t), &idle())
            .unwrap_err(),
        "SMA_CONFIGURATION_LIMIT_EXCEEDED"
    );
    assert_eq!(s.load().unwrap(), before);
    let encoded = s.export().unwrap();
    assert!(encoded.len() <= MAX_BYTES);
    let p = s
        .preview(
            1,
            intent(
                "restore",
                "configuration",
                serde_json::from_str(&encoded).unwrap(),
            ),
        )
        .unwrap();
    assert!(p.errors.is_empty());
    let mut d = ConfigurationDocument::default();
    d.target_apis = (0..10_001).map(|n| target(&format!("t{n}"))).collect();
    assert_eq!(
        domain::validate(&d).unwrap_err(),
        "SMA_CONFIGURATION_LIMIT_EXCEEDED"
    );
}
#[test]
fn normal_admission_is_zero_connection_even_when_http_true() {
    let f = Fixture::new();
    let s = f.service();
    let listener = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
    listener.set_nonblocking(true).unwrap();
    let rt = tokio::runtime::Runtime::new().unwrap();
    let url = format!("http://{}", listener.local_addr().unwrap());
    use aiis_semantic_mapping_agent_lib::{
        domain::mapping_runtime::ApiFirstMappingRuntimeStartRequest,
        services::mapping_runtime as mapping,
    };
    assert_eq!(
        s.admit_execution().unwrap_err(),
        "SMA_LOCAL_CONFIGURATION_EXECUTION_NOT_AVAILABLE"
    );
    assert_eq!(
        rt.block_on(mapping::run_mapping_manual_once(
            "fixture".into(),
            "version".into(),
            url.clone()
        ))
        .unwrap_err(),
        "SMA_LOCAL_CONFIGURATION_EXECUTION_NOT_AVAILABLE"
    );
    let state = mapping::ApiFirstMappingRuntimeState::default();
    assert_eq!(
        rt.block_on(mapping::start_api_first_mapping_runtime(
            &state,
            ApiFirstMappingRuntimeStartRequest {
                backend_base_url: url
            }
        ))
        .unwrap_err(),
        "SMA_LOCAL_CONFIGURATION_EXECUTION_NOT_AVAILABLE"
    );
    assert_eq!(
        mapping::resume_api_first_mapping_runtime(&state).unwrap_err(),
        "SMA_LOCAL_CONFIGURATION_EXECUTION_NOT_AVAILABLE"
    );
    assert!(listener.accept().is_err());
    assert_eq!(s.load().unwrap().revision, 0);
}
#[test]
fn catalog_material_selection_and_referenced_deletion_are_local_atomic() {
    let f = Fixture::new();
    let s = f.service();
    let op = json!({"method":"POST","path":"/fixture","summary":"Fixture","operationId":"fixture","operationSnapshot":{},"requestContract":target("x")["parameterSchema"],"bodyTemplate":{"v":null},"normalizationStatus":"ready","normalizationErrorCode":null,"jsonTemplate":"{\"v\":null}","contentHash":"fixture","sourceLocator":"file:fixture.json"});
    let i = intent("catalog", "catalog", json!([op]));
    let p = s.preview(0, i.clone()).unwrap();
    assert!(p.errors.is_empty());
    assert!(s.load().unwrap().document.catalog.is_empty());
    s.apply(0, i, &p.token, false, &idle()).unwrap();
    s.change(
        1,
        intent("selection", "materials", json!(["POST /fixture"])),
        &idle(),
    )
    .unwrap();
    let key = s.load().unwrap().document.materials[0]["materialKey"].clone();
    s.change(
        2,
        intent("loadMaterials", "targetApis", json!([key])),
        &idle(),
    )
    .unwrap();
    let before = s.load().unwrap();
    assert_eq!(before.document.target_apis.len(), 1);
    let e = s
        .change(3, intent("selection", "materials", json!([])), &idle())
        .unwrap_err();
    assert!(e.contains(before.document.target_apis[0]["apiKey"].as_str().unwrap()));
    assert_eq!(s.load().unwrap(), before);
    let empty = s
        .preview(3, intent("catalog", "catalog", json!([])))
        .unwrap();
    assert!(!empty.errors.is_empty());
    assert_eq!(s.load().unwrap(), before);
}
#[test]
fn source_metadata_has_evidence_no_values_and_detects_type_conflicts() {
    let f = Fixture::new();
    let s = f.service();
    seed(&s);
    let metadata = json!([{"sourceKey":"unknown-source","factName":"unknown-fact","dataType":"integer","factKind":"current","sourceLocator":"isolated-fixture-contract","definitionVersion":"original-definition-v1"}]);
    s.change(
        3,
        intent("metadata", "sourceMetadata", metadata.clone()),
        &idle(),
    )
    .unwrap();
    let p = s.saved_preview("mappings:mapping", 4).unwrap();
    assert!(p["request"].is_null());
    assert_eq!(
        p["sourceReferences"][0]["metadata"]["definitionVersion"],
        "original-definition-v1"
    );
    assert_eq!(p["sourceReferences"][0]["status"], "metadata_only");
    let before = s.load().unwrap();
    let mut bad = metadata.clone();
    bad[0]["value"] = json!(10);
    assert!(s
        .change(4, intent("metadata", "sourceMetadata", bad), &idle())
        .is_err());
    let mut bad = metadata;
    bad[0]["dataType"] = json!("boolean");
    assert!(s
        .change(4, intent("metadata", "sourceMetadata", bad), &idle())
        .is_err());
    assert_eq!(s.load().unwrap(), before);
    let mut empty = rule();
    empty["values"] = json!([]);
    empty["valueRuleKey"] = Value::Null;
    empty["originSourceKey"] = json!("unknown-source");
    empty["originFactName"] = json!("unknown-fact");
    let saved = s
        .change(4, intent("upsert", "mappingValueRules", empty), &idle())
        .unwrap();
    assert!(saved
        .document
        .mapping_value_rules
        .iter()
        .any(|r| r["valueRuleKey"]
            .as_str()
            .unwrap()
            .starts_with("fact-rule-")));
}
#[test]
fn sqlite_snapshot_survives_a_real_os_process_boundary() {
    if let Ok(path) = std::env::var("SMA004_OWNED_CHILD_DATABASE") {
        let s = LocalConfigurationService::new(Ok(PathBuf::from(path)));
        let snapshot = s.load().unwrap();
        assert_eq!(snapshot.revision, 3);
        assert_eq!(snapshot.document.mappings[0]["mappingKey"], "mapping");
        assert!(s.saved_preview("mappings:mapping", 3).unwrap()["request"].is_null());
        return;
    }
    let f = Fixture::new();
    let s = f.service();
    seed(&s);
    drop(s);
    let status = std::process::Command::new(std::env::current_exe().unwrap())
        .args([
            "--exact",
            "sqlite_snapshot_survives_a_real_os_process_boundary",
        ])
        .env("SMA004_OWNED_CHILD_DATABASE", f.path())
        .status()
        .unwrap();
    assert!(status.success());
}
#[cfg(unix)]
#[test]
fn readonly_sqlite_rejects_commit_without_recreating_or_fallback() {
    use std::os::unix::fs::PermissionsExt;
    let f = Fixture::new();
    let s = f.service();
    seed(&s);
    let before = s.load().unwrap();
    drop(s);
    std::fs::set_permissions(f.path(), std::fs::Permissions::from_mode(0o444)).unwrap();
    let reopened = f.service();
    let result = reopened.change(
        3,
        intent("upsert", "targetApis", target("blocked")),
        &idle(),
    );
    assert!(result.is_err());
    drop(reopened);
    std::fs::set_permissions(f.path(), std::fs::Permissions::from_mode(0o644)).unwrap();
    assert_eq!(f.service().load().unwrap(), before);
}
