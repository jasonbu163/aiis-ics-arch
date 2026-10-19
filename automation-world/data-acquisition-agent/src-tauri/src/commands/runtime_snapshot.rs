//! File Path: /automation-world/data-acquisition-agent/src-tauri/src/commands/runtime_snapshot.rs
//! Description: Tauri runtime snapshot command adapter
//! Main Features:
//!   - Exposes the read-only runtime snapshot to the Vue console
//!   - Delegates runtime assembly to the service layer
//!   - Keeps Tauri command code thin

use crate::domain::runtime::RuntimeSnapshot;
use crate::services::runtime_snapshot::build_runtime_snapshot;

#[tauri::command]
pub(crate) fn get_runtime_snapshot() -> Result<RuntimeSnapshot, String> {
    crate::config::local_bootstrap::legacy_guard()?;
    Ok(build_runtime_snapshot())
}
