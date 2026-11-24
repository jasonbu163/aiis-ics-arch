//! 新 CA 编辑器 IPC。用户选定路径由原生文件对话框返回。
use crate::domain::ca_flow::{Document, Issue, MAX_JSON};
use crate::infrastructure::ca_store;
use crate::services::{
    ca_node_test::{self, Intent},
    ca_workspace::{Binding, Saved, Workspace},
};
use serde_json::{json, Value};
use std::{path::PathBuf, sync::Arc};
use tauri::{AppHandle, Manager, State};
use tauri_plugin_dialog::DialogExt;

type Ws<'a> = State<'a, Arc<Workspace>>;

fn wants_legacy(args: impl IntoIterator<Item = String>) -> bool {
    args.into_iter().any(|arg| arg == "--ca-legacy-console")
}
pub(crate) fn legacy_mode() -> bool {
    wants_legacy(std::env::args().skip(1))
}
#[cfg(test)]
mod tests {
    use super::wants_legacy;
    #[test]
    fn desktop_legacy_is_exact_opt_in() {
        assert!(!wants_legacy([]));
        for flag in [
            "--ca-collect-plc-snapshots-once",
            "--ca-collect-plc-snapshots-loop",
            "--ca-smoke-plc-collection-loop",
            "--ca-legacy-console=yes",
        ] {
            assert!(!wants_legacy([flag.to_owned()]));
        }
        assert!(wants_legacy(["--ca-legacy-console".to_owned()]));
    }
}
#[tauri::command]
pub(crate) fn ca_app_mode() -> &'static str {
    if legacy_mode() {
        "legacy"
    } else {
        "editor"
    }
}

pub(crate) fn open_workspace(app: &tauri::App) -> Result<(), Box<dyn std::error::Error>> {
    let mut profile = (app.path().app_data_dir()?.join("flow-editor-v1"), false);
    #[cfg(debug_assertions)]
    if let Some(value) = std::env::var_os("CA_FLOW_EDITOR_PROFILE") {
        let root = PathBuf::from(value).canonicalize()?;
        let temp = std::env::temp_dir().canonicalize()?;
        let within = |parent: &std::path::Path| root != parent && root.starts_with(parent);
        let system_tmp = std::path::Path::new("/tmp").canonicalize().ok();
        if (!within(&temp) && !system_tmp.as_deref().is_some_and(within))
            || !root.join(".ca-editor-fixture").is_file()
        {
            return Err("Invalid isolated CA test profile".into());
        }
        profile = (root.join("flow-editor-v1"), true);
    }
    app.manage(Arc::new(Workspace::open(profile.0, profile.1)?));
    Ok(())
}
async fn blocking<T: Send + 'static>(
    f: impl FnOnce() -> Result<T, String> + Send + 'static,
) -> Result<T, String> {
    tauri::async_runtime::spawn_blocking(f)
        .await
        .map_err(|_| "operation_interrupted".to_owned())?
}
fn choose(app: &AppHandle, save: bool) -> Result<PathBuf, String> {
    let dialog = app.dialog().file().add_filter("JSON", &["json"]);
    let path = if save {
        dialog.set_file_name("flow.json").blocking_save_file()
    } else {
        dialog.blocking_pick_file()
    };
    path.ok_or("user_cancelled")?
        .into_path()
        .map_err(|_| "file_path".into())
}
#[tauri::command]
pub(crate) fn ca_flow_validate(ws: Ws<'_>, document: Document) -> Result<Vec<Issue>, String> {
    ws.validate(&document)
}
#[tauri::command]
pub(crate) fn ca_flow_list(ws: Ws<'_>) -> Result<Vec<Saved>, String> {
    Ok(ws.snapshot()?.flows.clone())
}
#[tauri::command]
pub(crate) fn ca_flow_get(ws: Ws<'_>, id: String, revision: u32) -> Result<Saved, String> {
    ws.get_flow(&id, revision)
}
#[tauri::command]
pub(crate) fn ca_flow_save(ws: Ws<'_>, document: Document, expected: u32) -> Result<Saved, String> {
    ws.save_flow(document, expected)
}
#[tauri::command]
pub(crate) async fn ca_flow_import(
    app: AppHandle,
    ws: Ws<'_>,
    token: Option<String>,
    copy_id: Option<String>,
) -> Result<Value, String> {
    let ws = Arc::clone(&ws);
    blocking(move || {
        if let Some(token) = token {
            return Ok(json!(ws.import_flow(&token, copy_id)?));
        }
        let path = choose(&app, false)?;
        let raw = ca_store::read_bytes(&path, MAX_JSON)?;
        ws.preview_flow(path, &raw)
    })
    .await
}
#[tauri::command]
pub(crate) async fn ca_flow_export(
    app: AppHandle,
    ws: Ws<'_>,
    id: String,
    revision: u32,
) -> Result<Value, String> {
    let ws = Arc::clone(&ws);
    blocking(move || {
        let saved = ws.get_flow(&id, revision)?;
        if !ws.validate(&saved.document)?.is_empty() {
            return Err("flow_invalid".into());
        }
        let path = choose(&app, true)?;
        let bytes = saved.bytes();
        ca_store::atomic(&path, &bytes, false)?;
        Ok(json!({"file_sha256":saved.file_sha256,"semantic_sha256":saved.semantic_sha256}))
    })
    .await
}
#[tauri::command]
pub(crate) async fn ca_plc_catalog_preview(app: AppHandle, ws: Ws<'_>) -> Result<Value, String> {
    let ws = Arc::clone(&ws);
    blocking(move || {
        let path = choose(&app, false)?;
        let bytes = ca_store::read_bytes(&path, MAX_JSON)?;
        ws.preview_catalog(path, &bytes)
    })
    .await
}
#[tauri::command]
pub(crate) fn ca_plc_catalog_commit(
    ws: Ws<'_>,
    token: String,
    alias: String,
) -> Result<Value, String> {
    ws.import_catalog(&token, &alias)
}
#[tauri::command]
pub(crate) fn ca_resource_list(ws: Ws<'_>) -> Result<Value, String> {
    ws.bindings()
}
#[tauri::command]
pub(crate) fn ca_resource_save_binding(ws: Ws<'_>, binding: Binding) -> Result<(), String> {
    ws.bind(binding)
}
#[tauri::command]
pub(crate) fn ca_node_test_preview(ws: Ws<'_>, intent: Intent) -> Result<Value, String> {
    ca_node_test::preview(&ws, intent)
}
#[tauri::command]
pub(crate) async fn ca_node_test_run(
    ws: Ws<'_>,
    token: String,
    confirmed: bool,
) -> Result<Value, String> {
    let ws = Arc::clone(&ws);
    blocking(move || ca_node_test::run(&ws, &token, confirmed)).await
}
#[tauri::command]
pub(crate) fn ca_node_test_list(ws: Ws<'_>) -> Result<Vec<Value>, String> {
    Ok(ws.snapshot()?.tests.iter().rev().cloned().collect())
}
#[tauri::command]
pub(crate) fn ca_node_test_get(ws: Ws<'_>, id: String) -> Result<Value, String> {
    ws.snapshot()?
        .tests
        .iter()
        .find(|item| item["id"] == id)
        .cloned()
        .ok_or("test_not_found".into())
}
