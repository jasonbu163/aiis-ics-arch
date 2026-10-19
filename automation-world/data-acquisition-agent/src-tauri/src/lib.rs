//! File Path: /automation-world/data-acquisition-agent/src-tauri/src/lib.rs
//! Description: DAA SQLite唯一Tauri composition root
//! Main Features:
//!   - Registers internal Rust modules
//!   - Registers Tauri command adapters
//!   - Starts the AIIS Data Acquisition Agent desktop runtime

#[cfg(all(feature = "local-validation", not(debug_assertions)))]
compile_error!("local-validation is forbidden in release builds");

mod commands;
mod config;
mod domain;
mod infrastructure;
mod services;

/// 旧CLI/headless入口在配置、锁及任何设备I/O之前拒绝。
pub fn run_headless_command(args: impl IntoIterator<Item = String>) -> Result<bool, String> {
    if args.into_iter().any(|arg| arg.starts_with("--ca-")) {
        return Err("legacy_entry_retired".into());
    }
    Ok(false)
}
pub fn run_headless_runtime() -> i32 {
    eprintln!(
        "{}",
        serde_json::json!({"event":"legacy_entry_rejected","process":"daa","resource":"headless","result":"rejected","error_code":"legacy_entry_retired","next":"Use pnpm tauri dev; YAML is a one-time migration source"})
    );
    2
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
    let bootstrap = config::local_bootstrap::current()
        .cloned()
        .unwrap_or_else(|| {
            config::local_bootstrap::load(std::env::args().skip(1).collect())
                .expect("invalid runtime bootstrap")
        });
    let local = services::local_recovery::open(bootstrap.clone()).expect("local runtime refused");
    let shutdown = local.clone();
    tauri::Builder::default()
        .manage(commands::local_acquisition::LocalState {
            bootstrap,
            engine: Some(local),
        })
        .invoke_handler(tauri::generate_handler![
            commands::local_acquisition::daa_get_bootstrap,
            commands::local_acquisition::daa_get_configuration,
            commands::local_acquisition::daa_get_yaml_migration,
            commands::local_acquisition::daa_retry_yaml_migration,
            commands::local_acquisition::daa_save_draft,
            commands::local_acquisition::daa_import_sources,
            commands::local_acquisition::daa_preview_offsets,
            commands::local_acquisition::daa_confirm_offsets,
            commands::local_acquisition::daa_activate_configuration,
            commands::local_acquisition::daa_set_connection,
            commands::local_acquisition::daa_set_collection,
            commands::local_acquisition::daa_test_connection,
            commands::local_acquisition::daa_diagnose_point,
            commands::local_acquisition::daa_get_local_snapshot,
            commands::local_acquisition::daa_list_history,
            commands::local_acquisition::daa_get_sample,
            commands::local_acquisition::daa_get_logs
        ])
        .build(tauri::generate_context!())
        .expect("error while building AIIS Data Acquisition Agent")
        .run(move |_app, event| {
            if matches!(
                event,
                tauri::RunEvent::ExitRequested { .. } | tauri::RunEvent::Exit
            ) {
                shutdown.shutdown();
            }
        });
}

#[cfg(feature = "local-validation")]
pub fn run_local_validation_command(args: Vec<String>) -> i32 {
    commands::local_validation::run(args)
}
pub fn prepare_runtime(args: Vec<String>) -> Result<(), String> {
    config::local_bootstrap::load(args).map(|_| ())
}
