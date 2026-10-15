//! File Path: /automation-world/semantic-mapping-agent/src-tauri/src/commands/file_export/mod.rs
//! Description: Thin Tauri command adapter for user-selected Collection Facts exports.
//! Main Features:
//!   - Accepts only the generated file name, MIME type, and byte content
//!   - Delegates native Save As selection and writing to the file-export service

use crate::services::file_export;

#[tauri::command]
pub async fn save_collection_fact_file(
    app: tauri::AppHandle,
    file_name: String,
    mime_type: String,
    contents: Vec<u8>,
) -> Result<bool, String> {
    file_export::save_collection_fact_file(&app, &file_name, &mime_type, contents).await
}
