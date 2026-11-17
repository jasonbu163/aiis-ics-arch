//! 原生目录选择与逐 PLC 导出薄桥：前端只传短期票据，不传文件系统路径。
use super::*;
use ds_runtime::services::catalog_export::{self, PreviewIntent, RevisionIntent, TokenIntent};
use tauri_plugin_dialog::DialogExt;

#[tauri::command]
pub async fn ds_catalog_revision(
    s: State<'_, Desktop>,
    request: dto::Operation<RevisionIntent>,
) -> Result<Reply, String> {
    Ok(operation(
        s.runtime.clone(),
        request,
        false,
        "ds_catalog_revision",
        catalog_export::inspect,
    )
    .await)
}
#[tauri::command]
pub async fn ds_catalog_preview(
    s: State<'_, Desktop>,
    request: dto::Operation<PreviewIntent>,
) -> Result<Reply, String> {
    Ok(operation(
        s.runtime.clone(),
        request,
        false,
        "ds_catalog_preview",
        catalog_export::preview,
    )
    .await)
}
#[tauri::command]
pub async fn ds_catalog_choose_directory(
    host: tauri::AppHandle,
    s: State<'_, Desktop>,
    request: dto::Operation<TokenIntent>,
) -> Result<Reply, String> {
    Ok(operation(
        s.runtime.clone(),
        request,
        false,
        "ds_catalog_choose_directory",
        move |app, intent| {
            let Some(selected) = host.dialog().file().blocking_pick_folder() else {
                return runtime_queries::value("cancelled");
            };
            let path = selected.into_path().map_err(|_| "catalog_directory")?;
            catalog_export::choose_directory(app, &intent.token, &path)
        },
    )
    .await)
}
#[tauri::command]
pub async fn ds_catalog_commit(
    s: State<'_, Desktop>,
    request: dto::Operation<TokenIntent>,
) -> Result<Reply, String> {
    Ok(operation(
        s.runtime.clone(),
        request,
        true,
        "ds_catalog_commit",
        catalog_export::commit,
    )
    .await)
}
#[tauri::command]
pub async fn ds_catalog_cancel(
    s: State<'_, Desktop>,
    request: dto::Operation<TokenIntent>,
) -> Result<Reply, String> {
    Ok(operation(
        s.runtime.clone(),
        request,
        false,
        "ds_catalog_cancel",
        catalog_export::cancel,
    )
    .await)
}
