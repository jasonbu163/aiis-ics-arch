# DS Plan

[中文](PLAN.zh-CN.md) · [Task catalog](plans/README.md)

This PLAN owns further DS product work. The root and AW retain overall summaries and links. Original root ARCH-AW-005 records stay in place; Human Owner accepted DS-001 r1 and ARCH-AW-005 r5 on 2026-10-27 (Asia/Shanghai).

| Task | Status | Scope and next step |
| --- | --- | --- |
| [DS-004 r2: Bilingual point display names](plans/DS-004-bilingual-point-display-names/spec.md) | `qa_blocked` | QA4 found no new definite failure in synthetic checks; mandatory native checks remain paused after an isolation incident. |
| [DS-003 r5: Per-PLC point JSON export](plans/DS-003-plc-json-export/spec.md) | `qa_passed` | QA2 passed after the corrected DS→DAA native joint retest; Human Owner acceptance is pending. |
| [DS-002 r2: Modbus TCP simulation and S7 compatibility](plans/DS-002-multi-protocol-simulation-and-device-debugging/spec.md) | `draft` | The spec contains the six-page comparison, node diagram, S7 compatibility contract and AC01–AC12. Await exact scope approval for A0 and conditional A1. Device debugging is planned for a later phase. |
| [DS-001 r1: Policy table, bulk editing and usability](plans/DS-001-policy-table-and-usability/spec.md) | `owner_accepted` | Human Owner accepted the current DS version on 2026-10-27; [acceptance and closeout](plans/DS-001-policy-table-and-usability/spec.md#owner-acceptance-ds001). Policy/bulk editing, input/usability, text guide and separately approved DIRECT corrections are delivered. [DEV records](plans/DS-001-policy-table-and-usability/tasks.md) remain historical; independent QA was waived for DS-001. No additional functionality or full QA in closeout. |
| [ARCH-AW-005 r5: Historical product baseline](../../plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md) | `owner_accepted` | Human Owner accepted r5 on 2026-10-27; [acceptance and retained resources](../../plans/ARCH-AW-005-ds-g0-prototype-validation/checklist.md#owner-acceptance-r5). Original QA4 remains qa_passed for its exact candidate; all earlier failures and G0 retirement evidence remain. Subsequent DS-001/manual and DIRECT corrections are not relabelled as old QA4 evidence. |
| [aiis-ics-arch::DAA-007 r2: Related joint-test startup configuration](../data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/spec.md) | `owner_accepted` | Related DAA-007 r2 and controlled Stage B were finally accepted on 2026-10-30. This DS startup delta is accepted through the DAA record without retroactive changes to earlier DS QA/acceptance. Historical limits remain; Stage C/automatic startup/field work are separate. |

DAA–DS S7-to-SQLite joint validation remains separately gated; Stage C stays deferred. This task's manual-acceptance exception does not change later joint-verification requirements.
