//! File Path: /control-agent/src-tauri/src/domain/authorization.rs
//! Description: Authorization gate domain structures
//! Main Features:
//!   - Defines disabled-by-default high-risk authorization gate snapshots
//!   - Describes local self-test evidence without storing secrets
//!   - Keeps authorization DTOs separate from Tauri runtime bootstrap

use serde::Serialize;

pub(crate) struct AuthorizationCheckRequest {
    pub(crate) operator_id: String,
    pub(crate) action_scope: String,
    pub(crate) resource_id: String,
    pub(crate) payload_hash: String,
    pub(crate) temporary_token_present: bool,
    pub(crate) approval_id: String,
    pub(crate) requested_at_unix_seconds: u64,
    pub(crate) expires_at_unix_seconds: u64,
}

pub(crate) struct AuthorizationCheckResponse {
    pub(crate) approved: bool,
    pub(crate) approval_id: String,
    pub(crate) result: String,
    pub(crate) expires_at_unix_seconds: u64,
    pub(crate) error_message: String,
}

#[derive(Serialize)]
pub(crate) struct AuthorizationSelfTestSnapshot {
    pub(crate) attempted: bool,
    pub(crate) passed: bool,
    pub(crate) provider: String,
    pub(crate) operator_id: String,
    pub(crate) action_scope: String,
    pub(crate) resource_id: String,
    pub(crate) payload_hash: String,
    pub(crate) temporary_token_present: bool,
    pub(crate) approval_id: String,
    pub(crate) expires_at_unix_seconds: u64,
    pub(crate) result: String,
    pub(crate) error_message: String,
}

#[derive(Serialize)]
pub(crate) struct AuthorizationGateSnapshot {
    pub(crate) enabled: bool,
    pub(crate) high_risk_auth_required: bool,
    pub(crate) upper_system_url_configured: bool,
    pub(crate) timeout_ms: u64,
    pub(crate) fail_closed: bool,
    pub(crate) local_operator_required: bool,
    pub(crate) self_test: AuthorizationSelfTestSnapshot,
}
