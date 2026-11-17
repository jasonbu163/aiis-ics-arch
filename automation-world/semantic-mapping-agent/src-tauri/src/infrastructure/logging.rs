//! Minimal SMA startup/gate JSONL evidence; no payload values or connection secrets.
use crate::config::{AppDefaults, ResolvedProfile};
use tracing_subscriber::prelude::*;
pub(crate) fn init(
    profile: &ResolvedProfile,
    config: &AppDefaults,
) -> Result<tracing_appender::non_blocking::WorkerGuard, Box<dyn std::error::Error>> {
    let directory = profile.logging_directory();
    let file = tracing_appender::rolling::RollingFileAppender::builder()
        .rotation(tracing_appender::rolling::Rotation::DAILY)
        .filename_prefix("runtime.jsonl")
        .build(directory)
        .map_err(|error| {
            std::io::Error::other(format!("SMA_PROFILE_DIR_LOGGING_UNAVAILABLE: {error}"))
        })?;
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
    tracing::info!(event="sma_started", process="aiis-semantic-mapping-agent", configuration_source=%config.configuration_source, external_io_enabled=config.external_io_enabled, backend_configured=!config.backend_base_url.trim().is_empty(), result="ready");
    Ok(guard)
}
