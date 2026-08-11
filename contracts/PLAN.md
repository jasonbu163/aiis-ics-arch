<!--
  File Path: /contracts/PLAN.md
  Description: Contract hub development plan
  Main Features:
    - Tracks contract-hub rollout phases
    - Links the control-agent gate contract to backend and CA follow-up work
-->
# Contract Hub Plan

[中文版本](PLAN.zh-CN.md)

This plan tracks the rollout of the project-level contract hub.

## Goal

Create a repeatable mechanism for AI backend development, third-party frontend development, AI frontend development, control-agent runtime work, and backend/worker handoff.

The first real thread is the `control-agent` high-risk authorization gate.

## Phase K0. Contract Hub Baseline

Status: in progress.

Tasks:

- [x] Create `contracts/README.md`.
- [x] Create `contracts/README.zh-CN.md`.
- [x] Create `contracts/PLAN.md`.
- [x] Create `contracts/PLAN.zh-CN.md`.
- [x] Define the directory split: `demands/`, `published/`, and `gates/`.
- [x] Record the status lifecycle: `proposed`, `accepted`, `implemented`, `verified`, `deprecated`.

Acceptance:

- The directory explains what belongs in each contract layer.
- The contract hub does not claim to replace backend schemas, OpenAPI, migrations, or control-agent runtime docs.

## Phase K1. Control-Agent Authorization Demand

Status: accepted.

Tasks:

- [x] Promote the existing `control-agent` PLAN / COMMAND_CONTRACT authorization-gate requirement into a demand document.
- [x] Keep the demand consumer-owned: `control-agent` needs an upper-level authorization check before future high-risk actions.
- [x] Preserve the boundary that backend APIs verify authorization but do not remotely execute agent actions.

Acceptance:

- `contracts/demands/control-agent/high-risk-authorization-gate.md` exists.
- The demand links back to `control-agent/docs/COMMAND_CONTRACT.md`.

## Phase K2. Backend Published API Contract

Status: implemented, database-backed verification blocked by local MySQL root authorization.

Tasks:

- [x] Define the planned backend action-scope registry, gate-token issue API and authorization verify API.
- [x] Record request, response, permissions, token binding, fail-closed semantics and source-of-truth rules.
- [x] Add the `control_agent_gate_tokens` model and Alembic migration.
- [x] Implement the backend API module.
- [x] Add backend tests for action-scope registry access, token issue, admin-to-supervisor issue, denied, invalid token, operator mismatch, forbidden low-role subject and response-shape cases.
- [ ] Re-run backend API tests after local MySQL root test-database initialization is available.

Acceptance:

- `contracts/published/http-api/control-agent-authorization-verify.md` exists.
- Highest-privilege users can issue a temporary gate token for an active `admin` or `supervisor` subject identified by both id and username.
- `admin` and `supervisor` users can read the backend action-scope registry; `operator` users are rejected.
- Gate tokens are stored as hashes only, bind to the target subject and are valid for 1 to 12 hours.
- Backend implementation does not create a remote-control endpoint for `control-agent`.
- After database-backed verification is available, tests prove the response envelope and camelCase fields.

Current verification note:

- `uv run python -m compileall app/control_agent alembic/versions/20260624_1200_b4c5d6e7f8a9_add_control_agent_gate_tokens.py tests/test_control_agent_authorization.py tests/test_migrations.py` passes.
- Alembic script discovery reports the single head `b4c5d6e7f8a9`.
- FastAPI route registration includes `/api/v1/control-agent/action-scopes`, `/api/v1/control-agent/gate-tokens` and `/api/v1/control-agent/authorization/verify`.
- `uv run pytest tests/test_migrations.py` is blocked before test execution by the same MySQL root authorization error.
- `uv run pytest tests/test_control_agent_authorization.py tests/test_response_contract.py` is blocked before test execution by MySQL root authorization: `Access denied for user 'root'@'169.254.169.254'`.

## Phase K3. Control-Agent Preflight Gate

Status: proposed.

Tasks:

- [x] Create the first preflight checklist.
- [ ] Run the checklist after database-backed backend tests are unblocked.
- [ ] Return to the `control-agent` development thread and wire the authorization client only after the backend contract is implemented and verified.

Acceptance:

- `contracts/gates/control-agent-preflight.md` identifies the checks required before CA gate development.
- The gate separates backend readiness from CA implementation readiness.

## Verification Commands

Run these after implementation phases, as applicable:

```bash
uv run pytest tests/test_control_agent_authorization.py tests/test_response_contract.py
pnpm --dir control-agent build
cargo fmt --manifest-path control-agent/src-tauri/Cargo.toml --check
cargo test --manifest-path control-agent/src-tauri/Cargo.toml
git diff --check
```
