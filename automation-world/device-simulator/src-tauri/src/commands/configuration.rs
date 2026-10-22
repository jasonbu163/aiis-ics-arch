//! 配置/保存/停机apply薄命令；所有证明和SQLite归共享Rust服务。
use super::*;
#[tauri::command]
pub async fn ds_get_configuration(
    s: State<'_, Desktop>,
    request: dto::ConfigurationQuery,
) -> Result<Reply, String> {
    Ok(execute(
        s.runtime.clone(),
        false,
        "ds_get_configuration",
        None,
        move |a| runtime_queries::configuration(a, request),
    )
    .await)
}
#[tauri::command]
pub async fn ds_save_configuration(
    s: State<'_, Desktop>,
    request: dto::Operation<ds_runtime::services::configuration::SaveIntent>,
) -> Result<Reply, String> {
    Ok(operation(
        s.runtime.clone(),
        request,
        true,
        "ds_save_configuration",
        runtime_queries::save,
    )
    .await)
}
#[tauri::command]
pub async fn ds_preview_apply(
    s: State<'_, Desktop>,
    request: dto::Operation<ds_runtime::services::apply::ApplyIntent>,
) -> Result<Reply, String> {
    Ok(operation(
        s.runtime.clone(),
        request,
        false,
        "ds_preview_apply",
        |a, p| runtime_queries::value(ds_runtime::services::apply::preview(a, p)?),
    )
    .await)
}
#[tauri::command]
pub async fn ds_apply_revision(
    s: State<'_, Desktop>,
    request: dto::Operation<ds_runtime::services::apply::ApplyConfirmation>,
) -> Result<Reply, String> {
    Ok(operation(
        s.runtime.clone(),
        request,
        true,
        "ds_apply_revision",
        ds_runtime::services::apply::confirm,
    )
    .await)
}
