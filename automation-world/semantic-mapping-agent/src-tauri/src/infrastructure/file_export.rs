//! File Path: /automation-world/semantic-mapping-agent/src-tauri/src/infrastructure/file_export.rs
//! Description: Native Save As dialog and single-file write adapter.
//! Main Features:
//!   - Opens a platform file-save dialog using the approved generated name and extension
//!   - Writes only the path returned by that dialog, treating user cancellation as no-op

use std::fs;

use tauri::AppHandle;
use tauri_plugin_dialog::DialogExt;

pub fn save_with_dialog(
    app: &AppHandle,
    file_name: &str,
    contents: &[u8],
    filter_name: &str,
    extension: &str,
) -> Result<bool, String> {
    let Some(file_path) = app
        .dialog()
        .file()
        .set_file_name(file_name)
        .add_filter(filter_name, &[extension])
        .blocking_save_file()
    else {
        return Ok(false);
    };
    let path = file_path
        .into_path()
        .map_err(|_| "COLLECTION_FACT_FILE_EXPORT_FAILED".to_owned())?;

    fs::write(path, contents).map_err(|_| "COLLECTION_FACT_FILE_EXPORT_FAILED".to_owned())?;
    Ok(true)
}
