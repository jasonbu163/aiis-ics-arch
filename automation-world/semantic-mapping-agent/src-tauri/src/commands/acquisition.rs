//! 现有采集 API 手工回环的 Tauri IPC 入口。
use crate::{
    contracts::{acquisition::LoopbackConfig, local_configuration::ConfigurationSnapshot},
    infrastructure::acquisition::Failure,
    services::{
        acquisition::{self, AcquisitionSession, PreviewView},
        local_configuration::LocalConfigurationService,
    },
};
use serde_json::Value;
use tauri::State;

#[tauri::command]
pub fn save_acquisition_loopback(
    state: State<'_, LocalConfigurationService>,
    expected_revision: u64,
    config: LoopbackConfig,
) -> Result<ConfigurationSnapshot, String> {
    state.save_acquisition_loopback(expected_revision, config)
}

#[tauri::command]
pub async fn acquisition_options(
    state: State<'_, LocalConfigurationService>,
) -> Result<Value, String> {
    acquisition::options(&state.load()?).await.map_err(render)
}

#[tauri::command]
pub async fn acquisition_latest(
    state: State<'_, LocalConfigurationService>,
    material_key: String,
    plc_id: String,
    db_number: u16,
    point_ids: Vec<String>,
) -> Result<Value, String> {
    acquisition::latest(
        &state.load()?,
        &material_key,
        &plc_id,
        db_number,
        &point_ids,
    )
    .await
    .map_err(render)
}

#[tauri::command]
pub async fn acquisition_history(
    state: State<'_, LocalConfigurationService>,
    material_key: String,
    plc_id: String,
    db_number: u16,
    from: String,
    to: String,
    page: u32,
) -> Result<Value, String> {
    acquisition::history(
        &state.load()?,
        &material_key,
        &plc_id,
        db_number,
        &from,
        &to,
        page,
    )
    .await
    .map_err(render)
}

#[tauri::command]
pub async fn acquisition_sample(
    state: State<'_, LocalConfigurationService>,
    material_key: String,
    history_id: String,
    plc_id: String,
    db_number: u16,
) -> Result<Value, String> {
    acquisition::sample(
        &state.load()?,
        &material_key,
        &history_id,
        &plc_id,
        db_number,
    )
    .await
    .map_err(render)
}

#[tauri::command]
pub async fn acquisition_preview(
    state: State<'_, LocalConfigurationService>,
    session: State<'_, AcquisitionSession>,
    history_id: String,
    source_seq: String,
    expected_revision: u64,
) -> Result<PreviewView, String> {
    acquisition::preview(
        &session,
        &state,
        &history_id,
        &source_seq,
        expected_revision,
    )
    .await
    .map_err(render)
}

#[tauri::command]
pub async fn acquisition_test_push(
    state: State<'_, LocalConfigurationService>,
    session: State<'_, AcquisitionSession>,
    preview_id: String,
) -> Result<Value, String> {
    acquisition::push(&session, &state, &preview_id)
        .await
        .map_err(render)
}

#[tauri::command]
pub async fn acquisition_readback(
    state: State<'_, LocalConfigurationService>,
    session: State<'_, AcquisitionSession>,
    preview_id: String,
) -> Result<Value, String> {
    acquisition::readback(&session, &state, &preview_id)
        .await
        .map_err(render)
}

#[tauri::command]
pub fn acquisition_forget_preview(session: State<'_, AcquisitionSession>) -> Result<(), String> {
    session.invalidate().map_err(render)
}

fn render(error: Failure) -> String {
    let code = if error.unknown {
        format!("SMA_ACQUISITION_RESULT_UNKNOWN:{}", error.code)
    } else {
        error.code
    };
    match error.status {
        Some(status) => format!("{code} ({status})"),
        None => code,
    }
}
