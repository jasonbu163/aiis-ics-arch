//! File Path: /automation-world/semantic-mapping-agent/src-tauri/src/commands/runtimes/mod.rs
//! Description: Thin adapters for HTTP Mapping runtime.
//! Main Features:
//!   - Exposes the saved HTTP Mapping lifecycle
//!   - Keeps Mapping commands free of SQL/Profile input, scheduling, and transaction logic

use crate::domain::mapping_runtime::ApiFirstMappingRuntimeStartRequest;
use crate::domain::runtime::RuntimeSnapshot;
use crate::services::mapping_runtime;

#[tauri::command]
pub async fn start_api_first_mapping_runtime(
    configuration: tauri::State<
        '_,
        crate::services::local_configuration::LocalConfigurationService,
    >,
    state: tauri::State<'_, mapping_runtime::ApiFirstMappingRuntimeState>,
    request: ApiFirstMappingRuntimeStartRequest,
) -> Result<RuntimeSnapshot, String> {
    configuration.admit_execution()?;
    mapping_runtime::start_api_first_mapping_runtime(&state, request).await
}

#[tauri::command]
pub async fn pause_api_first_mapping_runtime(
    state: tauri::State<'_, mapping_runtime::ApiFirstMappingRuntimeState>,
) -> Result<RuntimeSnapshot, String> {
    mapping_runtime::pause_api_first_mapping_runtime(&state).await
}

#[tauri::command]
pub fn resume_api_first_mapping_runtime(
    configuration: tauri::State<
        '_,
        crate::services::local_configuration::LocalConfigurationService,
    >,
    state: tauri::State<'_, mapping_runtime::ApiFirstMappingRuntimeState>,
) -> Result<RuntimeSnapshot, String> {
    configuration.admit_execution()?;
    mapping_runtime::resume_api_first_mapping_runtime(&state)
}

#[tauri::command]
pub async fn stop_api_first_mapping_runtime(
    state: tauri::State<'_, mapping_runtime::ApiFirstMappingRuntimeState>,
) -> Result<RuntimeSnapshot, String> {
    mapping_runtime::stop_api_first_mapping_runtime(&state).await
}

#[tauri::command]
pub fn get_api_first_mapping_runtime(
    state: tauri::State<'_, mapping_runtime::ApiFirstMappingRuntimeState>,
) -> RuntimeSnapshot {
    state.0.snapshot()
}
