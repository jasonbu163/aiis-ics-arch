<!--
  File Path: /contracts/published/http-api/control-agent-authorization-verify.md
  Description: Planned backend authorization verification API contract
  Main Features:
    - Defines the provider-side HTTP contract for control-agent authorization
    - Keeps the endpoint scoped to verification instead of remote execution
-->
# Control-Agent Authorization Verify API

[中文版本](control-agent-authorization-verify.zh-CN.md)

## Contract Metadata

| Field | Value |
| --- | --- |
| Status | `implemented` |
| Consumer | `control-agent` |
| Provider | backend HTTP API |
| Implemented endpoints | `GET /api/v1/control-agent/action-scopes`; `POST /api/v1/control-agent/gate-tokens`; `POST /api/v1/control-agent/authorization/verify` |
| Source of truth after implementation | backend route, schema and OpenAPI |
| Related demand | `contracts/demands/control-agent/high-risk-authorization-gate.md` |

## Action Scope Registry Endpoint

```http
GET /api/v1/control-agent/action-scopes
Authorization: Bearer <backendAccessToken>
```

Authenticated `admin` and `supervisor` users can read this registry. `operator` users are forbidden.

Response:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "registryVersion": "2026-06-24-control-agent-gate-v1",
    "defaultScope": "authorization.self_test",
    "items": [
      {
        "actionScope": "authorization.self_test",
        "riskLevel": "self_test",
        "status": "implemented",
        "requiresGateToken": true,
        "defaultResourceId": "control-agent",
        "payloadHashStrategy": "fixed_self_test",
        "samplePayloadHash": "sha256:self-test-payload",
        "allowedSubjectRoles": ["admin", "supervisor"],
        "titleKey": "controlAgent.authorization.scope.selfTest.title",
        "descriptionKey": "controlAgent.authorization.scope.selfTest.description"
      }
    ]
  }
}
```

The current registry deliberately publishes only `authorization.self_test`. Real high-risk actions must be added here before CA or frontend UI can enable them.

## Issue Gate Token Endpoint

```http
POST /api/v1/control-agent/gate-tokens
Authorization: Bearer <backendAccessToken>
Content-Type: application/json
```

Only the highest-privilege user group can issue a token. The issuer must explicitly name the target user by both id and username.

Request:

```json
{
  "subjectUserId": 2,
  "subjectUsername": "supervisor",
  "durationHours": 2
}
```

Rules:

- `subjectUserId` and `subjectUsername` must identify the same active backend user.
- The target user role must be `admin` or `supervisor`.
- `operator` users cannot receive gate tokens.
- `durationHours` must be between 1 and 12.
- The default duration is 2 hours.
- The response returns the raw token once.
- The database stores only `tokenHash`, not the raw token.
- The token is bound to `subjectUserId` / `subjectUsername`; both fields are verified when the token is used.

Response:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "gateToken": "<opaque-token>",
    "tokenId": 1,
    "subjectUserId": 2,
    "subjectUsername": "supervisor",
    "subjectRole": "supervisor",
    "issuedByUserId": 1,
    "issuedByUsername": "admin",
    "issuedByRole": "admin",
    "allowedScopes": ["authorization.self_test"],
    "resourceScope": "*",
    "expiresAt": "2026-06-24T12:00:00Z",
    "failClosed": true
  }
}
```

## Verify Authorization Endpoint

```http
POST /api/v1/control-agent/authorization/verify
Authorization: Bearer <gateToken>
Content-Type: application/json
```

## Request Body

```json
{
  "operatorUserId": 2,
  "operatorUsername": "supervisor",
  "actionScope": "authorization.self_test",
  "resourceId": "control-agent",
  "payloadHash": "sha256:self-test-payload"
}
```

## Success Response

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "allowed": true,
    "decision": "allowed",
    "approvalId": "auth-20260624-000001",
    "operatorUserId": 2,
    "operatorUsername": "supervisor",
    "actionScope": "authorization.self_test",
    "resourceId": "control-agent",
    "payloadHash": "sha256:self-test-payload",
    "expiresAt": "2026-06-24T12:00:00Z",
    "failClosed": true
  }
}
```

## Denied Response

Denied business decisions should still return the standard response envelope:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "allowed": false,
    "decision": "scope_not_allowed",
    "approvalId": null,
    "operatorUserId": 2,
    "operatorUsername": "supervisor",
    "actionScope": "unknown.action",
    "resourceId": "control-agent",
    "payloadHash": "sha256:self-test-payload",
    "expiresAt": null,
    "failClosed": true
  }
}
```

Authentication failures should use the backend authentication behavior. Permission failures should use the backend permission behavior.

## First Allowed Scope

The first allowed scope is:

```text
authorization.self_test
```

This proves the gate without enabling any field action. It returns `allowed=true` only for an active gate token bound to the same operator user id and username.

## Frontend / CA Usage Notes

`gateToken` is a temporary key. It is not an action permission by itself.

The verify request still needs an explicit action descriptor:

- `actionScope` is a backend-published action key. It must come from `GET /api/v1/control-agent/action-scopes` or this contract. Do not let users type arbitrary strings in production UI.
- `resourceId` identifies the target resource of this action. For the current self-test, use `control-agent`. Future examples may look like `plan:123` or `device:line-1`.
- `payloadHash` binds the approval check to the exact action payload. For the current self-test, use `sha256:self-test-payload`. Future CA clients should compute this value from a canonical JSON payload before verification.

Swagger UI testing note:

1. Authorize Swagger with an admin backend access token.
2. Issue a gate token through `/control-agent/gate-tokens`.
3. Replace the Swagger authorization token with the returned `gateToken`.
4. Call `/control-agent/authorization/verify` with `authorization.self_test`, `control-agent` and `sha256:self-test-payload`.

If Swagger defaults such as `actionScope: "string"` are submitted, the correct result is `allowed=false` with `decision=scope_not_allowed`.

Future work:

- Add real high-risk actions to the backend action-scope registry after their business operation, resource id and payload hash rules are documented.
- Extend token issuance with `allowedScopes` and `resourceScope` only after the first action registry is stable.
- Keep real high-risk buttons disabled until the action registry, payload hash canonicalization and audit path are documented.

## Provider Rules

- The verify API verifies authorization only.
- The verify API must not create, claim, cancel, pause, resume, or execute command rows.
- Token issuance stores only the token hash.
- Low-permission users cannot issue gate tokens.
- Gate token issuers must be `admin`.
- Gate token subjects may be `admin` or `supervisor`.
- Gate token subjects are identified by both `subjectUserId` and `subjectUsername`.
- The action-scope registry is read-only and must not execute actions.
- The API must not contact PLCs or field devices.
- Response data must serialize to camelCase.
- `failClosed` must be true.
- Unknown scopes must deny.

## Backend Implementation Notes

Implemented module:

```text
backend/app/control_agent/
  api/routes.py
  schemas/authorization.py
  services/async_authorization.py
```

Implemented tests:

```text
backend/tests/test_control_agent_authorization.py
```

Current verification note:

- The module compiles.
- Direct service validation passes.
- FastAPI route registration includes the implemented endpoints.
- Full API tests are blocked by local MySQL root test-database initialization.

## Verification

- Valid admin or supervisor JWT can read the action-scope registry.
- `operator` users cannot read the action-scope registry.
- Valid admin JWT can issue a gate token for an active `admin` or `supervisor` subject.
- Valid gate token + matching `operatorUserId` / `operatorUsername` + `authorization.self_test` returns `allowed=true`.
- Missing or invalid gate token returns fail-closed denial or backend auth rejection.
- Non-authorized user cannot issue gate tokens.
- `operator` users cannot receive gate tokens.
- Unknown `actionScope` returns `allowed=false`.
- Response envelope contains `code`, `message`, and `data`.
- Nested data uses camelCase fields.
