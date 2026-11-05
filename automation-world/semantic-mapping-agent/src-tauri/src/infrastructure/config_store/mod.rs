//! SMA独立SQLite schema v1：singleton完整配置、短事务CAS、损坏与未知schema拒绝。
use crate::contracts::local_configuration::*;
use rusqlite::{params, Connection, TransactionBehavior};
use std::{path::Path, time::Duration};
pub struct ConfigStore {
    connection: Connection,
}
fn db_error(error: rusqlite::Error) -> String {
    let code = match &error {
        rusqlite::Error::SqliteFailure(e, _)
            if matches!(
                e.code,
                rusqlite::ErrorCode::DatabaseBusy | rusqlite::ErrorCode::DatabaseLocked
            ) =>
        {
            "SMA_CONFIGURATION_BUSY"
        }
        _ => "SMA_CONFIGURATION_STORAGE_FAILED",
    };
    tracing::warn!(
        event = "sma_configuration_storage",
        result = "failed",
        error_code = code
    );
    code.into()
}
impl ConfigStore {
    pub fn open(path: &Path) -> Result<Self, String> {
        if !path.is_absolute() {
            return Err("SMA_CONFIGURATION_PROFILE_INVALID".into());
        }
        let existing = path.exists();
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent).map_err(|_| "SMA_CONFIGURATION_PROFILE_UNAVAILABLE")?;
        }
        let mut connection = Connection::open(path).map_err(db_error)?;
        connection
            .busy_timeout(Duration::from_millis(150))
            .map_err(db_error)?;
        if !existing {
            let tx = connection
                .transaction_with_behavior(TransactionBehavior::Immediate)
                .map_err(db_error)?;
            tx.execute_batch("CREATE TABLE configuration (singleton INTEGER PRIMARY KEY CHECK(singleton=1), schema_version INTEGER NOT NULL, revision INTEGER NOT NULL, document TEXT NOT NULL, updated_at TEXT NOT NULL); PRAGMA user_version=1;").map_err(db_error)?;
            let document = serde_json::to_string(&ConfigurationDocument::default())
                .map_err(|_| "SMA_CONFIGURATION_INVALID")?;
            tx.execute(
                "INSERT INTO configuration VALUES(1,1,0,?1,?2)",
                params![document, crate::domain::runtime::business_now_string()],
            )
            .map_err(db_error)?;
            tx.commit().map_err(db_error)?;
        }
        let store = Self { connection };
        let version: u32 = store
            .connection
            .query_row("PRAGMA user_version", [], |row| row.get(0))
            .map_err(db_error)?;
        if version != 1 {
            return Err("SMA_CONFIGURATION_SCHEMA_UNSUPPORTED".into());
        }
        let snapshot = store.load()?;
        crate::domain::local_configuration::validate(&snapshot.document)?;
        tracing::info!(
            event = "sma_configuration_open",
            revision = snapshot.revision,
            result = "opened"
        );
        Ok(store)
    }
    pub fn load(&self) -> Result<ConfigurationSnapshot, String> {
        read(&self.connection)
    }
    pub fn update<F>(
        &mut self,
        expected: u64,
        transform: F,
    ) -> Result<ConfigurationSnapshot, String>
    where
        F: FnOnce(&ConfigurationDocument) -> Result<ConfigurationDocument, String>,
    {
        let tx = self
            .connection
            .transaction_with_behavior(TransactionBehavior::Immediate)
            .map_err(db_error)?;
        let old = read(&tx)?;
        if old.revision != expected {
            return Err("SMA_CONFIGURATION_CONFLICT".into());
        }
        let next = transform(&old.document)?;
        crate::domain::local_configuration::validate(&next)?;
        if next == old.document {
            return Ok(old);
        }
        let revision = old
            .revision
            .checked_add(1)
            .ok_or("SMA_CONFIGURATION_REVISION_EXHAUSTED")?;
        let document = serde_json::to_string(&next).map_err(|_| "SMA_CONFIGURATION_INVALID")?;
        let updated_at = crate::domain::runtime::business_now_string();
        let count = tx.execute("UPDATE configuration SET revision=?1, document=?2, updated_at=?3 WHERE singleton=1 AND revision=?4", params![revision, document, updated_at, expected]).map_err(db_error)?;
        if count != 1 {
            return Err("SMA_CONFIGURATION_CONFLICT".into());
        }
        tx.commit().map_err(db_error)?;
        Ok(ConfigurationSnapshot {
            schema_version: 1,
            revision,
            updated_at,
            document: next,
        })
    }
}
fn read(connection: &Connection) -> Result<ConfigurationSnapshot, String> {
    let (version, revision, document, updated_at): (u32,u64,String,String) = connection.query_row("SELECT schema_version,revision,document,updated_at FROM configuration WHERE singleton=1", [], |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?))).map_err(db_error)?;
    if version != 1 {
        return Err("SMA_CONFIGURATION_SCHEMA_UNSUPPORTED".into());
    }
    let document = serde_json::from_str(&document).map_err(|_| "SMA_CONFIGURATION_INVALID")?;
    Ok(ConfigurationSnapshot {
        schema_version: version,
        revision,
        updated_at,
        document,
    })
}
