//! SMA HTTP 命令适配器：显式采集、独立调度及预览令牌确认。
use crate::{
    contracts::http_mapping::*,
    services::{
        http_mapping::{HttpMappingService, RuntimeStatus},
        http_scheduler::{SchedulerSide, SchedulerStatus},
    },
};
use serde_json::Value;
use std::collections::BTreeMap;
use tauri::State;

#[tauri::command]
pub(crate) async fn sma_test_source(
    state: State<'_, HttpMappingService>,
    source_key: String,
) -> Result<SourceTest, String> {
    crate::config::require_external_io()?;
    state.test_source(&source_key).await
}

#[tauri::command]
pub(crate) fn sma_latest_sources(
    state: State<'_, HttpMappingService>,
) -> Result<Vec<SourceState>, String> {
    state.latest()
}

#[tauri::command]
pub(crate) fn sma_preview_mapping(
    state: State<'_, HttpMappingService>,
    mapping_id: String,
    expected_revision: u64,
) -> Result<PostPreview, String> {
    state.preview_mapping(&mapping_id, expected_revision)
}

#[tauri::command]
pub(crate) fn sma_preview_target(
    state: State<'_, HttpMappingService>,
    target_api_id: String,
    expected_revision: u64,
    values: BTreeMap<String, Value>,
) -> Result<PostPreview, String> {
    state.preview_target(&target_api_id, expected_revision, values)
}

#[tauri::command]
pub(crate) async fn sma_confirm_post(
    state: State<'_, HttpMappingService>,
    token: String,
) -> Result<PostResult, String> {
    if let Err(error) = crate::config::require_external_io() {
        state.cancel_post(&token);
        return Err(error);
    }
    state.confirm_post(&token).await
}

#[tauri::command]
pub(crate) fn sma_cancel_post(state: State<'_, HttpMappingService>, token: String) {
    state.cancel_post(&token);
}

#[tauri::command]
pub(crate) async fn sma_start_runtime(
    state: State<'_, HttpMappingService>,
    side: SchedulerSide,
) -> Result<SchedulerStatus, String> {
    crate::config::require_external_io()?;
    state.start(side)
}

#[tauri::command]
pub(crate) fn sma_stop_runtime(
    state: State<'_, HttpMappingService>,
    side: SchedulerSide,
) -> SchedulerStatus {
    state.stop(side)
}

#[tauri::command]
pub(crate) fn sma_runtime_status(state: State<'_, HttpMappingService>) -> RuntimeStatus {
    state.status()
}
