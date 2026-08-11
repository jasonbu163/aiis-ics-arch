//! File Path: /control-agent/src-tauri/src/lib.rs
//! Description: Control Agent Tauri runtime composition root
//! Main Features:
//!   - Registers internal Rust modules
//!   - Registers Tauri command adapters
//!   - Starts the AIIS ICS Control Agent desktop runtime

mod commands;
mod config;
mod domain;
mod infrastructure;
mod services;

pub(crate) fn autostart_plc_collection_loop_from_env() {
    let config = crate::config::AgentConfig::load();

    let mode = services::plc_collection::plc_autostart_mode(&config);
    if mode == "stopped" {
        return;
    }

    let env_errors = services::plc_collection::plc_autostart_gate_errors(&config);
    if !env_errors.is_empty() {
        tracing::warn!(
            event = "plc_collection_startup_autostart_rejected",
            accepted = false,
            running = false,
            status = "blocked",
            message = "blocked_by_env_conflict",
            gate_errors = ?env_errors,
        );
        return;
    }

    let result = match mode.as_str() {
        "read_only" => services::plc_collection::start_plc_read_from_console(),
        "collect" => services::plc_collection::start_plc_collection_from_console(),
        _ => return,
    };

    tracing::info!(
        event = "plc_collection_startup_autostart",
        accepted = result.accepted,
        running = result.running,
        status = %result.status,
        message = %result.message,
        gate_errors = ?result.gate_errors,
    );
}

pub fn run_headless_command(args: impl IntoIterator<Item = String>) -> bool {
    let args = args.into_iter().collect::<Vec<_>>();

    if args
        .iter()
        .any(|arg| arg == "--ca-collect-plc-snapshots-once")
    {
        let result = services::plc_collection::collect_plc_db_blocks_once();
        println!(
            "{}",
            serde_json::to_string(&result).unwrap_or_else(|_| {
                "{\"status\":\"failed\",\"message\":\"serialize_failed\"}".to_string()
            })
        );
        return true;
    }

    if args
        .iter()
        .any(|arg| arg == "--ca-collect-plc-snapshots-loop")
    {
        let result = services::plc_collection::collect_plc_db_blocks_loop();
        println!(
            "{}",
            serde_json::to_string(&result).unwrap_or_else(|_| {
                "{\"status\":\"failed\",\"message\":\"serialize_failed\"}".to_string()
            })
        );
        return true;
    }

    if args
        .iter()
        .any(|arg| arg == "--ca-smoke-plc-collection-loop")
    {
        let result = services::plc_collection::smoke_plc_collection_loop_from_console();
        println!(
            "{}",
            serde_json::to_string(&result).unwrap_or_else(|_| {
                "{\"status\":\"failed\",\"message\":\"serialize_failed\"}".to_string()
            })
        );
        return true;
    }

    false
}

pub fn run_headless_runtime() -> i32 {
    commands::headless_runtime::run()
}

#[cfg(test)]
mod boundary_tests {
    use std::fs;
    use std::path::{Path, PathBuf};

    fn rust_files_under(dir: &Path) -> Vec<PathBuf> {
        let mut files = Vec::new();
        let Ok(entries) = fs::read_dir(dir) else {
            return files;
        };

        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                files.extend(rust_files_under(&path));
            } else if path.extension().and_then(|value| value.to_str()) == Some("rs") {
                files.push(path);
            }
        }

        files
    }

    #[test]
    fn commands_and_services_do_not_construct_database_queries() {
        let manifest_dir = Path::new(env!("CARGO_MANIFEST_DIR"));
        let forbidden_patterns = [
            "sqlx::query",
            "Entity::find",
            "Column::",
            "DatabaseConnection",
            "connect_sea_orm",
            "sea_orm::",
        ];

        for relative_dir in ["src/commands", "src/services"] {
            let dir = manifest_dir.join(relative_dir);
            for file in rust_files_under(&dir) {
                let content = fs::read_to_string(&file)
                    .unwrap_or_else(|error| panic!("Failed to read {}: {error}", file.display()));
                for pattern in forbidden_patterns {
                    assert!(
                        !content.contains(pattern),
                        "{} must not contain database infrastructure pattern `{}`",
                        file.display(),
                        pattern
                    );
                }
            }
        }
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let config = config::AgentConfig::load();
    let logging_guards = infrastructure::logging::init_logging(&config);
    infrastructure::logging::emit_startup_event(&config);

    tauri::Builder::default()
        .manage(logging_guards)
        .setup(|_app| {
            autostart_plc_collection_loop_from_env();
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::plc_collection::start_plc_read,
            commands::plc_collection::start_plc_read_for_plc,
            commands::plc_collection::stop_plc_read,
            commands::plc_collection::stop_plc_read_for_plc,
            commands::plc_collection::enable_plc_persistence,
            commands::plc_collection::enable_plc_persistence_for_plc,
            commands::plc_collection::pause_plc_persistence,
            commands::plc_collection::pause_plc_persistence_for_plc,
            commands::plc_collection::start_plc_collection,
            commands::plc_collection::start_plc_collection_for_plc,
            commands::plc_collection::stop_plc_collection,
            commands::plc_collection::stop_plc_collection_for_plc,
            commands::plc_collection::start_plc_collection_loop,
            commands::plc_collection::start_plc_collection_loop_for_plc,
            commands::plc_collection::stop_plc_collection_loop,
            commands::plc_collection::stop_plc_collection_loop_for_plc,
            commands::plc_diagnostics::read_plc_samples_once,
            commands::plc_diagnostics::read_plc_samples_once_for_plc,
            commands::runtime_snapshot::get_runtime_snapshot
        ])
        .run(tauri::generate_context!())
        .expect("error while running AIIS ICS Control Agent");
}
