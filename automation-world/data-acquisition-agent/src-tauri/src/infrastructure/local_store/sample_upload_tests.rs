//! 合成 SQLite 中验证 v2 冻结、重试及回执事务；不访问 profile 或网络。
use super::sample_upload::{self, Frozen, LegacyStatus};
use crate::domain::{facts_canonical as pf, sample_upload::Reply};
use rusqlite::Connection;
use serde_json::json;

fn fixture(id: &str, plc: &str) -> Frozen {
    let body = json!({"contractVersion":"plc-facts/v2","instanceId":"instance","sampleId":id,"plcId":plc,"dbNumber":1,"sourceGeneration":"generation","sourceSeq":"1","groupId":"group","configRevision":"revision","points":[]}).to_string();
    Frozen {
        sample_id: id.into(),
        instance_id: "instance".into(),
        plc_id: plc.into(),
        db_number: 1,
        source_generation: "generation".into(),
        origin: "http://127.0.0.1:8001/api/v1/integration/plc-facts/samples".into(),
        body_sha: pf::sha(body.as_bytes()),
        body,
    }
}

#[cfg(unix)]
fn within_system_temp_root(root: &std::path::Path) -> bool {
    ["/tmp", "/var/tmp", "/private/var/folders"]
        .iter()
        .filter_map(|path| std::fs::canonicalize(path).ok())
        .any(|path| root.starts_with(path))
}

#[cfg(unix)]
fn synthetic_temp_root() -> std::path::PathBuf {
    let root = std::env::temp_dir().canonicalize().unwrap();
    assert!(
        within_system_temp_root(&root),
        "fixture root is not a system temporary path"
    );
    root
}

#[cfg(unix)]
#[test]
fn synthetic_fixture_root_accepts_independent_temp_and_rejects_non_temp() {
    let temp = std::fs::canonicalize("/tmp").unwrap();
    let qa_like = temp
        .join("daa010-r5-qa-example")
        .join("daa-008-r2-a-fixtures");
    assert!(within_system_temp_root(&qa_like));
    let outside = temp.parent().unwrap().join("not-a-system-temporary-root");
    assert!(!within_system_temp_root(&outside));
}

#[cfg(unix)]
#[test]
fn new_empty_profile_is_sealed_v4_with_upload_stopped() {
    use super::{profile_contract as pc, Stores};
    let root = synthetic_temp_root();
    let profile = root.join(format!(
        "new-profile-{}",
        crate::domain::local_configuration::id()
    ));
    std::fs::create_dir(&profile).unwrap();
    let dir = profile.join("local-acquisition-v1");
    let mut store = Stores::open(&dir).unwrap();
    let config_version: i64 = store
        .config
        .pragma_query_value(None, "user_version", |r| r.get(0))
        .unwrap();
    let runtime_version: i64 = store
        .runtime
        .pragma_query_value(None, "user_version", |r| r.get(0))
        .unwrap();
    assert_eq!((config_version, runtime_version), (2, 4));
    let settings = store.sample_upload_settings().unwrap();
    assert!(settings.origin.is_none());
    assert_eq!(settings.interval_seconds, 5);
    let state = store.sample_upload_snapshot(false).unwrap();
    assert_eq!(state["pending"], 0);
    store.clean_exit().unwrap();
    drop(store);
    let snapshot = pc::capture(&dir).unwrap();
    let credential = snapshot.get(pc::CREDENTIAL).unwrap();
    let contract = pc::decode(&credential.small, &snapshot.profile, &snapshot.store).unwrap();
    pc::bind(&contract, &snapshot).unwrap();
    let mut reopened = Stores::open(&dir).unwrap();
    assert!(reopened.sample_upload_settings().unwrap().origin.is_none());
    reopened.clean_exit().unwrap();
    drop(reopened);
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn reporting_settings_are_atomic_and_sampling_preserves_each_start_binding() {
    use crate::domain::sample_upload::ReportingBinding;
    let profile = synthetic_temp_root().join(format!(
        "r2-reporting-{}",
        crate::domain::local_configuration::id()
    ));
    std::fs::create_dir(&profile).unwrap();
    let dir = profile.join("local-acquisition-v1");
    let mut s = super::Stores::open(&dir).unwrap();
    let config = super::tests::configuration();
    let revision = super::tests::activated(&mut s, &config);
    let local = config.plcs[0].id.clone();
    let initial = s.sample_upload_settings().unwrap();
    assert!(initial.bindings.is_empty());
    let first = s
        .commit_cycle(super::tests::cycle(&config, &revision))
        .unwrap();
    let local_sample: String = s
        .runtime
        .query_row(
            "SELECT id FROM samples WHERE cycle_id=?1 ORDER BY id LIMIT 1",
            [first["cycleId"].as_str().unwrap()],
            |r| r.get(0),
        )
        .unwrap();
    // Every DB in the unbound cycle stays out of the reporting queue.
    assert_eq!(s.sample_upload_snapshot(false).unwrap()["pending"], 0);
    let mut old = initial.clone();
    old.origin = Some("http://127.0.0.1:38117".into());
    old.bindings = vec![ReportingBinding {
        local_plc_id: local.clone(),
        instance_id: "instance-old".into(),
        plc_id: "remote/plc".into(),
        source_generation: "generation-old".into(),
    }];
    let saved = s
        .save_sample_upload_settings(old.clone(), initial.settings_revision.clone())
        .unwrap();
    let captured = s.reporting_identity(&local).unwrap();
    let mut reused = saved.clone();
    reused.bindings[0].instance_id = "another-instance".into();
    assert_eq!(
        s.save_sample_upload_settings(reused, saved.settings_revision.clone())
            .unwrap_err(),
        "source_generation_reuse"
    );
    assert_eq!(
        s.sample_upload_settings().unwrap().bindings[0]
            .instance_id
            .as_str(),
        "instance-old"
    );
    let mut replacement = saved.clone();
    replacement.bindings[0].instance_id = "instance-new".into();
    replacement.bindings[0].source_generation = "generation-new".into();
    assert_eq!(
        s.save_sample_upload_settings(replacement.clone(), initial.settings_revision)
            .unwrap_err(),
        "delivery_settings_conflict"
    );
    assert_eq!(
        s.sample_upload_settings().unwrap().bindings[0]
            .instance_id
            .as_str(),
        "instance-old"
    );
    let saved_new = s
        .save_sample_upload_settings(replacement, saved.settings_revision)
        .unwrap();
    s.commit_cycle_with_reporting(super::tests::cycle(&config, &revision), captured)
        .unwrap();
    s.commit_cycle(super::tests::cycle(&config, &revision))
        .unwrap();
    let bindings = s.sample_upload_bindings().unwrap();
    assert!(bindings
        .iter()
        .any(|b| b.instance_id == "instance-old" && b.source_generation == "generation-old"));
    assert!(bindings
        .iter()
        .any(|b| b.instance_id == "instance-new" && b.source_generation == "generation-new"));
    let target = saved_new.target().unwrap().unwrap();
    let frozen = s
        .next_sample_upload(&target, &bindings, false)
        .unwrap()
        .unwrap();
    assert_eq!(
        (
            &*frozen.instance_id,
            &*frozen.plc_id,
            &*frozen.source_generation
        ),
        ("instance-old", "remote/plc", "generation-old")
    );
    let body: serde_json::Value = serde_json::from_str(&frozen.body).unwrap();
    assert_eq!(
        (
            body["instanceId"].as_str(),
            body["plcId"].as_str(),
            body["sourceGeneration"].as_str()
        ),
        (
            Some("instance-old"),
            Some("remote/plc"),
            Some("generation-old")
        )
    );
    assert_eq!(
        s.sample(&local_sample).unwrap()["deliveryState"],
        "local_only"
    );
    let local_count = s
        .runtime
        .query_row::<u64, _, _>(
            "SELECT count(*) FROM samples WHERE cycle_id=?1",
            [first["cycleId"].as_str().unwrap()],
            |r| r.get(0),
        )
        .unwrap();
    assert_eq!(
        s.cleanup_acknowledged(0, 4 * 1024 * 1024 * 1024).unwrap() as u64,
        local_count
    );
    assert!(s.sample(&local_sample).is_err());
    s.clean_exit().unwrap();
    drop(s);
    let mut reopened = super::Stores::open(&dir).unwrap();
    assert_eq!(
        reopened.sample_upload_settings().unwrap().bindings[0]
            .instance_id
            .as_str(),
        "instance-new"
    );
    assert_eq!(
        reopened
            .next_sample_upload(&target, &reopened.sample_upload_bindings().unwrap(), false)
            .unwrap()
            .unwrap()
            .body,
        frozen.body
    );
    reopened.clean_exit().unwrap();
    drop(reopened);
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn sealed_original_v4_upgrade_keeps_existing_frozen_bytes_and_inode() {
    use super::{profile_contract as pc, schema, Stores};
    let profile = sealed_v4_fixture();
    seed_v4_fixture(&profile, 1);
    let dir = profile.join("local-acquisition-v1");
    let mut s = Stores::open(&dir).unwrap();
    let sources = s.sample_upload_bindings().unwrap();
    let target = "http://127.0.0.1:38117/api/v1/integration/plc-facts/samples";
    let frozen = s
        .next_sample_upload(target, &sources, false)
        .unwrap()
        .unwrap();
    s.mark_sample_upload_attempt(&frozen).unwrap();
    let original: (String,String,String) = s.runtime.query_row("SELECT s.payload,s.sha256,c.manifest FROM samples s JOIN collection_cycles c ON c.id=s.cycle_id WHERE s.id=?1", [&frozen.sample_id], |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?))).unwrap();
    s.clean_exit().unwrap();
    drop(s);
    // Synthetic fixture: reconstruct a sealed predecessor with the same immutable rows.
    let db = super::connect(&dir.join("runtime.sqlite"), false, schema::RUNTIME_APP).unwrap();
    db.execute_batch("DROP TABLE reporting_disabled; DROP TABLE reporting_cycles; DROP TABLE reporting_generations; DROP TABLE reporting_bindings; DROP TABLE reporting_identity;").unwrap();
    db.close().unwrap();
    let before = pc::capture(&dir).unwrap();
    let mut contract = pc::decode(
        &before.get(pc::CREDENTIAL).unwrap().small,
        &before.profile,
        &before.store,
    )
    .unwrap();
    contract.stores[1].schema_fingerprint = schema::fingerprint(&schema::runtime_v4_sql()).unwrap();
    std::fs::write(dir.join(pc::CREDENTIAL), pc::encode(&contract).unwrap()).unwrap();
    let before = pc::capture(&dir).unwrap();
    let mut upgraded = Stores::open(&dir).unwrap();
    assert!(schema::verify_structure(&upgraded.runtime, &schema::runtime_v4_sql()).is_err());
    let after: (String,String,String) = upgraded.runtime.query_row("SELECT s.payload,s.sha256,c.manifest FROM samples s JOIN collection_cycles c ON c.id=s.cycle_id WHERE s.id=?1", [&frozen.sample_id], |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?))).unwrap();
    assert_eq!(after, original);
    let row: (String, String, String) = upgraded
        .runtime
        .query_row(
            "SELECT state,body,body_sha FROM sample_uploads WHERE sample_id=?1",
            [&frozen.sample_id],
            |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?)),
        )
        .unwrap();
    assert_eq!(
        (row.0.as_str(), row.1.as_str(), row.2.as_str()),
        ("unknown", frozen.body.as_str(), frozen.body_sha.as_str())
    );
    assert_eq!(
        upgraded.sample_upload_settings().unwrap().bindings[0]
            .instance_id
            .as_str(),
        frozen.instance_id.as_str()
    );
    upgraded.clean_exit().unwrap();
    drop(upgraded);
    let after = pc::capture(&dir).unwrap();
    assert_eq!(
        before.get("runtime.sqlite").unwrap().stat.identity,
        after.get("runtime.sqlite").unwrap().stat.identity
    );
    let mut again = Stores::open(&dir).unwrap();
    assert_eq!(
        again
            .next_sample_upload(target, &again.sample_upload_bindings().unwrap(), false)
            .unwrap()
            .unwrap()
            .body,
        frozen.body
    );
    again.clean_exit().unwrap();
    drop(again);
    pc::create_sync(&dir.join(pc::STAGING), b"synthetic interrupted upgrade").unwrap();
    assert!(matches!(Stores::open(&dir), Err(e) if e == "profile_initialization_incomplete"));
    assert!(dir.join(pc::STAGING).exists());
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn interrupted_reporting_upgrade_preserves_staging_and_refuses_reopen() {
    use super::{profile_contract as pc, profile_contract_tests, schema, Stores};
    let profile = sealed_v4_fixture();
    let dir = profile.join("local-acquisition-v1");
    let db = super::connect(&dir.join("runtime.sqlite"), false, schema::RUNTIME_APP).unwrap();
    db.execute_batch("DROP TABLE reporting_disabled; DROP TABLE reporting_cycles; DROP TABLE reporting_generations; DROP TABLE reporting_bindings; DROP TABLE reporting_identity;").unwrap();
    db.close().unwrap();
    let before = pc::capture(&dir).unwrap();
    let mut contract = pc::decode(
        &before.get(pc::CREDENTIAL).unwrap().small,
        &before.profile,
        &before.store,
    )
    .unwrap();
    contract.stores[1].schema_fingerprint = schema::fingerprint(&schema::runtime_v4_sql()).unwrap();
    std::fs::write(dir.join(pc::CREDENTIAL), pc::encode(&contract).unwrap()).unwrap();
    profile_contract_tests::inject_failure(Some("reporting_upgrade_committed"));
    let error = Stores::open(&dir)
        .err()
        .expect("injected upgrade interruption");
    profile_contract_tests::inject_failure(None);
    assert_eq!(error, "synthetic_profile_reporting_upgrade_committed");
    assert!(dir.join(pc::STAGING).exists());
    let material = pc::capture(&dir).unwrap();
    assert!(matches!(Stores::open(&dir), Err(e) if e == "profile_initialization_incomplete"));
    assert_eq!(pc::capture(&dir).unwrap(), material);
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn plc_switch_keeps_unknown_and_new_samples_for_later_delivery() {
    let profile = sealed_v4_fixture();
    seed_v4_fixture(&profile, 1);
    let dir = profile.join("local-acquisition-v1");
    let mut s = super::Stores::open(&dir).unwrap();
    add_v4_cycle_for(&mut s, 1).unwrap();
    let settings = s.sample_upload_settings().unwrap();
    let target = "http://127.0.0.1:38117/api/v1/integration/plc-facts/samples";
    let sources = s.sample_upload_bindings().unwrap();
    let frozen = s
        .next_sample_upload(target, &sources, false)
        .unwrap()
        .unwrap();
    let local: String = s
        .runtime
        .query_row(
            "SELECT plc_id FROM samples WHERE id=?1",
            [&frozen.sample_id],
            |r| r.get(0),
        )
        .unwrap();
    let first = local;
    let second = settings
        .bindings
        .iter()
        .find(|b| b.local_plc_id != first)
        .unwrap()
        .local_plc_id
        .clone();
    let attempt = s.mark_sample_upload_attempt(&frozen).unwrap();
    s.record_sample_upload_response(&frozen, Err("synthetic_offline".into()), attempt)
        .unwrap();
    let mut disabled = settings.clone();
    disabled.disabled_local_plcs.push(first.clone());
    let saved = s
        .save_sample_upload_settings(disabled, settings.settings_revision)
        .unwrap();
    assert_eq!(saved.disabled_local_plcs, vec![first.clone()]);
    assert!(!s.sample_upload_enabled(&frozen.sample_id).unwrap());
    add_v4_cycle_for(&mut s, 0).unwrap();
    let eligible = s
        .next_sample_upload(target, &sources, false)
        .unwrap()
        .unwrap();
    let selected_local: String = s
        .runtime
        .query_row(
            "SELECT plc_id FROM samples WHERE id=?1",
            [&eligible.sample_id],
            |r| r.get(0),
        )
        .unwrap();
    assert_eq!(selected_local, second);
    s.clean_exit().unwrap();
    drop(s);
    let mut s = super::Stores::open(&dir).unwrap();
    let settings = s.sample_upload_settings().unwrap();
    assert_eq!(settings.disabled_local_plcs, vec![first]);
    let mut enabled = settings.clone();
    enabled.disabled_local_plcs.clear();
    s.save_sample_upload_settings(enabled, settings.settings_revision)
        .unwrap();
    let retried = s
        .next_sample_upload(target, &s.sample_upload_bindings().unwrap(), false)
        .unwrap()
        .unwrap();
    assert_eq!(retried.sample_id, frozen.sample_id);
    assert_eq!(retried.body, frozen.body);
    assert_eq!(retried.body_sha, frozen.body_sha);
    s.clean_exit().unwrap();
    drop(s);
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn switch_upgrade_preserves_old_samples_and_defaults_existing_plcs_on() {
    use super::{profile_contract as pc, schema, Stores};
    let profile = sealed_v4_fixture();
    seed_v4_fixture(&profile, 1);
    let dir = profile.join("local-acquisition-v1");
    let mut s = Stores::open(&dir).unwrap();
    let target = "http://127.0.0.1:38117/api/v1/integration/plc-facts/samples";
    let frozen = s
        .next_sample_upload(target, &s.sample_upload_bindings().unwrap(), false)
        .unwrap()
        .unwrap();
    let attempt = s.mark_sample_upload_attempt(&frozen).unwrap();
    s.record_sample_upload_response(&frozen, Err("synthetic_offline".into()), attempt)
        .unwrap();
    let before: Vec<(String, String, String)> = s
        .runtime
        .prepare("SELECT id,payload,sha256 FROM samples ORDER BY id")
        .unwrap()
        .query_map([], |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?)))
        .unwrap()
        .collect::<Result<_, _>>()
        .unwrap();
    let bindings = s.sample_upload_settings().unwrap().bindings;
    s.clean_exit().unwrap();
    drop(s);
    let db = super::connect(&dir.join("runtime.sqlite"), false, schema::RUNTIME_APP).unwrap();
    db.execute_batch("DROP TABLE reporting_disabled").unwrap();
    db.close().unwrap();
    let snap = pc::capture(&dir).unwrap();
    let mut contract = pc::decode(
        &snap.get(pc::CREDENTIAL).unwrap().small,
        &snap.profile,
        &snap.store,
    )
    .unwrap();
    contract.stores[1].schema_fingerprint =
        schema::fingerprint(&schema::runtime_v4_extended_sql()).unwrap();
    std::fs::write(dir.join(pc::CREDENTIAL), pc::encode(&contract).unwrap()).unwrap();
    let mut s = Stores::open(&dir).unwrap();
    let after: Vec<(String, String, String)> = s
        .runtime
        .prepare("SELECT id,payload,sha256 FROM samples ORDER BY id")
        .unwrap()
        .query_map([], |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?)))
        .unwrap()
        .collect::<Result<_, _>>()
        .unwrap();
    assert_eq!(before, after);
    assert_eq!(s.sample_upload_settings().unwrap().bindings, bindings);
    let preserved: (String, String, String, u32) = s
        .runtime
        .query_row(
            "SELECT state,body,body_sha,attempt FROM sample_uploads WHERE sample_id=?1",
            [&frozen.sample_id],
            |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?, r.get(3)?)),
        )
        .unwrap();
    assert_eq!(
        (
            preserved.0.as_str(),
            preserved.1.as_str(),
            preserved.2.as_str(),
            preserved.3
        ),
        (
            "unknown",
            frozen.body.as_str(),
            frozen.body_sha.as_str(),
            attempt
        )
    );
    assert!(s
        .sample_upload_settings()
        .unwrap()
        .disabled_local_plcs
        .is_empty());
    s.clean_exit().unwrap();
    drop(s);
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn interrupted_switch_upgrade_preserves_staging_and_refuses_reopen() {
    use super::{profile_contract as pc, profile_contract_tests, schema, Stores};
    let profile = sealed_v4_fixture();
    let dir = profile.join("local-acquisition-v1");
    let db = super::connect(&dir.join("runtime.sqlite"), false, schema::RUNTIME_APP).unwrap();
    db.execute_batch("DROP TABLE reporting_disabled").unwrap();
    db.close().unwrap();
    let snap = pc::capture(&dir).unwrap();
    let mut contract = pc::decode(
        &snap.get(pc::CREDENTIAL).unwrap().small,
        &snap.profile,
        &snap.store,
    )
    .unwrap();
    contract.stores[1].schema_fingerprint =
        schema::fingerprint(&schema::runtime_v4_extended_sql()).unwrap();
    std::fs::write(dir.join(pc::CREDENTIAL), pc::encode(&contract).unwrap()).unwrap();
    profile_contract_tests::inject_failure(Some("reporting_switches_upgrade_committed"));
    let error = Stores::open(&dir)
        .err()
        .expect("injected upgrade interruption");
    profile_contract_tests::inject_failure(None);
    assert_eq!(
        error,
        "synthetic_profile_reporting_switches_upgrade_committed"
    );
    assert!(dir.join(pc::STAGING).exists());
    let material = pc::capture(&dir).unwrap();
    assert!(matches!(Stores::open(&dir), Err(e) if e == "profile_initialization_incomplete"));
    assert_eq!(pc::capture(&dir).unwrap(), material);
    std::fs::remove_dir_all(profile).unwrap();
}

fn database() -> Connection {
    let c = Connection::open_in_memory().unwrap();
    c.execute_batch("PRAGMA foreign_keys=ON; CREATE TABLE samples(id TEXT PRIMARY KEY,payload_bytes INTEGER NOT NULL,saved_at TEXT NOT NULL,cycle_id TEXT NOT NULL); INSERT INTO samples VALUES('first',100,'2026-11-10T10:00:00.000+08:00','cycle'),('second',200,'2026-11-10T10:00:01.000+08:00','cycle'); CREATE TABLE reporting_cycles(cycle_id TEXT PRIMARY KEY,instance_id TEXT,plc_id TEXT,source_generation TEXT);").unwrap();
    c.execute_batch(sample_upload::SQL).unwrap();
    c.execute_batch("CREATE TABLE sample_delivery(sample_id TEXT PRIMARY KEY,state TEXT); CREATE TABLE delivery_parts(sample_id TEXT,part INTEGER,parts INTEGER,state TEXT,batch_id TEXT,receipt_id TEXT); CREATE TABLE delivery_cycles(cycle_id TEXT); CREATE TABLE delivery_batches(batch_id TEXT PRIMARY KEY,members TEXT,state TEXT,attempt INTEGER,parent_id TEXT); CREATE TABLE delivery_receipts(batch_id TEXT,receipt_id TEXT,terminal TEXT); INSERT INTO sample_delivery VALUES('first','pending'),('second','pending');").unwrap();
    c
}

#[cfg(unix)]
pub(crate) fn sealed_v4_fixture() -> std::path::PathBuf {
    sealed_fixture(4)
}

#[cfg(unix)]
pub(crate) fn sealed_v3_inflight_fixture() -> std::path::PathBuf {
    let profile = sealed_fixture(3);
    let mut store = super::Stores::open(&profile.join("local-acquisition-v1")).unwrap();
    let config = super::tests::configuration();
    let revision = super::tests::activated(&mut store, &config);
    let sample = store
        .commit_cycle(super::tests::cycle(&config, &revision))
        .unwrap();
    let built = store
        .build_delivery_cycle(sample["cycleId"].as_str().unwrap())
        .unwrap();
    super::delivery_tests::adopt(&mut store, &built);
    let settings = store.delivery_settings().unwrap();
    let frozen = store.freeze_cycle(built, &settings, true).unwrap().unwrap();
    assert_eq!(store.mark_dispatch(&frozen).unwrap(), 1);
    store.clean_exit().unwrap();
    drop(store);
    profile
}

#[cfg(unix)]
pub(crate) fn sealed_fixture(version: u32) -> std::path::PathBuf {
    use super::{profile_contract as pc, schema, Stores};
    use crate::domain::{
        business_time,
        local_configuration::{id, Configuration},
        local_sample::encode,
    };
    use std::os::unix::fs::PermissionsExt;
    assert!([3, 4].contains(&version));
    let root = synthetic_temp_root();
    let profile = root.join(format!("profile-{}", id()));
    std::fs::create_dir(&profile).unwrap();
    let lock = crate::infrastructure::local_profile_lock::ProfileLock::acquire(&profile).unwrap();
    let dir = profile.join("local-acquisition-v1");
    std::fs::create_dir(&dir).unwrap();
    std::fs::set_permissions(&dir, std::fs::Permissions::from_mode(0o700)).unwrap();
    let instance = id();
    for role in ["config", "runtime"] {
        let path = dir.join(format!("{role}.sqlite"));
        std::fs::File::create(&path).unwrap();
        let db = super::connect(
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
            db.execute_batch(&schema::config_sql()).unwrap();
            db.execute(
                "INSERT INTO instance_metadata VALUES(1,?1,2,'asia-shanghai-rfc3339-ms-v1')",
                [&instance],
            )
            .unwrap();
            db.execute(
                "INSERT INTO configuration_draft VALUES(1,?1,?2,'[]')",
                rusqlite::params![id(), encode(&Configuration::default()).unwrap()],
            )
            .unwrap();
            db.execute_batch(&format!(
                "PRAGMA application_id={};PRAGMA user_version=2",
                schema::CONFIG_APP
            ))
            .unwrap();
        } else {
            db.execute_batch(&if version == 4 {
                schema::runtime_v4_sql()
            } else {
                schema::runtime_v3_sql()
            })
            .unwrap();
            db.execute(
                "INSERT INTO runtime_metadata VALUES(1,?1,?2,1,NULL,'asia-shanghai-rfc3339-ms-v1')",
                rusqlite::params![instance, version],
            )
            .unwrap();
            let old = crate::domain::local_delivery::DeliverySettings::default();
            db.execute(
                "INSERT INTO delivery_settings(id,settings_revision,payload) VALUES(1,?1,?2)",
                rusqlite::params![old.settings_revision, encode(&old).unwrap()],
            )
            .unwrap();
            if version == 4 {
                db.execute(
                    "INSERT INTO sample_upload_settings VALUES(1,?1,NULL,'/api/v1/integration/plc-facts/samples',5)",
                    [id()],
                )
                .unwrap();
            }
            db.execute_batch(&format!(
                "PRAGMA application_id={};PRAGMA user_version={version}",
                schema::RUNTIME_APP
            ))
            .unwrap();
        }
        db.close().unwrap();
    }
    let snap = pc::capture(&dir).unwrap();
    let entries = [
        ("config", schema::CONFIG_APP, 2, schema::config_sql()),
        (
            "runtime",
            schema::RUNTIME_APP,
            version,
            if version == 4 {
                schema::runtime_v4_sql()
            } else {
                schema::runtime_v3_sql()
            },
        ),
    ]
    .into_iter()
    .map(|(role, app, version, ddl)| pc::StoreContract {
        role: role.into(),
        file_name: format!("{role}.sqlite"),
        application_id: app,
        schema_version: version,
        schema_fingerprint: schema::fingerprint(&ddl).unwrap(),
        file_identity: snap
            .get(&format!("{role}.sqlite"))
            .unwrap()
            .stat
            .identity
            .clone(),
    })
    .collect();
    let contract = pc::Contract {
        contract: "daa-profile-recovery/v1".into(),
        init_id: id(),
        instance_id: instance,
        created_at: business_time::now(),
        time_profile: business_time::TIME_PROFILE.into(),
        identity_profile: "unix-dev-ino/v1".into(),
        canonical_profile_dir: profile.to_str().unwrap().into(),
        canonical_store_dir: dir.to_str().unwrap().into(),
        profile_identity: snap.profile_identity.unwrap(),
        store_identity: snap.store_identity.unwrap(),
        page_size: 4096,
        journal_mode: "delete".into(),
        stores: entries,
    };
    let path = dir.join(pc::CREDENTIAL);
    std::fs::write(&path, pc::encode(&contract).unwrap()).unwrap();
    std::fs::set_permissions(&path, std::fs::Permissions::from_mode(0o600)).unwrap();
    drop(lock);
    // 可启动性与 sealed 身份由真实产品工厂校验，而不是 fixture 自证。
    let mut s = Stores::open(&dir).unwrap();
    s.clean_exit().unwrap();
    drop(s);
    profile
}

#[cfg(unix)]
pub(super) fn bind_legacy_fixture(
    s: &mut super::Stores,
    config: &crate::domain::local_configuration::Configuration,
) {
    let mut settings = s.sample_upload_settings().unwrap();
    let expected = settings.settings_revision.clone();
    for plc in &config.plcs {
        let generation: String = s
            .runtime
            .query_row(
                "SELECT generation FROM plc_sources WHERE plc_id=?1",
                [&plc.id],
                |r| r.get(0),
            )
            .unwrap();
        settings
            .bindings
            .push(crate::domain::sample_upload::ReportingBinding {
                local_plc_id: plc.id.clone(),
                instance_id: s.instance.clone(),
                plc_id: plc.id.clone(),
                source_generation: generation,
            });
    }
    s.save_sample_upload_settings(settings, expected).unwrap();
}

#[cfg(unix)]
pub(crate) fn seed_v4_fixture(profile: &std::path::Path, cycles: usize) {
    let mut s = super::Stores::open(&profile.join("local-acquisition-v1")).unwrap();
    let config = super::tests::configuration();
    let revision = super::tests::activated(&mut s, &config);
    bind_legacy_fixture(&mut s, &config);
    for _ in 0..cycles {
        s.commit_cycle(super::tests::cycle(&config, &revision))
            .unwrap();
    }
    s.clean_exit().unwrap();
}

#[cfg(unix)]
pub(crate) fn add_v4_cycle(
    s: &mut super::Stores,
) -> crate::domain::local_configuration::LocalResult<()> {
    let revision = s.configuration()?.active.ok_or("active_missing")?;
    let config = s.revision(&revision)?;
    s.commit_cycle(super::tests::cycle(&config, &revision))?;
    Ok(())
}

#[cfg(unix)]
pub(crate) fn add_v4_cycle_for(
    s: &mut super::Stores,
    index: usize,
) -> crate::domain::local_configuration::LocalResult<()> {
    let revision = s.configuration()?.active.ok_or("active_missing")?;
    let mut config = s.revision(&revision)?;
    config.plcs.swap(0, index);
    let group_index = config
        .groups
        .iter()
        .position(|g| g.plc_id == config.plcs[0].id)
        .ok_or("group_missing")?;
    config.groups.swap(0, group_index);
    s.commit_cycle(super::tests::cycle(&config, &revision))?;
    Ok(())
}

#[cfg(unix)]
pub(crate) fn captured_v4_cycle_for(
    s: &super::Stores,
    index: usize,
) -> crate::domain::local_configuration::LocalResult<(
    crate::domain::local_sample::CycleInput,
    Option<crate::domain::sample_upload::ReportingIdentity>,
)> {
    let revision = s.configuration()?.active.ok_or("active_missing")?;
    let mut config = s.revision(&revision)?;
    config.plcs.swap(0, index);
    let group_index = config
        .groups
        .iter()
        .position(|g| g.plc_id == config.plcs[0].id)
        .ok_or("group_missing")?;
    config.groups.swap(0, group_index);
    let identity = s.reporting_identity(&config.plcs[0].id)?;
    Ok((super::tests::cycle(&config, &revision), identity))
}

#[cfg(unix)]
pub(crate) fn deactivate_second_plc(
    s: &mut super::Stores,
) -> crate::domain::local_configuration::LocalResult<()> {
    let revision = s.configuration()?.active.ok_or("active_missing")?;
    let mut config = s.revision(&revision)?;
    let other = config.plcs[1].id.clone();
    config.plcs.retain(|x| x.id != other);
    config.dbs.retain(|x| x.plc_id != other);
    config.points.retain(|x| x.plc_id != other);
    config.groups.retain(|x| x.plc_id != other);
    config.sources.retain(|x| x.plc_id != other);
    super::tests::activated(s, &config);
    Ok(())
}

#[test]
fn old_ledger_requires_proof_across_parts_batches_and_relations() {
    let c = database();
    assert_eq!(
        sample_upload::legacy_status(&c, "first", "cycle").unwrap(),
        LegacyStatus::NeverSent
    );
    c.execute_batch("INSERT INTO delivery_cycles VALUES('cycle'); INSERT INTO delivery_parts VALUES('first',1,1,'prepared','parent',NULL); INSERT INTO delivery_batches VALUES('parent','[{\"sampleId\":\"first\"}]','prepared',0,NULL); INSERT INTO delivery_batches VALUES('child','[]','prepared',0,'parent');").unwrap();
    assert_eq!(
        sample_upload::legacy_status(&c, "first", "cycle").unwrap(),
        LegacyStatus::NeverSent
    );
    c.execute(
        "UPDATE delivery_batches SET attempt=1 WHERE batch_id='child'",
        [],
    )
    .unwrap();
    assert_eq!(
        sample_upload::legacy_status(&c, "first", "cycle").unwrap(),
        LegacyStatus::NeedsReview
    );
    c.execute(
        "UPDATE delivery_batches SET attempt=0,state='unknown' WHERE batch_id='child'",
        [],
    )
    .unwrap();
    assert_eq!(
        sample_upload::legacy_status(&c, "first", "cycle").unwrap(),
        LegacyStatus::NeedsReview
    );
    c.execute_batch("UPDATE delivery_parts SET state='acknowledged',receipt_id='receipt'; INSERT INTO delivery_receipts VALUES('parent','receipt','acknowledged'); UPDATE sample_delivery SET state='acknowledged' WHERE sample_id='first';").unwrap();
    assert_eq!(
        sample_upload::legacy_status(&c, "first", "cycle").unwrap(),
        LegacyStatus::HistoricalAcknowledged
    );
    c.execute(
        "UPDATE sample_delivery SET state='pending' WHERE sample_id='first'",
        [],
    )
    .unwrap();
    assert_eq!(
        sample_upload::legacy_status(&c, "first", "cycle").unwrap(),
        LegacyStatus::NeedsReview
    );
    c.execute(
        "UPDATE sample_delivery SET state='acknowledged' WHERE sample_id='first'",
        [],
    )
    .unwrap();
    c.execute("UPDATE delivery_parts SET receipt_id=NULL", [])
        .unwrap();
    assert_eq!(
        sample_upload::legacy_status(&c, "first", "cycle").unwrap(),
        LegacyStatus::NeedsReview
    );
    assert_eq!(
        c.query_row::<i64, _, _>("SELECT count(*) FROM sample_uploads", [], |r| r.get(0))
            .unwrap(),
        0
    );
}

fn state(c: &Connection, id: &str) -> (String, u32, Option<String>, Option<String>) {
    c.query_row(
        "SELECT state,attempt,receipt,receipt_sha FROM sample_uploads WHERE sample_id=?1",
        [id],
        |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?, r.get(3)?)),
    )
    .unwrap()
}

#[test]
fn runtime4_schema_retains_legacy_ledger_and_checks_new_empty_ledger() {
    let c = Connection::open_in_memory().unwrap();
    c.execute_batch(&super::schema::runtime_v4_sql()).unwrap();
    c.execute_batch("PRAGMA user_version=4").unwrap();
    let old = crate::domain::local_delivery::DeliverySettings::default();
    c.execute(
        "INSERT INTO delivery_settings(id,settings_revision,payload) VALUES(1,?1,?2)",
        rusqlite::params![old.settings_revision, serde_json::to_string(&old).unwrap()],
    )
    .unwrap();
    let revision = crate::domain::local_configuration::id();
    c.execute(
        "INSERT INTO sample_upload_settings VALUES(1,?1,NULL,'/api/v1/integration/plc-facts/samples',5)",
        [&revision],
    )
    .unwrap();
    super::delivery::verify_schema(&c).unwrap();
    sample_upload::full_check(&c, "instance").unwrap();
    c.execute(
        "UPDATE sample_upload_settings SET origin='http://user:pass@127.0.0.1'",
        [],
    )
    .unwrap();
    assert!(sample_upload::full_check(&c, "instance").is_err());
}

#[test]
fn retries_keep_original_bytes_and_only_matching_receipt_confirms() {
    let mut c = database();
    let f = fixture("first", "plc");
    assert_eq!(
        sample_upload::pending_usage(&c).unwrap(),
        (2, 300, Some("2026-11-10T10:00:00.000+08:00".into()))
    );
    sample_upload::freeze(&mut c, &f, "2026-11-10T10:00:00.000+08:00").unwrap();
    sample_upload::freeze(&mut c, &f, "2026-11-10T10:00:00.000+08:00").unwrap();
    let mut changed = f.clone();
    changed.origin = "http://127.0.0.1:8002/api/v1/integration/plc-facts/samples".into();
    assert_eq!(
        sample_upload::freeze(&mut c, &changed, "2026-11-10T10:00:00.000+08:00").unwrap_err(),
        "sample_binding_conflict"
    );
    assert_eq!(
        sample_upload::mark_attempt(&mut c, &f, "2026-11-10T10:00:01.000+08:00").unwrap(),
        1
    );
    let wrong = json!({"code":200,"message":"success","data":{"contractVersion":"plc-facts/v2","instanceId":"instance","sampleId":"other","status":"committed","outcome":"created"}}).to_string();
    assert_eq!(
        sample_upload::apply(
            &mut c,
            &f,
            200,
            "application/json",
            wrong.as_bytes(),
            "2026-11-10T10:00:02.000+08:00",
            "2026-11-10T10:00:03.000+08:00"
        )
        .unwrap(),
        Reply::Retry("invalid_receipt")
    );
    assert_eq!(state(&c, "first"), ("unknown".into(), 1, None, None));
    assert_eq!(
        sample_upload::mark_attempt(&mut c, &f, "2026-11-10T10:00:03.000+08:00").unwrap(),
        2
    );
    sample_upload::recover(&mut c, "2026-11-10T10:00:04.000+08:00").unwrap();
    assert_eq!(state(&c, "first"), ("unknown".into(), 2, None, None));
    assert_eq!(
        sample_upload::mark_attempt(&mut c, &f, "2026-11-10T10:00:05.000+08:00").unwrap(),
        3
    );
    let receipt = json!({"code":200,"message":"success","data":{"contractVersion":"plc-facts/v2","instanceId":"instance","sampleId":"first","status":"committed","outcome":"duplicate"}}).to_string();
    assert!(sample_upload::apply(
        &mut c,
        &changed,
        200,
        "application/json",
        receipt.as_bytes(),
        "2026-11-10T10:00:06.000+08:00",
        "2026-11-10T10:00:07.000+08:00"
    )
    .is_err());
    assert_eq!(
        sample_upload::apply(
            &mut c,
            &f,
            200,
            "application/json",
            receipt.as_bytes(),
            "2026-11-10T10:00:06.000+08:00",
            "2026-11-10T10:00:07.000+08:00"
        )
        .unwrap(),
        Reply::Committed
    );
    assert_eq!(
        state(&c, "first"),
        (
            "acknowledged".into(),
            3,
            Some(receipt.clone()),
            Some(pf::sha(receipt.as_bytes()))
        )
    );
    assert_eq!(
        sample_upload::pending_usage(&c).unwrap(),
        (1, 200, Some("2026-11-10T10:00:01.000+08:00".into()))
    );
    assert_eq!(
        c.query_row::<String, _, _>(
            "SELECT state FROM sample_delivery WHERE sample_id='first'",
            [],
            |r| r.get(0)
        )
        .unwrap(),
        "pending"
    );
    let stored: (String, String, String) = c
        .query_row(
            "SELECT body,body_sha,origin FROM sample_uploads WHERE sample_id='first'",
            [],
            |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?)),
        )
        .unwrap();
    assert_eq!(stored, (f.body, f.body_sha, f.origin));
}

#[test]
fn scope_rejection_blocks_only_its_source_and_preserves_material() {
    let mut c = database();
    let first = fixture("first", "plc-a");
    let second = fixture("second", "plc-b");
    for f in [&first, &second] {
        sample_upload::freeze(&mut c, f, "2026-11-10T10:00:00.000+08:00").unwrap();
    }
    sample_upload::mark_attempt(&mut c, &first, "2026-11-10T10:00:01.000+08:00").unwrap();
    let raw = json!({"code":403,"message":"plc_facts_v2.scope_rejected","data":null,"errorCode":"plc_facts_v2.scope_rejected"}).to_string();
    assert_eq!(
        sample_upload::apply(
            &mut c,
            &first,
            403,
            "application/json",
            raw.as_bytes(),
            "2026-11-10T10:00:02.000+08:00",
            "2026-11-10T10:00:03.000+08:00"
        )
        .unwrap(),
        Reply::SourceBlocked
    );
    assert_eq!(state(&c, "first"), ("unknown".into(), 1, None, None));
    assert!(sample_upload::mark_attempt(&mut c, &first, "2026-11-10T10:00:03.000+08:00").is_err());
    assert_eq!(
        sample_upload::mark_attempt(&mut c, &second, "2026-11-10T10:00:03.000+08:00").unwrap(),
        1
    );
}

#[cfg(unix)]
#[test]
fn sealed_v4_reopen_preserves_unknown_and_retention_uses_only_v2_ack() {
    use super::{profile_contract, tests, Stores};
    use crate::domain::{
        local_configuration::Configuration,
        local_sample::{CycleManifest, SamplePayload},
        sample_upload as wire,
    };
    let profile = sealed_v4_fixture();
    let dir = profile.join("local-acquisition-v1");
    let mut store = Stores::open(&dir).unwrap();
    let config = tests::configuration();
    let revision = tests::activated(&mut store, &config);
    bind_legacy_fixture(&mut store, &config);
    store
        .commit_cycle(tests::cycle(&config, &revision))
        .unwrap();
    let rows: Vec<(String,String,String,String,String,String,String)> = store.runtime.prepare("SELECT s.id,s.payload,s.sha256,c.manifest,c.sha256,x.payload,x.sha256 FROM samples s JOIN collection_cycles c ON c.id=s.cycle_id JOIN configuration_contexts x ON x.revision=s.revision ORDER BY s.id").unwrap().query_map([], |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?,r.get(4)?,r.get(5)?,r.get(6)?))).unwrap().collect::<Result<_,_>>().unwrap();
    assert_eq!(rows.len(), 2);
    let mut frozen = Vec::new();
    for (id, raw, sha, manifest, _, context, _) in rows {
        let sample: SamplePayload = serde_json::from_str(&raw).unwrap();
        let manifest: CycleManifest = serde_json::from_str(&manifest).unwrap();
        let context: Configuration = serde_json::from_str(&context).unwrap();
        let body = wire::build(&sample, &sha, &manifest, &context, &store.instance).unwrap();
        let f = Frozen {
            sample_id: id,
            instance_id: store.instance.clone(),
            plc_id: sample.plc_id,
            db_number: sample.db_number,
            source_generation: sample.source_generation,
            origin: "http://127.0.0.1:8001/api/v1/integration/plc-facts/samples".into(),
            body_sha: pf::sha(body.as_bytes()),
            body,
        };
        sample_upload::freeze(&mut store.runtime, &f, &crate::domain::business_time::now())
            .unwrap();
        frozen.push(f);
    }
    let commit = |store: &mut Stores, f: &Frozen| {
        let at = crate::domain::business_time::now();
        sample_upload::mark_attempt(&mut store.runtime, f, &at).unwrap();
        let receipt = json!({"code":200,"message":"success","data":{"contractVersion":"plc-facts/v2","instanceId":f.instance_id,"sampleId":f.sample_id,"status":"committed","outcome":"created"}}).to_string();
        assert_eq!(
            sample_upload::apply(
                &mut store.runtime,
                f,
                200,
                "application/json",
                receipt.as_bytes(),
                &at,
                &at
            )
            .unwrap(),
            Reply::Committed
        );
    };
    commit(&mut store, &frozen[0]);
    assert_eq!(
        store
            .capacity(4 * 1024 * 1024 * 1024)
            .unwrap()
            .pending_count,
        1
    );
    assert_eq!(
        store
            .runtime
            .query_row::<String, _, _>(
                "SELECT state FROM sample_delivery WHERE sample_id=?1",
                [&frozen[0].sample_id],
                |r| r.get(0)
            )
            .unwrap(),
        "pending"
    );
    let at = crate::domain::business_time::now();
    sample_upload::mark_attempt(&mut store.runtime, &frozen[1], &at).unwrap();
    assert_eq!(
        store
            .cleanup_acknowledged(0, 4 * 1024 * 1024 * 1024)
            .unwrap(),
        0
    );
    drop(store); // 模拟已标记派发后进程中断，不补写 clean_exit。
    let mut reopened = Stores::open(&dir).unwrap();
    let saved: (String, String, String) = reopened
        .runtime
        .query_row(
            "SELECT state,body,body_sha FROM sample_uploads WHERE sample_id=?1",
            [&frozen[1].sample_id],
            |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?)),
        )
        .unwrap();
    assert_eq!(
        saved,
        (
            "unknown".into(),
            frozen[1].body.clone(),
            frozen[1].body_sha.clone()
        )
    );
    assert_eq!(
        reopened
            .capacity(4 * 1024 * 1024 * 1024)
            .unwrap()
            .pending_count,
        1
    );
    commit(&mut reopened, &frozen[1]);
    assert_eq!(
        reopened
            .capacity(4 * 1024 * 1024 * 1024)
            .unwrap()
            .pending_count,
        0
    );
    std::thread::sleep(std::time::Duration::from_millis(20));
    reopened
        .runtime
        .execute(
            "INSERT INTO sample_references VALUES(?1,'synthetic-protected-reference')",
            [&frozen[0].sample_id],
        )
        .unwrap();
    assert_eq!(
        reopened
            .cleanup_acknowledged(0, 4 * 1024 * 1024 * 1024)
            .unwrap(),
        0
    );
    reopened.runtime.execute("DELETE FROM sample_references WHERE sample_id=?1 AND reference_id='synthetic-protected-reference'", [&frozen[0].sample_id]).unwrap();
    // 上一批扫描游标会先走到末尾，再从头执行正常维护。
    assert_eq!(
        reopened
            .cleanup_acknowledged(0, 4 * 1024 * 1024 * 1024)
            .unwrap(),
        0
    );
    assert_eq!(
        reopened
            .cleanup_acknowledged(0, 4 * 1024 * 1024 * 1024)
            .unwrap(),
        2
    );
    assert_eq!(
        reopened
            .runtime
            .query_row::<i64, _, _>("SELECT count(*) FROM samples", [], |r| r.get(0))
            .unwrap(),
        0
    );
    reopened.clean_exit().unwrap();
    drop(reopened);
    assert!(profile_contract::capture(&dir).is_ok());
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn v4_candidates_bind_oldest_and_newest_to_confirmed_source_and_target() {
    use super::{tests, Stores};
    let profile = sealed_v4_fixture();
    let dir = profile.join("local-acquisition-v1");
    let mut store = Stores::open(&dir).unwrap();
    let config = tests::configuration();
    let revision = tests::activated(&mut store, &config);
    bind_legacy_fixture(&mut store, &config);
    store
        .commit_cycle(tests::cycle(&config, &revision))
        .unwrap();
    let old = store.sample_upload_settings().unwrap();
    let mut settings = old.clone();
    settings.origin = Some("http://127.0.0.1:8001".into());
    settings.interval_seconds = 5;
    let saved = store
        .save_sample_upload_settings(settings.clone(), old.settings_revision.clone())
        .unwrap();
    assert_ne!(saved.settings_revision, old.settings_revision);
    assert_eq!(
        store
            .save_sample_upload_settings(settings, old.settings_revision)
            .unwrap_err(),
        "delivery_settings_conflict"
    );
    let bindings = store.sample_upload_bindings().unwrap();
    assert!(bindings.len() >= 2);
    let first = store
        .next_sample_upload(
            "http://127.0.0.1:8001/api/v1/integration/plc-facts/samples",
            &bindings,
            false,
        )
        .unwrap()
        .unwrap();
    let last = store
        .next_sample_upload(
            "http://127.0.0.1:8001/api/v1/integration/plc-facts/samples",
            &bindings,
            true,
        )
        .unwrap()
        .unwrap();
    assert_ne!(first.sample_id, last.sample_id);
    assert!(store
        .next_sample_upload(
            "http://127.0.0.1:8002/api/v1/integration/plc-facts/samples",
            &bindings,
            false
        )
        .unwrap()
        .is_none());
    let first_again = store
        .next_sample_upload(
            "http://127.0.0.1:8001/api/v1/integration/plc-facts/samples",
            &bindings,
            false,
        )
        .unwrap()
        .unwrap();
    assert_eq!(first_again, first);
    store.clean_exit().unwrap();
    drop(store);
    let mut reopened = Stores::open(&dir).unwrap();
    assert_eq!(
        reopened
            .next_sample_upload(
                "http://127.0.0.1:8001/api/v1/integration/plc-facts/samples",
                &bindings,
                false
            )
            .unwrap()
            .unwrap(),
        first
    );
    reopened.clean_exit().unwrap();
    drop(reopened);
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn target_change_requires_explicit_rebinding_for_attempted_bytes() {
    use super::{tests, Stores};
    let profile = sealed_v4_fixture();
    let dir = profile.join("local-acquisition-v1");
    let mut store = Stores::open(&dir).unwrap();
    let config = tests::configuration();
    let revision = tests::activated(&mut store, &config);
    bind_legacy_fixture(&mut store, &config);
    store
        .commit_cycle(tests::cycle(&config, &revision))
        .unwrap();
    let mut settings = store.sample_upload_settings().unwrap();
    let old_revision = settings.settings_revision.clone();
    settings.origin = Some("http://127.0.0.1:8001".into());
    let settings = store
        .save_sample_upload_settings(settings, old_revision)
        .unwrap();
    let old_url = settings.target().unwrap().unwrap();
    let bindings = store.sample_upload_bindings().unwrap();
    let first = store
        .next_sample_upload(&old_url, &bindings, false)
        .unwrap()
        .unwrap();
    let second = store
        .next_sample_upload(&old_url, &bindings, true)
        .unwrap()
        .unwrap();
    let attempt = store.mark_sample_upload_attempt(&first).unwrap();
    assert_eq!(attempt, 1);
    assert_eq!(
        store
            .record_sample_upload_response(&first, Err("lost".into()), attempt)
            .unwrap()
            .0,
        Reply::Retry("transport_unknown")
    );
    let waiting = vec![first.sample_id.clone()];
    assert_eq!(
        store
            .next_sample_upload_ready(&old_url, &bindings, false, &waiting)
            .unwrap()
            .unwrap()
            .sample_id,
        second.sample_id
    );
    assert_eq!(
        store
            .next_sample_upload_ready(&old_url, &bindings, false, &[])
            .unwrap()
            .unwrap()
            .sample_id,
        first.sample_id
    );

    let mut changed = settings.clone();
    changed.origin = Some("http://127.0.0.1:8002".into());
    changed.path = "/compatible/samples".into();
    let changed = store
        .save_sample_upload_settings(changed, settings.settings_revision)
        .unwrap();
    let new_url = changed.target().unwrap().unwrap();
    assert!(store
        .next_sample_upload(&new_url, &bindings, false)
        .unwrap()
        .is_none());
    store
        .confirm_sample_upload_sources(&new_url, &bindings)
        .unwrap();
    let unsent = store
        .next_sample_upload(&new_url, &bindings, false)
        .unwrap()
        .unwrap();
    assert_eq!(unsent.sample_id, second.sample_id);
    assert_eq!(unsent.body, second.body);
    assert!(store
        .rebind_sample_upload(
            &first.sample_id,
            &old_url,
            &new_url,
            &changed.settings_revision,
            &[]
        )
        .is_err());
    store
        .rebind_sample_upload(
            &first.sample_id,
            &old_url,
            &new_url,
            &changed.settings_revision,
            &bindings,
        )
        .unwrap();
    let rebound = store
        .next_sample_upload(&new_url, &bindings, false)
        .unwrap()
        .unwrap();
    assert_eq!(rebound.sample_id, first.sample_id);
    assert_eq!(rebound.body, first.body);
    assert_eq!(rebound.body_sha, first.body_sha);
    assert_eq!(store.mark_sample_upload_attempt(&rebound).unwrap(), 2);
    let receipt = json!({"code":200,"message":"success","data":{"contractVersion":"plc-facts/v2","instanceId":first.instance_id,"sampleId":first.sample_id,"status":"committed","outcome":"duplicate"}}).to_string();
    let at = crate::domain::business_time::now();
    assert!(sample_upload::apply_for_attempt(
        &mut store.runtime,
        &first,
        1,
        200,
        "application/json",
        receipt.as_bytes(),
        &at,
        &at
    )
    .is_err());
    assert_eq!(
        sample_upload::apply_for_attempt(
            &mut store.runtime,
            &rebound,
            2,
            200,
            "application/json",
            receipt.as_bytes(),
            &at,
            &at
        )
        .unwrap(),
        Reply::Committed
    );
    let detail = store.get_sample_upload(&rebound.sample_id).unwrap();
    assert_eq!(detail["attempts"][0]["url"], old_url);
    assert_eq!(detail["attempts"][1]["url"], new_url);
    assert_eq!(detail["rebindings"].as_array().unwrap().len(), 1);
    store.clean_exit().unwrap();
    drop(store);
    let mut reopened = Stores::open(&dir).unwrap();
    assert_eq!(
        reopened.get_sample_upload(&rebound.sample_id).unwrap()["state"],
        "acknowledged"
    );
    reopened.clean_exit().unwrap();
    drop(reopened);
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn versioned_configuration_import_activation_and_two_db_collection() {
    use super::source_import_tests::{confirm, engine, req};
    use crate::domain::local_configuration::{Group, LocalResult, Plc};
    use crate::infrastructure::managed_s7::Transport;
    struct Synthetic;
    impl Transport for Synthetic {
        fn connect(&mut self, _: &Plc) -> LocalResult<()> {
            Ok(())
        }
        fn read(&mut self, db: u16, _: u32, size: u32) -> LocalResult<Vec<u8>> {
            if db == 502 {
                Err("synthetic_read_failure".into())
            } else {
                Ok(vec![7; size as usize])
            }
        }
        fn disconnect(&mut self) {}
        fn connected(&self) -> bool {
            true
        }
    }
    fn source(name: &str, count: usize) -> String {
        let fields = (0..count)
            .map(|i| format!("p{i:03}: BYTE; "))
            .collect::<String>();
        format!("DATA_BLOCK \"{name}\" {{ S7_Optimized_Access := 'FALSE' }} VAR {fields} END_VAR BEGIN END_DATA_BLOCK")
    }
    let one = source("First", 400);
    let two = source("Second", 512);
    let profile = sealed_v4_fixture();
    let e = engine(&profile);
    let v = e.configuration().unwrap();
    let mut c = v.draft;
    let plc_id = crate::domain::local_configuration::id();
    let group_id = crate::domain::local_configuration::id();
    c.plcs.push(Plc {
        id: plc_id.clone(),
        name: "Synthetic".into(),
        enabled: true,
        host: "127.0.0.1".into(),
        port: 35117,
        rack: 0,
        slot: 1,
        connect_timeout_ms: 1000,
        io_timeout_ms: 500,
        deadline_ms: 5000,
    });
    c.groups.push(Group {
        id: group_id.clone(),
        plc_id,
        name: "Large group".into(),
        enabled: true,
        interval_ms: 1000,
    });
    let v = e.save(c, v.etag).unwrap();
    let r = req(
        &v.draft,
        &v.etag,
        &[("first.db", &one), ("second.db", &two)],
    );
    let preview = e.import_selected(r.clone()).unwrap();
    assert!(preview.can_confirm, "{:?}", preview.issues);
    confirm(&e, r);
    for db in e.configuration().unwrap().draft.dbs {
        let v = e.configuration().unwrap();
        let offsets = e.offsets_at(db.id.clone(), Some(v.etag.clone())).unwrap();
        e.confirm_offsets_at(
            db.id,
            offsets.iter().map(|p| p.point_id.clone()).collect(),
            v.etag,
            Some(offsets[0].layout_digest.clone()),
        )
        .unwrap();
    }
    let mut v = e.configuration().unwrap();
    for point in &mut v.draft.points {
        point.enabled = true;
        point.group_id = Some(group_id.clone());
    }
    let v = e.save(v.draft, v.etag).unwrap();
    assert_eq!(v.draft.points.len(), 912);
    assert!(v.issues.is_empty(), "{:?}", v.issues);
    let r = req(
        &v.draft,
        &v.etag,
        &[("first.db", &one), ("second.db", &two)],
    );
    let p = e.import_selected(r).unwrap();
    assert!(p.can_confirm, "{:?}", p.issues);
    assert!(
        !p.readiness.iter().any(|i| [
            "group_limits",
            "db_point_limits",
            "read_budget",
            "encoding_budget"
        ]
        .contains(&i.code.as_str())),
        "{:?}",
        p.readiness
    );
    let result = e.activate(v.etag.clone(), v.active.clone(), false).unwrap();
    let revision = result["active"].as_str().unwrap().to_string();
    let local_plc = v.draft.plcs[0].id.clone();
    e.storage
        .call(false, move |s| {
            let generation: String = s
                .runtime
                .query_row(
                    "SELECT generation FROM plc_sources WHERE plc_id=?1",
                    [&local_plc],
                    |r| r.get(0),
                )
                .map_err(super::sql_error)?;
            let mut settings = s.sample_upload_settings()?;
            let expected = settings.settings_revision.clone();
            settings
                .bindings
                .push(crate::domain::sample_upload::ReportingBinding {
                    local_plc_id: local_plc.clone(),
                    instance_id: s.instance.clone(),
                    plc_id: local_plc,
                    source_generation: generation,
                });
            s.save_sample_upload_settings(settings, expected)?;
            Ok(())
        })
        .unwrap();
    let cycle = crate::services::local_scheduler::collect(
        &v.draft,
        &v.draft.plcs[0],
        &v.draft.groups[0],
        &revision,
        &mut Synthetic,
        "fixture",
    )
    .unwrap();
    let counts = cycle
        .points
        .iter()
        .map(|(db, p)| {
            (
                *db,
                p.len(),
                p.values().filter(|v| v.quality != "good").count(),
            )
        })
        .collect::<Vec<_>>();
    assert_eq!(counts, [(501, 400, 0), (502, 512, 512)]);
    e.storage
        .call(false, move |s| s.commit_cycle(cycle).map(|_| ()))
        .unwrap();
    let bindings = e
        .storage
        .call(true, |s| s.sample_upload_bindings())
        .unwrap();
    for _ in 0..2 {
        let target = "http://127.0.0.1:38117/api/v1/integration/plc-facts/samples";
        let bindings = bindings.clone();
        e.storage.call(false, move |s| {
            let f = s.next_sample_upload(target, &bindings, false)?.ok_or("missing_sample")?;
            let body: serde_json::Value = serde_json::from_str(&f.body).map_err(|_| "body_invalid")?;
            assert_eq!(body["points"].as_array().unwrap().len(), if f.db_number == 501 {400} else {512});
            let attempt = s.mark_sample_upload_attempt(&f)?;
            let response = crate::infrastructure::facts_http::Response { status:200, media_type:"application/json".into(), retry_after:None, body:json!({"code":200,"message":"success","data":{"contractVersion":"plc-facts/v2","instanceId":f.instance_id,"sampleId":f.sample_id,"status":"committed","outcome":"created"}}).to_string().into_bytes() };
            assert_eq!(s.record_sample_upload_response(&f, Ok(response), attempt)?.0, Reply::Committed);
            Ok(())
        }).unwrap();
    }
    e.shutdown();
    drop(e);
    let reopened = engine(&profile);
    let view = reopened.configuration().unwrap();
    assert_eq!(view.draft.points.len(), 912);
    assert_eq!(view.active.as_deref(), Some(revision.as_str()));
    assert!(view.issues.is_empty());
    assert_eq!(reopened.delivery_snapshot().unwrap()["acknowledged"], 2);
    reopened.shutdown();
    drop(reopened);
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn per_plc_identity_preserves_legacy_and_refuses_old_ipc_and_old_admission() {
    use crate::domain::sample_upload::Settings;
    let profile = sealed_v4_fixture();
    seed_v4_fixture(&profile, 1);
    let dir = profile.join("local-acquisition-v1");
    let mut s = super::Stores::open(&dir).unwrap();
    let old = s.sample_upload_settings().unwrap();
    assert_eq!(old.bindings.len(), 2);
    assert_eq!(old.bindings[0].instance_id, old.bindings[1].instance_id);
    let first_local = old.bindings[0].local_plc_id.clone();
    let inactive_local = old.bindings[1].local_plc_id.clone();
    let active_revision = s.configuration().unwrap().active.unwrap();
    let mut active = s.revision(&active_revision).unwrap();
    active.plcs.retain(|p| p.id != inactive_local);
    active.groups.retain(|g| g.plc_id != inactive_local);
    active.dbs.retain(|db| db.plc_id != inactive_local);
    active.points.retain(|point| point.plc_id != inactive_local);
    active
        .sources
        .retain(|source| source.plc_id != inactive_local);
    super::tests::activated(&mut s, &active);
    assert!(s
        .reporting_local_sources()
        .unwrap()
        .iter()
        .all(|row| row["localPlcId"] != inactive_local));
    assert_eq!(s.sample_upload_settings().unwrap().bindings, old.bindings);
    let captured = s.reporting_identity(&first_local).unwrap().unwrap();
    let pre_sources = s.sample_upload_bindings().unwrap();
    let target = "http://127.0.0.1:38117/api/v1/integration/plc-facts/samples";
    let frozen = s
        .next_sample_upload(target, &pre_sources, false)
        .unwrap()
        .unwrap();
    let attempt = s.mark_sample_upload_attempt(&frozen).unwrap();
    s.record_sample_upload_response(&frozen, Err("synthetic_offline".into()), attempt)
        .unwrap();
    let before: (String, String, String, String, u32) = s.runtime.query_row(
        "SELECT instance_id,origin,body,body_sha,attempt FROM sample_uploads WHERE sample_id=?1",
        [&frozen.sample_id], |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?,r.get(4)?))).unwrap();
    let mut mixed = old.clone();
    mixed.bindings[0].instance_id = "new-instance-A".into();
    mixed.bindings[0].source_generation = "new-generation-A".into();
    mixed.bindings[1].instance_id = "new-instance-B".into();
    mixed.bindings[1].source_generation = "new-generation-B".into();
    let saved = s
        .save_sample_upload_settings(mixed, old.settings_revision.clone())
        .unwrap();
    assert_eq!(s.sample_upload_settings().unwrap().bindings, saved.bindings);
    let sentinel: Option<String> = s
        .runtime
        .query_row(
            "SELECT instance_id FROM reporting_identity WHERE id=1",
            [],
            |r| r.get(0),
        )
        .unwrap();
    assert!(sentinel.is_none());
    // Equivalent pre-r1 full_check: old shared instance must exist and match each generation.
    let old_would_refuse: bool = s.runtime.query_row("SELECT EXISTS(SELECT 1 FROM reporting_bindings b LEFT JOIN reporting_identity i ON i.id=1 LEFT JOIN reporting_generations g ON g.plc_id=b.plc_id AND g.source_generation=b.source_generation AND g.local_plc_id=b.local_plc_id AND g.instance_id=i.instance_id WHERE i.instance_id IS NULL OR g.plc_id IS NULL)", [], |r| r.get(0)).unwrap();
    assert!(old_would_refuse);
    let after: (String, String, String, String, u32) = s.runtime.query_row(
        "SELECT instance_id,origin,body,body_sha,attempt FROM sample_uploads WHERE sample_id=?1",
        [&frozen.sample_id], |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?,r.get(4)?))).unwrap();
    assert_eq!(before, after);
    let current = s.reporting_identity(&first_local).unwrap().unwrap();
    assert_ne!(captured.instance_id, current.instance_id);
    let before_conflict = s.sample_upload_settings().unwrap();
    let mut bad = before_conflict.clone();
    bad.bindings[0].instance_id = "another-instance".into();
    assert_eq!(
        s.save_sample_upload_settings(bad, before_conflict.settings_revision.clone())
            .unwrap_err(),
        "source_generation_reuse"
    );
    assert_eq!(
        s.sample_upload_settings().unwrap().bindings,
        before_conflict.bindings
    );
    assert_eq!(
        s.save_sample_upload_settings(before_conflict.clone(), old.settings_revision)
            .unwrap_err(),
        "delivery_settings_conflict"
    );
    let mut duplicate = before_conflict.clone();
    duplicate.bindings[1].plc_id = duplicate.bindings[0].plc_id.clone();
    assert_eq!(
        s.save_sample_upload_settings(duplicate, before_conflict.settings_revision.clone())
            .unwrap_err(),
        "invalid_settings"
    );
    let mut same = before_conflict.clone();
    for (idx, binding) in same.bindings.iter_mut().enumerate() {
        binding.instance_id = "shared".into();
        binding.source_generation = "same-gen".into();
        binding.plc_id = format!("distinct-{idx}");
    }
    let same = s
        .save_sample_upload_settings(same, before_conflict.settings_revision)
        .unwrap();
    assert_eq!(s.sample_upload_settings().unwrap().bindings, same.bindings);
    assert_eq!(
        s.runtime
            .query_row::<String, _, _>(
                "SELECT instance_id FROM reporting_identity WHERE id=1",
                [],
                |r| r.get(0)
            )
            .unwrap(),
        "shared"
    );
    let mut mixed_again = same.clone();
    mixed_again.bindings[0].instance_id = "mixed-again".into();
    mixed_again.bindings[0].source_generation = "mixed-new".into();
    let mixed_again = s
        .save_sample_upload_settings(mixed_again, same.settings_revision)
        .unwrap();
    let encoded = serde_json::to_value(&mixed_again).unwrap();
    let mut old_request = encoded.clone();
    old_request.as_object_mut().unwrap().remove("identityMode");
    old_request["instanceId"] = serde_json::json!("shared");
    for b in old_request["bindings"].as_array_mut().unwrap() {
        b.as_object_mut().unwrap().remove("instanceId");
    }
    assert!(serde_json::from_value::<Settings>(old_request).is_err());
    // Captured from the actual baseline SFC save path: it spreads the new marker,
    // adds its old global instanceId, and reconstructs rows without per-row instanceId.
    let old_sfc = serde_json::json!({"schemaVersion":1,"settingsRevision":"r","origin":null,"path":"/samples","intervalSeconds":5,"identityMode":"per_plc","bindings":[{"localPlcId":"local-a","plcId":"PLC-A","sourceGeneration":"replacement-0"},{"localPlcId":"local-b","plcId":"PLC-B","sourceGeneration":"replacement-1"}],"instanceId":"old-editor-instance"});
    let old_sfc_empty = serde_json::json!({"schemaVersion":1,"settingsRevision":"r","origin":null,"path":"/samples","intervalSeconds":5,"identityMode":"per_plc","bindings":[],"instanceId":null});
    assert!(serde_json::from_value::<Settings>(old_sfc.clone()).is_err());
    assert!(serde_json::from_value::<Settings>(old_sfc_empty).is_err());
    let mut no_global = old_sfc;
    no_global.as_object_mut().unwrap().remove("instanceId");
    assert!(serde_json::from_value::<Settings>(no_global).is_err());
    #[derive(serde::Deserialize)]
    #[allow(dead_code)]
    #[serde(rename_all = "camelCase", deny_unknown_fields)]
    struct OldSettings {
        schema_version: u32,
        settings_revision: String,
        origin: Option<String>,
        path: String,
        interval_seconds: u32,
        instance_id: Option<String>,
        bindings: Vec<OldBinding>,
    }
    #[derive(serde::Deserialize)]
    #[allow(dead_code)]
    #[serde(rename_all = "camelCase", deny_unknown_fields)]
    struct OldBinding {
        local_plc_id: String,
        plc_id: String,
        source_generation: String,
    }
    assert!(serde_json::from_value::<OldSettings>(encoded).is_err());
    s.clean_exit().unwrap();
    drop(s);
    let mut reopened = super::Stores::open(&dir).unwrap();
    assert_eq!(
        reopened.sample_upload_settings().unwrap().bindings,
        mixed_again.bindings
    );
    let persisted: (String,String,String,String,u32) = reopened.runtime.query_row("SELECT instance_id,origin,body,body_sha,attempt FROM sample_uploads WHERE sample_id=?1", [&frozen.sample_id], |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?,r.get(4)?))).unwrap();
    assert_eq!(before, persisted);
    let sources = reopened.sample_upload_bindings().unwrap();
    assert!(sources.iter().any(|b| b.instance_id == frozen.instance_id
        && b.plc_id == frozen.plc_id
        && b.source_generation == frozen.source_generation));
    assert_eq!(
        reopened
            .next_sample_upload(target, &sources, false)
            .unwrap()
            .unwrap()
            .body,
        frozen.body
    );
    reopened.clean_exit().unwrap();
    drop(reopened);
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn runtime2_and_3_keep_local_collection_and_refuse_v2_delivery() {
    use crate::{config::local_bootstrap::Bootstrap, services::local_supervisor::LocalEngine};
    for version in [2, 3] {
        let profile = if version == 3 {
            sealed_fixture(3)
        } else {
            // runtime2 is an admitted unsealed predecessor, never a sealed profile.
            use super::schema;
            use crate::domain::{
                local_configuration::{id, Configuration},
                local_sample::encode,
            };
            let profile = synthetic_temp_root().join(format!("daa013-v2-{}", id()));
            std::fs::create_dir(&profile).unwrap();
            let lock =
                crate::infrastructure::local_profile_lock::ProfileLock::acquire(&profile).unwrap();
            let dir = profile.join("local-acquisition-v1");
            std::fs::create_dir(&dir).unwrap();
            let instance = id();
            for role in ["config", "runtime"] {
                let path = dir.join(format!("{role}.sqlite"));
                std::fs::File::create(&path).unwrap();
                let app = if role == "config" {
                    schema::CONFIG_APP
                } else {
                    schema::RUNTIME_APP
                };
                let db = super::connect(&path, true, app).unwrap();
                if role == "config" {
                    db.execute_batch(&schema::config_sql()).unwrap();
                    db.execute("INSERT INTO instance_metadata VALUES(1,?1,2,'asia-shanghai-rfc3339-ms-v1')", [&instance]).unwrap();
                    db.execute(
                        "INSERT INTO configuration_draft VALUES(1,?1,?2,'[]')",
                        rusqlite::params![id(), encode(&Configuration::default()).unwrap()],
                    )
                    .unwrap();
                } else {
                    db.execute_batch(&schema::runtime_sql()).unwrap();
                    db.execute("INSERT INTO runtime_metadata VALUES(1,?1,2,1,NULL,'asia-shanghai-rfc3339-ms-v1')", [&instance]).unwrap();
                }
                db.execute_batch(&format!(
                    "PRAGMA application_id={app}; PRAGMA user_version=2;"
                ))
                .unwrap();
                db.close().unwrap();
            }
            drop(lock);
            profile
        };
        let dir = profile.join("local-acquisition-v1");
        let mut store = super::Stores::open(&dir).unwrap();
        let startup = crate::domain::local_runtime::StartupSettings {
            schema_version: 1,
            auto_collect: true,
            auto_report: false,
        };
        assert_eq!(
            store.startup_settings().unwrap(),
            crate::domain::local_runtime::StartupSettings::default()
        );
        store.save_startup_settings(startup.clone()).unwrap();
        assert_eq!(
            store
                .save_startup_settings(crate::domain::local_runtime::StartupSettings {
                    auto_report: true,
                    ..startup.clone()
                })
                .unwrap_err(),
            "delivery_profile_upgrade_required"
        );
        let config = super::tests::configuration();
        let revision = super::tests::activated(&mut store, &config);
        assert!(store
            .reporting_identity(&config.plcs[0].id)
            .unwrap()
            .is_none());
        let cycle = store
            .commit_cycle(super::tests::cycle(&config, &revision))
            .unwrap();
        let count: u32 = store
            .runtime
            .query_row(
                "SELECT count(*) FROM samples WHERE cycle_id=?1",
                [cycle["cycleId"].as_str().unwrap()],
                |row| row.get(0),
            )
            .unwrap();
        assert_eq!(count, 2);
        store.clean_exit().unwrap();
        drop(store);
        let boot = Bootstrap {
            mode: "local_sqlite".into(),
            profile: profile.clone(),
            read_allowed: false,
            validation: false,
            migration: None,
            ignored_keys: vec![],
            fixture: None,
        };
        let engine = LocalEngine::open(boot).unwrap();
        assert_eq!(
            engine.startup_settings().unwrap()["settings"]["autoCollect"],
            true
        );
        assert!(!engine.delivery_available().unwrap());
        assert_eq!(
            engine
                .set_delivery("start", Some("revision".into()), Some(vec![]))
                .unwrap_err(),
            "delivery_profile_upgrade_required"
        );
        let current: u32 = engine
            .storage
            .call(true, |s| {
                s.runtime
                    .query_row("PRAGMA user_version", [], |r| r.get(0))
                    .map_err(super::sql_error)
            })
            .unwrap();
        assert_eq!(current, version);
        engine.shutdown();
        drop(engine);
        std::fs::remove_dir_all(profile).unwrap();
    }
}

#[cfg(unix)]
#[test]
fn mixed_bindings_preserve_all_existing_sample_and_receipt_states() {
    let profile = sealed_v4_fixture();
    seed_v4_fixture(&profile, 4);
    let dir = profile.join("local-acquisition-v1");
    let mut store = super::Stores::open(&dir).unwrap();
    let cycles: Vec<String> = store
        .runtime
        .prepare("SELECT id FROM collection_cycles ORDER BY rowid")
        .unwrap()
        .query_map([], |r| r.get(0))
        .unwrap()
        .collect::<Result<_, _>>()
        .unwrap();
    assert_eq!(cycles.len(), 4);
    // Synthetic predecessor without a marker and a later explicitly local-only cycle.
    store
        .runtime
        .execute(
            "DELETE FROM reporting_cycles WHERE cycle_id=?1",
            [&cycles[0]],
        )
        .unwrap();
    store.runtime.execute("UPDATE reporting_cycles SET instance_id=NULL,plc_id=NULL,source_generation=NULL WHERE cycle_id=?1", [&cycles[1]]).unwrap();
    let sources = store.sample_upload_bindings().unwrap();
    let target = "http://127.0.0.1:38117/api/v1/integration/plc-facts/samples";
    let prepared = store
        .next_sample_upload(target, &sources, false)
        .unwrap()
        .unwrap();
    let unknown = store
        .next_sample_upload_ready(target, &sources, false, &[prepared.sample_id.clone()])
        .unwrap()
        .unwrap();
    let attempt = store.mark_sample_upload_attempt(&unknown).unwrap();
    store
        .record_sample_upload_response(&unknown, Err("synthetic_lost".into()), attempt)
        .unwrap();
    let acknowledged = store
        .next_sample_upload_ready(
            target,
            &sources,
            false,
            &[prepared.sample_id.clone(), unknown.sample_id.clone()],
        )
        .unwrap()
        .unwrap();
    let attempt = store.mark_sample_upload_attempt(&acknowledged).unwrap();
    let receipt = json!({"code":200,"message":"success","data":{"contractVersion":"plc-facts/v2","instanceId":acknowledged.instance_id,"sampleId":acknowledged.sample_id,"status":"committed","outcome":"created"}}).to_string();
    let response = crate::infrastructure::facts_http::Response {
        status: 200,
        media_type: "application/json".into(),
        retry_after: None,
        body: receipt.into_bytes(),
    };
    assert_eq!(
        store
            .record_sample_upload_response(&acknowledged, Ok(response), attempt)
            .unwrap()
            .0,
        Reply::Committed
    );
    let snapshot = |s: &super::Stores| -> Vec<Vec<String>> {
        [
            "SELECT json_object('id',s.id,'cycle',s.cycle_id,'seq',s.source_seq,'payload',s.payload,'sha',s.sha256,'started',c.started_at,'manifest',c.manifest,'manifestSha',c.sha256,'context',x.payload,'contextSha',x.sha256,'reportInstance',r.instance_id,'reportPlc',r.plc_id,'reportGeneration',r.source_generation,'marker',r.cycle_id) FROM samples s JOIN collection_cycles c ON c.id=s.cycle_id JOIN configuration_contexts x ON x.revision=s.revision LEFT JOIN reporting_cycles r ON r.cycle_id=s.cycle_id ORDER BY s.sample_order",
            "SELECT json_object('id',sample_id,'instance',instance_id,'plc',plc_id,'db',db_number,'generation',source_generation,'origin',origin,'body',body,'sha',body_sha,'state',state,'attempt',attempt,'next',next_attempt_at,'dispatched',dispatched_at,'acknowledged',acknowledged_at,'receipt',receipt,'receiptSha',receipt_sha) FROM sample_uploads ORDER BY sample_id",
            "SELECT json_object('sample',sample_id,'attempt',attempt,'target',target_url,'started',started_at) FROM sample_upload_attempts ORDER BY sample_id,attempt",
        ].iter().map(|sql| s.runtime.prepare(sql).unwrap().query_map([], |r| r.get::<_,String>(0)).unwrap().collect::<Result<Vec<_>,_>>().unwrap()).collect()
    };
    let before = snapshot(&store);
    assert_eq!(before[0].len(), 8);
    assert_eq!(before[1].len(), 3);
    let settings = store.sample_upload_settings().unwrap();
    let mut mixed = settings.clone();
    for (i, binding) in mixed.bindings.iter_mut().enumerate() {
        binding.instance_id = format!("mixed-{i}");
        binding.source_generation = format!("new-generation-{i}");
    }
    store
        .save_sample_upload_settings(mixed, settings.settings_revision)
        .unwrap();
    assert_eq!(before, snapshot(&store));
    let eligible: u64 = store.sample_upload_snapshot(false).unwrap()["pending"]
        .as_u64()
        .unwrap();
    assert_eq!(eligible, 5); // six eligible samples minus the one acknowledged
    store.clean_exit().unwrap();
    drop(store);
    let mut reopened = super::Stores::open(&dir).unwrap();
    assert_eq!(before, snapshot(&reopened));
    let still_unknown = reopened.get_sample_upload(&unknown.sample_id).unwrap();
    assert_eq!(still_unknown["state"], "unknown");
    assert_eq!(still_unknown["body"], unknown.body);
    assert_eq!(still_unknown["bodySha256"], unknown.body_sha);
    let still_acknowledged = reopened.get_sample_upload(&acknowledged.sample_id).unwrap();
    assert_eq!(still_acknowledged["state"], "acknowledged");
    assert!(still_acknowledged["receipt"].as_str().is_some());
    reopened.clean_exit().unwrap();
    drop(reopened);
    std::fs::remove_dir_all(profile).unwrap();
}

#[cfg(unix)]
#[test]
fn rebind_rechecks_complete_sources_after_late_historical_cycle() {
    let profile = sealed_v4_fixture();
    seed_v4_fixture(&profile, 0);
    let dir = profile.join("local-acquisition-v1");
    let mut store = super::Stores::open(&dir).unwrap();
    let (late_cycle, late_identity) = captured_v4_cycle_for(&store, 1).unwrap();
    add_v4_cycle_for(&mut store, 0).unwrap();
    let initial = store.sample_upload_settings().unwrap();
    let mut old = initial.clone();
    old.origin = Some("http://127.0.0.1:38117".into());
    let old = store
        .save_sample_upload_settings(old, initial.settings_revision)
        .unwrap();
    let old_url = old.target().unwrap().unwrap();
    let frozen = store
        .next_sample_upload(&old_url, &store.sample_upload_bindings().unwrap(), false)
        .unwrap()
        .unwrap();
    let attempt = store.mark_sample_upload_attempt(&frozen).unwrap();
    store
        .record_sample_upload_response(&frozen, Err("synthetic_lost".into()), attempt)
        .unwrap();
    let mut new = old.clone();
    new.origin = Some("http://127.0.0.1:38118".into());
    for (i, binding) in new.bindings.iter_mut().enumerate() {
        binding.instance_id = format!("new-instance-{i}");
        binding.source_generation = format!("new-generation-{i}");
    }
    let new = store
        .save_sample_upload_settings(new, old.settings_revision)
        .unwrap();
    let new_url = new.target().unwrap().unwrap();
    let confirmed = store.sample_upload_bindings().unwrap();
    assert!(confirmed.iter().any(|b| b.instance_id == frozen.instance_id
        && b.plc_id == frozen.plc_id
        && b.source_generation == frozen.source_generation));
    // An already-started B cycle becomes pending after the service's earlier source read.
    store
        .commit_cycle_with_reporting(late_cycle, late_identity.clone())
        .unwrap();
    let current = store.sample_upload_bindings().unwrap();
    assert!(current
        .iter()
        .any(|b| !confirmed.contains(b) && b.plc_id == late_identity.as_ref().unwrap().plc_id));
    assert_eq!(
        store
            .rebind_sample_upload(
                &frozen.sample_id,
                &old_url,
                &new_url,
                &new.settings_revision,
                &confirmed
            )
            .unwrap_err(),
        "source_confirmation_changed"
    );
    let unchanged = store.get_sample_upload(&frozen.sample_id).unwrap();
    assert_eq!(unchanged["state"], "unknown");
    assert_eq!(unchanged["origin"], old_url);
    assert_eq!(unchanged["body"], frozen.body);
    assert_eq!(unchanged["bodySha256"], frozen.body_sha);
    assert_eq!(unchanged["rebindings"].as_array().unwrap().len(), 0);
    store
        .rebind_sample_upload(
            &frozen.sample_id,
            &old_url,
            &new_url,
            &new.settings_revision,
            &current,
        )
        .unwrap();
    let rebound = store.get_sample_upload(&frozen.sample_id).unwrap();
    assert_eq!(rebound["origin"], new_url);
    assert_eq!(rebound["body"], frozen.body);
    assert_eq!(rebound["bodySha256"], frozen.body_sha);
    assert_eq!(rebound["rebindings"].as_array().unwrap().len(), 1);
    store.clean_exit().unwrap();
    drop(store);
    std::fs::remove_dir_all(profile).unwrap();
}
