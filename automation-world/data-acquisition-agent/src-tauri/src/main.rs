//! File Path: /automation-world/data-acquisition-agent/src-tauri/src/main.rs
//! Description: DAA原生唯一SQLite入口
//! Main Features:
//!   - Hides the console window in Windows release builds
//!   - Rejects retired headless/CLI arguments before configuration
//!   - Delegates startup to the shared Tauri library module

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let result = aiis_data_acquisition_agent_lib::run_headless_command(args.clone())
        .and_then(|_| aiis_data_acquisition_agent_lib::prepare_runtime(args));
    if let Err(error) = result {
        eprintln!(
            "{}",
            serde_json::json!({"event":"runtime_start_rejected","process":"daa","resource":"startup","result":"rejected","error_code":error,"next":"Remove retired runtime overrides and use pnpm tauri dev; YAML is a one-time migration source"})
        );
        std::process::exit(2);
    }
    aiis_data_acquisition_agent_lib::run()
}
