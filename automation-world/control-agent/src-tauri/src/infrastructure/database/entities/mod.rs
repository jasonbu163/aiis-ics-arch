//! File Path: /control-agent/src-tauri/src/infrastructure/database/entities/mod.rs
//! Description: SeaORM entity registry for backend-owned PLC snapshot tables
//! Main Features:
//!   - Groups collector state, raw snapshot and latest snapshot entities
//!   - Keeps generated-style table models out of services and commands
//!   - Preserves backend/Alembic as the schema owner

pub(crate) mod monitor_collector_state;
pub(crate) mod plc_db_block_latest_snapshot;
pub(crate) mod plc_db_block_raw_snapshot;
