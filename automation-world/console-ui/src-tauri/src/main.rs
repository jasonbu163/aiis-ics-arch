//! File Path: /control-agent/src-tauri/src/main.rs
//! Description: Native executable entrypoint for the Control Agent
//! Main Features:
//!   - Hides the console window in Windows release builds
//!   - Supports explicit headless pilot verification commands
//!   - Delegates startup to the shared Tauri library module

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    if aiis_ics_control_agent_lib::run_headless_command(std::env::args().skip(1)) {
        return;
    }

    aiis_ics_control_agent_lib::run()
}
