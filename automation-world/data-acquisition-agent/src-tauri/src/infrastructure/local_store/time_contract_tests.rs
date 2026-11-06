//! DAA-007/008定向时间与投递预算验证：仅自造profile，实际Stores与原字节路径，无监听/网络/默认库访问。
use super::*;
use crate::domain::business_time as time;
use std::collections::BTreeMap;
fn owned() -> PathBuf {
    let root = std::env::temp_dir().canonicalize().unwrap();
    assert!(root.starts_with("/private/tmp") && root.to_string_lossy().contains("daa-008-r1-a-"));
    let dir = root.join(format!("time-contract-{}", id()));
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
        "config_structure",
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
            if variant == "config_structure" {
                Connection::open(dir.join("config.sqlite"))
                    .unwrap()
                    .execute_batch("DROP TABLE configuration_draft")
                    .unwrap();
            }
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
fn time_contract_new_config2_runtime3_payload_sha_query_and_retention() {
    let profile = owned();
    let dir = profile.join("local-acquisition-v1");
    let mut s = Stores::open(&dir).unwrap();
    for (c, table, expected) in [
        (&s.config, "instance_metadata", 2),
        (&s.runtime, "runtime_metadata", 3),
    ] {
        assert_eq!(
            c.query_row("PRAGMA user_version", [], |r| r.get::<_, i64>(0))
                .unwrap(),
            expected
        );
        assert_eq!(
            c.query_row(
                &format!("SELECT schema_version,time_profile FROM {table}"),
                [],
                |r| Ok((r.get::<_, i64>(0)?, r.get::<_, String>(1)?))
            )
            .unwrap(),
            (expected, time::TIME_PROFILE.into())
        );
        let (v, at): (i64, String) = c
            .query_row(
                "SELECT version,applied_at FROM schema_migrations",
                [],
                |r| Ok((r.get(0)?, r.get(1)?)),
            )
            .unwrap();
        assert_eq!(v, expected);
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

#[test]
fn v2_keeps_schema_configuration_history_ids_sequence_and_pending() {
    use crate::infrastructure::local_store::delivery_tests::{fresh, seed};
    let mut s = fresh();
    let dir = s.dir.clone();
    s.clean_exit().unwrap();
    drop(s);
    std::fs::remove_file(dir.join("runtime.sqlite")).unwrap();
    std::fs::remove_dir_all(dir.join("logs")).unwrap();
    let config = rusqlite::Connection::open(dir.join("config.sqlite")).unwrap();
    let instance: String = config
        .query_row("SELECT instance_id FROM instance_metadata", [], |r| {
            r.get(0)
        })
        .unwrap();
    drop(config);
    let runtime = rusqlite::Connection::open(dir.join("runtime.sqlite")).unwrap();
    runtime
        .execute_batch(
            "PRAGMA page_size=4096;PRAGMA auto_vacuum=INCREMENTAL;PRAGMA journal_mode=DELETE;",
        )
        .unwrap();
    runtime.execute_batch(&schema::runtime_sql()).unwrap();
    runtime
        .execute(
            "INSERT INTO runtime_metadata VALUES(1,?1,2,1,NULL,'asia-shanghai-rfc3339-ms-v1')",
            [instance],
        )
        .unwrap();
    runtime
        .execute_batch(&format!(
            "PRAGMA application_id={};PRAGMA user_version=2",
            schema::RUNTIME_APP
        ))
        .unwrap();
    let before = runtime
        .prepare("SELECT name,sql FROM sqlite_master ORDER BY name")
        .unwrap()
        .query_map([], |r| {
            Ok((r.get::<_, String>(0)?, r.get::<_, Option<String>>(1)?))
        })
        .unwrap()
        .collect::<Result<Vec<_>, _>>()
        .unwrap();
    drop(runtime);
    let mut s = Stores::open(&dir).unwrap();
    let mut config = Configuration::default();
    config.storage.retention_days = 9;
    s.config
        .execute(
            "UPDATE configuration_draft SET payload=?1",
            [encode(&config).unwrap()],
        )
        .unwrap();
    let material = seed(&mut s, 1);
    let sample_id = material.parts[0].sample_id.clone();
    s.runtime
        .execute(
            "INSERT INTO plc_sources VALUES('plc-demo','generation-demo',2)",
            [],
        )
        .unwrap();
    let original = s.sample(&sample_id).unwrap();
    let config_before = s.configuration().unwrap();
    s.clean_exit().unwrap();
    drop(s);
    let s = Stores::open(&dir).unwrap();
    assert_eq!(s.sample(&sample_id).unwrap(), original);
    assert_eq!(s.configuration().unwrap().etag, config_before.etag);
    assert_eq!(s.configuration().unwrap().draft.storage.retention_days, 9);
    assert_eq!(
        s.runtime
            .query_row::<i64, _, _>(
                "SELECT next_seq FROM plc_sources WHERE plc_id='plc-demo'",
                [],
                |r| r.get(0)
            )
            .unwrap(),
        2
    );
    assert!(!s.delivery_available().unwrap());
    assert_eq!(
        s.delivery_settings().unwrap_err(),
        "delivery_profile_upgrade_required"
    );
    assert!(s.configuration().unwrap().draft.plcs.is_empty());
    let after = s
        .runtime
        .prepare("SELECT name,sql FROM sqlite_master ORDER BY name")
        .unwrap()
        .query_map([], |r| {
            Ok((r.get::<_, String>(0)?, r.get::<_, Option<String>>(1)?))
        })
        .unwrap()
        .collect::<Result<Vec<_>, _>>()
        .unwrap();
    assert_eq!(before, after);
}

#[test]
fn delivery_sample_counts_are_disjoint_and_need_attention_is_visible() {
    use super::delivery_tests::{adopt, fresh, receipt, seed, seed_from};
    use serde_json::json;
    let mut s = fresh();
    let first = seed_from(&mut s, 1, "fragmented");
    assert_eq!(first.parts.len(), 2);
    adopt(&mut s, &first);
    let mut frozen = vec![];
    for seq in 1..=6 {
        let built = if seq == 1 {
            first.clone()
        } else {
            seed(&mut s, seq)
        };
        let settings = s.delivery_settings().unwrap();
        frozen.push(s.freeze_cycle(built, &settings, true).unwrap().unwrap());
    }
    seed(&mut s, 7); // Never frozen.
    let raw = serde_json::to_string(&receipt(&frozen[0])).unwrap();
    s.commit_delivery(&frozen[0], &serde_json::from_str(&raw).unwrap(), &raw)
        .unwrap();
    for (index, state) in [
        (1, "inflight"),
        (2, "retry_wait"),
        (3, "unknown"),
        (4, "blocked"),
        (5, "expired_unconfirmed"),
    ] {
        s.runtime
            .execute(
                "UPDATE delivery_batches SET state=?1 WHERE batch_id=?2",
                params![state, frozen[index].batch.batch_id],
            )
            .unwrap();
    }
    // A sample can be referenced by an old batch and a diagnostic/parent chain. Count once.
    let sample = &frozen[3].batch.samples[0].sample_id;
    let members =
        json!({"cycleId":frozen[3].batch.cycles[0].cycle_id,"sampleIds":[sample]}).to_string();
    s.runtime.execute("INSERT INTO delivery_batches(batch_id,target_id,settings_revision,request_digest,body_sha,body,members,parent_depth,state,next_attempt_at,created_at) SELECT ?1,target_id,settings_revision,'','',NULL,?2,0,'needs_review',next_attempt_at,created_at FROM delivery_batches WHERE batch_id=?3",params![id(),members,frozen[3].batch.batch_id]).unwrap();
    let snapshot = s.delivery_snapshot(true).unwrap();
    assert_eq!(snapshot["pending"], 6);
    assert_eq!(snapshot["acknowledged"], 1);
    assert_eq!(
        snapshot["sampleCounts"],
        json!({"unfrozen":1,"frozen":2,"needsProcessing":3,"acknowledged":1})
    );
    assert_eq!(snapshot["state"], "needs_review");
    // Blocked and expired diagnostics retain their own running-state label.
    s.runtime
        .execute(
            "UPDATE delivery_batches SET state='acknowledged' WHERE state!='blocked'",
            [],
        )
        .unwrap();
    assert_eq!(s.delivery_snapshot(true).unwrap()["state"], "blocked");
    s.runtime
        .execute(
            "UPDATE delivery_batches SET state='expired_unconfirmed' WHERE state='blocked'",
            [],
        )
        .unwrap();
    assert_eq!(
        s.delivery_snapshot(true).unwrap()["state"],
        "expired_unconfirmed"
    );
    assert_eq!(s.delivery_snapshot(false).unwrap()["state"], "stopped");
}

#[test]
fn delivery_client_cardinality_and_max_response_ack_sqlite_budget() {
    use super::super::delivery_tests::{adopt, receipt};
    use crate::domain::facts_canonical as pf;
    // Product admission: one group <=256 enabled points, <=32 reads, one frozen cycle/batch.
    // Use all three cardinality limits, real commit_cycle, validated context and fixed wire builder.
    let mut s = super::super::delivery_tests::fresh();
    let mut c = configuration();
    c.plcs.truncate(1);
    c.groups.truncate(1);
    c.dbs.clear();
    c.sources.clear();
    c.points.clear();
    let plc = c.plcs[0].id.clone();
    let group = c.groups[0].id.clone();
    for number in 1..=32u16 {
        let source = SourceDocument {
            id: id(),
            name: format!("synthetic-{number}.scl"),
            content: format!("synthetic DB{number}"),
            sha256: digest(&format!("synthetic DB{number}")),
            plc_id: plc.clone(),
            db_number: Some(number),
            diagnostics: vec![],
            lineage_id: None,
        };
        let db = Db {
            id: id(),
            plc_id: plc.clone(),
            source_id: source.id.clone(),
            name: format!("DB{number}"),
            number,
            length: 1,
            complete: true,
            flat: true,
            tree: (0..8)
                .map(|bit| FieldNode {
                    name: format!("p{bit}"),
                    path: format!("p{bit}"),
                    data_type: "BOOL".into(),
                    line: bit + 1,
                    comment: String::new(),
                    lower: None,
                    upper: None,
                    children: vec![],
                })
                .collect(),
            import_binding: None,
        };
        for bit in 0..8u8 {
            c.points.push(Point {
                id: id(),
                plc_id: plc.clone(),
                db_id: db.id.clone(),
                source_path: format!("p{bit}"),
                name: format!("p{bit}"),
                name_mode: None,
                data_type: "BOOL".into(),
                comment: String::new(),
                enabled: true,
                group_id: Some(group.clone()),
                address: Some(Address {
                    offset: 0,
                    bit: Some(bit),
                    confirmed: true,
                    origin: "manual".into(),
                    reason: "synthetic-confirmed".into(),
                }),
            });
        }
        c.sources.push(source);
        c.dbs.push(db);
    }
    assert!(validate(&c).is_empty(), "{:?}", validate(&c));
    let revision = activated(&mut s, &c);
    let now = crate::domain::business_time::now();
    let mut cycle = input(&c, &revision, &now);
    cycle.reads = (1..=32)
        .map(|db_number| ReadTiming {
            db_number,
            start: 0,
            size: 1,
            started_at: now.clone(),
            finished_at: now.clone(),
            duration_ms: 0,
            quality: "good".into(),
        })
        .collect();
    s.commit_cycle(cycle).unwrap();
    let cid: String = s
        .runtime
        .query_row("SELECT id FROM collection_cycles", [], |r| r.get(0))
        .unwrap();
    let built = s.build_delivery_cycle(&cid).unwrap();
    adopt(&mut s, &built);
    let f = s.next_delivery().unwrap().unwrap();
    assert_eq!(f.batch.samples.len(), 32);
    assert_eq!(
        f.batch
            .samples
            .iter()
            .map(|p| p.point_ids.len())
            .sum::<usize>(),
        256
    );
    let mut ack = receipt(&f);
    let observed = crate::domain::facts_wire::time(&now).unwrap();
    ack["data"]["proofExpiresAt"] = json!((crate::domain::facts_wire::time(
        ack["data"]["committedAt"].as_str().unwrap()
    )
    .unwrap()
        + chrono::Duration::days(120))
    .to_rfc3339_opts(chrono::SecondsFormat::Nanos, false));
    ack["data"]["commitSerial"] = json!(i64::MAX.to_string());
    for result in ack["data"]["results"].as_array_mut().unwrap() {
        result["position"]["commitSerial"] = json!(i64::MAX.to_string());
        result["expiresAt"] = json!(observed
            .checked_add_months(chrono::Months::new(3))
            .unwrap()
            .to_rfc3339_opts(chrono::SecondsFormat::Nanos, false));
    }
    let compact = serde_json::to_string(&ack).unwrap();
    // 同一合法typed语义，仅增加JSON格式空白：接收资源上限，不冒称provider普通输出。
    let raw = format!(
        "{}{}",
        " ".repeat(crate::domain::facts_wire::RECEIPT_MAX - compact.len()),
        compact
    );
    crate::domain::local_delivery::verify_success(&f.batch, &ack).unwrap();
    let originals = |s: &Stores| {
        s.runtime
            .prepare("SELECT payload,sha256 FROM samples ORDER BY id")
            .unwrap()
            .query_map([], |r| Ok((r.get::<_, String>(0)?, r.get::<_, String>(1)?)))
            .unwrap()
            .collect::<Result<Vec<_>, _>>()
            .unwrap()
    };
    let original_before = originals(&s);
    let before = tree(&s.dir);
    let capacity_before = s.capacity(c.storage.quota_bytes).unwrap();
    // Inspect the physical rollback journal from inside the real ACK transaction, after receipt insert.
    unsafe extern "C" fn probe(
        context: *mut rusqlite::ffi::sqlite3_context,
        _: i32,
        _: *mut *mut rusqlite::ffi::sqlite3_value,
    ) {
        let dir = &*(rusqlite::ffi::sqlite3_user_data(context) as *const PathBuf);
        let bytes = super::super::capacity::bytes(&dir.join("runtime.sqlite-journal"));
        std::fs::write(dir.join("ack-journal-bytes.txt"), bytes.to_string()).unwrap();
        std::fs::write(
            dir.join("ack-main-bytes.txt"),
            super::super::capacity::bytes(&dir.join("runtime.sqlite")).to_string(),
        )
        .unwrap();
        std::fs::copy(
            dir.join("runtime.sqlite-journal"),
            dir.join("ack-budget-journal-evidence.bin"),
        )
        .unwrap();
        rusqlite::ffi::sqlite3_result_int(context, 0);
    }
    let dir = s.dir.clone();
    unsafe {
        assert_eq!(
            rusqlite::ffi::sqlite3_create_function_v2(
                s.runtime.handle(),
                b"synthetic_ack_probe\0".as_ptr().cast(),
                0,
                rusqlite::ffi::SQLITE_UTF8,
                (&dir as *const PathBuf).cast_mut().cast(),
                Some(probe),
                None,
                None,
                None
            ),
            0
        );
    }
    s.runtime.execute_batch("CREATE TEMP TRIGGER synthetic_ack_probe BEFORE UPDATE ON sample_delivery BEGIN SELECT synthetic_ack_probe(); SELECT RAISE(ABORT,'synthetic_ack_budget_rollback'); END;").unwrap();
    assert!(s
        .commit_delivery(&f, &ack, &raw)
        .unwrap_err()
        .contains("synthetic_ack_budget_rollback"));
    let rollback_journal: u64 = std::fs::read_to_string(s.dir.join("ack-journal-bytes.txt"))
        .unwrap()
        .parse()
        .unwrap();
    assert!(rollback_journal > 512);
    std::fs::copy(
        s.dir.join("ack-budget-journal-evidence.bin"),
        s.dir.join("ack-budget-rollback-journal-evidence.bin"),
    )
    .unwrap();
    assert_eq!(
        s.runtime
            .query_row::<u32, _, _>("SELECT count(*) FROM delivery_receipts", [], |r| r.get(0))
            .unwrap(),
        0
    );
    assert_eq!(
        tree(&s.dir).get("runtime.sqlite"),
        before.get("runtime.sqlite")
    );
    s.runtime.execute_batch("DROP TRIGGER synthetic_ack_probe; CREATE TEMP TRIGGER synthetic_ack_probe BEFORE UPDATE ON sample_delivery BEGIN SELECT synthetic_ack_probe(); END;").unwrap();
    s.commit_delivery(&f, &ack, &raw).unwrap();
    let commit_journal: u64 = std::fs::read_to_string(s.dir.join("ack-journal-bytes.txt"))
        .unwrap()
        .parse()
        .unwrap();
    s.runtime
        .execute_batch("DROP TRIGGER synthetic_ack_probe;")
        .unwrap();
    unsafe {
        assert_eq!(
            rusqlite::ffi::sqlite3_create_function_v2(
                s.runtime.handle(),
                b"synthetic_ack_probe\0".as_ptr().cast(),
                0,
                rusqlite::ffi::SQLITE_UTF8,
                std::ptr::null_mut(),
                None,
                None,
                None,
                None
            ),
            0
        );
    }
    let capacity_after = s.capacity(c.storage.quota_bytes).unwrap();
    assert_eq!(
        s.runtime
            .query_row::<String, _, _>("SELECT response_utf8 FROM delivery_receipts", [], |r| r
                .get(0))
            .unwrap(),
        raw
    );
    assert_eq!(s.delivery_snapshot(false).unwrap()["acknowledged"], 32);
    assert_eq!(capacity_after.delivery_receipt_bytes, raw.len() as u64);
    assert_eq!(originals(&s), original_before);
    assert_eq!(raw.len(), crate::domain::facts_wire::RECEIPT_MAX);
    let old_page_budget = capacity_before.reserved_bytes - 96 * 1024 * 1024;
    let peak_main = std::fs::read_to_string(s.dir.join("ack-main-bytes.txt"))
        .unwrap()
        .parse::<u64>()
        .unwrap()
        .max(capacity_after.main_bytes);
    assert!(peak_main - capacity_before.main_bytes < 32 * 1024 * 1024);
    assert!(commit_journal < old_page_budget && rollback_journal < old_page_budget);
    assert!(capacity_before.reserved_bytes >= 32 * 1024 * 1024 + 8 * 1024 * 1024);
    let evidence = json!({"fixture":s.dir,"sampleParts":32,"points":256,"requestBytes":f.body.len(),"ackBytes":raw.len(),"compactAckBytes":compact.len(),"measuredPeakMainBytes":peak_main,"oldPageJournalBudgetBytes":old_page_budget,"additionalAckRecoveryBudgetBytes":32*1024*1024,"ackSha256":pf::sha(raw.as_bytes()),"rollbackJournalBytes":rollback_journal,"commitJournalBytes":commit_journal,"capacityBefore":capacity_before,"capacityAfter":capacity_after,"before":before,"after":tree(&s.dir),"canonicalAckConservativeBoundBytes":32*1024+256*259+2*1024,"boundAssumptions":"32 results x 1024 metadata + 256 identifiers x (258 escaped bytes + comma) + 2048 envelope/cycle; one frozen cycle, <=256 group points; actual IDs UUIDs, serial uses signed BIGINT i64::MAX; proof is committedAt +120 days (retention.py), raw expires observedAt +3 natural months; provider compact JSON, no padding","scope":"same fully typed legal receipt, JSON formatting whitespace to exactly 8MiB client input resource bound; not ordinary provider serialization; canonical bound enumerated separately"});
    let out = std::env::temp_dir().join("rework-qa1-ack-budget.json");
    std::fs::write(&out, serde_json::to_vec_pretty(&evidence).unwrap()).unwrap();
    println!("ACK budget evidence {}", out.display());
}
