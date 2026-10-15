//! File Path: /control-agent/src-tauri/src/infrastructure/logging.rs
//! Description: Structured runtime log adapter
//! Main Features:
//!   - Initializes tracing subscribers for stdout and local runtime/audit files
//!   - Emits JSON-line diagnostic events through tracing targets
//!   - Keeps logging side effects out of Tauri commands and services

use std::fmt;

use chrono::{Local, SecondsFormat};
use tracing::info;
use tracing_appender::non_blocking::WorkerGuard;
use tracing_appender::rolling::{RollingFileAppender, Rotation};
use tracing_subscriber::filter::filter_fn;
use tracing_subscriber::fmt::format::Writer;
use tracing_subscriber::fmt::time::FormatTime;
use tracing_subscriber::prelude::*;
use tracing_subscriber::util::SubscriberInitExt;
use tracing_subscriber::EnvFilter;

use crate::config::AgentConfig;
use crate::domain::runtime::RuntimeSnapshot;

const RUNTIME_TARGET: &str = "control_agent_runtime";
const AUDIT_TARGET: &str = "control_agent_audit";

#[derive(Clone, Copy, Debug)]
struct LocalRfc3339Timer;

impl FormatTime for LocalRfc3339Timer {
    fn format_time(&self, writer: &mut Writer<'_>) -> fmt::Result {
        writer.write_str(&local_rfc3339_timestamp())
    }
}

fn local_rfc3339_timestamp() -> String {
    Local::now().to_rfc3339_opts(SecondsFormat::Micros, true)
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub(crate) enum LogFormat {
    JsonLines,
}

impl LogFormat {
    fn from_value(value: &str) -> Self {
        match value.trim().to_ascii_lowercase().as_str() {
            "json" | "jsonl" | "json-lines" => Self::JsonLines,
            _ => Self::JsonLines,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub(crate) struct LoggingSettings {
    pub(crate) structured_logs_enabled: bool,
    pub(crate) file_logs_enabled: bool,
    pub(crate) log_dir: String,
    pub(crate) log_level: String,
    pub(crate) log_format: LogFormat,
    pub(crate) log_rotation: String,
    pub(crate) audit_log_enabled: bool,
}

impl LoggingSettings {
    pub(crate) fn from_config(config: &AgentConfig) -> Self {
        Self {
            structured_logs_enabled: config
                .bool_or_default("CONTROL_AGENT_STRUCTURED_LOGS_ENABLED", true),
            file_logs_enabled: config.bool_or_default("CONTROL_AGENT_FILE_LOGS_ENABLED", true),
            log_dir: config.value_or_default("CONTROL_AGENT_LOG_DIR", "logs/control-agent"),
            log_level: config.value_or_default("CONTROL_AGENT_LOG_LEVEL", "info"),
            log_format: LogFormat::from_value(
                &config.value_or_default("CONTROL_AGENT_LOG_FORMAT", "jsonl"),
            ),
            log_rotation: config.value_or_default("CONTROL_AGENT_LOG_ROTATION", "daily"),
            audit_log_enabled: config.bool_or_default("CONTROL_AGENT_AUDIT_LOG_ENABLED", true),
        }
    }
}

pub(crate) struct LoggingGuards {
    _runtime_file_guard: Option<WorkerGuard>,
    _audit_file_guard: Option<WorkerGuard>,
}

pub(crate) fn init_logging(config: &AgentConfig) -> LoggingGuards {
    let settings = LoggingSettings::from_config(config);
    let filter = EnvFilter::try_new(&settings.log_level).unwrap_or_else(|_| EnvFilter::new("info"));

    let stdout_layer = settings.structured_logs_enabled.then(|| {
        tracing_subscriber::fmt::layer()
            .json()
            .with_timer(LocalRfc3339Timer)
            .flatten_event(true)
            .with_current_span(false)
            .with_span_list(false)
            .with_filter(filter_fn(|metadata| metadata.target() != AUDIT_TARGET))
    });

    let (runtime_file_layer, runtime_file_guard) = if settings.file_logs_enabled {
        if let Some(appender) = runtime_file_appender(&settings, "runtime.log") {
            let (writer, guard) = tracing_appender::non_blocking(appender);
            let layer = tracing_subscriber::fmt::layer()
                .json()
                .with_timer(LocalRfc3339Timer)
                .flatten_event(true)
                .with_current_span(false)
                .with_span_list(false)
                .with_writer(writer)
                .with_filter(filter_fn(|metadata| metadata.target() != AUDIT_TARGET));

            (Some(layer), Some(guard))
        } else {
            (None, None)
        }
    } else {
        (None, None)
    };

    let (audit_file_layer, audit_file_guard) =
        if settings.file_logs_enabled && settings.audit_log_enabled {
            if let Some(appender) = runtime_file_appender(&settings, "audit.log") {
                let (writer, guard) = tracing_appender::non_blocking(appender);
                let layer = tracing_subscriber::fmt::layer()
                    .json()
                    .with_timer(LocalRfc3339Timer)
                    .flatten_event(true)
                    .with_current_span(false)
                    .with_span_list(false)
                    .with_writer(writer)
                    .with_filter(filter_fn(|metadata| metadata.target() == AUDIT_TARGET));

                (Some(layer), Some(guard))
            } else {
                (None, None)
            }
        } else {
            (None, None)
        };

    let _ = tracing_subscriber::registry()
        .with(filter)
        .with(stdout_layer)
        .with(runtime_file_layer)
        .with(audit_file_layer)
        .try_init();

    LoggingGuards {
        _runtime_file_guard: runtime_file_guard,
        _audit_file_guard: audit_file_guard,
    }
}

fn runtime_file_appender(
    settings: &LoggingSettings,
    file_name: &str,
) -> Option<RollingFileAppender> {
    let rotation = match settings.log_rotation.trim().to_ascii_lowercase().as_str() {
        "daily" => Rotation::DAILY,
        _ => Rotation::NEVER,
    };

    let builder = RollingFileAppender::builder()
        .rotation(rotation.clone())
        .filename_prefix(file_name);

    if matches!(rotation, Rotation::DAILY) {
        builder
            .latest_symlink(file_name)
            .build(&settings.log_dir)
            .or_else(|_| {
                RollingFileAppender::builder()
                    .rotation(rotation)
                    .filename_prefix(file_name)
                    .build(&settings.log_dir)
            })
            .ok()
    } else {
        builder.build(&settings.log_dir).ok()
    }
}

pub(crate) fn structured_logs_enabled(config: &AgentConfig) -> bool {
    config.bool_or_default("CONTROL_AGENT_STRUCTURED_LOGS_ENABLED", true)
}

pub(crate) fn emit_startup_event(config: &AgentConfig) {
    if !structured_logs_enabled(config) {
        return;
    }

    info!(
        target: RUNTIME_TARGET,
        event = "control_agent_started",
        agent = "aiis-ics-control-agent",
        version = env!("CARGO_PKG_VERSION"),
        mode = "plc_collection",
        access_mode = %config.value_or_default("CONTROL_AGENT_ACCESS_MODE", "database"),
        database_enabled = config.bool_or_default("CONTROL_AGENT_DATABASE_ENABLED", false),
    );
}

pub(crate) fn emit_runtime_snapshot_event(config: &AgentConfig, snapshot: &RuntimeSnapshot) {
    if !structured_logs_enabled(config) {
        return;
    }

    info!(
        target: RUNTIME_TARGET,
        event = "runtime_snapshot_built",
        agent = %snapshot.agent_name,
        mode = %snapshot.mode,
        generated_at_unix_seconds = snapshot.generated_at_unix_seconds,
        uptime_seconds = snapshot.agent_heartbeat.uptime_seconds,
        database_enabled = snapshot.database_enabled,
        database_configured = snapshot.database_configured,
        plc_contract_loaded = snapshot.plc_point_contract.loaded,
        plc_endpoint_reachable = snapshot.plc_endpoint_probe.reachable,
        plc_sample_driver = %snapshot.plc_sample_read.driver,
        plc_sample_succeeded = snapshot.plc_sample_read.succeeded,
        authorization_gate_enabled = snapshot.authorization_gate.enabled,
        authorization_self_test_passed = snapshot.authorization_gate.self_test.passed,
    );
}

#[cfg(test)]
mod tests {
    use std::collections::HashMap;

    use super::*;

    #[test]
    fn local_log_timestamp_uses_rfc3339_shape() {
        let timestamp = local_rfc3339_timestamp();
        let has_offset_suffix = timestamp.len() >= 6 && {
            let suffix = &timestamp[timestamp.len() - 6..];
            (suffix.starts_with('+') || suffix.starts_with('-')) && suffix.as_bytes()[3] == b':'
        };

        assert!(timestamp.contains('T'));
        assert!(timestamp.ends_with('Z') || has_offset_suffix);
    }

    #[test]
    fn builds_file_logging_settings_from_config() {
        let values = HashMap::from([
            (
                "CONTROL_AGENT_FILE_LOGS_ENABLED".to_string(),
                "false".to_string(),
            ),
            (
                "CONTROL_AGENT_LOG_DIR".to_string(),
                "tmp/control-agent-logs".to_string(),
            ),
            ("CONTROL_AGENT_LOG_LEVEL".to_string(), "debug".to_string()),
            ("CONTROL_AGENT_LOG_FORMAT".to_string(), "jsonl".to_string()),
            (
                "CONTROL_AGENT_AUDIT_LOG_ENABLED".to_string(),
                "true".to_string(),
            ),
        ]);
        let config = AgentConfig::from_values(values);

        let settings = LoggingSettings::from_config(&config);

        assert!(!settings.file_logs_enabled);
        assert_eq!(settings.log_dir, "tmp/control-agent-logs");
        assert_eq!(settings.log_level, "debug");
        assert_eq!(settings.log_format, LogFormat::JsonLines);
        assert!(settings.audit_log_enabled);
    }

    #[test]
    fn emits_startup_event_without_panicking_when_file_logs_are_disabled() {
        let values = HashMap::from([(
            "CONTROL_AGENT_FILE_LOGS_ENABLED".to_string(),
            "false".to_string(),
        )]);
        let config = AgentConfig::from_values(values);

        let _guards = init_logging(&config);

        emit_startup_event(&config);
    }
}
