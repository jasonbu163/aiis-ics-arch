# Field Flow Task Catalog

Chinese version: [README.zh-CN.md](README.zh-CN.md)

FF task bundles live here. The historical Task ID is retained during relocation; the repository catalog links this unique owning bundle.

| Task | Status | PM scope | Development | Verification |
| --- | --- | --- | --- | --- |
| FF-005 Basic and advanced example library | `owner_accepted` (r1) | [r1 spec](FF-005-basic-and-advanced-examples/spec.md) | [Development](FF-005-basic-and-advanced-examples/tasks.md) | [Verification](FF-005-basic-and-advanced-examples/checklist.md); Human Owner accepted exact r1 A on 2026-11-04 after QA2 passed AC01–AC12. QA1 history and the old hold_ack limit remain; generated resources were closed out and original evidence retained. Later capability and field gates stay separate. |
| FF-004 Per-PLC JSON catalog and multi-PLC calls | `owner_accepted` (r2 A) | [r2 spec](FF-004-plc-json-catalog-and-multi-plc/spec.md) | [Development](FF-004-plc-json-catalog-and-multi-plc/tasks.md) | [Verification](FF-004-plc-json-catalog-and-multi-plc/checklist.md); The Human Owner accepted exact r2 A on 2026-11-10 after QA3 passed AC01–AC14 on macOS arm64 loopback. Driver limits and earlier QA failures remain recorded. Field validation is a separate gate. |
| FF-003 C# runtime and demo01 | `dev_blocked` (r2) | [r2 spec](FF-003-csharp-runtime-demo01/spec.md) | [Development](FF-003-csharp-runtime-demo01/tasks.md) | Native Win10 x64 verification awaits a lab host. Independent QA follows the actual handoff |
| FF-002 User Guides and Runtime Positioning | `qa_passed` (r1) | [r1 spec](FF-002-user-guide-and-runtime-positioning/spec.md) | [Development](FF-002-user-guide-and-runtime-positioning/tasks.md); New independent Verification passed the corrected guides and bounded local tutorials; QA1 failure is retained. Human Owner final acceptance is pending; Windows porting, Linux validation, field hosting and long soak remain separate. | [Verification](FF-002-user-guide-and-runtime-positioning/checklist.md) |
| FF-001 Dual Runtimes and demo01 | `qa_passed` (r4) | [r4 spec](FF-001-dual-runtime-demo01/spec.md); exact approval on 2026-10-22; complete r3/r2/r1 retained | [tasks](FF-001-dual-runtime-demo01/tasks.md); current dual-version handoff includes three Rust QA1 repairs and formal/isolated full18, Python48 unchanged | [QA records](FF-001-dual-runtime-demo01/checklist.md); actual fresh QA2 passed local AC01–AC15 for both versions and closed F-001/F-002/F-003; QA1 qa_failed retained; Human Owner final acceptance pending |
| ARCH-TOOL-001 Field Flow | `draft` | [r2 spec](ARCH-TOOL-001-field-flow-runner/spec.md), including complete r1 history and the proposed CA follow-up prompt | Not created; exact implementation scope approval pending | Not created; requires developer_handoff followed by fresh-context Verification |

The PM scope is in spec.md. Development creates tasks.md only after its gate; Verification creates checklist.md after handoff. Pending role documents are not pre-created.

[Owning plan](../PLAN.md)
