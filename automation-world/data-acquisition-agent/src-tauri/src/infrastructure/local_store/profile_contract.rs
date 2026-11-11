//! 新profile原字节凭据、静态DDL指纹及持锁受控恢复；不认证、不认领既有资料。
use super::{schema, unsupported};
use crate::domain::{
    business_time, facts_canonical as pf,
    local_configuration::{id, valid_id, LocalResult},
};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::path::{Path, PathBuf};
pub(super) const CREDENTIAL: &str = "profile-contract.json";
pub(super) const SENTINEL: &str = ".profile-init.json";
pub(super) const STAGING: &str = ".profile-contract.installing";
pub(super) const AUX_BUDGET: u64 = 256 * 1024;
macro_rules! dto {($name:ident {$($field:ident:$ty:ty),*$(,)?})=>{#[derive(Clone,Debug,PartialEq,Eq,Serialize,Deserialize)]#[serde(rename_all="camelCase",deny_unknown_fields)]pub(super) struct $name {$(pub $field:$ty),*}}}
dto!(Identity {
    dev: String,
    ino: String
});
dto!(StoreContract {
    role: String,
    file_name: String,
    application_id: i64,
    schema_version: u32,
    schema_fingerprint: String,
    file_identity: Identity
});
dto!(Contract {contract:String,init_id:String,instance_id:String,created_at:String,time_profile:String,identity_profile:String,canonical_profile_dir:String,canonical_store_dir:String,profile_identity:Identity,store_identity:Identity,page_size:u32,journal_mode:String,stores:Vec<StoreContract>});
dto!(Envelope {
    format_version: u32,
    payload_utf8: String,
    payload_sha256: String
});
dto!(Initializing {
    format_version: u32,
    init_id: String,
    canonical_store_dir: String,
    created_at: String,
    phase: String
});
fn invalid() -> String {
    "profile_contract_invalid".into()
}
fn path_text(path: &Path) -> LocalResult<&str> {
    let s = path.to_str().ok_or_else(invalid)?;
    if s.len() > 4096
        || !path.is_absolute()
        || s.chars().any(char::is_control)
        || path
            .components()
            .any(|p| matches!(p, std::path::Component::ParentDir))
    {
        return Err(invalid());
    }
    Ok(s)
}
fn decimal(s: &str, positive: bool) -> bool {
    s.parse::<u64>()
        .map(|n| (!positive || n > 0) && n.to_string() == s)
        .unwrap_or(false)
}
impl Identity {
    fn valid(&self) -> bool {
        decimal(&self.dev, false) && decimal(&self.ino, true)
    }
}
pub(super) fn decode(raw: &[u8], profile: &Path, store: &Path) -> LocalResult<Contract> {
    let outer: Envelope = serde_json::from_value(local_json(
        std::str::from_utf8(raw).map_err(|_| invalid())?,
        32768,
    )?)
    .map_err(|_| invalid())?;
    if outer.format_version != 1
        || outer.payload_utf8.len() > 16384
        || outer.payload_sha256 != pf::sha(outer.payload_utf8.as_bytes())
    {
        return Err(invalid());
    }
    let value: Contract =
        serde_json::from_value(local_json(&outer.payload_utf8, 16384)?).map_err(|_| invalid())?;
    if value.contract != "daa-profile-recovery/v1"
        || !valid_id(&value.init_id)
        || !valid_id(&value.instance_id)
        || crate::domain::facts_wire::time(&value.created_at).is_err()
        || value.time_profile != business_time::TIME_PROFILE
        || value.identity_profile != "unix-dev-ino/v1"
        || value.page_size != 4096
        || value.journal_mode != "delete"
        || value.canonical_profile_dir != path_text(profile)?
        || value.canonical_store_dir != path_text(store)?
        || !value.profile_identity.valid()
        || !value.store_identity.valid()
        || value.stores.len() != 2
    {
        return Err(invalid());
    }
    for (index, (role, app, version, ddl)) in [
        ("config", schema::CONFIG_APP, 2, schema::config_sql()),
        ("runtime", schema::RUNTIME_APP, 3, schema::runtime_v3_sql()),
    ]
    .into_iter()
    .enumerate()
    {
        let s = &value.stores[index];
        if s.role != role
            || s.file_name != format!("{role}.sqlite")
            || s.application_id != app
            || s.schema_version != version
            || s.schema_fingerprint != schema::fingerprint(&ddl)?
            || !s.file_identity.valid()
        {
            return Err(invalid());
        }
    }
    if value.stores[0].file_identity == value.stores[1].file_identity {
        return Err(invalid());
    }
    Ok(value)
}
pub(super) fn encode(value: &Contract) -> LocalResult<Vec<u8>> {
    let inner = serde_json::to_string(value).map_err(|_| invalid())?;
    let bytes = serde_json::to_vec(&Envelope {
        format_version: 1,
        payload_sha256: pf::sha(inner.as_bytes()),
        payload_utf8: inner,
    })
    .map_err(|_| invalid())?;
    decode(
        &bytes,
        Path::new(&value.canonical_profile_dir),
        Path::new(&value.canonical_store_dir),
    )?;
    Ok(bytes)
}
/// 只接受原始SqliteFailure扩展码；格式化文本和primary READONLY都没有恢复权限。
pub(super) fn rollback_error(error: &rusqlite::Error) -> bool {
    matches!(error,rusqlite::Error::SqliteFailure(e,_) if e.extended_code==776)
}

#[cfg(unix)]
use std::os::unix::{
    fs::{MetadataExt, OpenOptionsExt, PermissionsExt},
    io::IntoRawFd,
};
use std::{
    fs::{File, OpenOptions},
    io::{Read, Write},
};
#[derive(Clone, Debug, PartialEq, Eq)]
pub(super) struct Stat {
    pub len: u64,
    pub identity: Identity,
    pub links: u64,
    pub mode: u32,
    modified: (i64, i64),
    changed: (i64, i64),
}
pub(super) fn stat(meta: &std::fs::Metadata) -> Stat {
    #[cfg(unix)]
    {
        Stat {
            len: meta.len(),
            identity: Identity {
                dev: meta.dev().to_string(),
                ino: meta.ino().to_string(),
            },
            links: meta.nlink(),
            mode: meta.mode() & 0o777,
            modified: (meta.mtime(), meta.mtime_nsec()),
            changed: (meta.ctime(), meta.ctime_nsec()),
        }
    }
    #[cfg(not(unix))]
    {
        Stat {
            len: meta.len(),
            identity: Identity {
                dev: "0".into(),
                ino: "0".into(),
            },
            links: 1,
            mode: 0,
            modified: (
                meta.modified()
                    .ok()
                    .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
                    .map(|t| t.as_secs() as i64)
                    .unwrap_or(0),
                0,
            ),
            changed: (0, 0),
        }
    }
}
#[derive(Clone, Debug, PartialEq, Eq)]
pub(super) struct Material {
    pub name: String,
    pub stat: Stat,
    pub sha: String,
    pub header: Vec<u8>,
    pub small: Vec<u8>,
}
#[derive(Clone, Debug, PartialEq, Eq)]
pub(super) struct Snapshot {
    pub profile: PathBuf,
    pub store: PathBuf,
    pub profile_identity: Option<Identity>,
    pub store_identity: Option<Identity>,
    pub store_mode: u32,
    pub files: Vec<Material>,
}
impl Snapshot {
    pub fn get(&self, name: &str) -> Option<&Material> {
        self.files.iter().find(|m| m.name == name)
    }
}
pub(super) fn canonical(path: &Path) -> LocalResult<PathBuf> {
    path_text(path)?;
    for ancestor in path.ancestors() {
        if ancestor.is_symlink() {
            return Err(unsupported("profile_symlink"));
        }
    }
    let mut missing = vec![];
    let mut cursor = path;
    while !cursor.exists() {
        missing.push(cursor.file_name().ok_or_else(invalid)?.to_owned());
        cursor = cursor.parent().ok_or_else(invalid)?;
    }
    let mut result = cursor.canonicalize().map_err(unsupported)?;
    for part in missing.into_iter().rev() {
        result.push(part);
    }
    path_text(&result)?;
    Ok(result)
}
fn close_file(file: File) -> LocalResult<()> {
    #[cfg(unix)]
    {
        if unsafe { libc::close(file.into_raw_fd()) } != 0 {
            return Err("profile_io_close".into());
        }
    }
    #[cfg(not(unix))]
    {
        drop(file);
    }
    Ok(())
}
fn no_follow(options: &mut OpenOptions) {
    #[cfg(unix)]
    {
        options.custom_flags(libc::O_NOFOLLOW | libc::O_CLOEXEC);
    }
}
fn read_material(path: &Path, name: &str) -> LocalResult<Material> {
    use sha2::{Digest, Sha256};
    let before = std::fs::symlink_metadata(path).map_err(unsupported)?;
    if !before.is_file() || before.file_type().is_symlink() || stat(&before).links != 1 {
        return Err(unsupported("profile_file_type"));
    }
    let mut options = OpenOptions::new();
    options.read(true);
    no_follow(&mut options);
    let mut file = options.open(path).map_err(unsupported)?;
    let read = (|| {
        let actual = file.metadata().map_err(unsupported)?;
        if stat(&before) != stat(&actual) {
            return Err(unsupported("profile_changed"));
        }
        let mut sha = Sha256::new();
        let mut buffer = [0u8; 65536];
        let mut header = vec![];
        let mut small = vec![];
        let auxiliary = [CREDENTIAL, SENTINEL, STAGING].contains(&name);
        if auxiliary && actual.len() > if name == SENTINEL { 8192 } else { 32768 } {
            return Err(invalid());
        }
        loop {
            let n = file.read(&mut buffer).map_err(unsupported)?;
            if n == 0 {
                break;
            }
            sha.update(&buffer[..n]);
            if name.ends_with(".sqlite") && header.len() < 100 {
                header.extend_from_slice(&buffer[..n.min(100 - header.len())]);
            }
            if auxiliary {
                small.extend_from_slice(&buffer[..n]);
            }
        }
        if stat(&file.metadata().map_err(unsupported)?) != stat(&actual) {
            return Err(unsupported("profile_changed"));
        }
        Ok(Material {
            name: name.into(),
            stat: stat(&actual),
            sha: format!("sha256:{:x}", sha.finalize()),
            header,
            small,
        })
    })();
    let closed = close_file(file);
    let material = read?;
    closed?;
    Ok(material)
}
/// 所有原始DB/journal FD在返回前checked-close；调用方之后才可创建SQLite连接。
pub(super) fn capture(dir: &Path) -> LocalResult<Snapshot> {
    let store = canonical(dir)?;
    let profile = canonical(store.parent().ok_or_else(invalid)?)?;
    let directory = |p: &Path| -> LocalResult<Option<std::fs::Metadata>> {
        match std::fs::symlink_metadata(p) {
            Ok(m) if m.is_dir() && !m.file_type().is_symlink() => Ok(Some(m)),
            Ok(_) => Err(unsupported("profile_directory")),
            Err(e) if e.kind() == std::io::ErrorKind::NotFound => Ok(None),
            Err(e) => Err(unsupported(e)),
        }
    };
    let pm = directory(&profile)?;
    let sm = directory(&store)?;
    let mut snap = Snapshot {
        profile,
        store,
        profile_identity: pm.as_ref().map(|m| stat(m).identity),
        store_identity: sm.as_ref().map(|m| stat(m).identity),
        store_mode: sm.as_ref().map(|m| stat(m).mode).unwrap_or(0),
        files: vec![],
    };
    for name in [
        "config.sqlite",
        "config.sqlite-journal",
        "config.sqlite-wal",
        "config.sqlite-shm",
        "runtime.sqlite",
        "runtime.sqlite-journal",
        "runtime.sqlite-wal",
        "runtime.sqlite-shm",
        CREDENTIAL,
        SENTINEL,
        STAGING,
    ] {
        let path = snap.store.join(name);
        if path.exists() || path.is_symlink() {
            snap.files.push(read_material(&path, name)?);
        }
    }
    Ok(snap)
}
fn reject_incomplete(s: &Snapshot) -> LocalResult<()> {
    if s.get(SENTINEL).is_some() || s.get(STAGING).is_some() {
        return Err("profile_initialization_incomplete".into());
    }
    if s.files
        .iter()
        .any(|m| m.name.ends_with("-wal") || m.name.ends_with("-shm"))
    {
        return Err(unsupported("unexpected_wal_material"));
    }
    Ok(())
}
pub(super) fn cold_materials(s: &Snapshot) -> LocalResult<()> {
    reject_incomplete(s)?;
    if s.files
        .iter()
        .filter(|m| m.name.ends_with("-journal"))
        .count()
        > 1
    {
        return Err("profile_recovery_rejected".into());
    }
    for m in &s.files {
        if m.stat.links != 1 {
            return Err(unsupported("profile_hardlink"));
        }
        if m.name.ends_with(".sqlite")
            && (m.header.len() != 100
                || &m.header[..16] != b"SQLite format 3\0"
                || m.header[18] != 1
                || m.header[19] != 1)
        {
            return Err(unsupported("unsupported_database_header"));
        }
    }
    Ok(())
}
fn bind(c: &Contract, s: &Snapshot) -> LocalResult<()> {
    if s.profile_identity.as_ref() != Some(&c.profile_identity)
        || s.store_identity.as_ref() != Some(&c.store_identity)
        || s.store_mode != 0o700
    {
        return Err(invalid());
    }
    for expected in &c.stores {
        let file = s.get(&expected.file_name).ok_or_else(invalid)?;
        let h = &file.header;
        if file.stat.identity != expected.file_identity
            || file.stat.links != 1
            || h.len() != 100
            || &h[..16] != b"SQLite format 3\0"
            || h[16..18] != [16, 0]
            || h[18] != 1
            || h[19] != 1
            || u32::from_be_bytes(h[60..64].try_into().unwrap()) != expected.schema_version
            || u32::from_be_bytes(h[68..72].try_into().unwrap()) as i64 != expected.application_id
        {
            return Err(invalid());
        }
    }
    let credential = s.get(CREDENTIAL).ok_or_else(invalid)?;
    if credential.stat.links != 1 || credential.stat.mode != 0o600 {
        return Err(invalid());
    }
    Ok(())
}
pub(super) fn checkpoint(stage: &str, dir: &Path) -> LocalResult<()> {
    #[cfg(all(test, unix))]
    {
        super::profile_contract_tests::checkpoint(stage, dir)?;
    }
    let _ = (stage, dir);
    Ok(())
}
fn sync_dir(dir: &Path) -> LocalResult<()> {
    checkpoint("directory_sync", dir)?;
    let mut options = OpenOptions::new();
    options.read(true);
    no_follow(&mut options);
    #[cfg(unix)]
    {
        options.custom_flags(libc::O_NOFOLLOW | libc::O_DIRECTORY | libc::O_CLOEXEC);
    }
    let file = options.open(dir).map_err(|_| "profile_io_sync")?;
    let synced = file.sync_all().map_err(|_| "profile_io_sync");
    let closed = close_file(file);
    synced?;
    closed
}
fn create_sync(path: &Path, bytes: &[u8]) -> LocalResult<()> {
    let dir = path.parent().ok_or_else(invalid)?;
    let mut options = OpenOptions::new();
    options.write(true).create_new(true);
    no_follow(&mut options);
    #[cfg(unix)]
    {
        options.mode(0o600);
    }
    let mut file = options.open(path).map_err(|_| "profile_install_conflict")?;
    let written: LocalResult<()> = (|| {
        file.write_all(bytes).map_err(|_| "profile_io_write")?;
        checkpoint("file_sync", dir)?;
        file.sync_all().map_err(|_| "profile_io_sync")?;
        Ok(())
    })();
    let closed = close_file(file);
    written?;
    closed?;
    checkpoint("file_close", dir)?;
    sync_dir(dir)
}
#[cfg(unix)]
fn initialize(dir: &Path) -> LocalResult<(Snapshot, Contract)> {
    std::fs::create_dir_all(dir).map_err(|_| "profile_io")?;
    std::fs::set_permissions(dir, std::fs::Permissions::from_mode(0o700))
        .map_err(|_| "profile_io")?;
    let snapshot = capture(dir)?;
    super::capacity::physical_budget(&snapshot)?;
    let marker = Initializing {
        format_version: 1,
        init_id: id(),
        canonical_store_dir: path_text(&snapshot.store)?.into(),
        created_at: business_time::now(),
        phase: "initializing".into(),
    };
    create_sync(
        &dir.join(SENTINEL),
        &serde_json::to_vec(&marker).map_err(|_| invalid())?,
    )?;
    checkpoint("sentinel_durable", dir)?;
    create_sync(&dir.join("config.sqlite"), &[])?;
    create_sync(&dir.join("runtime.sqlite"), &[])?;
    checkpoint("database_files_durable", dir)?;
    super::initialize_pair(dir)?;
    checkpoint("database_commits_closed", dir)?;
    for role in ["config", "runtime"] {
        let mut options = OpenOptions::new();
        options.read(true);
        no_follow(&mut options);
        let f = options
            .open(dir.join(format!("{role}.sqlite")))
            .map_err(|_| "profile_io")?;
        let synced = f.sync_all().map_err(|_| "profile_io_sync");
        let closed = close_file(f);
        synced?;
        closed?;
    }
    sync_dir(dir)?;
    let snapshot = capture(dir)?;
    let instance = super::inspect_sql(dir)
        .map_err(super::ProbeFailure::message)?
        .ok_or_else(invalid)?;
    super::schema::full_check(dir, &instance)?;
    checkpoint("initial_ro_checked", dir)?;
    if capture(dir)? != snapshot {
        return Err(unsupported("profile_changed"));
    }
    let stores = [
        ("config", schema::CONFIG_APP, 2, schema::config_sql()),
        ("runtime", schema::RUNTIME_APP, 3, schema::runtime_v3_sql()),
    ]
    .into_iter()
    .map(|(role, app, v, ddl)| {
        Ok(StoreContract {
            role: role.into(),
            file_name: format!("{role}.sqlite"),
            application_id: app,
            schema_version: v,
            schema_fingerprint: schema::fingerprint(&ddl)?,
            file_identity: snapshot
                .get(&format!("{role}.sqlite"))
                .ok_or_else(invalid)?
                .stat
                .identity
                .clone(),
        })
    })
    .collect::<LocalResult<Vec<_>>>()?;
    let contract = Contract {
        contract: "daa-profile-recovery/v1".into(),
        init_id: marker.init_id,
        instance_id: instance,
        created_at: marker.created_at,
        time_profile: business_time::TIME_PROFILE.into(),
        identity_profile: "unix-dev-ino/v1".into(),
        canonical_profile_dir: path_text(&snapshot.profile)?.into(),
        canonical_store_dir: path_text(&snapshot.store)?.into(),
        profile_identity: snapshot.profile_identity.clone().ok_or_else(invalid)?,
        store_identity: snapshot.store_identity.clone().ok_or_else(invalid)?,
        page_size: 4096,
        journal_mode: "delete".into(),
        stores,
    };
    let raw = encode(&contract)?;
    create_sync(&dir.join(STAGING), &raw)?;
    super::capacity::auxiliary_bytes(dir)?;
    let staged = read_material(&dir.join(STAGING), STAGING)?;
    checkpoint("staging_durable", dir)?;
    std::fs::hard_link(dir.join(STAGING), dir.join(CREDENTIAL))
        .map_err(|_| "profile_install_conflict")?;
    sync_dir(dir)?;
    super::capacity::auxiliary_bytes(dir)?;
    checkpoint("credential_installed", dir)?;
    std::fs::remove_file(dir.join(STAGING)).map_err(|_| "profile_io")?;
    sync_dir(dir)?;
    checkpoint("staging_removed", dir)?;
    std::fs::remove_file(dir.join(SENTINEL)).map_err(|_| "profile_io")?;
    sync_dir(dir)?;
    let installed = capture(dir)?;
    cold_materials(&installed)?;
    bind(&contract, &installed)?;
    let credential = installed.get(CREDENTIAL).ok_or_else(invalid)?;
    if credential.small != raw || credential.stat.identity != staged.stat.identity {
        return Err(unsupported("profile_changed"));
    }
    for name in ["config.sqlite", "runtime.sqlite"] {
        if installed.get(name) != snapshot.get(name) {
            return Err(unsupported("profile_changed"));
        }
    }
    checkpoint("sentinel_removed", dir)?;
    Ok((installed, contract))
}
fn native_once(dir: &Path, role: &'static str) -> LocalResult<()> {
    tracing::info!(
        event = "profile_recovery_started",
        process = "daa-local",
        resource = role,
        result = "native_attempt"
    );
    let c = rusqlite::Connection::open_with_flags(
        dir.join(format!("{role}.sqlite")),
        rusqlite::OpenFlags::SQLITE_OPEN_READ_WRITE | rusqlite::OpenFlags::SQLITE_OPEN_NO_MUTEX,
    )
    .map_err(|_| "profile_recovery_write_possible")?;
    let result: LocalResult<()> = (|| {
        c.busy_timeout(std::time::Duration::from_millis(1000))
            .map_err(|_| "profile_recovery_write_possible")?;
        c.query_row::<u32, _, _>("PRAGMA schema_version", [], |r| r.get(0))
            .map_err(|_| "profile_recovery_write_possible")?;
        Ok(())
    })();
    let closed = c.close().map_err(|_| "profile_recovery_write_possible");
    result?;
    Ok(closed?)
}
/// 原生回滚仅允许对应库/journal变化，其余已见材料仍绑定原候选，不重分类sealed。
fn verify_native_baseline(
    before: &Snapshot,
    after: &Snapshot,
    role: &str,
    contract: &Contract,
) -> LocalResult<()> {
    let database = format!("{role}.sqlite");
    let journal = format!("{database}-journal");
    if before.profile != after.profile
        || before.store != after.store
        || before.profile_identity != after.profile_identity
        || before.store_identity != after.store_identity
        || before.store_mode != after.store_mode
    {
        return Err(unsupported("profile_changed"));
    }
    let unchanged = |s: &Snapshot| {
        s.files
            .iter()
            .filter(|m| m.name != database && m.name != journal)
            .cloned()
            .collect::<Vec<_>>()
    };
    if unchanged(before) != unchanged(after) {
        return Err(unsupported("profile_changed"));
    }
    cold_materials(after)?;
    bind(contract, after)
}
/// 唯一准入工厂：返回的原ProfileLock必须随Stores保持到双库关闭，测试也不例外。
pub(super) fn admit(dir: &Path) -> LocalResult<super::LockedProfile> {
    let canonical_store = canonical(dir)?;
    let dir = canonical_store.as_path();
    let claim = super::ProcessClaim::new(&canonical(dir.parent().ok_or_else(invalid)?)?)?;
    if [SENTINEL, STAGING]
        .iter()
        .any(|name| std::fs::symlink_metadata(dir.join(name)).is_ok())
    {
        return Err("profile_initialization_incomplete".into());
    }
    let before = capture(dir)?;
    cold_materials(&before)?;
    let mut credential = before
        .get(CREDENTIAL)
        .map(|m| decode(&m.small, &before.profile, &before.store))
        .transpose()?;
    #[cfg(not(unix))]
    if credential.is_some() {
        return Err("profile_identity_unsupported".into());
    }
    if let Some(c) = &credential {
        bind(c, &before)?;
    }
    let probe = super::inspect_sql(dir);
    let failed_role = match &probe {
        Err(super::ProbeFailure::Sqlite(role, error))
            if credential.is_some() && rollback_error(error) =>
        {
            Some(*role)
        }
        _ => None,
    };
    if probe.is_err() && failed_role.is_none() {
        return Err(probe.unwrap_err().message());
    }
    if capture(dir)? != before {
        return Err(unsupported("profile_changed"));
    }
    checkpoint("before_lock", dir)?;
    let lock = crate::infrastructure::local_profile_lock::ProfileLock::acquire(&before.profile)?;
    if canonical(&lock.profile)? != before.profile || capture(dir)? != before {
        return Err(unsupported("profile_changed"));
    }
    claim.refresh()?;
    checkpoint("locked", dir)?;
    let mut recovered = false;
    let mut expected = before.clone();
    if let Some(role) = failed_role {
        let c = credential.as_ref().ok_or_else(invalid)?;
        let journals = before
            .files
            .iter()
            .filter(|m| m.name.ends_with("-journal"))
            .collect::<Vec<_>>();
        if journals.len() != 1
            || journals[0].name != format!("{role}.sqlite-journal")
            || journals[0].stat.links != 1
        {
            return Err("profile_recovery_rejected".into());
        }
        let companion = super::inspect_one(
            dir,
            if role == "config" {
                "runtime"
            } else {
                "config"
            },
        )
        .map_err(super::ProbeFailure::message)?;
        if companion.0 != c.instance_id {
            return Err(invalid());
        }
        super::capacity::physical_budget(&before)?;
        checkpoint("before_native", dir)?;
        if capture(dir)? != before {
            return Err(unsupported("profile_changed"));
        }
        if let Err(e) = native_once(dir, role) {
            tracing::error!(
                event = "profile_recovery_write_possible",
                process = "daa-local",
                resource = "profile",
                result = "rejected"
            );
            return Err(e);
        }
        recovered = true;
    } else if probe.as_ref().map(|v| v.is_none()).unwrap_or(false) {
        if capture(dir)? != before {
            return Err(unsupported("profile_changed"));
        }
        #[cfg(unix)]
        {
            let (initialized, contract) = initialize(dir)?;
            expected = initialized;
            credential = Some(contract);
        }
        #[cfg(not(unix))]
        {
            std::fs::create_dir_all(dir).map_err(|_| "profile_io")?;
            for name in ["config.sqlite", "runtime.sqlite"] {
                let f = OpenOptions::new()
                    .write(true)
                    .create_new(true)
                    .open(dir.join(name))
                    .map_err(|_| "profile_io")?;
                close_file(f)?;
            }
            super::initialize_pair(dir)?;
            expected = capture(dir)?;
        }
    }
    let checked = (|| {
        if recovered {
            checkpoint("native_closed", dir)?;
            let native = capture(dir)?;
            verify_native_baseline(
                &before,
                &native,
                failed_role.ok_or_else(invalid)?,
                credential.as_ref().ok_or_else(invalid)?,
            )?;
            expected = native;
            checkpoint("after_native", dir)?;
        }
        let baseline = capture(dir)?;
        if baseline != expected {
            return Err(unsupported("profile_changed"));
        }
        cold_materials(&baseline)?;
        let instance = super::inspect_sql(dir)
            .map_err(super::ProbeFailure::message)?
            .ok_or_else(invalid)?;
        // 全检义务来自本次preflight/初始化的原凭据，绝不按当前marker重新决定。
        if let Some(c) = credential.as_ref() {
            bind(c, &baseline)?;
            if c.instance_id != instance {
                return Err(invalid());
            }
            schema::full_check(dir, &instance)?;
        }
        // native后的新基线是显式建立的；sealed cold也执行同一完整后检，不能只认metadata。
        let post = capture(dir)?;
        if post != baseline {
            return Err(unsupported("profile_changed"));
        }
        checkpoint("after_ro", dir)?;
        if capture(dir)? != post {
            return Err(unsupported("profile_changed"));
        }
        Ok(())
    })();
    if checked.is_err() {
        tracing::error!(
            event = "profile_recovery_business_admission_failed",
            process = "daa-local",
            resource = "profile",
            result = "rejected",
            recovery_write_completed = recovered
        );
        return Err(if recovered {
            "profile_recovery_business_admission_failed"
        } else {
            "profile_contract_business_admission_failed"
        }
        .into());
    }
    if recovered {
        tracing::info!(
            event = "profile_recovery_completed",
            process = "daa-local",
            resource = "profile",
            result = "admitted"
        );
    }
    Ok(super::LockedProfile {
        _os: lock,
        _process: claim,
    })
}

/// 本地结构沿用serde原递归边界；不套provider depth20/decimal规范限制，但拒绝重复键/尾随/BOM。
pub(super) fn local_json(raw: &str, max: usize) -> LocalResult<Value> {
    struct Unique;
    impl<'de> serde::Deserialize<'de> for Unique {
        fn deserialize<D: serde::Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
            struct Check;
            impl<'de> serde::de::Visitor<'de> for Check {
                type Value = Unique;
                fn expecting(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
                    f.write_str("strict local JSON")
                }
                fn visit_map<A: serde::de::MapAccess<'de>>(
                    self,
                    mut map: A,
                ) -> Result<Unique, A::Error> {
                    let mut keys = std::collections::BTreeSet::new();
                    while let Some(key) = map.next_key::<String>()? {
                        if !keys.insert(key) {
                            return Err(serde::de::Error::custom("duplicate key"));
                        }
                        map.next_value::<Unique>()?;
                    }
                    Ok(Unique)
                }
                fn visit_seq<A: serde::de::SeqAccess<'de>>(
                    self,
                    mut seq: A,
                ) -> Result<Unique, A::Error> {
                    while seq.next_element::<Unique>()?.is_some() {}
                    Ok(Unique)
                }
                fn visit_str<E: serde::de::Error>(self, _: &str) -> Result<Unique, E> {
                    Ok(Unique)
                }
                fn visit_bool<E: serde::de::Error>(self, _: bool) -> Result<Unique, E> {
                    Ok(Unique)
                }
                fn visit_i64<E: serde::de::Error>(self, _: i64) -> Result<Unique, E> {
                    Ok(Unique)
                }
                fn visit_u64<E: serde::de::Error>(self, _: u64) -> Result<Unique, E> {
                    Ok(Unique)
                }
                fn visit_f64<E: serde::de::Error>(self, _: f64) -> Result<Unique, E> {
                    Ok(Unique)
                }
                fn visit_unit<E: serde::de::Error>(self) -> Result<Unique, E> {
                    Ok(Unique)
                }
            }
            d.deserialize_any(Check)
        }
    }
    if raw.len() > max {
        return Err("profile_ledger_invalid".into());
    }
    let mut d = serde_json::Deserializer::from_str(raw);
    <Unique as serde::Deserialize>::deserialize(&mut d).map_err(|_| "profile_ledger_invalid")?;
    d.end().map_err(|_| "profile_ledger_invalid")?;
    serde_json::from_str(raw).map_err(|_| "profile_ledger_invalid".into())
}

#[cfg(test)]
#[derive(Debug, PartialEq, Eq)]
pub(crate) struct ProfilePreflight(Snapshot);

#[cfg(test)]
pub(crate) fn preflight(dir: &Path) -> LocalResult<ProfilePreflight> {
    let _claim = super::ProcessClaim::new(&canonical(
        dir.parent().ok_or("profile_absolute_required")?,
    )?)?;
    let before = capture(dir)?;
    cold_materials(&before)?;
    super::inspect_sql(dir).map_err(super::ProbeFailure::message)?;
    if capture(dir)? != before {
        return Err(unsupported("profile_changed"));
    }
    Ok(ProfilePreflight(before))
}
#[cfg(test)]
impl ProfilePreflight {
    pub(crate) fn recheck(&self, dir: &Path) -> LocalResult<()> {
        if &preflight(dir)? != self {
            return Err(unsupported("profile_changed"));
        }
        Ok(())
    }
}
