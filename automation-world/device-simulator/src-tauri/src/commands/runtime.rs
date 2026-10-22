//! 正常快照/控制/typed写入/单close，所有入口复用唯一Rust runtime。
use super::*;
#[tauri::command]
pub async fn ds_get_bootstrap(s: State<'_, Desktop>) -> Result<Reply, String> {
    let bootstrap = s.bootstrap.clone();
    Ok(execute(
        s.runtime.clone(),
        false,
        "ds_get_bootstrap",
        None,
        move |_| runtime_queries::value(&bootstrap),
    )
    .await)
}
#[tauri::command]
pub async fn ds_get_runtime_snapshot(
    s: State<'_, Desktop>,
    request: dto::SnapshotQuery,
) -> Result<Reply, String> {
    Ok(execute(
        s.runtime.clone(),
        false,
        "ds_get_runtime_snapshot",
        None,
        move |a| runtime_queries::snapshot(a, request),
    )
    .await)
}
#[tauri::command]
pub async fn ds_control_instance(
    s: State<'_, Desktop>,
    request: dto::Operation<dto::ControlIntent>,
) -> Result<Reply, String> {
    Ok(operation(
        s.runtime.clone(),
        request,
        true,
        "ds_control_instance",
        runtime_queries::control,
    )
    .await)
}
#[tauri::command]
pub async fn ds_write_point(
    s: State<'_, Desktop>,
    request: dto::Operation<dto::WriteIntent>,
) -> Result<Reply, String> {
    Ok(operation(
        s.runtime.clone(),
        request,
        true,
        "ds_write_point",
        runtime_queries::write,
    )
    .await)
}
#[tauri::command]
pub async fn ds_close_connection(
    s: State<'_, Desktop>,
    request: dto::Operation<dto::CloseIntent>,
) -> Result<Reply, String> {
    Ok(operation(
        s.runtime.clone(),
        request,
        true,
        "ds_close_connection",
        runtime_queries::close_connection,
    )
    .await)
}
