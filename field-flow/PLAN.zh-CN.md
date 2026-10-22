# Field Flow 计划

English version: [PLAN.md](PLAN.md)

本目录管理 FF 任务详情和源码；仓库根计划仅作跨项目导航，不复制 FF 的任务权威正文。

| Task ID | 聚合状态 | 范围 | 最新事实 / 下一 gate |
| --- | --- | --- | --- |
| FF-001 | `qa_passed`（r4） | [r4 Python 应答校验及双语言运行时](plans/FF-001-dual-runtime-demo01/spec.md) | 实际 fresh QA2 已通过双版本本地 AC01–AC15，独立关闭三项 Rust QA1 缺陷；正式/隔离 Rust 全18项通过。未变的 Python48 原 QA1 全量证据已核准，另完成新环境构建/单元/gate/CLI 复验。QA1 qa_failed/历史保留；Human Owner 最终验收、现场及长期运行验证待定。 |
| ARCH-TOOL-001 | `draft` | [r2 讨论基线](plans/ARCH-TOOL-001-field-flow-runner/spec.md) | PM 固化独立实现、长期运行要求及 CA 关系，完整保留 r1；基线保持不变，实施状态归 [FF-001 bundle](plans/FF-001-dual-runtime-demo01/spec.md)。 |

已存在的角色文档见[任务目录](plans/README.zh-CN.md)。本地驱动预检与完整运行时构建/启动、现场、长时间运行及部署验收分别记录。
