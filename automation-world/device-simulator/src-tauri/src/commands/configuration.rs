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

#[tauri::command]
pub async fn ds_preview_publish_revision(
    s: State<'_, Desktop>,
    request: dto::Operation<ds_runtime::services::versions::VersionIntent>,
) -> Result<Reply, String> {
    Ok(operation(
        s.runtime.clone(),
        request,
        false,
        "ds_preview_publish_revision",
        |a, p| runtime_queries::value(ds_runtime::services::versions::preview_publish(a, p)?),
    )
    .await)
}
#[tauri::command]
pub async fn ds_publish_revision(
    s: State<'_, Desktop>,
    request: dto::Operation<ds_runtime::services::versions::VersionConfirmation>,
) -> Result<Reply, String> {
    Ok(operation(
        s.runtime.clone(),
        request,
        true,
        "ds_publish_revision",
        |a, p| {
            runtime_queries::value(ds_runtime::services::versions::confirm(
                a,
                "publish_revision",
                p,
            )?)
        },
    )
    .await)
}
#[tauri::command]
pub async fn ds_preview_delete_revision(
    s: State<'_, Desktop>,
    request: dto::Operation<ds_runtime::services::versions::DeleteIntent>,
) -> Result<Reply, String> {
    Ok(operation(
        s.runtime.clone(),
        request,
        false,
        "ds_preview_delete_revision",
        |a, p| runtime_queries::value(ds_runtime::services::versions::preview_delete(a, p)?),
    )
    .await)
}
#[tauri::command]
pub async fn ds_delete_revisions(
    s: State<'_, Desktop>,
    request: dto::Operation<ds_runtime::services::versions::VersionConfirmation>,
) -> Result<Reply, String> {
    Ok(operation(
        s.runtime.clone(),
        request,
        true,
        "ds_delete_revisions",
        |a, p| {
            runtime_queries::value(ds_runtime::services::versions::confirm(
                a,
                "delete_revisions",
                p,
            )?)
        },
    )
    .await)
}
#[tauri::command]
pub async fn ds_cancel_preview(
    s: State<'_, Desktop>,
    request: dto::Operation<ds_runtime::services::versions::CancelPreview>,
) -> Result<Reply, String> {
    Ok(operation(
        s.runtime.clone(),
        request,
        false,
        "ds_cancel_preview",
        ds_runtime::services::versions::cancel_preview,
    )
    .await)
}
