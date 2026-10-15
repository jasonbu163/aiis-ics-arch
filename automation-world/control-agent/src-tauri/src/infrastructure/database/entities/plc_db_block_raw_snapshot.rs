//! File Path: /control-agent/src-tauri/src/infrastructure/database/entities/plc_db_block_raw_snapshot.rs
//! Description: SeaORM entity for plc_db_block_raw_snapshots
//! Main Features:
//!   - Mirrors backend-owned PLC DB block raw snapshot schema
//!   - Supports Control Agent PLC fact-layer writes
//!   - Keeps table metadata aligned with backend/Alembic migrations

use sea_orm::entity::prelude::*;

#[derive(Clone, Debug, PartialEq, DeriveEntityModel)]
#[sea_orm(table_name = "plc_db_block_raw_snapshots")]
pub struct Model {
    #[sea_orm(primary_key)]
    pub id: i32,
    pub plc_key: String,
    pub device_id: i32,
    pub db_number: i32,
    pub group_name: String,
    pub contract_version: String,
    pub collected_at: DateTime,
    pub driver: String,
    pub quality: String,
    pub read_duration_ms: i32,
    pub raw_bytes: Option<Vec<u8>>,
    pub decoded_payload: Json,
    pub unsupported_payload: Option<Json>,
    pub error_message: Option<String>,
    pub created_at: DateTime,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {}

impl ActiveModelBehavior for ActiveModel {}
