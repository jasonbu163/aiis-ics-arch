//! 逐 PLC 导出 IPC：原生目录选择只绑定短期预览令牌。
use super::local_acquisition::{failure, invoke, LocalFailure, LocalState};
use serde_json::{json, Value};
use tauri_plugin_dialog::DialogExt;

type IpcResult = Result<Value, LocalFailure>;
#[tauri::command]
pub(crate) async fn daa_catalog_export_inspect(
    state: tauri::State<'_, LocalState>,
    request: Value,
) -> IpcResult {
    invoke(state, "daa_catalog_export_inspect", request).await
}
#[tauri::command]
pub(crate) async fn daa_catalog_export_preview(
    state: tauri::State<'_, LocalState>,
    request: Value,
) -> IpcResult {
    invoke(state, "daa_catalog_export_preview", request).await
}
#[tauri::command]
pub(crate) async fn daa_catalog_export_commit(
    state: tauri::State<'_, LocalState>,
    request: Value,
) -> IpcResult {
    invoke(state, "daa_catalog_export_commit", request).await
}
#[tauri::command]
pub(crate) async fn daa_catalog_export_cancel(
    state: tauri::State<'_, LocalState>,
    request: Value,
) -> IpcResult {
    invoke(state, "daa_catalog_export_cancel", request).await
}
#[tauri::command]
pub(crate) async fn daa_catalog_export_directory(
    host: tauri::AppHandle,
    state: tauri::State<'_, LocalState>,
    request: Value,
) -> IpcResult {
    let engine = state.engine.clone().ok_or_else(|| LocalFailure {
        error_code: "wrong_runtime_mode".into(),
        current_etag: None,
        current_active_revision: None,
    })?;
    let request: crate::services::catalog_export::TokenRequest =
        serde_json::from_value(request).map_err(|_| failure(&engine, "invalid_request".into()))?;
    tauri::async_runtime::spawn_blocking(move || {
        engine
            .catalog_export_release_directory(&request.token)
            .map_err(|code| failure(&engine, code))?;
        let Some(selected) = host.dialog().file().blocking_pick_folder() else {
            engine
                .catalog_export_cancel(request)
                .map_err(|code| failure(&engine, code))?;
            return Ok(json!({"result":"cancelled"}));
        };
        let path = selected
            .into_path()
            .map_err(|_| failure(&engine, "catalog_directory".into()))?;
        engine
            .catalog_export_directory(&request.token, &path)
            .map_err(|code| failure(&engine, code))
    })
    .await
    .map_err(|_| LocalFailure {
        error_code: "local_operation_failed".into(),
        current_etag: None,
        current_active_revision: None,
    })?
}
