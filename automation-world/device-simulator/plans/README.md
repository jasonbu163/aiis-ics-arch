# DS Task Index

[中文](README.zh-CN.md) · [DS plan](../PLAN.md)

Further DS product scope belongs to its local `plans/<task>/spec.md`, with progress indexed in this project's PLAN. ARCH-AW-005 remains a related historical root bundle; its records, approvals and acceptance are not moved, copied or inherited.

| Task | Status | Scope entry | Subsequent records |
| --- | --- | --- | --- |
| DS-002 Multi-protocol simulation and device debugging design | `draft` | [r1 spec](DS-002-multi-protocol-simulation-and-device-debugging/spec.md) | Actual PM design awaits exact Human Owner approval. Implementation phases remain separately gated; tasks.md is pending a precise approved implementation scope, and checklist.md follows a real Development handoff and fresh-context Verification. Neither later document has been created. |
| DS-001 Policy table, bulk editing and usability | `owner_accepted` | [r1 spec](DS-001-policy-table-and-usability/spec.md) | Human Owner accepted the current version on 2026-10-27; [acceptance/closeout](DS-001-policy-table-and-usability/spec.md#owner-acceptance-ds001). [DEV records](DS-001-policy-table-and-usability/tasks.md) and [text guide](../USER_GUIDE.md) retained; independent QA/checklist not executed under the task exception. |
| Related aiis-ics-arch::DAA-007 r2 startup delta | `owner_accepted` | [Unique DAA spec](../../data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/spec.md) | Related DAA-007 r2 and controlled Stage B were finally accepted on 2026-10-30. This DS startup delta is accepted through the DAA record without retroactive changes to earlier DS QA/acceptance. Historical limits remain; Stage C/automatic startup/field work are separate. |

Historical baseline: [ARCH-AW-005 r5 spec](../../../plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md) · [DEV records](../../../plans/ARCH-AW-005-ds-g0-prototype-validation/tasks.md) · [verification and 2026-10-27 Owner acceptance](../../../plans/ARCH-AW-005-ds-g0-prototype-validation/checklist.md#owner-acceptance-r5). Historical technical QA and Owner acceptance remain separate facts. DAA–DS S7-to-SQLite joint validation is separately gated; Stage C stays deferred.
