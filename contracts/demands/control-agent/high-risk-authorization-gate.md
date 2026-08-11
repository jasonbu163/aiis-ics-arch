<!--
  File Path: /contracts/demands/control-agent/high-risk-authorization-gate.md
  Description: Control-agent high-risk authorization demand
  Main Features:
    - Records the consumer-side gate requirement
    - Defines the minimum authorization data expected by control-agent
-->
# High-Risk Authorization Gate Demand

[中文版本](high-risk-authorization-gate.zh-CN.md)

## Contract Metadata

| Field | Value |
| --- | --- |
| Status | `accepted` |
| Consumer | `control-agent` |
| Provider candidate | backend HTTP API |
| Source demand | `control-agent/docs/COMMAND_CONTRACT.md` |
| Implementation owner | backend first, then `control-agent` client wiring |
| Gate | `contracts/gates/control-agent-preflight.md` |

## Demand

`control-agent` needs an upper-level authorization check before future high-risk local actions create field side effects.

The operator starts the action locally. The backend or upper-level system verifies whether the action is allowed. The backend must not directly invoke the running agent or execute the action on behalf of the agent.

## Minimum Request Data

| Field | Meaning |
| --- | --- |
| `operatorUserId` | Backend user id using the gate token. |
| `operatorUsername` | Backend username using the gate token. |
| `actionScope` | Stable action key, such as `authorization.self_test` or a future high-risk action key. |
| `resourceId` | Target resource identifier, such as `control-agent`, `plan:123`, or a device key. |
| `payloadHash` | Hash of the action payload or summary, used for anti-replay binding. |
| `temporaryToken` | Gate token issued by the backend and supplied through the authorization header. |

## Minimum Response Data

| Field | Meaning |
| --- | --- |
| `allowed` | Boolean allow/deny decision. |
| `decision` | Stable decision key: `allowed`, `denied`, `expired`, `invalid_token`, `scope_not_allowed`, or `not_configured`. |
| `approvalId` | Stable approval id when allowed. |
| `operatorUserId` | Authorized operator user id after backend verification. |
| `operatorUsername` | Authorized operator username after backend verification. |
| `actionScope` | Authorized action scope. |
| `resourceId` | Authorized resource id. |
| `payloadHash` | Payload hash echoed back when accepted. |
| `expiresAt` | Expiry timestamp for the approval. |
| `failClosed` | Always true for high-risk actions unless a separate emergency exception is documented. |

## Non-Goals

- This demand does not request a remote-control endpoint for `control-agent`.
- This demand does not request backend-side command execution.
- This demand does not move command claiming, heartbeat, resource locks, or execution checkpoints into HTTP request handling.

## Acceptance

- Backend publishes an authorization verify contract.
- Only the highest-privilege user group can issue a temporary gate token.
- The gate token issuer is `admin`.
- The gate token subject can be `admin` or `supervisor`, and must be specified by both id and username.
- The gate token cannot be used by another operator user id or username.
- Gate token duration is between 1 and 12 hours.
- Invalid, missing, expired, or unauthorized tokens fail closed.
- Unknown action scopes fail closed.
- The response uses the standard backend response envelope.
- The final CA implementation logs authorization evidence before field side effects.
