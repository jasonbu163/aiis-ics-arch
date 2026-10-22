//! 本地IPC v1薄adapter：有名白名单命令、camelCase DTO、线程卸载；无SQL/驱动/调度实现。
use crate::{
    config::local_bootstrap::Bootstrap,
    domain::{local_configuration::*, local_runtime::HistoryQuery},
    services::local_supervisor::LocalEngine,
};
use serde::Deserialize;
use serde_json::{json, Value};
use std::sync::Arc;
pub(crate) struct LocalState {
    pub bootstrap: Bootstrap,
    pub engine: Option<Arc<LocalEngine>>,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct Save {
    draft: Configuration,
    expected_etag: String,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct Offsets {
    db_id: String,
    expected_etag: Option<String>,
    point_ids: Option<Vec<String>>,
    layout_digest: Option<String>,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct Activate {
    expected_etag: String,
    expected_active_revision: Option<String>,
    #[serde(default)]
    rollback: bool,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct Control {
    plc_ids: Vec<String>,
    desired: bool,
    expected_active_revision: String,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct Diagnostic {
    plc_id: String,
    point_id: Option<String>,
    expected_active_revision: String,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct Sample {
    sample_id: String,
    #[serde(default)]
    context_offset: usize,
}
#[derive(Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct Logs {
    cursor: i64,
    limit: u32,
}
fn parse<T: serde::de::DeserializeOwned>(v: Value) -> LocalResult<T> {
    serde_json::from_value(v).map_err(|_| "invalid_request".into())
}
fn value<T: serde::Serialize>(v: T) -> LocalResult<Value> {
    serde_json::to_value(v).map_err(|_| "encoding_failed".into())
}
pub(crate) fn dispatch(
    engine: Arc<LocalEngine>,
    command: &str,
    request: Value,
) -> LocalResult<Value> {
    if serde_json::to_vec(&request)
        .map_err(|_| "invalid_request")?
        .len()
        > 16 * 1024 * 1024
    {
        return Err("request_limits".into());
    }
    match command {
        "daa_get_yaml_migration" => value(engine.yaml_migration()?),
        "daa_retry_yaml_migration" => {
            #[derive(Deserialize)]
            #[serde(rename_all = "camelCase", deny_unknown_fields)]
            struct Retry {
                expected_etag: String,
                expected_attempt_id: String,
            }
            let r: Retry = parse(request)?;
            value(engine.retry_yaml(r.expected_etag, r.expected_attempt_id)?)
        }
        "daa_get_configuration" => {
            engine.invalidate_previews();
            value(engine.configuration()?)
        }
        "daa_preview_point_names" => value(engine.preview_point_names(parse(request)?)?),
        "daa_confirm_point_names" => value(engine.confirm_point_names(parse(request)?)?),
        "daa_save_draft" => {
            let r: Save = parse(request)?;
            value(engine.save(r.draft, r.expected_etag)?)
        }
        "daa_import_sources" => {
            let r: crate::domain::source_import::ImportRequest = parse(request)?;
            if r.stage.as_deref() == Some("identify") {
                if r.confirm {
                    return Err("invalid_request".into());
                }
                value(engine.identify_sources(&r)?)
            } else {
                value(engine.import_selected(r)?)
            }
        }
        "daa_preview_offsets" => {
            let r: Offsets = parse(request)?;
            value(engine.offsets_at(r.db_id, r.expected_etag)?)
        }
        "daa_confirm_offsets" => {
            let r: Offsets = parse(request)?;
            value(engine.confirm_offsets_at(
                r.db_id,
                r.point_ids.ok_or("invalid_request")?,
                r.expected_etag.ok_or("invalid_request")?,
                r.layout_digest,
            )?)
        }
        "daa_activate_configuration" => {
            let r: Activate = parse(request)?;
            engine.activate(r.expected_etag, r.expected_active_revision, r.rollback)
        }
        "daa_set_connection" | "daa_set_collection" => {
            let r: Control = parse(request)?;
            engine.request(
                r.plc_ids,
                if command == "daa_set_connection" {
                    "connection"
                } else {
                    "collection"
                },
                r.desired,
                &r.expected_active_revision,
                None,
            )
        }
        "daa_test_connection" | "daa_diagnose_point" => {
            let r: Diagnostic = parse(request)?;
            engine.request(
                vec![r.plc_id],
                if command == "daa_test_connection" {
                    "test"
                } else {
                    "diagnose"
                },
                false,
                &r.expected_active_revision,
                r.point_id,
            )
        }
        "daa_get_local_snapshot" => engine.snapshot(),
        "daa_list_history" => engine.history(parse::<HistoryQuery>(request)?),
        "daa_get_sample" => {
            let r: Sample = parse(request)?;
            engine.sample_chunk(r.sample_id, r.context_offset)
        }
        "daa_get_logs" => {
            let r: Logs = parse(request)?;
            engine.logs(r.cursor, r.limit)
        }
        _ => Err("unknown_local_command".into()),
    }
}
#[tauri::command]
pub(crate) fn daa_get_bootstrap(state: tauri::State<'_, LocalState>) -> Value {
    json!({"schemaVersion":1,"mode":state.bootstrap.mode,"origin":if state.bootstrap.validation{"fixture"}else{"native"},"localStorage":state.engine.is_some(),"readAllowed":state.bootstrap.read_allowed,"uploadAvailable":false,"version":env!("CARGO_PKG_VERSION"),"identity":"com.aiis.aw.dataacquisitionagent","ignoredKeys":state.bootstrap.ignored_keys})
}
#[derive(serde::Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct LocalFailure {
    pub error_code: String,
    pub current_etag: Option<String>,
    pub current_active_revision: Option<String>,
}
pub(crate) fn failure(engine: &LocalEngine, code: String) -> LocalFailure {
    let current = if [
        "draft_conflict",
        "activation_conflict",
        "revision_conflict",
        "import_preview_conflict",
    ]
    .contains(&code.as_str())
    {
        engine.configuration().ok()
    } else {
        None
    };
    LocalFailure {
        error_code: code,
        current_etag: current.as_ref().map(|v| v.etag.clone()),
        current_active_revision: current.and_then(|v| v.active),
    }
}
type IpcResult = Result<Value, LocalFailure>;
async fn invoke(
    state: tauri::State<'_, LocalState>,
    command: &'static str,
    request: Value,
) -> IpcResult {
    let engine = state.engine.clone().ok_or_else(|| LocalFailure {
        error_code: "wrong_runtime_mode".into(),
        current_etag: None,
        current_active_revision: None,
    })?;
    tauri::async_runtime::spawn_blocking(move || {
        dispatch(engine.clone(), command, request).map_err(|code| failure(&engine, code))
    })
    .await
    .map_err(|_| LocalFailure {
        error_code: "local_operation_failed".into(),
        current_etag: None,
        current_active_revision: None,
    })?
}
#[tauri::command]
pub(crate) async fn daa_get_configuration(
    state: tauri::State<'_, LocalState>,
    request: Value,
) -> IpcResult {
    invoke(state, "daa_get_configuration", request).await
}
#[tauri::command]
pub(crate) async fn daa_save_draft(
    state: tauri::State<'_, LocalState>,
    request: Value,
) -> IpcResult {
    invoke(state, "daa_save_draft", request).await
}
#[tauri::command]
pub(crate) async fn daa_import_sources(
    state: tauri::State<'_, LocalState>,
    request: Value,
) -> IpcResult {
    invoke(state, "daa_import_sources", request).await
}
#[tauri::command]
pub(crate) async fn daa_preview_offsets(
    state: tauri::State<'_, LocalState>,
    request: Value,
) -> IpcResult {
    invoke(state, "daa_preview_offsets", request).await
}
#[tauri::command]
pub(crate) async fn daa_confirm_offsets(
    state: tauri::State<'_, LocalState>,
    request: Value,
) -> IpcResult {
    invoke(state, "daa_confirm_offsets", request).await
}
#[tauri::command]
pub(crate) async fn daa_activate_configuration(
    state: tauri::State<'_, LocalState>,
    request: Value,
) -> IpcResult {
    invoke(state, "daa_activate_configuration", request).await
}
#[tauri::command]
pub(crate) async fn daa_set_connection(
    state: tauri::State<'_, LocalState>,
    request: Value,
) -> IpcResult {
    invoke(state, "daa_set_connection", request).await
}
#[tauri::command]
pub(crate) async fn daa_set_collection(
    state: tauri::State<'_, LocalState>,
    request: Value,
) -> IpcResult {
    invoke(state, "daa_set_collection", request).await
}
#[tauri::command]
pub(crate) async fn daa_test_connection(
    state: tauri::State<'_, LocalState>,
    request: Value,
) -> IpcResult {
    invoke(state, "daa_test_connection", request).await
}
#[tauri::command]
pub(crate) async fn daa_diagnose_point(
    state: tauri::State<'_, LocalState>,
    request: Value,
) -> IpcResult {
    invoke(state, "daa_diagnose_point", request).await
}
#[tauri::command]
pub(crate) async fn daa_get_local_snapshot(
    state: tauri::State<'_, LocalState>,
    request: Value,
) -> IpcResult {
    invoke(state, "daa_get_local_snapshot", request).await
}
#[tauri::command]
pub(crate) async fn daa_list_history(
    state: tauri::State<'_, LocalState>,
    request: Value,
) -> IpcResult {
    invoke(state, "daa_list_history", request).await
}
#[tauri::command]
pub(crate) async fn daa_get_sample(
    state: tauri::State<'_, LocalState>,
    request: Value,
) -> IpcResult {
    invoke(state, "daa_get_sample", request).await
}
#[tauri::command]
pub(crate) async fn daa_get_logs(state: tauri::State<'_, LocalState>, request: Value) -> IpcResult {
    invoke(state, "daa_get_logs", request).await
}

#[tauri::command]
pub(crate) async fn daa_get_yaml_migration(
    state: tauri::State<'_, LocalState>,
    request: Value,
) -> IpcResult {
    invoke(state, "daa_get_yaml_migration", request).await
}
#[tauri::command]
pub(crate) async fn daa_retry_yaml_migration(
    state: tauri::State<'_, LocalState>,
    request: Value,
) -> IpcResult {
    invoke(state, "daa_retry_yaml_migration", request).await
}

#[tauri::command]
pub(crate) async fn daa_preview_point_names(
    state: tauri::State<'_, LocalState>,
    request: Value,
) -> IpcResult {
    invoke(state, "daa_preview_point_names", request).await
}
#[tauri::command]
pub(crate) async fn daa_confirm_point_names(
    state: tauri::State<'_, LocalState>,
    request: Value,
) -> IpcResult {
    invoke(state, "daa_confirm_point_names", request).await
}
