//! Tauri薄命令与有界业务执行适配；观测记录真实IPC入口/回执，业务仍归共享Rust服务。
pub mod catalog_export;
pub mod catalog_import;
pub mod configuration;
pub mod import;
pub mod queries;
pub mod runtime;
use crate::app::Desktop;
use ds_runtime::{config::workspace as dto, services::queries as runtime_queries};
use tauri::State;
type Reply = dto::Response<ds_runtime::app::Snapshot>;
fn catalog_receipt(command: &str, result: &mut Reply) {
    // 逐文件结果可含已知成功与未知项；保留清单，同时不把总提交状态伪报成已知。
    if command == "ds_catalog_commit"
        && result.data.as_ref().is_some_and(|data| {
            data.get("rows")
                .and_then(|rows| rows.as_array())
                .is_some_and(|rows| {
                    rows.iter()
                        .any(|row| row.get("result").and_then(|v| v.as_str()) == Some("unknown"))
                })
        })
    {
        result.committed = None;
        result.receipt_state = "unknown".into();
    }
}
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
        let mut result = dto::Response::from_result(work(&runtime), committed);
        catalog_receipt(command, &mut result);
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

#[cfg(test)]
mod receipt_tests {
    use super::*;
    use serde::Serialize;
    #[derive(Serialize)]
    struct Row {
        result: &'static str,
    }
    #[derive(Serialize)]
    struct Data {
        rows: Vec<Row>,
        committed: Option<bool>,
    }
    #[test]
    fn catalog_receipt_retains_partial_rows_and_reports_unknown() {
        let data = runtime_queries::value(Data {
            rows: vec![Row { result: "written" }, Row { result: "unknown" }],
            committed: None,
        })
        .unwrap();
        let mut reply = dto::Response::from_result(Ok(data), true);
        catalog_receipt("ds_catalog_commit", &mut reply);
        assert_eq!(reply.committed, None);
        assert_eq!(reply.receipt_state, "unknown");
        assert_eq!(reply.data.unwrap()["rows"].as_array().unwrap().len(), 2);
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
