//! Tauri薄命令与有界业务执行适配；观测记录真实IPC入口/回执，业务仍归共享Rust服务。
pub mod configuration;
pub mod import;
pub mod queries;
pub mod runtime;
use crate::app::Desktop;
use ds_runtime::{config::workspace as dto, services::queries as runtime_queries};
use tauri::State;
type Reply = dto::Response<ds_runtime::app::Snapshot>;
async fn execute<F>(
    runtime: std::sync::Arc<ds_runtime::app::App>,
    committed: bool,
    command: &'static str,
    operation: Option<String>,
    work: F,
) -> Reply
where
    F: FnOnce(&ds_runtime::app::App) -> Result<ds_runtime::app::Snapshot, String> + Send + 'static,
{
    match tauri::async_runtime::spawn_blocking(move || {
        let mut event = ds_runtime::app::command_event(command);
        event["phase"] = "request".into();
        if let Some(id) = &operation {
            event["operationId"] = id.as_str().into();
        }
        runtime.events.put(event.clone());
        let result = dto::Response::from_result(work(&runtime), committed);
        event["phase"] = "response".into();
        event["result"] = result.result.as_str().into();
        event["committed"] = result.committed.into();
        event["errorCode"] = result.error_code.clone().into();
        event["receiptState"] = result.receipt_state.as_str().into();
        runtime.events.put(event);
        result
    })
    .await
    {
        Ok(result) => result,
        Err(_) => dto::Response::from_result(
            Err(if committed {
                "runtime_task_receipt_unknown"
            } else {
                "runtime_task_failed"
            }
            .into()),
            false,
        ),
    }
}
async fn operation<T, F>(
    runtime: std::sync::Arc<ds_runtime::app::App>,
    request: dto::Operation<T>,
    committed: bool,
    command: &'static str,
    work: F,
) -> Reply
where
    T: Send + 'static,
    F: FnOnce(&ds_runtime::app::App, T) -> Result<ds_runtime::app::Snapshot, String>
        + Send
        + 'static,
{
    execute(
        runtime,
        committed,
        command,
        Some(request.operation_id.clone()),
        move |a| {
            runtime_queries::mutation(a, &request.operation_id)?;
            work(a, request.payload)
        },
    )
    .await
}
