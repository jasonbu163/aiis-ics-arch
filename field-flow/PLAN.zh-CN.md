# Field Flow 计划

English version: [PLAN.md](PLAN.md)

本目录管理 FF 任务详情和后续源码；仓库根计划仅作跨项目导航，不复制 FF 的任务权威正文。

| Task ID | 聚合状态 | 范围 | 最新事实 / 下一 gate |
| --- | --- | --- | --- |
| FF-001 | `draft`（r3）；r2 `dev_blocked` | [r3 双语言运行时与 demo01](plans/FF-001-dual-runtime-demo01/spec.md) | 已批准 r2 的 Rust 编译及局部协议验证成立，但未匹配 S7 写 ACK 被接受并提交 confirmed。PM 提议通过原库公开 raw ISO 交换接口增加受限 INT 适配。精确 r3 待批准；全部源码/历史/证据保留，Python 未开始，尚无完成交接或 QA。 |
| ARCH-TOOL-001 | `draft` | [r2 讨论基线](plans/ARCH-TOOL-001-field-flow-runner/spec.md) | PM 固化两个独立实现、长期运行要求及 CA 关系，完整保留 r1；讨论基线保持不变，已批准的首轮实施归 FF-001 r2。 |

已存在的角色文档见[任务目录](plans/README.zh-CN.md)。本地驱动预检与完整运行时构建/启动、现场、长时间运行及部署验收分别记录。
