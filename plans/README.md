# Architecture Task Catalog

Chinese version: [README.zh-CN.md](README.zh-CN.md)

This catalog links only role documents that currently exist. `tasks.md` is created only after exact Human Owner approval of its PM Revision; `checklist.md` is created only after `developer_handoff` by fresh-context Verification.

| Task | Aggregate status | PM scope | Development | Verification |
| --- | --- | --- | --- | --- |
| ARCH-MULTI-001 v1/v2 Stack and Multi-backend Roadmap | `draft` | [spec.md](ARCH-MULTI-001-versioned-stack-roadmap/spec.md); Owner direction recorded | Pending scoped implementation tasks and exact Revision approval | Pending developer handoffs |
| ARCH-DOCKER-002 Reusable Docker Deployment | `developer_handoff` | [spec.md](ARCH-DOCKER-002-reusable-deployment/spec.md) | [tasks.md](ARCH-DOCKER-002-reusable-deployment/tasks.md); r2 static self-check passed | Pending fresh-context Verification |
| ARCH-001 Public Architecture Baseline Extraction | `owner_accepted` | [spec.md](ARCH-001-public-architecture-baseline-extraction/spec.md) | [tasks.md](ARCH-001-public-architecture-baseline-extraction/tasks.md) | [checklist.md](ARCH-001-public-architecture-baseline-extraction/checklist.md); Human Owner accepted r3 |
| ARCH-MIG-001 Core-only Migration Baseline | `owner_accepted` | [spec.md](ARCH-MIG-001-core-migration-baseline/spec.md) | [tasks.md](ARCH-MIG-001-core-migration-baseline/tasks.md) | [checklist.md](ARCH-MIG-001-core-migration-baseline/checklist.md); Human Owner accepted r1 |
| ARCH-DOCKER-001 Empty-volume Docker Runtime Proof | `owner_accepted` | [spec.md](ARCH-DOCKER-001-empty-volume-runtime-proof/spec.md) | [tasks.md](ARCH-DOCKER-001-empty-volume-runtime-proof/tasks.md) | [checklist.md](ARCH-DOCKER-001-empty-volume-runtime-proof/checklist.md); Human Owner accepted r1 |
| ARCH-DEV-001 Local Development Environment Adoption | `owner_accepted` | [spec.md](ARCH-DEV-001-local-development-environment-adoption/spec.md) | [tasks.md](ARCH-DEV-001-local-development-environment-adoption/tasks.md) | [checklist.md](ARCH-DEV-001-local-development-environment-adoption/checklist.md); Human Owner accepted r4 |
| ARCH-REL-001 Source Release 1.0.0 | `owner_accepted` | [spec.md](ARCH-REL-001-source-release-1.0.0/spec.md) | [tasks.md](ARCH-REL-001-source-release-1.0.0/tasks.md) records r3 preparation, publication evidence and the §5.4 receipt handoff; superseded r1/r2 Development history is retained | [checklist.md](ARCH-REL-001-source-release-1.0.0/checklist.md); `qa_passed` and Human Owner final acceptance recorded; §5.4 receipt pending manual main-only push |
| ARCH-FE-001 Frontend Module Auto Assembly | `draft` | [spec.md](ARCH-FE-001-frontend-module-auto-assembly/spec.md) | Pending blocker closure and exact Revision approval | Pending `developer_handoff` |
| ARCH-FE-002 Project Frontend Role Access and Module Pilot | `owner_accepted` | [spec.md](ARCH-FE-002-project-role-access-and-module-pilot/spec.md); Owner-approved r4 | [tasks.md](ARCH-FE-002-project-role-access-and-module-pilot/tasks.md); r4 developer_handoff | [checklist.md](ARCH-FE-002-project-role-access-and-module-pilot/checklist.md); independent r4 qa_passed, r2/r3 history retained; Human Owner accepted r4 on 2026-10-09 |
| ARCH-FE-004 Frontend System Name Configuration | `draft` | [spec.md](ARCH-FE-004-system-name-env-configuration/spec.md); r1 bilingual build-time system names | Pending exact Human Owner r1 approval | Pending developer_handoff |
| ARCH-BE-001 Backend Role API Permissions | `qa_passed` | [spec.md](ARCH-BE-001-role-api-permissions/spec.md); r3 approved format restoration | [tasks.md](ARCH-BE-001-role-api-permissions/tasks.md); r3 developer_handoff | [checklist.md](ARCH-BE-001-role-api-permissions/checklist.md); r1/r2 history retained, r3 independently qa_passed; Owner final acceptance pending |
| CA-CONFIG-001 Packaged Configuration Management | `draft` | [spec.md](CA-CONFIG-001-packaged-configuration-management/spec.md) | Pending baseline refresh and exact Revision approval | Pending `developer_handoff` |

The root [PLAN.md](../PLAN.md) is the prioritized dashboard. Scope, implementation evidence and independent verdict remain in each task's role-owned documents.
