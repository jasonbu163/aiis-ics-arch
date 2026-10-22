//! DS专有库实证：新库身份、CAS/不可变来源/selected重开与未知原件保护。
use ds_runtime::{
    domain::{
        configuration::{self, InstanceConfig, Workspace},
        source::SourceVersion,
    },
    infrastructure::config_store::Store,
};
use std::{fs, path::PathBuf};
fn profile(case: &str) -> PathBuf {
    let root = std::env::var_os("DS_TEST_RUN_ROOT").expect("explicit owned DS_TEST_RUN_ROOT");
    let path = PathBuf::from(root).join(format!("store-{case}-{}", configuration::uuid()));
    fs::create_dir_all(&path).unwrap();
    path
}
fn instance() -> InstanceConfig {
    serde_json::from_value(
        serde_json::json!({"id":configuration::uuid(),"name":"Synthetic","port":30102}),
    )
    .unwrap()
}
#[test]
fn real_cas_sources_selection_and_reopen() {
    let p = profile("cas");
    let store = Store::open(&p).unwrap();
    assert!(matches!(Store::open(&p),Err(e) if e=="profile_in_use"));
    let initial = store.load().unwrap();
    assert_eq!(initial.workspace, Workspace::default());
    assert!(initial.latest_revision.is_none());
    let unchanged = store
        .save(&initial.etag, initial.workspace.clone())
        .unwrap();
    assert_eq!(unchanged.result, "unchanged");
    assert_eq!(unchanged.etag, initial.etag);
    let raw = b"\xEF\xBB\xBF// synthetic CRLF\r\n".to_vec();
    let source = SourceVersion {
        version_id: configuration::uuid(),
        lineage_id: configuration::uuid(),
        blob_sha256: configuration::hash_bytes(&raw),
        logical_name: "synthetic.db".into(),
        import_profile: "tia-v1".into(),
        bytes: raw.clone(),
    };
    let mut workspace = initial.workspace;
    workspace.instances.push(instance());
    workspace.source_versions.push(source.clone());
    let saved = store.save(&initial.etag, workspace.clone()).unwrap();
    assert_eq!(saved.result, "saved");
    assert_ne!(saved.etag, initial.etag);
    assert!(store
        .save(&initial.etag, workspace.clone())
        .unwrap_err()
        .starts_with("etag_conflict:"));
    let revision = saved.revision_id.unwrap();
    assert_eq!(store.revision(&revision).unwrap(), workspace);
    let selection = store
        .select(&workspace.instances[0].id, &revision, None)
        .unwrap();
    assert_eq!(
        selection.slice_sha256,
        configuration::digest(&workspace.instances[0])
    );
    assert_eq!(
        store
            .select(&workspace.instances[0].id, &revision, None)
            .unwrap_err(),
        "selection_conflict"
    );
    let mut modified = workspace.clone();
    modified.source_versions[0].logical_name = "changed.db".into();
    assert_eq!(
        store.save(&saved.etag, modified).unwrap_err(),
        "source_immutable"
    );
    assert_eq!(store.load().unwrap().etag, saved.etag);
    store.shutdown().unwrap();
    let c = rusqlite::Connection::open(p.join("device-simulator-v1/config.sqlite")).unwrap();
    assert_eq!(
        c.pragma_query_value(None, "application_id", |r| r.get::<_, i64>(0))
            .unwrap(),
        0x44535631
    );
    assert_eq!(
        c.pragma_query_value(None, "user_version", |r| r.get::<_, i64>(0))
            .unwrap(),
        1
    );
    assert_eq!(
        c.query_row("SELECT utf8 FROM source_blobs", [], |r| r
            .get::<_, Vec<u8>>(0))
            .unwrap(),
        raw
    );
    assert_eq!(
        c.query_row("SELECT count(*) FROM configuration_revisions", [], |r| r
            .get::<_, i64>(0))
            .unwrap(),
        1
    );
    drop(c);
    let reopened = Store::open(&p).unwrap();
    assert_eq!(reopened.load().unwrap().workspace, workspace);
    assert_eq!(
        reopened.selections().unwrap()[0].selection_etag,
        selection.selection_etag
    );
    reopened.shutdown().unwrap();
}
#[test]
fn reject_unknown_corrupt_wal_symlink_and_duplicate_identity_without_replacing_original() {
    for (kind, bytes) in [
        ("corrupt", b"NOT A DATABASE".as_slice()),
        ("empty", b"".as_slice()),
    ] {
        let p = profile(kind);
        fs::create_dir(p.join("device-simulator-v1")).unwrap();
        let db = p.join("device-simulator-v1/config.sqlite");
        fs::write(&db, bytes).unwrap();
        assert!(Store::open(&p).is_err());
        assert_eq!(fs::read(&db).unwrap(), bytes);
    }
    let p = profile("unknown");
    fs::create_dir(p.join("device-simulator-v1")).unwrap();
    let db = p.join("device-simulator-v1/config.sqlite");
    let c = rusqlite::Connection::open(&db).unwrap();
    c.execute_batch(
        "CREATE TABLE foreign_data(value TEXT); INSERT INTO foreign_data VALUES('keep');",
    )
    .unwrap();
    drop(c);
    let before = fs::read(&db).unwrap();
    assert!(matches!(Store::open(&p),Err(e) if e=="storage_identity"));
    assert_eq!(fs::read(&db).unwrap(), before);
    let p = profile("wal");
    let store = Store::open(&p).unwrap();
    store.shutdown().unwrap();
    fs::write(p.join("device-simulator-v1/config.sqlite-wal"), b"keep").unwrap();
    assert!(matches!(Store::open(&p),Err(e) if e=="storage_unexpected_wal"));
    let p = profile("symlink");
    let target = p.join("target");
    fs::create_dir(&target).unwrap();
    std::os::unix::fs::symlink(&target, p.join("device-simulator-v1")).unwrap();
    assert!(matches!(Store::open(&p),Err(e) if e=="profile_symlink"));
    let p = profile("invalid-save");
    let store = Store::open(&p).unwrap();
    let state = store.load().unwrap();
    let mut w = state.workspace;
    let instance = instance();
    w.instances = vec![instance.clone(), instance];
    assert_eq!(
        store.save(&state.etag, w).unwrap_err(),
        "configuration_identity"
    );
    assert_eq!(store.load().unwrap().etag, state.etag);
    store.shutdown().unwrap();
}

#[test]
fn concurrent_cas_real_rollback_committed_reply_loss_and_preserved_readonly_database() {
    use std::sync::{Arc, Barrier};
    let root = profile("transaction-faults");
    let store = Arc::new(Store::open(&root).unwrap());
    let state = store.load().unwrap();
    let barrier = Arc::new(Barrier::new(3));
    let mut threads = vec![];
    for name in ["First", "Second"] {
        let (store, barrier, state) = (store.clone(), barrier.clone(), state.clone());
        threads.push(std::thread::spawn(move || {
            let mut w = state.workspace;
            let mut i = instance();
            i.name = name.into();
            w.instances.push(i);
            barrier.wait();
            store.save(&state.etag, w)
        }));
    }
    barrier.wait();
    let results = threads
        .into_iter()
        .map(|t| t.join().unwrap())
        .collect::<Vec<_>>();
    assert_eq!(results.iter().filter(|r| r.is_ok()).count(), 1);
    assert_eq!(
        results
            .iter()
            .filter(|r| matches!(r, Err(e) if e.starts_with("etag_conflict:")))
            .count(),
        1
    );
    let state = store.load().unwrap();
    let original = fs::read(&store.path).unwrap();
    let mut changed = state.workspace.clone();
    changed.instances[0].name = "Rolled back".into();
    store.test_fault("insufficient_space").unwrap();
    assert_eq!(
        store.save(&state.etag, changed.clone()).unwrap_err(),
        "storage_free_space"
    );
    assert_eq!(store.load().unwrap().workspace, state.workspace);
    assert_eq!(fs::read(&store.path).unwrap(), original);
    store.test_fault("before_save_commit").unwrap();
    assert_eq!(
        store.save(&state.etag, changed.clone()).unwrap_err(),
        "test_fault"
    );
    assert_eq!(store.load().unwrap().workspace, state.workspace);
    assert_eq!(fs::read(&store.path).unwrap(), original);
    store.test_fault("after_save_commit").unwrap();
    assert_eq!(
        store.save(&state.etag, changed.clone()).unwrap_err(),
        "save_receipt_unknown"
    );
    // No retry: query the actual immutable revision and draft after the lost receipt.
    let committed = store.load().unwrap();
    assert_ne!(committed.etag, state.etag);
    assert_eq!(committed.workspace, changed);
    assert_eq!(store.revisions(0).unwrap().len(), 2);
    let id = &committed.workspace.instances[0].id;
    let revision = committed.latest_revision.as_ref().unwrap();
    store.test_fault("before_select_commit").unwrap();
    assert_eq!(store.select(id, revision, None).unwrap_err(), "test_fault");
    assert!(store.selections().unwrap().is_empty());
    store.test_fault("after_select_commit").unwrap();
    assert_eq!(
        store.select(id, revision, None).unwrap_err(),
        "selection_receipt_unknown"
    );
    assert_eq!(store.selections().unwrap()[0].revision_id, *revision);
    store.shutdown().unwrap();
    let path = store.path.clone();
    drop(store);
    let original = fs::read(&path).unwrap();
    use std::os::unix::fs::PermissionsExt;
    fs::set_permissions(&path, fs::Permissions::from_mode(0o400)).unwrap();
    assert!(Store::open(&root).is_err());
    assert_eq!(fs::read(&path).unwrap(), original);
    fs::set_permissions(&path, fs::Permissions::from_mode(0o600)).unwrap();
}

#[test]
fn unknown_version_schema_hash_and_owned_capacity_rejection_preserve_originals() {
    for (kind, sql) in [
        ("version", "PRAGMA user_version=2"),
        ("identity", "PRAGMA application_id=1234"),
        (
            "schema",
            "UPDATE schema_migrations SET migration_sha256='invalid'",
        ),
    ] {
        let root = profile(kind);
        let store = Store::open(&root).unwrap();
        let path = store.path.clone();
        store.shutdown().unwrap();
        let c = rusqlite::Connection::open(&path).unwrap();
        c.execute_batch(sql).unwrap();
        drop(c);
        let before = fs::read(&path).unwrap();
        assert!(Store::open(&root).is_err());
        assert_eq!(fs::read(&path).unwrap(), before);
    }
    let root = profile("capacity");
    let store = Store::open(&root).unwrap();
    let path = store.path.clone();
    store.shutdown().unwrap();
    drop(store);
    // Sparse owned file exercises the actual main+journal+pending size admission without filling a host volume.
    let file = fs::OpenOptions::new().write(true).open(&path).unwrap();
    file.set_len(65 * 1024 * 1024).unwrap();
    drop(file);
    let lock = ds_runtime::infrastructure::profile_lock::ProfileLock::acquire(&root).unwrap();
    assert_eq!(lock.check_capacity(0).unwrap_err(), "storage_capacity");
    assert_eq!(fs::metadata(&path).unwrap().len(), 65 * 1024 * 1024);
}
