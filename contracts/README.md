<!--
  File Path: /contracts/README.md
  Description: Contract hub index for cross-role development
  Main Features:
    - Defines demand, published contract and gate boundaries
    - Separates frontend API contracts from control-agent runtime contracts
-->
# Contract Hub

[中文版本](README.zh-CN.md)

`contracts/` is the project-level contract hub for cross-role and cross-process development.

It records:

- What a consumer needs.
- What a provider commits to expose.
- Which source of truth owns the final implementation.
- Which gate proves the contract is ready to consume.

This directory is not a replacement for OpenAPI, Pydantic schemas, Alembic migrations, or the `control-agent` command-table contract. It is the coordination layer that points to those sources of truth.

## Directory Map

| Path | Purpose |
| --- | --- |
| `demands/` | Consumer-side requirements before implementation. Consumers include `frontend-js`, `control-agent`, third-party clients, backend services, or external systems. |
| `published/` | Provider-side committed contracts. Providers include backend HTTP APIs, runtime database contracts, command tasks, events, and future external adapters. |
| `gates/` | Readiness checks that decide whether a contract can be implemented or consumed. |

## Status Model

Each contract should use one of these statuses:

| Status | Meaning |
| --- | --- |
| `proposed` | A consumer has requested a capability, but the provider has not accepted the shape. |
| `accepted` | The provider accepts the direction and can implement or publish a contract. |
| `implemented` | Code exists, but verification may still be incomplete. |
| `verified` | Tests, build checks, integration checks, or manual acceptance prove the contract works. |
| `deprecated` | The contract is replaced or no longer used. |

## Boundary Rules

- Backend HTTP APIs remain the business and third-party integration surface.
- `control-agent` internal site-runtime behavior may use explicit direct database contracts.
- Backend APIs must not become a remote-control surface for a running `control-agent`.
- HTTP response shape, schema aliases, error codes and OpenAPI truth stay in backend code.
- Database schema truth stays in SQLAlchemy models and Alembic migrations.
- Contract documents must link back to the owning source of truth.

## Current Active Contract Threads

| Thread | Consumer | Provider | Status |
| --- | --- | --- | --- |
| [High-risk authorization gate](demands/control-agent/high-risk-authorization-gate.md) | `control-agent` | backend HTTP API | `accepted` |
| [Control-agent authorization verify API](published/http-api/control-agent-authorization-verify.md) | `control-agent` | backend HTTP API | `implemented` |
| [Control-agent preflight gate](gates/control-agent-preflight.md) | project delivery | backend + `control-agent` | `proposed` |
| [AW facts integration](demands/automation-world-facts-integration.md) · [中文](demands/automation-world-facts-integration.zh-CN.md) | DAA / SMA / HTTP consumers | Backend facts + typed business modules | `proposed`; ARCH-AW-008 document scope only |

## PLC facts provider v1

[PLC facts v1](published/http-api/plc-facts-v1/README.md) fixes the anonymous batch/latest/history source contract, strict Decimal JSON, durable outcomes, publication cursors and finite retention. The machine artifacts describe source implementation; database adoption, runtime verification, DAA integration and deployment have separate gates.


[Business integration v1](published/http-api/business-integration-v1/README.md) publishes the eight typed anonymous business operations, closed schemas, examples and digest vectors. BE010 r2 source remains unadopted; actual target adoption and database/B require separate approval.
