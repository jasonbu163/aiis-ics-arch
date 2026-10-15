# AIIS ICS Architecture Plan

Chinese version: [PLAN.zh-CN.md](PLAN.zh-CN.md)

## Current source baseline

- Baseline source version: `1.0.0` (the annotated `v1.0.0` tag and `release/1.x.x` maintenance branch are
  verified; no hosted release or deployment is implied).
- Current working-tree surfaces: `backend/`, `frontend-js/`, `automation-world/`, `tools/`, `contracts/`; CA is relocated under AW and frozen, while DAA/SMA initialization is tracked below.
- Project-specific modules and inputs belong to consuming project repositories.

## Architecture workstreams

| Workstream | Status | Record | Boundary |
| --- | --- | --- | --- |
| Three-world architecture roadmap | `qa_passed` | [ARCH-MULTI-001 spec](plans/ARCH-MULTI-001-versioned-stack-roadmap/spec.md) | r2 [ROADMAP](ROADMAP.md) pair delivered; independent document QA passed AC1–AC10; Human Owner final review pending; no code changes |
| AW Agent foundation | `owner_accepted` | [ARCH-AW-001 spec](plans/ARCH-AW-001-agent-foundation/spec.md) | CA relocated/frozen; DAA/SMA initialize and start independently; focused review passed; Human Owner accepted r1 on 2026-10-14; no further tests added; UI/SQLite work deferred |
| AW Whitepaper and Runtime Design | `qa_passed` | [ARCH-AW-002 spec](plans/ARCH-AW-002-agent-runtime-design/spec.md) | r2 whitepaper and detailed runtime design delivered; independent document QA passed AC1–AC11; Human Owner final review pending; no code changes |
| Reusable Docker deployment | `developer_handoff` | [ARCH-DOCKER-002 spec](plans/ARCH-DOCKER-002-reusable-deployment/spec.md) | r2 implemented; three Compose static checks passed; old root entry retired; fresh-context Verification pending, runtime separately gated |
| Public Core extraction | `owner_accepted` | [ARCH-001 spec](plans/ARCH-001-public-architecture-baseline-extraction/spec.md) | Human Owner accepted r3 after fresh-context Verification passed the public-safe Core, smoke/dev/release-check and cleanup audit |
| Core migration baseline | `owner_accepted` | [ARCH-MIG-001 spec](plans/ARCH-MIG-001-core-migration-baseline/spec.md) | Human Owner accepted the single `d4e6f8a0b2c4` Core root and fourteen-table source/static/no-DB baseline |
| Empty-volume Docker runtime proof | `owner_accepted` | [ARCH-DOCKER-001 spec](plans/ARCH-DOCKER-001-empty-volume-runtime-proof/spec.md) | Human Owner accepted r1 after fresh-context Verification passed the isolated MySQL 8.4.6 build/migrate/health/proxy/cleanup proof |
| Local development environment adoption | `owner_accepted` | [ARCH-DEV-001 spec](plans/ARCH-DEV-001-local-development-environment-adoption/spec.md) | Human Owner accepted r4 after the fixed-name dev runtime, health/frontend checks, bootstrap default-off proof and retired-smoke documentation cleanup |
| Source release 1.0.0 | `owner_accepted` | [ARCH-REL-001 spec](plans/ARCH-REL-001-source-release-1.0.0/spec.md) | Fresh-context Verification passed r3 and Human Owner accepted it; the §5.4 main-only governance receipt is prepared but still pending Human Owner manual push |
| Frontend module assembly | `draft` | [ARCH-FE-001 spec](plans/ARCH-FE-001-frontend-module-auto-assembly/spec.md) | Manifest-driven menu/permission assembly; not part of Core extraction |
| Project frontend role access and module pilot | `owner_accepted` | [ARCH-FE-002 spec](plans/ARCH-FE-002-project-role-access-and-module-pilot/spec.md) | r4 independently passed brand, configuration, startup, build and public browser checks; r2/r3 history retained; Human Owner accepted r4 on 2026-10-09; remaining modules reserved for 003 |
| Remaining frontend module manifest adaptation | `owner_accepted` | [ARCH-FE-003 spec](plans/ARCH-FE-003-remaining-module-manifest-adaptation/spec.md) | r2 price page uses auxiliary APIs directly; checker, 36 tests and isolated build passed independent verification; Human Owner accepted r2 on 2026-10-12 and reported successful env page-access testing; r1 history retained |
| Frontend system name and subtitle configuration | `owner_accepted` | [ARCH-FE-004 spec](plans/ARCH-FE-004-system-name-env-configuration/spec.md) | Human Owner reported successful testing and accepted r3 on 2026-10-10 after independent static verification; r1/r2 history and original evidence retained |
| Backend role API permissions | `qa_passed` | [ARCH-BE-001 spec](plans/ARCH-BE-001-role-api-permissions/spec.md) | r3 restores eleven English env section headings; values/comments preserved; independent QA passed; Human Owner final acceptance pending |
| Energy price backend API | `owner_accepted` | [ARCH-BE-002 spec](plans/ARCH-BE-002-energy-price-api/spec.md) | r3 approved for reusable auxiliary in this repository; three APIs, independent permissions and explicit migration; Independent QA passed; Human Owner accepted r3 on 2026-10-13, live DB operations deferred |
| Mapping Service API pilot | `draft` | [ARCH-BE-003 spec](plans/ARCH-BE-003-mapping-service-api-pilot/spec.md) | r2 targets this repository equipment; four business choices confirmed and hourly-storage analysis recorded; temperature granularity and exact scope approval pending; existing backend mapping retained |
| Hourly prices and daily history | `owner_accepted` | [ARCH-BE-004 spec](plans/ARCH-BE-004-energy-price-hourly-history/spec.md) | r2 independent QA passed: 211 backend, 38 frontend tests and browser verification; F-001 closed, Human Owner accepted on 2026-10-13 after successful manual use; live data migration separately gated |
| Backend business module reintegration | `qa_blocked` | [ARCH-BE-005 spec](plans/ARCH-BE-005-backend-business-module-reintegration/spec.md) | r3 A independently passed: 319 source tests and browser checks; B MySQL/Docker actions await specific approval and verification; final acceptance pending |
| Packaged CA configuration | `draft` | [CA-CONFIG-001 spec](plans/CA-CONFIG-001-packaged-configuration-management/spec.md) | Database type/address settings and YAML upload UI |

## Deferred boundaries

ARCH-MIG-001 r1, ARCH-DOCKER-001 r1 and ARCH-DEV-001 r4 are owner-accepted. The MIT license and stated
ownership are retained, but production Docker topology, real PLC/CA operation and project module migration remain
separate Human Owner gates. ARCH-REL-001 r3 is `owner_accepted` after fresh-context Verification recorded
`qa_passed` and Human Owner final acceptance. Its r1/r2 Development records and r2 main preparation commit
remain superseded history. The six-path §5.4 main-only governance receipt is prepared but still pending Human
Owner manual staging, commit and push; this status does not imply a GitHub Release, deployment or production
readiness.

Keep this file as a concise index. Detailed scope, commands and evidence belong to the owning task bundle.
