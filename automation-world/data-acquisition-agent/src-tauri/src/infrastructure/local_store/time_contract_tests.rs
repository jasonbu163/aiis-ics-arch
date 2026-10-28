//! DAA-007定向时间合同验证：仅自造profile，实际Stores与原字节路径，无监听/网络/默认库访问。
use super::*;
use crate::domain::business_time as time;
use std::collections::BTreeMap;
fn owned() -> PathBuf {
    let dir =
        PathBuf::from("/private/tmp/daa-007-r1-exec-e6s14xue").join(format!("dev-test-{}", id()));
    std::fs::create_dir_all(&dir).unwrap();
    dir
}
fn tree(dir: &Path) -> BTreeMap<String, String> {
    fn visit(root: &Path, dir: &Path, out: &mut BTreeMap<String, String>) {
        for entry in std::fs::read_dir(dir).unwrap() {
            let path = entry.unwrap().path();
            let key = path
                .strip_prefix(root)
                .unwrap()
                .to_string_lossy()
                .into_owned();
            if path.is_dir() {
                out.insert(key, "directory".into());
                visit(root, &path, out);
            } else {
                use sha2::{Digest, Sha256};
                out.insert(
                    key,
                    format!("{:x}", Sha256::digest(std::fs::read(path).unwrap())),
                );
            }
        }
    }
    let mut out = BTreeMap::new();
    visit(dir, dir, &mut out);
    out
}
fn boot(profile: PathBuf) -> Bootstrap {
    Bootstrap {
        mode: "local_sqlite".into(),
        profile,
        read_allowed: false,
        validation: false,
        migration: None,
        ignored_keys: vec![],
        fixture: None,
    }
}
fn reject_unchanged(profile: &Path) {
    let before = tree(profile);
    let error = match LocalEngine::open(boot(profile.into())) {
        Ok(_) => panic!("unsupported accepted"),
        Err(e) => e,
    };
    assert!(error.starts_with("time_profile_unsupported:"), "{error}");
    assert_eq!(before, tree(profile));
    assert!(!profile.join(".daa-runtime.lock").exists());
}
#[test]
fn time_contract_legacy_unknown_single_and_identity_reject_before_lock() {
    for variant in [
        "legacy",
        "unknown",
        "missing",
        "identity",
        "journal",
        "wal_header",
    ] {
        let profile = owned();
        let dir = profile.join("local-acquisition-v1");
        if variant == "legacy" {
            std::fs::create_dir(&dir).unwrap();
            for (name, app, table) in [
                ("config.sqlite", schema::CONFIG_APP, "instance_metadata"),
                ("runtime.sqlite", schema::RUNTIME_APP, "runtime_metadata"),
            ] {
                let c = Connection::open(dir.join(name)).unwrap();
                c.execute_batch(&format!("PRAGMA application_id={app}; PRAGMA user_version=1; CREATE TABLE {table}(id INTEGER PRIMARY KEY,instance_id TEXT,schema_version INTEGER); INSERT INTO {table} VALUES(1,'{}',1);", id())).unwrap();
            }
        } else {
            let mut stores = Stores::open(&dir).unwrap();
            stores.clean_exit().unwrap();
            drop(stores);
            let c = Connection::open(dir.join("runtime.sqlite")).unwrap();
            if variant == "unknown" {
                c.execute_batch("PRAGMA ignore_check_constraints=ON; UPDATE runtime_metadata SET time_profile='unknown'").unwrap();
            }
            if variant == "identity" {
                c.execute("UPDATE runtime_metadata SET instance_id=?1", [id()])
                    .unwrap();
            }
            drop(c);
            if variant == "wal_header" {
                let path = dir.join("runtime.sqlite");
                let mut bytes = std::fs::read(&path).unwrap();
                bytes[18] = 2;
                bytes[19] = 2;
                std::fs::write(path, bytes).unwrap();
            }
            if variant == "missing" {
                std::fs::remove_file(dir.join("runtime.sqlite")).unwrap();
            }
            if variant == "journal" {
                std::fs::write(dir.join("runtime.sqlite-wal"), b"untrusted").unwrap();
            }
        }
        reject_unchanged(&profile);
        std::fs::remove_dir_all(profile).unwrap();
    }
}
#[test]
fn time_contract_lock_second_check_detects_empty_and_valid_drift_before_rw() {
    for mode in ["empty", "version", "bytes"] {
        let existing = mode != "empty";
        let profile = owned();
        let dir = profile.join("local-acquisition-v1");
        if existing {
            let mut s = Stores::open(&dir).unwrap();
            s.clean_exit().unwrap();
            drop(s);
        }
        let check = preflight(&dir).unwrap();
        let lock =
            crate::infrastructure::local_profile_lock::ProfileLock::acquire(&profile).unwrap();
        if existing {
            let c = Connection::open(dir.join("runtime.sqlite")).unwrap();
            if mode == "version" {
                c.execute_batch("PRAGMA user_version=9").unwrap();
            } else {
                c.execute_batch("UPDATE runtime_metadata SET clean_exit=0")
                    .unwrap();
            }
        } else {
            std::fs::create_dir(&dir).unwrap();
            std::fs::write(dir.join("unexpected"), b"drift").unwrap();
        }
        let before = tree(&profile);
        let error = check.recheck(&dir).unwrap_err();
        assert!(error.starts_with("time_profile_unsupported:"));
        if mode == "bytes" {
            assert_eq!(error, "time_profile_unsupported:profile_changed");
        }
        assert_eq!(before, tree(&profile));
        assert!(profile.join(".daa-runtime.lock").exists());
        drop(lock);
        std::fs::remove_dir_all(profile).unwrap();
    }
}
fn input(c: &Configuration, revision: &str, started: &str) -> CycleInput {
    let plc = &c.plcs[0];
    let group = &c.groups[0];
    let mut points: BTreeMap<u16, BTreeMap<String, PointFact>> = BTreeMap::new();
    for p in c
        .points
        .iter()
        .filter(|p| p.plc_id == plc.id && p.group_id.as_deref() == Some(&group.id))
    {
        let db = c.dbs.iter().find(|d| d.id == p.db_id).unwrap();
        points.entry(db.number).or_default().insert(
            p.id.clone(),
            PointFact {
                definition: p.clone(),
                value: json!(false),
                observed_at: started.into(),
                quality: "good".into(),
                reason: None,
            },
        );
    }
    CycleInput {
        plc_id: plc.id.clone(),
        group_id: group.id.clone(),
        revision: revision.into(),
        started_at: started.into(),
        finished_at: started.into(),
        origin: "synthetic_time_contract".into(),
        points,
        reads: vec![ReadTiming {
            db_number: 1,
            start: 0,
            size: 1,
            started_at: started.into(),
            finished_at: started.into(),
            duration_ms: 0,
            quality: "good".into(),
        }],
    }
}
fn query(from: Option<&str>, to: Option<&str>) -> HistoryQuery {
    HistoryQuery {
        cursor: None,
        limit: Some(100),
        plc_id: None,
        group_id: None,
        quality: None,
        from: from.map(str::to_string),
        to: to.map(str::to_string),
    }
}
#[test]
fn time_contract_new_v2_matrix_payload_sha_query_and_retention() {
    let profile = owned();
    let dir = profile.join("local-acquisition-v1");
    let mut s = Stores::open(&dir).unwrap();
    for (c, table) in [
        (&s.config, "instance_metadata"),
        (&s.runtime, "runtime_metadata"),
    ] {
        assert_eq!(
            c.query_row("PRAGMA user_version", [], |r| r.get::<_, i64>(0))
                .unwrap(),
            2
        );
        assert_eq!(
            c.query_row(
                &format!("SELECT schema_version,time_profile FROM {table}"),
                [],
                |r| Ok((r.get::<_, i64>(0)?, r.get::<_, String>(1)?))
            )
            .unwrap(),
            (2, time::TIME_PROFILE.into())
        );
        let (v, at): (i64, String) = c
            .query_row(
                "SELECT version,applied_at FROM schema_migrations",
                [],
                |r| Ok((r.get(0)?, r.get(1)?)),
            )
            .unwrap();
        assert_eq!(v, 2);
        assert_eq!(at, time::normalize(&at).unwrap());
    }
    let c = configuration();
    let r = activated(&mut s, &c);
    for table in ["configuration_revisions", "activation_intents"] {
        let at: String = s
            .config
            .query_row(
                &format!("SELECT created_at FROM {table} LIMIT 1"),
                [],
                |r| r.get(0),
            )
            .unwrap();
        assert_eq!(at, time::normalize(&at).unwrap());
    }
    let result = s
        .commit_cycle(input(&c, &r, "2026-10-22T16:00:00.123Z"))
        .unwrap();
    let rows = s.history(query(None, None)).unwrap();
    assert_eq!(rows["schemaVersion"], 1);
    assert_eq!(rows["items"].as_array().unwrap().len(), 2);
    let sample = rows["items"][0]["sampleId"].as_str().unwrap();
    let raw = s.sample(sample).unwrap();
    for (key, hash, version) in [
        ("payload", "sha256", 2),
        ("manifest", "manifestSha256", 2),
        ("context", "contextSha256", 1),
    ] {
        let text = raw[key].as_str().unwrap();
        assert_eq!(digest(text), raw[hash]);
        assert_eq!(
            serde_json::from_str::<Value>(text).unwrap()["schemaVersion"],
            version
        );
    }
    let payload: Value = serde_json::from_str(raw["payload"].as_str().unwrap()).unwrap();
    assert_eq!(payload["startedAt"], "2026-10-23T00:00:00.123+08:00");
    assert_eq!(payload["savedAt"], result["savedAt"]);
    let saved = result["savedAt"].as_str().unwrap();
    let utc = chrono::DateTime::parse_from_rfc3339(saved)
        .unwrap()
        .with_timezone(&chrono::Utc)
        .to_rfc3339_opts(chrono::SecondsFormat::Millis, true);
    assert_eq!(
        s.history(query(Some(&utc), Some(&utc))).unwrap()["items"]
            .as_array()
            .unwrap()
            .len(),
        2
    );
    assert!(s
        .history(query(
            Some("2026-10-23T00:00:01+08:00"),
            Some("2026-10-22T16:00:00Z")
        ))
        .is_err());
    assert!(s.history(query(Some("invalid"), None)).is_err());
    let instant = chrono::DateTime::parse_from_rfc3339(saved).unwrap();
    let before = (instant - chrono::Duration::milliseconds(1)).to_rfc3339();
    let after = (instant + chrono::Duration::milliseconds(1)).to_rfc3339();
    assert!(s.history(query(None, Some(&before))).unwrap()["items"]
        .as_array()
        .unwrap()
        .is_empty());
    assert!(s.history(query(Some(&after), None)).unwrap()["items"]
        .as_array()
        .unwrap()
        .is_empty());
    let mut first_query = query(None, None);
    first_query.limit = Some(1);
    let first_page = s.history(first_query).unwrap();
    let mut next_query = query(None, None);
    next_query.limit = Some(1);
    next_query.cursor = first_page["nextCursor"].as_i64();
    let next_page = s.history(next_query).unwrap();
    assert_eq!(next_page["items"].as_array().unwrap().len(), 1);
    assert_ne!(
        first_page["items"][0]["sampleId"],
        next_page["items"][0]["sampleId"]
    );
    let mut bad_query = query(None, None);
    bad_query.quality = Some("bad".into());
    assert!(s.history(bad_query).unwrap()["items"]
        .as_array()
        .unwrap()
        .is_empty());
    assert_eq!(s.sample(sample).unwrap()["payload"], raw["payload"]);
    // Pure synthetic old cycles: a strictly older acknowledged cycle is eligible, pending stays protected.
    s.runtime
        .execute(
            "UPDATE collection_cycles SET saved_at='2000-01-01T00:00:00.999+08:00'",
            [],
        )
        .unwrap();
    assert_eq!(s.cleanup_acknowledged(1, c.storage.quota_bytes).unwrap(), 0);
    s.runtime
        .execute("UPDATE sample_delivery SET state='acknowledged'", [])
        .unwrap();
    s.cleanup_cursor = 0;
    assert_eq!(s.cleanup_acknowledged(1, c.storage.quota_bytes).unwrap(), 2);
    s.event("time_contract", "test", "ok").unwrap();
    let logs = s.logs(0, 10).unwrap();
    let event_at = logs["items"].as_array().unwrap().last().unwrap()["createdAt"]
        .as_str()
        .unwrap();
    assert_eq!(event_at, time::normalize(event_at).unwrap());
    s.clean_exit().unwrap();
    let instance = s.instance.clone();
    drop(s);
    let mut reopened = Stores::open(&dir).unwrap();
    assert_eq!(reopened.instance, instance);
    reopened.clean_exit().unwrap();
    drop(reopened);
    std::fs::remove_dir_all(profile).unwrap();
}
#[test]
fn time_contract_cross_day_milliseconds_offsets_and_logging_precision() {
    assert_eq!(
        time::normalize("2026-10-22T16:00:00.9999Z").unwrap(),
        "2026-10-23T00:00:00.999+08:00"
    );
    assert_eq!(
        time::normalize("2026-10-22T12:00:00.123-04:00").unwrap(),
        "2026-10-23T00:00:00.123+08:00"
    );
    assert!(time::normalize("2026-10-23T00:00:00").is_err());
    assert_eq!(
        time::retention_cutoff("2026-10-23T00:00:00.999+08:00", 1).unwrap(),
        "2026-10-22T00:00:00.999+08:00"
    );
    let profile = owned();
    let log = crate::infrastructure::local_logging::LocalLog::new(profile.join("logs")).unwrap();
    log.event("time_contract", "log", "ok").unwrap();
    let line = std::fs::read_to_string(profile.join("logs/runtime.jsonl")).unwrap();
    let value: Value = serde_json::from_str(line.trim()).unwrap();
    let at = value["at"].as_str().unwrap();
    assert_eq!(at, time::normalize(at).unwrap());
    let diagnostic = time::diagnostic_now();
    assert!(diagnostic.ends_with("+08:00"));
    assert_eq!(
        diagnostic
            .split('.')
            .nth(1)
            .unwrap()
            .split('+')
            .next()
            .unwrap()
            .len(),
        9
    );
    drop(log);
    std::fs::remove_dir_all(profile).unwrap();
}
