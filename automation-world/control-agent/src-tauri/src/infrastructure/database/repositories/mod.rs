//! File Path: /control-agent/src-tauri/src/infrastructure/database/repositories/mod.rs
//! Description: SeaORM repositories for PLC collection database access
//! Main Features:
//!   - Creates SeaORM database connections from runtime configuration
//!   - Reads and writes backend-owned PLC snapshot tables
//!   - Keeps services independent from ORM implementation details

use std::time::Duration;

use sea_orm::{
    ActiveModelTrait, ColumnTrait, ConnectOptions, ConnectionTrait, Database, DatabaseConnection,
    DbBackend, EntityTrait, IntoActiveModel, PaginatorTrait, QueryFilter, QueryOrder, Set,
    Statement,
};

use crate::domain::plc_collection::{
    MonitorCollectorStateSnapshot, NewMonitorCollectorState, NewPlcDbBlockSnapshot,
    PlcLatestGroupSnapshot,
};

use super::entities::{
    monitor_collector_state, plc_db_block_latest_snapshot, plc_db_block_raw_snapshot,
};

pub(crate) struct PlcCollectionDatabaseStatusRows {
    pub(crate) collector_state: MonitorCollectorStateSnapshot,
    pub(crate) raw_snapshot_count: u32,
    pub(crate) latest_groups: Vec<PlcLatestGroupSnapshot>,
}

pub(crate) struct PlcCollectionDatabaseWriter {
    db: DatabaseConnection,
}

const DATABASE_NOW_ALIAS: &str = "ca_database_now";
const DATABASE_NOW_QUERY: &str = "SELECT NOW() AS ca_database_now";
const DATABASE_SYSTEM_TIME_ZONE_QUERY: &str = "SET time_zone = 'SYSTEM'";

pub(crate) async fn connect_sea_orm(
    database_url: &str,
    timeout_ms: u64,
) -> Result<DatabaseConnection, String> {
    let mut options = ConnectOptions::new(database_url.to_string());
    options
        .max_connections(1)
        .connect_timeout(Duration::from_millis(timeout_ms))
        .acquire_timeout(Duration::from_millis(timeout_ms));

    let db = Database::connect(options)
        .await
        .map_err(|error| format!("Failed to connect database through SeaORM: {error}"))?;

    db.execute(Statement::from_string(
        DbBackend::MySql,
        DATABASE_SYSTEM_TIME_ZONE_QUERY.to_string(),
    ))
    .await
    .map_err(|error| format!("Failed to use database system time zone: {error}"))?;

    Ok(db)
}

pub(crate) async fn database_now(
    db: &DatabaseConnection,
) -> Result<sea_orm::prelude::DateTime, String> {
    let row = db
        .query_one(Statement::from_string(
            DbBackend::MySql,
            DATABASE_NOW_QUERY.to_string(),
        ))
        .await
        .map_err(|error| format!("Failed to read database current time: {error}"))?
        .ok_or_else(|| "Database current time query returned no row".to_string())?;

    row.try_get("", DATABASE_NOW_ALIAS)
        .map_err(|error| format!("Failed to decode database current time: {error}"))
}

fn i32_to_u32(value: i32) -> u32 {
    value.max(0) as u32
}

fn date_time_text(value: Option<sea_orm::prelude::DateTime>) -> String {
    value
        .map(|date_time| date_time.format("%Y-%m-%d %H:%M:%S").to_string())
        .unwrap_or_default()
}

fn json_object_count(value: &serde_json::Value) -> u32 {
    value
        .as_object()
        .map(|object| object.len().min(u32::MAX as usize) as u32)
        .unwrap_or_default()
}

fn optional_json_object_count(value: &Option<serde_json::Value>) -> u32 {
    value.as_ref().map(json_object_count).unwrap_or_default()
}

fn empty_collector_state(collector_key: String) -> MonitorCollectorStateSnapshot {
    MonitorCollectorStateSnapshot {
        loaded: false,
        collector_key,
        status: "missing".to_string(),
        worker_id: String::new(),
        mode: String::new(),
        target_interval_ms: 0,
        started_at: String::new(),
        last_heartbeat_at: String::new(),
        last_sample_at: String::new(),
        sample_count: 0,
        failure_count: 0,
        last_collect_duration_ms: 0,
        last_write_duration_ms: 0,
        last_loop_delay_ms: 0,
        last_error: String::new(),
    }
}

fn collector_state_snapshot(
    state: Option<monitor_collector_state::Model>,
    collector_key: String,
) -> MonitorCollectorStateSnapshot {
    let Some(state) = state else {
        return empty_collector_state(collector_key);
    };

    MonitorCollectorStateSnapshot {
        loaded: true,
        collector_key: state.collector_key,
        status: state.status,
        worker_id: state.worker_id.unwrap_or_default(),
        mode: state.mode,
        target_interval_ms: i32_to_u32(state.target_interval_ms),
        started_at: date_time_text(state.started_at),
        last_heartbeat_at: date_time_text(state.last_heartbeat_at),
        last_sample_at: date_time_text(state.last_sample_at),
        sample_count: i32_to_u32(state.sample_count),
        failure_count: i32_to_u32(state.failure_count),
        last_collect_duration_ms: state
            .last_collect_duration_ms
            .map(i32_to_u32)
            .unwrap_or_default(),
        last_write_duration_ms: state
            .last_write_duration_ms
            .map(i32_to_u32)
            .unwrap_or_default(),
        last_loop_delay_ms: state.last_loop_delay_ms.map(i32_to_u32).unwrap_or_default(),
        last_error: state.last_error.unwrap_or_default(),
    }
}

fn latest_group_snapshot(row: plc_db_block_latest_snapshot::Model) -> PlcLatestGroupSnapshot {
    PlcLatestGroupSnapshot {
        plc_key: row.plc_key,
        db_number: row.db_number,
        group_name: row.group_name,
        quality: row.quality,
        collected_at: date_time_text(Some(row.collected_at)),
        raw_snapshot_id: row.raw_snapshot_id.map(i32_to_u32).unwrap_or_default(),
        decoded_count: json_object_count(&row.decoded_payload),
        unsupported_count: optional_json_object_count(&row.unsupported_payload),
        read_duration_ms: i32_to_u32(row.read_duration_ms),
        error_message: row.error_message.unwrap_or_default(),
    }
}

pub(crate) async fn read_monitor_collector_state(
    db: &DatabaseConnection,
    collector_key: &str,
) -> Result<Option<monitor_collector_state::Model>, String> {
    monitor_collector_state::Entity::find_by_id(collector_key.to_string())
        .one(db)
        .await
        .map_err(|error| format!("Failed to read monitor collector state: {error}"))
}

pub(crate) async fn count_plc_db_block_raw_snapshots(
    db: &DatabaseConnection,
) -> Result<u32, String> {
    let count = plc_db_block_raw_snapshot::Entity::find()
        .count(db)
        .await
        .map_err(|error| format!("Failed to count PLC DB block raw snapshots: {error}"))?;

    Ok(count.min(u32::MAX as u64) as u32)
}

pub(crate) async fn latest_plc_db_block_snapshots(
    db: &DatabaseConnection,
) -> Result<Vec<plc_db_block_latest_snapshot::Model>, String> {
    plc_db_block_latest_snapshot::Entity::find()
        .order_by_asc(plc_db_block_latest_snapshot::Column::DbNumber)
        .order_by_asc(plc_db_block_latest_snapshot::Column::GroupName)
        .all(db)
        .await
        .map_err(|error| format!("Failed to read PLC DB block latest snapshots: {error}"))
}

pub(crate) async fn read_plc_collection_database_status(
    database_url: &str,
    timeout_ms: u64,
    collector_key: &str,
) -> Result<PlcCollectionDatabaseStatusRows, String> {
    let db = connect_sea_orm(database_url, timeout_ms).await?;
    let collector_state = collector_state_snapshot(
        read_monitor_collector_state(&db, collector_key).await?,
        collector_key.to_string(),
    );
    let raw_snapshot_count = count_plc_db_block_raw_snapshots(&db).await?;
    let latest_groups = latest_plc_db_block_snapshots(&db)
        .await?
        .into_iter()
        .map(latest_group_snapshot)
        .collect::<Vec<_>>();

    Ok(PlcCollectionDatabaseStatusRows {
        collector_state,
        raw_snapshot_count,
        latest_groups,
    })
}

pub(crate) async fn write_plc_db_block_snapshot(
    db: &DatabaseConnection,
    snapshot: NewPlcDbBlockSnapshot,
) -> Result<i32, String> {
    let raw_model = plc_db_block_raw_snapshot::ActiveModel {
        plc_key: Set(snapshot.plc_key.clone()),
        device_id: Set(snapshot.device_id),
        db_number: Set(snapshot.db_number),
        group_name: Set(snapshot.group_name.clone()),
        contract_version: Set(snapshot.contract_version.clone()),
        collected_at: Set(snapshot.collected_at),
        driver: Set(snapshot.driver.clone()),
        quality: Set(snapshot.quality.clone()),
        read_duration_ms: Set(snapshot.read_duration_ms),
        raw_bytes: Set(snapshot.raw_bytes.clone()),
        decoded_payload: Set(snapshot.decoded_payload.clone()),
        unsupported_payload: Set(snapshot.unsupported_payload.clone()),
        error_message: Set(snapshot.error_message.clone()),
        ..Default::default()
    }
    .insert(db)
    .await
    .map_err(|error| format!("Failed to insert PLC DB block raw snapshot: {error}"))?;

    let latest = plc_db_block_latest_snapshot::Entity::find()
        .filter(plc_db_block_latest_snapshot::Column::PlcKey.eq(snapshot.plc_key.clone()))
        .filter(plc_db_block_latest_snapshot::Column::DbNumber.eq(snapshot.db_number))
        .filter(plc_db_block_latest_snapshot::Column::GroupName.eq(snapshot.group_name.clone()))
        .one(db)
        .await
        .map_err(|error| format!("Failed to find PLC DB block latest snapshot: {error}"))?;

    if let Some(latest_model) = latest {
        let mut active_model = latest_model.into_active_model();
        active_model.device_id = Set(snapshot.device_id);
        active_model.contract_version = Set(snapshot.contract_version);
        active_model.collected_at = Set(snapshot.collected_at);
        active_model.driver = Set(snapshot.driver);
        active_model.quality = Set(snapshot.quality);
        active_model.read_duration_ms = Set(snapshot.read_duration_ms);
        active_model.raw_snapshot_id = Set(Some(raw_model.id));
        active_model.decoded_payload = Set(snapshot.latest_decoded_payload);
        active_model.unsupported_payload = Set(snapshot.latest_unsupported_payload);
        active_model.error_message = Set(snapshot.error_message);
        active_model.updated_at = Set(snapshot.collected_at);

        active_model
            .update(db)
            .await
            .map_err(|error| format!("Failed to update PLC DB block latest snapshot: {error}"))?;
    } else {
        plc_db_block_latest_snapshot::ActiveModel {
            plc_key: Set(snapshot.plc_key),
            device_id: Set(snapshot.device_id),
            db_number: Set(snapshot.db_number),
            group_name: Set(snapshot.group_name),
            contract_version: Set(snapshot.contract_version),
            collected_at: Set(snapshot.collected_at),
            driver: Set(snapshot.driver),
            quality: Set(snapshot.quality),
            read_duration_ms: Set(snapshot.read_duration_ms),
            raw_snapshot_id: Set(Some(raw_model.id)),
            decoded_payload: Set(snapshot.latest_decoded_payload),
            unsupported_payload: Set(snapshot.latest_unsupported_payload),
            error_message: Set(snapshot.error_message),
            ..Default::default()
        }
        .insert(db)
        .await
        .map_err(|error| format!("Failed to insert PLC DB block latest snapshot: {error}"))?;
    }

    Ok(raw_model.id)
}

impl PlcCollectionDatabaseWriter {
    pub(crate) async fn connect(database_url: &str, timeout_ms: u64) -> Result<Self, String> {
        Ok(Self {
            db: connect_sea_orm(database_url, timeout_ms).await?,
        })
    }

    pub(crate) async fn database_now(&self) -> Result<sea_orm::prelude::DateTime, String> {
        database_now(&self.db).await
    }

    pub(crate) async fn write_snapshot(
        &self,
        snapshot: NewPlcDbBlockSnapshot,
    ) -> Result<i32, String> {
        write_plc_db_block_snapshot(&self.db, snapshot).await
    }

    pub(crate) async fn upsert_collector_state(
        &self,
        state: NewMonitorCollectorState,
    ) -> Result<(), String> {
        upsert_monitor_collector_state(&self.db, state).await
    }
}

pub(crate) async fn upsert_monitor_collector_state(
    db: &DatabaseConnection,
    state: NewMonitorCollectorState,
) -> Result<(), String> {
    let existing = monitor_collector_state::Entity::find_by_id(state.collector_key.clone())
        .one(db)
        .await
        .map_err(|error| format!("Failed to find monitor collector state: {error}"))?;

    if let Some(existing_model) = existing {
        let mut active_model = existing_model.into_active_model();
        let current_sample_count = active_model.sample_count.as_ref().to_owned();
        let current_failure_count = active_model.failure_count.as_ref().to_owned();

        active_model.status = Set(state.status);
        active_model.worker_id = Set(state.worker_id);
        active_model.mode = Set(state.mode);
        active_model.device_id = Set(state.device_id);
        active_model.target_interval_ms = Set(state.target_interval_ms);
        active_model.last_heartbeat_at = Set(Some(state.last_heartbeat_at));
        if state.last_sample_at.is_some() {
            active_model.last_sample_at = Set(state.last_sample_at);
        }
        active_model.sample_count = Set(if state.sample_succeeded {
            current_sample_count.saturating_add(1)
        } else {
            current_sample_count
        });
        active_model.failure_count =
            Set(current_failure_count.saturating_add(state.failure_count_increment));
        active_model.last_collect_duration_ms = Set(state.last_collect_duration_ms);
        active_model.last_write_duration_ms = Set(state.last_write_duration_ms);
        active_model.last_loop_delay_ms = Set(state.last_loop_delay_ms);
        active_model.last_error = Set(state.last_error);
        active_model.updated_at = Set(state.last_heartbeat_at);

        active_model
            .update(db)
            .await
            .map_err(|error| format!("Failed to update monitor collector state: {error}"))?;
    } else {
        monitor_collector_state::ActiveModel {
            collector_key: Set(state.collector_key),
            status: Set(state.status),
            worker_id: Set(state.worker_id),
            mode: Set(state.mode),
            device_id: Set(state.device_id),
            target_interval_ms: Set(state.target_interval_ms),
            started_at: Set(Some(state.last_heartbeat_at)),
            last_heartbeat_at: Set(Some(state.last_heartbeat_at)),
            last_sample_at: Set(state.last_sample_at),
            sample_count: Set(if state.sample_succeeded { 1 } else { 0 }),
            failure_count: Set(state.failure_count_increment),
            buffered_failure_count: Set(0),
            dropped_sample_count: Set(0),
            last_buffered_at: Set(None),
            last_replay_count: Set(0),
            last_collect_duration_ms: Set(state.last_collect_duration_ms),
            last_write_duration_ms: Set(state.last_write_duration_ms),
            last_loop_delay_ms: Set(state.last_loop_delay_ms),
            last_error: Set(state.last_error),
            ..Default::default()
        }
        .insert(db)
        .await
        .map_err(|error| format!("Failed to insert monitor collector state: {error}"))?;
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn database_now_query_uses_non_reserved_alias() {
        assert!(DATABASE_NOW_QUERY.contains(DATABASE_NOW_ALIAS));
        assert!(!DATABASE_NOW_QUERY.contains("current_time"));
    }

    #[test]
    fn database_connection_uses_database_system_time_zone() {
        assert_eq!(DATABASE_SYSTEM_TIME_ZONE_QUERY, "SET time_zone = 'SYSTEM'");
        assert!(!DATABASE_SYSTEM_TIME_ZONE_QUERY.contains("+08"));
        assert!(!DATABASE_SYSTEM_TIME_ZONE_QUERY.contains("Asia/Shanghai"));
    }
}
