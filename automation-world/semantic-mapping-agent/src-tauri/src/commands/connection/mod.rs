//! Thin SMA local bootstrap and external-I/O gate adapters. No SQL/device IPC.
#[tauri::command]
pub fn load_app_defaults() -> crate::config::AppDefaults {
    let defaults = crate::config::load_defaults_from_env();
    tracing::info!(event="sma_defaults_loaded", process="aiis-semantic-mapping-agent", configuration_source=%defaults.configuration_source, external_io_enabled=defaults.external_io_enabled, backend_configured=!defaults.backend_base_url.trim().is_empty(), result="loaded");
    defaults
}
#[tauri::command]
pub fn check_external_io() -> Result<(), String> {
    crate::config::require_external_io()
}
