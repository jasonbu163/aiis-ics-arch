# Field Flow

English version: [README.md](README.md)

Field Flow（FF）归属可独立维护的手写现场流程运行程序；在 AW 持续发展期间，任一实现都可能长期配合 Backend 承担现场职责。本目录管理 FF 的计划与后续源码，与离线 tools 工具集合分开。

Rust 局部候选已编译并获得本地协议证据，但 r2 Development 已阻塞：高层 S7 驱动把未匹配的确认响应当成成功。[Development 记录及失败证据](plans/FF-001-dual-runtime-demo01/tasks.md)完整保留。[r3 提案](plans/FF-001-dual-runtime-demo01/spec.md)保留原库，经公开 raw ISO 交换接口增加受限 INT 请求/响应适配，等待 Human Owner 精确批准。Python 尚未开始，完整运行时验收及 QA 仍待完成。

## 两个独立实现

| 工程 | 各自管理的工程面 |
| --- | --- |
| `field-flow-rust/` | Cargo 清单/锁、Rust 源码、配置示例、测试和运行数据 |
| `field-flow-python/` | Python 项目/uv 锁、Python 源码、配置示例、测试和运行数据 |

每个实现应能独立复制、构建和启动，不依赖另一个版本的源码、可执行文件、测试服务进程、虚拟环境或可写状态，也不依赖父目录运行清单。两版保持流程行为与验收场景一致，文件和函数组织可以遵循各自语言习惯。

Rust 目录保留局部、阻塞中的实现；Python 目录仍为规划。完整构建/启动说明将在实现及验证完成后补充。

## 手写流程

每个应用流程模块代表一条逻辑流，通过稳定 flow ID 和业务名标识触发方式、步骤、有类型输入输出、跨轮状态与失败行为。runtime 负责调度和生命周期，infrastructure 负责 PLC/HTTP 通信。

首批场景为 HTTP GET -> 条件 -> S7 DB 写入，以及 S7 DB 读取 -> 条件/上升沿 -> HTTP POST。这些是拟实现的场景，不表示连接器已经实现或现场测试已经通过。

## Backend 与长期运行

Backend 保留业务校验和业务数据归属，FF 经明确约定的 API 配合；具体路由、确认和幂等合同仍需核对。现场配置和客户专属规则归消费项目。

设计目标包括流程故障隔离、有界通信与重连、持久事件及投递状态、未知结果核实、持久日志与轮转、健康/进度报告和正常退出。各实现独立管理本地恢复数据。安装、schema 创建、后台托管和现场操作需要另行明确实施与验证范围。

同一冲突流程/资源/业务效果由一个有效写入方负责。Rust、Python 或未来 CA 之间切换时，应先核对 pending/unknown 工作和已确认进度，再交接执行；各自管理的数据库不能默认互换。

## 与未来 CA 的关系

FF 保持可独立维护，其流程说明和已验证场景可作为后续 CA 节点流程的来源。AI 辅助代码迁移先形成候选草稿，再核对行为。CA 编辑器、AI Chat 与 DeepSeek 接入归独立的 CA 工作流。

[CA 会话接续提示词](plans/ARCH-TOOL-001-field-flow-runner/spec.md#ca-handoff-prompt)整理了拟交接内容；当前未发送给 CA 会话，也不构成对该会话的写入授权。

## 文档入口

- [PLAN.zh-CN.md](PLAN.zh-CN.md)索引 FF 当前任务及下一 gate。
- [任务目录](plans/README.zh-CN.md)只链接真实存在的角色文档。
- [讨论基线](plans/ARCH-TOOL-001-field-flow-runner/spec.md)管理详细范围、决策、分阶段验收和可还原的 r1 历史。
- [首轮实施范围](plans/FF-001-dual-runtime-demo01/spec.md)定义独立运行时与 demo01 本地闭环；r3 为待批准草案，完整已批准 r2/r1 历史保留。
- 继续遵循[仓库契约](../AGENTS.md)和[开发流程](../.codex/workflows/development-lifecycle-workflow.md)。
