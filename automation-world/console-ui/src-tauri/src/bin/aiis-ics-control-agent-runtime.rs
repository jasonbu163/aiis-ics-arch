//! File Path: /control-agent/src-tauri/src/bin/aiis-ics-control-agent-runtime.rs
//! Description: Standalone headless Control Agent runtime entrypoint
//! Main Features:
//!   - Runs the shared PLC supervisor without starting Tauri or a WebView
//!   - Delegates stdin/stdout JSON Lines control to the library command adapter

fn main() {
    let exit_code = aiis_ics_control_agent_lib::run_headless_runtime();

    if exit_code != 0 {
        std::process::exit(exit_code);
    }
}
