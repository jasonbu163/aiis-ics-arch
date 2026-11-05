# DS Plan

[中文](PLAN.zh-CN.md) · [Task catalog](plans/README.md)

This PLAN owns further DS product work. The root and AW retain overall summaries and links. Original root ARCH-AW-005 records stay in place; Human Owner accepted DS-001 r1 and ARCH-AW-005 r5 on 2026-10-27 (Asia/Shanghai).

| Task | Status | Scope and next step |
| --- | --- | --- |
| [DS-002 r1: Multi-protocol simulation and device debugging design](plans/DS-002-multi-protocol-simulation-and-device-debugging/spec.md) | `draft` | Actual PM prepared the S7/Modbus TCP design, isolated simulation/debugging roles, v1 protection, staged implementation and proposed FF file mapping. Await exact Human Owner design approval; no implementation or independent QA, and no later-stage authorization. |
| [DS-001 r1: Policy table, bulk editing and usability](plans/DS-001-policy-table-and-usability/spec.md) | `owner_accepted` | Human Owner accepted the current DS version on 2026-10-27; [acceptance and closeout](plans/DS-001-policy-table-and-usability/spec.md#owner-acceptance-ds001). Policy/bulk editing, input/usability, text guide and separately approved DIRECT corrections are delivered. [DEV records](plans/DS-001-policy-table-and-usability/tasks.md) remain historical; independent QA was waived for DS-001. No additional functionality or full QA in closeout. |
| [ARCH-AW-005 r5: Historical product baseline](../../plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md) | `owner_accepted` | Human Owner accepted r5 on 2026-10-27; [acceptance and retained resources](../../plans/ARCH-AW-005-ds-g0-prototype-validation/checklist.md#owner-acceptance-r5). Original QA4 remains qa_passed for its exact candidate; all earlier failures and G0 retirement evidence remain. Subsequent DS-001/manual and DIRECT corrections are not relabelled as old QA4 evidence. |
| [aiis-ics-arch::DAA-007 r2: Related joint-test startup configuration](../data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/spec.md) | `owner_accepted` | Related DAA-007 r2 and controlled Stage B were finally accepted on 2026-10-30. This DS startup delta is accepted through the DAA record without retroactive changes to earlier DS QA/acceptance. Historical limits remain; Stage C/automatic startup/field work are separate. |

DAA–DS S7-to-SQLite joint validation remains separately gated; Stage C stays deferred. This task's manual-acceptance exception does not change later joint-verification requirements.
