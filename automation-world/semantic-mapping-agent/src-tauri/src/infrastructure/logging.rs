//! Minimal SMA startup/gate JSONL evidence; no payload values or connection secrets.
use tauri::{AppHandle, Manager};
use tracing_subscriber::prelude::*;
pub fn init(
    app: &AppHandle,
) -> Result<tracing_appender::non_blocking::WorkerGuard, Box<dyn std::error::Error>> {
    let directory = crate::config::profile_override()
        .unwrap_or(app.path().app_data_dir()?)
        .join("logs");
    let file = tracing_appender::rolling::daily(directory, "runtime.jsonl");
    let (writer, guard) = tracing_appender::non_blocking(file);
    let _ = tracing_subscriber::registry()
        .with(tracing_subscriber::filter::LevelFilter::INFO)
        .with(
            tracing_subscriber::fmt::layer()
                .json()
                .with_writer(std::io::stdout),
        )
        .with(tracing_subscriber::fmt::layer().json().with_writer(writer))
        .try_init();
    let config = crate::config::load_defaults_from_env();
    tracing::info!(event="sma_started", process="aiis-semantic-mapping-agent", configuration_source=%config.configuration_source, external_io_enabled=config.external_io_enabled, backend_configured=!config.backend_base_url.trim().is_empty(), result="ready");
    Ok(guard)
}
