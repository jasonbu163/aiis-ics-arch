//! File Path: /control-agent/src-tauri/src/commands/mod.rs
//! Description: Tauri command adapter module registry
//! Main Features:
//!   - Groups thin Tauri command handlers
//!   - Keeps command handlers separate from runtime services
//!   - Exposes read-only runtime snapshot commands
//!   - Exposes gated PLC collection lifecycle controls
//!   - Exposes operator-triggered PLC diagnostic read controls

pub(crate) mod headless_runtime;
pub(crate) mod plc_collection;
pub(crate) mod plc_diagnostics;
pub(crate) mod runtime_snapshot;
