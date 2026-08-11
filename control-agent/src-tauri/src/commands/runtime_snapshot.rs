//! File Path: /control-agent/src-tauri/src/commands/runtime_snapshot.rs
//! Description: Tauri runtime snapshot command adapter
//! Main Features:
//!   - Exposes the read-only runtime snapshot to the Vue console
//!   - Delegates runtime assembly to the service layer
//!   - Keeps Tauri command code thin

use crate::domain::runtime::RuntimeSnapshot;
use crate::services::runtime_snapshot::build_runtime_snapshot;

#[tauri::command]
pub(crate) fn get_runtime_snapshot() -> RuntimeSnapshot {
    build_runtime_snapshot()
}
