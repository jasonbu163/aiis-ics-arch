# Field Flow 任务目录

English version: [README.md](README.md)

FF 任务 bundle 归本目录；迁移时保留历史 Task ID，仓库根目录仅链接这一份 owning bundle。

| 任务 | 状态 | PM 范围 | Development | Verification |
| --- | --- | --- | --- | --- |
| FF-003 C# 运行时与 demo01 | `draft` (r1) | [r1 spec](FF-003-csharp-runtime-demo01/spec.md) | 精确 r1 批准后创建；尚未开发 | 真实 developer_handoff 后另启 fresh Verification |
| FF-002 使用手册、案例教程与运行时定位 | `qa_passed`（r1） | [r1 spec](FF-002-user-guide-and-runtime-positioning/spec.md) | [Development](FF-002-user-guide-and-runtime-positioning/tasks.md); 新的独立 Verification 已通过修正手册及有限本地教程验收，QA1 失败保留；Human Owner 最终验收待定。Windows 适配、Linux 验证、现场托管与长稳仍分别推进。 | [Verification](FF-002-user-guide-and-runtime-positioning/checklist.md) |
| FF-001 双语言运行时与 demo01 | `qa_passed`（r4） | [r4 spec](FF-001-dual-runtime-demo01/spec.md)；2026-10-22 精确批准，完整 r3/r2/r1 保留 | [tasks](FF-001-dual-runtime-demo01/tasks.md)；当前双版本交接含 Rust 三项 QA1 修复及正式/隔离全18项检查，Python48 保持 | [QA 记录](FF-001-dual-runtime-demo01/checklist.md)；实际 fresh QA2 已通过双版本本地 AC01–AC15，关闭 F-001/F-002/F-003；保留 QA1 qa_failed，Human Owner 最终验收待定 |
| ARCH-TOOL-001 Field Flow | `draft` | [r2 spec](ARCH-TOOL-001-field-flow-runner/spec.md)，包含完整 r1 历史与 CA 接续提示词 | 未创建；精确实施范围待批准 | 未创建；需 Development 交接后 fresh-context Verification |

PM 范围归 spec.md；Development 过门禁后创建 tasks.md，Verification 在交接后创建 checklist.md，不预造后续角色文档。

[所属计划](../PLAN.zh-CN.md)
