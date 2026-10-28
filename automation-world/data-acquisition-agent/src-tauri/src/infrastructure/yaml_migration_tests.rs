//! cfg(test)迁入反例与原子边界；全部资源使用独立系统tmp，无设备或旧profile。
use super::*;
use crate::{domain::local_runtime::HistoryQuery, infrastructure::local_store::Stores};
use std::{
    process::Command,
    time::{Duration, Instant},
};
fn temp() -> PathBuf {
    let p = PathBuf::from("/private/tmp").join(format!("daa003-migration-{}", id()));
    fs::create_dir(&p).unwrap();
    fs::write(p.join(".owner"), "DAA-003-r1-test").unwrap();
    p
}
fn paths(p: &Path) -> MigrationPaths {
    MigrationPaths {
        points: p.join("points.yaml"),
        points_origin: "test".into(),
        policy: p.join("policy.yaml"),
        policy_origin: "test".into(),
    }
}
const YAML:&str="PLC_A:\n  ip: 127.0.0.1\n  groups:\n    - name: one\n      db_number: 1\n      start: 0\n      size: 8\n      points:\n        - {name: a, type: Real, offset: 0, readable: false, writable: true}\n    - name: two\n      db_number: 2\n      start: 0\n      size: 8\n      points:\n        - {name: a, type: Date_And_Time, offset: 0, length: 8}\nPLC_B:\n  ip: 127.0.0.2\n  port: 1102\n  rack: 0\n  slot: 1\n  groups: []\n";
fn candidate(p: &Path) -> Candidate {
    fs::write(p.join("points.yaml"), YAML).unwrap();
    discover(&paths(p))
}
#[test]
fn migration_all_objects_and_strict_boundaries() {
    let p = temp();
    let c = candidate(&p);
    assert_eq!(
        c.receipt.summary.status,
        "imported_with_diagnostics",
        "{}",
        encode(&c.receipt).unwrap()
    );
    assert_eq!(
        (
            c.configuration.plcs.len(),
            c.configuration.groups.len(),
            c.configuration.dbs.len(),
            c.configuration.points.len()
        ),
        (2, 2, 2, 2)
    );
    assert!(c.configuration.plcs.iter().all(|p| !p.enabled));
    assert!(c.configuration.groups.iter().all(|p| !p.enabled));
    assert!(c
        .configuration
        .dbs
        .iter()
        .all(|p| !p.complete && !p.flat && p.tree.is_empty()));
    assert!(c
        .configuration
        .points
        .iter()
        .all(|p| !p.enabled && p.group_id.is_some() && !p.address.as_ref().unwrap().confirmed));
    for bad in [
        "A: {ip: 127.0.0.1, ip: 127.0.0.2}",
        "A: &a {ip: 127.0.0.1}\nB: *a",
        "---\n{}\n---\n{}",
        "[one]",
        "A: {ip: 1, groups: []}",
        "A: {ip: 127.0.0.1, groups: typo}",
    ] {
        fs::write(&paths(&p).points, bad).unwrap();
        let c = discover(&paths(&p));
        assert_eq!(c.receipt.summary.status, "failed", "{bad}");
        assert!(c.configuration.plcs.is_empty());
    }
    fs::write(&paths(&p).points, "# empty\nnull\n").unwrap();
    assert_eq!(discover(&paths(&p)).receipt.summary.status, "skipped_empty");
    fs::write(
        &paths(&p).points,
        "A: {ip: 127.0.0.1, password: SECRET_MUST_NOT_COPY, groups: []}",
    )
    .unwrap();
    let c = discover(&paths(&p));
    assert!(!encode(&c.receipt).unwrap().contains("SECRET_MUST_NOT_COPY"));
    assert_eq!(c.configuration.plcs.len(), 1);
    fs::write(&paths(&p).points, vec![b'x'; SOURCE_LIMIT + 1]).unwrap();
    let c = discover(&paths(&p));
    assert_eq!(
        c.receipt.summary.error_code.as_deref(),
        Some("yaml_source_limit")
    );
    assert_eq!(
        c.receipt.summary.sources[0].hash_unavailable.as_deref(),
        Some("source_limit")
    );
    assert!(c.receipt.summary.sources[0].sha256.is_none());
}
#[test]
fn migration_receipt_cas_restart_and_existing_protection() {
    let p = temp();
    let mut s = Stores::open(&p.join("store")).unwrap();
    let etag = s.configuration().unwrap().etag;
    let c = candidate(&p);
    let result = s.commit_yaml(c, &etag, None).unwrap();
    let payload = s.configuration().unwrap().draft;
    let receipt = s.yaml_receipt().unwrap().unwrap();
    assert_eq!(receipt.ids.len(), 10);
    assert_eq!(
        s.config
            .query_row("SELECT count(*) FROM source_documents", [], |r| r
                .get::<_, i64>(0))
            .unwrap(),
        3
    );
    assert!(s.commit_yaml(discover(&paths(&p)), &etag, None).is_err());
    drop(s);
    fs::write(&paths(&p).points, "broken: [").unwrap();
    let mut s = Stores::open(&p.join("store")).unwrap();
    let state = crate::services::local_yaml_migration::startup(&mut s, Some(&paths(&p)));
    assert_eq!(state.attempt_id, result.attempt_id);
    assert_eq!(s.configuration().unwrap().draft, payload);
    assert_eq!(s.yaml_receipt().unwrap().unwrap().ids, receipt.ids);
    // Clearing the draft cannot cause another automatic scan or replace the successful receipt.
    let v = s.configuration().unwrap();
    s.save_draft(&Configuration::default(), &v.etag).unwrap();
    assert!(
        !crate::services::local_yaml_migration::startup(&mut s, Some(&paths(&p))).retry_allowed
    );
    let other = temp();
    let mut s = Stores::open(&other.join("store")).unwrap();
    let v = s.configuration().unwrap();
    let mut saved = v.draft;
    saved.storage.retention_days = 8;
    s.save_draft(&saved, &v.etag).unwrap();
    let original = s.configuration().unwrap().etag;
    let r = crate::services::local_yaml_migration::startup(&mut s, Some(&paths(&other)));
    assert_eq!(r.status, "existing_sqlite_preserved");
    assert!(r.sources.is_empty());
    assert_eq!(s.configuration().unwrap().etag, original);
}
// These hooks exist only in the private test build; production/validation have no fault inputs.
pub(crate) fn commit_boundary(tx: &rusqlite::Transaction<'_>, phase: &str) {
    if std::env::var("DAA003_MIGRATION_CHILD_PHASE").as_deref() == Ok(phase) {
        let p = child_path();
        tx.cache_flush().unwrap();
        fs::write(p.join("ready"), phase).unwrap();
        std::thread::sleep(Duration::from_secs(10));
        std::process::abort();
    }
}
pub(crate) fn after_commit_boundary() {
    if std::env::var("DAA003_MIGRATION_CHILD_PHASE").as_deref() == Ok("after") {
        let p = child_path();
        fs::write(p.join("ready"), "after").unwrap();
        std::thread::sleep(Duration::from_secs(10));
        std::process::abort();
    }
}
fn child_path() -> PathBuf {
    let p = PathBuf::from(std::env::var_os("DAA003_MIGRATION_CHILD_DIR").unwrap());
    let p = p.canonicalize().unwrap();
    assert!(
        p.starts_with("/private/tmp")
            && p.file_name()
                .unwrap()
                .to_str()
                .unwrap()
                .starts_with("daa003-migration-")
    );
    assert_eq!(
        fs::read_to_string(p.join(".owner")).unwrap(),
        "DAA-003-r1-test"
    );
    p
}
#[test]
#[ignore]
fn migration_crash_child() {
    let p = child_path();
    let mut s = Stores::open(&p.join("store")).unwrap();
    let etag = s.configuration().unwrap().etag;
    s.commit_yaml(candidate(&p), &etag, None).unwrap();
}
#[test]
fn migration_commit_before_after_process_reopen() {
    for phase in ["before", "after"] {
        let p = temp();
        let mut child = Command::new(std::env::current_exe().unwrap())
            .args([
                "--exact",
                "infrastructure::yaml_migration::tests::migration_crash_child",
                "--ignored",
                "--nocapture",
            ])
            .env("DAA003_MIGRATION_CHILD_DIR", &p)
            .env("DAA003_MIGRATION_CHILD_PHASE", phase)
            .spawn()
            .unwrap();
        let start = Instant::now();
        while !p.join("ready").exists() {
            assert!(start.elapsed() < Duration::from_secs(8));
            std::thread::sleep(Duration::from_millis(20));
        }
        child.kill().unwrap();
        let status = child.wait().unwrap();
        assert!(!status.success());
        let s = Stores::open(&p.join("store")).unwrap();
        if phase == "before" {
            assert!(s.configuration().unwrap().draft.plcs.is_empty());
            assert!(s.yaml_receipt().unwrap().is_none());
        } else {
            assert_eq!(s.configuration().unwrap().draft.plcs.len(), 2);
            assert!(s.yaml_receipt().unwrap().is_some());
        }
        assert_eq!(
            s.runtime
                .query_row("SELECT count(*) FROM samples", [], |r| r.get::<_, i64>(0))
                .unwrap(),
            0
        );
    }
}
#[test]
fn migration_policy_limits_duplicates_and_file_safety() {
    let p = temp();
    let paths = paths(&p);
    fs::write(&paths.policy,"P:\n  snapshot_policy_version: 2\n  groups:\n    - group_name: g\n      db_number: 2\n      points:\n        - {name: a, raw_enabled: false, raw_policy: hourly, latest_enabled: true}\n").unwrap();
    let c = discover(&paths);
    assert_eq!(c.receipt.summary.status, "archived_policy_only");
    assert_eq!(c.receipt.summary.counts.policy_points, 1);
    assert!(c.configuration.plcs.is_empty());
    fs::write(&paths.policy, "P: {snapshot_policy_version: 3, groups: []}").unwrap();
    assert_eq!(discover(&paths).receipt.summary.status, "failed");
    fs::remove_file(&paths.policy).unwrap();
    let duplicate = YAML.replace("db_number: 2", "db_number: 1").replace(
        "type: Date_And_Time, offset: 0, length: 8",
        "type: Real, offset: 0",
    );
    fs::write(&paths.points, &duplicate).unwrap();
    assert_eq!(
        discover(&paths).receipt.summary.error_code.as_deref(),
        Some("yaml_duplicate_semantic_point")
    );
    fs::write(
        &paths.points,
        duplicate.replace("type: Real, offset: 0}", "type: Real, offset: 4}"),
    )
    .unwrap(); // distinct address retains both source identities
    assert_eq!(discover(&paths).configuration.points.len(), 2);
    fs::write(&paths.points,"A: {ip: 127.0.0.1}\nB: {ip: 127.0.0.2}\nC: {ip: 127.0.0.3}\nD: {ip: 127.0.0.4}\nE: {ip: 127.0.0.5}\n").unwrap();
    assert_eq!(
        discover(&paths).receipt.summary.error_code.as_deref(),
        Some("yaml_plc_limit")
    );
    fs::write(&paths.points, [0xff, 0xfe]).unwrap();
    assert_eq!(
        discover(&paths).receipt.summary.error_code.as_deref(),
        Some("yaml_utf8_required")
    );
    fs::remove_file(&paths.points).unwrap();
    #[cfg(unix)]
    {
        std::os::unix::fs::symlink(&paths.policy, &paths.points).unwrap();
        assert_eq!(
            discover(&paths).receipt.summary.error_code.as_deref(),
            Some("yaml_symlink")
        );
        fs::remove_file(&paths.points).unwrap();
    }
    fs::create_dir(&paths.points).unwrap();
    assert_eq!(
        discover(&paths).receipt.summary.error_code.as_deref(),
        Some("yaml_regular_file_required")
    );
    fs::remove_dir(&paths.points).unwrap();
    fs::write(&paths.points, YAML).unwrap();
    let source = read(&paths.points, "points", "test").ok().unwrap();
    fs::write(&paths.points, "changed").unwrap();
    assert_eq!(unchanged(&source).unwrap_err(), "yaml_source_changed");
    let deep = format!("{}null{}", "[".repeat(17), "]".repeat(17));
    assert!(parse(&deep).is_err());
    assert!(parse("!!str 123").is_err());
    let mut diagnostic = MigrationSummary::state("failed");
    for _ in 0..500 {
        diagnostic.diagnostic("test", "safe");
    }
    assert_eq!(
        (
            diagnostic.diagnostics.len(),
            diagnostic.diagnostic_total,
            diagnostic.diagnostic_omitted
        ),
        (200, 500, 300)
    );
}
#[test]
fn migration_empty_retry_cas_capacity_lock_and_private_protection() {
    let p = temp();
    let paths = paths(&p);
    let mut s = Stores::open(&p.join("store")).unwrap();
    let first = crate::services::local_yaml_migration::startup(&mut s, Some(&paths));
    assert_eq!(first.status, "skipped_empty");
    let v = s.configuration().unwrap();
    let attempt = first.attempt_id.unwrap();
    fs::write(&paths.points, YAML).unwrap();
    let skipped = crate::services::local_yaml_migration::startup(&mut s, Some(&paths));
    assert_eq!(skipped.status, "skipped_empty");
    assert_eq!(s.configuration().unwrap().etag, v.etag);
    assert_eq!(
        s.commit_yaml(discover(&paths), "stale", Some(&attempt))
            .unwrap_err(),
        "draft_conflict"
    );
    assert_eq!(
        s.commit_yaml(discover(&paths), &v.etag, Some("stale"))
            .unwrap_err(),
        "yaml_attempt_conflict"
    );
    let meter = std::sync::Arc::new(std::sync::atomic::AtomicU64::new(0));
    s.test_meter = Some((
        meter.clone(),
        std::sync::Arc::new(std::sync::atomic::AtomicU64::new(0)),
    ));
    assert_eq!(
        s.commit_yaml(discover(&paths), &v.etag, Some(&attempt))
            .unwrap_err(),
        "configuration_capacity"
    );
    s.test_meter = None;
    assert_eq!(s.configuration().unwrap().etag, v.etag);
    let reader = rusqlite::Connection::open(p.join("store/config.sqlite")).unwrap();
    reader
        .execute_batch("BEGIN; SELECT * FROM configuration_draft;")
        .unwrap();
    assert_eq!(
        s.commit_yaml(discover(&paths), &v.etag, Some(&attempt))
            .unwrap_err(),
        "storage_busy"
    );
    reader.execute_batch("ROLLBACK").unwrap();
    assert_eq!(s.configuration().unwrap().etag, v.etag);
    let done = s
        .commit_yaml(discover(&paths), &v.etag, Some(&attempt))
        .unwrap();
    assert!(!done.retry_allowed);
    assert!(!s.yaml_empty().unwrap());
    let mut forged = s.configuration().unwrap().draft;
    forged.sources[0].name = PRIVATE_NAME.into();
    assert_eq!(
        s.save_draft(&forged, &s.configuration().unwrap().etag)
            .unwrap_err(),
        "yaml_private_source"
    );
    let original = s.yaml_receipt().unwrap().unwrap();
    s.config
        .execute(
            "UPDATE source_documents SET content='{}' WHERE name=?1",
            [PRIVATE_NAME],
        )
        .unwrap();
    assert_eq!(s.yaml_receipt().unwrap_err(), "yaml_receipt_corrupt");
    assert_eq!(original.summary.status, "imported_with_diagnostics");
    let lock = crate::infrastructure::local_profile_lock::ProfileLock::acquire(&p).unwrap();
    assert!(crate::infrastructure::local_profile_lock::ProfileLock::acquire(&p).is_err());
    drop(lock);
    assert!(crate::infrastructure::local_profile_lock::ProfileLock::acquire(&p).is_ok());
}
#[test]
fn migration_private_record_survives_pruning_and_source_collision_rolls_back() {
    let p = temp();
    let mut s = Stores::open(&p.join("store")).unwrap();
    let c = candidate(&p);
    let etag = s.configuration().unwrap().etag;
    s.commit_yaml(c, &etag, None).unwrap();
    let before = encode(&s.yaml_receipt().unwrap().unwrap()).unwrap();
    s.yaml_test_prune().unwrap();
    assert_eq!(encode(&s.yaml_receipt().unwrap().unwrap()).unwrap(), before);
    let other = temp();
    let mut s = Stores::open(&other.join("store")).unwrap();
    let mut c = candidate(&other);
    c.configuration.sources[1].sha256 = c.configuration.sources[0].sha256.clone();
    let v = s.configuration().unwrap();
    assert_eq!(
        s.commit_yaml(c, &v.etag, None).unwrap_err(),
        "yaml_source_hash_conflict"
    );
    assert_eq!(s.configuration().unwrap().etag, v.etag);
    assert!(s.configuration().unwrap().draft.plcs.is_empty());
    assert!(s.yaml_receipt().unwrap().is_none());
}
#[test]
fn migration_two_plcs_multidb_policy_independent_expected() {
    let p = temp();
    let paths = paths(&p);
    let yaml="P1:\n  ip: 127.0.0.1\n  groups:\n    - name: int_group\n      db_number: 1\n      start: 0\n      size: 4\n      points: [{name: same, type: Int, offset: 2, readable: false}]\n    - name: bool_group\n      db_number: 2\n      start: 0\n      size: 4\n      points: [{name: same, type: Bool, offset: 1, bit: 7}]\nP2:\n  ip: 127.0.0.2\n  groups:\n    - name: int_group\n      db_number: 3\n      start: 0\n      size: 8\n      points: [{name: same, type: Int, offset: 4}]\n    - name: bool_group\n      db_number: 4\n      start: 0\n      size: 8\n      points: [{name: same, type: Bool, offset: 3, bit: 2}]\n";
    fs::write(&paths.points, yaml).unwrap();
    fs::write(&paths.policy,"P1:\n  snapshot_policy_version: 2\n  groups:\n    - name: int_group\n      db_number: 1\n      points: [{name: same, raw_enabled: true, raw_policy: on_change, latest_enabled: false}]\n    - group_name: bool_group\n      db_number: 2\n      points: [{name: same, raw_enabled: false, raw_policy: hourly, latest_enabled: true}]\nP2:\n  snapshot_policy_version: 2\n  groups:\n    - name: int_group\n      db_number: 3\n      points: [{name: same, raw_enabled: false, raw_policy: every_sample, latest_enabled: false}]\n    - name: bool_group\n      db_number: 4\n      points: [{name: same, raw_enabled: true, raw_policy: every_sample, latest_enabled: true}]\n").unwrap();
    let c = discover(&paths);
    let cc = &c.configuration;
    assert_eq!(
        (
            cc.plcs.len(),
            cc.dbs.len(),
            cc.groups.len(),
            cc.points.len(),
            cc.sources.len()
        ),
        (2, 4, 4, 4, 2)
    );
    assert_eq!(
        (
            c.receipt.summary.counts.policy_plcs,
            c.receipt.summary.counts.policy_groups,
            c.receipt.summary.counts.policy_points
        ),
        (2, 4, 4)
    );
    let expected = [
        ("P1", 1, "INT", 2, None),
        ("P1", 2, "BOOL", 1, Some(7)),
        ("P2", 3, "INT", 4, None),
        ("P2", 4, "BOOL", 3, Some(2)),
    ];
    for (name, num, typ, offset, bit) in expected {
        let plc = cc.plcs.iter().find(|p| p.name == name).unwrap();
        let db = cc
            .dbs
            .iter()
            .find(|d| d.plc_id == plc.id && d.number == num)
            .unwrap();
        let point = cc.points.iter().find(|p| p.db_id == db.id).unwrap();
        let a = point.address.as_ref().unwrap();
        assert_eq!((&*point.data_type, a.offset, a.bit), (typ, offset, bit));
        assert!(!plc.enabled && !point.enabled && !a.confirmed && !db.complete && !db.flat);
        assert!(point.group_id.is_some());
    }
    let archive = encode(&c.receipt.archive).unwrap();
    assert_eq!(archive.matches("\"matched\"").count(), 4);
    assert_eq!(c.receipt.ids.len(), 16);
}
#[test]
fn resident_retirement_empty_engine_ignores_locators_and_retry_is_read_only() {
    let p = std::env::temp_dir().join(format!("resident-empty-{}", id()));
    fs::create_dir(&p).unwrap();
    let locators = paths(&p);
    // 旧locator即使指向目录/非法YAML，也不能在普通engine打开或summary中探测。
    fs::create_dir(&locators.points).unwrap();
    fs::write(&locators.policy, "broken: [").unwrap();
    let b = crate::config::local_bootstrap::Bootstrap {
        mode: "local_sqlite".into(),
        profile: p.clone(),
        read_allowed: true,
        validation: false,
        migration: Some(locators),
        ignored_keys: vec![],
        fixture: None,
    };
    let e = crate::services::local_supervisor::LocalEngine::open(b).unwrap();
    let v = e.configuration().unwrap();
    assert_eq!(v.draft, Configuration::default());
    assert!(v.active.is_none() && e.states.lock().unwrap().is_empty());
    let before = e
        .storage
        .call(true, |s| {
            Ok((
                s.configuration()?.etag,
                s.config
                    .query_row("SELECT count(*) FROM source_documents", [], |r| {
                        r.get::<_, i64>(0)
                    })
                    .unwrap(),
            ))
        })
        .unwrap();
    let db = p.join("local-acquisition-v1/config.sqlite");
    let bytes = fs::read(&db).unwrap();
    let summary = e.yaml_migration().unwrap();
    assert_eq!(summary.status, "not_attempted");
    assert!(!summary.retry_allowed && summary.attempt_id.is_none());
    assert_eq!(
        e.retry_yaml("stale".into(), "stale".into()).unwrap_err(),
        "yaml_retry_forbidden"
    );
    assert_eq!(fs::read(&db).unwrap(), bytes);
    assert_eq!(e.configuration().unwrap().etag, before.0);
    assert_eq!(before.1, 0);
    assert!(e.history(HistoryQuery::default()).unwrap()["items"]
        .as_array()
        .unwrap()
        .is_empty());
    e.shutdown();
    drop(e);
    fs::remove_dir_all(p).unwrap();
}

#[test]
fn resident_retirement_existing_receipt_and_source_bytes_survive_save_prune() {
    let p = std::env::temp_dir().join(format!("resident-receipt-{}", id()));
    fs::create_dir(&p).unwrap();
    let dir = p.join("local-acquisition-v1");
    let mut stores = Stores::open(&dir).unwrap();
    let etag = stores.configuration().unwrap().etag;
    stores.commit_yaml(candidate(&p), &etag, None).unwrap();
    let before: Vec<(String, String, String)> = stores
        .config
        .prepare("SELECT id,sha256,content FROM source_documents ORDER BY id")
        .unwrap()
        .query_map([], |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?)))
        .unwrap()
        .collect::<Result<_, _>>()
        .unwrap();
    let saved = stores.configuration().unwrap();
    drop(stores);
    let e = crate::services::local_supervisor::LocalEngine::open(
        crate::config::local_bootstrap::Bootstrap {
            mode: "local_sqlite".into(),
            profile: p.clone(),
            read_allowed: true,
            validation: false,
            migration: None,
            ignored_keys: vec![],
            fixture: None,
        },
    )
    .unwrap();
    let summary = e.yaml_migration().unwrap();
    assert_eq!(summary.status, "imported_with_diagnostics");
    assert!(!summary.retry_allowed);
    assert_eq!(e.configuration().unwrap().etag, saved.etag);
    assert_eq!(
        e.retry_yaml(saved.etag, summary.attempt_id.unwrap())
            .unwrap_err(),
        "yaml_retry_forbidden"
    );
    e.storage
        .call(false, |s| {
            let v = s.configuration()?;
            let mut draft = v.draft;
            draft.storage.retention_days = 8;
            s.save_draft(&draft, &v.etag)?;
            s.yaml_test_prune()
        })
        .unwrap();
    let after: Vec<(String, String, String)> = e
        .storage
        .call(true, |s| {
            Ok(s.config
                .prepare("SELECT id,sha256,content FROM source_documents ORDER BY id")
                .unwrap()
                .query_map([], |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?)))
                .unwrap()
                .collect::<Result<_, _>>()
                .unwrap())
        })
        .unwrap();
    assert_eq!(after, before);
    e.shutdown();
    drop(e);
    fs::remove_dir_all(p).unwrap();
}

#[test]
fn migration_historical_storage_failure() {
    let p = temp();
    let mut s = Stores::open(&p.join("store")).unwrap();
    let v = s.configuration().unwrap();
    fs::create_dir(p.join("store/logs/runtime.jsonl")).unwrap();
    let result = crate::services::local_yaml_migration::startup(&mut s, Some(&paths(&p)));
    assert_eq!(result.status, "failed");
    assert_eq!(result.status_persistence, "unknown");
    assert!(s.yaml_receipt().unwrap().is_none());
    assert_eq!(s.configuration().unwrap().etag, v.etag);
    assert!(s.log.health().is_err());
}
#[test]
fn migration_existing_runtime_source_and_policy_preserved_without_source_read() {
    let p = temp();
    let mut s = Stores::open(&p.join("store")).unwrap();
    let plc = id();
    let generation = id();
    s.runtime
        .execute(
            "INSERT INTO plc_sources VALUES(?1,?2,42)",
            rusqlite::params![plc, generation],
        )
        .unwrap();
    let v = s.configuration().unwrap();
    let paths = paths(&p);
    fs::create_dir(&paths.points).unwrap();
    let summary = crate::services::local_yaml_migration::startup(&mut s, Some(&paths));
    assert_eq!(summary.status, "existing_sqlite_preserved");
    assert!(summary.sources.is_empty());
    assert_eq!(s.configuration().unwrap().etag, v.etag);
    assert_eq!(
        s.runtime
            .query_row(
                "SELECT generation,next_seq FROM plc_sources WHERE plc_id=?1",
                [plc],
                |r| Ok((r.get::<_, String>(0)?, r.get::<_, i64>(1)?))
            )
            .unwrap(),
        (generation, 42)
    );
}

#[test]
fn migration_document_empty_forms() {
    for s in [
        "",
        "# comment",
        "null",
        "~",
        "{}",
        "[]",
        "---\n",
        "---\n...\n",
    ] {
        assert!(empty(&parse(s).unwrap()), "{s}");
    }
}
#[test]
fn migration_group_point_and_node_limits_are_atomic() {
    let p = temp();
    let locators = paths(&p);
    let mut yaml = String::from("P: {ip: 127.0.0.1, groups: [");
    for n in 1..=9 {
        yaml.push_str(&format!(
            "{{name: g{n}, db_number: {n}, start: 0, size: 1, points: []}},"
        ));
    }
    yaml.push_str("]}");
    fs::write(&locators.points, &yaml).unwrap();
    let c = discover(&locators);
    assert_eq!(
        c.receipt.summary.error_code.as_deref(),
        Some("yaml_group_limit")
    );
    assert!(c.configuration.groups.is_empty());
    let mut yaml=String::from("P:\n  ip: 127.0.0.1\n  groups:\n    - name: g\n      db_number: 1\n      start: 0\n      size: 65536\n      points:\n");
    for n in 0..4097 {
        yaml.push_str(&format!(
            "        - {{name: p{n}, type: Byte, offset: {n}}}\n"
        ));
    }
    assert!(yaml.len() < SOURCE_LIMIT);
    fs::write(&locators.points, yaml).unwrap();
    let c = discover(&locators);
    assert_eq!(
        c.receipt.summary.error_code.as_deref(),
        Some("yaml_point_limit")
    );
    assert!(c.configuration.points.is_empty());
    assert!(c.receipt.ids.is_empty());
    let nodes = format!("[{}]", "null,".repeat(100001));
    assert!(parse(&nodes).is_err());
}
