# AIIS ICS Architecture Plan

Chinese version: [PLAN.zh-CN.md](PLAN.zh-CN.md)

## Current source baseline

- Baseline source version: `1.0.0` (source record only; no tag, branch, hosted release, or deployment is implied).
- Core surfaces: `backend/`, `frontend-js/`, `control-agent/`, `tools/`, `contracts/`.
- Project-specific modules and inputs belong to consuming project repositories.

## Architecture workstreams

| Workstream | Status | Record | Boundary |
| --- | --- | --- | --- |
| Public Core extraction | `owner_accepted` | [ARCH-001 spec](plans/ARCH-001-public-architecture-baseline-extraction/spec.md) | Human Owner accepted r3 after fresh-context Verification passed the public-safe Core, smoke/dev/release-check and cleanup audit |
| Core migration baseline | `owner_accepted` | [ARCH-MIG-001 spec](plans/ARCH-MIG-001-core-migration-baseline/spec.md) | Human Owner accepted the single `d4e6f8a0b2c4` Core root and fourteen-table source/static/no-DB baseline |
| Empty-volume Docker runtime proof | `owner_accepted` | [ARCH-DOCKER-001 spec](plans/ARCH-DOCKER-001-empty-volume-runtime-proof/spec.md) | Human Owner accepted r1 after fresh-context Verification passed the isolated MySQL 8.4.6 build/migrate/health/proxy/cleanup proof |
| Local development environment adoption | `owner_accepted` | [ARCH-DEV-001 spec](plans/ARCH-DEV-001-local-development-environment-adoption/spec.md) | Human Owner accepted r4 after the fixed-name dev runtime, health/frontend checks, bootstrap default-off proof and retired-smoke documentation cleanup |
| Source release 1.0.0 | `draft` | [ARCH-REL-001 spec](plans/ARCH-REL-001-source-release-1.0.0/spec.md) | PM r1 defines a source-only `release/1.0.0` branch plus annotated `v1.0.0` tag; Human Owner approval is pending and no release refs are authorized yet |
| Frontend module assembly | `draft` | [ARCH-FE-001 spec](plans/ARCH-FE-001-frontend-module-auto-assembly/spec.md) | Manifest-driven menu/permission assembly; not part of Core extraction |
| Packaged CA configuration | `draft` | [CA-CONFIG-001 spec](plans/CA-CONFIG-001-packaged-configuration-management/spec.md) | Database type/address settings and YAML upload UI |

## Deferred boundaries

ARCH-MIG-001 r1 and ARCH-DOCKER-001 r1 are owner-accepted. The MIT license and stated ownership are retained,
but production Docker topology, real PLC/CA operation and project module migration remain separate Human Owner
gates. Git/GitHub source publication is now scoped only by the draft ARCH-REL-001 r1 and remains unauthorized
until its exact Revision is approved.

Keep this file as a concise index. Detailed scope, commands and evidence belong to the owning task bundle.
