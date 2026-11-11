# Field Flow Rust 任务目录

[English](README.md)

仅导航到 Field Flow 唯一 owning bundles，不复制任务权威正文。

| 任务 | 状态 | PM 范围 | Development | Verification |
| --- | --- | --- | --- | --- |
| FF-004 每PLC一个JSON与多PLC调用 | `owner_accepted` (r2 A) | [r2 spec](../../plans/FF-004-plc-json-catalog-and-multi-plc/spec.md) | [Development](../../plans/FF-004-plc-json-catalog-and-multi-plc/tasks.md) | [Verification](../../plans/FF-004-plc-json-catalog-and-multi-plc/checklist.md); QA3 在 macOS arm64 回环环境通过 AC01–AC14，Human Owner 于 2026-11-10 最终验收精确 r2 A。旧驱动限制与失败历史保留，现场验证仍属后续。 |
| FF-005 基础与进阶案例库 | `owner_accepted` (r1) | [r1 spec](../../plans/FF-005-basic-and-advanced-examples/spec.md) | [Development](../../plans/FF-005-basic-and-advanced-examples/tasks.md) | [Verification](../../plans/FF-005-basic-and-advanced-examples/checklist.md); Human Owner已于2026-11-04终验精确r1 A，QA2通过AC01–AC12；QA1历史及旧hold_ack限制保留，自有构建环境已收尾、原始证据保留。后续能力与现场gate仍独立。 |
| FF-002 | `qa_passed`（r1） | [r1 spec](../../plans/FF-002-user-guide-and-runtime-positioning/spec.md) | [Development](../../plans/FF-002-user-guide-and-runtime-positioning/tasks.md) | [Verification](../../plans/FF-002-user-guide-and-runtime-positioning/checklist.md) |
| FF-001 | `qa_passed` (r4) | [r4 spec](../../plans/FF-001-dual-runtime-demo01/spec.md) | [tasks](../../plans/FF-001-dual-runtime-demo01/tasks.md) | [checklist](../../plans/FF-001-dual-runtime-demo01/checklist.md); QA2 通过；Human Owner 最终验收待定 |
