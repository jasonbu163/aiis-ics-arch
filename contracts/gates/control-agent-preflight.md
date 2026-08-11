<!--
  File Path: /contracts/gates/control-agent-preflight.md
  Description: Control-agent gate preflight checklist
  Main Features:
    - Tracks backend readiness before CA authorization wiring
    - Separates authorization verification from command execution
-->
# Control-Agent Preflight Gate

[中文版本](control-agent-preflight.zh-CN.md)

## Scope

This gate decides whether the project is ready to implement the `control-agent` authorization client for future high-risk actions.

It does not approve real field action execution by itself.

## Backend Readiness

- [x] `POST /api/v1/control-agent/gate-tokens` exists.
- [x] `GET /api/v1/control-agent/action-scopes` exists.
- [x] `POST /api/v1/control-agent/authorization/verify` exists.
- [x] The endpoint requires authentication.
- [x] The endpoint requires a permission appropriate for control-agent authorization.
- [x] Only the highest-privilege user group can issue gate tokens.
- [x] Gate tokens are stored as hashes and returned raw only once.
- [x] Gate tokens are bound to an explicit `admin` or `supervisor` subject by both id and username.
- [x] Gate token duration is constrained to 1-12 hours.
- [x] `authorization.self_test` returns `allowed=true` for an authorized operator in service validation.
- [x] The current self-test action scope is discoverable through the backend registry API.
- [x] Unknown action scopes return `allowed=false` in service validation.
- [x] Invalid tokens fail closed in service behavior.
- [ ] Expired, revoked and database-backed token checks pass through API tests.
- [x] Response data includes `allowed`, `decision`, `approvalId`, `operatorUserId`, `operatorUsername`, `actionScope`, `resourceId`, `payloadHash`, `expiresAt`, and `failClosed`.
- [x] Response data serializes to camelCase.
- [x] Backend tests cover success, deny, authentication failure, permission failure and response contract shape.
- [x] The API does not create, claim, execute, cancel, pause, resume or recover command rows.

## Contract Readiness

- [x] Consumer demand exists.
- [x] Provider API contract exists.
- [x] The contract states that backend API is an authorization gate, not a remote-control endpoint.
- [x] The contract documents the backend action-scope registry endpoint.
- [x] Backend route implementation matches the published contract shape.
- [ ] Any deviation from this contract is recorded before CA implementation starts.

## Control-Agent Readiness

- [ ] CA has a configuration value for the backend authorization URL.
- [ ] CA sends the token through the authorization header, not in logs or query strings.
- [ ] CA sends `operatorUserId`, `operatorUsername`, `actionScope`, `resourceId`, and `payloadHash`.
- [ ] CA refuses high-risk actions when the backend call denies, times out, fails, or returns invalid data.
- [ ] CA logs authorization evidence without writing raw secrets.
- [ ] CA still does not use backend API as a command-execution path.

## Verification Commands

Backend:

```bash
uv run pytest tests/test_control_agent_authorization.py tests/test_response_contract.py
```

Control-agent:

```bash
pnpm --dir control-agent build
cargo fmt --manifest-path control-agent/src-tauri/Cargo.toml --check
cargo test --manifest-path control-agent/src-tauri/Cargo.toml
```

Repository:

```bash
git diff --check
```
