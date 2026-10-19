//! File Path: /automation-world/data-acquisition-agent/src-tauri/src/commands/plc_diagnostics.rs
//! Description: Thin Tauri command adapters for PLC diagnostics
//! Main Features:
//!   - Exposes operator-triggered read-only PLC sample reads
//!   - Keeps PLC driver logic inside services and infrastructure adapters

use crate::domain::plc::PlcSampleReadSnapshot;
use crate::services::plc_diagnostics;

#[tauri::command]
pub(crate) fn read_plc_samples_once() -> Result<PlcSampleReadSnapshot, String> {
    crate::config::local_bootstrap::legacy_guard()?;
    Ok(plc_diagnostics::read_plc_samples_once_from_console())
}

#[tauri::command]
pub(crate) fn read_plc_samples_once_for_plc(
    plc_key: String,
) -> Result<PlcSampleReadSnapshot, String> {
    crate::config::local_bootstrap::legacy_guard()?;
    Ok(plc_diagnostics::read_plc_samples_once_for_plc_from_console(
        plc_key,
    ))
}
