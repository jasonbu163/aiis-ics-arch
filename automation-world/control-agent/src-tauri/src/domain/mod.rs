//! File Path: /control-agent/src-tauri/src/domain/mod.rs
//! Description: Domain model module registry for the Control Agent runtime
//! Main Features:
//!   - Groups authorization gate domain structures
//!   - Groups runtime snapshot domain structures
//!   - Groups PLC diagnostics domain structures

pub(crate) mod authorization;
pub(crate) mod headless_runtime;
pub(crate) mod plc;
pub(crate) mod plc_collection;
pub(crate) mod runtime;
