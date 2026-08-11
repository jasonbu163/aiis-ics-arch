# Architecture Task Catalog

Chinese version: [README.zh-CN.md](README.zh-CN.md)

This catalog links only role documents that currently exist. `tasks.md` is created only after exact Human Owner approval of its PM Revision; `checklist.md` is created only after `developer_handoff` by fresh-context Verification.

| Task | Aggregate status | PM scope | Development | Verification |
| --- | --- | --- | --- | --- |
| ARCH-001 Public Architecture Baseline Extraction | `developer_handoff` | [spec.md](ARCH-001-public-architecture-baseline-extraction/spec.md) | [tasks.md](ARCH-001-public-architecture-baseline-extraction/tasks.md) | Existing [checklist.md](ARCH-001-public-architecture-baseline-extraction/checklist.md) is the historical r2 `qa_blocked` record; fresh-context r3 Verification is next |
| ARCH-MIG-001 Core-only Migration Baseline | `owner_accepted` | [spec.md](ARCH-MIG-001-core-migration-baseline/spec.md) | [tasks.md](ARCH-MIG-001-core-migration-baseline/tasks.md) | [checklist.md](ARCH-MIG-001-core-migration-baseline/checklist.md); Human Owner accepted r1 |
| ARCH-DOCKER-001 Empty-volume Docker Runtime Proof | `owner_accepted` | [spec.md](ARCH-DOCKER-001-empty-volume-runtime-proof/spec.md) | [tasks.md](ARCH-DOCKER-001-empty-volume-runtime-proof/tasks.md) | [checklist.md](ARCH-DOCKER-001-empty-volume-runtime-proof/checklist.md); Human Owner accepted r1 |
| ARCH-FE-001 Frontend Module Auto Assembly | `draft` | [spec.md](ARCH-FE-001-frontend-module-auto-assembly/spec.md) | Pending blocker closure and exact Revision approval | Pending `developer_handoff` |
| CA-CONFIG-001 Packaged Configuration Management | `draft` | [spec.md](CA-CONFIG-001-packaged-configuration-management/spec.md) | Pending baseline refresh and exact Revision approval | Pending `developer_handoff` |

The root [PLAN.md](../PLAN.md) is the prioritized dashboard. Scope, implementation evidence and independent verdict remain in each task's role-owned documents.
