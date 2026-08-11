//! File Path: /control-agent/src-tauri/src/services/mod.rs
//! Description: Control Agent service module registry
//! Main Features:
//!   - Groups authorization gate diagnostics
//!   - Groups PLC diagnostics service orchestration
//!   - Groups runtime snapshot assembly
//!   - Keeps Tauri command adapters thin

pub(crate) mod authorization_gate;
pub(crate) mod plc_collection;
pub(crate) mod plc_diagnostics;
pub(crate) mod runtime_snapshot;
