//! File Path: /control-agent/src-tauri/src/infrastructure/database/entities/monitor_collector_state.rs
//! Description: SeaORM entity for monitor_collector_states
//! Main Features:
//!   - Mirrors backend-owned collector state schema
//!   - Supports Control Agent PLC collector heartbeat and counters
//!   - Keeps runtime status metadata out of snapshot history tables

use sea_orm::entity::prelude::*;

#[derive(Clone, Debug, PartialEq, DeriveEntityModel)]
#[sea_orm(table_name = "monitor_collector_states")]
pub struct Model {
    #[sea_orm(primary_key, auto_increment = false)]
    pub collector_key: String,
    pub status: String,
    pub worker_id: Option<String>,
    pub mode: String,
    pub device_id: i32,
    pub target_interval_ms: i32,
    pub started_at: Option<DateTime>,
    pub last_heartbeat_at: Option<DateTime>,
    pub last_sample_at: Option<DateTime>,
    pub sample_count: i32,
    pub failure_count: i32,
    pub buffered_failure_count: i32,
    pub dropped_sample_count: i32,
    pub last_buffered_at: Option<DateTime>,
    pub last_replay_count: i32,
    pub last_collect_duration_ms: Option<i32>,
    pub last_write_duration_ms: Option<i32>,
    pub last_loop_delay_ms: Option<i32>,
    pub last_error: Option<String>,
    pub updated_at: DateTime,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {}

impl ActiveModelBehavior for ActiveModel {}
