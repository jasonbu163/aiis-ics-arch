//! File Path: /control-agent/src-tauri/src/services/authorization_gate.rs
//! Description: Authorization gate diagnostic service
//! Main Features:
//!   - Builds the disabled-by-default high-risk authorization gate snapshot
//!   - Runs local self-test evidence without contacting an upper system
//!   - Keeps execution actions blocked while exposing gate readiness

use crate::config::AgentConfig;
use crate::domain::authorization::{
    AuthorizationCheckRequest, AuthorizationCheckResponse, AuthorizationGateSnapshot,
    AuthorizationSelfTestSnapshot,
};

pub(crate) fn build_authorization_gate_snapshot(
    config: &AgentConfig,
    now_unix_seconds: u64,
) -> AuthorizationGateSnapshot {
    let self_test = build_self_test_snapshot(config, now_unix_seconds);

    AuthorizationGateSnapshot {
        enabled: config.bool_or_default("CONTROL_AGENT_UPPER_SYSTEM_AUTH_ENABLED", false),
        high_risk_auth_required: config
            .bool_or_default("CONTROL_AGENT_HIGH_RISK_AUTH_REQUIRED", true),
        upper_system_url_configured: config.is_configured("CONTROL_AGENT_UPPER_SYSTEM_AUTH_URL"),
        timeout_ms: crate::config::parse_u64_or_default(
            &config.value_or_default("CONTROL_AGENT_UPPER_SYSTEM_AUTH_TIMEOUT_MS", "2000"),
            2000,
        ),
        fail_closed: true,
        local_operator_required: true,
        self_test,
    }
}

fn build_self_test_snapshot(
    config: &AgentConfig,
    now_unix_seconds: u64,
) -> AuthorizationSelfTestSnapshot {
    let attempted = config.bool_or_default("CONTROL_AGENT_AUTH_SELF_TEST_ENABLED", true);
    let provider = config.value_or_default("CONTROL_AGENT_AUTH_SELF_TEST_PROVIDER", "local_mock");
    let operator_id = config.value_or_default(
        "CONTROL_AGENT_AUTH_SELF_TEST_OPERATOR_ID",
        "local-self-test",
    );
    let action_scope = config.value_or_default(
        "CONTROL_AGENT_AUTH_SELF_TEST_ACTION_SCOPE",
        "authorization.self_test",
    );
    let resource_id =
        config.value_or_default("CONTROL_AGENT_AUTH_SELF_TEST_RESOURCE_ID", "control-agent");
    let payload_hash = config.value_or_default(
        "CONTROL_AGENT_AUTH_SELF_TEST_PAYLOAD_HASH",
        "sha256:self-test-payload",
    );
    let approval_id = config.value_or_default(
        "CONTROL_AGENT_AUTH_SELF_TEST_APPROVAL_ID",
        "local-self-test-approval",
    );
    let expires_in_seconds = crate::config::parse_u64_or_default(
        &config.value_or_default("CONTROL_AGENT_AUTH_SELF_TEST_EXPIRES_IN_SECONDS", "300"),
        300,
    );

    let request = AuthorizationCheckRequest {
        operator_id,
        action_scope,
        resource_id,
        payload_hash,
        temporary_token_present: config.is_configured("CONTROL_AGENT_AUTH_SELF_TEST_TOKEN"),
        approval_id,
        requested_at_unix_seconds: now_unix_seconds,
        expires_at_unix_seconds: now_unix_seconds.saturating_add(expires_in_seconds),
    };

    if !attempted {
        return AuthorizationSelfTestSnapshot {
            attempted,
            passed: false,
            provider,
            operator_id: request.operator_id,
            action_scope: request.action_scope,
            resource_id: request.resource_id,
            payload_hash: request.payload_hash,
            temporary_token_present: request.temporary_token_present,
            approval_id: request.approval_id,
            expires_at_unix_seconds: 0,
            result: "disabled".to_string(),
            error_message: String::new(),
        };
    }

    let response = evaluate_local_self_test(&provider, &request);

    AuthorizationSelfTestSnapshot {
        attempted,
        passed: response.approved,
        provider,
        operator_id: request.operator_id,
        action_scope: request.action_scope,
        resource_id: request.resource_id,
        payload_hash: request.payload_hash,
        temporary_token_present: request.temporary_token_present,
        approval_id: response.approval_id,
        expires_at_unix_seconds: response.expires_at_unix_seconds,
        result: response.result,
        error_message: response.error_message,
    }
}

fn evaluate_local_self_test(
    provider: &str,
    request: &AuthorizationCheckRequest,
) -> AuthorizationCheckResponse {
    if provider == "local_mock" {
        return AuthorizationCheckResponse {
            approved: true,
            approval_id: request.approval_id.clone(),
            result: "approved".to_string(),
            expires_at_unix_seconds: request.expires_at_unix_seconds,
            error_message: String::new(),
        };
    }

    AuthorizationCheckResponse {
        approved: false,
        approval_id: request.approval_id.clone(),
        result: "rejected".to_string(),
        expires_at_unix_seconds: request.requested_at_unix_seconds,
        error_message: "unsupported local authorization self-test provider".to_string(),
    }
}

#[cfg(test)]
mod tests {
    use std::collections::HashMap;

    use super::*;

    #[test]
    fn defaults_to_disabled_gate_with_passing_local_self_test() {
        let config = AgentConfig::from_values(HashMap::new());

        let snapshot = build_authorization_gate_snapshot(&config, 1_700_000_000);

        assert!(!snapshot.enabled);
        assert!(snapshot.high_risk_auth_required);
        assert!(!snapshot.upper_system_url_configured);
        assert!(snapshot.fail_closed);
        assert!(snapshot.local_operator_required);
        assert!(snapshot.self_test.attempted);
        assert!(snapshot.self_test.passed);
        assert_eq!(snapshot.self_test.provider, "local_mock");
        assert!(!snapshot.self_test.temporary_token_present);
    }

    #[test]
    fn rejects_unknown_self_test_provider_without_upper_system_call() {
        let config = AgentConfig::from_values(HashMap::from([(
            "CONTROL_AGENT_AUTH_SELF_TEST_PROVIDER".to_string(),
            "remote".to_string(),
        )]));

        let snapshot = build_authorization_gate_snapshot(&config, 1_700_000_000);

        assert!(snapshot.self_test.attempted);
        assert!(!snapshot.self_test.passed);
        assert_eq!(snapshot.self_test.result, "rejected");
        assert_eq!(
            snapshot.self_test.error_message,
            "unsupported local authorization self-test provider"
        );
    }
}
