//! File Path: /control-agent/src-tauri/src/domain/headless_runtime.rs
//! Description: Headless Control Agent command and response contracts
//! Main Features:
//!   - Defines the JSON Lines request envelope for the standalone runtime
//!   - Defines stable command result envelopes without duplicating PLC payload models

use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Debug, Deserialize)]
pub(crate) struct HeadlessRuntimeRequest {
    pub(crate) request_id: String,
    pub(crate) action: String,
    #[serde(default)]
    pub(crate) target: Option<String>,
}

#[derive(Serialize)]
pub(crate) struct HeadlessRuntimeResponse {
    pub(crate) event: String,
    pub(crate) request_id: String,
    pub(crate) action: String,
    pub(crate) target: String,
    pub(crate) accepted: bool,
    pub(crate) status: String,
    pub(crate) payload: Value,
    pub(crate) error: Option<String>,
}

impl HeadlessRuntimeResponse {
    pub(crate) fn result(
        request_id: String,
        action: String,
        target: String,
        accepted: bool,
        status: String,
        payload: Value,
        error: Option<String>,
    ) -> Self {
        Self {
            event: "ca_runtime_command_result".to_string(),
            request_id,
            action,
            target,
            accepted,
            status,
            payload,
            error,
        }
    }

    pub(crate) fn rejected(
        request_id: String,
        action: String,
        target: String,
        error: String,
    ) -> Self {
        Self {
            event: "ca_runtime_command_result".to_string(),
            request_id,
            action,
            target,
            accepted: false,
            status: "rejected".to_string(),
            payload: Value::Null,
            error: Some(error),
        }
    }
}
