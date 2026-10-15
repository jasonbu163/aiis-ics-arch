#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

//! File Path: /automation-world/semantic-mapping-agent/src-tauri/src/main.rs
//! Description: AIIS Semantic Mapping Agent process entry point.
//! Main Features:
//!     - Delegates application assembly to the library crate.

fn main() {
    aiis_semantic_mapping_agent_lib::app::run();
}
