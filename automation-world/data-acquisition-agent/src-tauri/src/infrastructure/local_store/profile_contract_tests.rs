//! DAA-008 r2纯格式/指纹与新目录A1：产品工厂/真实锁/真实进程退出，无env或网络。
use super::profile_contract::*;
use super::*;
use serde_json::json;
thread_local! {static FAILURE:std::cell::RefCell<Option<(String,usize,usize)>>=const{std::cell::RefCell::new(None)};}
thread_local! {static INSTALL_CONFLICT:std::cell::Cell<bool>=const{std::cell::Cell::new(false)};}
thread_local! {static DRIFT:std::cell::RefCell<Option<String>>=const{std::cell::RefCell::new(None)};static FREE_BYTES:std::cell::Cell<Option<u64>>=const{std::cell::Cell::new(None)};}
pub(super) fn available_space(real: u64) -> u64 {
    FREE_BYTES.with(|v| v.get().unwrap_or(real))
}
thread_local! {static REWORK_MUTATION:std::cell::RefCell<Option<(String,String)>>=const{std::cell::RefCell::new(None)};}
pub(super) fn checkpoint(stage: &str, dir: &Path) -> LocalResult<()> {
    let action = REWORK_MUTATION.with(|v| {
        let mut v = v.borrow_mut();
        if v.as_ref().map(|(s, _)| s.as_str()) == Some(stage) {
            v.take().map(|(_, a)| a)
        } else {
            None
        }
    });
    if let Some(action) = action {
        let before = capture(dir)?;
        match action.as_str() {
            "credential_remove" => std::fs::remove_file(dir.join(CREDENTIAL)).unwrap(),
            "credential_rewrite" => {
                use std::io::Write;
                std::fs::OpenOptions::new()
                    .append(true)
                    .open(dir.join(CREDENTIAL))
                    .unwrap()
                    .write_all(b" ")
                    .unwrap();
            }
            "credential_replace" => {
                let p = dir
                    .parent()
                    .unwrap()
                    .join("synthetic-credential-replacement");
                std::fs::copy(dir.join(CREDENTIAL), &p).unwrap();
                std::fs::rename(p, dir.join(CREDENTIAL)).unwrap();
            }
            "runtime_append" | "companion_append" => {
                use std::io::Write;
                std::fs::OpenOptions::new()
                    .append(true)
                    .open(dir.join(if action == "runtime_append" {
                        "runtime.sqlite"
                    } else {
                        "config.sqlite"
                    }))
                    .unwrap()
                    .write_all(b"synthetic stage drift")
                    .unwrap();
            }
            _ => panic!("unknown mutation"),
        }
        durable(
            &dir.parent().unwrap().join("rework-injection.json"),
            &json!({"stage":stage,"action":action,"before":snapshot_json(&before),"after":snapshot_json(&capture(dir)?)}),
        );
    }

    if DRIFT.with(|v| v.borrow().as_deref() == Some(stage)) {
        DRIFT.with(|v| *v.borrow_mut() = None);
        use std::io::Write;
        std::fs::OpenOptions::new()
            .append(true)
            .open(dir.join("runtime.sqlite"))
            .unwrap()
            .write_all(b"synthetic drift")
            .unwrap();
    }
    let fail = FAILURE.with(|f| {
        let mut f = f.borrow_mut();
        if let Some((key, n, seen)) = f.as_mut() {
            if key == stage {
                *seen += 1;
                return *seen == *n;
            }
        }
        false
    });
    if fail {
        return Err(format!("synthetic_profile_{stage}"));
    }
    if stage == "staging_durable" && INSTALL_CONFLICT.with(|v| v.replace(false)) {
        std::fs::write(dir.join(CREDENTIAL), b"synthetic competing credential").unwrap();
    }
    if ["before_native", "after_native", "after_ro"].contains(&stage)
        && dir.to_string_lossy().contains("daa-008-r2-a-")
    {
        let state = capture(dir)?;
        durable(
            &dir.parent().unwrap().join(format!("r2-stage-{stage}.json")),
            &snapshot_json(&state),
        );
    }
    if std::env::var("DAA_008_R2_CRASH_STAGE").ok().as_deref() == Some(stage) {
        assert!(
            dir.starts_with(std::env::temp_dir())
                && dir.to_string_lossy().contains("daa-008-r2-a-")
        );
        let path = dir.parent().unwrap().join("r2-crash-stage.txt");
        let file = std::fs::File::create(path).unwrap();
        use std::io::Write;
        (&file).write_all(stage.as_bytes()).unwrap();
        file.sync_all().unwrap();
        drop(file);
        unsafe { libc::_exit(86) }
    }
    Ok(())
}
#[test]
fn profile_contract_exact_sqlite_error_gate() {
    for code in [264, 8, 5, 10, 11, 776] {
        let error = rusqlite::Error::SqliteFailure(
            rusqlite::ffi::Error::new(code),
            Some("attempt to write a readonly database".into()),
        );
        assert_eq!(rollback_error(&error), code == 776);
    }
    assert!(!rollback_error(&rusqlite::Error::InvalidQuery));
}
#[test]
fn profile_contract_static_fingerprint_golden_bytes() {
    // 独立逐字节oracle：type/name/sql三个字段均以BE u32长度前缀。
    let sql="CREATE TABLE z(id INTEGER PRIMARY KEY); INSERT INTO z VALUES(1); CREATE UNIQUE INDEX a ON z(id);";
    let mut bytes = b"daa-ddl-sha256/v1\0".to_vec();
    for fields in [
        ["index", "a", "CREATE UNIQUE INDEX a ON z(id)"],
        ["table", "z", "CREATE TABLE z(id INTEGER PRIMARY KEY)"],
    ] {
        for field in fields {
            bytes.extend_from_slice(&(field.len() as u32).to_be_bytes());
            bytes.extend_from_slice(field.as_bytes());
        }
    }
    assert_eq!(
        schema::fingerprint(sql).unwrap(),
        crate::domain::facts_canonical::sha(&bytes)
    );
    assert_eq!(
        schema::fingerprint(sql).unwrap(),
        schema::fingerprint(&sql.replace("VALUES(1)", "VALUES(99)")).unwrap()
    );
    assert_ne!(
        schema::fingerprint(sql).unwrap(),
        schema::fingerprint(&sql.replace(" PRIMARY KEY", "")).unwrap()
    );
    // 公开DDL由独立stdlib逐记录编码所得固定golden，不以本实现生成唯一oracle。
    assert_eq!(
        schema::fingerprint(&schema::config_sql()).unwrap(),
        "sha256:64cc8187689bf3e04eb4b914811fe75e77a8d5dd6c0c895cfe12ed4814e1a806"
    );
    assert_eq!(
        schema::fingerprint(&schema::runtime_v3_sql()).unwrap(),
        "sha256:6657f7735d9932d561f0a1bc8ff836bf6190f678c5a6955520a665cab920ad4e"
    );
}
fn pure_contract() -> Contract {
    Contract {
        contract: "daa-profile-recovery/v1".into(),
        init_id: id(),
        instance_id: id(),
        created_at: crate::domain::business_time::now(),
        time_profile: crate::domain::business_time::TIME_PROFILE.into(),
        identity_profile: "unix-dev-ino/v1".into(),
        canonical_profile_dir: "/private/tmp/daa-008-r2-a-pure/profile".into(),
        canonical_store_dir: "/private/tmp/daa-008-r2-a-pure/profile/local-acquisition-v1".into(),
        profile_identity: Identity {
            dev: "1".into(),
            ino: "2".into(),
        },
        store_identity: Identity {
            dev: "1".into(),
            ino: "3".into(),
        },
        page_size: 4096,
        journal_mode: "delete".into(),
        stores: [
            ("config", schema::CONFIG_APP, 2, schema::config_sql()),
            ("runtime", schema::RUNTIME_APP, 3, schema::runtime_v3_sql()),
        ]
        .into_iter()
        .enumerate()
        .map(|(i, (role, app, version, ddl))| StoreContract {
            role: role.into(),
            file_name: format!("{role}.sqlite"),
            application_id: app,
            schema_version: version,
            schema_fingerprint: schema::fingerprint(&ddl).unwrap(),
            file_identity: Identity {
                dev: "1".into(),
                ino: (i + 4).to_string(),
            },
        })
        .collect(),
    }
}
#[test]
fn profile_contract_strict_original_utf8_and_fields() {
    let c = pure_contract();
    let profile = Path::new(&c.canonical_profile_dir);
    let store = Path::new(&c.canonical_store_dir);
    let raw = profile_contract::encode(&c).unwrap();
    assert_eq!(decode(&raw, profile, store).unwrap(), c);
    let wrap = |inner: String| {
        serde_json::to_vec(&json!({"formatVersion":1,"payloadSha256":crate::domain::facts_canonical::sha(inner.as_bytes()),"payloadUtf8":inner})).unwrap()
    };
    let pretty = serde_json::to_string_pretty(&c).unwrap();
    assert!(decode(&wrap(pretty), profile, store).is_ok());
    let mut bad: Value = serde_json::from_slice(&raw).unwrap();
    bad["payloadUtf8"] = json!(format!("{} ", bad["payloadUtf8"].as_str().unwrap()));
    assert!(decode(&serde_json::to_vec(&bad).unwrap(), profile, store).is_err());
    for (pointer, value) in [
        ("/contract", json!("other")),
        ("/initId", json!("not-uuid")),
        ("/createdAt", json!("2026-11-06T00:00:00Z")),
        ("/pageSize", json!(8192)),
        ("/profileIdentity/dev", json!("01")),
        ("/storeIdentity/ino", json!("0")),
        ("/stores/0/fileIdentity/ino", json!("5")),
        ("/stores/1/schemaVersion", json!(2)),
        ("/stores/0/schemaFingerprint", json!("sha256:wrong")),
        ("/canonicalStoreDir", json!("/private/tmp/../x")),
    ] {
        let mut inner = serde_json::to_value(&c).unwrap();
        *inner.pointer_mut(pointer).unwrap() = value;
        assert!(
            decode(&wrap(inner.to_string()), profile, store).is_err(),
            "{pointer}"
        );
    }
    let mut unknown = serde_json::to_value(&c).unwrap();
    unknown["unexpected"] = json!(true);
    assert!(decode(&wrap(unknown.to_string()), profile, store).is_err());
    let duplicate =
        String::from_utf8(raw.clone())
            .unwrap()
            .replacen('{', "{\"formatVersion\":1,", 1);
    assert!(decode(duplicate.as_bytes(), profile, store).is_err());
    for bad in [
        vec![b' '; 32769],
        [vec![239, 187, 191], raw.clone()].concat(),
        [raw.clone(), b"{}".to_vec()].concat(),
    ] {
        assert!(decode(&bad, profile, store).is_err());
    }
}
fn owned_profile() -> PathBuf {
    let root = std::env::temp_dir().canonicalize().unwrap();
    assert!(root.starts_with("/private/tmp") && root.to_string_lossy().contains("daa-008-r2-a-"));
    let profile = root.join(format!("profile-{}", id()));
    assert!(!profile.exists());
    std::fs::create_dir(&profile).unwrap();
    profile
}
#[test]
fn profile_contract_factory_initializes_and_cold_reopens() {
    let profile = owned_profile();
    let dir = profile.join("local-acquisition-v1");
    let mut s = Stores::open(&dir).unwrap();
    let credential = std::fs::read(dir.join(CREDENTIAL)).unwrap();
    let contract = decode(&credential, &profile, &dir).unwrap();
    assert_eq!(contract.instance_id, s.instance);
    assert!(!dir.join(SENTINEL).exists() && !dir.join(STAGING).exists());
    assert!(matches!(Stores::open(&dir),Err(e)if e=="profile_locked"));
    let capacity = s.capacity(1024 * 1024 * 1024).unwrap();
    let (logical, allocated) = capacity::auxiliary_bytes(&dir).unwrap();
    assert!(logical <= 32768 && allocated <= AUX_BUDGET);
    assert!(capacity.delivery_metadata_bytes >= logical);
    let mut file: *mut rusqlite::ffi::sqlite3_file = std::ptr::null_mut();
    unsafe {
        assert_eq!(
            rusqlite::ffi::sqlite3_file_control(
                s.runtime.handle(),
                b"main\0".as_ptr().cast(),
                rusqlite::ffi::SQLITE_FCNTL_FILE_POINTER,
                (&mut file as *mut *mut rusqlite::ffi::sqlite3_file).cast()
            ),
            0
        );
    }
    let sector = unsafe { ((*(*file).pMethods).xSectorSize.unwrap()(file) as u64).max(4096) };
    let old_pages = capacity.page_count * (4096 + 8 + sector) + sector;
    assert_eq!(
        capacity.main_bytes,
        std::fs::metadata(dir.join("runtime.sqlite")).unwrap().len() + allocated
    );
    assert_eq!(
        capacity.reserved_bytes + allocated,
        old_pages + 96 * 1024 * 1024
    );
    s.clean_exit().unwrap();
    let instance = s.instance.clone();
    drop(s);
    let reopened = Stores::open(&dir).unwrap();
    assert_eq!(reopened.instance, instance);
    assert_eq!(std::fs::read(dir.join(CREDENTIAL)).unwrap(), credential);
    assert_eq!(reopened.delivery_snapshot(false).unwrap()["running"], false);
    drop(reopened);
    let evidence = json!({"profile":profile,"instance":instance,"credentialSha256":crate::domain::facts_canonical::sha(&credential),"auxiliaryLogicalBytes":logical,"auxiliaryAllocatedBytes":allocated,"initializationSubBudgetBytes":AUX_BUDGET,"reserveBytes":capacity.reserved_bytes,"oldPageJournalBytes":old_pages,"sectorBytes":sector,"remainingAckRecoveryBytes":32*1024*1024-allocated,"actualAuxPlusRemainingAckBytes":32*1024*1024});
    std::fs::write(
        std::env::temp_dir().join("sealed-cold-evidence.json"),
        serde_json::to_vec_pretty(&evidence).unwrap(),
    )
    .unwrap();
}
#[test]
fn profile_contract_local_json_retains_original_local_limits() {
    let raw = format!("{}0{}", "[".repeat(35), "]".repeat(35));
    assert!(local_json(&raw, 4096).is_ok());
    assert!(crate::domain::facts_canonical::parse(raw.as_bytes(), 4096).is_err());
    assert!(local_json("1e10000", 4096).is_ok());
    assert!(local_json("{\"a\":1,\"a\":2}", 4096).is_err());
}
fn durable(path: &Path, value: &Value) {
    use std::io::Write;
    let mut file = std::fs::File::create(path).unwrap();
    file.write_all(&serde_json::to_vec_pretty(value).unwrap())
        .unwrap();
    file.sync_all().unwrap();
    drop(file);
    let dir = std::fs::File::open(path.parent().unwrap()).unwrap();
    dir.sync_all().unwrap();
}
fn snapshot_json(s: &Snapshot) -> Value {
    json!({"profileIdentity":s.profile_identity,"storeIdentity":s.store_identity,"files":s.files.iter().map(|m|json!({"name":m.name,"bytes":m.stat.len,"identity":m.stat.identity,"nlink":m.stat.links,"mode":m.stat.mode,"sha256":m.sha,"headerHex":m.header.iter().map(|b|format!("{b:02x}")).collect::<String>()})).collect::<Vec<_>>()})
}
fn ledger(s: &Stores) -> Value {
    let mut all = serde_json::Map::new();
    for (role, c, ddl) in [
        ("config", &s.config, schema::config_sql()),
        ("runtime", &s.runtime, schema::runtime_v3_sql()),
    ] {
        let mut tables = serde_json::Map::new();
        for (kind, name, _) in schema::ddl_records(&ddl).unwrap() {
            if kind != "table" {
                continue;
            }
            let mut q = c
                .prepare(&format!("SELECT * FROM {name} ORDER BY rowid"))
                .unwrap();
            let columns = q.column_count();
            let mut query = q.query([]).unwrap();
            let mut rows = vec![];
            while let Some(row) = query.next().unwrap() {
                let mut fields = vec![];
                for i in 0..columns {
                    fields.push(match row.get_ref(i).unwrap() {
                        rusqlite::types::ValueRef::Null => Value::Null,
                        rusqlite::types::ValueRef::Integer(n) => json!(n),
                        rusqlite::types::ValueRef::Text(_) => {
                            json!(row.get::<_, String>(i).unwrap())
                        }
                        _ => panic!("unexpected fixture type"),
                    });
                }
                rows.push(fields);
            }
            tables.insert(name, json!(rows));
        }
        all.insert(role.into(), Value::Object(tables));
    }
    Value::Object(all)
}
fn prepared_profile() -> PathBuf {
    let profile = owned_profile();
    let mut s = Stores::open(&profile.join("local-acquisition-v1")).unwrap();
    let c = super::tests::configuration();
    let revision = super::tests::activated(&mut s, &c);
    s.commit_cycle(super::tests::cycle(&c, &revision)).unwrap();
    let cid: String = s
        .runtime
        .query_row("SELECT id FROM collection_cycles", [], |r| r.get(0))
        .unwrap();
    let built = s.build_delivery_cycle(&cid).unwrap();
    super::delivery_tests::adopt(&mut s, &built);
    s.next_delivery().unwrap().unwrap();
    s.clean_exit().unwrap();
    drop(s);
    profile
}
fn ack(f: &delivery::Frozen) -> Value {
    let mut value = super::delivery_tests::receipt(f);
    for result in value["data"]["results"].as_array_mut().unwrap() {
        let part = f
            .batch
            .samples
            .iter()
            .find(|p| p.sample_id == result["sampleId"])
            .unwrap();
        let raw: Value = serde_json::from_str(&part.payload_utf8).unwrap();
        let first = raw["points"]
            .as_object()
            .unwrap()
            .values()
            .map(|p| crate::domain::facts_wire::time(p["observedAt"].as_str().unwrap()).unwrap())
            .min()
            .unwrap();
        result["expiresAt"] = json!(first
            .checked_add_months(chrono::Months::new(3))
            .unwrap()
            .to_rfc3339_opts(chrono::SecondsFormat::Nanos, false));
    }
    value
}
fn child(profile: &Path, mode: &str, stage: Option<&str>) -> std::process::Output {
    let mut cmd = std::process::Command::new(std::env::current_exe().unwrap());
    cmd.args([
        "--exact",
        "infrastructure::local_store::profile_contract_tests::profile_contract_child",
        "--nocapture",
    ])
    .env_clear()
    .env("TMPDIR", std::env::temp_dir())
    .env("DAA_008_R2_PROFILE", profile)
    .env("DAA_008_R2_CHILD", mode)
    .stdout(std::process::Stdio::piped())
    .stderr(std::process::Stdio::piped());
    if let Some(stage) = stage {
        cmd.env("DAA_008_R2_CRASH_STAGE", stage);
    }
    let argv = cmd
        .get_args()
        .map(|s| s.to_string_lossy().into_owned())
        .collect::<Vec<_>>();
    let executable = cmd.get_program().to_string_lossy().into_owned();
    let mut process = cmd.spawn().unwrap();
    let pid = process.id();
    let deadline = std::time::Instant::now() + std::time::Duration::from_secs(10);
    while process.try_wait().unwrap().is_none() {
        if std::time::Instant::now() > deadline {
            process.kill().unwrap();
            panic!("owned child timeout: {}", process.wait().unwrap());
        }
        std::thread::sleep(std::time::Duration::from_millis(10));
    }
    let output = process.wait_with_output().unwrap();
    durable(
        &profile.join(format!(
            "child-{mode}-{}-command.json",
            stage.unwrap_or("none")
        )),
        &json!({"executable":executable,"argv":argv,"envClear":true,"TMPDIR":std::env::temp_dir(),"profile":profile,"mode":mode,"stage":stage,"pid":pid,"exitCode":output.status.code(),"stdoutSha256":crate::domain::facts_canonical::sha(&output.stdout),"stderrSha256":crate::domain::facts_canonical::sha(&output.stderr)}),
    );
    std::fs::write(
        profile.join(format!("child-{mode}-{}.log", stage.unwrap_or("none"))),
        [&output.stdout[..], &output.stderr[..]].concat(),
    )
    .unwrap();
    output
}
#[test]
fn profile_contract_child() {
    let Ok(mode) = std::env::var("DAA_008_R2_CHILD") else {
        return;
    };
    let profile = PathBuf::from(std::env::var_os("DAA_008_R2_PROFILE").unwrap());
    assert!(profile.starts_with(std::env::temp_dir()));
    let dir = profile.join("local-acquisition-v1");
    if mode == "initialization_fault_suite" {
        initialization_fault_cases(&profile.join("initialization-faults.json"));
        return;
    }
    if mode == "hold_lock" {
        let _lock =
            crate::infrastructure::local_profile_lock::ProfileLock::acquire(&profile).unwrap();
        durable(
            &profile.join("lock-ready.json"),
            &json!({"pid":std::process::id()}),
        );
        let until = std::time::Instant::now() + std::time::Duration::from_secs(10);
        while !profile.join("lock-release.json").exists() {
            assert!(std::time::Instant::now() < until);
            std::thread::sleep(std::time::Duration::from_millis(10));
        }
        return;
    }
    let mut s = Stores::open(&dir).unwrap();
    if mode == "reopen" || mode == "init" {
        panic!("expected checkpoint exit");
    }
    let f = s.next_delivery().unwrap().unwrap();
    s.mark_dispatch(&f).unwrap();
    if mode == "hot_bad_old" {
        s.runtime
            .execute("UPDATE samples SET payload=payload||' '", [])
            .unwrap();
    }
    let value = ack(&f);
    let raw = serde_json::to_string(&value).unwrap();
    durable(&profile.join("r2-before.json"), &ledger(&s));
    if mode == "hot" || mode == "hot_bad_old" {
        struct Trace {
            db: *mut rusqlite::ffi::sqlite3,
            profile: PathBuf,
        }
        unsafe extern "C" fn trace(
            _: u32,
            data: *mut std::ffi::c_void,
            statement: *mut std::ffi::c_void,
            _: *mut std::ffi::c_void,
        ) -> i32 {
            let sql = rusqlite::ffi::sqlite3_sql(statement.cast());
            if !sql.is_null()
                && std::ffi::CStr::from_ptr(sql)
                    .to_bytes()
                    .starts_with(b"COMMIT")
            {
                let data = &*(data as *const Trace);
                let rc = rusqlite::ffi::sqlite3_db_cacheflush(data.db);
                durable(
                    &data.profile.join("r2-cacheflush.json"),
                    &json!({"returnCode":rc,"checkpoint":"real commit_delivery COMMIT trace before execution"}),
                );
                libc::_exit(if rc == 0 { 86 } else { 87 });
            }
            0
        }
        let mut context = Trace {
            db: unsafe { s.runtime.handle() },
            profile: profile.clone(),
        };
        unsafe {
            assert_eq!(
                rusqlite::ffi::sqlite3_trace_v2(
                    s.runtime.handle(),
                    rusqlite::ffi::SQLITE_TRACE_STMT as u32,
                    Some(trace),
                    (&mut context as *mut Trace).cast()
                ),
                0
            );
        }
        s.commit_delivery(&f, &value, &raw).unwrap();
        panic!("COMMIT checkpoint not reached");
    }
    assert_eq!(mode, "committed");
    s.commit_delivery(&f, &value, &raw).unwrap();
    durable(&profile.join("r2-after-commit.json"), &ledger(&s));
    unsafe { libc::_exit(86) }
}
#[test]
fn profile_contract_initialization_faults_and_no_replace() {
    let profile = owned_profile();
    let started = crate::domain::business_time::now();
    let output = child(&profile, "initialization_fault_suite", None);
    assert_eq!(
        output.status.code(),
        Some(0),
        "{}",
        String::from_utf8_lossy(&output.stdout)
    );
    let report: Value =
        serde_json::from_slice(&std::fs::read(profile.join("initialization-faults.json")).unwrap())
            .unwrap();
    let command: Value = serde_json::from_slice(
        &std::fs::read(profile.join("child-initialization_fault_suite-none-command.json")).unwrap(),
    )
    .unwrap();
    assert_eq!(report["pid"], command["pid"]);
    assert_eq!(report["parentPid"], json!(std::process::id()));
    assert_ne!(report["pid"], json!(std::process::id()));
    assert_eq!(report["faults"].as_array().unwrap().len(), 13);
    for case in report["faults"].as_array().unwrap() {
        assert_eq!(case["pid"], command["pid"]);
        assert_eq!(case["immediateLockReacquiredBeforeChildExit"], true);
    }
    durable(
        &profile.join("fault-suite-parent.json"),
        &json!({"parentPid":std::process::id(),"childPid":command["pid"],"childExit":output.status.code(),"startedAt":started,"finishedAt":crate::domain::business_time::now(),"assertionsRanInChildBeforeExit":true,"reportSha256":crate::domain::facts_canonical::sha(&std::fs::read(profile.join("initialization-faults.json")).unwrap())}),
    );
}
// 夹具只在单个exact子进程创建/打开；原立即取锁断言不依赖退出清理，不再spawn其他进程。
fn initialization_fault_cases(report_path: &Path) {
    let mut records = vec![];
    for stage in [
        "file_sync",
        "file_close",
        "directory_sync",
        "sentinel_durable",
        "database_files_durable",
        "config_committed",
        "runtime_committed",
        "sqlite_close",
        "database_commits_closed",
        "initial_ro_checked",
        "staging_durable",
        "credential_installed",
        "staging_removed",
    ] {
        let profile = owned_profile();
        let dir = profile.join("local-acquisition-v1");
        FAILURE.with(|f| *f.borrow_mut() = Some((stage.into(), 1, 0)));
        let result = Stores::open(&dir).err().expect("injected failure");
        FAILURE.with(|f| *f.borrow_mut() = None);
        assert!(
            result.starts_with("synthetic_profile_"),
            "{stage}: {result}"
        );
        assert!(!dir.join("logs").exists());
        assert!(Stores::open(&dir).is_err());
        let lock = crate::infrastructure::local_profile_lock::ProfileLock::acquire(&profile)
            .unwrap_or_else(|error| {
                use std::os::unix::fs::MetadataExt;
                let m=std::fs::symlink_metadata(profile.join(".daa-runtime.lock")).unwrap();
                let mut matching=vec![];let mut scanned=0;
                if let Ok(entries)=std::fs::read_dir("/dev/fd") {
                    for entry in entries.take(4096).flatten() {
                        if let Some(fd)=entry.file_name().to_str().and_then(|s|s.parse::<i32>().ok()) {
                            scanned+=1;let mut st=std::mem::MaybeUninit::<libc::stat>::uninit();
                            if unsafe{libc::fstat(fd,st.as_mut_ptr())}==0 {
                                let st=unsafe{st.assume_init()};
                                if st.st_dev as u64==m.dev() && st.st_ino==m.ino() {
                                    matching.push(json!({"fd":fd,"fdFlags":unsafe{libc::fcntl(fd,libc::F_GETFD)}}));
                                }
                            }
                        }
                    }
                }
                durable(&profile.join("initialization-lock-failure.json"),&json!({"stage":stage,"profile":profile,"pid":std::process::id(),"error":error,"firstInitializationError":result,"dev":m.dev(),"ino":m.ino(),"ownMatchingLockFDs":matching,"ownFDsScanned":scanned,"scanLimit":4096,"noRetryOrAssertionChange":true}));
                panic!("{stage}: lock not released: {error}");
            });
        drop(lock);
        use std::os::unix::fs::MetadataExt;
        let m = std::fs::symlink_metadata(profile.join(".daa-runtime.lock")).unwrap();
        let record = json!({"profile":profile,"stage":stage,"firstError":result,"sentinel":dir.join(SENTINEL).exists(),"staging":dir.join(STAGING).exists(),"credential":dir.join(CREDENTIAL).exists(),"reopenRejected":true,"productLogs":false,"pid":std::process::id(),"parentPid":unsafe{libc::getppid()},"lockIdentity":{"dev":m.dev(),"ino":m.ino()},"immediateLockReacquiredBeforeChildExit":true,"observedAt":crate::domain::business_time::now()});
        durable(&profile.join("initialization-case.json"), &record);
        records.push(record);
    }
    let profile = owned_profile();
    let dir = profile.join("local-acquisition-v1");
    INSTALL_CONFLICT.with(|v| v.set(true));
    assert!(matches!(Stores::open(&dir),Err(e)if e=="profile_install_conflict"));
    assert_eq!(
        std::fs::read(dir.join(CREDENTIAL)).unwrap(),
        b"synthetic competing credential"
    );
    assert!(dir.join(SENTINEL).exists() && dir.join(STAGING).exists());
    assert!(!dir.join("logs").exists());
    assert!(Stores::open(&dir).is_err());
    durable(
        report_path,
        &json!({"pid":std::process::id(),"parentPid":unsafe{libc::getppid()},"faults":records,"noReplaceProfile":profile,"noReplacePreservedCompetingBytes":true,"completedBeforeChildExit":true}),
    );
}
#[test]
fn profile_contract_initialization_durable_process_exits() {
    for stage in [
        "sentinel_durable",
        "config_committed",
        "runtime_committed",
        "database_commits_closed",
        "staging_durable",
        "credential_installed",
        "staging_removed",
        "sentinel_removed",
    ] {
        let profile = owned_profile();
        let dir = profile.join("local-acquisition-v1");
        let result = child(&profile, "init", Some(stage));
        assert_eq!(result.status.code(), Some(86));
        assert!(!dir.join("logs").exists());
        if stage == "sentinel_removed" {
            let s = Stores::open(&dir).unwrap();
            assert_eq!(s.delivery_snapshot(false).unwrap()["state"], "stopped");
        } else {
            assert!(Stores::open(&dir).is_err());
        }
    }
}
#[test]
fn profile_contract_last_directory_sync_failure_is_not_retroactive_success() {
    // PM只读解释：当次必须拒绝；下次若最终可见资料完整则是新的sealed cold完整后检。
    let profile = owned_profile();
    let dir = profile.join("local-acquisition-v1");
    FAILURE.with(|f| *f.borrow_mut() = Some(("directory_sync".into(), 8, 0)));
    let first = Stores::open(&dir).err().unwrap();
    FAILURE.with(|f| *f.borrow_mut() = None);
    assert_eq!(first, "synthetic_profile_directory_sync");
    assert!(!dir.join("logs").exists());
    assert!(
        !dir.join(SENTINEL).exists()
            && !dir.join(STAGING).exists()
            && dir.join(CREDENTIAL).exists()
    );
    let next = Stores::open(&dir).unwrap();
    assert_eq!(next.delivery_snapshot(false).unwrap()["state"], "stopped");
    drop(next);
    durable(
        &profile.join("final-sync-failure-and-next-cold.json"),
        &json!({"firstError":first,"firstAdmitted":false,"firstPersistentLogs":false,"nextColdFullCheck":true,"priorFsyncSuccessClaimed":false,"powerLossProof":false}),
    );
}
#[test]
fn profile_contract_recovery_three_process_exit_boundaries() {
    for stage in ["before_native", "after_native", "after_ro"] {
        let profile = prepared_profile();
        let dir = profile.join("local-acquisition-v1");
        assert_eq!(child(&profile, "hot", None).status.code(), Some(86));
        let before: Value =
            serde_json::from_slice(&std::fs::read(profile.join("r2-before.json")).unwrap())
                .unwrap();
        let initial = snapshot_json(&capture(&dir).unwrap());
        durable(&profile.join("r2-crash-materials.json"), &initial);
        std::fs::copy(
            dir.join("runtime.sqlite-journal"),
            profile.join("r2-hot-journal.bin"),
        )
        .unwrap();
        assert_eq!(
            child(&profile, "reopen", Some(stage)).status.code(),
            Some(86)
        );
        if stage == "before_native" {
            assert_eq!(snapshot_json(&capture(&dir).unwrap()), initial);
        } else {
            assert!(!dir.join("runtime.sqlite-journal").exists());
        }
        let s = Stores::open(&dir).unwrap();
        let after = ledger(&s);
        originals_equal(&before, &after);
        for table in ["sample_delivery", "delivery_parts", "sample_references"] {
            assert_eq!(after["runtime"][table], before["runtime"][table]);
        }
        assert_eq!(after["runtime"]["delivery_receipts"], json!([]));
        assert_eq!(s.delivery_snapshot(false).unwrap()["counts"]["unknown"], 1);
        assert_eq!(s.delivery_snapshot(false).unwrap()["running"], false);
        drop(s);
        durable(&profile.join("r2-after.json"), &after);
    }
}
fn tree_for_recovery(dir: &Path) -> Value {
    fn visit(root: &Path, dir: &Path, out: &mut Vec<Value>) {
        let mut entries = std::fs::read_dir(dir)
            .unwrap()
            .map(Result::unwrap)
            .collect::<Vec<_>>();
        entries.sort_by_key(|e| e.file_name());
        for e in entries {
            let path = e.path();
            let m = std::fs::symlink_metadata(&path).unwrap();
            let name = path
                .strip_prefix(root)
                .unwrap()
                .to_string_lossy()
                .to_string();
            if m.file_type().is_symlink() {
                out.push(json!([name, "symlink", std::fs::read_link(&path).unwrap()]));
            } else if m.is_dir() {
                visit(root, &path, out);
            } else {
                out.push(json!([
                    name,
                    m.len(),
                    crate::domain::facts_canonical::sha(&std::fs::read(path).unwrap())
                ]));
            }
        }
    }
    let mut out = vec![];
    visit(dir, dir, &mut out);
    json!(out)
}
fn fixture_sql(profile: &Path, role: &str, sql: &str) {
    let _lock = crate::infrastructure::local_profile_lock::ProfileLock::acquire(profile).unwrap();
    let c = rusqlite::Connection::open_with_flags(
        profile
            .join("local-acquisition-v1")
            .join(format!("{role}.sqlite")),
        rusqlite::OpenFlags::SQLITE_OPEN_READ_WRITE | rusqlite::OpenFlags::SQLITE_OPEN_NO_MUTEX,
    )
    .unwrap();
    c.execute_batch(sql).unwrap();
    c.close().unwrap();
}
#[test]
fn profile_contract_rejects_binding_marker_header_link_wal_and_unknown_ddl() {
    use std::os::unix::fs::symlink;
    let mut records = vec![];
    for case in [
        "sentinel",
        "staging",
        "hash",
        "oversize",
        "replace",
        "symlink",
        "hardlink",
        "credential_hardlink",
        "wal",
        "shm",
        "wal_header",
        "wrong_application",
        "unknown_ddl",
        "empty_key",
        "null_key",
    ] {
        let profile = owned_profile();
        let dir = profile.join("local-acquisition-v1");
        drop(Stores::open(&dir).unwrap());
        match case {
            "sentinel" => std::fs::write(dir.join(SENTINEL), b"broken marker").unwrap(),
            "staging" => std::fs::write(dir.join(STAGING), b"unfinished").unwrap(),
            "hash" => {
                let mut value: Value =
                    serde_json::from_slice(&std::fs::read(dir.join(CREDENTIAL)).unwrap()).unwrap();
                value["payloadSha256"] = json!("sha256:bad");
                std::fs::write(dir.join(CREDENTIAL), value.to_string()).unwrap();
            }
            "oversize" => std::fs::write(dir.join(CREDENTIAL), vec![b' '; 32769]).unwrap(),
            "replace" => {
                std::fs::copy(dir.join("runtime.sqlite"), profile.join("replacement")).unwrap();
                std::fs::rename(profile.join("replacement"), dir.join("runtime.sqlite")).unwrap();
            }
            "symlink" => {
                std::fs::rename(dir.join("runtime.sqlite"), profile.join("saved-runtime")).unwrap();
                symlink(profile.join("saved-runtime"), dir.join("runtime.sqlite")).unwrap();
            }
            "hardlink" => {
                std::fs::hard_link(dir.join("runtime.sqlite"), profile.join("alias")).unwrap()
            }
            "credential_hardlink" => {
                std::fs::hard_link(dir.join(CREDENTIAL), profile.join("alias")).unwrap()
            }
            "wal" => std::fs::write(dir.join("runtime.sqlite-wal"), b"x").unwrap(),
            "shm" => std::fs::write(dir.join("runtime.sqlite-shm"), b"x").unwrap(),
            "wal_header" | "wrong_application" => {
                use std::io::{Seek, SeekFrom, Write};
                let mut f = std::fs::OpenOptions::new()
                    .write(true)
                    .open(dir.join("runtime.sqlite"))
                    .unwrap();
                f.seek(SeekFrom::Start(if case == "wal_header" { 18 } else { 68 }))
                    .unwrap();
                f.write_all(if case == "wal_header" {
                    &[2, 2]
                } else {
                    &[0, 0]
                })
                .unwrap();
                f.sync_all().unwrap();
            }
            "unknown_ddl" => fixture_sql(&profile, "runtime", "CREATE TABLE unknown(id INTEGER)"),
            "empty_key" | "null_key" => {
                let key = if case == "null_key" { "NULL" } else { "''" };
                fixture_sql(&profile,"config",&format!("INSERT INTO source_documents VALUES({key},'{}','bad-key','synthetic archive','[]')",crate::domain::local_sample::digest("synthetic archive")));
            }
            _ => unreachable!(),
        }
        let before = tree_for_recovery(&dir);
        let error = Stores::open(&dir).err().expect(case);
        assert_eq!(tree_for_recovery(&dir), before, "{case}");
        records.push(json!({"profile":profile,"case":case,"error":error,"rejectedWithoutBusinessWrites":true}));
    }
    durable(
        &std::env::temp_dir().join("binding-rejections.json"),
        &json!(records),
    );
}
#[test]
fn profile_contract_rejects_dual_journal_and_toctou() {
    for stage in ["dual_journal", "before_lock", "before_native"] {
        let profile = prepared_profile();
        let dir = profile.join("local-acquisition-v1");
        assert_eq!(child(&profile, "hot", None).status.code(), Some(86));
        let journal = std::fs::read(dir.join("runtime.sqlite-journal")).unwrap();
        if stage == "dual_journal" {
            std::fs::write(
                dir.join("config.sqlite-journal"),
                b"untrusted second journal",
            )
            .unwrap();
        } else {
            DRIFT.with(|v| *v.borrow_mut() = Some(stage.into()));
        }
        let error = Stores::open(&dir).err().unwrap();
        DRIFT.with(|v| *v.borrow_mut() = None);
        assert!(error.contains("profile_changed") || error == "profile_recovery_rejected");
        assert_eq!(
            std::fs::read(dir.join("runtime.sqlite-journal")).unwrap(),
            journal
        );
        assert!(!profile.join("r2-stage-after_native.json").exists());
        durable(
            &profile.join("gate-refusal.json"),
            &json!({"stage":stage,"error":error,"nativeAttempted":false,"journalSha256":crate::domain::facts_canonical::sha(&journal),"testInjectedDrift":stage!="dual_journal"}),
        );
    }
}
#[test]
fn profile_contract_resource_gate_and_live_directory_alias() {
    let profile = owned_profile();
    let dir = profile.join("local-acquisition-v1");
    FREE_BYTES.with(|v| v.set(Some(0)));
    let error = Stores::open(&dir).err().unwrap();
    FREE_BYTES.with(|v| v.set(None));
    assert_eq!(error, "profile_initialization_capacity");
    assert!(
        !dir.join(SENTINEL).exists()
            && !dir.join("config.sqlite").exists()
            && !dir.join("logs").exists()
    );
    let s = Stores::open(&dir).unwrap();
    let moved = profile.with_file_name(format!("moved-{}", id()));
    std::fs::rename(&profile, &moved).unwrap();
    assert!(
        matches!(Stores::open(&moved.join("local-acquisition-v1")),Err(e)if e=="profile_locked")
    );
    std::fs::rename(&moved, &profile).unwrap();
    drop(s);
    let hot = prepared_profile();
    let dir = hot.join("local-acquisition-v1");
    assert_eq!(child(&hot, "hot", None).status.code(), Some(86));
    let before = snapshot_json(&capture(&dir).unwrap());
    FREE_BYTES.with(|v| v.set(Some(0)));
    let error = Stores::open(&dir).err().unwrap();
    FREE_BYTES.with(|v| v.set(None));
    assert_eq!(error, "profile_initialization_capacity");
    assert_eq!(snapshot_json(&capture(&dir).unwrap()), before);
    assert!(!hot.join("r2-stage-after_native.json").exists());
}
fn originals_equal(before: &Value, after: &Value) {
    for (role, tables) in [
        (
            "config",
            vec![
                "source_documents",
                "configuration_draft",
                "configuration_revisions",
                "active_selection",
                "activation_intents",
            ],
        ),
        (
            "runtime",
            vec![
                "plc_sources",
                "configuration_contexts",
                "activation_journal",
                "collection_cycles",
                "samples",
                "delivery_cycles",
            ],
        ),
    ] {
        for table in tables {
            assert_eq!(before[role][table], after[role][table], "{role}.{table}");
        }
    }
}
#[test]
fn profile_contract_real_ack_hot_rollback_and_committed_reopen() {
    for mode in ["hot", "committed"] {
        let profile = prepared_profile();
        let dir = profile.join("local-acquisition-v1");
        let output = child(&profile, mode, None);
        assert_eq!(
            output.status.code(),
            Some(86),
            "{}",
            String::from_utf8_lossy(&output.stderr)
        );
        let before: Value =
            serde_json::from_slice(&std::fs::read(profile.join("r2-before.json")).unwrap())
                .unwrap();
        let snapshot = capture(&dir).unwrap();
        durable(
            &profile.join("r2-crash-materials.json"),
            &snapshot_json(&snapshot),
        );
        if mode == "hot" {
            let flush: Value =
                serde_json::from_slice(&std::fs::read(profile.join("r2-cacheflush.json")).unwrap())
                    .unwrap();
            assert_eq!(flush["returnCode"], 0);
            assert!(snapshot.get("runtime.sqlite-journal").unwrap().stat.len > 512);
            assert!(
                matches!(inspect_sql(&dir),Err(ProbeFailure::Sqlite("runtime",ref e))if rollback_error(e))
            );
            std::fs::copy(
                dir.join("runtime.sqlite-journal"),
                profile.join("r2-hot-journal.bin"),
            )
            .unwrap();
        }
        let s = Stores::open(&dir).unwrap();
        let after = ledger(&s);
        originals_equal(&before, &after);
        assert_eq!(s.delivery_snapshot(false).unwrap()["running"], false);
        if mode == "hot" {
            assert_eq!(after["runtime"]["delivery_receipts"], json!([]));
            assert_eq!(
                after["runtime"]["sample_delivery"],
                before["runtime"]["sample_delivery"]
            );
            assert_eq!(
                after["runtime"]["delivery_parts"],
                before["runtime"]["delivery_parts"]
            );
            assert_eq!(
                after["runtime"]["sample_references"],
                before["runtime"]["sample_references"]
            );
            assert_eq!(s.delivery_snapshot(false).unwrap()["counts"]["unknown"], 1);
            for index in [0, 1, 2, 3, 4, 5, 6, 7, 8, 10] {
                assert_eq!(
                    after["runtime"]["delivery_batches"][0][index],
                    before["runtime"]["delivery_batches"][0][index],
                    "batch column {index}"
                );
            }
        } else {
            let committed: Value = serde_json::from_slice(
                &std::fs::read(profile.join("r2-after-commit.json")).unwrap(),
            )
            .unwrap();
            for table in [
                "sample_delivery",
                "delivery_parts",
                "delivery_receipts",
                "sample_references",
                "delivery_batches",
            ] {
                assert_eq!(
                    after["runtime"][table], committed["runtime"][table],
                    "{table}"
                );
            }
        }
        drop(s);
        durable(&profile.join("r2-after.json"), &after);
        durable(
            &profile.join("r2-after-materials.json"),
            &snapshot_json(&capture(&dir).unwrap()),
        );
    }
}

#[test]
fn profile_contract_business_ledger_refusal_before_and_after_native() {
    for kind in ["raw_sha", "ack_atomic"] {
        let profile = prepared_profile();
        let dir = profile.join("local-acquisition-v1");
        fixture_sql(
            &profile,
            "runtime",
            if kind == "raw_sha" {
                "UPDATE samples SET payload=payload||' '"
            } else {
                "UPDATE sample_delivery SET state='acknowledged',acknowledged_at='2026-11-06T10:00:00+08:00'"
            },
        );
        let before = tree_for_recovery(&dir);
        let error = Stores::open(&dir).err().unwrap();
        assert_eq!(error, "profile_contract_business_admission_failed");
        assert_eq!(tree_for_recovery(&dir), before);
        durable(
            &profile.join("cold-ledger-refusal.json"),
            &json!({"kind":kind,"error":error,"businessAdmitted":false,"nativeAttempted":false}),
        );
    }
    let profile = prepared_profile();
    let dir = profile.join("local-acquisition-v1");
    assert_eq!(child(&profile, "hot_bad_old", None).status.code(), Some(86));
    let before = capture(&dir).unwrap();
    let journal = before.get("runtime.sqlite-journal").unwrap();
    std::fs::copy(
        dir.join("runtime.sqlite-journal"),
        profile.join("r2-hot-journal.bin"),
    )
    .unwrap();
    assert!(
        matches!(inspect_sql(&dir),Err(ProbeFailure::Sqlite("runtime",ref e))if rollback_error(e))
    );
    let error = Stores::open(&dir).err().unwrap();
    assert_eq!(error, "profile_recovery_business_admission_failed");
    assert!(!dir.join("runtime.sqlite-journal").exists());
    assert!(profile.join("r2-stage-after_native.json").exists());
    let after = capture(&dir).unwrap();
    assert_ne!(before, after);
    durable(
        &profile.join("post-native-ledger-refusal.json"),
        &json!({"error":error,"nativeWriteCompleted":true,"businessAdmitted":false,"journalBytes":journal.stat.len,"journalSha256":journal.sha,"before":snapshot_json(&before),"after":snapshot_json(&after)}),
    );
}
#[test]
fn profile_contract_real_external_profile_lock() {
    let profile = owned_profile();
    let dir = profile.join("local-acquisition-v1");
    drop(Stores::open(&dir).unwrap());
    let before = tree_for_recovery(&dir);
    let exe = std::env::current_exe().unwrap();
    let argv = [
        "--exact",
        "infrastructure::local_store::profile_contract_tests::profile_contract_child",
        "--nocapture",
    ];
    let mut process = std::process::Command::new(&exe)
        .args(argv)
        .env_clear()
        .env("TMPDIR", std::env::temp_dir())
        .env("DAA_008_R2_CHILD", "hold_lock")
        .env("DAA_008_R2_PROFILE", &profile)
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::piped())
        .spawn()
        .unwrap();
    let until = std::time::Instant::now() + std::time::Duration::from_secs(5);
    while !profile.join("lock-ready.json").exists() {
        if std::time::Instant::now() >= until {
            process.kill().unwrap();
            panic!("child lock deadline");
        }
        std::thread::sleep(std::time::Duration::from_millis(10));
    }
    let error = Stores::open(&dir).err().unwrap();
    assert_eq!(error, "profile_locked");
    assert_eq!(tree_for_recovery(&dir), before);
    durable(&profile.join("lock-release.json"), &json!(true));
    let output = process.wait_with_output().unwrap();
    assert_eq!(output.status.code(), Some(0));
    durable(
        &profile.join("external-lock-evidence.json"),
        &json!({"executable":exe,"argv":argv,"envClear":true,"TMPDIR":std::env::temp_dir(),"exit":output.status.code(),"error":error,"storeUnchanged":true}),
    );
    drop(Stores::open(&dir).unwrap());
}

fn import_synthetic(
    c: &Configuration,
    number: u16,
    fields: usize,
    comment: usize,
    nested: bool,
) -> Configuration {
    let plc = c.plcs[0].id.clone();
    let name = format!("Synthetic{number}");
    let mut raw = format!(
        "DATA_BLOCK \"{name}\"\n{{ S7_Optimized_Access := 'FALSE' }}\nVERSION : 0.1\nVAR\n"
    );
    if nested {
        for i in 0..8 {
            raw.push_str(&format!("n{i} : Struct\n"));
        }
        raw.push_str("leaf : Bool;\n");
        for _ in 0..8 {
            raw.push_str("END_STRUCT;\n");
        }
    } else {
        for i in 0..fields {
            raw.push_str(&format!("p{i} : Bool; // {}\n", "x".repeat(comment)));
        }
    }
    raw.push_str("END_VAR\nBEGIN\nEND_DATA_BLOCK\n");
    let source = crate::domain::local_configuration::SourceDocument {
        id: String::new(),
        name: format!("synthetic{number}.db"),
        content: raw,
        sha256: String::new(),
        plc_id: plc,
        db_number: Some(number),
        diagnostics: vec![],
        lineage_id: None,
    };
    let imported = crate::infrastructure::tia_source::import(c, vec![source]).unwrap();
    assert!(imported.can_confirm, "{:?}", imported.issues);
    imported.configuration
}
#[test]
fn profile_contract_large_and_deep_valid_local_context_stays_local() {
    let profile = owned_profile();
    let dir = profile.join("local-acquisition-v1");
    let mut s = Stores::open(&dir).unwrap();
    let mut c = super::tests::configuration();
    c = import_synthetic(&c, 3, 1500, 400, false);
    c = import_synthetic(&c, 4, 1, 0, true);
    assert!(crate::domain::local_configuration::validate(&c).is_empty());
    let revision = super::tests::activated(&mut s, &c);
    s.commit_cycle(super::tests::cycle(&c, &revision)).unwrap();
    let context: String = s
        .runtime
        .query_row(
            "SELECT payload FROM configuration_contexts WHERE revision=?1",
            [&revision],
            |r| r.get(0),
        )
        .unwrap();
    assert!(context.len() > 1024 * 1024);
    let mut settings = s.delivery_settings().unwrap();
    let old = settings.settings_revision.clone();
    settings.target_id = Some("synthetic-target".into());
    settings.origin = Some("https://example.invalid".into());
    settings.adoption_reference = "local-context-bound".into();
    let generation: String = s
        .runtime
        .query_row(
            "SELECT generation FROM plc_sources WHERE plc_id=?1",
            [&c.plcs[0].id],
            |r| r.get(0),
        )
        .unwrap();
    settings.sources = vec![crate::domain::local_delivery::SourceAdoption {
        plc_id: c.plcs[0].id.clone(),
        source_generation: generation,
        definition_set_digest: format!("sha256:{}", "0".repeat(64)),
        context_sha256: format!("sha256:{}", crate::domain::local_sample::digest(&context)),
        sequence_from: "1".into(),
        sequence_through: "1".into(),
        reference: "synthetic-candidate-only-no-provider-adoption".into(),
    }];
    settings.contract_pins = json!(crate::domain::local_delivery::CONTRACT_PINS
        .iter()
        .map(|(k, v)| (k.to_string(), v.to_string()))
        .collect::<std::collections::BTreeMap<_, _>>());
    s.save_delivery_settings(settings, old).unwrap();
    assert!(s.next_delivery().unwrap().is_none());
    assert!(
        s.delivery_snapshot(false).unwrap()["sampleCounts"]["needsProcessing"]
            .as_u64()
            .unwrap()
            > 0
    );
    let before = ledger(&s);
    s.clean_exit().unwrap();
    drop(s);
    let s = Stores::open(&dir).unwrap();
    let after = ledger(&s);
    originals_equal(&before, &after);
    drop(s);
    durable(
        &profile.join("large-local-context.json"),
        &json!({"contextBytes":context.len(),"contextSha256":crate::domain::local_sample::digest(&context),"localValid":true,"uploadBlocked":true,"coldReopened":true}),
    );
}
#[test]
fn profile_contract_partial_ack_and_rejected_parent_are_valid_cold_states() {
    use crate::domain::{
        facts_wire::Batch,
        local_sample::{CycleInput, PointFact, ReadTiming},
    };
    // Construct a legal persisted subset batch before any dispatch. Product throughput is not asserted.
    let profile = owned_profile();
    let dir = profile.join("local-acquisition-v1");
    let mut s = Stores::open(&dir).unwrap();
    let mut c = super::tests::configuration();
    c = import_synthetic(&c, 3, 160, 500, false);
    for p in &mut c.points {
        p.enabled = false;
        p.group_id = None;
    }
    let db = c
        .dbs
        .iter()
        .find(|d| d.number == 3 && d.plc_id == c.plcs[0].id)
        .unwrap()
        .clone();
    let changes = crate::infrastructure::plc_layout::preview(&c, &db.id).unwrap();
    crate::infrastructure::plc_layout::confirm(
        &mut c,
        &db.id,
        &changes
            .iter()
            .map(|p| p.point_id.clone())
            .collect::<Vec<_>>(),
    )
    .unwrap();
    for p in c.points.iter_mut().filter(|p| p.db_id == db.id) {
        p.enabled = true;
        p.group_id = Some(c.groups[0].id.clone());
    }
    assert!(
        crate::domain::local_configuration::validate(&c).is_empty(),
        "{:?}",
        crate::domain::local_configuration::validate(&c)
    );
    let revision = super::tests::activated(&mut s, &c);
    let now = crate::domain::business_time::now();
    let facts = c
        .points
        .iter()
        .filter(|p| p.enabled)
        .map(|p| {
            (
                p.id.clone(),
                PointFact {
                    definition: p.clone(),
                    value: json!(false),
                    observed_at: now.clone(),
                    quality: "good".into(),
                    reason: None,
                },
            )
        })
        .collect();
    s.commit_cycle(CycleInput {
        plc_id: c.plcs[0].id.clone(),
        group_id: c.groups[0].id.clone(),
        revision,
        started_at: now.clone(),
        finished_at: now.clone(),
        origin: "synthetic-local".into(),
        points: std::collections::BTreeMap::from([(3, facts)]),
        reads: vec![ReadTiming {
            db_number: 3,
            start: 0,
            size: db.length,
            started_at: now.clone(),
            finished_at: now,
            duration_ms: 0,
            quality: "good".into(),
        }],
    })
    .unwrap();
    let cycle: String = s
        .runtime
        .query_row("SELECT id FROM collection_cycles", [], |r| r.get(0))
        .unwrap();
    let built = s.build_delivery_cycle(&cycle).unwrap();
    assert!(built.parts.len() > 1);
    super::delivery_tests::adopt(&mut s, &built);
    let f = s.next_delivery().unwrap().unwrap();
    let batch = Batch::new(
        f.batch.instance_id.clone(),
        f.batch.batch_id.clone(),
        f.batch.batch_created_at.clone(),
        f.batch.cycles.clone(),
        vec![f.batch.samples[0].clone()],
        None,
    )
    .unwrap();
    let body = batch.bytes().unwrap();
    let members = crate::domain::local_sample::encode(
        &batch
            .samples
            .iter()
            .map(|p| json!({"sampleId":p.sample_id,"part":p.part,"contentDigest":p.content_digest}))
            .collect::<Vec<_>>(),
    )
    .unwrap();
    let tx = s.runtime.transaction().unwrap();
    tx.execute("UPDATE delivery_batches SET request_digest=?1,body_sha=?2,body=?3,members=?4 WHERE batch_id=?5",rusqlite::params![batch.request_digest,crate::domain::facts_canonical::sha(body.as_bytes()),body,members,batch.batch_id]).unwrap();
    tx.execute(
        "UPDATE delivery_parts SET state='pending',batch_id=NULL WHERE batch_id=?1 AND part!=?2",
        rusqlite::params![batch.batch_id, batch.samples[0].part],
    )
    .unwrap();
    tx.commit().unwrap();
    let f = s.next_delivery().unwrap().unwrap();
    s.mark_dispatch(&f).unwrap();
    let value = ack(&f);
    assert_eq!(value["data"]["cycles"][0]["complete"], false);
    assert_eq!(value["data"]["cycles"][0]["qualityGood"], true);
    assert_eq!(value["data"]["results"][0]["sourceSampleComplete"], false);
    s.commit_delivery(&f, &value, &value.to_string()).unwrap();
    s.clean_exit().unwrap();
    drop(s);
    let mut s = Stores::open(&dir).unwrap();
    assert_eq!(
        s.runtime
            .query_row::<String, _, _>("SELECT state FROM sample_delivery", [], |r| r.get(0))
            .unwrap(),
        "pending"
    );
    let remaining = s.next_delivery().unwrap().unwrap();
    let mut final_ack = ack(&remaining);
    final_ack["data"]["cycles"][0]["complete"] = json!(true);
    let expected = final_ack["data"]["cycles"][0]["expectedParts"].clone();
    final_ack["data"]["cycles"][0]["receivedParts"] = expected;
    for r in final_ack["data"]["results"].as_array_mut().unwrap() {
        r["sourceSampleComplete"] = json!(true);
    }
    s.mark_dispatch(&remaining).unwrap();
    s.commit_delivery(&remaining, &final_ack, &final_ack.to_string())
        .unwrap();
    s.clean_exit().unwrap();
    drop(s);
    let s = Stores::open(&dir).unwrap();
    assert_eq!(
        s.runtime
            .query_row::<String, _, _>("SELECT state FROM sample_delivery", [], |r| r.get(0))
            .unwrap(),
        "acknowledged"
    );
    drop(s);
    durable(
        &profile.join("partial-cached-ack-cold.json"),
        &json!({"cachedComplete":false,"cachedQualityGood":true,"cachedSourceSampleComplete":false,"afterRemainingPartsColdAccepted":true}),
    );
    let profile = prepared_profile();
    let dir = profile.join("local-acquisition-v1");
    let mut s = Stores::open(&dir).unwrap();
    let f = s.next_delivery().unwrap().unwrap();
    s.mark_dispatch(&f).unwrap();
    let now = crate::domain::business_time::now();
    let expiry = (crate::domain::facts_wire::time(&now).unwrap() + chrono::Duration::days(120))
        .to_rfc3339_opts(chrono::SecondsFormat::Nanos, false);
    let rejected = json!({"code":403,"message":"source_rejected","errorCode":"plc_facts.source_rejected","data":{"contractVersion":"plc-facts/v1","instanceId":f.batch.instance_id,"batchId":f.batch.batch_id,"requestDigest":f.batch.request_digest,"receiptId":id(),"recordedAt":now,"persistence":"rejection_recorded","newFactsCommitted":false,"retryable":false,"retirementAllowed":true,"rejectionToken":"synthetic-parent-token","rejectionExpiresAt":expiry,"diagnostics":f.batch.samples.iter().map(|p|json!({"sampleId":p.sample_id,"part":p.part,"diagnosis":"eligible","historicalProof":Value::Null})).collect::<Vec<_>>()}});
    let raw = rejected.to_string();
    let eligible = match crate::domain::local_delivery::classify(
        &f.batch,
        403,
        "application/json",
        raw.as_bytes(),
        None,
        1,
        0,
    ) {
        crate::domain::local_delivery::Reply::Rejected { eligible, .. } => eligible,
        _ => panic!("legal rejection"),
    };
    s.reject_delivery(&f, &rejected, &eligible, &raw).unwrap();
    let child = s.next_delivery().unwrap().unwrap();
    assert_eq!(child.depth, 1);
    s.clean_exit().unwrap();
    drop(s);
    let mut s = Stores::open(&dir).unwrap();
    let child = s.next_delivery().unwrap().unwrap();
    assert_eq!(child.depth, 1);
    let value = ack(&child);
    s.mark_dispatch(&child).unwrap();
    s.commit_delivery(&child, &value, &value.to_string())
        .unwrap();
    s.clean_exit().unwrap();
    drop(s);
    drop(Stores::open(&dir).unwrap());
    durable(
        &profile.join("rejected-parent-cold.json"),
        &json!({"childDepth":1,"parentProofRetained":true,"coldBeforeAndAfterChildAck":true}),
    );
}

fn rework_drift_case(stage: &str, action: &str, mode: &str) {
    let profile = if mode == "cold" || mode == "initialize" {
        owned_profile()
    } else {
        prepared_profile()
    };
    let dir = profile.join("local-acquisition-v1");
    if mode == "cold" {
        let mut s = Stores::open(&dir).unwrap();
        s.clean_exit().unwrap();
        drop(s);
    }
    if mode == "hot" || mode == "hot_bad_old" {
        assert_eq!(child(&profile, mode, None).status.code(), Some(86));
        assert!(
            matches!(inspect_sql(&dir),Err(ProbeFailure::Sqlite("runtime",ref e))if rollback_error(e))
        );
        std::fs::copy(
            dir.join("runtime.sqlite-journal"),
            profile.join("rework-hot-journal.bin"),
        )
        .unwrap();
    }
    let before = if mode == "initialize" {
        Value::Null
    } else {
        snapshot_json(&capture(&dir).unwrap())
    };
    REWORK_MUTATION.with(|v| *v.borrow_mut() = Some((stage.into(), action.into())));
    let result = Stores::open(&dir);
    let admitted = result.is_ok();
    let error = result.as_ref().err().cloned();
    let bad_raw_count = result.as_ref().ok().map(|s| {
        s.runtime
            .query_row::<i64, _, _>(
                "SELECT count(*) FROM samples WHERE payload LIKE '% '",
                [],
                |r| r.get(0),
            )
            .unwrap()
    });
    drop(result);
    assert!(REWORK_MUTATION.with(|v| v.borrow().is_none()));
    durable(
        &profile.join("rework-result.json"),
        &json!({"profile":profile,"mode":mode,"stage":stage,"action":action,"admitted":admitted,"error":error,"badRawCountIfAdmitted":bad_raw_count,"before":before,"after":snapshot_json(&capture(&dir).unwrap()),"journalAfter":dir.join("runtime.sqlite-journal").exists()}),
    );
    assert!(
        !admitted,
        "{mode}/{stage}/{action} silently rebased or downgraded"
    );
    if stage == "after_native" || stage == "native_closed" {
        assert_eq!(
            error.as_deref(),
            Some("profile_recovery_business_admission_failed")
        );
        assert!(!dir.join("runtime.sqlite-journal").exists());
    }
}
#[test]
fn profile_contract_rework_regression_seen_credential_loss() {
    rework_drift_case("locked", "credential_remove", "cold");
}
#[test]
fn profile_contract_rework_regression_cold_same_inode_drift() {
    rework_drift_case("locked", "runtime_append", "cold");
}
#[test]
fn profile_contract_rework_regression_native_credential_loss_bad_sha() {
    rework_drift_case("after_native", "credential_remove", "hot_bad_old");
}

#[test]
fn profile_contract_rework_phase_material_continuity() {
    for (stage, action, mode) in [
        ("locked", "credential_rewrite", "cold"),
        ("after_ro", "credential_remove", "cold"),
        ("native_closed", "credential_rewrite", "hot"),
        ("native_closed", "credential_replace", "hot"),
        ("native_closed", "companion_append", "hot"),
        ("after_native", "runtime_append", "hot"),
        ("after_native", "credential_replace", "hot"),
        ("after_ro", "credential_rewrite", "hot"),
        ("initial_ro_checked", "runtime_append", "initialize"),
        ("sentinel_removed", "credential_remove", "initialize"),
        ("sentinel_removed", "runtime_append", "initialize"),
    ] {
        rework_drift_case(stage, action, mode);
    }
}
