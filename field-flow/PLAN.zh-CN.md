# Field Flow 计划

English version: [PLAN.md](PLAN.md)

本目录管理 FF 任务详情和源码；仓库根计划仅作跨项目导航，不复制 FF 的任务权威正文。

| Task ID | 聚合状态 | 范围 | 最新事实 / 下一 gate |
| --- | --- | --- | --- |
| FF-005 | `owner_accepted` (r1) | [基础与进阶案例库](plans/FF-005-basic-and-advanced-examples/spec.md) | Human Owner已于2026-11-04终验精确r1 A，QA2通过AC01–AC12；QA1历史及旧hold_ack限制保留，自有构建环境已收尾、原始证据保留。后续能力与现场gate仍独立。 [Development](plans/FF-005-basic-and-advanced-examples/tasks.md); [Verification](plans/FF-005-basic-and-advanced-examples/checklist.md). 此处保持FF-005的接受范围；FF-004随后已独立推进至下行r2 A。 |
| FF-004 | `qa_passed` (r2 A) | [每PLC一个JSON与多PLC调用](plans/FF-004-plc-json-catalog-and-multi-plc/spec.md) | 新的fresh-context QA通过精确r2 A的AC01–AC14，旧驱动限制与失败历史保留；Human Owner最终验收待定，后续能力与现场gate独立。 [Development](plans/FF-004-plc-json-catalog-and-multi-plc/tasks.md); [Verification](plans/FF-004-plc-json-catalog-and-multi-plc/checklist.md). |
| FF-003 | `draft` (r1) | [C# 运行时与 demo01](plans/FF-003-csharp-runtime-demo01/spec.md) | 实际 PM 已形成独立 C# 工程、demo01 本地闭环、私有 SDK 准备与双语使用/发布说明的 r1 草案；待 Human Owner 精确范围批准，尚未开发或 QA。 |
| FF-002 | `qa_passed`（r1） | [使用手册、案例教程与运行时定位](plans/FF-002-user-guide-and-runtime-positioning/spec.md) | 新的独立 Verification 已通过修正手册及有限本地教程验收，QA1 失败保留；Human Owner 最终验收待定。Windows 适配、Linux 验证、现场托管与长稳仍分别推进。 |
| FF-001 | `qa_passed`（r4） | [r4 Python 应答校验及双语言运行时](plans/FF-001-dual-runtime-demo01/spec.md) | 实际 fresh QA2 已通过双版本本地 AC01–AC15，独立关闭三项 Rust QA1 缺陷；正式/隔离 Rust 全18项通过。未变的 Python48 原 QA1 全量证据已核准，另完成新环境构建/单元/gate/CLI 复验。QA1 qa_failed/历史保留；Human Owner 最终验收、现场及长期运行验证待定。 |
| ARCH-TOOL-001 | `draft` | [r2 讨论基线](plans/ARCH-TOOL-001-field-flow-runner/spec.md) | PM 固化独立实现、长期运行要求及 CA 关系，完整保留 r1；基线保持不变，实施状态归 [FF-001 bundle](plans/FF-001-dual-runtime-demo01/spec.md)。 |

已存在的角色文档见[任务目录](plans/README.zh-CN.md)。本地驱动预检与完整运行时构建/启动、现场、长时间运行及部署验收分别记录。
