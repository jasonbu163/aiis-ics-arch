//! File Path: /control-agent/src-tauri/src/commands/plc_collection.rs
//! Description: Tauri command adapters for PLC collection controls
//! Main Features:
//!   - Exposes explicit read, persistence and collection controls for PLC runtime units
//!   - Delegates gate checks and loop lifecycle to the service layer
//!   - Keeps UI-triggered collection controls out of runtime bootstrap code

use crate::domain::plc_collection::PlcCollectionControlResult;
use crate::services::plc_collection::{
    enable_plc_persistence_for_plc_from_console, enable_plc_persistence_from_console,
    pause_plc_persistence_for_plc_from_console, pause_plc_persistence_from_console,
    start_plc_collection_for_plc_from_console, start_plc_collection_from_console,
    start_plc_collection_loop_for_plc_from_console, start_plc_collection_loop_from_console,
    start_plc_read_for_plc_from_console, start_plc_read_from_console,
    stop_plc_collection_for_plc_from_console, stop_plc_collection_from_console,
    stop_plc_collection_loop_for_plc_from_console, stop_plc_collection_loop_from_console,
    stop_plc_read_for_plc_from_console, stop_plc_read_from_console,
};

#[tauri::command]
pub(crate) fn start_plc_read() -> PlcCollectionControlResult {
    start_plc_read_from_console()
}

#[tauri::command]
pub(crate) fn start_plc_read_for_plc(plc_key: String) -> PlcCollectionControlResult {
    start_plc_read_for_plc_from_console(plc_key)
}

#[tauri::command]
pub(crate) fn stop_plc_read() -> PlcCollectionControlResult {
    stop_plc_read_from_console()
}

#[tauri::command]
pub(crate) fn stop_plc_read_for_plc(plc_key: String) -> PlcCollectionControlResult {
    stop_plc_read_for_plc_from_console(plc_key)
}

#[tauri::command]
pub(crate) fn enable_plc_persistence() -> PlcCollectionControlResult {
    enable_plc_persistence_from_console()
}

#[tauri::command]
pub(crate) fn enable_plc_persistence_for_plc(plc_key: String) -> PlcCollectionControlResult {
    enable_plc_persistence_for_plc_from_console(plc_key)
}

#[tauri::command]
pub(crate) fn pause_plc_persistence() -> PlcCollectionControlResult {
    pause_plc_persistence_from_console()
}

#[tauri::command]
pub(crate) fn pause_plc_persistence_for_plc(plc_key: String) -> PlcCollectionControlResult {
    pause_plc_persistence_for_plc_from_console(plc_key)
}

#[tauri::command]
pub(crate) fn start_plc_collection() -> PlcCollectionControlResult {
    start_plc_collection_from_console()
}

#[tauri::command]
pub(crate) fn start_plc_collection_for_plc(plc_key: String) -> PlcCollectionControlResult {
    start_plc_collection_for_plc_from_console(plc_key)
}

#[tauri::command]
pub(crate) fn stop_plc_collection() -> PlcCollectionControlResult {
    stop_plc_collection_from_console()
}

#[tauri::command]
pub(crate) fn stop_plc_collection_for_plc(plc_key: String) -> PlcCollectionControlResult {
    stop_plc_collection_for_plc_from_console(plc_key)
}

#[tauri::command]
pub(crate) fn start_plc_collection_loop() -> PlcCollectionControlResult {
    start_plc_collection_loop_from_console()
}

#[tauri::command]
pub(crate) fn start_plc_collection_loop_for_plc(plc_key: String) -> PlcCollectionControlResult {
    start_plc_collection_loop_for_plc_from_console(plc_key)
}

#[tauri::command]
pub(crate) fn stop_plc_collection_loop() -> PlcCollectionControlResult {
    stop_plc_collection_loop_from_console()
}

#[tauri::command]
pub(crate) fn stop_plc_collection_loop_for_plc(plc_key: String) -> PlcCollectionControlResult {
    stop_plc_collection_loop_for_plc_from_console(plc_key)
}
