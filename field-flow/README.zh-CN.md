# Field Flow

English version: [README.md](README.md)

Field Flow（FF）用于独立维护、手写的现场流程运行程序；AW 发展期间，某个实现可能长期配合 Backend 工作。本目录管理 FF 计划及源码，与离线工具集合分开。

精确 [FF-001 r4](plans/FF-001-dual-runtime-demo01/spec.md)的[双版本 Development 交接](plans/FF-001-dual-runtime-demo01/tasks.md)已通过 fresh-context [QA2](plans/FF-001-dual-runtime-demo01/checklist.md)，覆盖两工程本地 AC01–AC15。Rust 排队 IO 期限、调用前时钟保护及真实 started 统计修复后均独立复验关闭，正式/隔离全18项通过。Python48 保持，原 QA1 全量独立证据已核准，并完成新环境构建/单元/gate/CLI 复验。全部旧失败/候选保留；Human Owner 最终验收、现场验证及长期运行验收待定。

Python定位为熟悉语言、练手及快速原型，本轮不做打包；Rust为后续长期部署runtime的主要建设方向。保留现有Python功能、测试和历史QA，不要求未来所有生产flow双语言同步；平台、现场、托管、容量和长稳仍需分别验收。

完整对照及读者路线见[USER_GUIDE](USER_GUIDE.zh-CN.md)，自身完整步骤分别见[Rust手册](field-flow-rust/USER_GUIDE.zh-CN.md)、[Python手册](field-flow-python/USER_GUIDE.zh-CN.md)和[Rust BUILD](field-flow-rust/BUILD.zh-CN.md)。

## 两个独立实现

| 工程 | 各自管理的工程面 |
| --- | --- |
| `field-flow-rust/` | Cargo 清单/锁、Rust 源码、配置示例、测试和运行数据 |
| `field-flow-python/` | Python 项目/uv 锁、Python 源码、配置示例、测试和运行数据 |

每个实现应能独立复制、构建和启动，不依赖另一个版本的源码、可执行文件、测试服务进程、虚拟环境或可写状态，也不依赖父目录运行清单。当前对照案例保持行为与验收场景一致；后续不默认双实现，文件和函数可遵循各自语言习惯。

[Rust 工程说明](field-flow-rust/README.zh-CN.md)和 [Python 工程说明](field-flow-python/README.zh-CN.md)分别提供独立构建、启动及验证命令。两版已实现 demo01 本地 HTTP GET → PLC INT 闭环，并通过独立本地 QA；现场验证和长期运行验收归后续阶段。

## 手写流程

每个应用流程模块代表一条逻辑流，通过稳定 flow ID 和业务名标识触发方式、步骤、有类型输入输出、跨轮状态与失败行为。runtime 负责调度和生命周期，infrastructure 负责 PLC/HTTP 通信。

demo01 为 HTTP GET -> 条件判断 -> S7 DB INT 写入，Rust 和 Python 候选均有本地 DEV 证据。demo02“PLC 上升沿 -> HTTP POST”属于下一增量。

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
- [首轮实施范围](plans/FF-001-dual-runtime-demo01/spec.md)定义独立运行时与 demo01 本地闭环；精确 r4 已批准，完整已批准 r3/r2/r1 历史保留。
- 继续遵循[仓库契约](../AGENTS.md)和[开发流程](../.codex/workflows/development-lifecycle-workflow.md)。
