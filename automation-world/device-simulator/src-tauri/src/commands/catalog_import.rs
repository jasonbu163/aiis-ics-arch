//! 原生文件选择与目录导入薄桥；前端不能提交文件系统路径。
use super::*;
use ds_runtime::services::catalog_import::{self, CancelIntent, ConfirmIntent, PreviewIntent};
use tauri_plugin_dialog::DialogExt;
#[derive(serde::Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ChooseIntent {}
#[tauri::command]
pub async fn ds_catalog_import_choose(
    host: tauri::AppHandle,
    s: State<'_, Desktop>,
    request: dto::Operation<ChooseIntent>,
) -> Result<Reply, String> {
    Ok(operation(
        s.runtime.clone(),
        request,
        false,
        "ds_catalog_import_choose",
        move |app, _| {
            let Some(file) = host
                .dialog()
                .file()
                .add_filter("JSON", &["json"])
                .blocking_pick_file()
            else {
                return runtime_queries::value("cancelled");
            };
            let path = file.into_path().map_err(|_| "catalog_file_unavailable")?;
            catalog_import::choose(app, &path)
        },
    )
    .await)
}
#[tauri::command]
pub async fn ds_catalog_import_preview(
    s: State<'_, Desktop>,
    request: dto::Operation<PreviewIntent>,
) -> Result<Reply, String> {
    Ok(operation(
        s.runtime.clone(),
        request,
        false,
        "ds_catalog_import_preview",
        |app, p| runtime_queries::value(catalog_import::preview(app, p)?),
    )
    .await)
}
#[tauri::command]
pub async fn ds_catalog_import_confirm(
    s: State<'_, Desktop>,
    request: dto::Operation<ConfirmIntent>,
) -> Result<Reply, String> {
    Ok(operation(
        s.runtime.clone(),
        request,
        true,
        "ds_catalog_import_confirm",
        |app, p| runtime_queries::value(catalog_import::confirm(app, p)?),
    )
    .await)
}
#[tauri::command]
pub async fn ds_catalog_import_cancel(
    s: State<'_, Desktop>,
    request: dto::Operation<CancelIntent>,
) -> Result<Reply, String> {
    Ok(operation(
        s.runtime.clone(),
        request,
        false,
        "ds_catalog_import_cancel",
        catalog_import::cancel,
    )
    .await)
}
