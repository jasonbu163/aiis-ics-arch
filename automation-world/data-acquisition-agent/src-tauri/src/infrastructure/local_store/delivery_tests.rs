//! 仅显式A1临时根的全新合成SQLite，验证真实事务回滚/恢复与原字节守恒；无env/网络。
use super::*;
use crate::domain::{
    facts_canonical as pf,
    facts_wire::*,
    local_delivery::{DeliverySettings, SourceAdoption},
};
use rusqlite::params;
use serde_json::{json, Value};
pub(crate) fn fresh() -> Stores {
    legacy(3)
}
// Historical public-vector fixtures omit the complete local activation/source graph.
// Build unsealed legacy schemas directly under the real lock; never unseal a new profile.
pub(crate) fn legacy(version: u32) -> Stores {
    assert!([2, 3].contains(&version));
    let root = std::env::temp_dir()
        .canonicalize()
        .expect("explicit TMPDIR");
    assert!(
        root.starts_with("/private/tmp")
            && (root.to_string_lossy().contains("daa-008-r1-a-")
                || root.to_string_lossy().contains("daa-008-r2-a-")
                || root.to_string_lossy().contains("daa010-r5-dev-private"))
    );
    let profile = root.join(format!(
        "legacy-profile-{}",
        crate::domain::local_configuration::id()
    ));
    let dir = profile.join("local-acquisition-v1");
    let lock = crate::infrastructure::local_profile_lock::ProfileLock::acquire(&profile).unwrap();
    std::fs::create_dir(&dir).unwrap();
    let instance = crate::domain::local_configuration::id();
    for role in ["config", "runtime"] {
        let path = dir.join(format!("{role}.sqlite"));
        std::fs::File::create(&path).unwrap();
        let c = connect(
            &path,
            true,
            if role == "config" {
                schema::CONFIG_APP
            } else {
                schema::RUNTIME_APP
            },
        )
        .unwrap();
        if role == "config" {
            c.execute_batch(&schema::config_sql()).unwrap();
            c.execute(
                "INSERT INTO instance_metadata VALUES(1,?1,2,'asia-shanghai-rfc3339-ms-v1')",
                [&instance],
            )
            .unwrap();
            c.execute(
                "INSERT INTO configuration_draft VALUES(1,?1,?2,'[]')",
                params![
                    crate::domain::local_configuration::id(),
                    encode(&Configuration::default()).unwrap()
                ],
            )
            .unwrap();
            c.execute_batch(&format!(
                "PRAGMA application_id={};PRAGMA user_version=2",
                schema::CONFIG_APP
            ))
            .unwrap();
        } else {
            c.execute_batch(&if version == 3 {
                schema::runtime_v3_sql()
            } else {
                schema::runtime_sql()
            })
            .unwrap();
            c.execute(
                "INSERT INTO runtime_metadata VALUES(1,?1,?2,1,NULL,'asia-shanghai-rfc3339-ms-v1')",
                params![instance, version],
            )
            .unwrap();
            if version == 3 {
                let settings = DeliverySettings::default();
                c.execute(
                    "INSERT INTO delivery_settings(id,settings_revision,payload) VALUES(1,?1,?2)",
                    params![settings.settings_revision, encode(&settings).unwrap()],
                )
                .unwrap();
            }
            c.execute_batch(&format!(
                "PRAGMA application_id={};PRAGMA user_version={version}",
                schema::RUNTIME_APP
            ))
            .unwrap();
        }
        c.close().unwrap();
    }
    drop(lock);
    assert!(!dir.join("profile-contract.json").exists());
    Stores::open(&dir).unwrap()
}
pub(crate) fn seed(s: &mut Stores, seq: i64) -> BuiltCycle {
    seed_from(s, seq, "request")
}
pub(crate) fn seed_from(s: &mut Stores, seq: i64, fixture: &str) -> BuiltCycle {
    let vectors: Value = serde_json::from_str(include_str!(
        "../../../../../../contracts/published/http-api/plc-facts-v1/vectors.json"
    ))
    .unwrap();
    let request = if fixture == "request" {
        &vectors["request"]
    } else {
        &vectors["fixtures"][fixture]
    };
    let c = &request["cycles"][0];
    let mut manifest =
        pf::parse(c["manifestUtf8"].as_str().unwrap().as_bytes(), 128 * 1024).unwrap();
    let mut payload = pf::parse(
        request["samples"][0]["payloadUtf8"]
            .as_str()
            .unwrap()
            .as_bytes(),
        512 * 1024,
    )
    .unwrap();
    let cycle = crate::domain::local_configuration::id();
    let sample = crate::domain::local_configuration::id();
    let revision = manifest["revision"].as_str().unwrap().to_string();
    manifest["cycleId"] = json!(cycle);
    manifest["sourceSeq"] = json!(seq.to_string());
    manifest["samples"][0]["sampleId"] = json!(sample);
    payload["instanceId"] = json!(s.instance);
    payload["cycleId"] = json!(cycle);
    payload["sampleId"] = json!(sample);
    payload["sourceSeq"] = json!(seq.to_string());
    let raw = serde_json::to_string(&payload).unwrap();
    let hash = crate::domain::local_sample::digest(&raw);
    manifest["samples"][0]["sha256"] = json!(hash);
    let manifest_raw = serde_json::to_string(&manifest).unwrap();
    let manifest_hash = crate::domain::local_sample::digest(&manifest_raw);
    let context = c["contextUtf8"].as_str().unwrap();
    let context_hash = crate::domain::local_sample::digest(context);
    s.runtime
        .execute(
            "INSERT OR IGNORE INTO configuration_contexts VALUES(?1,1,?2,?3)",
            params![revision, context_hash, context],
        )
        .unwrap();
    s.runtime.execute("INSERT INTO collection_cycles VALUES(?1,'plc-demo','generation-demo',?2,'group-demo',?3,'2026-11-04T10:00:00.100+08:00','2026-11-04T10:00:00.200+08:00','2026-11-04T10:00:00.201+08:00','good',?4,?5,1)",params![cycle,seq,revision,manifest_raw,manifest_hash]).unwrap();
    s.runtime.execute("INSERT INTO samples(id,cycle_id,db_number,plc_id,group_id,source_seq,revision,quality,saved_at,schema_version,payload,sha256,payload_bytes) VALUES(?1,?2,1,'plc-demo','group-demo',?3,?4,'good','2026-11-04T10:00:00.201+08:00',2,?5,?6,?7)",params![sample,cycle,seq,revision,raw,hash,raw.len()]).unwrap();
    s.runtime
        .execute(
            "INSERT INTO sample_delivery VALUES(?1,'pending',NULL)",
            [&sample],
        )
        .unwrap();
    build_cycle(
        &s.instance,
        &manifest_raw,
        &manifest_hash,
        context,
        &context_hash,
        &[(raw, hash)],
    )
    .unwrap()
}
pub(crate) fn adopt(s: &mut Stores, b: &BuiltCycle) {
    let old = s.delivery_settings().unwrap();
    let mut settings = DeliverySettings {
        target_id: Some("synthetic-target".into()),
        origin: Some("https://example.invalid".into()),
        adoption_reference: "synthetic-only-no-network".into(),
        sources: vec![SourceAdoption {
            plc_id: b.plc_id.clone(),
            source_generation: b.source_generation.clone(),
            definition_set_digest: b.definition_set_digest.clone(),
            context_sha256: b.cycle.context_sha256.clone(),
            sequence_from: "1".into(),
            sequence_through: (i64::MAX - 1).to_string(),
            reference: "synthetic-adoption".into(),
        }],
        ..old.clone()
    };
    settings.contract_pins = Value::Object(
        crate::domain::local_delivery::CONTRACT_PINS
            .iter()
            .map(|(k, v)| (k.to_string(), json!(v)))
            .collect(),
    );
    s.save_delivery_settings(settings, old.settings_revision)
        .unwrap();
}
pub(crate) fn receipt(f: &delivery::Frozen) -> Value {
    let now = crate::domain::business_time::now();
    let expiry = (time(&now).unwrap() + chrono::Duration::days(120))
        .to_rfc3339_opts(chrono::SecondsFormat::Nanos, true);
    let results=f.batch.samples.iter().enumerate().map(|(i,p)|json!({"sampleId":p.sample_id,"part":p.part,"parts":p.parts,"sourceSha256":p.source_sha256,"contentDigest":p.content_digest,"outcome":"created","originalOutcome":"created","confirmation":"created","sourceSampleComplete":f.batch.samples.iter().filter(|s|s.sample_id==p.sample_id).count()==p.parts as usize,"position":{"commitSerial":"7","ordinal":i+1},"latestAdvancedPointIds":p.point_ids,"expiresAt":"2027-02-04T10:00:00.123000000+08:00","valueReadable":true})).collect::<Vec<_>>();
    let cycles=f.batch.cycles.iter().map(|c|{let expected=c.transport_manifest.iter().map(|s|s.parts.len()).sum::<usize>();let received=f.batch.samples.iter().filter(|p|p.cycle_id==c.cycle_id).count();json!({"cycleId":c.cycle_id,"cycleDigest":cycle_digest(c).unwrap(),"complete":received==expected,"qualityGood":f.batch.samples.iter().filter(|p|p.cycle_id==c.cycle_id).all(|p|pf::parse(p.payload_utf8.as_bytes(),512*1024).unwrap()["points"].as_object().unwrap().values().all(|v|v["quality"]=="good")),"receivedParts":received,"expectedParts":expected})}).collect::<Vec<_>>();
    json!({"code":200,"message":"success","data":{"contractVersion":"plc-facts/v1","digestProfile":"pf-json/v1","instanceId":f.batch.instance_id,"batchId":f.batch.batch_id,"requestDigest":f.batch.request_digest,"receiptId":crate::domain::local_configuration::id(),"status":"committed","persistence":"committed","newFactsCommitted":true,"outcome":"created","originalOutcome":"created","confirmation":"facts_committed","commitSerial":"7","committedAt":now,"proofExpiresAt":expiry,"results":results,"cycles":cycles}})
}
fn original(s: &Stores) -> Vec<(String, String)> {
    s.runtime
        .prepare("SELECT payload,sha256 FROM samples ORDER BY id")
        .unwrap()
        .query_map([], |r| Ok((r.get(0)?, r.get(1)?)))
        .unwrap()
        .collect::<Result<Vec<_>, _>>()
        .unwrap()
}
#[test]
fn v3_freeze_ack_atomic_original_bytes() {
    let mut s = fresh();
    let b = seed(&mut s, 1);
    adopt(&mut s, &b);
    let before = original(&s);
    let f = s.next_delivery().unwrap().unwrap();
    assert_eq!(f.batch.samples[0].payload_utf8, before[0].0);
    assert_eq!(s.mark_dispatch(&f).unwrap(), 1);
    let ack = receipt(&f);
    s.runtime.execute_batch("CREATE TRIGGER synthetic_ack_fail BEFORE UPDATE ON sample_delivery BEGIN SELECT RAISE(ABORT,'synthetic_ack_failure'); END;").unwrap();
    let raw = serde_json::to_string_pretty(&ack).unwrap();
    assert!(s.commit_delivery(&f, &ack, &raw).is_err());
    assert_eq!(
        s.runtime
            .query_row::<u32, _, _>("SELECT count(*) FROM delivery_receipts", [], |r| r.get(0))
            .unwrap(),
        0
    );
    assert_eq!(
        s.runtime
            .query_row::<String, _, _>("SELECT state FROM sample_delivery", [], |r| r.get(0))
            .unwrap(),
        "pending"
    );
    assert_eq!(original(&s), before);
    s.runtime
        .execute_batch("DROP TRIGGER synthetic_ack_fail;")
        .unwrap();
    s.commit_delivery(&f, &ack, &raw).unwrap();
    assert_eq!(
        s.runtime
            .query_row::<String, _, _>("SELECT response_utf8 FROM delivery_receipts", [], |r| r
                .get(0))
            .unwrap(),
        raw
    );
    assert_eq!(
        s.runtime
            .query_row::<String, _, _>("SELECT state FROM sample_delivery", [], |r| r.get(0))
            .unwrap(),
        "acknowledged"
    );
    assert_eq!(
        s.runtime
            .query_row::<u32, _, _>("SELECT count(*) FROM sample_references", [], |r| r.get(0))
            .unwrap(),
        0
    );
    assert_eq!(original(&s), before);
    s.commit_delivery(&f, &ack, &raw).unwrap();
}
#[test]
fn legacy_inflight_reopen_preserves_identity_and_stays_stopped() {
    let mut s = fresh();
    let b = seed(&mut s, 1);
    adopt(&mut s, &b);
    let before = original(&s);
    let f = s.next_delivery().unwrap().unwrap();
    s.mark_dispatch(&f).unwrap();
    let dir = s.dir.clone();
    drop(s);
    let s = Stores::open(&dir).unwrap();
    assert_eq!(s.delivery_snapshot(false).unwrap()["running"], false);
    assert_eq!(
        s.runtime
            .query_row::<String, _, _>("SELECT state FROM delivery_batches", [], |r| r.get(0))
            .unwrap(),
        "inflight"
    );
    let retained: (String, String, String, i64) = s
        .runtime
        .query_row(
            "SELECT batch_id,body,body_sha,attempt FROM delivery_batches",
            [],
            |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?, r.get(3)?)),
        )
        .unwrap();
    assert_eq!(retained, (f.batch.batch_id, f.body, f.body_sha, 1));
    assert_eq!(
        s.runtime
            .query_row::<u64, _, _>("SELECT count(*) FROM delivery_receipts", [], |r| r.get(0))
            .unwrap(),
        0
    );
    assert_eq!(original(&s), before);
}
#[test]
fn latest_three_then_history_and_eight_frozen() {
    let mut s = fresh();
    let b = seed(&mut s, 1);
    for n in 2..=12 {
        seed(&mut s, n);
    }
    adopt(&mut s, &b);
    let mut sequence = vec![];
    for _ in 0..4 {
        let f = s.next_delivery().unwrap().unwrap();
        sequence.push(
            pf::parse(f.batch.samples[0].payload_utf8.as_bytes(), 512 * 1024).unwrap()["sourceSeq"]
                .as_str()
                .unwrap()
                .to_string(),
        );
        s.mark_dispatch(&f).unwrap();
        let ack = receipt(&f);
        s.commit_delivery(&f, &ack, &serde_json::to_string(&ack).unwrap())
            .unwrap();
    }
    assert_eq!(sequence, ["12", "11", "10", "1"]);
    for _ in 0..8 {
        let f = s.next_delivery().unwrap().unwrap();
        s.mark_dispatch(&f).unwrap();
        s.fail_delivery(
            &f.batch.batch_id,
            "unknown",
            "synthetic_timeout",
            300,
            false,
        )
        .unwrap();
    }
    let count: u32 = s
        .runtime
        .query_row(
            "SELECT count(*) FROM delivery_batches WHERE body IS NOT NULL AND state!='rejected'",
            [],
            |r| r.get(0),
        )
        .unwrap();
    assert_eq!(count, 8);
    let _ = s.next_delivery().unwrap();
    let after: u32 = s
        .runtime
        .query_row(
            "SELECT count(*) FROM delivery_batches WHERE body IS NOT NULL AND state!='rejected'",
            [],
            |r| r.get(0),
        )
        .unwrap();
    assert_eq!(after, 8);
}
#[test]
fn crash_child_uncommitted_ack() {
    if std::env::var("DAA_008_SYNTHETIC_CRASH_CHILD")
        .ok()
        .as_deref()
        != Some("yes")
    {
        return;
    }
    let path = std::path::PathBuf::from(std::env::var_os("DAA_008_SYNTHETIC_CRASH_PATH").unwrap());
    assert!(path.starts_with(std::env::temp_dir()));
    let mut s = Stores::open(&path).unwrap();
    let tx = s.runtime.transaction().unwrap();
    tx.execute("UPDATE delivery_parts SET state='acknowledged'", [])
        .unwrap();
    tx.execute("UPDATE sample_delivery SET state='acknowledged'", [])
        .unwrap();
    tx.execute("UPDATE delivery_batches SET state='acknowledged'", [])
        .unwrap();
    assert_eq!(
        unsafe { rusqlite::ffi::sqlite3_db_cacheflush(tx.handle()) },
        0
    );
    unsafe { libc::_exit(86) }
}
#[test]
fn unsealed_hot_journal_is_refused_without_recovery_authority() {
    let mut s = fresh();
    let b = seed(&mut s, 1);
    adopt(&mut s, &b);
    let before = original(&s);
    let f = s.next_delivery().unwrap().unwrap();
    s.mark_dispatch(&f).unwrap();
    let path = s.dir.clone();
    let snapshot = serde_json::json!({"fixture":path,"samples":before,"sampleDelivery":"pending","batchState":"inflight","receiptCount":0,"bodySha256":f.body_sha});
    std::fs::write(
        path.join("daa-008-hot-before.json"),
        serde_json::to_vec_pretty(&snapshot).unwrap(),
    )
    .unwrap();
    drop(s);
    let status = std::process::Command::new(std::env::current_exe().unwrap())
        .args([
            "--exact",
            "infrastructure::local_store::delivery_tests::crash_child_uncommitted_ack",
            "--nocapture",
        ])
        .env("DAA_008_SYNTHETIC_CRASH_CHILD", "yes")
        .env("DAA_008_SYNTHETIC_CRASH_PATH", &path)
        .status()
        .unwrap();
    assert_eq!(status.code(), Some(86));
    let journal = path.join("runtime.sqlite-journal");
    assert!(std::fs::metadata(&journal).unwrap().len() > 512);
    let journal_before = std::fs::read(&journal).unwrap();
    let error = Stores::open(&path)
        .err()
        .expect("unsealed hot must be refused");
    assert!(error.starts_with("time_profile_unsupported:"), "{error}");
    assert_eq!(std::fs::read(&journal).unwrap(), journal_before);
    assert!(!path.join("profile-contract.json").exists());
}
#[test]
fn settings_cas_and_never_frozen_source_recheck() {
    let mut s = fresh();
    let b = seed(&mut s, 1);
    let before = original(&s);
    let view = s.configuration().unwrap();
    let old = s.delivery_settings().unwrap();
    let mut settings = old.clone();
    settings.target_id = Some("synthetic-target".into());
    settings.origin = Some("https://example.invalid".into());
    settings.contract_pins = Value::Object(
        crate::domain::local_delivery::CONTRACT_PINS
            .iter()
            .map(|(k, v)| (k.to_string(), json!(v)))
            .collect(),
    );
    settings.sources = vec![SourceAdoption {
        plc_id: b.plc_id.clone(),
        source_generation: b.source_generation.clone(),
        definition_set_digest: format!("sha256:{}", "0".repeat(64)),
        context_sha256: b.cycle.context_sha256.clone(),
        sequence_from: "1".into(),
        sequence_through: "9223372036854775806".into(),
        reference: "synthetic-old-definition".into(),
    }];
    let saved = s
        .save_delivery_settings(settings, old.settings_revision.clone())
        .unwrap();
    assert!(s.next_delivery().unwrap().is_none());
    assert_eq!(s.delivery_snapshot(false).unwrap()["counts"]["blocked"], 1);
    let mut adopted = saved.clone();
    adopted.sources = vec![SourceAdoption {
        plc_id: b.plc_id.clone(),
        source_generation: b.source_generation.clone(),
        definition_set_digest: b.definition_set_digest.clone(),
        context_sha256: b.cycle.context_sha256.clone(),
        sequence_from: "1".into(),
        sequence_through: "9223372036854775806".into(),
        reference: "synthetic".into(),
    }];
    let saved = s
        .save_delivery_settings(adopted, saved.settings_revision)
        .unwrap();
    assert!(s
        .save_delivery_settings(saved.clone(), old.settings_revision)
        .is_err());
    let f = s.next_delivery().unwrap().unwrap();
    let mut changed = saved.clone();
    changed.origin = Some("https://other.invalid".into());
    assert!(s
        .save_delivery_settings(changed, saved.settings_revision)
        .unwrap_err()
        .starts_with("delivery_target_unresolved"));
    assert_eq!(original(&s), before);
    assert_eq!(s.configuration().unwrap().etag, view.etag);
    assert_eq!(f.batch.samples[0].payload_utf8, before[0].0);
}
#[test]
fn freeze_dispatch_failures_and_capacity_preserve_recovery() {
    let mut s = fresh();
    let b = seed(&mut s, 1);
    adopt(&mut s, &b);
    let before = original(&s);
    s.runtime.execute_batch("CREATE TRIGGER synthetic_freeze_fail BEFORE INSERT ON delivery_batches BEGIN SELECT RAISE(ABORT,'synthetic_freeze_failure'); END;").unwrap();
    let settings = s.delivery_settings().unwrap();
    assert!(s.freeze_cycle(b.clone(), &settings, true).is_err());
    assert_eq!(
        s.runtime
            .query_row::<u32, _, _>("SELECT count(*) FROM delivery_parts", [], |r| r.get(0))
            .unwrap(),
        0
    );
    assert_eq!(
        s.runtime
            .query_row::<u32, _, _>("SELECT count(*) FROM sample_references", [], |r| r.get(0))
            .unwrap(),
        0
    );
    s.runtime
        .execute_batch("DROP TRIGGER synthetic_freeze_fail;")
        .unwrap();
    let f = s.next_delivery().unwrap().unwrap();
    s.runtime.execute_batch("CREATE TRIGGER synthetic_dispatch_fail BEFORE UPDATE ON delivery_batches BEGIN SELECT RAISE(ABORT,'synthetic_dispatch_failure'); END;").unwrap();
    assert!(s.mark_dispatch(&f).is_err());
    assert_eq!(
        s.runtime
            .query_row::<String, _, _>("SELECT state FROM delivery_batches", [], |r| r.get(0))
            .unwrap(),
        "prepared"
    );
    s.runtime
        .execute_batch("DROP TRIGGER synthetic_dispatch_fail;")
        .unwrap();
    let capacity = s.capacity(1024 * 1024 * 1024).unwrap();
    assert!(capacity.reserved_bytes >= 64 * 1024 * 1024);
    let free = std::sync::Arc::new(std::sync::atomic::AtomicU64::new(1024 * 1024 * 1024));
    let main = std::sync::Arc::new(std::sync::atomic::AtomicU64::new(980 * 1024 * 1024));
    s.test_meter = Some((free, main));
    assert!(!s.capacity(1024 * 1024 * 1024).unwrap().admission);
    assert!(s.next_delivery().unwrap().is_some());
    s.mark_dispatch(&f).unwrap();
    let ack = receipt(&f);
    s.commit_delivery(&f, &ack, &serde_json::to_string(&ack).unwrap())
        .unwrap();
    assert_eq!(original(&s), before);
}
#[test]
fn acknowledged_retention_removes_metadata_but_pending_remains() {
    let mut s = fresh();
    let b = seed(&mut s, 1);
    seed(&mut s, 2);
    adopt(&mut s, &b);
    let f = s.next_delivery().unwrap().unwrap();
    s.mark_dispatch(&f).unwrap();
    let ack = receipt(&f);
    s.commit_delivery(&f, &ack, &serde_json::to_string(&ack).unwrap())
        .unwrap();
    s.runtime
        .execute(
            "UPDATE collection_cycles SET saved_at='2025-01-01T00:00:00.000+08:00'",
            [],
        )
        .unwrap();
    assert_eq!(s.cleanup_acknowledged(7, 1024 * 1024 * 1024).unwrap(), 1);
    assert_eq!(
        s.runtime
            .query_row::<u32, _, _>("SELECT count(*) FROM delivery_receipts", [], |r| r.get(0))
            .unwrap(),
        0
    );
    assert_eq!(
        s.runtime
            .query_row::<u32, _, _>("SELECT count(*) FROM samples", [], |r| r.get(0))
            .unwrap(),
        1
    );
    assert_eq!(
        s.runtime
            .query_row::<String, _, _>("SELECT state FROM sample_delivery", [], |r| r.get(0))
            .unwrap(),
        "pending"
    );
}
#[test]
fn more_than_two_hundred_fast_rounds_do_not_starve_second_plc() {
    let mut s = fresh();
    let a = seed(&mut s, 1);
    for n in 2..=202 {
        seed(&mut s, n);
    }
    let temporary = seed(&mut s, 999);
    let mut p = pf::parse(temporary.parts[0].payload_utf8.as_bytes(), 512 * 1024).unwrap();
    let mut m = pf::parse(temporary.cycle.manifest_utf8.as_bytes(), 128 * 1024).unwrap();
    for v in [&mut p, &mut m] {
        v["plcId"] = json!("plc-other");
        v["sourceSeq"] = json!("1");
        v["revision"] = json!("config-other");
    }
    p["points"]["point_x"]["definition"]["plcId"] = json!("plc-other");
    let context = temporary
        .cycle
        .context_utf8
        .replace("plc-demo", "plc-other");
    let raw = serde_json::to_string(&p).unwrap();
    let hash = crate::domain::local_sample::digest(&raw);
    m["samples"][0]["sha256"] = json!(hash);
    let manifest = serde_json::to_string(&m).unwrap();
    let mh = crate::domain::local_sample::digest(&manifest);
    s.runtime
        .execute(
            "INSERT INTO configuration_contexts VALUES('config-other',1,?1,?2)",
            params![crate::domain::local_sample::digest(&context), context],
        )
        .unwrap();
    s.runtime.execute("UPDATE collection_cycles SET plc_id='plc-other',source_seq=1,revision='config-other',manifest=?1,sha256=?2 WHERE id=?3",params![manifest,mh,temporary.cycle.cycle_id]).unwrap();
    s.runtime.execute("UPDATE samples SET plc_id='plc-other',source_seq=1,revision='config-other',payload=?1,sha256=?2,payload_bytes=?3 WHERE cycle_id=?4",params![raw,hash,raw.len(),temporary.cycle.cycle_id]).unwrap();
    let b = build_cycle(
        &s.instance,
        &manifest,
        &mh,
        &context,
        &crate::domain::local_sample::digest(&context),
        &[(raw, hash)],
    )
    .unwrap();
    adopt(&mut s, &a);
    let old = s.delivery_settings().unwrap();
    let mut settings = old.clone();
    settings.sources.push(SourceAdoption {
        plc_id: b.plc_id.clone(),
        source_generation: b.source_generation.clone(),
        definition_set_digest: b.definition_set_digest.clone(),
        context_sha256: b.cycle.context_sha256.clone(),
        sequence_from: "1".into(),
        sequence_through: "9223372036854775806".into(),
        reference: "second-synthetic-plc".into(),
    });
    s.save_delivery_settings(settings, old.settings_revision)
        .unwrap();
    let first = s.next_delivery().unwrap().unwrap();
    let first_plc = pf::parse(first.batch.samples[0].payload_utf8.as_bytes(), 512 * 1024).unwrap()
        ["plcId"]
        .clone();
    s.mark_dispatch(&first).unwrap();
    s.fail_delivery(
        &first.batch.batch_id,
        "unknown",
        "synthetic_timeout",
        300,
        false,
    )
    .unwrap();
    let second = s.next_delivery().unwrap().unwrap();
    let second_plc = pf::parse(second.batch.samples[0].payload_utf8.as_bytes(), 512 * 1024)
        .unwrap()["plcId"]
        .clone();
    assert_ne!(first_plc, second_plc);
    assert!(first_plc == "plc-other" || second_plc == "plc-other");
}
#[test]
fn lifecycle_crash_child() {
    let mode = match std::env::var("DAA_008_LIFECYCLE_CHILD") {
        Ok(v) => v,
        Err(_) => return,
    };
    let path = std::path::PathBuf::from(std::env::var_os("DAA_008_SYNTHETIC_CRASH_PATH").unwrap());
    assert!(path.starts_with(std::env::temp_dir()));
    let mut s = Stores::open(&path).unwrap();
    if mode == "before_freeze" {
        unsafe { libc::_exit(86) }
    }
    let f = s.next_delivery().unwrap().unwrap();
    if mode == "after_freeze" {
        unsafe { libc::_exit(86) }
    }
    s.mark_dispatch(&f).unwrap();
    if mode == "after_dispatch" || mode == "response_before_ack" {
        let _synthetic_response = receipt(&f);
        unsafe { libc::_exit(86) }
    }
    if mode == "after_ack_before_ui" {
        let ack = receipt(&f);
        s.commit_delivery(&f, &ack, &serde_json::to_string(&ack).unwrap())
            .unwrap();
        unsafe { libc::_exit(86) }
    }
    panic!("unknown synthetic lifecycle mode")
}
#[test]
fn durable_crash_positions_preserve_identity_and_stop_state() {
    for mode in [
        "before_freeze",
        "after_freeze",
        "after_dispatch",
        "response_before_ack",
        "after_ack_before_ui",
    ] {
        let mut s = fresh();
        let b = seed(&mut s, 1);
        adopt(&mut s, &b);
        let before = original(&s);
        let path = s.dir.clone();
        drop(s);
        let status = std::process::Command::new(std::env::current_exe().unwrap())
            .args([
                "--exact",
                "infrastructure::local_store::delivery_tests::lifecycle_crash_child",
                "--nocapture",
            ])
            .env("DAA_008_LIFECYCLE_CHILD", mode)
            .env("DAA_008_SYNTHETIC_CRASH_PATH", &path)
            .status()
            .unwrap();
        assert_eq!(status.code(), Some(86), "{mode}");
        let s = Stores::open(&path).unwrap();
        assert_eq!(original(&s), before, "{mode}");
        assert_eq!(s.delivery_snapshot(false).unwrap()["running"], false);
        let count: u32 = s
            .runtime
            .query_row("SELECT count(*) FROM delivery_batches", [], |r| r.get(0))
            .unwrap();
        if mode == "before_freeze" {
            assert_eq!(count, 0);
            continue;
        }
        let state: String = s
            .runtime
            .query_row("SELECT state FROM delivery_batches", [], |r| r.get(0))
            .unwrap();
        assert_eq!(
            state,
            match mode {
                "after_freeze" => "prepared",
                "after_ack_before_ui" => "acknowledged",
                _ => "inflight",
            }
        );
        let acknowledged: String = s
            .runtime
            .query_row("SELECT state FROM sample_delivery", [], |r| r.get(0))
            .unwrap();
        assert_eq!(
            acknowledged,
            if mode == "after_ack_before_ui" {
                "acknowledged"
            } else {
                "pending"
            }
        );
    }
}
#[test]
fn delivery_io_failure_child() {
    if std::env::var("DAA_008_IO_CHILD").ok().as_deref() != Some("yes") {
        return;
    }
    let path = std::path::PathBuf::from(std::env::var_os("DAA_008_SYNTHETIC_CRASH_PATH").unwrap());
    assert!(path.starts_with(std::env::temp_dir()));
    let mut s = Stores::open(&path).unwrap();
    let f = s.next_delivery().unwrap().unwrap();
    s.mark_dispatch(&f).unwrap();
    let ack = receipt(&f);
    let mut old: libc::rlimit = unsafe { std::mem::zeroed() };
    unsafe {
        assert_eq!(libc::getrlimit(libc::RLIMIT_FSIZE, &mut old), 0);
        libc::signal(libc::SIGXFSZ, libc::SIG_IGN);
        assert_eq!(
            libc::setrlimit(
                libc::RLIMIT_FSIZE,
                &libc::rlimit {
                    rlim_cur: 4096,
                    rlim_max: old.rlim_max
                }
            ),
            0
        );
    }
    let outcome = s.commit_delivery(&f, &ack, &serde_json::to_string(&ack).unwrap());
    unsafe {
        assert_eq!(libc::setrlimit(libc::RLIMIT_FSIZE, &old), 0);
    }
    assert!(outcome.is_err(), "real journal file-size failure required");
    assert_eq!(
        s.runtime
            .query_row::<u32, _, _>("SELECT count(*) FROM delivery_receipts", [], |r| r.get(0))
            .unwrap(),
        0
    );
    assert_eq!(
        s.runtime
            .query_row::<String, _, _>("SELECT state FROM sample_delivery", [], |r| r.get(0))
            .unwrap(),
        "pending"
    );
    s.fail_delivery(&f.batch.batch_id, "unknown", "synthetic_ioerr", 1, false)
        .unwrap();
}
#[test]
fn real_journal_io_failure_leaves_unknown_original() {
    let mut s = fresh();
    let b = seed(&mut s, 1);
    adopt(&mut s, &b);
    let before = original(&s);
    let path = s.dir.clone();
    drop(s);
    let status = std::process::Command::new(std::env::current_exe().unwrap())
        .args([
            "--exact",
            "infrastructure::local_store::delivery_tests::delivery_io_failure_child",
            "--nocapture",
        ])
        .env("DAA_008_IO_CHILD", "yes")
        .env("DAA_008_SYNTHETIC_CRASH_PATH", &path)
        .status()
        .unwrap();
    assert!(status.success());
    let s = Stores::open(&path).unwrap();
    assert_eq!(original(&s), before);
    assert_eq!(
        s.runtime
            .query_row::<String, _, _>("SELECT state FROM delivery_batches", [], |r| r.get(0))
            .unwrap(),
        "unknown"
    );
    assert_eq!(
        s.runtime
            .query_row::<u32, _, _>("SELECT count(*) FROM delivery_receipts", [], |r| r.get(0))
            .unwrap(),
        0
    );
}
