//! 有界日志薄适配，不接受SQL、路径或进程命令。
use super::*;
#[tauri::command]
pub async fn ds_query_logs(
    s: State<'_, Desktop>,
    request: dto::LogsQuery,
) -> Result<Reply, String> {
    Ok(
        execute(s.runtime.clone(), false, "ds_query_logs", None, move |a| {
            runtime_queries::logs(a, request)
        })
        .await,
    )
}
