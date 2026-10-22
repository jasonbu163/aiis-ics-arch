//! SQLite身份/初始化：未知库、半初始化、损坏和外键缺失一律保留并失败。
use super::{queries, Snapshot};
use crate::{
    domain::configuration::{hash_bytes, uuid, Workspace},
    infrastructure::profile_lock::ProfileLock,
};
use rusqlite::{params, Connection, OpenFlags};
pub const MIGRATION: &str = include_str!("migrations/0001_initial.sql");
pub fn open(lock: &ProfileLock) -> Result<Connection, String> {
    lock.check_capacity(0)?;
    let fresh = !lock.database.exists();
    if !fresh
        && std::fs::metadata(&lock.database)
            .map_err(|_| "storage_unavailable")?
            .len()
            == 0
    {
        return Err("storage_incomplete".into());
    }
    let mut c = Connection::open_with_flags(
        &lock.database,
        OpenFlags::SQLITE_OPEN_READ_WRITE
            | if fresh {
                OpenFlags::SQLITE_OPEN_CREATE
            } else {
                OpenFlags::empty()
            },
    )
    .map_err(|_| "storage_open")?;
    if c.is_readonly(rusqlite::DatabaseName::Main)
        .map_err(|_| "storage_open")?
    {
        return Err("storage_readonly".into());
    }
    c.busy_timeout(std::time::Duration::from_millis(1000))
        .map_err(|_| "storage_configuration")?;
    if !fresh {
        let app: i64 = c
            .pragma_query_value(None, "application_id", |r| r.get(0))
            .map_err(|_| "storage_identity")?;
        let version: i64 = c
            .pragma_query_value(None, "user_version", |r| r.get(0))
            .map_err(|_| "storage_identity")?;
        if app != 0x44535631 || version != 1 {
            return Err("storage_identity".into());
        }
        let mode: String = c
            .pragma_query_value(None, "journal_mode", |r| r.get(0))
            .map_err(|_| "storage_identity")?;
        if mode.to_lowercase() != "delete" {
            return Err("storage_journal_mode".into());
        }
    }
    c.execute_batch("PRAGMA page_size=4096; PRAGMA journal_mode=DELETE; PRAGMA synchronous=EXTRA; PRAGMA foreign_keys=ON; PRAGMA mmap_size=0; PRAGMA trusted_schema=OFF;").map_err(|_|"storage_configuration")?;
    let page_size: i64 = c
        .pragma_query_value(None, "page_size", |r| r.get(0))
        .map_err(|_| "storage_configuration")?;
    let version: String = c
        .query_row("SELECT sqlite_version()", [], |r| r.get(0))
        .map_err(|_| "storage_configuration")?;
    if page_size != 4096 || version != "3.46.0" {
        return Err("storage_configuration".into());
    }
    if fresh {
        let tx = c.transaction().map_err(|_| "storage_initialize")?;
        tx.execute_batch(MIGRATION)
            .map_err(|_| "storage_initialize")?;
        tx.execute(
            "INSERT INTO schema_migrations(version,migration_sha256) VALUES(1,?1)",
            [hash_bytes(MIGRATION.as_bytes())],
        )
        .map_err(|_| "storage_initialize")?;
        tx.execute("INSERT INTO workspace_metadata(singleton,profile_id,format_version) VALUES(1,?1,'ds-config-v1')",[uuid()]).map_err(|_|"storage_initialize")?;
        let payload = serde_json::to_vec(&Workspace::default()).unwrap();
        tx.execute("INSERT INTO configuration_draft(singleton,etag,canonical_payload,sha256) VALUES(1,?1,?2,?3)",params![uuid(),payload,hash_bytes(&payload)]).map_err(|_|"storage_initialize")?;
        tx.execute_batch("PRAGMA application_id=1146312241; PRAGMA user_version=1;")
            .map_err(|_| "storage_initialize")?;
        tx.commit().map_err(|_| "storage_initialize_unknown")?;
    }
    validate(&c)?;
    Ok(c)
}
fn validate(c: &Connection) -> Result<(), String> {
    let integrity: String = c
        .query_row("PRAGMA quick_check(1)", [], |r| r.get(0))
        .map_err(|_| "storage_corrupt")?;
    if integrity != "ok" {
        return Err("storage_corrupt".into());
    }
    let mut fk = c
        .prepare("PRAGMA foreign_key_check")
        .map_err(|_| "storage_reference")?;
    if fk
        .query([])
        .map_err(|_| "storage_reference")?
        .next()
        .map_err(|_| "storage_reference")?
        .is_some()
    {
        return Err("storage_reference".into());
    }
    let (id, format): (String, String) = c
        .query_row(
            "SELECT profile_id,format_version FROM workspace_metadata WHERE singleton=1",
            [],
            |r| Ok((r.get(0)?, r.get(1)?)),
        )
        .map_err(|_| "storage_identity")?;
    if uuid::Uuid::parse_str(&id).is_err() || format != "ds-config-v1" {
        return Err("storage_identity".into());
    }
    let migration: String = c
        .query_row(
            "SELECT migration_sha256 FROM schema_migrations WHERE version=1",
            [],
            |r| r.get(0),
        )
        .map_err(|_| "storage_identity")?;
    if migration != hash_bytes(MIGRATION.as_bytes()) {
        return Err("storage_schema".into());
    }
    let expected = Connection::open_in_memory().map_err(|_| "storage_schema")?;
    expected
        .execute_batch(MIGRATION)
        .map_err(|_| "storage_schema")?;
    fn objects(c: &Connection) -> Result<Vec<(String, String, String)>, String> {
        let mut q=c.prepare("SELECT type,name,coalesce(sql,'') FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' ORDER BY type,name").map_err(|_|"storage_schema")?;
        let rows = q
            .query_map([], |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?)))
            .map_err(|_| "storage_schema")?;
        rows.collect::<Result<Vec<_>, _>>()
            .map_err(|_| "storage_schema".into())
    }
    if objects(c)? != objects(&expected)? {
        return Err("storage_schema".into());
    }
    let Snapshot { workspace, .. } = queries::load(c)?;
    queries::validate_references(c, &workspace)?;
    for selected in queries::selections(c)? {
        let workspace = queries::revision(c, &selected.revision_id)?;
        let instance = workspace
            .instances
            .iter()
            .find(|i| i.id == selected.instance_id)
            .ok_or("storage_reference")?;
        if crate::domain::configuration::digest(instance) != selected.slice_sha256 {
            return Err("storage_reference".into());
        }
    }
    Ok(())
}
