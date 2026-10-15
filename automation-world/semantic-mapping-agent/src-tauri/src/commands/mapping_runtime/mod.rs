//! File Path: /automation-world/semantic-mapping-agent/src-tauri/src/commands/mapping_runtime/mod.rs
//! Description: Thin Tauri adapters for saved Mapping manual runs and local runtime startup preferences.
//! Main Features:
//!   - Accepts only saved Mapping identity, observed row version, and saved Backend base URL intent
//!   - Delegates HTTP-only execution and app-open-only preference persistence to the service

use crate::config::runtime_startup::RuntimeStartupPreferences;
use crate::domain::mapping_runtime::MappingManualRunResult;
use crate::services::mapping_runtime;

#[tauri::command]
pub async fn run_mapping_manual_once(
    mapping_id: String,
    expected_row_version: String,
    backend_base_url: String,
) -> Result<MappingManualRunResult, String> {
    crate::config::require_external_io()?;
    mapping_runtime::run_mapping_manual_once(mapping_id, expected_row_version, backend_base_url)
        .await
}

#[tauri::command]
pub fn load_runtime_startup_preferences(
    app: tauri::AppHandle,
) -> Result<RuntimeStartupPreferences, String> {
    mapping_runtime::load_runtime_startup_preferences(&app)
}

#[tauri::command]
pub fn save_runtime_startup_preferences(
    app: tauri::AppHandle,
    preferences: RuntimeStartupPreferences,
) -> Result<(), String> {
    mapping_runtime::save_runtime_startup_preferences(&app, preferences)
}
