# Field Flow Task Catalog

Chinese version: [README.zh-CN.md](README.zh-CN.md)

FF task bundles live here. The historical Task ID is retained during relocation; the repository catalog links this unique owning bundle.

| Task | Status | PM scope | Development | Verification |
| --- | --- | --- | --- | --- |
| FF-001 Dual Runtimes and demo01 | `qa_passed` (r4) | [r4 spec](FF-001-dual-runtime-demo01/spec.md); exact approval on 2026-10-22; complete r3/r2/r1 retained | [tasks](FF-001-dual-runtime-demo01/tasks.md); current dual-version handoff includes three Rust QA1 repairs and formal/isolated full18, Python48 unchanged | [QA records](FF-001-dual-runtime-demo01/checklist.md); actual fresh QA2 passed local AC01–AC15 for both versions and closed F-001/F-002/F-003; QA1 qa_failed retained; Human Owner final acceptance pending |
| ARCH-TOOL-001 Field Flow | `draft` | [r2 spec](ARCH-TOOL-001-field-flow-runner/spec.md), including complete r1 history and the proposed CA follow-up prompt | Not created; exact implementation scope approval pending | Not created; requires developer_handoff followed by fresh-context Verification |

The PM scope is in spec.md. Development creates tasks.md only after its gate; Verification creates checklist.md after handoff. Pending role documents are not pre-created.

[Owning plan](../PLAN.md)
