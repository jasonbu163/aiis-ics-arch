//! 本地配置薄IPC：所有写入和纯预览委托同一Rust服务，不读取远端。
use crate::{
    contracts::local_configuration::*,
    services::{
        local_configuration::LocalConfigurationService,
        mapping_runtime::ApiFirstMappingRuntimeState,
    },
};
#[tauri::command]
pub fn load_local_configuration(
    state: tauri::State<'_, LocalConfigurationService>,
) -> Result<ConfigurationSnapshot, String> {
    state.load()
}
#[tauri::command]
pub fn change_local_configuration(
    state: tauri::State<'_, LocalConfigurationService>,
    runtime: tauri::State<'_, ApiFirstMappingRuntimeState>,
    expected_revision: u64,
    intent: ChangeIntent,
) -> Result<ConfigurationSnapshot, String> {
    state.change(expected_revision, intent, &runtime.0)
}
#[tauri::command]
pub fn preview_local_configuration(
    state: tauri::State<'_, LocalConfigurationService>,
    expected_revision: u64,
    intent: ChangeIntent,
) -> Result<ImportPreview, String> {
    state.preview(expected_revision, intent)
}
#[tauri::command]
pub fn apply_local_configuration(
    state: tauri::State<'_, LocalConfigurationService>,
    runtime: tauri::State<'_, ApiFirstMappingRuntimeState>,
    expected_revision: u64,
    intent: ChangeIntent,
    token: String,
    confirmed: bool,
) -> Result<ConfigurationSnapshot, String> {
    state.apply(expected_revision, intent, &token, confirmed, &runtime.0)
}
#[tauri::command]
pub fn export_local_configuration(
    state: tauri::State<'_, LocalConfigurationService>,
) -> Result<String, String> {
    state.export()
}
#[tauri::command]
pub fn preview_saved_local_mapping(
    state: tauri::State<'_, LocalConfigurationService>,
    mapping_id: String,
    expected_revision: u64,
) -> Result<serde_json::Value, String> {
    state.saved_preview(&mapping_id, expected_revision)
}
