//! File Path: /control-agent/src-tauri/src/infrastructure/mod.rs
//! Description: Infrastructure adapter module registry
//! Main Features:
//!   - Groups PLC snapshot database adapters
//!   - Groups PLC driver, decoder, point and S7 helpers
//!   - Keeps external protocol details out of services and Tauri commands

pub(crate) mod database;
pub(crate) mod logging;
pub(crate) mod minimal_s7_adapter;
pub(crate) mod plc_client;
pub(crate) mod plc_decode;
pub(crate) mod plc_points;
pub(crate) mod plc_s7;
pub(crate) mod plc_snapshot_policy;
pub(crate) mod rust_snap7_adapter;
