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

impl ConfigStore {
    /// 读取同一 SQLite 读事务所见的配置与最新快照。
    pub fn with_http_snapshots(
        &mut self,
        keys: impl FnOnce(&ConfigurationDocument) -> Vec<String>,
    ) -> Result<
        (
            ConfigurationSnapshot,
            Vec<crate::contracts::http_mapping::SourceSnapshot>,
        ),
        String,
    > {
        let transaction = self.connection.transaction().map_err(db_error)?;
        let config = read(&transaction)?;
        let keys = keys(&config.document);
        let mut snapshots = Vec::new();
        if !keys.is_empty() && has_http_snapshots(&transaction)? {
            use rusqlite::OptionalExtension;
            let mut statement = transaction
                .prepare(
                    "SELECT definition_key, snapshot FROM http_source_latest WHERE source_key=?1",
                )
                .map_err(db_error)?;
            let mut rows = std::collections::BTreeMap::new();
            for source in &config.document.http_sources {
                if let Some(key) = source["sourceKey"].as_str() {
                    rows.insert(key, source);
                }
            }
            for key in keys {
                let Some(definition) = rows.get(key.as_str()) else {
                    continue;
                };
                let row: Option<(String, String)> = statement
                    .query_row([&key], |row| Ok((row.get(0)?, row.get(1)?)))
                    .optional()
                    .map_err(db_error)?;
                if let Some((stored_definition, snapshot)) = row {
                    let fingerprint =
                        crate::domain::http_mapping::source_definition_key(definition);
                    if stored_definition == fingerprint {
                        snapshots.push(
                            serde_json::from_str(&snapshot)
                                .map_err(|_| "SMA_HTTP_SNAPSHOT_INVALID")?,
                        );
                    }
                }
            }
        }
        transaction.commit().map_err(db_error)?;
        Ok((config, snapshots))
    }

    pub fn publish_http_snapshot(
        &mut self,
        definition: &serde_json::Value,
        collected_at: String,
        points: Vec<crate::contracts::http_mapping::PointReading>,
    ) -> Result<crate::contracts::http_mapping::SourceSnapshot, String> {
        use crate::contracts::http_mapping::SourceSnapshot;
        use rusqlite::OptionalExtension;

        let key = definition["sourceKey"]
            .as_str()
            .ok_or("SMA_HTTP_SOURCE_INVALID")?;
        let transaction = self
            .connection
            .transaction_with_behavior(TransactionBehavior::Immediate)
            .map_err(db_error)?;
        let config = read(&transaction)?;
        if !config
            .document
            .http_sources
            .iter()
            .any(|source| source == definition)
        {
            return Err("SMA_HTTP_SOURCE_CONFIGURATION_CHANGED".into());
        }
        transaction
            .execute_batch(
                "CREATE TABLE IF NOT EXISTS http_source_latest (
               source_key TEXT PRIMARY KEY, definition_key TEXT NOT NULL,
               version INTEGER NOT NULL CHECK (version > 0), snapshot TEXT NOT NULL
             );",
            )
            .map_err(db_error)?;
        let previous: Option<u64> = transaction
            .query_row(
                "SELECT version FROM http_source_latest WHERE source_key=?1",
                [key],
                |row| row.get(0),
            )
            .optional()
            .map_err(db_error)?;
        let version = previous
            .unwrap_or_default()
            .checked_add(1)
            .ok_or("SMA_HTTP_VERSION_EXHAUSTED")?;
        let snapshot = SourceSnapshot {
            source_key: key.into(),
            version,
            collected_at,
            points,
        };
        let data = serde_json::to_string(&snapshot).map_err(|_| "SMA_HTTP_SNAPSHOT_INVALID")?;
        transaction.execute(
            "INSERT INTO http_source_latest VALUES(?1,?2,?3,?4)
             ON CONFLICT(source_key) DO UPDATE SET
                definition_key=excluded.definition_key, version=excluded.version, snapshot=excluded.snapshot",
            params![key, crate::domain::http_mapping::source_definition_key(definition), version, data],
        ).map_err(db_error)?;
        transaction.commit().map_err(db_error)?;
        Ok(snapshot)
    }
}

fn has_http_snapshots(connection: &Connection) -> Result<bool, String> {
    connection.query_row(
        "SELECT EXISTS(SELECT 1 FROM sqlite_master WHERE type='table' AND name='http_source_latest')",
        [],
        |row| row.get(0),
    ).map_err(db_error)
}
