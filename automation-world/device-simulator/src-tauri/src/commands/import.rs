//! 多源/布局/命名preview/confirm白名单意图，不接受前端生成的证明。
use super::*;
#[tauri::command]
pub async fn ds_preview_import(
    s: State<'_, Desktop>,
    request: dto::Operation<ds_runtime::services::source_import::ImportIntent>,
) -> Result<Reply, String> {
    Ok(operation(
        s.runtime.clone(),
        request,
        false,
        "ds_preview_import",
        |a, p| {
            runtime_queries::value(ds_runtime::services::source_import::preview(
                &a.configuration,
                p,
            )?)
        },
    )
    .await)
}
#[tauri::command]
pub async fn ds_preview_layout(
    s: State<'_, Desktop>,
    request: dto::Operation<ds_runtime::services::layout::LayoutIntent>,
) -> Result<Reply, String> {
    Ok(operation(
        s.runtime.clone(),
        request,
        false,
        "ds_preview_layout",
        |a, p| runtime_queries::value(ds_runtime::services::layout::preview(&a.configuration, p)?),
    )
    .await)
}
#[tauri::command]
pub async fn ds_preview_names(
    s: State<'_, Desktop>,
    request: dto::Operation<ds_runtime::services::naming::NamesIntent>,
) -> Result<Reply, String> {
    Ok(operation(
        s.runtime.clone(),
        request,
        false,
        "ds_preview_names",
        |a, p| runtime_queries::value(ds_runtime::services::naming::preview(&a.configuration, p)?),
    )
    .await)
}
macro_rules! confirm {
    ($name:ident,$kind:literal) => {
        #[tauri::command]
        pub async fn $name(
            s: State<'_, Desktop>,
            request: dto::Operation<dto::Confirmation>,
        ) -> Result<Reply, String> {
            Ok(operation(
                s.runtime.clone(),
                request,
                true,
                stringify!($name),
                |a, p| {
                    runtime_queries::value(a.configuration.confirm(
                        $kind,
                        &p.token,
                        &p.expected_etag,
                        &p.candidate_sha256,
                    )?)
                },
            )
            .await)
        }
    };
}
confirm!(ds_confirm_import, "import");
confirm!(ds_confirm_layout, "layout");
confirm!(ds_confirm_names, "names");
