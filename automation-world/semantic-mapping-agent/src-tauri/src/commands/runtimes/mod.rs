//! File Path: /automation-world/semantic-mapping-agent/src-tauri/src/commands/runtimes/mod.rs
//! Description: Thin adapters for Backend-HTTP Simulation, API-first Mapping, and direct-DB Projection runtimes.
//! Main Features:
//!   - Exposes separate lifecycles that can run simultaneously
//!   - Keeps Simulation and Mapping commands free of SQL/Profile input, scheduling, and transaction logic

use crate::domain::mapping_runtime::ApiFirstMappingRuntimeStartRequest;
use crate::domain::runtime::RuntimeSnapshot;
use crate::services::{mapping_runtime, simulation};

#[tauri::command]
pub async fn start_collection_fact_simulation_runtime(
    state: tauri::State<'_, simulation::CollectionFactSimulationRuntimeState>,
    request: simulation::model::CollectionSimulationHttpStartRequest,
) -> Result<RuntimeSnapshot, String> {
    crate::config::require_external_io()?;
    simulation::collection::start_http(&state, request).await
}

#[tauri::command]
pub async fn pause_collection_fact_simulation_runtime(
    state: tauri::State<'_, simulation::CollectionFactSimulationRuntimeState>,
) -> Result<RuntimeSnapshot, String> {
    simulation::collection::pause(&state).await
}

#[tauri::command]
pub fn resume_collection_fact_simulation_runtime(
    state: tauri::State<'_, simulation::CollectionFactSimulationRuntimeState>,
) -> Result<RuntimeSnapshot, String> {
    crate::config::require_external_io()?;
    simulation::collection::resume(&state)
}

#[tauri::command]
pub async fn stop_collection_fact_simulation_runtime(
    state: tauri::State<'_, simulation::CollectionFactSimulationRuntimeState>,
) -> Result<RuntimeSnapshot, String> {
    simulation::collection::stop(&state).await
}

#[tauri::command]
pub fn get_collection_fact_simulation_runtime(
    state: tauri::State<'_, simulation::CollectionFactSimulationRuntimeState>,
) -> RuntimeSnapshot {
    state.0.snapshot()
}

#[tauri::command]
pub async fn start_api_first_mapping_runtime(
    state: tauri::State<'_, mapping_runtime::ApiFirstMappingRuntimeState>,
    request: ApiFirstMappingRuntimeStartRequest,
) -> Result<RuntimeSnapshot, String> {
    crate::config::require_external_io()?;
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
    state: tauri::State<'_, mapping_runtime::ApiFirstMappingRuntimeState>,
) -> Result<RuntimeSnapshot, String> {
    crate::config::require_external_io()?;
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
