//! File Path: /automation-world/semantic-mapping-agent/src-tauri/src/services/file_export.rs
//! Description: Bounded Collection Facts export orchestration.
//! Main Features:
//!   - Validates the two approved JSON/XLSX output forms before native saving
//!   - Moves blocking system-dialog and file work off the async command path

use crate::infrastructure::file_export;
use tauri::AppHandle;

struct CollectionFactExport {
    file_name: String,
    contents: Vec<u8>,
    filter_name: &'static str,
    extension: &'static str,
}

pub async fn save_collection_fact_file(
    app: &AppHandle,
    file_name: &str,
    mime_type: &str,
    contents: Vec<u8>,
) -> Result<bool, String> {
    let export = validate_export(file_name, mime_type, contents)?;
    let app = app.clone();

    tokio::task::spawn_blocking(move || {
        file_export::save_with_dialog(
            &app,
            &export.file_name,
            &export.contents,
            export.filter_name,
            export.extension,
        )
    })
    .await
    .map_err(|_| "COLLECTION_FACT_FILE_EXPORT_FAILED".to_owned())?
}

fn validate_export(
    file_name: &str,
    mime_type: &str,
    contents: Vec<u8>,
) -> Result<CollectionFactExport, String> {
    if file_name.is_empty() || file_name.contains(['/', '\\']) {
        return Err("COLLECTION_FACT_FILE_EXPORT_INVALID".to_owned());
    }

    let (filter_name, extension, expected_mime_type) = if file_name.ends_with(".json") {
        ("JSON", "json", "application/json;charset=utf-8")
    } else if file_name.ends_with(".xlsx") {
        (
            "Excel Workbook",
            "xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    } else {
        return Err("COLLECTION_FACT_FILE_EXPORT_INVALID".to_owned());
    };

    if mime_type != expected_mime_type {
        return Err("COLLECTION_FACT_FILE_EXPORT_INVALID".to_owned());
    }

    Ok(CollectionFactExport {
        file_name: file_name.to_owned(),
        contents,
        filter_name,
        extension,
    })
}
