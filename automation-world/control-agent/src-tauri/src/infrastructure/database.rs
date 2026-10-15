//! File Path: /control-agent/src-tauri/src/infrastructure/database.rs
//! Description: Database infrastructure module registry
//! Main Features:
//!   - Exposes backend-owned PLC snapshot entities
//!   - Exposes SeaORM repositories for the PLC collection runtime

pub(crate) mod entities;
pub(crate) mod repositories;
